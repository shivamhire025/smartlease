import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server import mcp
from starlette.middleware import Middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

# Get the base app
app = mcp.streamable_http_app()

# Wrap it — allow ALL hosts (Railway's healthcheck uses healthcheck.railway.app)
from starlette.applications import Starlette
from starlette.routing import Mount

wrapped = Starlette(
    routes=[Mount("/", app=app)],
    middleware=[
        Middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    ]
)

port = int(os.environ.get("PORT", 8080))
uvicorn.run(wrapped, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")