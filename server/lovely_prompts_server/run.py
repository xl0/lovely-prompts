from lovely_prompts_server.server import app

import uvicorn

if __name__ == "__main__":
    uvicorn.run(app)
