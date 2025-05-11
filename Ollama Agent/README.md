### 安装依赖包
```bash
uv add ollama resend python-dotenv
```
### 请按以下顺序进行浏览:

1. chat.py

2. chat_async.py

3. chat_history.py

4. tools_base.py

5. tools_modified.py

tools_modified.py 包含三个工具:
```bash
available_functions = {
    'add_two_numbers': add_two_numbers,
    'subtract_two_numbers': subtract_two_numbers,
    'send_email': send_email,
}
```
加法函数，减法函数，发送邮件函数.

发送邮件函数需要resend API，如果需要测试请在这里注册一个账号 [Resend](https://resend.com/)

在跟目录创建.env 文件
```bash
RESEND_API_KEY=<你的API KEY>
```
在send_email函数中替换为你的域名email（已标注）

