from fastapi import UploadFile, HTTPException

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

async def validate_pdf_file(file: UploadFile):
    # 1. Kiểm tra kích thước file
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds the 5MB limit.")

    # 2. Kiểm tra Magic Bytes (%PDF)
    if not contents.startswith(b"%PDF"):
        raise HTTPException(status_code=422, detail="Invalid PDF file or wrong magic bytes.")

    # Đặt lại con trỏ file về đầu
    await file.seek(0)
    return True