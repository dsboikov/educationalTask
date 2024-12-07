from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, MessageHandler, filters
from credentials import Keys
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu, default_callback_handler,
                  load_prompt, dialog_user_info_to_str, send_text_buttons, Dialog)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        'pic_recognition': 'Распознать фото 🔀',
        'translate': 'Переводчик 🔀'
    })


async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    match filters.COMMAND:
        case 'start':
            await start(update, context)

ob_keys = Keys()
dialog = Dialog()
commands_tuple = (('start', start),)

chat_gpt = ChatGptService(ob_keys.gpt_token)
app = ApplicationBuilder().token(ob_keys.bot_token).build()
#app.add_handler(CommandHandler("start", start))
for command, handler in commands_tuple:
    app.add_handler(CommandHandler(command, handler))

# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))

# Зарегистрировать обработчик коллбэка можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
