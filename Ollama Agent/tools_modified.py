import asyncio
import ollama
from ollama import ChatResponse

# 定义工具
def subtract_two_numbers(a: int, b: int) -> int:
    """
    Subtract two numbers
    """
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both arguments must be integers")
    print("function subtract_two_numbers called")
    return a - b

def add_two_numbers(a: int, b: int) -> int:
    """
    Add two numbers
    """
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both arguments must be integers")
    print("function add_two_numbers called")
    return a + b

# send email
def send_email(recipients : list[str], subject: str, body: str):
    """
    Sends an email with HTML formatting to the list of email addresses.

    Args:
        recipients (List[str]): The list of email addresses.
        subject (str): The subject of the email.
        body (str): The HTML content of the email.

    Returns:
        str: Status of sending email.
    """
    if recipients and subject and body:
        import os
        import resend
        from dotenv import load_dotenv
        load_dotenv()
        resend.api_key = os.environ.get("RESEND_API_KEY")
        if not resend.api_key:
            return "Error: RESEND_API_KEY environment variable not set."
        params: resend.Emails.SendParams = {

            "from":  "Name <email@gmail.com>", # 更改为你的发送人email， Name 可以替换为任何名称，<email@gmail.com> 替换为你的域名email
            "to": recipients,
            "subject": subject,
            "html": body,
        }
        try:
            email = resend.Emails.send(params)
            return f'Email successfully sent to {recipients}'
        except resend.ResendError as e:
            return f'Error sending email to {recipients}: {e}'
        except Exception as e:
            return f'An unexpected error occurred while sending email to {recipients}: {e}'
    else:
        return "Error: Recipients, subject, and body cannot be empty."


# OpenAI 格式
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

add_two_numbers_tool = {
    'type': 'function',
    'function': {
        'name': 'add_two_numbers',
        'description': 'Add two numbers',
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

send_email_tool = {
    'type': 'function',
    'function': {
        'name': 'send_email',
        'description': 'Send an email to the specified recipients with a given subject and HTML body.',
        'parameters': {
            'type': 'object',
            'required': ['recipients', 'subject', 'body'],
            'properties': {
                'recipients': {
                    'type': 'array',
                    'items': {'type': 'string', 'format': 'email'},
                    'description': 'The list of recipient email addresses.'
                },
                'subject': {'type': 'string', 'description': 'The subject line of the email.'},
                'body': {'type': 'string', 'description': 'The HTML content of the email.'},
            },
        },
    },
}


available_functions = {
    'add_two_numbers': add_two_numbers,
    'subtract_two_numbers': subtract_two_numbers,
    'send_email': send_email,
}
# 用独立函数调用工具，增加代码可读性
async def call_function(tool_call):
    """Call the function specified in the tool call and return the output."""
    if function_to_call := available_functions.get(tool_call.function.name):
        print('Calling function:', tool_call.function.name)
        print('Arguments:', tool_call.function.arguments)
        output = function_to_call(**tool_call.function.arguments)
        print('Function output:', output)
        return output
    else:
        print('Function', tool_call.function.name, 'not found')
        return None
# 主函数
async def main():
    client = ollama.AsyncClient()
    model_name = 'qwen2.5'
    # 设置历史记录和系统提示词
    messages = [{'role': 'system', 'content': 'You are a helpful assistant. you have available tools to used in case you need them'}
]

    # 多轮对话
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        # 添加用户输入到历史记录
        messages.append({'role': 'user', 'content': user_input})

        # 调用模型
        response: ChatResponse = await client.chat(
            model_name,
            messages=messages,
            tools=[add_two_numbers_tool, subtract_two_numbers_tool, send_email_tool],
        )

        # 输出模型响应，观察输出结果
        print('response:', response)
         
        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                output = await call_function(tool_call)
                if output is not None:
                    messages.append(response.message)
                    messages.append({'role': 'tool', 'content': str(output), 'name': tool_call.function.name})

                    # 从模型获取最终响应
                    final_response = await client.chat(model_name, messages=messages)
                    print('Assistant:', final_response.message.content)
                    messages.append({'role': 'assistant', 'content': final_response.message.content})
        else:
            # 没有工具调用，一般回答
            print('Assistant:', response.message.content)
            messages.append({'role': 'assistant', 'content': response.message.content})

        # 观察历史记录
        print(messages)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nGoodbye!')

'''
example:
i want send email to my friend, could you help me?

his email add is tao727188712@gmail.com, you decide email subject and body, i want check Parkview Commons' July report. He didn't deliver on time.
'''
