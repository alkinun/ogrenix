vllm serve unsloth/GLM-4-32B-0414-unsloth-bnb-4bit \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 10000 \
    --gpu-memory-utilization 0.9 \
    --dtype bfloat16 \
