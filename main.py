import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import config
import bot_handlers
import gemini_client

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main() -> None:
    """Jalankan bot."""
    logger.info("Memulai bot...")

    # Validasi Kritis: Pastikan token ada
    if not config.TELEGRAM_TOKEN:
        logger.critical("CRITICAL: Token Telegram tidak ditemukan di environment variables! Bot tidak bisa berjalan.")
        sys.exit("Token Telegram tidak ditemukan.") 

    if not gemini_client.configure_gemini():
        logger.warning("WARNING: Gagal mengkonfigurasi Gemini API! Fitur AI mungkin tidak berfungsi.")

    application = Application.builder().token(config.TELEGRAM_TOKEN).build()

    # Pendaftaran Handler dari config.COMMANDS
    registered_commands = []
    for command_name, function_name_str in config.COMMANDS.items():
        try:
            handler_func = getattr(bot_handlers, function_name_str)
            application.add_handler(CommandHandler(command_name, handler_func))
            registered_commands.append(f"/{command_name}")
            logger.info(f"Command /{command_name} berhasil didaftarkan ke fungsi {function_name_str}.")
        except AttributeError:
            logger.error(f"ERROR: Fungsi '{function_name_str}' tidak ditemukan di bot_handlers.py untuk command '/{command_name}'. Command ini tidak akan berfungsi.")
        except Exception as e:
            logger.error(f"ERROR: Gagal mendaftarkan command '/{command_name}' : {e}")

    logger.info(f"Command yang terdaftar: {', '.join(registered_commands)}")

    # Daftarkan handler lain (seperti MessageHandler) di bawah ini
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.handle_message))
    # Jika ada handler lain (CallbackQueryHandler, etc.), daftarkan di sini

    
    logger.info("Bot siap menerima pesan...")
    application.run_polling()
    logger.info("Bot dihentikan.")


if __name__ == '__main__':
    main()