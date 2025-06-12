import argparse
import docker
import json
import os
import sys
import tarfile
import tempfile

VERSION = "1.0.0"


def image_export(client, image_id, dst_path):
    """导出镜像到指定路径（已解压）"""
    try:
        # 获取镜像的 tar 流
        image_stream = client.api.get_image(image_id)

        # 创建临时 tar 文件
        with tempfile.NamedTemporaryFile(delete=False) as tmp_tar:
            for chunk in image_stream:
                tmp_tar.write(chunk)
            tmp_tar_path = tmp_tar.name

        # 解压到目标目录
        with tarfile.open(tmp_tar_path, "r") as tar:
            tar.extractall(dst_path)

        # 清理临时文件
        os.unlink(tmp_tar_path)

    except Exception as e:
        raise Exception(f"image export failed: {e}")


def image_tar(path, output_stream):
    """将目录打包为 tar 流"""
    try:
        with tarfile.open(fileobj=output_stream, mode="w") as tar:
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, path)
                    tar.add(file_path, arcname=arcname)
    except Exception as e:
        raise Exception(f"tar creation failed: {e}")


def diff_export(client, image1_name, image2_name, output_stream):
    """执行镜像层去重导出"""
    try:
        # 检查两个镜像
        image1 = client.api.inspect_image(image1_name)
        image2 = client.api.inspect_image(image2_name)

        if not image2.get("RepoTags"):
            raise Exception(f"{image2_name} repo tags is empty")

        # 查找重复的文件层
        layers1 = image1["RootFS"]["Layers"]
        layers2 = image2["RootFS"]["Layers"]

        duplicate_layers = []
        for i, layer in enumerate(layers1):
            if i >= len(layers2) or layer != layers2[i]:
                break
            duplicate_layers.append(layer)

        print(f"Found {len(duplicate_layers)} duplicate layers")
        for i, layer in enumerate(duplicate_layers):
            print(f"Layer {i + 1}: {layer}")
        print()

        if not duplicate_layers:
            raise RuntimeError("No duplicate layers found")

        # 创建临时目录
        with tempfile.TemporaryDirectory(prefix="docker-import-") as tmp_dir:
            # 导出 image2
            image_export(client, image2["RepoTags"][0], tmp_dir)

            # 读取 manifest.json
            manifest_path = os.path.join(tmp_dir, "manifest.json")
            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            # 找到对应的层信息
            layers = []
            image2_id = image2["Id"].replace("sha256:", "")
            for item in manifest:
                if image2_id in item["Config"]:
                    layers = item["Layers"]
                    break

            # 删除重复层（将文件截断为空）
            for duplicate_layer in duplicate_layers:
                duplicate_layer_id = duplicate_layer.replace("sha256:", "")
                for layer in layers:
                    if duplicate_layer_id in layer:
                        layer_path = os.path.join(tmp_dir, layer)
                        if os.path.exists(layer_path):
                            # 截断文件为空
                            with open(layer_path, "w") as f:
                                pass
                        else:
                            print(
                                f"Warning: Layer {duplicate_layer_id} not found in {tmp_dir}"
                            )

            # 重新打包
            image_tar(tmp_dir, output_stream)

    except Exception as e:
        raise Exception(f"diff export failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        prog="dockerdiff", description="Docker 镜像层去重工具"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # save 子命令
    save_parser = subparsers.add_parser("save", help="保存去重后的镜像")
    save_parser.add_argument("image1", help="第一个镜像")
    save_parser.add_argument("image2", help="第二个镜像")
    save_parser.add_argument("-o", "--output", help="输出文件路径（默认输出到 STDOUT）")

    # version 子命令
    version_parser = subparsers.add_parser("version", help="显示版本信息")

    args = parser.parse_args()

    if args.command == "version":
        print(VERSION)
        return

    if args.command == "save":
        # 初始化 Docker 客户端
        client = docker.from_env(timeout=60 * 10)

        # 确定输出流
        if args.output:
            output_stream = open(args.output, "wb")
        else:
            output_stream = sys.stdout.buffer

        try:
            # 执行去重导出
            diff_export(client, args.image1, args.image2, output_stream)
            print(f"去重导出完成，输出到: {args.output if args.output else 'STDOUT'}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)  # Move exit(1) here to ensure it only runs on error
        finally:
            if args.output:
                output_stream.close()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
