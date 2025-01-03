# -*- coding: utf-8 -*-
"""PDF GPT Generator.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1spM_c-fBXzr-bTi5VR4eIxxEzqD4Opx7
"""

# installing dependencies

# Commented out IPython magic to ensure Python compatibility.

# 
import streamlit as st
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import CTransformers
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage  # Import from langchain_core

st.set_page_config(
    page_title="PDF-Q-and-A-ChatBot",
    page_icon="📚"
)

# Custom CSS to hide Streamlit icon, GitHub, and Fork icons
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp {padding-top: 0;}
footer .stButton {display: none;}  /* Hide the Streamlit logo */
footer .stMetrics {display: none;}  /* Hide the Streamlit logo */
</style>
"""
# Inject custom CSS
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


 
hugging_face_token = st.secrets["hugging_face_token"]
os.environ['HUGGINGFACEHUB_API_TOKEN'] = hugging_face_token
 
def load_llm():
    model = "TheBloke/Llama-2-7B-Chat-GGML"
    llm = CTransformers(
        model=model,
        model_type="llama",
        max_new_tokens=512,
        temperature=0.8
    )
    return llm
 
st.title('🦜🔗 PDF Q&A ChatBot')  # Conversational title
 
with st.sidebar:
  pdf = st.file_uploader('Upload your PDF here', type=['pdf'])

if pdf is not None:
    st.success("Great! I've got your PDF. What would you like to know?")  # Success message
 
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
 
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    knowledge_base = FAISS.from_texts(chunks, embeddings)
 
    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
 
    user_question = st.chat_input("Ask your question:")
    if user_question:
        st.info("Let me think...")  # Informative message before processing
 
        docs = knowledge_base.similarity_search(user_question)
 
        llm = load_llm()
 
        prompt_template = """
        Use the following information to answer the user's question.
        If you don't know the answer, just say you don't know, don't try to guess.
 
        context: {context}
        Question: {question}
 
        Only return the helpful answer and nothing else.
        Helpful answer:
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain_type_kwargs = {"prompt": prompt}
 
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=knowledge_base.as_retriever(search_kwargs={"k": 2}),
            chain_type_kwargs=chain_type_kwargs
        )
# 
        response = chain.run(input_documents=docs, query=user_question)
 
        # Update chat history and display messages
        st.session_state.chat_history.append(HumanMessage(content=user_question))
        st.session_state.chat_history.append(AIMessage(content=response))
 
        for message in st.session_state.chat_history:
            if isinstance(message, AIMessage):
                with st.chat_message("AI"):
                    st.write(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("Human"):
                    st.write(message.content)
 
#

