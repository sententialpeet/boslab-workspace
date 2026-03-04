import gradio as gr
import re
import os
from openai import OpenAI
import tempfile

def load_openai_key():
    memory_path = '/home/boslabserver/.openclaw/workspace/MEMORY.md'
    try:
        with open(memory_path, 'r') as f:
            content = f.read()
        match = re.search(r'API Key:\s*`([^`]+)`', content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else None
    except:
        return None

def get_client():
    key = load_openai_key()
    if not key:
        raise ValueError("No OpenAI key in MEMORY.md")
    return OpenAI(api_key=key)

def transcribe(audio):
    if not audio:
        return "No audio. Click mic ▶️ and speak."
    try:
        client = get_client()
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=(os.path.basename(audio), open(audio, 'rb'), 'audio/wav'),
            response_format="text"
        )
        return transcript
    except Exception as e:
        return f"STT failed: {str(e)}"

def chat_response(transcript, history):
    try:
        client = get_client()
        messages = [{"role": "system", "content": "Casual friend. Short replies."}]
        for pair in history:
            messages.append({"role": "user", "content": pair[0]})
            messages.append({"role": "assistant", "content": pair[1]})
        messages.append({"role": "user", "content": transcript})
        response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, max_tokens=100)
        history.append([transcript, response.choices[0].message.content])
        return history, ""
    except Exception as e:
        return history, f"Chat failed: {str(e)}"

def create_tts(text):
    if not text:
        return None
    try:
        client = get_client()
        speech = client.audio.speech.create(model="tts-1", voice="alloy", input=text[:250])
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp.write(speech.content)
            return tmp.name
    except:
        return None

with gr.Blocks(title="Voice Chat") as demo:
    gr.Markdown("## 🗣️ Voice Chat - Mic → STT → GPT → TTS")
    gr.Markdown("Click mic ▶️ (red), speak, stop, Submit. Bot speaks back!")
    
    with gr.Row():
        audio_in = gr.Audio(sources=["microphone"], type="filepath", label="🎤 Mic")
    
    with gr.Row():
        btn = gr.Button("Submit Voice", variant="primary")
    
    chatbot = gr.Chatbot(height=350)
    audio_out = gr.Audio(label="🔊 Reply", autoplay=True)
    status = gr.Textbox(label="Transcript", interactive=False)
    
    def relay(audio):
        transcript = transcribe(audio)
        history = chatbot.value or []
        history, err = chat_response(transcript, history)
        tts_file = create_tts(history[-1][1] if history else "")
        return history, tts_file, transcript, gr.update()
    
    btn.click(relay, audio_in, [chatbot, audio_out, status])
    
demo.launch(server_name="0.0.0.0", server_port=7861, show_error=True)

print("STT UI launched on http://0.0.0.0:7861")
