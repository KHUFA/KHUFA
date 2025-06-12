from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import os
from utils import convert_and_get_page_count
from payments import generate_qr
from printer import print_file, get_printer_status

# --- НАСТРОЙКИ ---
TOKEN = "7553375409:AAFWjmqr58Q7DoKgzkZhTCedcc7LlWX9v3c"
ADMIN_ID = 1039033897
price_per_page = 5
greeting_message = "👋 Привет! Отправьте документ (.pdf, .doc, .docx) или изображение (.jpg, .png) для печати."

# --- КОМАНДЫ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(greeting_message)

async def set_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    global price_per_page
    try:
        price_per_page = int(context.args[0])
        await update.message.reply_text(f"✅ Цена за страницу установлена: {price_per_page}₽")
    except:
        await update.message.reply_text("⚠️ Введите цену правильно. Пример: /price 7")

async def set_greeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    global greeting_message
    greeting_message = " ".join(context.args)
    await update.message.reply_text("✅ Приветственное сообщение обновлено.")

async def printer_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    status = get_printer_status()
    await update.message.reply_text(f"🖨 Статус принтера: {status}")

# --- ОБРАБОТКА ФАЙЛОВ ---
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    file_ext = os.path.splitext(doc.file_name)[-1].lower()
    if file_ext not in ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']:
        await update.message.reply_text("❌ Поддерживаются только: .pdf, .doc, .docx, .jpg, .png")
        return

    os.makedirs("files", exist_ok=True)
    file = await doc.get_file()
    original_path = f"files/{file.file_unique_id}{file_ext}"
    await file.download_to_drive(original_path)

    try:
        pdf_path, pages = convert_and_get_page_count(original_path)
        price = pages * price_per_page

        context.user_data['file'] = os.path.abspath(pdf_path)
        context.user_data['price'] = price

        keyboard = [[InlineKeyboardButton("💳 Оплатить", callback_data="pay")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Файл: {doc.file_name}\nСтраниц: {pages}\nСтоимость: {price}₽",
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при обработке файла: {e}")

# --- КОЛЛБЭК ОПЛАТЫ ---
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "pay":
        price = context.user_data.get("price", 0)
        qr_path = generate_qr(price)
        await query.message.reply_photo(photo=open(qr_path, 'rb'), caption="Отсканируйте QR для оплаты")

        file_abs_path = context.user_data.get("file")
        try:
            print_file(file_abs_path)
            await query.message.reply_text("✅ Печать началась!")
        except Exception as e:
            await query.message.reply_text(f"❌ Ошибка при печати: {e}")

# --- ЛЮБЫЕ СООБЩЕНИЯ ---
async def any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and not update.message.text.startswith('/'):
        await update.message.reply_text(greeting_message)

# --- ЗАПУСК ---
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", set_price))
app.add_handler(CommandHandler("setgreet", set_greeting))
app.add_handler(CommandHandler("printer", printer_status))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), any_message))

if __name__ == "__main__":
    app.run_polling()
