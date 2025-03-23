import asyncio
import ollama
from ollama import ChatResponse

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

# OpenAI format
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

# Initialize messages with a system message to set the context
messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]

available_functions = {
    'add_two_numbers': add_two_numbers,
    'subtract_two_numbers': subtract_two_numbers,
}

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

async def main():
    client = ollama.AsyncClient()
    model_name = 'qwq'
    while True:
        # Get user input
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        # Add user input to messages
        messages.append({'role': 'user', 'content': user_input})

        # Send the message to the model
        response: ChatResponse = await client.chat(
            model_name,
            messages=messages,
            tools=[add_two_numbers_tool, subtract_two_numbers_tool],
        )

        print('Assistant:', response.message.content) # model response is empty

        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                output = await call_function(tool_call)
                if output is not None:
                    messages.append(response.message)
                    messages.append({'role': 'tool', 'content': str(output), 'name': tool_call.function.name})

                    # Get final response from model with function outputs
                    final_response = await client.chat(model_name, messages=messages)
                    print('Assistant:', final_response.message.content)
                    messages.append({'role': 'assistant', 'content': final_response.message.content})
        else:
            # If no tool calls, just print the model's response
            print('Assistant:', response.message.content)
            messages.append({'role': 'assistant', 'content': response.message.content})

        # 原始模型数据
        print(messages)

        import json
        # 将整个响应转换为格式化的 JSON 字符串
        print("Full response (JSON formatted):")
        print(json.dumps(messages, indent=2))


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nGoodbye!')