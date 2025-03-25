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

# ✅ 시스템 프롬프트 설정 (LLM의 응답 규칙 지정)
system_prompt = (
    "너는 임산부를 위한 약물 안정성 정보를 제공하는 AI야. 사용자가 입력한 약물에 대한 정보를 제공할 때, 다음 가이드를 따라줘:\n"
    "\n"
    "1. 약물의 성분명과 일반적인 사용 목적을 설명해줘.\n"
    "2. 임산부가 복용할 경우 임신 주수에 따라 위험 여부를 분석해줘.\n"
    "3. 해당 약물의 부작용과 임산부에게 미치는 영향을 알려줘.\n"
    "4. 데이터베이스의 정보를 반드시 참고해서 답변을 제공해줘.\n"
    "5. 약물의 대체 가능 여부와 안전한 대안이 있는지 제시해줘.\n"
    "6. 질문이 애매하거나 불확실할 경우, 전문가 상담을 권유해줘.\n"
    "\n"
    "⚠️ **경고문구**: 나는 의료 전문가가 아니므로, 제공된 정보는 참고용이며 반드시 의사나 약사와 상담해야 합니다.⚠️"
)

#model = genai.GenerativeModel("gemini-1.5-pro")  # ✅ GPT 대신 Gemini 모델 사용
model = genai.GenerativeModel("gemini-1.5-pro", generation_config={"temperature": 0})

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
        # ✅ 시스템 프롬프트 적용하여 LLM 호출
        conversation = system_prompt + "\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
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
