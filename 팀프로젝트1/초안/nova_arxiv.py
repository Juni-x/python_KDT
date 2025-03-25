import arxiv
import os
import re
import tarfile
import pandas as pd

# 논문 내용 추출 함수 - 요약 및 결론 후처리
def clean_text(text):
    if text is None:
        return None
    
    # 요약 및 결론 내용 중 불필요 내용 제거
    text = re.sub(r"\{.*?\}", "", text) # {} 안의 내용 제거
    text = re.sub(r"\(.*?\)", "", text) # () 안의 내용 제거
    text = re.sub(r"\\textsuperscript\{.*?\}", "", text) # \textsuperscript 제거
    text = re.sub(r"\\textbf\{.*?\}", "", text) # \textbf 제거
    text = re.sub(r"\\textcolor\{.*?\}\{(.*?)\}", r"\1", text) # \textcolor 제거
    text = re.sub(r"\\url\{.*?\}", "", text) # \url 제거
    text = re.sub(r"\\[a-zA-Z]+", "", text) # 남아있는 \ 명령어 제거
    text = re.sub(r"%.*?$", "", text, flags=re.MULTILINE) # %로 시작하는 주석 제거
    text = re.sub(r"\s*\.\s*\}", "", text) # . } 같은 구문 제거
    text = re.sub(r"\s*\}", "", text) # 남은 } 제거
    text = text.replace("\n", " ") # 개행 문자를 공백으로 변경
    text = re.sub(r"\s+", " ", text).strip() # 다중 공백을 단일 공백으로 변경

    return text

# 논문 내용 추출 함수 - 저자 후처리
def clean_authors(authors_text):

    if authors_text is None:
        return []
    
    # 저자 내용 중 불필요 내용 제거
    authors_text = re.sub(r"%.*?$", "", authors_text, flags=re.MULTILINE) # %로 시작하는 주석 제거
    authors_text = re.sub(r"\\thanks\{.*?\}", "", authors_text) # 감사 문구 제거
    authors_text = re.sub(r"\\textsuperscript\{.*?\}", "", authors_text) # \textsuperscript 제거
    authors_text = re.sub(r"\\and", ",", authors_text) # and를 쉼표로 변경
    authors_text = re.sub(r"\\[a-zA-Z]+", "", authors_text) # 남아있는 \ 명령어 제거
    authors_text = re.sub(r"[\{\}]", "", authors_text) # { } 제거
    authors = re.split(r",+", authors_text)  # 쉼표로 분할
    authors = [clean_text(author.strip()) for author in authors] # 공백 제거 및 후처리
    authors = [author for author in authors if author] # 빈 문자열 제거

    return authors

# 논문 내용 추출 함수
def extract_info(arxiv_id, download_dir="nova_arxiv_papers"):
    try:
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results())

        # 폴더 생성
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # arXiv에서 논문 파일 다운로드
        source_file_path = paper.download_source(dirpath=download_dir)

        # tar 파일 압축 해제
        if source_file_path.endswith(".tar.gz"):
            with tarfile.open(source_file_path, "r:gz") as tar:
                tar.extractall(path=download_dir)
            # .tex 파일 경로
            tex_file_path = [f for f in os.listdir(download_dir) if f.endswith(".tex")][0]
            tex_file_path = os.path.join(download_dir, tex_file_path)
        else:
            print(f"다른 파일 형식: {source_file_path}")
            return None

        # .tex 파일 정보 추출
        with open(tex_file_path, "r", encoding="utf-8") as f:
            content = f.read()

            # 요약(Abstract) 추출
            abstract_match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", content, re.DOTALL)
            abstract = abstract_match.group(1).strip() if abstract_match else None

            # 결론(Conclusion) 추출
            conclusion_match = re.search(r"\\section\{(?:Conclusion|Conclusions|Concluding Remarks|Conclusion and Future Work)\}(.*?)\\section", content, re.DOTALL | re.IGNORECASE)
            conclusion = conclusion_match.group(1).strip() if conclusion_match else None

            # 저자(Authors) 추출
            authors_match = re.search(r"\\author\{(.*?)\}", content, re.DOTALL)
            authors = authors_match.group(1).strip() if authors_match else None

            # 저자 후처리
            authors = clean_authors(authors)

        # 요약 및 결론 후처리
        abstract = clean_text(abstract)
        conclusion = clean_text(conclusion)

        # 논문 내용 딕셔너리 생성
        result = {
            "arxiv_id": arxiv_id,
            "year": paper.published.year,
            "authors": authors,
            "abstract": abstract,
            "conclusion": conclusion,
        }

        return result

    except Exception as e:
        print(f"Error: {e}")
        return None

# 논문 중복 방지 함수
def check_arxiv_id(arxiv_id, csv_file="nova_arxiv.csv"):
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        return arxiv_id in df["arXiv ID"].values
    return False

# 논문 내용 -> csv 파일 저장 함수
def save_csv(paper_info, csv_file="nova_arxiv.csv"):

    # 논문 정보
    data = {
        "arXiv ID": paper_info["arxiv_id"],
        "Year": paper_info["year"],
        "Authors": ", ".join(paper_info["authors"]),
        "Abstract": paper_info["abstract"],
        "Conclusion": paper_info["conclusion"]
    }
    
    # 기존 CSV 파일 존재 확인
    if os.path.exists(csv_file):
        # 기존 파일 읽기
        df = pd.read_csv(csv_file)
    else:
        # 새로운 DataFrame 생성
        df = pd.DataFrame(columns=data.keys())

    # 새로운 행 추가
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)

    # CSV 파일 저장
    df.to_csv(csv_file, index=False, encoding="utf-8")
    print(f"논문 정보가 {csv_file}에 저장되었습니다.")


# 논문 정보 추출 및 CSV 파일 저장 프로세스 함수
def process_paper(arxiv_id, csv_file="nova_arxiv.csv"):

    # 논문 중복 방지지
    if check_arxiv_id(arxiv_id, csv_file):
        print(f"arXiv ID : {arxiv_id}는 이미 CSV 파일에 존재합니다. 프로세스를 종료합니다.")
        return
    
    # 논문 정보 추출
    paper_info = extract_info(arxiv_id)
    
    # 논문 정보 있을 시
    if paper_info:
        print(f"arXiv ID : {paper_info['arxiv_id']}")
        print(f"Year : {paper_info['year']}")
        print(f"Authors : {paper_info['authors']}")
        print(f"Abstract : {paper_info['abstract']}")
        print(f"Conclusion : {paper_info['conclusion']}")        
        save_csv(paper_info, csv_file)
    else:
        print(f"arXiv ID : {arxiv_id}에 대한 정보를 추출 할 수 없습니다.")

# arXiv ID 입력
arxiv_id = "2501.02997"

# 프로세스 실행
process_paper(arxiv_id, "nova_arxiv.csv")
