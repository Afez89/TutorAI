# AI Tutor

A guided teacher chat application powered by Claude. The assistant helps learners reason through questions step by step instead of simply giving answers.

Install the Anthropic SDK:

```powershell
python -m pip install -r requirements.txt
```

Set the API key without putting it in source control. In PowerShell:

```powershell
$env:ANTHROPIC_API_KEY = "your-rotated-key"
```

Use the local Python client:

```python
from claude_client import ClaudeClient

claude = ClaudeClient()
answer = claude.ask("Help me understand fractions step by step.")
print(answer)
```

`CLAUDE_MODEL` can override the default model. Never commit a real API key or a populated `.env` file.

## Deploy to Netlify

This project includes a Netlify Function for the Claude API, so the API key stays on the server and is never sent to the browser.

1. In Netlify, choose **Add new project** and import the `Afez89/TutorAI` GitHub repository.
2. Leave the build command empty. The repository's `netlify.toml` publishes `static/` and configures the function directory.
3. In **Site configuration > Environment variables**, add `ANTHROPIC_API_KEY` with your current key. Add `CLAUDE_MODEL` with `claude-sonnet-4-6` if you want to set it explicitly.
4. Deploy the site.

The frontend continues to call `/api/chat`; Netlify routes that path to `netlify/functions/chat.mjs`.

## Uploads

The chat accepts PNG, JPEG, GIF, and WebP images, PDFs, and text files such as TXT, Markdown, CSV, and JSON. Files are converted into Claude content blocks in the browser and sent through the server-side function; each file is limited to 3 MB.
