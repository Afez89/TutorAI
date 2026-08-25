import Anthropic from '@anthropic-ai/sdk';

const teacherPrompt = `You are a patient, supportive teacher who helps learners build understanding, confidence, and independent problem-solving skills.

Teach with guided discovery:
- Clarify the learner's goal and assess what they already know.
- Break complex topics into manageable steps.
- Prefer questions, hints, and partial steps before giving a complete solution.
- Ask the learner to explain their reasoning when practical.
- Use simple examples, then increase difficulty gradually.
- Treat mistakes as useful evidence and correct misconceptions constructively.
- Define unfamiliar terms and state important assumptions.
- End with a concise summary and a practical next step.

Be accurate, respectful, inclusive, and encouraging. Acknowledge uncertainty when information needs verification. Maintain appropriate professional boundaries and protect privacy.`;

function jsonResponse(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

export default async (request) => {
  if (request.method !== 'POST') {
    return jsonResponse(405, { error: 'Method not allowed.' });
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    return jsonResponse(500, { error: 'ANTHROPIC_API_KEY is not configured in Netlify.' });
  }

  try {
    const payload = await request.json();
    const messages = payload?.messages;
    if (!Array.isArray(messages) || messages.length === 0) {
      return jsonResponse(400, { error: 'At least one message is required.' });
    }

    const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
    const response = await client.messages.create({
      model: process.env.CLAUDE_MODEL || 'claude-sonnet-4-6',
      max_tokens: 1200,
      system: teacherPrompt,
      messages,
    });
    const text = response.content
      .filter((block) => block.type === 'text')
      .map((block) => block.text)
      .join('');

    return jsonResponse(200, { response: text });
  } catch (error) {
    console.error('Claude request failed:', error);
    return jsonResponse(502, { error: 'Claude could not respond right now.' });
  }
};
