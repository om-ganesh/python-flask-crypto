# Docker commands  

## To run docker

Here are some docker commands useful in this project.

If docker is not installed, install it.

    sudo apt  install docker.io

Follow the instructions in the TPM course repo. To run docker, the current user
should be in group docker. Use `id` command to check. The following command add
the current user into docker group. 

    sudo usermod -a -G docker $USER

After adding the user into the group, log out and log in again to activate 
the new group. Or use the following command to log in again. 

    exec su -l $USER

## Build the images

The command to build the images is as follows. It takes a long time (10
minutes?) to complete. Be patient.

    docker build -t tpmcourse:latest .

## Run the docker container

Once we have a docker image, we can start it and we have a container.  So a
docker image is like a program and a container is like a process.  The
difference is that a docker container can be stopped and resumed later.

### Start a container

To start a container from an image: 

    docker run -it tpmcourse:latest

    # --name can specify a name, which we can use refer to this container later
    docker run --name tpm -it tpmcourse:latest

To list active container:

    docker ps
    # we can find the container ID and names for each container

If a container is stopped (e.g., when we exit from the shell), we will not see
the container on the active list. Use `-a` option to see all containers, even
if they are not running

    docker ps -a 

### Stop a container

If you exit from the shell, the container will be stopped as the process has
terminated. 

We can also stop a container with docker command.

    # need to run in another terminal
    docker stop CONTAINER

Once a container is stopped, we do not see it with `docker ps` command. We 
need to add `-a` option to see stopped containers.

### Resume a container

To resume a container:

    # -a : attach the current console 
    docker start -ai CONTAINER

The container will be runnning and you have a shell in it. 

We can also start the container in the detached mode and keep it running in the
background. 

    docker start CONTAINER

## Start a shell in container

If we need to access a shell in a detached container, we can use `docker exec`
command. For example, the following command starts a bash in a running
container. 

    # we can start any shell we like, for example, bash
    docker exec -it CONTAINER bash

## Other docker command

If a container is running, but does not have a console, we can attach the
current console.

    docker attach CONTAINER
    
To delete a container:

    ### All files in the container will be LOST !!!
    ### Copy all files to host first !!
    ### Normally you only need this after you receive the final grade 

    docker rm CONTAINER

## Copy files

We can use `docker cp` to copy files between the container and the host file system.

    docker cp ./cleanup.sh CONTAINER:/root
    docker cp CONTAINER:/root/a.pem local/a.pem

## TPM Course container

When the TPM container is started for the first time (with `docker run`), the
TPM simulator should work. If we (accidentally) exit from the shell, the
container will be stopped. After we start/resume the container (with `docker
start`), the TPM simulator may not be working because some processes have been
terminated.  

I found it is more convenient to start the docker in the detached mode and keep
it running. We can use `docker exec` to start another shell in the container.
Even better, we can pick a shell we like, for example, bash.

    # only start the container if it is stopped
    docker start CONTAINER

    # start bash in the running container
    docker exec -it CONTAINER bash

Once we are in bash, if the TPM simulator is not working, we can clean up and
restart the simulator. The commands are in `tpm2restart.sh`.  You can copy the
script to the container and run the script to restart the TPM simulator.

If we exit from bash, the TPM simulator is still running. If we need
shell, we just need to run `docker exec`.

