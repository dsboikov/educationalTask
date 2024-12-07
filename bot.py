from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, MessageHandler, filters
from credentials import Keys
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu, default_callback_handler,
                  load_prompt, dialog_user_info_to_str, send_text_buttons, Dialog, prepare_text_buttons,
                  send_text_with_prepared_buttons)


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


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "gpt"
    chat_gpt.set_prompt(load_prompt("gpt"))
    await send_image(update, context, "gpt")
    await send_text(update, context, load_message("gpt"))


async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.message.text
    buttons = await prepare_text_buttons({
        "start": "Закончить",
    })
    message = await send_text_with_prepared_buttons(update, context, 'Минуточку, я подумаю...', buttons)
    answer = await chat_gpt.send_question(load_prompt("gpt"), request)
    await message.edit_text(text=answer, reply_markup=buttons)


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dialog.mode = "talk"
    await send_image(update, context, "talk")
    text = load_message("talk")
    await send_text_buttons(update, context, text, {
        "talk_cobain": "Курт Кобейн",
        "talk_queen": "Королева Елизавета II",
        "talk_tolkien": "Джон Рональд Руэл Толкиен",
        "talk_nietzsche": "Фридрих Ницше",
        "talk_hawking": "Стивен Хокинг"
    })


async def talk_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    prompt = load_prompt(query)
    chat_gpt.set_prompt(prompt)
    greet = await chat_gpt.add_message("Поздоровайся и представься")
    await send_image(update, context, query)
    await send_text(update, context, greet)


async def talk_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = await prepare_text_buttons({
        "start": "Закончить",
        "change_talk": "Поговорить с другими",
    })
    text = update.message.text
    message = await send_text_with_prepared_buttons(update, context, 'Минуточку...', buttons)
    answer = await chat_gpt.add_message(text)
    await message.edit_text(text=answer, reply_markup=buttons)



async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    match dialog.mode:
        case 'start':
            await start(update, context)
        case 'random':
            await random(update, context)
        case 'gpt':
            await gpt_dialog(update, context)
        case 'talk':
            await talk_dialog(update, context)


async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    query = update.callback_query.data
    match query:
        case 'start':
            await start(update, context)
        case 'random_more':
            await random(update, context)
        case 'change_talk':
            await talk(update, context)
        case "talk_cobain":
            await talk_button(update, context)
        case "talk_queen":
            await talk_button(update, context)
        case "talk_tolkien":
            await talk_button(update, context)
        case "talk_nietzsche":
            await talk_button(update, context)
        case "talk_hawking":
            await talk_button(update, context)
        case _:
            await default_callback_handler(update, context)


ob_keys = Keys()
dialog = Dialog()
commands_tuple = (
    ('start', start),
    ('random', random),
    ('gpt', gpt),
    ('talk', talk),
)

chat_gpt = ChatGptService(ob_keys.gpt_token)
app = ApplicationBuilder().token(ob_keys.bot_token).build()

for command, handler in commands_tuple:
    app.add_handler(CommandHandler(command, handler))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mode_handler))
app.add_handler(MessageHandler(filters.ATTACHMENT, mode_handler))

app.add_handler(CallbackQueryHandler(cb_handler))

app.run_polling()
