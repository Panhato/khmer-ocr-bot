import logging
import io

# Import សម្រាប់ Telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Import សម្រាប់ OCR
from PIL import Image
import pytesseract

# Import សម្រាប់ Pre-processing (កម្រិតខ្ពស់)
# import cv2  <-- យើងមិនប្រើវាទេ ពេលនេះ
# import numpy as np <-- យើងមិនប្រើវាទេ ពេលនេះ

import numpy as np

# --- ចាប់ផ្តើមការដំឡើង (Setup) ---

# កំណត់ទីតាំង Tesseract (ត្រូវការសម្រាប់តែ Windows ពេលខ្លះ)
# ត្រូវប្រាកដថា Path នេះត្រឹមត្រូវ បើអ្នកត្រូវការវា
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# បើកការ Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ដាក់ API Token "ថ្មី" របស់អ្នកនៅទីនេះ (បន្ទាប់ពីអ្នក Revoke)
# សូមប្រយ័ត្ន! កុំចែករំលែក TOKEN ថ្មីរបស់អ្នកទៀត!
YOUR_TOKEN = "7317233106:AAGZfc4Uizu9m3E3wwLJSqjZP7w8dF_-6ec" # <--- ជំនួស TEXT នេះដោយ TOKEN ពិតប្រាកដរបស់អ្នក!


# --- និយមន័យ Function របស់ Bot ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ផ្ញើសារស្វាគមន៍នៅពេលអ្នកប្រើវាយ /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"សួស្តី {user.mention_html()}!",
    )
    await update.message.reply_text("សូមផ្ញើរូបភាពដែលមានអក្សរខ្មែរ ឬអង់គ្លេសមក ខ្ញុំនឹងព្យាយាមអានវាឲ្យអ្នក។")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ផ្ញើសារណែនាំនៅពេលអ្នកប្រើវាយ /help"""
    await update.message.reply_text("គ្រាន់តែផ្ញើរូបភាព (photo) មក ខ្ញុំនឹងដកស្រង់អត្ថបទចេញពីវា។")


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    ដោះស្រាយពេលអ្នកប្រើផ្ញើរូបភាពមក (ជាមួយ Pre-processing)
    """
    
    await update.message.reply_text("កំពុងដំណើរការ (សាកល្បង_ແບບសាមញ្ញ)... សូមរង់ចាំបន្តិច...")
    
    try:
        # 1. ទាញយករូបភាព
        photo_file = await update.message.photo[-1].get_file()
        image_bytes_io = io.BytesIO()
        await photo_file.download_to_memory(image_bytes_io)
        image_bytes_io.seek(0)
        
        # 2. បើករូបភាពដោយប្រើ Pillow (PIL)
        # យើងត្រឡប់ទៅប្រើ Pillow វិញ ដើម្បីសាកល្បង
        img_pil = Image.open(image_bytes_io)

        # 3. ប្រើ Tesseract លើរូបភាព "ដើម" (PIL)
        # *** យើងរំលងជំហាន OpenCV (cv2) ទាំងអស់ ***
        text = pytesseract.image_to_string(img_pil, lang='khm+eng')

        if text.strip():
            await update.message.reply_text(f"✅ អត្ថបទ (ពី​រូប​ដើម):\n\n{text}")
        else:
            await update.message.reply_text("❌ រកមិនឃើញអត្ថបទ (ទោះបីជាបានសម្អាតរូបភាពហើយក៏ដោយ)។")
            
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        await update.message.reply_text(f"🚫 មានបញ្ហាក្នុងការដំណើរការរូបភាព៖ {e}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ឆ្លើយតបទៅនឹងសារអក្សរធម្មតា"""
    await update.message.reply_text("សូមផ្ញើជា 'រូបភាព' (Photo) មិនមែនជា 'ឯកសារ' (File) ឬអក្សរទេ។")


def main() -> None:
    """ចាប់ផ្តើម Bot"""
    # បង្កើត Application object
    application = Application.builder().token(YOUR_TOKEN).build()

    # ចុះឈ្មោះ Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # ចុះឈ្មោះ Message Handlers
    # នេះគឺជាកន្លែងដែល Function handle_image ត្រូវបានហៅ
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # ចាប់ផ្តើម Bot
    logger.info("Bot កំពុងដំណើរការ... ចុច Ctrl+C ដើម្បីបិទ។")
    application.run_polling()


# --- ចំណុចចាប់ផ្តើមដំណើរការ Script ---

if __name__ == "__main__":
    main()