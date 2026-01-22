# FastAPI Template

[English](README.en.md) | [中文](README.md)

A simple yet comprehensive FastAPI template.

> [!WARNING]
> This project is for learning and reference purposes only. Please thoroughly test before using in production environments.

## Running

### Development Environment

1. Create a `.env` file by referencing [`.env.example`](.env.example) and configure environment variables.

2. Use [uv](https://docs.astral.sh/uv/) to run the project. uv will automatically create a virtual environment, install dependencies, and start the project.

   ```bash
   uv run run.py
   ```

### Production Environment

In production environments, the project should be run via docker compose.

1. Create a `.env` file by referencing [`.env.example`](.env.example) and configure environment variables.

2. Run the project via docker compose.

   ```bash
   docker compose up -d
   ```
