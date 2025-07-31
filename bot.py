from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

# 📌 Conversation States
EXAM, SUBJECT, YEAR = range(3)

# 🧾 Required Channel
REQUIRED_CHANNEL = "dailytechlinks"

# 📚 Sample Data (Future me PDF or Website links yahan jod sakte ho)
data = {
    "SSC CGL": {
        "General Awareness": {
            "2022": "https://sscadda.com/ssc-cgl-2022-ga.pdf"
        },
        "Maths": {
            "2021": "https://sscadda.com/ssc-cgl-2021-maths.pdf"
        }
    },
    "UPSC Prelims": {
        "CSAT": {
            "2023": "https://visionias.in/upsc-csat-2023.pdf"
        },
        "GS Paper 1": {
            "2022": "https://upsc.gov.in/sites/default/files/Pre_2022_Paper_I.pdf"
        }
    },
    "Class 12": {
        "Biology": {
            "2022": "https://ncert.nic.in/textbook/pdf/kebo112.pdf"
        },
        "Maths": {
            "2022": "https://ncert.nic.in/textbook/pdf/kemy112.pdf"
        }
    }
}

# 🔍 Check channel membership
async def check_channel_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=f"@{REQUIRED_CHANNEL}", user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# 🔹 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await check_channel_membership(update, context):
        await update.message.reply_text(
            f"🚫 Please join our channel first:\n👉 https://t.me/{REQUIRED_CHANNEL}"
        )
        return ConversationHandler.END

    reply_keyboard = [[exam] for exam in data.keys()]
    await update.message.reply_text(
        "📚 Select your exam:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return EXAM

# 🔹 Exam selected
async def exam_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['exam'] = update.message.text
    subjects = data.get(context.user_data['exam'], {})
    reply_keyboard = [[subject] for subject in subjects.keys()]
    await update.message.reply_text(
        "🧪 Choose your subject:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SUBJECT

# 🔹 Subject selected
async def subject_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['subject'] = update.message.text
    years = data.get(context.user_data['exam'], {}).get(context.user_data['subject'], {})
    reply_keyboard = [[year] for year in years.keys()]
    await update.message.reply_text(
        "📅 Choose the year:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return YEAR

# 🔹 Year selected
async def year_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    exam = context.user_data['exam']
    subject = context.user_data['subject']
    year = update.message.text

    pdf_link = data.get(exam, {}).get(subject, {}).get(year)
    if pdf_link:
        await update.message.reply_text(f"✅ Here is your PDF:\n{pdf_link}")
    else:
        await update.message.reply_text("❌ PDF not found.")
    return ConversationHandler.END

# 🔹 /cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Process cancelled.")
    return ConversationHandler.END

# 🔧 Bot setup
app = ApplicationBuilder().token("8450532503:AAEUNEuibjV8RQgLc20Zeee2nIS2IR5f5dI").build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        EXAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, exam_chosen)],
        SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, subject_chosen)],
        YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, year_chosen)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)
app.run_polling()