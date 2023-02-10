# Docker Installation Guide

## Prerequisites

Docker must be installed on your system. If you don't have Docker installed, follow the instructions for your operating system here.

You should have basic knowledge of Docker and its concepts, such as containers and images.

## Installation
Clone the repository containing the Dockerfile:

    git clone https://github.com/badboysm890/DynamicImageServer.git

Change into the directory where the Dockerfile is located:

    cd DynamicImageServer

Build the Container

    docker build -t banner_generator . 

Once Successfully built

    docker run -p 80:5000 banner_generator

This will automatically run the server in port 80 and server should be ready to run.

## To Deploy use the command

    docker run -d -p 80:5000 banner_generator --restart always

This will run the container in detached mode and will restart to run even if system restarts.
