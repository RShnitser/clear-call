from app import client
from io import BytesIO

def transcribe_audio(buffer: BytesIO)->str:
  transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=buffer
      )
  return transcription.text

def parse_text(input: str)->str:
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "This is a test."},
      {"role": "user", "content": input},
    ]
  )
  text = response.choices[0].message.content
  return text