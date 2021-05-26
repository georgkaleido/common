#!/usr/bin/env bash

DIR=$1
VERSION=$2
CLEANUP=$3

if [[ -z $DIR || -z $VERSION ]]; then
  echo "USAGE: evaluate.sh DIR VERSION [CLEANUP]"
  exit 1
fi

# person

d=`pwd`
cd ../../

if [[ ! -z $CLEANUP ]]; then
  echo "cleaning up..."
  find $DIR/alpha -type f -name '*result.png' -delete
fi

echo "evaluating alpha..."
python3 -m removebg.demo $DIR/alpha --path_networks ../kaleido-models/ --path_parent test --evaluate --evaluate_file $d/$VERSION.json --caption $VERSION --skip
