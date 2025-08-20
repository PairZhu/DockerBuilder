FROM ubuntu:24.04
# 写入配置文件
COPY uv.toml /root/.config/uv/uv.toml
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget && \
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/bin" sh