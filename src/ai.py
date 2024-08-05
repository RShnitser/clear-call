from io import BytesIO
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
import textwrap
from langchain_core.prompts import ChatPromptTemplate

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
  client = ChatOpenAI(temperature=0, model_name=model_name)
  chain = load_summarize_chain(client, chain_type="stuff", prompt=prompt, verbose=True)
  output = chain.invoke(docs)["output_text"]
  result = textwrap.fill(output, width=50, break_long_words=False, replace_whitespace=False)
  return result

def answer_question(input: str, transcription: str)->str:

  model_name = "gpt-3.5-turbo"
  client = ChatOpenAI(temperature=0, model_name=model_name)
  prompt_template = """You are an assistance for a real estate agency.  
  The following text will be a conversation between a real estate
  agent and a client.  Use the following text to answer the question.  
  Don't try to make up an answer.  If you do not know the answer, say that 
  you are unable to answer the question.

  Context:{context}

  Question: {question}
  Answer:"""

  text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    model_name=model_name
  )
  texts = text_splitter.split_text(transcription)
  docs = [Document(page_content=t) for t in texts]

  prompt = PromptTemplate(template=prompt_template, input_variables=["contect", "question"])
  chain = load_qa_chain(client, chain_type="stuff", prompt=prompt)
  output = chain.invoke({"input_documents":docs, "question":input}, verbose=True, return_only_outputs=False)["output_text"]
  return output

