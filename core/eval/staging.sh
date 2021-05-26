#!/usr/bin/env bash

KEY=$1
IMG=$2
EXT=$3
FLAGS=$4

if [[ -z $KEY || -z $IMG|| -z $EXT ]]; then
  echo "USAGE: evaluate.sh KEY PATH EXT [FLAGS]"
  echo " > ./staging.sh asdfasfdasdfasdfasdfa /path/to/file.jpg .png \"-F 'size=full'\""
  exit 1
fi


run() {
    echo "production..."
    cmd="curl -H 'X-API-Key: $1' -F 'image_file=@$2' $3 -f https://api.remove.bg/v1.0/removebg -o $2-no-bg-production_result$4"
    echo $cmd
    eval $cmd


    echo "staging..."
    cmd="curl -H 'X-API-Key: $1' -F 'image_file=@$2' $3 -f https://localhost:8080/v1.0/removebg -o $2-no-bg-staging_result$4 --insecure"
    eval $cmd
}

if [[ -d $IMG ]]; then

    for f in $IMG/*
    do
        echo "Processing $f..."

        run "$KEY" "$f" "$FLAGS" "$EXT"
    done

else
    run "$KEY" "$IMG" "$FLAGS" "$EXT"
fi