fastapi[standard]
ollama

端口测试 windows
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d "{\"model\": \"llama3.2\", \"messages\": [{\"role\": \"user\", \"content\": \"Why is the sky blue?\"}]}"

macOS
curl -X POST "http://localhost:8000/chat" \
-H "Content-Type: application/json" \
-d "{\"model\": \"llama3.2\", \"messages\": [{\"role\": \"user\", \"content\": \"Why is the sky blue?\"}]}"