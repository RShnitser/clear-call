from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, render_template, send_file
from io import BytesIO
from src import ai
from flask_bcrypt import Bcrypt
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, ForeignKey, LargeBinary, DateTime
from sqlalchemy.orm import Mapped, mapped_column
import datetime

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite+{os.environ.get("DB_URI")}/?authToken={os.environ.get("DB_AUTH")}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

bcrypt = Bcrypt(app)

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(50))

class Document(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    transcript: Mapped[LargeBinary] = mapped_column(LargeBinary())
    summary: Mapped[LargeBinary] = mapped_column(LargeBinary())
    date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.datetime.now())
    label: Mapped[str] = mapped_column(String(100))

class Client(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.datetime.now())
    name: Mapped[str] = mapped_column(String(100))
    sentiment: Mapped[str] = mapped_column(String(100))
    contact_info: Mapped[str] = mapped_column(String(100))
    budget_range: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(100))
    house_info: Mapped[str] = mapped_column(String(100))

with app.app_context():
    db.create_all()

def create_client(client_data, user_id):
  client = Client(
    user_id=user_id,
    name=client_data.name, 
    sentiment=client_data.sentiment,
    contact_info=client_data.contact_info,
    budget_range=client_data.budget_range,
    location=client_data.location,
    house_info=client_data.house_info)
  
  db.session.add(client)
  db.session.commit()

def create_links(user_id):
   links = [
        (f"swap_upload/{user_id}", "Upload"),
        (f"swap_download/{user_id}", "Download"),
        (f"swap_client/{user_id}", "Client Data"),
    ]
   return links

@app.route("/")
def home():
 
  return render_template("index.html")

@app.route("/swap_create")
def swap_account():
  return render_template("create_user.html")

@app.route("/swap_login")
def swap_login():
  return render_template("login.html")

@app.route("/swap_upload/<int:user_id>")
def swap_upload(user_id):
  return render_template("upload.html", upload_link=f"upload/{user_id}")

@app.route("/swap_download/<int:user_id>")
def swap_download(user_id):
  docs = db.session.execute(db.select(Document.id, Document.date, Document.label).where(Document.user_id == user_id).order_by(Document.date.desc())).all()
  links = []
  for doc in docs:
    links.append((doc.date, doc.label, f"/download_transcript/{doc.id}", f"/download_summary/{doc.id}"))
  return render_template("download.html", links=links)

@app.route("/swap_client/<int:user_id>")
def swap_client(user_id):
  clients = db.session.scalars(db.select(Client).where(Client.user_id == user_id).order_by(Client.date.desc())).all()
  return render_template("client.html", clients=clients)


@app.route("/upload/<int:user_id>", methods = ['POST'])
def upload(user_id):
  if request.method == 'POST': 
    label = request.form["name"]
    file = request.files['file']

    if file and label:
      buffer = BytesIO()
      file.save(buffer)
      buffer.name = file.filename
      segments, transcript = ai.transcribe_audio(client, buffer)
      summary = ai.create_summary(transcript)
      document = Document(label=label, user_id=user_id, transcript="\n\n".join(segments).encode("utf-8"), summary=summary.encode("utf-8"))
      db.session.add(document)
      db.session.commit()

      client_data = ai.parse_transcript(transcript)
      create_client(client_data, user_id)

      return render_template("summary.html",
                          transcript_link=f"download_transcript/{document.id}", 
                          summary_link=f"download_summary/{document.id}",
                          back_link=f"back/{user_id}",
                          segments=segments, summary=summary)
  return render_template("upload.html", upload_link=f"upload/{user_id}")

@app.route("/download_transcript/<int:id>")
def download_transcript(id):
  document = db.get_or_404(Document, id)
  content = BytesIO(document.transcript)
  return send_file(content, download_name="transcript.txt", mimetype="text/plain", as_attachment=True)

@app.route("/download_summary/<int:id>")
def download_summary(id):
  document = db.get_or_404(Document, id)
  content = BytesIO(document.summary)
  return send_file(content, download_name="summary.txt", mimetype="text/plain", as_attachment=True)

@app.route("/back/<int:id>")
def back(id):
  return render_template("upload.html", upload_link=f"upload/{id}" )

@app.route("/create_account", methods = ['POST'])
def create_account():

  username = request.form["name"]
  password = request.form["password"]

  if username and password:
    hash = bcrypt.generate_password_hash(password, 10).decode("utf-8")
    user = User(name=username, password=hash)
    db.session.add(user)
    db.session.commit()
    links = create_links(user.id)
    return render_template("nav.html", upload_link=f"upload/{user.id}", links=links)
  return render_template("create_user.html")

@app.route("/login", methods = ['POST'])
def login():
  name = request.form["name"]
  password = request.form["password"]

  user = db.one_or_404(db.select(User).filter_by(name=name))
  if user:
    if bcrypt.check_password_hash(user.password, password):
      links = create_links(user.id)
      return render_template("nav.html", upload_link=f"upload/{user.id}", links=links)
  return render_template("login.html")

@app.route("/logout")
def logout():
  return render_template("login.html")