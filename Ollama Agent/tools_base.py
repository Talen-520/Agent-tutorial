import asyncio
import ollama
from ollama import ChatResponse

# docstring，注释，让模型理解函数用途和如何使用
def add_two_numbers(a: int, b: int) -> int:
    """
    Add two numbers

    Args:
      a (int): The first number
      b (int): The second number

    Returns:
      int: The sum of the two numbers
    """
    print("function add_two_numbers called")
    return a + b


def subtract_two_numbers(a: int, b: int) -> int:
    """
    Subtract two numbers
    """
    print("function subtract_two_numbers called")
    return a - b


# send email
def send_email(to  : list[str], subject: str, body: str):
    """
    send email to the list of email addresses

    Args:
      to (list[str]): The list of email addresses
      subject (str): The subject of the email
      body (str): The body of the email

    Returns:
      bool: True if the email is sent successfully, False otherwise
    """
    import os
    import resend
    from dotenv import load_dotenv
    load_dotenv()

    resend.api_key = os.environ["RESEND_API_KEY"]
    params: resend.Emails.SendParams = {
        "from": "Tao <TaoHu@rabrisai.com>",
        "to": to,
        "subject": subject,
        "html": body,
    }

    email = resend.Emails.send(params)
    return True if email else False

# 手动注释, 在ollama中docstring二选一，也可都写
subtract_two_numbers_tool = {
    'type': 'function',
    'function': {
        'name': 'subtract_two_numbers',
        'description': 'Subtract two numbers',
        'parameters': {
            'type': 'object',
            'required': ['a', 'b'],
            'properties': {
                'a': {'type': 'integer', 'description': 'The first number'},
                'b': {'type': 'integer', 'description': 'The second number'},
            },
        },
    },
}

messages = [{'role': 'user', 'content': '三加一等于多少?'}]
print('Prompt:', messages[0]['content'])

available_functions = {
    'add_two_numbers': add_two_numbers,
    'subtract_two_numbers': subtract_two_numbers,
    'send_email': send_email,
}


async def main():
    client = ollama.AsyncClient()

    response: ChatResponse = await client.chat(
        'qwen2.5',
        messages=messages,
        tools=[add_two_numbers, subtract_two_numbers_tool, send_email],
    )

    if response.message.tool_calls:
        # 遍历函数并调用所有可用工具
        for tool in response.message.tool_calls:
            # 确保函数可用，然后调用它
            if function_to_call := available_functions.get(tool.function.name):
                print('Calling function:', tool.function.name)
                print('Arguments:', tool.function.arguments)
                output = function_to_call(**tool.function.arguments)
                print('Function output:', output)
            else:
                # 如果没有可用工具，则输出错误
                print('Function', tool.function.name, 'not found')
    if response.message.tool_calls:
        messages.append(response.message)
        messages.append({'role': 'tool', 'content': str(
            output), 'name': tool.function.name})
        # 从模型获取最终响应
        final_response = await client.chat('qwen2.5', messages=messages)
        print('Final response:', final_response.message.content)

    else:
        print('No tool calls returned from model')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nGoodbye!')
