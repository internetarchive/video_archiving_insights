#!/bin/bash

date=$(date -v-4d +%F)

for i in {0..23}; do
    gzip -d YT-VIDEO-METADATA-$date/YT-VIDEO-METADATA-$date-$(printf "%02d" $i).jsonl.gz &
done
