import asyncio
from ollama import AsyncClient
# 异步
async def chat():
  messages = [
    {
      'role': 'user',
      'content': 'Why is the sky blue?',
    },
  ]  
  async for part in await AsyncClient().chat(model='llama3.2', messages=messages, stream=True):
    print(part['message']['content'], end='', flush=True)

if __name__ == '__main__':
  asyncio.run(chat())