#! /usr/bin/bash
# Designed to work with bluesky pods
set -e
set -o xtrace

if [ "$1" != "" ]; then
    agent_file=$1
else
    agent_file="./mvp_full_stack_agent.py"
fi

pushd ../bluesky-dbv2
podman build -t bluesky-dbv2 .
popd

podman run --pod pod_acq-pod \
        --net acq-pod_default \
        --network-alias sneaky \
        -ti  --rm \
        -v $agent_file:/app/agent.py \
        -v ./tiled_client_config.yml:/etc/tiled/profiles/tiled_client_config.yml \
        -e BS_AGENT_STARTUP_SCRIPT_PATH=/app/agent.py \
        -p 60615:60615 \
        bluesky-dbv2 \
        uvicorn bluesky_adaptive.server:app --port 60615 --host 0.0.0.0
