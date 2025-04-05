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

# 设置历史记录和系统提示词
messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]

available_functions = {
    'add_two_numbers': add_two_numbers,
    'subtract_two_numbers': subtract_two_numbers,
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
            tools=[add_two_numbers_tool, subtract_two_numbers_tool],
        )

        # 输出模型响应，观察输出结果
        print('response:', response)
        print('response message tool_calls:', response.message.tool_calls)
        print('response message content:', response.message.tool_calls)
         
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