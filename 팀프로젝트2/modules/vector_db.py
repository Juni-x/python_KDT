import os
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# ✅ 환경 변수 로드
load_dotenv("env.env")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# ✅ 벡터 DB 저장 경로
VECTOR_STORE_PATH = "data/vector_store/"
CSV_FILE_PATH = "data/drug_data.csv"

def create_vector_db():
    """벡터 DB를 생성하고 저장하는 함수"""
    print("🔄 벡터 DB 생성 중...")

    if not os.path.exists(CSV_FILE_PATH):
        print("❌ CSV 파일이 존재하지 않습니다. 데이터 경로를 확인하세요.")
        return

    df = pd.read_csv(CSV_FILE_PATH)

    if df.empty:
        print("❌ CSV 파일이 비어 있습니다. 데이터를 확인하세요.")
        return

    print(f"📌 CSV 데이터 로드 완료: 총 {len(df)} 개의 약물 데이터")

    # ✅ 벡터화할 텍스트 데이터 변경
    df["벡터화_내용"] = df.apply(lambda row: f"약물명: {row['성분명']} - 상품명: {row['대표 상품명']} - 임부금기: {row['임부금기(등급)']} - 설명: {row['허가사항']}", axis=1)

    # ✅ Google Gemini API 기반 임베딩 모델 사용
    embeddings = GoogleGenerativeAIEmbeddings(google_api_key=gemini_api_key, model="models/embedding-001")

    # ✅ 벡터 DB 생성 (FAISS 사용)
    faiss_db = FAISS.from_texts(df["벡터화_내용"].astype(str).tolist(), embeddings)

    # ✅ 벡터 DB 저장
    faiss_db.save_local(VECTOR_STORE_PATH)
    print("✅ 벡터 DB 저장 완료!")

def check_vector_db():
    """벡터 DB가 정상적으로 저장되었는지 확인하는 함수"""
    if not os.path.exists(os.path.join(VECTOR_STORE_PATH, "index.faiss")):
        print("❌ 벡터 DB 파일이 존재하지 않습니다. 다시 생성하세요.")
        return

    # ✅ Google Gemini API 기반 임베딩 모델 추가
    embeddings = GoogleGenerativeAIEmbeddings(google_api_key=gemini_api_key, model="models/embedding-001")

    # ✅ FAISS DB 로드 (보안 옵션 활성화)
    try:
        faiss_db = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
        
        # ✅ 벡터 개수 확인 코드 추가
        num_vectors = faiss_db.index.ntotal  # 벡터 개수 확인
        print(f"🔍 벡터 DB 내 저장된 문서 개수: {num_vectors}")

    except Exception as e:
        print(f"❌ 벡터 DB 로드 실패: {str(e)}")

def test_vector_db(query_text):
    """ 벡터 DB에서 유사한 약물을 검색하는 함수 """
    if not os.path.exists(os.path.join(VECTOR_STORE_PATH, "index.faiss")):
        print("❌ 벡터 DB 파일이 존재하지 않습니다. 벡터 DB를 먼저 생성하세요.")
        return

    # ✅ Google Gemini API 기반 임베딩 모델 추가
    embeddings = GoogleGenerativeAIEmbeddings(google_api_key=gemini_api_key, model="models/embedding-001")

    # ✅ FAISS DB 로드 (보안 옵션 활성화)
    faiss_db = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)

    # ✅ 검색 쿼리 로그 출력
    print(f"🔎 검색어: {query_text}")

    # ✅ 검색어를 Embedding 변환 후 검색
    retriever = faiss_db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    search_results = retriever.invoke(query_text)

    if search_results:
        print(f"🔍 '{query_text}'에 대한 벡터 DB 검색 결과:")
        for idx, result in enumerate(search_results):
            print(f"{idx+1}. {result.page_content}")
    else:
        print(f"⚠️ '{query_text}'에 대한 검색 결과가 없습니다.")

if __name__ == "__main__":
    print("\n🔍 벡터 DB 확인 중...")
    create_vector_db()
    check_vector_db()

    print("\n🔎 벡터 DB 검색 테스트...")
    test_queries = ["이부프로펜", "타이레놀", "로라타딘"]
    for query in test_queries:
        print("\n---------------------------")
        test_vector_db(query)