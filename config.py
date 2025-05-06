import os
import logging

# Konfigurasi Kunci API
# Mengambil dari Replit Secrets atau Environment Variables (ENV)
# jika kalian ingin mendeploy contoh nya di pythonanywhere, pastkan untuk menambah file .env di folder dan tambahkan variabel TELEGRAM_TOKEN dan GEMINI_API_KEY di dalamnya, jangan lupa juga isi requirements.txt dengan python-dotenv agar bisa membaca file .env. Jika sudah install requirements.txt dengan pip install -r requirements.txt di terminal pythonanywhere

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Validasi Kunci API
if not TELEGRAM_TOKEN:
    logging.warning("Token Telegram tidak ditemukan! Atur di Secrets.")
if not GEMINI_API_KEY:
    logging.warning("Kunci API Gemini tidak ditemukan! Atur di Secrets.")

# Konfigurasi Gemini
# Pilih model Gemini yang ingin kamu gunakan, pastikan kamu menggunakan nama model yang benar yang diambil dari nama versi yang ada di https://ai.google.dev/gemini-api/docs/models    (contoh: gemini-1.5-flash-latest)
GEMINI_MODEL_NAME = 'gemini-1.5-flash-latest'  

# INTRUKSI SISTEM (SYSTEM PROMPT) UNTUK GEMINI
# Gunakan ini untuk mengatur kepribadian atau persona AI.
# Ubah teks di bawah ini sesuai keinginan kamu.
GEMINI_SYSTEM_INSTRUCTION = "menjadi orang yang sangat pintar"

# Konfigurasi Perintah (commands)
# jika ada commands yang lain tambahkan di sini, jangan lupa di daftarkan di bot_handlers.py jangan lupa juga daftarkan di main.py di bagian application.add_handler(CommandHandler(command_name, handler_func)) 
COMMANDS = {
    "start": "start",               # /start memanggil fungsi start
    "reset": "reset_chat",          # /reset memanggil fungsi reset_chat
    "about": "about",               # /about memanggil fungsi about
    "help": "help_command",         # /help memanggil fungsi help_command
}
