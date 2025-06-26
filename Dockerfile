FROM vllm/vllm-openai:v0.7.3

RUN pip uninstall -y vllm && \
    uv pip install --no-cache-dir --system torch==2.8.0 torchvision==0.22.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu124 && \
    uv pip install --no-cache-dir --system vllm==0.9.1

ENTRYPOINT ["python3", "-m", "vllm.entrypoints.openai.api_server"]