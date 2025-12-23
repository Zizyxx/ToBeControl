import pytz
import certifi
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from config import uri, logger

# --- Setup Koneksi ---
try:
    mongo_client = MongoClient(
        uri,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000,
    )
    # Test Ping
    mongo_client.admin.command("ping")
    
    db = mongo_client["tbc_bot_db"]
    users_collection = db["users"]
    logs_collection = db["logs"]

    # Buat Index biar cepat
    users_collection.create_index([("user_id", ASCENDING)], background=True)
    logs_collection.create_index([("user_id", ASCENDING)], background=True)

    logger.info("✅ Terhubung ke MongoDB.")

except Exception as e:
    logger.error(f"❌ Gagal koneksi MongoDB: {e}")
    users_collection = None
    logs_collection = None

# --- Fungsi-Fungsi CRUD ---

def register_user(user_id, first_name, username):
    if users_collection is None: return
    try:
        users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "first_name": first_name or "",
                    "username": username or "",
                    "last_active": datetime.now(pytz.timezone("Asia/Jakarta")),
                },
                "$setOnInsert": {"jadwal_obat": []},
            },
            upsert=True,
        )
    except Exception:
        logger.exception("Error register_user")

def add_jadwal(user_id, jam, nama_obat):
    if users_collection is None: return False
    try:
        # Cek duplikat
        found = users_collection.find_one(
            {"user_id": user_id, "jadwal_obat": {"$elemMatch": {"jam": jam, "obat": nama_obat}}}
        )
        if found:
            return False
            
        users_collection.update_one(
            {"user_id": user_id},
            {"$push": {"jadwal_obat": {"jam": jam, "obat": nama_obat}}}
        )
        return True
    except Exception:
        logger.exception("Error add_jadwal")
        return False

def get_jadwal(user_id):
    if users_collection is None: return []
    try:
        doc = users_collection.find_one({"user_id": user_id})
        return doc.get("jadwal_obat", []) if doc else []
    except Exception:
        return []

def delete_jadwal(user_id, jam, obat=None):
    if users_collection is None: return 0
    try:
        query = {"jadwal_obat": {"jam": jam}}
        if obat:
            query["jadwal_obat"]["obat"] = obat
            
        res = users_collection.update_one(
            {"user_id": user_id},
            {"$pull": query}
        )
        return res.modified_count
    except Exception:
        return 0

def log_minum_obat(user_id, obat, status):
    if logs_collection is None: return
    try:
        logs_collection.insert_one({
            "user_id": user_id,
            "obat": obat,
            "status": status,
            "waktu": datetime.now(pytz.timezone("Asia/Jakarta")),
        })
    except Exception:
        logger.exception("Error log_minum_obat")

def get_total_logs(user_id):
    if logs_collection is None: return 0
    return logs_collection.count_documents({"user_id": user_id})

def get_daily_logs(user_id):
    """Mengambil data minum obat 7 hari terakhir untuk grafik"""
    if logs_collection is None: return {}
    
    try:
        # Pipeline Agregasi MongoDB:
        # 1. Filter berdasarkan User ID
        # 2. Grouping berdasarkan tanggal (YYYY-MM-DD)
        # 3. Hitung jumlah obat
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$waktu", "timezone": "Asia/Jakarta"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}, # Urutkan dari tanggal terlama
            {"$limit": 7}          # Ambil max 7 hari terakhir
        ]
        
        results = list(logs_collection.aggregate(pipeline))
        
        # Format ulang hasil agar mudah dipakai di grafik
        # Contoh output: {'2023-11-20': 3, '2023-11-21': 2}
        data = {item["_id"]: item["count"] for item in results}
        return data

    except Exception as e:
        logger.exception("Error get_daily_logs")
        return {}