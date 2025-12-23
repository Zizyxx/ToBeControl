from config import GROQ_API_KEY, logger

# Coba import library Groq a
try:
    from groq import Groq
except ImportError:
    Groq = None

groq_client = None

# Inisialisasi Client
if GROQ_API_KEY and Groq:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("✅ AI Service Siap.")
    except Exception as e:
        logger.error(f"❌ Gagal init AI: {e}")
else:
    logger.warning("⚠️ AI dinonaktifkan (Key hilang atau library belum install).")

def get_ai_response(user_text):
    """Fungsi pembungkus untuk memanggil AI"""
    if not groq_client:
        return "Maaf, layanan AI sedang tidak aktif."
    
    try:
        res = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Kamu adalah asisten TBC yang ramah. Jawab singkat & suportif."},
                {"role": "user", "content": user_text},
            ],
            max_tokens=200,
        )
        return res.choices[0].message.content
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return "Maaf, otak AI sedang error sebentar."