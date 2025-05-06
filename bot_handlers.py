import logging
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes
from telegram.error import BadRequest
import gemini_client


logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.message.chat_id
    gemini_client.reset_chat_history(chat_id)
    logger.info(f"Riwayat chat direset untuk {chat_id} karena perintah /start.")
    await update.message.reply_html(
        f"Halo {user.mention_html()}! Saya adalah bot AI yang terhubung ke Gemini. ",
    )
    logger.info(f"User {user.id} ({user.first_name}) memulai bot di chat {chat_id}.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menerima pesan teks, mengirim ke Gemini, dan mencoba membalas."""
    user_message = update.message.text
    user = update.effective_user
    chat_id = update.message.chat_id
    logger.info(f"Menerima pesan dari {user.id} ({user.first_name}) di chat {chat_id}: {user_message}")

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    gemini_reply = await gemini_client.generate_response(user_message, chat_id)

    if gemini_reply:
        try:
            await update.message.reply_text(gemini_reply, parse_mode=ParseMode.MARKDOWN) 
            logger.info(f"Mengirim balasan Gemini ke chat {chat_id}")
        except BadRequest as e:
            if "can't parse entities" in str(e).lower():
                logger.warning(f"Gagal mengirim sebagai Markdown Legacy ke chat {chat_id}: {e}. Mencoba                    plain text.")
                try:
                    await update.message.reply_text(gemini_reply) 
                    logger.info(f"Mengirim balasan Gemini (Plain Text Fallback) ke chat {chat_id}")
                except Exception as fallback_e:
                    logger.error(f"Gagal mengirim fallback plain text ke chat {chat_id}: {fallback_e}")
                    await update.message.reply_text("Maaf, saya kesulitan mengirim balasan. Silakan coba                       lagi.")
            else:
                logger.error(f"Error BadRequest (bukan parsing) saat mengirim balasan ke chat {chat_id}:                   {e}")
                await update.message.reply_text("Maaf, terjadi kesalahan saat mengirim balasan.")
        except Exception as e:
            logger.error(f"Error tak terduga saat mengirim balasan ke chat {chat_id}: {e}")
            await update.message.reply_text("Maaf, terjadi kesalahan tak terduga saat mengirim balasan.")
    else:
        await update.message.reply_text("Maaf, terjadi kesalahan internal saat memproses permintaan Anda.")
        logger.error(f"Gagal mendapatkan balasan valid dari gemini_client untuk chat {chat_id}")


async def reset_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    user = update.effective_user
    if gemini_client.reset_chat_history(chat_id):
        await update.message.reply_text("Oke, saya telah melupakan percakapan kita sebelumnya di chat ini")
        logger.info(f"User {user.id} ({user.first_name}) mereset riwayat di chat {chat_id}.")
    else:
        await update.message.reply_text("Sepertinya belum ada percakapan yang perlu direset untuk chat             ini.")
        logger.info(f"User {user.id} ({user.first_name}) mencoba mereset riwayat kosong di chat                    {chat_id}.")

# Fungsi Help_command
# Fungsi ini akan memberikan pesan bantuan kepada pengguna.
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Memberikan pesan bantuan dasar."""
    logger.info(f"User {update.effective_user.id} memanggil /help.")
    help_text = (
        "Butuh bantuan? Berikut beberapa perintah:\n"
        "/start - Memulai ulang bot\n"
        "/reset - Melupakan percakapan\n"
        "/about - Info tentang bot ini\n"
        "/help - Menampilkan pesan ini\n\n"
        "Kirim pesan biasa untuk berbicara dengan AI."
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN) 

# jika kalian ingin menambahkan fungsi lain, tambahkan di sini
# jika sudah, jangan lupa untuk daftarkan di config.py di bagian COMMANDS dan main.py di bagian application.add_handler(CommandHandler(command_name, handler_func))