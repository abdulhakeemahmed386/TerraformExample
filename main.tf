terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "2.14.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# Pulls the image
resource "docker_image" "ubuntu" {
  name = "jenkins/jenkins:lts"
}

# Create a container
resource "docker_container" "foo" {
  image = docker_image.ubuntu.latest
  name  = "foo"
}