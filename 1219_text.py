import pytesseract
from pdf2image import convert_from_path
import os

# Tesseract 경로 설정 (MacOS에서 Homebrew로 설치된 경로)
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def pdf_to_text(file_path, output_folder="images", lang="eng", start_page=None, end_page=None, dpi=150):
    """
    PDF 파일에서 텍스트를 추출.

    Args:
        file_path (str): PDF 파일 경로.
        output_folder (str): 페이지 이미지를 저장할 폴더.
        lang (str): Tesseract 언어 설정 (기본값은 영어).
        start_page (int): 처리할 시작 페이지 (None이면 전체 처리).
        end_page (int): 처리할 마지막 페이지 (None이면 전체 처리).
        dpi (int): 이미지 해상도 설정.
    Returns:
        str: PDF에서 추출된 전체 텍스트.
    """
    # 파일 존재 여부 확인
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {file_path}")
    
    # PDF를 이미지로 변환
    images = convert_from_path(file_path, dpi=dpi, first_page=start_page, last_page=end_page)
    os.makedirs(output_folder, exist_ok=True)

    full_text = ""
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i+1}.png")
        image.save(image_path, "PNG")  # 이미지를 PNG로 저장

        # OCR 수행
        text = pytesseract.image_to_string(image, lang=lang, config="--psm 3")  # 기본 PSM 설정
        full_text += text + "\n"

    return full_text

def extract_section_from_text(text, section_name):
    """
    텍스트에서 특정 섹션(예: Abstract, Conclusion) 부분을 추출.

    Args:
        text (str): PDF에서 추출된 전체 텍스트.
        section_name (str): 탐색할 섹션 이름 (예: 'abstract', 'conclusion').
    Returns:
        str: 섹션 부분의 텍스트.
    """
    # 텍스트를 소문자로 변환하여 섹션 탐지
    text_lower = text.lower()
    section_start = text_lower.find(section_name.lower())
    if section_start == -1:
        return f"{section_name} 섹션을 찾을 수 없습니다."

    # 섹션 이후 텍스트 가져오기
    section_text = text[section_start:]
    section_excerpt = "\n".join(section_text.split("\n")[:10])  # 상위 10줄만 추출
    return section_excerpt

# 경로 설정
pdf_file = "/Users/juni/Desktop/python_KDT/downloads/example.pdf"
output_folder = "/Users/juni/Desktop/python_KDT/downloads/images"

# PDF에서 텍스트 추출
try:
    print("PDF에서 텍스트 추출 중...")

    # PDF 전체 텍스트 처리
    text = pdf_to_text(pdf_file, output_folder=output_folder, lang="eng")

    # Abstract 부분 추출 (다음 섹션이 Introduction으로 가정)
    abstract = extract_section_from_text(text, "abstract", next_section="introduction")
    print("\nAbstract 부분:")
    print(abstract)

    # Conclusion 부분 추출 (다음 섹션이 References로 가정)
    conclusion = extract_section_from_text(text, "conclusion", next_section="references")
    print("\nConclusion 부분:")
    print(conclusion)

except Exception as e:
    print(f"오류 발생: {e}")