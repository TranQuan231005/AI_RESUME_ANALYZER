import io
import re
import unicodedata
from pypdf import PdfReader
from app.schemas.document import ParsedDocument
from app.exceptions import ApiError 

def sanitize_filename(filename: str) -> str:
    """Lọc bỏ ký tự đặc biệt, giữ lại chữ, số, dấu gạch và chấm."""
    return re.sub(r'[^a-zA-Z0-9_\-\.]+', '_', filename).strip('_')

def normalize_text(text: str) -> str:
    """Chuẩn hóa Unicode (NFKC) và gom nhóm khoảng trắng liền mạch."""
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_pdf_content(file_bytes: bytes, original_filename: str) -> ParsedDocument:
    size_bytes = len(file_bytes)
    sanitized_name = sanitize_filename(original_filename)

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        page_count = len(reader.pages)
        
        extracted_text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text_parts.append(page_text)
                
        raw_text = " ".join(extracted_text_parts)
        final_text = normalize_text(raw_text)
        
        if not final_text or len(final_text) < 10: 
            raise ApiError(status_code=400, detail="PDF is empty or contains no extractable text.")
            
        return ParsedDocument(
            fileName=sanitized_name,
            text=final_text,
            pageCount=page_count,
            sizeBytes=size_bytes
        )
    except ApiError:
        raise
    except Exception:
        raise ApiError(status_code=422, detail="Invalid or corrupted PDF file.")