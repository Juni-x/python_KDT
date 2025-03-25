import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ✅ 환경 변수 로드
load_dotenv()

# ✅ API 키 불러오기 (Google Gemini만 사용)
gemini_api_key = os.getenv("GEMINI_API_KEY")

# ✅ Streamlit UI
st.title("🤰 임산부 금기 성분 확인 챗봇")
uploaded_file = st.file_uploader("📂 금기 성분 엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file:
    # ✅ 엑셀 데이터 로드
    loader = UnstructuredExcelLoader(uploaded_file)
    docs = loader.load()

    # ✅ 문서 분할 (텍스트 크기 조절)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_documents = text_splitter.split_documents(docs)

    # ✅ 벡터 저장소(FAISS) 생성
    embeddings = GoogleGenerativeAIEmbeddings(google_api_key=gemini_api_key, model="models/embedding-001")
    vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)

    # ✅ 검색 엔진 설정
    retriever = vectorstore.as_retriever()

    # ✅ 프롬프트 설정
    prompt = PromptTemplate.from_template(
        """너는 임산부의 약물 복용 정보를 제공하는 AI 챗봇이야. 
        아래의 데이터를 활용하여 질문에 답변해줘.
        만약 모르는 내용이라면 '잘 모르겠습니다'라고 답변해.

        # 제공된 정보:
        {context}

        # 사용자 질문:
        {question}

        # 답변:"""
    )

    # ✅ Google Gemini 모델 연결 (OpenAI 제거)
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=gemini_api_key)

    # ✅ 문서 포맷 함수
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # ✅ 체인(Chain) 생성
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # ✅ 사용자 입력 받기
    user_query = st.text_input("💊 복용 여부를 확인할 성분을 입력하세요:")

    if st.button("검색하기"):
        if user_query:
            response = chain.invoke(user_query)
            st.subheader("🔹 검색 결과")
            st.write(response)
        else:
            st.warning("❗ 성분명을 입력해주세요.")