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

st.set_page_config(page_title='드럭인포맘', page_icon='💊', layout='wide')
st.title("💊 드럭인포맘 DrugInfoMom")

# ✅ 미리 저장된 CSV 파일 2개 불러오기 (앱 실행 시 자동 로드)
@st.cache_data
def load_csv():
    df_drugs = pd.read_csv("임산부_사용_약물.csv")  # 첫 번째 CSV 파일
    df_warnings = pd.read_csv("임산부_주의_약물.csv")  # 두 번째 CSV 파일
    return df_drugs, df_warnings

# ✅ 데이터 로드
df_drugs, df_warnings = load_csv()

# ✅ 이전 대화 저장
if "messages" not in st.session_state:
    st.session_state.messages = []
    # ✅ 챗봇 첫 실행 시 자기소개 메시지 추가
    st.session_state.messages.append({
        "role": "assistant",
        "content": "안녕하세요🤗 임산부 약물 상담 도우미 **드럭인포맘**입니다! 무엇을 도와드릴까요?"
    })
    st.session_state.first_interaction = True  # 첫 상호작용 여부 확인

# ✅ 채팅 UI
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="💊" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

# ✅ 사용자 입력 받기
if user_question := st.chat_input("드럭인포맘에게 질문하세요."):
    # ✅ 사용자 질문 추가
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_question)
    
    # ✅ 로딩 인디케이터 표시 (로딩 중일 때는 새 메시지를 미리 추가하지 않음)
    with st.spinner("드럭인포맘이 답변을 작성 중입니다..."):
        # ✅ 대화 히스토리 포함하여 LLM 호출
        conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
        response = model.generate_content(conversation)
        bot_answer = response.text  # ✅ OpenAI와 다르게 response.text로 가져와야 함
    
    # ✅ 첫 번째 질문 이후부터는 인사 및 자기소개 제거
    if st.session_state.first_interaction:
        st.session_state.first_interaction = False  # 첫 상호작용 후 플래그 변경
    else:
        bot_answer = bot_answer.split("\n", 1)[-1]  # 첫 줄(인사말) 제거

    # ✅ 답변을 UI에 추가 (로딩이 끝난 후에만 표시됨)
    st.session_state.messages.append({"role": "assistant", "content": bot_answer})
    st.rerun()