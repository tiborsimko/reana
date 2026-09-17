# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2026 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Client setup uses the client's selected server without reading its store."""

import importlib.util
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from reana.reana_dev import run


@pytest.mark.parametrize("bypass", [False, True])
def test_explicit_target_mismatch_requires_login_and_confirmation(monkeypatch, bypass):
    """A valid login on another cluster must never satisfy an explicit target."""
    calls = []
    responses = iter(
        [
            subprocess.CompletedProcess(
                [], 0, "REANA server: https://other.example.org\n", ""
            ),
            subprocess.CompletedProcess([], 0, "", ""),
            subprocess.CompletedProcess(
                [], 0, "REANA server: https://localhost:30443\n", ""
            ),
        ]
    )

    def execute(arguments, **kwargs):
        calls.append(arguments)
        return next(responses)

    monkeypatch.delenv("REANA_ACCESS_TOKEN", raising=False)
    monkeypatch.setattr(run.subprocess, "run", execute)
    monkeypatch.setattr(run.sys, "stdin", SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(run.sys, "stdout", SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(run, "display_message", Mock())
    run.ensure_client_login("client", "https://localhost:30443", bypass)
    assert calls[0] == calls[2] == ["client", "ping"]
    assert calls[1] == ["client", "login", "--server", "https://localhost:30443"] + (
        ["--no-tls-verify"] if bypass else []
    )


def test_saved_remote_server_is_reused_without_login(monkeypatch):
    """No explicit target means the client's current server is authoritative."""
    execute = Mock(
        return_value=subprocess.CompletedProcess(
            [], 0, "REANA server: https://remote.example.org\n", ""
        )
    )
    monkeypatch.setattr(run.subprocess, "run", execute)
    run.ensure_client_login("client")
    execute.assert_called_once_with(["client", "ping"], capture_output=True, text=True)


def test_connection_failure_does_not_start_a_browser(monkeypatch):
    """A failed network probe gives diagnostics instead of a redundant login."""
    execute = Mock(
        return_value=subprocess.CompletedProcess(
            [],
            1,
            "",
            "Could not connect to https://remote.example.org (from saved login): The connection was refused.",
        )
    )
    monkeypatch.setattr(run.subprocess, "run", execute)
    with pytest.raises(SystemExit):
        run.ensure_client_login("client")
    assert execute.call_count == 1


def test_e2e_client_uses_disposable_settings_and_retains_token(monkeypatch):
    """Browser-session e2e tokens need a temporary store, not another CLI login."""
    path = Path(__file__).parents[1] / "scripts/test-auth-workflow-e2e.py"
    spec = importlib.util.spec_from_file_location("auth_e2e", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    runner = module.E2E.__new__(module.E2E)
    runner.server_url = "https://localhost:30443"
    runner.access_token = "session.jwt.token"
    runner.client_path = "client"
    runner.demo_dir = "/demo"
    monkeypatch.setenv("REANA_SERVER_URL", "https://stale.example.org")
    monkeypatch.setenv("REANA_SERVER_TLS_VERIFY", "0")
    captured = []

    def execute(arguments, **kwargs):
        env = kwargs["env"]
        assert "REANA_SERVER_URL" not in env
        assert "REANA_SERVER_TLS_VERIFY" not in env
        assert env["REANA_ACCESS_TOKEN"] == runner.access_token
        config_path = Path(env["REANA_CLIENT_CONFIG"])
        assert config_path.stat().st_mode & 0o777 == 0o600
        data = json.loads(config_path.read_text())
        assert data["active_server"] == runner.server_url
        assert data["servers"][runner.server_url]["tls"]["verify"] is False
        captured.append(config_path)
        return "success"

    runner.run = execute
    assert runner.client("ping") == "success"
    assert not captured[0].exists()
