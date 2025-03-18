import asyncio
from ollama import AsyncClient
# 参数：messages：对话历史，model：模型名称 
async def chat(messages,model='llama3.2'):
    async for part in await AsyncClient().chat(model=model, messages=messages, stream=True):
        print(part['message']['content'], end='', flush=True)
    return part['message']['content']  # Return the last response


async def main():
    # 设置系统提示词
    system_prompt = 'You are a helpful AI assistant.'

    # 初始化对话历史
    chat_history = [
        {'role': 'system', 'content': system_prompt}
    ]
    # 开始对话循环
    while True:
        user_input = input('\n\nUser: ')
        if user_input.lower() == 'exit':
            break
        # 将用户消息添加到历史
        chat_history.append({'role': 'user', 'content': user_input})
        # 调用chat函数获取助手响应
        assistant_response = await chat(chat_history,model='llama3.2')

        # 将回答添加到历史
        chat_history.append({'role': 'assistant', 'content': assistant_response})

if __name__ == '__main__':
    asyncio.run(main())