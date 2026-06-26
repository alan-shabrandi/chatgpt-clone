import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, chat
from vector_store import extract_and_chunk_pdf

@asynccontextmanager
async def lifespan(app: FastAPI):
    # کدهای مربوط به زمان استارتاپ برنامه
    pdf_path = "document.pdf"
    if os.path.exists(pdf_path):
        print(f"Loading and indexing {pdf_path}...")
        chunks = extract_and_chunk_pdf(pdf_path)
        chat.vector_store.add_documents(chunks)
    else:
        print(f"Warning: {pdf_path} not found. Please place it in the root directory.")
    yield

app = FastAPI(lifespan=lifespan)

# ۱. مدیریت داینامیک دامنه‌های مجاز برای لوکال و پروداکشن
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # برای توسعه لوکال
    "http://127.0.0.1:3000",
]

# اگر آدرس فرانت‌آند ابری (مثلاً در Vercel) را در متغیرهای محیطی ست کردید، به لیست اضافه می‌شود
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

# تنظیمات پیشرفته CORS برای سازگاری با HttpOnly Cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # 👈 استفاده از لیست داینامیک بجای هاردکد
    allow_credentials=True,         # 👈 برای ارسال کوکی‌های امن کاملاً حیاتی است
    allow_methods=["*"],
    allow_headers=["*"],
)

# اتصال روترها
app.include_router(auth.router)
app.include_router(chat.router)