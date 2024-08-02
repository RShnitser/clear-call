from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, render_template
from io import BytesIO, BufferedReader

load_dotenv()
client = OpenAI()
app = Flask(__name__)

@app.route("/")
def home():
  # response = client.chat.completions.create(
  #   model="gpt-3.5-turbo",
  #   messages=[
  #     {"role": "system", "content": "This is a test."},
  #     {"role": "user", "content": "Test"},
  #   ]
  # )
  # text = response.choices[0].message.content
  return render_template("index.html")


@app.route("/upload", methods = ['POST'])
def upload():

  if request.method == 'POST':   
    file = request.files['file']

    if file:
      buffer = BytesIO()
      file.save(buffer)
      buffer.name = file.filename
     
      transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=buffer
      )
      print(transcription.text)
      # print(data)
  #   if data:
  #     return "Success"
  #   else:
  #     return "Fail"
  # return render_template("index.html")
  return "upload"