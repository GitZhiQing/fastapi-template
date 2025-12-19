# FastAPI Template

> [!WARNING]
> 项目仅供学习和参考目的，生产环境使用前请充分测试。

一个简单但完善的 FastAPI 模板，目前已配置完善以下功能：

- 兼容 Docker 部署环境
- 异步 PostgreSQL 连接
- 异步 Redis 连接

## 运行

项目使用 [uv](https://docs.astral.sh/uv/) 管理环境。

在项目根目录运行以下命令，uv 将自动创建虚拟环境并安装依赖，然后启动项目。

```bash
uv run run.py
```
