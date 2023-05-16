# docker build -t kmeans_service:latest .
FROM  fedora
# Lock in a python version because of some backward compatability issues
RUN dnf update -y \
    && dnf install -y \
    python3.9 \
    g++ \
    gcc \
    git \
    && dnf clean all

RUN python3.9 -m ensurepip --upgrade
RUN pip3 install 'bluesky-adaptive[all]'
RUN pip3 install 'tiled[all]'
RUN pip3 install uvicorn fastapi caproto nslsii
RUN pip3 install git+https://github.com/bluesky/databroker.git@v2.0.0b13#egg=databroker


COPY agent_sim.py /src/agent_sandbox.py
#COPY agent_sandbox.py /src/agent_sandbox.py
COPY tiled_client_config.yml /etc/tiled/profiles/tiled_client_config.yml

ENV BS_AGENT_STARTUP_SCRIPT_PATH=/src/agent_sandbox.py

CMD uvicorn bluesky_adaptive.server:app --host 0.0.0.0 --port 60610