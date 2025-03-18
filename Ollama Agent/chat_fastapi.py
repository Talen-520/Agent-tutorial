import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ollama import AsyncClient
from typing import List, Dict, Any

app = FastAPI(title="Ollama Chat API")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest):
    try:
        # Convert Pydantic models to dictionaries for ollama client
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Call Ollama client
        response = await AsyncClient().chat(
            model=request.model,
            messages=messages
        )
        
        # Extract the response content from Ollama's response
        return ChatResponse(response=response["message"]["content"])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Ollama API: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)