import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from mcp_server import mcp

app = mcp.streamable_http_app()

port = int(os.environ.get("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

No `if __name__` block — just runs directly.

Then update the Railway start command to:
```
python start_mcp.py