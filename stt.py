#!/usr/bin/env python3
import openai
import re
import sys
import os

def load_openai_key():
    memory_path = '/home/boslabserver/.openclaw/workspace/MEMORY.md'
    if not os.path.exists(memory_path):
        raise FileNotFoundError(f'MEMORY.md not found: {memory_path}')
    
    with open(memory_path, 'r') as f:
        content = f.read()
    
    # Extract OpenAI key from ## OpenAI section
    match = re.search(r'API Key:\s*`([^`]+)`', content)
    if not match:
        raise ValueError('OpenAI API key not found in MEMORY.md')
    
    return match.group(1)

def transcribe_audio(file_path, model='whisper-1', response_format='text'):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'Audio file not found: {file_path}')
    
    client = openai.OpenAI(api_key=load_openai_key())
    
    with open(file_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format=response_format
        )
    return transcript

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: ./stt.py <audio_file>')
        print('Supports: mp3, mp4, mpeg, mpga, m4a, wav, webm')
        print('Max 25MB. Outputs plain text.')
        sys.exit(1)
    
    audio_file = sys.argv[1]
    try:
        result = transcribe_audio(audio_file)
        print(result)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
