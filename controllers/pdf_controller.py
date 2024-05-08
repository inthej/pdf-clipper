from services.pdf_service import PdfService


class PdfController:
    @staticmethod
    async def bookmarks():
        return PdfService.extract_bookmarks("2023년 오너스 메뉴얼.pdf")

    @staticmethod
    async def links():
        return PdfService.extract_links_with_text("2023년 오너스 메뉴얼.pdf")
