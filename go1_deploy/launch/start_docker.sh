docker stop foxy_controller || true
docker rm foxy_controller || true
docker run -d\
	--env="DISPLAY=${DISPLAY}" \
	--env="QT_X11_NO_MITSHM=1" \
	--volume="/home/unitree/eurekaverse:/home/isaac/eurekaverse" \
    --volume="/home/unitree/.Xauthority:/root/.Xauthority:rw" \
	--volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --volume="/run/jtop.sock:/run/jtop.sock" \
    -p 5000:5000 \
    -p 8888:8888 \
	--privileged \
	--runtime=nvidia \
	--net=host \
	--workdir="/home/isaac/eurekaverse/go1_deploy/scripts" \
	--name="foxy_controller" \
	go1-deploy tail -f /dev/null
docker start foxy_controller
docker exec -it foxy_controller bash -c 'cd /home/isaac/eurekaverse/ && python3 -m pip install -e . && cd /home/isaac/eurekaverse/extreme-parkour/legged_gym/ && python3 -m pip install -e .'