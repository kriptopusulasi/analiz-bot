import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters, ConversationHandler
)

TOKEN = "8429998639:AAGz51yiH8T8xsft5ERpOaZc9qV8AHXC7QM"
GROUP_ID = -1003862895508

logging.basicConfig(level=logging.INFO)

ZAMAN_SEC, PARITE_YAZ = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📊 Analiz Talep Et", callback_data="analiz_baslat")]]
    await update.message.reply_text(
        "👋 PSL WEEX Analiz Botuna Hoşgeldiniz!\n\nAnaliz talebinde bulunmak için butona basın.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def analiz_baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("⏱ 15 Dakika", callback_data="z_15dk"),
         InlineKeyboardButton("⏱ 1 Saat", callback_data="z_1s")],
        [InlineKeyboardButton("⏱ 4 Saat", callback_data="z_4s"),
         InlineKeyboardButton("⏱ 1 Gün", callback_data="z_1g")]
    ]
    await query.edit_message_text(
        "⏱ Zaman dilimini seçin:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ZAMAN_SEC

async def zaman_secildi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    zaman_map = {"z_15dk": "15 Dakika", "z_1s": "1 Saat", "z_4s": "4 Saat", "z_1g": "1 Gün"}
    context.user_data["zaman"] = zaman_map[query.data]
    await query.edit_message_text(
        f"✅ Zaman: {context.user_data['zaman']}\n\nHangi pariteyi analiz etmemi istersiniz?\n(Örnek: BTC/USDT)",
    )
    return PARITE_YAZ

async def parite_alindi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parite = update.message.text.upper()
    zaman = context.user_data.get("zaman", "Bilinmiyor")
    kullanici = update.message.from_user
    isim = kullanici.first_name
    if kullanici.last_name:
        isim += f" {kullanici.last_name}"
    username = f"@{kullanici.username}" if kullanici.username else "Kullanici adi yok"

    keyboard = [[InlineKeyboardButton("📊 Yeni Analiz Talep Et", callback_data="analiz_baslat")]]
    await update.message.reply_text(
        f"Talebiniz alindi!\n\nParite: {parite}\nZaman: {zaman}\n\nAnalistler en kisa surede analizi paylasacak.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=(
            f"YENI ANALIZ TALEBI\n"
            f"---\n"
            f"Talep Eden: {isim} ({username})\n"
            f"Parite: {parite}\n"
            f"Zaman Dilimi: {zaman}\n"
            f"---\n"
            f"Analiz yapacak analist lutfen yanitlayin!"
        )
    )
    return ConversationHandler.END

async def iptal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Iptal edildi.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(analiz_baslat, pattern="analiz_baslat")],
        states={
            ZAMAN_SEC: [CallbackQueryHandler(zaman_secildi, pattern="^z_")],
            PARITE_YAZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, parite_alindi)],
        },
        fallbacks=[CommandHandler("iptal", iptal)],
        per_chat=False
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    print("Bot baslatiliyor...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
