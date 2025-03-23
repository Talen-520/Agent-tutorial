import asyncio
import ollama
from ollama import ChatResponse

def add_two_numbers(a: int, b: int) -> int:
    """
    Add two numbers

    Args:
      a (int): The first number
      b (int): The second number

    Returns:
      int: The sum of the two numbers
    """
    return a + b

def subtract_two_numbers(a: int, b: int) -> int:
    """
    Subtract two numbers

    Args:
      a (int): The first number
      b (int): The second number

    Returns:
      int: The difference of the two numbers
    """
    return a - b

# Start with initial user query
messages = [{'role': 'user', 'content': 'What is three plus one?'}]
print('Prompt:', messages[0]['content'])

available_functions = {
    'add_two_numbers': add_two_numbers,
    'subtract_two_numbers': subtract_two_numbers,
}

async def main():
    client = ollama.AsyncClient()

    # Main conversation loop - would continue for multiple turns in a real application
    while True:
        # Get response from model
        response: ChatResponse = await client.chat(
            'qwq',
            messages=messages,
            tools=[add_two_numbers, subtract_two_numbers],
        )

        # Add the model's response to messages for history
        messages.append(response.message)
        
        # For this response only, track which tool calls we've processed
        # This resets with each new user request
        processed_tool_ids = set()
        
        if response.message.tool_calls:
            # Process each tool call in this response
            for tool in response.message.tool_calls:
                # Check if we've already processed this specific tool call in this response
                tool_id = getattr(tool, 'id', f"{tool.function.name}-{str(tool.function.arguments)}")
                
                if tool_id in processed_tool_ids:
                    print(f'Skipping duplicate tool call: {tool.function.name}')
                    continue
                
                # Mark this specific tool call as processed for this response only
                processed_tool_ids.add(tool_id)
                
                # Ensure the function is available, and then call it
                if function_to_call := available_functions.get(tool.function.name):
                    print('Calling function:', tool.function.name)
                    print('Arguments:', tool.function.arguments)
                    output = function_to_call(**tool.function.arguments)
                    print('Function output:', output)
                    
                    # Add the function output to messages
                    messages.append({
                        'role': 'tool', 
                        'content': str(output), 
                        'name': tool.function.name
                    })
                else:
                    print('Function', tool.function.name, 'not found')
                    print()
            # Get final response from model with function outputs
            final_response = await client.chat('qwq', messages=messages)
            print('Final response:', final_response.message.content)
            
            # Add the final response to the conversation history
            messages.append(final_response.message)
        else:
            print('Response:', response.message.content)
        
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nGoodbye!')