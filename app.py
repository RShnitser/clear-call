from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, render_template, send_file
from io import BytesIO
from src import ai
from flask_bcrypt import Bcrypt
import os
from flask_sqlalchemy import SQLAlchemy


load_dotenv()
client = OpenAI()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite+{os.environ.get("DB_URI")}/?authToken={os.environ.get("DB_AUTH")}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    documents = db.relationship('Document', backref='user', lazy=True)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    transcript = db.Column(db.LargeBinary)
    summary = db.Column(db.LargeBinary)

@app.route("/")
def home():
 
  return render_template("index.html")

@app.route("/swap_create")
def swap_account():
  return render_template("create_user.html")

@app.route("/swap_login")
def swap_login():
  return render_template("login.html")


@app.route("/upload/<user_id>", methods = ['POST'])
def upload(user_id):
  int_user_id = int(user_id)
  if request.method == 'POST':   
    file = request.files['file']

    if file:
      buffer = BytesIO()
      file.save(buffer)
      buffer.name = file.filename
      transcript = ai.transcribe_audio(client, buffer)
      summary = ai.parse_text(transcript)
      document = Document(user_id=1, transcript=transcript.encode("utf-8"), summary=summary.encode("utf-8"))
      db.session.add(document)
      db.session.commit()


    return render_template("message.html",transcript_link=f"download_transcript/{int_user_id}", summary_link=f"download_summary/{int_user_id}", chat_id=f"chat/{int_user_id}", text=transcript)
  return render_template("upload.html", upload_link=f"upload/{int_user_id}")

@app.route("/chat/<id>", methods = ['POST'] )
def chat(id):
  question = request.form.get('chat')
  int_id = int(id)
  document = Document.query.filter(Document.id == int_id).first()
  answer = ai.answer_question(question, document.transcript.decode("utf-8"))
  return render_template("chat_response.html", question=question, answer=answer)


@app.route("/download_transcript/<id>")
def download_transcript(id):
  int_id = int(id)
  document = Document.query.filter(Document.id == int_id).first()
  content = BytesIO(document.transcript)
  return send_file(content, download_name="transcript.txt", mimetype="text/plain", as_attachment=True)

@app.route("/download_summary/<id>")
def download_summary(id):
  int_id = int(id)
  document = Document.query.filter(Document.id == int_id).first()
  content = BytesIO(document.summary)
  return send_file(content, download_name="summary.txt", mimetype="text/plain", as_attachment=True)

@app.route("/back")
def back():
  return render_template("upload.html")

@app.route("/create_account", methods = ['POST'])
def create_account():
  username = request.form["name"]
  password = request.form["password"]
  if username and password:
    hash = bcrypt.generate_password_hash(password, 10).decode("utf-8")
    user = User(name=username, password=hash)
    db.session.add(user)
    db.session.commit()
    return render_template("upload.html", upload_link=f"upload/{user.id}")
  return render_template("create_user.html")

@app.route("/login", methods = ['POST'])
def login():
  username = request.form["name"]
  password = request.form["password"]
  user = User.query.filter(User.name == username).first()
  if user:
    if bcrypt.check_password_hash(user.password, password):
      return render_template("upload.html", upload_link=f"upload/{user.id}")
  return render_template("login.html")