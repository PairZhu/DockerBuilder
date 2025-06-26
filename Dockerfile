FROM vllm/vllm-openai:v0.7.3

RUN pip uninstall -y vllm && \
    uv pip install --no-cache-dir --system vllm==0.9.1

ENTRYPOINT ["python3", "-m", "vllm.entrypoints.openai.api_server"]