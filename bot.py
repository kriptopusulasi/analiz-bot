import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = "8429998639:AAGz51yiH8T8xsft5ERpOaZc9qV8AHXC7QM"
GROUP_ID = -1003862895508

ZAMAN_SEC, PARITE_YAZ = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Analiz Talep Et", callback_data="baslat")]]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("PSL WEEX Analiz Botu\n\nAnaliz talebinde bulunmak icin asagidaki butona basin.", reply_markup=markup)

async def baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("15 Dakika", callback_data="z15"), InlineKeyboardButton("1 Saat", callback_data="z1s")],
        [InlineKeyboardButton("4 Saat", callback_data="z4s"), InlineKeyboardButton("1 Gun", callback_data="z1g")]
    ]
    await query.edit_message_text("Zaman dilimini secin:", reply_markup=InlineKeyboardMarkup(keyboard))
    return ZAMAN_SEC

async def zaman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    zaman_map = {"z15": "15 Dakika", "z1s": "1 Saat", "z4s": "4 Saat", "z1g": "1 Gun"}
    context.user_data["zaman"] = zaman_map.get(query.data, "?")
    await query.edit_message_text(f"Zaman: {context.user_data['zaman']}\n\nHangi pariteyi analiz etmemi istersiniz?\nOrnek: BTC/USDT")
    return PARITE_YAZ

async def parite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = update.message.text.upper()
    z = context.user_data.get("zaman", "?")
    u = update.message.from_user
    isim = u.first_name + (" " + u.last_name if u.last_name else "")
    username = "@" + u.username if u.username else "yok"

    keyboard = [[InlineKeyboardButton("Yeni Analiz Talep Et", callback_data="baslat")]]
    await update.message.reply_text(
        f"Talebiniz alindi!\nParite: {p}\nZaman: {z}\n\nAnalistler en kisa surede analizi paylasacak.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"YENI ANALIZ TALEBI\n---\nTalep Eden: {isim} ({username})\nParite: {p}\nZaman: {z}\n---\nAnaliz yapacak analist lutfen yanitlayin!"
    )
    return ConversationHandler.END

async def iptal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Iptal edildi.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(baslat, pattern="^baslat$")],
        states={
            ZAMAN_SEC: [CallbackQueryHandler(zaman, pattern="^z")],
            PARITE_YAZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, parite)],
        },
        fallbacks=[CommandHandler("iptal", iptal)],
        per_chat=False
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
