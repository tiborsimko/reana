#!/usr/bin/env bash

reana-client list | grep -v '^NAME' | awk '{print $1;}' | sort -u | awk '{print "reana-client delete -w", $0, "--include-all-runs --include-workspace --include-records"}' | sh

