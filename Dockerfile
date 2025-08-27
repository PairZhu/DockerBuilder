FROM ubuntu:24.04
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    lsb-release \
    gnupg \
    ca-certificates && \
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/bin" sh
# 写入配置文件
COPY uv.toml /root/.config/uv/uv.toml

# 安装 Docker CLI（不安装 daemon）
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
        > /etc/apt/sources.list.d/docker.list && \
    apt-get update && apt-get install -y docker-ce-cli
