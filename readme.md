# Telebot-Gemini PythonAnywhere Setup

## Persyaratan

1.  **Akun PythonAnywhere:** kalian memerlukan akun di [PythonAnywhere](https://www.pythonanywhere.com/). Akun gratis sudah cukup untuk bot sederhana.
2.  **Kunci API Telegram:** Dapatkan token bot dari [@BotFather](https://t.me/BotFather) di Telegram.
3.  **Kunci API Gemini:** Dapatkan kunci API dari [Google AI Studio](https://aistudio.google.com/apikey).

## Langkah-langkah Penyiapan di PythonAnywhere

1.  **Buka Konsol Bash:**
    * Login ke akun PythonAnywhere.
    * Buka tab "Consoles".
    * Mulai konsol "Bash".

2.  **Clone Repository:**
    * Di dalam konsol Bash, clone repository ini:
      ```bash
      git clone https://github.com/ulya2402/telebot-gemini
      ```
    * Masuk ke direktori proyek:
      ```bash
      cd telebot-gemini
      ```

3.  **Buat dan Aktifkan Lingkungan Virtual (Virtual Environment):**
    * Sangat disarankan untuk menggunakan lingkungan virtual:
      ```bash
      python3.9 -m venv myenv
      ```
    * Aktifkan lingkungan virtual:
      ```bash
      source myenv/bin/activate
      ```
    * Anda akan melihat `(myenv)` di awal baris perintah jika berhasil.

4.  **Buat Berkas `.env`:**
    * Buat berkas bernama `.env` di dalam direktori proyek utama:
      ```bash
      nano .env
      ```
    * Masukkan kunci API Anda ke dalam berkas tersebut dengan format berikut (ganti `nilai_token...` dan `nilai_api...` dengan kunci asli kalian):
      ```dotenv
      TELEGRAM_TOKEN=nilai_token_telegram_kalian
      GEMINI_API_KEY=nilai_api_gemini_kalian
      ```
    * Simpan berkas dan keluar dari editor `nano` (tekan `Ctrl+X`, lalu `Y`, lalu `Enter`).

5.  **Instal Pustaka yang Dibutuhkan:**
    * Pastikan kalian masih berada di dalam lingkungan virtual (`(myenv)`).
    * Instal semua pustaka dari `requirements.txt`:
      ```bash
      pip install -r requirements.txt
      ```
6. **Jalankan Bot**
   Pastikan kalian masih berada di direktori proyek utama dan lingkungan virtual (`myenv`) aktif.
   * Jalankan skrip utama bot:
      ```bash
      python main.py
      ```

## Konfigurasi Tambahan (Opsional)

* **Mengubah Instruksi Sistem Gemini:** Edit berkas `config.py` dan ubah nilai variabel `GEMINI_SYSTEM_INSTRUCTION`.
* **Mengganti Model Gemini:** Edit berkas `config.py` dan ubah nilai variabel `GEMINI_MODEL_NAME`. Pastikan menggunakan nama model yang valid dari [dokumentasi model Gemini](https://ai.google.dev/gemini-api/docs/models).
