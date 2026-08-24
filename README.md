# Claude API client

Install the Anthropic SDK:

```powershell
python -m pip install -r requirements.txt
```

Set the API key without putting it in source control. In PowerShell:

```powershell
$env:ANTHROPIC_API_KEY = "your-rotated-key"
```

Use the client:

```python
from claude_client import ClaudeClient

claude = ClaudeClient()
answer = claude.ask("Explain API testing in one paragraph.")
print(answer)
```

`CLAUDE_MODEL` can override the default model. Never commit a real API key or a populated `.env` file.
