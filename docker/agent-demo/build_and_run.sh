pushd ../queue-server
docker build -t queue-server:latest .
popd
pushd ../http-server
docker build -t http-server:latest .
popd
docker build -t adaptive_server_demo:latest .
docker-compose up