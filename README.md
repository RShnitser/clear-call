# Clear Call

Clear Call is a web application that uses
OpenAI and langchain to transcribe audio,
summarize the transcript, and answer 
questions about the transcript.

## Running

Requires python and pip

run  
```
pip install -r requirements.txt
```
in project directory to install dependencies
```
flask run
```
to start app

## Login and Create Account

Create or login with username and password

## Upload Screen

Upload an audio file in the mp3, mp4, mpeg, mpga, m4a, wav, or webm. format.
After a file is uploaded, the transcript and summary wil be displayed.

## Download Screen

Download links to transcripts and summaries from all previously uploaded audio files.

## Client Data Screen

Shows information about the client that could potentially aid in making a sale

## To Do
- Set limitations on types of files that can be uploaded
- Protected Routes
- Progress bars

