import fitz # PyMuPDF


class PdfService:
    @staticmethod
    def extract_bookmarks(pdf_path):
        doc = fitz.open(pdf_path)
        bookmarks = doc.get_toc(simple=False)
        result = []
        for index, bookmark in enumerate(bookmarks):
            level, title, page, details = bookmark
            page_number = details.get('page')
            result.append({
                "level": level,
                "title": title,
                "page_number": page_number
            })
        return result

    @staticmethod
    def extract_links_with_text(pdf_path):
        doc = fitz.open(pdf_path)
        links_with_text = []
        for page_number, page in enumerate(doc, start=1):
            # page.get_text("words"): 현재 페이지에서 단어별로 텍스트를 추출하는 메서드
            # 현재 페이지의 모든 단어를 가져와서 각 단어의 좌표와 함께 텍스트를 반환한다.
            text_instances = page.get_text("words")  # 페이지의 텍스트를 단어 단위로 추출
            links = page.get_links()
            for link in links:
                print('@link:', link) # 모든 링크 정보 출력
                if link['kind'] == fitz.LINK_NAMED:  # 내부 페이지 링크 확인
                    link_text = PdfService._find_link_text(link['from'], text_instances)
                    if link_text:
                        links_with_text.append({
                            "link_text": link_text,
                            "from_page": page_number,
                            "to_page": int(link['page'])  # 링크가 가리키는 페이지 번호
                        })
        return links_with_text

    @staticmethod
    def _find_link_text(link_rect, words):
        # print('words', words)
        print('@@link_rect', link_rect)
        # 링크 좌표를 사각형으로 변환하여 교차점 확인을 위한 Rect로 변환
        link_area = fitz.Rect(link_rect)
        # 링크 영역과 교차하는 단어 찾아서 연결
        linked_text = [word[4] for word in words if fitz.Rect(word[:4]).intersects(link_area)]
        return ' '.join(linked_text).strip()
