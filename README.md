# FastAPI Template

一个简单但完善的 FastAPI 模板。

> [!WARNING]
> 项目仅供学习和参考，生产环境使用前请充分测试。

## 运行

### 开发环境

1. 参考 [`.env.example`](.env.example) 创建 `.env` 文件，配置环境变量。

2. 使用 [uv](https://docs.astral.sh/uv/) 运行项目，uv 将自动创建虚拟环境、安装依赖，并启动项目。

   ```bash
   uv run run.py
   ```

### 生产环境

生产环境下，需要通过 docker compose 运行项目。

1. 参考 [`.env.example`](.env.example) 创建 `.env` 文件，配置环境变量。

2. 通过 docker compose 运行项目。

   ```bash
   docker compose up -d
   ```
