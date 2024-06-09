import streamlit as st
import uuid
import sys
from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.llms import Bedrock
import os
import boto3
import json

client = boto3.client('secretsmanager')

USER_ICON = "images/user.png"
AI_ICON = "images/ai.png"
MAX_HISTORY_LENGTH = 5

bedrock_client = boto3.client('bedrock-runtime')

def custom_build_chain():
    response = client.get_secret_value(SecretId='kendra_secrets')
    secret_data = json.loads(response['SecretString'])
    kendra_index_id = secret_data['index_id']
    
    llm = Bedrock(
        model_id="amazon.titan-text-express-v1",
        client=bedrock_client
    )
      
    retriever = AmazonKendraRetriever(index_id=kendra_index_id)

    prompt_template = """
    The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. {context} Instruction: Based on the above documents, provide a detailed answer for, {question} Answer "don't know" if not present in the document. Solution:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
  
    condense_qa_template = """
    Given the following conversation and a follow up question, rephrase the follow up question 
    to be a standalone question.
  
    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""
    standalone_question_prompt = PromptTemplate.from_template(condense_qa_template)
  
    qa = ConversationalRetrievalChain.from_llm(
          llm=llm, 
          retriever=retriever, 
          condense_question_prompt=standalone_question_prompt, 
          return_source_documents=True, 
          combine_docs_chain_kwargs={"prompt":PROMPT})
    return qa

def custom_run_chain(chain, prompt: str, history=[]):
    return chain({"question": prompt, "chat_history": history})

if 'user_id' in st.session_state:
    user_id = st.session_state['user_id']
else:
    user_id = str(uuid.uuid4())
    st.session_state['user_id'] = user_id

if 'llm_chain' not in st.session_state:
    st.session_state['llm_app'] = {}
    st.session_state['llm_chain'] = custom_build_chain()

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if "chats" not in st.session_state:
    st.session_state.chats = [
        {
            'id': 0,
            'question': '',
            'answer': ''
        }
    ]

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = []

if "input" not in st.session_state:
    st.session_state.input = ""

st.markdown("<style>.block-container {padding: 32px 0;}.element-container img {background-color: #fff;}.main-header {font-size: 24px;}</style>", unsafe_allow_html=True)

def custom_write_logo():
    section1, section2, section3 = st.columns([5, 1, 5])
    with section2:
        st.image(AI_ICON, use_column_width='always') 

def custom_write_top_bar():
    section1, section2, section3 = st.columns([1,10,2])
    with section1:
        st.image(AI_ICON, use_column_width='always')
    with section2:
        header = "Chat app using Amazon Bedrock and Kendra"
        st.write(f"<h3 class='main-header'>{header}</h3>", unsafe_allow_html=True)
    with section3:
        clear = st.button("Clear Chat")
    return clear

clear = custom_write_top_bar()

if clear:
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.input = ""
    st.session_state["chat_history"] = []

def custom_handle_input():
    input = st.session_state.input
    question_with_id = {
        'question': input,
        'id': len(st.session_state.questions)
    }
    st.session_state.questions.append(question_with_id)

    chat_history = st.session_state["chat_history"]
    
    if len(chat_history) == MAX_HISTORY_LENGTH:
        chat_history = chat_history[:-1]

    llm_chain = st.session_state['llm_chain']
    chain = st.session_state['llm_app']
    result = custom_run_chain(llm_chain, input, chat_history)
    answer = result['answer']
    chat_history.append((input, answer))
    
    st.session_state.answers.append({
        'answer': result,
        'id': len(st.session_state.questions)
    })
    st.session_state.input = ""

def custom_write_user_message(md):
    section1, section2 = st.columns([1,12])
    
    with section1:
        st.image(USER_ICON, use_column_width='always')
    with section2:
        st.warning(md['question'])

def custom_render_answer(answer):
    section1, section2 = st.columns([1,12])
    with section1:
        st.image(AI_ICON, use_column_width='always')
    with section2:
        st.info(answer['answer'])

def custom_write_chat_message(md, q):
    chat = st.container()
    with chat:
        custom_render_answer(md['answer'])
    
with st.container():
    for (q, a) in zip(st.session_state.questions, st.session_state.answers):
        custom_write_user_message(q)
        custom_write_chat_message(a, q)

st.markdown('---')
input = st.text_input("Ask a question on your document", key="input", on_change=custom_handle_input)
