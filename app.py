from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, render_template
from io import BytesIO


load_dotenv()
client = OpenAI()
app = Flask(__name__)

@app.route("/")
def home():
 
  return render_template("index.html")


@app.route("/upload", methods = ['POST'])
def upload():

  if request.method == 'POST':   
    file = request.files['file']

    if file:
      buffer = BytesIO()
      file.save(buffer)
      buffer.name = file.filename
     
      return render_template("message.html", text="success")
  return render_template("message.html", text="fail")

@app.route("/back")
def back():
  return render_template("upload.html")