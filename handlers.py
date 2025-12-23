import io
import matplotlib
# Mengatur backend ke 'Agg' agar tidak perlu layar monitor (headless)
# Ini wajib agar tidak error saat dijalankan di server/terminal biasa
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
from urllib.parse import quote_plus, unquote_plus
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Import modul buatan kita sendiri
import database as db
import ai_service as ai
from config import logger

# --- Helper Kecil ---
def validate_time(t):
    try:
        datetime.strptime(t, "%H:%M")
        return True
    except:
        return False

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.register_user(user.id, user.first_name, user.username)
    await update.message.reply_text(
        f"Halo {user.first_name}! 👋\n\n"
        "Saya bot pengingat TBC Modular.\n"
        "• /set HH:MM NamaObat\n"
        "• /list\n"
        "• /hapus HH:MM\n"
        "• /stats (Sekarang pakai Grafik! 📊)"
    )

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        return await update.message.reply_text("Format: /set 07:00 NamaObat")
    
    jam = args[0]
    obat = " ".join(args[1:])
    
    if not validate_time(jam):
        return await update.message.reply_text("Jam salah. Gunakan HH:MM (Contoh: 07:00)")
    
    success = db.add_jadwal(update.effective_user.id, jam, obat)
    if success:
        await update.message.reply_text(f"✅ Pengingat {obat} jam {jam} disimpan.")
    else:
        await update.message.reply_text("⚠️ Gagal. Mungkin jadwal sudah ada.")

async def list_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jadwal = db.get_jadwal(update.effective_user.id)
    if not jadwal:
        return await update.message.reply_text("Belum ada jadwal.")
    
    jadwal.sort(key=lambda x: x.get("jam", "00:00"))
    
    msg = "📋 **Jadwal Obat:**\n"
    for item in jadwal:
        msg += f"⏰ {item['jam']} - {item['obat']}\n"
    await update.message.reply_text(msg)

async def hapus_jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Format: /hapus 07:00")
    
    jam = context.args[0]
    count = db.delete_jadwal(update.effective_user.id, jam)
    if count > 0:
        await update.message.reply_text(f"🗑️ Jadwal jam {jam} dihapus.")
    else:
        await update.message.reply_text("Jadwal tidak ditemukan.")

# --- BAGIAN INI YANG BERUBAH TOTAL (FITUR GRAFIK) ---
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # 1. Ambil data harian dari database (Fungsi baru di Step 2)
    data = db.get_daily_logs(user_id)
    total = db.get_total_logs(user_id)
    
    # Jika datanya kosong, beri pesan teks saja
    if not data:
        return await update.message.reply_text(f"📊 Kamu sudah minum obat {total} kali totalnya.\n(Belum cukup data harian untuk grafik).")

    # Beri notifikasi sedang mengetik/loading
    await update.message.reply_text("⏳ Sedang menggambar grafik...")

    try:
        # 2. Siapkan sumbu X (Tanggal) dan Y (Jumlah)
        dates = list(data.keys())
        counts = list(data.values())

        # 3. Proses Menggambar dengan Matplotlib
        plt.figure(figsize=(6, 4)) # Ukuran kanvas
        plt.bar(dates, counts, color='skyblue') # Gambar grafik batang biru
        plt.xlabel('Tanggal')
        plt.ylabel('Jumlah Obat')
        plt.title('Kepatuhan Minum Obat (7 Hari Terakhir)')
        plt.xticks(rotation=45, ha='right') # Miringkan tulisan tanggal biar tidak tabrakan
        plt.tight_layout() # Rapikan margin

        # 4. Simpan gambar ke "Memori RAM" (Buffer), bukan ke Harddisk
        # Ini trik agar bot tidak penuh dengan file sampah gambar
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close() # Tutup kanvas agar memori lega

        # 5. Kirim Buffer gambar ke Telegram
        await update.message.reply_photo(
            photo=buf,
            caption=f"📊 **Laporan Kepatuhan**\nTotal Minum Obat: **{total}** kali.\nTetap semangat sembuh! 💪"
        )
    except Exception as e:
        logger.error(f"Gagal buat grafik: {e}")
        await update.message.reply_text(f"📊 Total: {total} kali.\n(Gagal memuat gambar grafik karena error sistem).")

# --- Callback & AI ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    data = q.data.split("|")
    if data[0] == "minum":
        obat_name = unquote_plus(data[1])
        db.log_minum_obat(q.from_user.id, obat_name, "tepat_waktu")
        await q.edit_message_text(f"✅ {obat_name} sudah diminum. Tercatat!")

async def chat_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private": return
    reply = ai.get_ai_response(update.message.text)
    await update.message.reply_text(reply)

# --- Scheduler Logic ---

async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
    tz = pytz.timezone("Asia/Jakarta")
    now_str = datetime.now(tz).strftime("%H:%M")
    
    # Import collection di dalam fungsi untuk menghindari circular import
    from database import users_collection
    
    if users_collection is None: return

    try:
        cursor = users_collection.find({"jadwal_obat.jam": now_str})
        
        for user in cursor:
            user_id = user["user_id"]
            obat_list = [o["obat"] for o in user["jadwal_obat"] if o["jam"] == now_str]
            
            for obat in obat_list:
                safe_obat = quote_plus(obat)
                kb = [[InlineKeyboardButton("✅ Sudah Minum", callback_data=f"minum|{safe_obat}")]]
                
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"⏰ **Waktunya Minum Obat!**\n💊 {obat}",
                        reply_markup=InlineKeyboardMarkup(kb)
                    )
                    logger.info(f"Reminder sent to {user_id}")
                except Exception:
                    pass
    except Exception as e:
        logger.error(f"Scheduler Error: {e}")