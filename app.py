from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "This is a test."},
    {"role": "user", "content": "Test"},
  ]
)

print(response.choices[0])