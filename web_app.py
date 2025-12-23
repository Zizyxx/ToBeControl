from flask import Flask, render_template, request, redirect, url_for, session
import os
import hashlib
import hmac
import time
from datetime import datetime
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

# Load Environment
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
BOT_USERNAME = "ToBeControl_bot" # Ganti dengan username bot kamu (tanpa @)

# Setup Flask
app = Flask(__name__)
app.secret_key = "kunci_rahasia_acak_bebas" # Ganti dengan random string untuk keamanan session

# Setup Database (Sama seperti di Bot)
try:
    mongo_client = MongoClient(
        MONGO_URI,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000,
    )
    db = mongo_client["tbc_bot_db"]
    users_collection = db["users"]
    logs_collection = db["logs"]
    print("✅ Website terhubung ke MongoDB!")
except Exception as e:
    print(f"❌ Gagal koneksi DB: {e}")

# --- Fungsi Keamanan Telegram ---
def check_telegram_authorization(auth_data):
    """
    Memverifikasi apakah data login benar-benar dari Telegram (Anti Hack).
    """
    check_hash = auth_data.get('hash')
    if not check_hash:
        return False
        
    data_check_arr = []
    for key, value in auth_data.items():
        if key != 'hash':
            data_check_arr.append(f'{key}={value}')
    
    data_check_arr.sort()
    data_check_string = '\n'.join(data_check_arr)
    
    secret_key = hashlib.sha256(TELEGRAM_TOKEN.encode()).digest()
    hash_calc = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    if hash_calc != check_hash:
        return False
        
    # Cek kedaluwarsa (data login cuma valid sebentar)
    if (time.time() - int(auth_data.get('auth_date'))) > 86400:
        return False
        
    return True

# --- Routes (Halaman Website) ---

@app.route('/')
def home():
    # Jika sudah login, lempar ke dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html', bot_username=BOT_USERNAME)

@app.route('/login_callback')
def login_callback():
    # Menerima data dari Widget Telegram
    data = request.args.to_dict()
    
    if check_telegram_authorization(data):
        # Login Sukses! Simpan sesi
        session['user_id'] = int(data['id'])
        session['first_name'] = data.get('first_name')
        session['photo_url'] = data.get('photo_url') # Foto profil telegram
        
        # Simpan/Update user di database (sync data baru)
        users_collection.update_one(
            {"user_id": int(data['id'])},
            {"$set": {
                "first_name": data.get('first_name'),
                "username": data.get('username'),
                "last_active_web": datetime.now()
            }},
            upsert=True
        )
        return redirect(url_for('dashboard'))
    else:
        return "Login Gagal atau Kadaluarsa."

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    user_id = session['user_id']
    
    # 1. Ambil Data Profil
    user = users_collection.find_one({"user_id": user_id})
    jadwal = user.get('jadwal_obat', []) if user else []
    
    # 2. Ambil Statistik
    total_minum = logs_collection.count_documents({"user_id": user_id})
    
    # 3. Ambil Log Terakhir (Max 5)
    logs = list(logs_collection.find({"user_id": user_id}).sort("waktu", -1).limit(5))
    
    return render_template(
        'dashboard.html', 
        user=session, 
        jadwal=jadwal, 
        total=total_minum,
        logs=logs
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)