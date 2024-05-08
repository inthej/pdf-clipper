import fitz  # PyMuPDF


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
            # print('text_instances', text_instances)
            links = page.get_links()
            for link in links:
                # print('@link:', link) # 모든 링크 정보 출력
                if link['kind'] == fitz.LINK_NAMED:  # 내부 페이지 링크 확인
                    link_text = PdfService._find_text_by_intersection(link['from'], text_instances)
                    # link_text = PdfService._find_text_around_link(link, page)
                    # numeric_text = ''.join(filter(str.isdigit, link_text))

                    if link_text:
                        links_with_text.append({
                            "link_text": link_text,
                            "from_page": page_number,
                            "to_page": int(link['page'])  # 링크가 가리키는 페이지 번호
                        })

        print('links_with_text length:', len(links_with_text))
        return links_with_text

    """
    _find_text_by_intersection : 이 메서드는 단순히 링크 영역과 교차하는 모든 단어를 추출합니다
    """
    @staticmethod
    def _find_text_by_intersection(link_rect, words):
        # 링크 좌표를 사각형으로 변환하여 교차점 확인을 위한 Rect로 변환
        link_area = fitz.Rect(link_rect)
        # 링크 영역 내에 있는 모든 텍스트를 추출하여 연결
        linked_text = []
        for word in words:
            word_rect = fitz.Rect(word[:4])  # 단어의 사각형 영역을 만듭니다.
            if word_rect.intersects(link_area):  # 단어의 영역이 링크의 영역과 교차하는지 확인합니다.
                linked_text.append(word[4])  # 숫자로 이루어진 단어의 텍스트를 append 추가합니다
        return ' '.join(linked_text).strip()

    """
    _find_text_by_area_overlap : 이 방식은 링크 영역과 단어 영역의 겹침 정도를 기반으로 텍스트를 추출하는 방법입니다.
    """
    @staticmethod
    def _find_text_by_area_overlap(link_rect, words):
        link_area = fitz.Rect(link_rect)  # 링크 영역을 Rect 객체로 변환
        linked_text = []  # 링크 텍스트를 저장할 리스트
        intersection_threshold = 0.50  # 단어가 링크 텍스트로 간주되기 위해 요구되는 최소 겹침 비율 (50%)
        for word in words:
            word_rect = fitz.Rect(word[:4])  # 각 단어의 영역을 Rect 객체로 변환
            if word_rect.intersects(link_area):  # 단어 영역이 링크 영역과 교차하는지 검사
                intersection = word_rect & link_area  # 교차하는 영역을 계산
                intersection_area = intersection.width * intersection.height  # 교차 영역의 면적을 계산
                word_area = word_rect.width * word_rect.height  # 단어 영역의 면적을 계산

                # 교차 영역이 단어 영역의 50% 이상인 경우, 해당 단어를 링크 텍스트로 추가
                if (intersection_area / word_area) >= intersection_threshold:
                    linked_text.append(word[4])  # 링크 텍스트 리스트에 단어 추가
        return ' '.join(linked_text).strip()  # 추출된 링크 텍스트를 문자열로 반환

    """
    _find_text_by_centroid_location :  각 단어의 중심점이 링크 영역 내에 있는지를 확인하여 링크 텍스트를 추출
    """
    @staticmethod
    def _find_text_by_centroid_location(link_rect, words):
        link_area = fitz.Rect(link_rect) # 링크의 좌표를 사각형으로 변환하여 링크 영역을 정의합니다.
        linked_text = [] # 추출된 링크 텍스트를 저장할 리스트입니다.
        for word in words: # 페이지에서 추출한 각 단어에 대해 반복 처리합니다.
            word_rect = fitz.Rect(word[:4]) # 각 단어의 영역을 사각형으로 변환합니다.
            word_center = fitz.Point((word_rect.x0 + word_rect.x1) / 2, (word_rect.y0 + word_rect.y1) / 2) # 각 단어의 중심점을 계산합니다.
            if link_area.contains(word_center):  # 계산된 중심점이 링크 영역 내에 있는지 확인합니다.
                linked_text.append(word[4]) # 중심점이 링크 영역 내에 위치할 경우, 해당 단어를 연결된 텍스트 목록에 추가합니다.
        return ' '.join(linked_text).strip() # 추출된 텍스트를 공백으로 구분하여 하나의 문자열로 결합합니다.

    """
    _find_text_around_link : 특정 링크 영역과 교차하는 모든 텍스트를 추출하고, 이를 연결하여 하나의 문자열로 반환
    """
    @staticmethod
    def _find_text_around_link(link, page):
        # 링크의 좌표와 주변 텍스트를 추출하여 가공
        link_rect = fitz.Rect(link['from'])
        link_text = ""
        for word in page.get_text("words"):
            word_rect = fitz.Rect(word[:4])
            if word_rect.intersects(link_rect):
                link_text += word[4] + " "
        return link_text.strip()
