FROM ubuntu:24.04

# 安装基础工具
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
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 安装 Docker in Docker (DinD)
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
        > /etc/apt/sources.list.d/docker.list && \
    apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 安装 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/bin" sh
# 写入配置文件
COPY uv.toml /root/.config/uv/uv.toml

# 配置 Docker 镜像加速器
RUN mkdir -p /etc/docker && \
    echo '{ "registry-mirrors": ["https://docker.1ms.run", "https://docker.1panel.live", "https://docker-0.unsee.tech"] }' > /etc/docker/daemon.json && \
    chmod 644 /etc/docker/daemon.json

VOLUME /var/lib/docker

ENTRYPOINT ["nohup", "dockerd", "&", "bash"]
