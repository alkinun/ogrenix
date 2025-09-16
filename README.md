```bash
git clone https://github.com/alkinun/ogrenix.git
pip install -U matplotlib markdown flask openai
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc   | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null   && echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main"   | sudo tee /etc/apt/sources.list.d/ngrok.list   && sudo apt update   && sudo apt install ngrok
ngrok config add-authtoken ...
export OPENROUTER_API_KEY=...
python3 app_cloud.py & ngrok http http://localhost:5002
```
