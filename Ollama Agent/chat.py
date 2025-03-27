from ollama import chat

# 基础对话
messages = [
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
]

response = chat('llama3.2', messages=messages)
print(response['message']['content'])

'''
# 格式化结果 
from ollama import chat
import json

messages = [
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
]

response = chat('llama3.2', messages=messages)

# 将 response 模型数据转换成字典
response_dict = response.model_dump() 
# 将整个响应转换为格式化的 JSON 字符串
print("Full response (JSON formatted):")
print(json.dumps(response_dict, indent=2))

# 将 message 部分转换为格式化的 JSON 字符串
print("\nMessage part (JSON formatted):")
print(json.dumps(response_dict['message'], indent=2))

# 打印 content 部分
print("\nContent part:")
print(response_dict['message']['content'])
'''