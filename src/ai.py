from io import BytesIO
from langchain.chains.summarize import load_summarize_chain
# from langchain.chains.question_answering import load_qa_chain
from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
import textwrap
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import OpenAIEmbeddings
# import test.vec
from langchain_core.pydantic_v1 import BaseModel, Field
import test.transcript

def transcribe_audio(client, buffer: BytesIO)->str:
  # transcription = client.audio.transcriptions.create(
  #       file=buffer,
  #       model="whisper-1", 
  #       response_format="verbose_json",
  #       timestamp_granularities=["segment"]
  #     )
  # return transcription.text
  segment_list = []
  for s in test.transcript.s:
     segment = f"{s["start"]:.2f}: {s["text"]}"
     segment_list.append(segment)
  # result = "\n\n".join(segment_list)
  # print(result)
 
  # return result
  return segment_list, test.transcript.text, test.transcript.summary

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

# def answer_question(input: str, transcription: str)->str:

#   model_name = "gpt-3.5-turbo"
#   client = ChatOpenAI(temperature=0, model_name=model_name)
#   prompt_template = """You are an assistance for a real estate agency.  
#   The following text will be a conversation between a real estate
#   agent and a client.  Use the following text to answer the question.  
#   Don't try to make up an answer.  If you do not know the answer, say that 
#   you are unable to answer the question.

#   Context:{context}

#   Question: {question}
#   Answer:"""

#   text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
#     model_name=model_name
#   )
#   texts = text_splitter.split_text(transcription)
#   docs = [Document(page_content=t) for t in texts]

#   prompt = PromptTemplate(template=prompt_template, input_variables=["contect", "question"])
#   chain = load_qa_chain(client, chain_type="stuff", prompt=prompt)
#   output = chain.invoke({"input_documents":docs, "question":input}, verbose=True, return_only_outputs=False)["output_text"]
#   return output

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

  # splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
  # docs = splitter.create_documents([text])

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
 

