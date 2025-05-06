import logging
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME, GEMINI_SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)

gemini_model_base = None
active_chats = {}  

def configure_gemini():
    """Mengkonfigurasi API dan model dasar Gemini."""
    global gemini_model_base
    if not GEMINI_API_KEY:
        logger.error("Kunci API Gemini tidak ada. Tidak dapat mengkonfigurasi Gemini.")
        return False

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model_base = genai.GenerativeModel(
            GEMINI_MODEL_NAME,
            system_instruction=GEMINI_SYSTEM_INSTRUCTION
        )
        logger.info(f"Model dasar Gemini '{GEMINI_MODEL_NAME}' berhasil dikonfigurasi.")
        active_chats.clear()
        return True
    except Exception as e:
        logger.error(f"Gagal mengkonfigurasi Gemini API: {e}")
        gemini_model_base = None
        active_chats.clear()
        return False

async def generate_response(prompt: str, chat_id: int) -> str | None:
    """
    Mengirim prompt ke Gemini menggunakan sesi chat yang sesuai (mempertahankan histori).
    Membuat sesi baru jika belum ada untuk chat_id tersebut.
    """
    global gemini_model_base, active_chats

    if gemini_model_base is None:
        logger.error("Model dasar Gemini belum diinisialisasi.")
        return "Maaf, koneksi ke AI sedang bermasalah (Model dasar tidak siap)."

    if chat_id not in active_chats:
        logger.info(f"Membuat sesi chat baru untuk chat_id: {chat_id}")
        active_chats[chat_id] = gemini_model_base.start_chat(history=[])
    chat_session = active_chats[chat_id]

    logger.info(f"Mengirim prompt ke Gemini (Chat ID: {chat_id}): '{prompt[:100]}...'")
    try:
        response = await chat_session.send_message_async(prompt)

        if response.prompt_feedback and response.prompt_feedback.block_reason:
            reason = response.prompt_feedback.block_reason
            logger.warning(f"Permintaan diblokir oleh Gemini (Chat ID: {chat_id}) karena: {reason}")
            return f"Maaf, permintaan Anda tidak dapat diproses karena alasan keamanan: {reason}. Riwayat              chat mungkin terpengaruh."

        gemini_reply = response.text
        logger.info(f"Menerima balasan dari Gemini (Chat ID: {chat_id}): '{gemini_reply[:100]}...'")
        return gemini_reply

    except Exception as e:
        logger.error(f"Terjadi error saat generate content dari Gemini (Chat ID: {chat_id}): {e}")
        try:
             pass
        except:
            pass
        return "Maaf, terjadi kesalahan saat menghubungi AI. Silakan coba lagi nanti."

def reset_chat_history(chat_id: int):
    """Menghapus riwayat percakapan untuk chat_id tertentu."""
    global active_chats
    if chat_id in active_chats:
        del active_chats[chat_id]
        logger.info(f"Riwayat percakapan untuk chat_id {chat_id} telah dihapus.")
        return True
    else:
        logger.info(f"Tidak ada riwayat percakapan aktif untuk chat_id {chat_id} untuk dihapus.")
        return False