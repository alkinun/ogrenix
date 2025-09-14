vllm serve google/gemma-3-12b-it \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.9 \
    --quantization bitsandbytes \
    --dtype bfloat16 \
