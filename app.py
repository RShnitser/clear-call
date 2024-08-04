from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, render_template, send_file
from io import BytesIO
from test import doc1
from src import ai
import bcrypt
import os
from flask_sqlalchemy import SQLAlchemy


load_dotenv()
client = OpenAI()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite+{os.environ.get("DB_URI")}/?authToken={os.environ.get("DB_AUTH")}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

@app.route("/")
def home():
 
  return render_template("index.html")


@app.route("/upload", methods = ['POST'])
def upload():

  if request.method == 'POST':   
    file = request.files['file']

    if file:
      # buffer = BytesIO(b'Alex Johnson: Hi Jamie, this is Alex Johnson from Sunshine Realty. How are you today?\r\n\r\nJamie Lee: Hi Alex, I\x92m doing well, thanks! How about you?\r\n\r\nAlex Johnson: I\x92m great, thank you. I\x92m glad we could connect today. I understand you\x92re looking to buy a new home. Can you tell me a bit more about what you\x92re looking for?\r\n\r\nJamie Lee: Absolutely. I\x92m looking for a three-bedroom house in a good school district. Ideally, it should have a decent-sized backyard and be within a 30-minute commute to downtown.\r\n\r\nAlex Johnson: Got it. Do you have any specific neighborhoods or areas in mind?\r\n\r\nJamie Lee: I\x92m open to suggestions, but I\x92ve heard good things about the Greenfield and Willow Creek neighborhoods. I\x92d love to hear your thoughts on those areas.\r\n\r\nAlex Johnson: Both Greenfield and Willow Creek are excellent choices. Greenfield is known for its top-rated schools and family-friendly environment. Willow Creek, on the other hand, offers a bit more in terms of newer developments and parks. I can show you listings in both areas. Does that sound good?\r\n\r\nJamie Lee: That sounds perfect. What\x92s the current market like in those neighborhoods?\r\n\r\nAlex Johnson: The market is quite active right now. In Greenfield, we\x92re seeing homes priced around $450,000 to $550,000 with competitive offers. Willow Creek has slightly higher prices, ranging from $500,000 to $600,000, but it\x92s worth it for the newer amenities.\r\n\r\nJamie Lee: That fits within my budget. What are the next steps?\r\n\r\nAlex Johnson: First, I\x92ll gather some listings that match your criteria and send them over to you. Once you\x92ve had a chance to review them, we can schedule some viewings. Does that work for you?\r\n\r\nJamie Lee: Yes, that works for me. When should I expect the listings?\r\n\r\nAlex Johnson: I\x92ll email them to you by the end of the day. I can follow up with a call tomorrow to see if you have any questions or if there\x92s anything specific you want to focus on.\r\n\r\nJamie Lee: Great, I\x92ll look out for your email. Thanks for being so thorough, Alex.\r\n\r\nAlex Johnson: No problem at all. I\x92m here to help. Do you have any other questions for me right now?\r\n\r\nJamie Lee: Not at the moment. I think we covered everything.\r\n\r\nAlex Johnson: Wonderful. I\x92ll be in touch soon with those listings. Have a great rest of your day, Jamie.\r\n\r\nJamie Lee: Thanks, you too, Alex. Talk soon!\r\n\r\nAlex Johnson: Talk soon. Bye!\r\n\r\nJamie Lee: Bye!')
      # buffer = BytesIO()
      # file.save(buffer)
      # buffer.name = file.filename
      result = ai.parse_text(doc1.d1)
      

      return render_template("message.html", text=result)
  return render_template("message.html", text=doc1.d1)

@app.route("/download")
def download():
  content = """
- Jamie Lee is looking for a three-bedroom house
in a good school district with a decent-sized
backyard and within a 30-minute commute to
downtown.
- Alex Johnson suggested Greenfield and
Willow Creek neighborhoods based on Jamie's
preferences.
- The current market in Greenfield
ranges from $450,000 to $550,000, while Willow
Creek has prices from $500,000 to $600,000.
- Alex
will send listings matching Jamie's criteria by
the end of the day and follow up with a call
tomorrow to schedule viewings.
- Areas of
improvement: Alex could provide more detailed
information on the neighborhoods, such as
amenities, crime rates, and community
demographics, to help Jamie make a more informed
decision. Additionally, Alex could offer to
accompany Jamie on property viewings to provide
expert guidance and answer any questions in
person."""
  return send_file(BytesIO(content.encode("utf-8")), download_name="summary.txt", mimetype="text/plain", as_attachment=True)

@app.route("/back")
def back():
  return render_template("upload.html")

@app.route("/create_account", methods = ['POST'])
def create_account():
  username = request.form["name"]
  password = request.form["password"]
  return render_template("upload.html")