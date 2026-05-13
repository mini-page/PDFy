import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../services/analyzer"))

from app.main import app

handler = app  # Vercel Python handler