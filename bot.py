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
    keyboard = [
        [InlineKeyboardButton("📊 Analiz Talep Et", callback_data="analiz_baslat")]
    ]
    await update.message.reply_text(
        "👋 PSL WEEX Analiz Botuna Hoşgeldiniz!\n\nAşağıdaki butona basarak analiz talebinde bulunabilirsiniz.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def analiz_baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⏱ 15 Dakika", callback_data="zaman_15dk"),
         InlineKeyboardButton("⏱ 1 Saat", callback_data="zaman_1s")],
        [InlineKeyboardButton("⏱ 4 Saat", callback_data="zaman_4s"),
         InlineKeyboardButton("⏱ 1 Gün", callback_data="zaman_1g")]
    ]
    await query.edit_message_text(
        "📊 Analiz talebiniz için zaman dilimini seçin:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ZAMAN_SEC

async def zaman_secildi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    zaman_map = {
        "zaman_15dk": "15 Dakika",
        "zaman_1s": "1 Saat",
        "zaman_4s": "4 Saat",
        "zaman_1g": "1 Gün"
    }
    context.user_data["zaman"] = zaman_map[query.data]

    await query.edit_message_text(
        f"✅ Zaman dilimi: *{context.user_data['zaman']}*\n\nŞimdi analiz istediğiniz pariteyi yazın:\n_(Örnek: BTC/USDT veya ETH/USDT)_",
        parse_mode="Markdown"
    )
    return PARITE_YAZ

async def parite_alindi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parite = update.message.text.upper()
    zaman = context.user_data.get("zaman", "Bilinmiyor")
    kullanici = update.message.from_user
    isim = kullanici.first_name
    if kullanici.last_name:
        isim += f" {kullanici.last_name}"
    username = f"@{kullanici.username}" if kullanici.username else "Kullanıcı adı yok"

    # Kullanıcıya onay mesajı
    keyboard = [
        [InlineKeyboardButton("📊 Yeni Analiz Talep Et", callback_data="analiz_baslat")]
    ]
    await update.message.reply_text(
        f"✅ *Talebiniz alındı!*\n\n💱 Parite: *{parite}*\n⏱ Zaman Dilimi: *{zaman}*\n\nAnalistlerimiz en kısa sürede analizi paylaşacak, lütfen bekleyiniz. 🙏",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Gruba talep mesajı
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=(
            f"📩 *YENİ ANALİZ TALEBİ*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 Talep Eden: *{isim}* ({username})\n"
            f"💱 Parite: *{parite}*\n"
            f"⏱ Zaman Dilimi: *{zaman}*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"✋ Analiz yapacak analist lütfen bu mesajı yanıtlayın!"
        ),
        parse_mode="Markdown"
    )

    return ConversationHandler.END

async def iptal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ İşlem iptal edildi.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(analiz_baslat, pattern="analiz_baslat")],
        states={
            ZAMAN_SEC: [CallbackQueryHandler(zaman_secildi, pattern="^zaman_")],
            PARITE_YAZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, parite_alindi)],
        },
        fallbacks=[CommandHandler("iptal", iptal)],
        per_chat=False
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
