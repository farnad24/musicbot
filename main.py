import os
import numpy as np
import librosa
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# تنظیمات اولیه
TELEGRAM_BOT_TOKEN = "7939569062:AAFWnOhEENiZM7QCJWFj59vsojdPj5vxMoY"
AUDIO_DATABASE_PATH = "/music"

# تابع ایجاد اثر انگشت صوتی
def create_fingerprint(audio_file_path):
    y, sr = librosa.load(audio_file_path)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    return np.mean(chroma, axis=1)  # میانگین Chroma Features

# تابع مقایسه اثر انگشت صوتی
def find_song_in_database(audio_file_path, database_path):
    query_fingerprint = create_fingerprint(audio_file_path)
    best_match = None
    best_score = float('inf')  # کمترین فاصله بهترین تطابق است

    for root, dirs, files in os.walk(database_path):
        for file in files:
            if file.endswith(('.mp3', '.wav')):
                song_path = os.path.join(root, file)
                song_fingerprint = create_fingerprint(song_path)
                distance = np.linalg.norm(query_fingerprint - song_fingerprint)  # محاسبه فاصله اقلیدسی
                if distance < best_score:
                    best_score = distance
                    best_match = song_path

    return best_match

# تابع استخراج صدا
def extract_audio_from_video(video_file_path, output_audio_path):
    from moviepy.editor import VideoFileClip
    video = VideoFileClip(video_file_path)
    video.audio.write_audiofile(output_audio_path)

# تابع شروع ربات
async def start(update: Update, context):
    await update.message.reply_text("سلام! من ربات تشخیص آهنگ هستم. یک فایل صوتی، ویدئویی یا ویس ارسال کنید.")

# تابع برای دریافت و پردازش فایل‌ها
async def handle_file(update: Update, context):
    message = update.message
    file_id = None
    file_type = None

    # دریافت فایل ارسالی توسط کاربر
    if message.voice:
        file_id = message.voice.file_id
        file_type = "voice"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"

    if not file_id:
        await message.reply_text("لطفاً یک فایل صوتی، ویدئویی یا ویس ارسال کنید.")
        return

    # دانلود فایل
    file = await context.bot.get_file(file_id)
    file_path = f"downloads/{file_id}.{file_type}"
    await file.download_to_drive(file_path)

    # اگر فایل ویدئویی باشد، صدای آن را استخراج کنید
    if file_type == "video":
        audio_file_path = f"downloads/{file_id}_audio.mp3"
        extract_audio_from_video(file_path, audio_file_path)
        file_path = audio_file_path

    # شناسایی آهنگ
    matched_song = find_song_in_database(file_path, AUDIO_DATABASE_PATH)

    if matched_song:
        await message.reply_text(f"آهنگ شناسایی شده: {os.path.basename(matched_song)}")
        await message.reply_audio(audio=open(matched_song, 'rb'))
    else:
        await message.reply_text("متاسفانه نتوانستم آهنگ را شناسایی کنم.")

# تابع اصلی
def main():
    # ایجاد یک شیء Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO | filters.VIDEO, handle_file))

    # شروع ربات
    application.run_polling()

if __name__ == '__main__':
    main()