import os
import sys

# Ensure root package omnicore is importable
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from omnicore.dashboard.api import app

# Vercel ASGI serverless app export
handler = app
