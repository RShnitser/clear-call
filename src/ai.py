from io import BytesIO
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
import textwrap
from langchain_core.pydantic_v1 import BaseModel, Field

def transcribe_audio(client, buffer: BytesIO)->str:
  transcript = client.audio.transcriptions.create(
        file=buffer,
        model="whisper-1", 
        response_format="verbose_json",
        timestamp_granularities=["segment"]
      )

  segment_list = []
  for s in transcript.segments:
     segment = f"{s["start"]:.2f}: {s["text"]}"
     segment_list.append(segment)

  return segment_list, transcript.text,

def create_summary(text: str)->str:
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
  client = ChatOpenAI(temperature=0, model_name=model_name)
  chain = load_summarize_chain(client, chain_type="stuff", prompt=prompt, verbose=False)
  output = chain.invoke(docs)["output_text"]
  result = textwrap.fill(output, width=50, break_long_words=False, replace_whitespace=False)
  return result

class Contact(BaseModel):
    name: str = Field(description="Name of the client")
    sentiment: str = Field(description="Sentiment of the conversatioln, positive, neutral, or negative")
    contact_info: str = Field(description="The client's contact information")
    budget_range: str = Field(description="The client's budget range")
    location: str = Field(description="Location the client is interested in")
    house_info: str = Field(description="Information related to the house they are looking for")

def parse_transcript(text: str):

  model_name = "gpt-3.5-turbo"

  prompt_template = """You are an assistance for a real estate agency.  
  The following text will be a conversation between a real estate
  agent and a client.  Classify the sentiment of this conversation as
  positive, negavtive, or neutral using only one of those words.  
  After, get the following data about the client.
  Name
  Any contact information
  Address
  Description of house they are looking for
  Location they are interested in
  Budget
  Type of house, with number of rooms

  Conversation:{text}

  Answer:"""

  splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(model_name = "gpt-3.5-turbo")
  texts = splitter.split_text(text)
  docs = [Document(page_content=t) for t in texts]
  prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
  client = ChatOpenAI(temperature=0, model_name=model_name)
  chain = load_summarize_chain(client, chain_type="stuff", prompt=prompt, verbose=True)
  output = chain.invoke(docs)["output_text"]

  
  contact_llm = client.with_structured_output(Contact)
  result = contact_llm.invoke(output)
  return result
 

