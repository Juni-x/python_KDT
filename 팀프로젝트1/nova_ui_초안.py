import os, base64, re
from dotenv import load_dotenv
import pandas as pd
import google.generativeai as genai
from google.cloud import vision
from google.oauth2 import service_account
from pdf2image import convert_from_path

import streamlit as st

# 환경 변수 로드
load_dotenv('env.env')

gemeni_api_key = os.getenv('GEMINI_API_KEY')
vision_api_path = os.getenv('VISION_API_PATH')

# Gemini 모델 로드
@st.cache_resource
def load_model():
    genai.configure(api_key=gemeni_api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    return model

# Cloud Vision 클라이언트 로드
@st.cache_resource
def load_client():
    try:
        credentials = service_account.Credentials.from_service_account_file(vision_api_path)
        client = vision.ImageAnnotatorClient(credentials=credentials)
        return client
    except Exception as e:
        st.error(f'Error in load_client(): {str(e)}')
        return None
    


# 논문 내용 추출 함수
def extract_info(text):
    # 타이틀(Title) 추출
    title_pattern = r"arXiv:.*\n(.*?)\n"
    title_match = re.search(title_pattern, text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "제목을 찾을 수 없습니다."

    # # 요약(Abstract) 추출
    abstract_pattern = r"Abstract\s*(.*?)(?=\n[1-9]+\s+[A-Za-z]|\n[A-Z][a-z])"
    abstract_match = re.search(abstract_pattern, text, re.DOTALL)
    abstract = abstract_match.group(1).strip() if abstract_match else "요약을 찾을 수 없습니다."

    # 결론(Conclusion) 추출
    conclusion_pattern = r"(?<=\n)(\d+\s)?(Conclusion|Concluding(?:\s\w+)?)\s*(.*?)(?=\n[A-Z][a-z]+|\Z)"
    conclusion_match = re.search(conclusion_pattern, text, re.DOTALL)
    conclusion = conclusion_match.group(3).strip() if conclusion_match else "결론을 찾을 수 없습니다."

    return title, abstract, conclusion

### OCR ###
# 텍스트 추출 (image)
def detect_text_from_image(image_path, client):
    try:
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        # st.write(texts[0].description)
        return texts[0].description
    except Exception as e:
        st.error(f'Error in detect_text_from_image(): {str(e)}')
        return None

# 텍스트 추출 (pdf)
def detect_text_from_pdf(input_path, save_path, client):
    try:
        pages = convert_from_path(input_path)
        all_text = ''
        for i, page in enumerate(pages):
            image_path = f'{save_path}/{str(i)}.jpg'
            page.save(image_path, 'JPEG')
        
            text = detect_text_from_image(image_path, client)
            all_text += f'\n\n--- Page {i+1} ---\n\n{text}'
        
        return all_text
    except Exception as e:
        st.error(f'Error in detect_text_from_pdf(): {str(e)}')
        return None

# 업로드된 pdf 파일 처리
def process_pdf(uploaded_file, pdf_save_dir, jpg_save_dir, client):
    try:
        # pdf 파일 저장
        pdf_path = os.path.join(pdf_save_dir, uploaded_file.name)
        with open(pdf_path, 'wb') as f:
                f.write(uploaded_file.read())
        
        # 텍스트 추출
        with st.spinner('텍스트 추출 중...'):
            jpg_dir = os.path.join(jpg_save_dir, uploaded_file.name)
            os.makedirs(jpg_dir, exist_ok=True)
            extracted_text = detect_text_from_pdf(pdf_path, jpg_dir, client)
        
        return pdf_path, extracted_text
    
    except Exception as e:
        st.error(f'Error in process_pdf(): {str(e)}')
        return None, None

# 업로드된 pdf 처리 결과 출력
def display_pdf(pdf_path, extracted_text):
    st.subheader('PDF 처리 결과')
    col1, col2 = st.columns([1, 1], gap='large')
    
    with col1: # 추출된 텍스트 출력
        st.text_area('추출된 텍스트', extracted_text, height=400)
    
    with col2: # 업로드된 pdf 출력
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height=400 type="application/pdf"></iframe>'
        st.write('업로드된 파일')
        st.markdown(pdf_display, unsafe_allow_html=True)

# 채팅 내역에 pdf 처리 결과 추가
def add_pdf_to_chat(filename, title, abstract, conclusion):
    system_message = f'''새로운 PDF 파일이 업로드되었습니다: {filename}
    
논문 제목

{title}

논문 요약

{abstract}

논문 결론

{conclusion}
'''
    
    st.session_state.messages.append({'role': 'assistant', 'content': system_message})


### Chatbot ###
# gemini와 대화하기
def chat_with_gemini(model, prompt, chat_history):
    try:
        # 대화 히스토리 포맷팅
        formatted_history = '\n'.join([
            f'{"User" if msg['role']=="user" else "Assistant"}: {msg["content"]}'
            for msg in chat_history[:-1] # 현재 프롬프트 제외
        ])

        # 프롬프트 구성
        context_prompt = f'''이전 대화 내용:
{formatted_history}

현재 질문:
{prompt}

이전 대화 맥락을 고려해서 답변해줘.
        '''

        response = model.generate_content(context_prompt)
        return response.text
    except Exception as e:
        st.error(f'Error in chat_with_gemini(): {str(e)}')
        return None

# 채팅 출력
def display_chat(model):
    st.subheader('Nova와 대화하기')
    
    # 채팅 히스토리 표시
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                st.markdown(message['content'])

    # 사용자 입력
    if prompt:=st.chat_input('Nova에게 질문하세요.'):
        # 사용자 메시지 추가
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        with st.chat_message('user'):
            st.markdown(prompt)
        
        # gemini 응답
        with st.chat_message('assistant'):
            response = chat_with_gemini(model, prompt, st.session_state.messages)
            st.markdown(response)
            st.session_state.messages.append({'role': 'assistant', 'content': response})


### UI_Streamlit ###
def main():
    st.set_page_config(
        page_title='Nova',
        page_icon='img/nova_icon.png',
        layout='wide')
    st.title('NOVA')

    # 모델과 클라이언트 로드
    model = load_model()
    client = load_client()

    # 세션 상태 초기화
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({ # 초기 메시지
            'role': 'assistant',
            'content': '안녕하세요🤗 AI 논문 어시스턴트 Nova입니다! 무엇을 도와드릴까요?'
        })
    if 'current_pdf' not in st.session_state:
        st.session_state.current_pdf = None
    
    ## OCR 섹션 ##
    # 사이드 바 (파일 업로드)
    st.sidebar.header('논문 파일 업로드')
    uploaded_file = st.sidebar.file_uploader('논문 파일(PDF)을 업로드하세요.', type=['pdf'])

    # 경로
    # 저장 디렉토리 설정
    pdf_save_dir = 'C:/Users/TU/Desktop/nova/input_pdf'
    jpg_save_dir = 'C:/Users/TU/Desktop/nova/input_pdf/save_jpg'
    os.makedirs(pdf_save_dir, exist_ok=True)

    # 새로운 PDF 파일이 업로드된 경우
    if uploaded_file is not None and uploaded_file.name!=st.session_state.current_pdf:
        pdf_path, extracted_text = process_pdf(uploaded_file, pdf_save_dir, jpg_save_dir, client)
        title, abstract, conclusion = extract_info(extracted_text)

        if pdf_path and extracted_text:
            display_pdf(pdf_path, extracted_text)
            add_pdf_to_chat(uploaded_file.name, title, abstract, conclusion)
            st.session_state.current_pdf = uploaded_file.name
    
    # 이전에 업로드된 PDF 파일 다시 표시
    elif uploaded_file is not None:
        pdf_path = os.path.join(pdf_save_dir, uploaded_file.name)
        extracted_text = detect_text_from_pdf(pdf_path, os.path.join(jpg_save_dir, uploaded_file.name), client)
        display_pdf(pdf_path, extracted_text)
    
    st.markdown('---')

    ## 챗봇 섹션 ##
    display_chat(model)

if __name__=='__main__':
    main()