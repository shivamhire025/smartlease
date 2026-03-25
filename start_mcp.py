import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uvicorn
from mcp_server import mcp

app = mcp.streamable_http_app(
    allowed_hosts=["*"]  # ← disables host header validation
)
port = int(os.environ.get("PORT", 8000))
uvicorn.run(
    app,
    host="0.0.0.0",
    port=port,
    proxy_headers=True,        # ← CRITICAL for Railway
    forwarded_allow_ips="*",   # ← Trust Railway's proxy
)
EOF