#!/bin/sh
set -e

echo "[hermes] Syncing config..."
mkdir -p /root/.hermes
cp /opt/hermes-defaults/config.yaml /root/.hermes/config.yaml

echo "[hermes] Syncing skills..."
mkdir -p /root/.hermes/skills
cp /opt/hermes-defaults/skills/* /root/.hermes/skills/

exec hermes gateway run
