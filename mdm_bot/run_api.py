"""
FastAPI server entry point
"""
import uvicorn
from mdm_bot.api import app


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2000)
