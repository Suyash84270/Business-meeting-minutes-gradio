# app.py - Gradio Meeting Minutes app
import os, traceback
from openai import OpenAI
import gradio as gr

# Read OpenAI key from environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment. Add it to Space secrets or env vars.")
client = OpenAI(api_key=OPENAI_API_KEY)

AUDIO_MODEL = "whisper-1"
CHAT_MODEL  = "gpt-4o-mini"

def generate_minutes(audio_file):
    try:
        if not audio_file:
            return "No audio file uploaded.", ""
        audio_path = audio_file[0] if isinstance(audio_file, (tuple, list)) else audio_file

        # Transcription
        try:
            with open(audio_path, "rb") as af:
                tr = client.audio.transcriptions.create(model=AUDIO_MODEL, file=af, response_format="text")
            transcription = (
                tr if isinstance(tr, str)
                else tr.get("text") if isinstance(tr, dict) and "text" in tr
                else getattr(tr, "text", str(tr))
            )
        except Exception as e:
            return f"[Transcription error] {e}", traceback.format_exc()

        # Generation
        system_prompt = ("You are an assistant that produces minutes of meetings from transcription, "
                         "with summary, key discussion points, takeaways and action items with owners, in markdown.")
        try:
            chat_resp = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcription}
                ],
                max_tokens=900,
                temperature=0.2,
            )
            try:
                minutes = chat_resp.choices[0].message.content
            except Exception:
                minutes = str(chat_resp)
            minutes = minutes.strip() if isinstance(minutes, str) else str(minutes).strip()
            return transcription, minutes
        except Exception as e:
            return f"[Generation error] {e}", traceback.format_exc()

    except Exception as e:
        return f"[Fatal error] {e}", traceback.format_exc()

with gr.Blocks(title="Meeting Minutes Generator") as demo:
    gr.Markdown("# 📋 Meeting Minutes Generator")
    gr.Markdown("Upload meeting audio and receive a formatted meeting minutes document (Markdown).")

    with gr.Row():
        audio_input = gr.Audio(type="filepath", label="Upload meeting audio (wav/mp3/m4a)")
        run_btn = gr.Button("Generate Minutes")

    with gr.Tabs():
        with gr.TabItem("Transcript"):
            transcript_out = gr.Textbox(label="Transcript", lines=10)
        with gr.TabItem("Meeting Minutes"):
            minutes_out = gr.Markdown()

    def _process(a):
        return generate_minutes(a)

    run_btn.click(_process, inputs=[audio_input], outputs=[transcript_out, minutes_out])

if __name__ == "__main__":
    demo.launch()
