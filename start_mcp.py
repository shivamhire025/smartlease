import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uvicorn
from mcp_server import mcp

app = mcp.streamable_http_app()
port = int(os.environ.get("PORT", 8080))
uvicorn.run(app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")