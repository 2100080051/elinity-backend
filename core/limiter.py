from fastapi import FastAPI,Depends,HTTPException,status
import time
from fastapi.middleware.cors import CORSMiddleware 


class RateLimiter:
    
    def __init__(self,requests:int=5,window:int=60):
        self.requests = requests # No of requests allowed
        self.window = window # Time window in seconds
        self.clients = {}

    async def __call__(self,client_id:str="default"):
        current_time = time.time()

        # Clean old records  or initialize new client
        if client_id in self.clients:
            self.clients[client_id] = [ts for ts in self.clients[client_id] if current_time - ts < self.window]
        else:
            self.clients[client_id] = [] # Initialize as empty list for this client

        # Check if limit exceeded
        if len(self.clients[client_id]) >= self.requests:
            raise HTTPException(status_code=429,detail="Rate limit exceeded.")
        
        # Add current request timestamp
        self.clients[client_id].append(current_time)

        return True


