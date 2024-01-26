#!/bin/sh

#This script is intended to be run by first doing a wget on this file and executing it locally
#it will clone the git repo and copy over a sample environment file to your home directory

sudo apt install python3.10-venv python3 virtualenv pip git
git clone git@github.com:javanator/gocr.git

pushd gocr
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
if ! [ -f $HOME/.gocr.env ]; then
  cp gocr.env ~/.gocr.env
  echo "No ENV file found. Sample Copied"
  echo "Edit $HOME/.gocr.env prior to use"
fi
popd

echo "Installation complete"
echo "manually source $HOME/gocr/venv/activate prior to use"
echo "manually Add $HOME/gocr/bin to PATH"

