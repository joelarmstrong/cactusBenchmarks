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
    docker run -d --name "$NAME" "$IMAGE_NAME" --outputDir /output \
           "$NAME" \
           $ARGS_TO_PASS
else
    docker run --name "$NAME" -d -v "$CONFIG":/"$CONFIG" "$IMAGE_NAME" \
        --cactusConfigFile /"$CONFIG" \
        --outputDir /output \
        "$NAME" \
        $ARGS_TO_PASS
fi
status=$(docker wait "$NAME")
if [[ $status == 0 ]]; then
    mkdir output-"$NAME"
    docker cp "$NAME":/output/* output-"$NAME"/
    docker rm "$NAME"
else
    echo "Run with container name $NAME has failed. Last 10 lines of the log:"
    docker logs --tail 10 "$NAME"
    echo "The container was not automatically cleaned up. Run:"
    echo "docker rm $NAME"
    echo "to free the disk space it was using."
    exit 1
fi
