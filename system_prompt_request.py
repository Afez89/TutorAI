"""Send a Claude request with a system prompt."""

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

client = Anthropic()
model = "claude-sonnet-4-6"
messages = []

system_prompt = """
You are a patient math tutor.
Do not directly answer a student's questions.
Guide them to a solution step by step.
"""


def add_user_message(conversation: list[dict[str, str]], content: str) -> None:
    conversation.append({"role": "user", "content": content})


print("Claude math tutor. Type 'quit' or 'exit' to stop.")

while True:
    try:
        user_input = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        break

    if user_input.lower() in {"quit", "exit"}:
        print("Goodbye!")
        break
    if not user_input:
        continue

    add_user_message(messages, user_input)
    stream = client.messages.create(
        model=model,
        messages=messages,
        max_tokens=1000,
        system=system_prompt,
        stream=True,
    )

    print("Claude: ", end="", flush=True)
    response_parts = []
    for event in stream:
        if event.type == "content_block_delta" and event.delta.type == "text_delta":
            print(event.delta.text, end="", flush=True)
            response_parts.append(event.delta.text)

    response_text = "".join(response_parts)
    print()
    messages.append({"role": "assistant", "content": response_text})
