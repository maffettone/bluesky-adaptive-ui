# Launch Containers to Develop UI against
These depend on [bluesky-pods](https://github.com/bluesky/bluesky-pods). 
Specifically, starting up the acq-pod.

```sh
cd compose/acq-pod
podman compose --in-pod true up
```

Next you can start a basic agent in a container that will interface with this pod and expose itself at `http://localhost:60615`.

```sh
bash launch-agent.sh
```
For example, asking the agent for a suggestion, will put a measurement on the queue and execute that measurement.

This will put agent `ask` data into tiled, and the subsequent measurement data into tiled.

The Kakfa links aren't working just yet, but this will be enough to get off the ground with agent written documents.
