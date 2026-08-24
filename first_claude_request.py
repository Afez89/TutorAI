"""Send the first request to Claude using the Anthropic SDK."""

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

client = Anthropic()
model = "claude-sonnet-4-20250514"

message = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "What is quantum computing? Answer in one sentence",
        }
    ],
)

for block in message.content:
    if block.type == "text":
        print(block.text)
