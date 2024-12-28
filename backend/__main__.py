"""
Driver code for the uvicorn server
"""
import uvicorn
from backend.server.server import app

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
