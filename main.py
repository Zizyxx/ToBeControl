from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters
)
from config import TELEGRAM_TOKEN, logger
import handlers

def main():
    logger.info("🤖 Memulai Bot TBC Modular...")
    
    # 1. Buat Aplikasi
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # 2. Daftarkan Handlers (dari file handlers.py)
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("set", handlers.set_reminder))
    app.add_handler(CommandHandler("list", handlers.list_jadwal))
    app.add_handler(CommandHandler("hapus", handlers.hapus_jadwal))
    app.add_handler(CommandHandler("stats", handlers.show_stats))
    
    app.add_handler(CallbackQueryHandler(handlers.button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.chat_ai))

    # 3. Jalankan Scheduler (Cek database setiap 60 detik)
    job_queue = app.job_queue
    job_queue.run_repeating(handlers.check_reminders, interval=60, first=10)

    # 4. Jalan!
    logger.info("🚀 Bot Siap dan Berjalan!")
    app.run_polling()

if __name__ == "__main__":
    main()