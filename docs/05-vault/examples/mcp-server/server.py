import os
import sys
import hvac
import logging
from typing import Any, List

# MCP SDK 임포트 (가정: mcp 패키지가 설치되어 있음)
# 실제 환경에서는: pip install mcp hvac
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vault-mcp")

# Vault 클라이언트 설정
VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault.vault.svc.cluster.local:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")

if not VAULT_TOKEN:
    # Kubernetes Auth 시도 (실제 운영 환경)
    try:
        f = open('/var/run/secrets/kubernetes.io/serviceaccount/token')
        jwt = f.read()
        client = hvac.Client(url=VAULT_ADDR)
        client.auth.kubernetes.login(role="myapp-role", jwt=jwt)
        logger.info("Logged in using Kubernetes Auth")
    except Exception as e:
        logger.error(f"Failed to authenticate: {e}")
        sys.exit(1)
else:
    # Token Auth (개발 환경)
    client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
    logger.info("Logged in using VAULT_TOKEN")

# MCP 서버 초기화
app = Server("vault-mcp-server")

@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="read_secret",
            description="Read a secret from HashiCorp Vault. Use this to get credentials.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the secret (e.g., secret/data/myapp/database)",
                    }
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="list_secrets",
            description="List secrets at a specific path in HashiCorp Vault.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to list (e.g., secret/metadata/myapp/)",
                    }
                },
                "required": ["path"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent | ImageContent | EmbeddedResource]:
    if name == "read_secret":
        path = arguments.get("path")
        try:
            # KV v2 읽기
            # path가 'secret/data/...' 형식이 아니면 자동으로 수정 고려 가능하지만,
            # 여기서는 명시적인 경로를 기대함.
            if "secret/data/" not in path and "secret/" in path:
                 # secret/myapp/db -> secret/data/myapp/db 변환 시도
                 path = path.replace("secret/", "secret/data/", 1)

            read_response = client.secrets.kv.v2.read_secret_version(
                path=path.replace("secret/data/", ""),
                mount_point="secret"
            )
            data = read_response["data"]["data"]
            return [TextContent(type="text", text=str(data))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error reading secret: {str(e)}")]

    elif name == "list_secrets":
        path = arguments.get("path")
        try:
            # KV v2 리스트
            # path에서 mount point 분리 등이 필요할 수 있음
            # 간단하게 구현
            list_response = client.secrets.kv.v2.list_secrets(
                path=path.replace("secret/metadata/", "").replace("secret/", ""),
                mount_point="secret"
            )
            keys = list_response["data"]["keys"]
            return [TextContent(type="text", text=str(keys))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error listing secrets: {str(e)}")]

    raise ValueError(f"Tool not found: {name}")

async def main():
    # Stdio 서버 실행 (로컬 테스트 또는 파이프 연결용)
    # SSE 서버를 위해서는 mcp[sse] 설치 및 fastAPI 등 연동 필요
    # 여기서는 가장 간단한 stdio 방식으로 구현하여 로그로 동작 확인
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
