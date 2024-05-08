from fastapi import APIRouter
from controllers.pdf_controller import PdfController

router = APIRouter()


@router.get("/pdf/bookmarks")
async def pdf_bookmarks():
    return await PdfController.bookmarks()


@router.get("/pdf/links")
async def pdf_links():
    return await PdfController.links()