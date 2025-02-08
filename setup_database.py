from dejavu import Dejavu

# تنظیمات Dejavu
config = {
    "database": {
        "host": "127.0.0.1",
        "user": "",
        "password": "",
        "database": "dejavu_db.db"
    }
}

djv = Dejavu(config)

# افزودن آهنگ‌ها به دیتابیس
djv.fingerprint_directory("/music", [".mp3", ".wav"])