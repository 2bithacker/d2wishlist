#!/usr/bin/env bash

URL=$1
BASE=$(basename ${URL})

echo "Fetching post from ${URL}..."
curl -s "${URL}.json" | jq -r '.[0].data.children[0].data.selftext' > ${BASE}.md
