import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

BOT_TOKEN = "8884383692:AAEZHl7GUQ3rwHoCnavuFeS99zbd8_1bDYo"
OWNER_CHAT_ID = 31667723

QUESTIONS = [
    "اولین چیزی که وقتی یاد من می‌کنی به ذهنت میاد چیه؟ 💭",
    "چه موضوع و مطلبی در مورد من از همه بیشتر صدق می‌کنه؟ 🌹",
    "چندتا نقطه ضعف من رو بگو",
    "یه چیزی که واقعاً دوست داری در مورد من بگی چیه؟",
    "قشنگ‌ترین حرفی که تا حالا بهت زدم چی بوده؟ 💬",
    "چه نقاط قوتی از من به ذهنت میرسه؟",
    "چیزی که رو دلت مونده و نگفتی چیه؟😅",
    "اگه بخوای من رو با یه رنگ توصیف کنی، چه رنگیه و چرا؟ 🎨",
    "یه خاطره که همیشه بخندونَدِت از من چیه؟ 😄",
    "آخرش... یه جمله دلی برام بنویس 💗",
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

(Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10) = range(10)
STEPS = [Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10]
answers = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    answers[user.id] = {}
    await update.message.reply_text(
        f"سلام {user.first_name} جان 💙\n\n"
        "چند تا سوال ازت دارم که می‌خوام دقیق جواب بدی.\n"
        "هر سوال رو می‌پرسم، تو با انصاف جواب بده.\n\n"
        "هر وقت خواستی متوقف کنی، بنویس /cancel\n"
        "اگه جواب یه سوال رو نداری، بنویس /skip\n\n"
        "بزن بریم! 🚀"
    )
    await update.message.reply_text(
        f"سوال ۱ از ۱۰:\n\n{QUESTIONS[0]}",
        reply_markup=ReplyKeyboardRemove()
    )
    return Q1


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    step = context.user_data.get("step", 0)
    text = update.message.text.strip()
    answers[user.id][step] = text
    next_step = step + 1
    if next_step < len(QUESTIONS):
        context.user_data["step"] = next_step
        await update.message.reply_text(
            f"سوال {next_step + 1} از {len(QUESTIONS)}:\n\n{QUESTIONS[next_step]}"
        )
        return STEPS[next_step]
    else:
        await send_to_owner(context, user)
        await update.message.reply_text(
            "ممنون عزیزم 💙\nجوابات رسید دستم."
        )
        answers.pop(user.id, None)
        context.user_data.clear()
        return ConversationHandler.END


async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    step = context.user_data.get("step", 0)
    answers[user.id][step] = "— (جواب نداد)"
    next_step = step + 1
    if next_step < len(QUESTIONS):
        context.user_data["step"] = next_step
        await update.message.reply_text(
            f"باشه، رد کن. 👌\n\nسوال {next_step + 1} از {len(QUESTIONS)}:\n\n{QUESTIONS[next_step]}"
        )
        return STEPS[next_step]
    else:
        await send_to_owner(context, user)
        await update.message.reply_text("ممنون عزیزم 💙\nجوابات رسید دستم.")
        answers.pop(user.id, None)
        context.user_data.clear()
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    answers.pop(user.id, None)
    context.user_data.clear()
    await update.message.reply_text("باشه عزیزم، هر وقت خواستی دوباره /start بزن 💙")
    return ConversationHandler.END


async def send_to_owner(context: ContextTypes.DEFAULT_TYPE, user):
    ans = answers.get(user.id, {})
    text = (
        f"💌 جوابای صادقانه از طرف {user.first_name}\n"
        f"🆔 آی‌دی: {user.id}\n"
        f"📛 یوزرنیم: @{user.username or 'نداره'}\n"
        f"{'─' * 30}\n\n"
    )
    for i, q in enumerate(QUESTIONS):
        a = ans.get(i, "—")
        text += f"{i+1}) {q}\n➤ {a}\n\n"
    try:
        await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=text)
    except Exception as e:
        logger.error(f"خطا: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            Q4: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            Q5: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            Q6: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            Q7: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            Q8: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            Q9: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            Q10: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("skip", skip),
        ],
    )
    app.add_handler(conv_handler)
    print("🤖 ربات روشن شد...")
    app.run_polling()


if __name__ == "__main__":
    main()
