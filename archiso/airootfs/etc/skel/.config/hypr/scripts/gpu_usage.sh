#!/usr/bin/env bash
# GPU utilization query for NVIDIA GeForce RTX 3080 Ti
val=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -n 1 | tr -d '[:space:]')
if [ -n "$val" ]; then
    echo "$val"
else
    echo "0"
fi
