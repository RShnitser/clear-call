from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, render_template

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
  file = request.files['file']
  if file:
    content = file.read()
    if content:
      return "Success"
    else:
      return "Fail"
  return render_template("index.html")