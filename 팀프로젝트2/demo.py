import streamlit as st
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os

# ✅ 환경 변수 로드
load_dotenv("env.env")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# ✅ Gemini API Key 설정
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-pro")  # ✅ GPT 대신 Gemini 모델 사용

st.title("드럭인포맘")

# CSV 파일 업로드
uploaded_file = st.file_uploader("약물 정보 CSV 파일을 업로드하세요", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("업로드된 데이터 미리보기:")
    st.dataframe(df.head())

# 사용자 입력 받기
user_question = st.text_input("궁금한 점을 입력하세요 (예: '8주차 임산부인데 타이레놀 먹어도 될까요?')")

if st.button("답변 받기") and user_question:
    # ✅ Gemini API 호출 방식 수정
    response = model.generate_content(user_question)

    bot_answer = response.text  # ✅ OpenAI와 다르게 response.text로 가져와야 함

    st.write("### 답변:")
    st.write(bot_answer)