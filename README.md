# Meeting Minutes Generator (Gradio)

This Gradio app:
- Accepts audio (wav/mp3/m4a)
- Transcribes with OpenAI Whisper
- Generates meeting minutes using OpenAI chat API (v1 client)

## Deploy
1. Add OPENAI_API_KEY in the deployment environment (Hugging Face Space secrets).
2. Run `app.py` (Gradio will serve the UI).

## Notes
- Do NOT commit your OPENAI_API_KEY to GitHub.
