
# NVIDIA Exporter
This is an prometheus exportor for nvidia gpu base metrics as well as metrics about container which used gpu.

# Running
This exporter only support running inside a container.
Before running this exporter, make sure docker can access to NVML. (nvidia-docker) 

    docker run --pid=host -v /var/run/docker.sock:/var/run/docker.sock -p 9439:9439 vippor/gpu-exporter:latest

If your docker version is lower, maybe you should run:

    nvidia-docker run --pid=host -v /var/run/docker.sock:/var/run/docker.sock -p 9439:9439 vippor/gpu-exporter:latest

Environment:
there are two env you can set
    port: 9439   //  exporter http port, default 9439
    interval: 5   // how much interval to collect metrics, default 5 seconds

# Noting:
It spends lots of time for get docker info and gpu info, so there is a cron task for collecting theirs by [interval] seconds.
When you access to the exporter api, there is a little delay time for metrics.   
       
  