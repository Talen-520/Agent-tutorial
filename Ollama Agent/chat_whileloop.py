import asyncio
from ollama import AsyncClient

async def chat(messages):
    try:
        async for part in await AsyncClient().chat(model='llama3.2', messages=messages, stream=True):
            print(part['message']['content'], end='', flush=True)
        return part['message']['content']  # Return the last response
    except Exception as e:
        return f"An error occurred: {e}"


async def main():
    system_prompt = 'You are a helpful AI assistant.'

    chat_history = [
        {'role': 'system', 'content': system_prompt}
    ]
    
    while True:
        user_input = input('\n\nUser: ')
        if user_input.lower() == 'exit':
            break
        
        chat_history.append({'role': 'user', 'content': user_input})
        assistant_response = await chat(chat_history)
        chat_history.append({'role': 'assistant', 'content': assistant_response})

if __name__ == '__main__':
    asyncio.run(main())