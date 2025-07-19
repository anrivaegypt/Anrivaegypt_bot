import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import pandas as pd

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Steps
(ASK_CHECKIN, ASK_CHECKOUT, ASK_ADULTS, ASK_CHILDREN, ASK_CHILD_AGES, ASK_RESORT) = range(6)

resorts = ["Sharm El Sheikh", "Hurghada", "Monastir, Tunisia", "Al Alamain"]

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Բարի գալուստ 🇪🇬 Anriva Egypt Bot։\n📅 Խնդրում եմ ուղարկեք մուտքի ամսաթիվը (օրինակ՝ 2024-10-10):")
    return ASK_CHECKIN

async def ask_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["checkin"] = update.message.text
    await update.message.reply_text("📅 Այժմ ուղարկեք ելքի ամսաթիվը (օրինակ՝ 2024-10-15):")
    return ASK_CHECKOUT

async def ask_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["checkout"] = update.message.text
    await update.message.reply_text("👤 Մեծահասակների քանակը:")
    return ASK_ADULTS

async def ask_adults(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["adults"] = int(update.message.text)
    await update.message.reply_text("👶 Երեխաների քանակը (եթե չկա՝ ուղարկեք 0):")
    return ASK_CHILDREN

async def ask_children(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["children"] = int(update.message.text)
    if user_data["children"] > 0:
        await update.message.reply_text("🎂 Երեխաների տարիքները՝ բաժանված ստորակետերով (օր․՝ 5,8):")
        return ASK_CHILD_AGES
    else:
        user_data["child_ages"] = []
        return await ask_resort(update, context)

async def ask_child_ages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ages = [int(a.strip()) for a in update.message.text.split(",") if a.strip().isdigit()]
    user_data["child_ages"] = ages
    return await ask_resort(update, context)

async def ask_resort(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[r] for r in resorts]
    await update.message.reply_text("🏝 Խնդրում եմ ընտրել հանգստավայրը:", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return ASK_RESORT

async def generate_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["resort"] = update.message.text

    hotels = [
        {"Hotel": "Hotel A", "Base Price ($)": 950},
        {"Hotel": "Hotel B", "Base Price ($)": 870},
        {"Hotel": "Hotel C", "Base Price ($)": 920},
    ]

    for h in hotels:
        h["Final Price ($)"] = round(h["Base Price ($)"] * 0.91 + 60, 2)

    df = pd.DataFrame(hotels)
    df = df.sort_values("Final Price ($)")
    file_path = "anriva_packages.xlsx"
    df.to_excel(file_path, index=False)

    await update.message.reply_document(document=open(file_path, "rb"))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Ընթացքը դադարեցված է։")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_CHECKIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_checkin)],
            ASK_CHECKOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_checkout)],
            ASK_ADULTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_adults)],
            ASK_CHILDREN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_children)],
            ASK_CHILD_AGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_child_ages)],
            ASK_RESORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_result)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
