# 논문 검색 라이브러리
from scholarly import scholarly

# 논문 요약 라이브러리
import nltk
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# 논문 번역 라이브러리
from googletrans import Translator

# 논문 검색 함수
def search_scholar(query, limit=5):

    # 검색 결과 리스트
    results = []
    try:
        # Google Scholar 검색 후 내용 적재
        search_results = scholarly.search_pubs(query)
        for i, result in enumerate(search_results):
            if i >= limit:
                break
            # 제목, 저자, 발행연도, 요약, URL 정보 적재
            paper = {
                'title': result['bib']['title'],
                'authors': ", ".join(result['bib']['author']),
                'year': result['bib'].get('pub_year', 'N/A'),
                'abstract': result.get('abstract', '요약 정보 없음'),
                'url': result['pub_url'] if 'pub_url' in result else 'URL 없음',
            }
            # 논문 추가
            results.append(paper)
    except Exception as e:
        raise RuntimeError(f"논문 검색 중 오류 발생: {e}")
    return results

# NLTK 다운로드
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# T5 모델 및 토크나이저 로드
model_name = 'eenzeenee/t5-base-korean-summarization'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# 논문 요약 함수
def summarize_scholar(text):
    try:
        prefix = "논문 요약 : "
        inputs = [prefix + text]
        inputs = tokenizer(inputs, max_length=512, truncation=True, return_tensors="pt")

        output = model.generate(**inputs, num_beams=3, do_sample=True, min_length=10, max_length=64)
        decoded_output = tokenizer.batch_decode(output, skip_special_tokens=True)[0]
        summary = nltk.sent_tokenize(decoded_output.strip())[0]
        return summary
    except Exception as e:
        return "요약 실패 : {}".format(str(e))
    
# Google Translator 초기화
translator = Translator()

# 논문 번역 함수
def translate_scholar(text, src="en", dest="ko"):
    try:
        translated = translator.translate(text, src=src, dest=dest)
        return translated.text
    except Exception as e:
        return f"번역 실패: {e}"
    
# 논문 번역 테스트 - 실행
scholar_data2 = """During my vacation, you will need to use this code as a base to supplement our services. First of all,
                    what seems to be the biggest problem is obtaining the thesis. As we know, the Google Scholar API is not provided by Google,
                    but is done by a specific company using its own method, so it seems that a new crawling method is needed."""
exam = translate_scholar(scholar_data2)
print(exam)
