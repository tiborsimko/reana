# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2021, 2023 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for reana-dev helm-* commands."""
import pytest


@pytest.mark.parametrize(
    "original,docker_images, expected",
    [
        (
            "docker.io/reanahub/reana-job-controller:0.8.0-alpha.3 \\\n"
            " docker.io/reanahub/reana-message-broker:0.8.0-alpha.1 \\",
            [
                "docker.io/reanahub/reana-job-controller:0.8.1",
                "docker.io/reanahub/reana-message-broker:0.8.0-alpha.1",
            ],
            "docker.io/reanahub/reana-job-controller:0.8.1 \\\n"
            " docker.io/reanahub/reana-message-broker:0.8.0-alpha.1 \\",
        ),
        (
            "image: docker.io/reanahub/reana-server:0.8.0-alpha.2\nenvironment:",
            ["docker.io/reanahub/reana-server:0.8.1"],
            "image: docker.io/reanahub/reana-server:0.8.1\nenvironment:",
        ),
    ],
)
def test_replace_docker_images(original, docker_images, expected):
    """
    Purpose of the test is to check if internal _replace_docker_images function
    properly replaces docker images (name + tag) followed by empty space or a new line
    """
    from reana.reana_dev.helm import _replace_docker_images

    assert _replace_docker_images(original, docker_images) == expected
