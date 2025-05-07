import logging
from telegram import Update
from telegram.constants import ChatAction, ParseMode, ChatType
from telegram.ext import ContextTypes
from telegram.error import BadRequest
import gemini_client
from config import GROUP_TRIGGER_COMMANDS

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.message.chat_id
    gemini_client.reset_chat_history(chat_id)
    logger.info(f"Riwayat chat direset untuk {chat_id} karena perintah /start.")
    await update.message.reply_html(
        f"Halo {user.mention_html()}! aku adalah bot AI yang terhubung ke Gemini. ",
    )
    logger.info(f"User {user.id} ({user.first_name}) memulai bot di chat {chat_id}.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menerima pesan teks, mengirim ke Gemini, dan mencoba membalas."""
    message = update.message
    user_message = message.text
    user = update.effective_user
    chat_id = message.chat_id
    chat_type = message.chat.type

    if not user_message:
        logger.debug(f"Pesan tanpa teks diterima dari {user.id} di chat {chat_id}. Diabaikan.")
        return

    logger.info(f"Menerima pesan dari {user.id} ({user.first_name}) di chat {chat_id} (tipe: {chat_type}): \"{user_message}\"")

    should_respond = False
    actual_message_to_process = user_message

    if chat_type == ChatType.PRIVATE:
        should_respond = True
        logger.debug(f"Pesan di private chat {chat_id}. Bot akan merespon.")
    elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        logger.debug(f"Pesan di grup {chat_id}. Mengecek kondisi respon...")
        bot_id = context.bot.id

        if message.reply_to_message and message.reply_to_message.from_user.id == bot_id:
            should_respond = True
            actual_message_to_process = user_message
            logger.info(f"Pesan di grup {chat_id} adalah reply ke bot (ID: {bot_id}). Bot akan merespon dengan: \"{actual_message_to_process}\"")
        else:
            msg_lower = user_message.lower()
            for trigger_command_config in GROUP_TRIGGER_COMMANDS:
                trigger = trigger_command_config.lower()

                if msg_lower.startswith(trigger):
                    if len(msg_lower) == len(trigger):
                        should_respond = True
                        actual_message_to_process = "" # Tidak ada teks tambahan setelah command
                        logger.info(f"Pesan di grup {chat_id} adalah trigger command '{trigger_command_config}' saja. Bot akan merespon.")
                        break
                    # Pesan adalah trigger command diikuti spasi dan teks (misal "/ai halo")
                    elif len(msg_lower) > len(trigger) and msg_lower[len(trigger)].isspace():
                        should_respond = True
                        actual_message_to_process = user_message[len(trigger):].strip()
                        logger.info(f"Pesan di grup {chat_id} menggunakan trigger command '{trigger_command_config}'. Teks diproses: \"{actual_message_to_process}\". Bot akan merespon.")
                        break

            if not should_respond:
                 logger.debug(f"Pesan di grup {chat_id} bukan reply ke bot dan tidak menggunakan trigger command yang valid. Bot tidak merespon.")

    if not should_respond:
        logger.debug(f"Kondisi respon tidak terpenuhi untuk pesan di chat {chat_id}. Bot tidak mengirim balasan.")
        return

    if not actual_message_to_process and chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        # jika pengguna hanya mengetik "/ai" tanpa pertanyaan.
        logger.info(f"Pesan proses kosong setelah trigger command di grup {chat_id}. Bot tidak mengirim ke Gemini.")
        # kalian bisa mengirim pesan bantuan di sini, misalnya:
        await update.message.reply_text(f"Mohon sertakan pertanyaan kamu setelah {trigger_command_config} atau periksa /help.")
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    gemini_reply = await gemini_client.generate_response(actual_message_to_process, chat_id)

    if gemini_reply:
        try:
            await message.reply_text(gemini_reply, parse_mode=ParseMode.MARKDOWN)
            logger.info(f"Mengirim balasan Gemini ke chat {chat_id} (reply ke message_id: {message.message_id})")
        except BadRequest as e:
            if "can't parse entities" in str(e).lower():
                logger.warning(f"Gagal mengirim sebagai Markdown ke chat {chat_id}: {e}. Mencoba plain text.")
                try:
                    await message.reply_text(gemini_reply)
                    logger.info(f"Mengirim balasan Gemini (Plain Text Fallback) ke chat {chat_id} (reply ke message_id: {message.message_id})")
                except Exception as fallback_e:
                    logger.error(f"Gagal mengirim fallback plain text ke chat {chat_id}: {fallback_e}")
                    await message.reply_text("Maaf, saya kesulitan mengirim balasan. Silakan coba lagi.")
            else:
                logger.error(f"Error BadRequest (bukan parsing) saat mengirim balasan ke chat {chat_id}: {e}")
                await message.reply_text("Maaf, terjadi kesalahan saat mengirim balasan.")
        except Exception as e:
            logger.error(f"Error tak terduga saat mengirim balasan ke chat {chat_id}: {e}")
            await message.reply_text("Maaf, terjadi kesalahan tak terduga saat mengirim balasan.")
    else:
        await message.reply_text("Maaf, terjadi kesalahan internal saat memproses permintaan Anda.")
        logger.error(f"Gagal mendapatkan balasan valid dari gemini_client untuk chat {chat_id} untuk pesan: \"{actual_message_to_process}\"")


async def reset_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    user = update.effective_user
    if gemini_client.reset_chat_history(chat_id):
        await update.message.reply_text("Oke, saya telah melupakan percakapan kita sebelumnya di chat ini.")
        logger.info(f"User {user.id} ({user.first_name}) mereset riwayat di chat {chat_id}.")
    else:
        await update.message.reply_text("Sepertinya belum ada percakapan yang perlu direset untuk chat ini.")
        logger.info(f"User {user.id} ({user.first_name}) mencoba mereset riwayat kosong di chat {chat_id}.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Memberikan pesan bantuan dasar."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) memanggil /help.")

    trigger_commands_text = ", ".join(GROUP_TRIGGER_COMMANDS)
    if not trigger_commands_text:
        trigger_commands_text = "(tidak ada yang diatur)"

    help_text = (
        "Butuh bantuan? Berikut beberapa perintah:\n"
        "/start - Memulai ulang bot & mereset percakapan.\n"
        "/reset - Melupakan percakapan saat ini.\n"
        "/help - Menampilkan pesan ini.\n\n"
        f"Di grup, gunakan perintah seperti `{GROUP_TRIGGER_COMMANDS[0] if GROUP_TRIGGER_COMMANDS else '/ai'} pertanyaan kamu` "
        "atau balas pesan ku untuk berinteraksi.\n"
        f"Trigger command yang aktif di grup: {trigger_commands_text}\n"
        "Di chat pribadi, kamu bisa langsung mengirim pesan."
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
