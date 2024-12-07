from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, MessageHandler, filters
from credentials import Keys
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu, default_callback_handler,
                  load_prompt, dialog_user_info_to_str, send_text_buttons, Dialog)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "start"
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'help_with_resume': 'Помощь с резюме 📝',
        'pic_recognition': 'Распознать фото 🖼️',
        'translate': 'Переводчик 🔀'
    })


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "random"
    await send_image(update, context, "random")
    answer = await chat_gpt.send_question(load_prompt("random"), '')
    await send_text_buttons(update, context, answer, {
        "start": "Закончить",
        "random_more": "⭐️ Ещё ⭐️",
    })


async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    match dialog.mode:
        case 'start':
            await start(update, context)
        case 'random':
            await random(update, context)


async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    query = update.callback_query.data
    match query:
        case 'start':
            await start(update, context)
        case 'random_more':
            await random(update, context)
        case _:
            await default_callback_handler(update, context)


ob_keys = Keys()
dialog = Dialog()
commands_tuple = (
    ('start', start),
    ('random', random),
)

chat_gpt = ChatGptService(ob_keys.gpt_token)
app = ApplicationBuilder().token(ob_keys.bot_token).build()

for command, handler in commands_tuple:
    app.add_handler(CommandHandler(command, handler))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mode_handler))
app.add_handler(MessageHandler(filters.ATTACHMENT, mode_handler))

app.add_handler(CallbackQueryHandler(cb_handler))

app.run_polling()
