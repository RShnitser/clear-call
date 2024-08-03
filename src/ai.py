from io import BytesIO
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
import textwrap

def transcribe_audio(client, buffer: BytesIO)->str:
  transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=buffer
      )
  return transcription.text

def parse_text(text: str)->str:
  model_name = "gpt-3.5-turbo"
  text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    model_name=model_name
  )

  texts = text_splitter.split_text(text)

  
  docs = [Document(page_content=t) for t in texts]
  prompt_template = """You are an assistance for a real estate agency.
  The following text will need to summarized with recommendations on how to follow
  up with the client and possible areas of improvement:

  {text}

  CONSCISE SUMMARY IN BULLET POINTS:"""

  prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
  # response = client.chat.completions.create(
  #   model="gpt-3.5-turbo",
  #   messages=[
  #     {"role": "system", "content": "This is a test."},
  #     {"role": "user", "content": input},
  #   ]
  # )
  # text = response.choices[0].message.content
  client = ChatOpenAI(temperature=0, model_name=model_name)
  chain = load_summarize_chain(client, chain_type="stuff", prompt=prompt, verbose=True)
  output = chain.invoke(docs)["output_text"]
  result = textwrap.fill(output, width=50, break_long_words=False, replace_whitespace=False)
  print(result)
  return result