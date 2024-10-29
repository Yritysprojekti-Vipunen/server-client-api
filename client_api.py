from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

class ClientAPI:
    def __init__(self):
        self.app = FastAPI()
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"], #http://localhost:5173
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.router = APIRouter()
        self.router.add_api_route(path="/", endpoint=self.hello, methods=["GET"])

        self.include_routes()

    def hello(self):
        return {"response": "Server is listening."}
    
    def include_routes(self):
        self.app.include_router(self.router)

    def run(self):
        uvicorn.run(app=self.app, host="127.0.0.1", port=1024)
