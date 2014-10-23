#!/bin/bash

sudo apt-get update
sudo apt-get dist-upgrade
sudo apt-get upgrade

sudo apt-get autoremove

cd /home/pi/pianette

git stash
git pull origin master

chmod +x main*