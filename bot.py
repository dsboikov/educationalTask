from typing import Callable, Dict, Any, Coroutine

from telegram import Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler,
                          MessageHandler, filters, ConversationHandler, CallbackContext, ExtBot)
from credentials import Keys
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu, default_callback_handler,
                  load_prompt, dialog_user_info_to_str, send_text_buttons, prepare_text_buttons,
                  send_text_with_prepared_buttons)
from mimetypes import MimeTypes
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename="logs/bot.log",
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    )



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['mode'] = "start"
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'helpwithresume': 'Помощь с резюме 📝',
        'picrecognition': 'Распознать фото 🖼️'
    })


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['mode'] = "random"
    await send_image(update, context, "random")
    answer = await chat_gpt.send_question(load_prompt("random"), '')
    await send_text_buttons(update, context, answer, {
        "start": "Закончить",
        "random_more": "⭐️ Ещё ⭐️",
    })


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['mode'] = "gpt"
    chat_gpt.set_prompt(load_prompt("gpt"))
    await send_image(update, context, "gpt")
    await send_text(update, context, load_message("gpt"))


async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    request = update.message.text
    buttons = await prepare_text_buttons({
        "start": "Закончить",
    })
    message = await send_text_with_prepared_buttons(update, context, 'Минуточку, я подумаю...', buttons)
    answer = await chat_gpt.send_question(load_prompt("gpt"), request)
    await message.edit_text(text=answer, reply_markup=buttons)


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['mode'] = "talk"
    await send_image(update, context, "talk")
    text = load_message("talk")
    await send_text_buttons(update, context, text, {
        "talk_cobain": "Курт Кобейн",
        "talk_queen": "Королева Елизавета II",
        "talk_tolkien": "Джон Рональд Руэл Толкиен",
        "talk_nietzsche": "Фридрих Ницше",
        "talk_hawking": "Стивен Хокинг"
    })


async def talk_button(update, context) -> None:
    query = update.callback_query.data
    await update.callback_query.answer()
    prompt = load_prompt(query)
    chat_gpt.set_prompt(prompt)
    greet = await chat_gpt.add_message("Поздоровайся и представься")
    await send_image(update, context, query)
    await send_text(update, context, greet)


async def talk_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    buttons = await prepare_text_buttons({
        "start": "Закончить",
        "change_talk": "Поговорить с другими",
    })
    text = update.message.text
    message = await send_text_with_prepared_buttons(update, context, 'Минуточку...', buttons)
    answer = await chat_gpt.add_message(text)
    await message.edit_text(text=answer, reply_markup=buttons)


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['mode'] = "quiz"
    context.user_data['score'] = 0
    chat_gpt.set_prompt(load_prompt("quiz"))
    return await quiz_theme(update, context)


async def quiz_theme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_text_buttons(update, context, load_message("quiz"), {
        'quiz_prog': 'Программирование',
        'quiz_math': 'Математика',
        'quiz_biology': 'Биология',
    })


async def quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Callable[
    [Update, Any], Coroutine[Any, Any, None]]:
    await update.callback_query.answer()
    question = await chat_gpt.add_message(update.callback_query.data)
    await send_text(update, context, question)
    return quiz_answer


async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answer = await chat_gpt.add_message(update.message.text)
    if answer == 'Правильно!':
        context.user_data['score'] = context.user_data.get('score', 0) + 1
    await send_text_buttons(update, context,
                            answer + '\n\nВаш счёт: ' + str(context.user_data['score']),
                            {
                                'quiz_more': 'Следующий вопрос',
                                'quiz_change': 'Сменить тему',
                                'start': 'завершить'
                            })


async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['mode'] = "resume"
    context.user_data['resume_dialog'] = {}
    context.user_data['resume_dialog_count'] = 0
    await send_image(update, context, "resume_profile")
    await send_text(update, context, load_message("resume_profile"))
    await send_text(update, context, "Введите название желаемой вакансии")


async def resume_dialog(update, context) -> None:
    text = update.message.text
    context.user_data['resume_dialog_count'] += 1

    if context.user_data['resume_dialog_count'] == 1:
        context.user_data['resume_dialog']["vacancy"] = text
        await send_text(update, context, "Введите ваши ФИО")
    elif context.user_data['resume_dialog_count'] == 2:
        context.user_data['resume_dialog']["fio"] = text
        await send_text(update, context, "Опыт работы: названия компаний, должности, обязанности")
    elif context.user_data['resume_dialog_count'] == 3:
        context.user_data['resume_dialog']["experience"] = text
        await send_text(update, context, "Какими навыками обладаете?")
    elif context.user_data['resume_dialog_count'] == 4:
        context.user_data['resume_dialog']["skills"] = text
        await send_text(update, context, "Добавьте информацию об образовании и квалификации")
    elif context.user_data['resume_dialog_count'] == 5:
        context.user_data['resume_dialog']["qualification"] = text
        prompt = load_prompt("resume_profile")
        user_info = dialog_user_info_to_str(context.user_data['resume_dialog'])
        my_message = await send_text(update, context,
                                     "ChatGPT занимается генерацией вашего резюме. Подождите пару секунд...")
        answer = await chat_gpt.send_question(prompt, user_info)
        buttons = await prepare_text_buttons({
            "start": "Закончить",
        })
        await my_message.edit_text(text=answer, reply_markup=buttons)


async def image_recognition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['mode'] = "image_recognition"
    await send_image(update, context, "image_recognition")
    await send_text(update, context, load_message("image_recognition"))


async def recognition_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        image_id = update.message.photo[-1].file_id if update.message.photo else \
            update.message.document.file_id if update.message.document else update.message.sticker.file_id
    except AttributeError:
        logging.error("Не удалось получить id изображения")
        logging.error(update.message)

    image_file_url = await context.bot.get_file(image_id)
    mime_type = mime.guess_type(image_file_url.file_path)[0]
    if 'image' not in mime_type:
        await send_text(update, context, "Неподдерживаемый тип файла")
        return
    buttons = await prepare_text_buttons({
        "start": "Закончить",
        "image_recognition": "⭐️ Ещё ⭐️",
    })
    message = await send_text_with_prepared_buttons(update, context, 'Минуточку, присмотрюсь...', buttons)
    answer = await chat_gpt.send_question_with_image(load_prompt("image_recognition"), image_file_url.file_path)
    await message.edit_text(text=answer, reply_markup=buttons)


async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    match context.user_data['mode']:
        case 'start':
            await start(update, context)
        case 'random':
            await random(update, context)
        case 'gpt':
            await gpt_dialog(update, context)
        case 'talk':
            await talk_dialog(update, context)
        case 'quiz':
            await quiz_answer(update, context)
        case 'resume':
            await resume_dialog(update, context)
        case "image_recognition":
            await recognition_result(update, context)


async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    query = update.callback_query.data
    if query in ('talk_cobain', 'talk_queen', 'talk_tolkien', 'talk_nietzsche', 'talk_hawking'):
        await talk_button(update, context)
    elif query in ('quiz_prog', 'quiz_math', 'quiz_biology', 'quiz_theme', 'quiz_more'):
        await quiz_question(update, context)
    else:
        match query:
            case 'start':
                await start(update, context)
            case 'random_more':
                await random(update, context)
            case 'change_talk':
                await talk(update, context)
            case "quiz_change":
                await quiz_theme(update, context)
            case "resume_dialog":
                await resume_dialog(update, context)
            case "image_recognition":
                await image_recognition(update, context)
            case _:
                await default_callback_handler(update, context)


ob_keys = Keys()
mime = MimeTypes()
commands_tuple = (
    ('start', start),
    ('random', random),
    ('gpt', gpt),
    ('talk', talk),
    ('quiz', quiz),
    ('helpwithresume', resume),
    ('picrecognition', image_recognition)
)

chat_gpt = ChatGptService(ob_keys.gpt_token)
app = ApplicationBuilder().token(ob_keys.bot_token).build()

for command, handler in commands_tuple:
    app.add_handler(CommandHandler(command, handler))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mode_handler))
app.add_handler(MessageHandler(filters.ATTACHMENT, mode_handler))

app.add_handler(CallbackQueryHandler(cb_handler))

app.run_polling()
