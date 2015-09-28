#!/bin/bash
set -o errexit
set -o pipefail

ARGS_TO_PASS=
while [[ $# > 1 ]]; do
    arg=$1
    case $arg in
        --cactusConfigFile)
            shift
            CONFIG=$(readlink -f "$1")
            ;;
        *)
            ARGS_TO_PASS="$ARGS_TO_PASS $1"
    esac
    shift
done

if [[ $# < 1 ]]; then
    echo "Usage: $0 [OPTIONS] CONTAINER_NAME" >&2
    exit 1
fi

NAME=$1
IMAGE_NAME=progressivecactus

# NB: assumes this is in cactusBenchmarks/bin
CACTUS_BENCHMARKS_DIR=$(readlink -f $(dirname $0)/..)

docker build -t "$IMAGE_NAME" "$CACTUS_BENCHMARKS_DIR"
if [ -z $CONFIG ]; then
    # Use default cactus config file (included in cactus repository)
    docker run -d --name "$NAME" "$IMAGE_NAME" --outputDir /output \
           "$NAME" \
           $ARGS_TO_PASS
else
    # Use custom cactus config file.
    # First, copy the config file to a temporary file, to ensure that
    # any changes to it while the container's running doesn't screw
    # with the output
    NEW_CONFIG=$(mktemp)
    cp "$CONFIG" "$NEW_CONFIG"
    CONFIG=$NEW_CONFIG
    # Now run the container, mounting the config file to a custom
    # location
    docker run --name "$NAME" -d -v "$CONFIG":/"$CONFIG" "$IMAGE_NAME" \
        --cactusConfigFile /"$CONFIG" \
        --outputDir /output \
        "$NAME" \
        $ARGS_TO_PASS
fi
status=$(docker wait "$NAME")
if [[ $status == 0 ]]; then
    mkdir output-"$NAME"
    docker cp "$NAME":/output output-"$NAME"/
    # For some reason, docker will insist on making the "output"
    # directory a subdirectory of the destination path it's
    # given. This is a roundabout way of getting it to do what we
    # actually want
    mv output-"$NAME"/output/* output-"$NAME"
    rmdir output-"$NAME"/output
    # Delete the container
    docker rm "$NAME"
    if [ -f "$CONFIG" ]; then
        # We created a temporary copy of the config file. Delete it
        # now.
        rm "$CONFIG"
    fi
else
    echo "Run with container name $NAME has failed. Last 10 lines of the log:"
    docker logs --tail 10 "$NAME"
    docker rm "$NAME"
    
    exit 1
fi
