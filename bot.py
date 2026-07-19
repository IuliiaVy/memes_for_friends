import asyncio
import os
import re
import random
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BotCommand
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import config
from ai_service import is_political, explain_meme, roast_meme, vibe_check

if not config.BOT_TOKEN:
    print("No BOT_TOKEN. Exiting.")
    exit(1)

# Initialize bot with default parse mode
bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Regex for bad cat name
BAD_CAT_NAME_PATTERN = re.compile(r'\b(пиздюк|пездюк|пестдюк|писдюк)[а-я]*\b', re.IGNORECASE)

SHERIFF_PHRASES = [
    "Мой револьвер всегда заряжен, сынок. 🤠",
    "В этом городе закон — это я. 🎖️",
    "Держи руки на виду. Я слежу за тобой. 👀",
    "Тут не место для таких шуточек. 🌵",
    "Тише едешь — дольше живешь, партнер. 🐎",
    "Я пью кофе черным, а правосудие подаю холодным. ☕",
    "Еще одно слово, и ты проведешь ночь в камере. 🚔",
    "Проходи мимо, если не ищешь неприятностей. 🛑"
]

WELCOME_TEXT = (
    "Я смотрю, вы тут совсем от рук отбились. Спрячьте свои пушки и выньте руки из карманов. "
    "Я ваш новый шериф, блюститель закона, и я пришел навести здесь порядок.\n\n"
    "В моем городе нет места политической грязи. Я вышвыриваю за дверь любые политические листовки.\n\n"
    "Вот мои правила:\n"
    "1️⃣ <b>Бригада (/brigada)</b> — Если какой-то умник притащил заезжую шутку или послание, смысл которого от вас ускользает, "
    "кидайте мне эту команду. Я соберу бригаду, вмиг растолкую тебе её смысл и переведу текст с любого чужеземного языка. "
    "Я человек бывалый, повидал немало и неплохо разбираюсь в таких делах.\n\n"
    "2️⃣ <b>Проверка вайба (/vibe_check)</b> — Если вам кажется, что от чьей-то картинки тянет гнильцой, или вы просто не доверяете незнакомцу, "
    "не несет ли он дурной дух в наш салун — дайте мне сигнал. Ответьте на это дело командой, и я проведу проверку вайба, просканирую всю ауру и вынесу свой вердикт.\n\n"
    "3️⃣ <b>Главная доска (/post_to_best)</b> — Но я умею ценить не только дисциплину. Если кто-то выдаст по-настоящему крутую шутку — сообщите мне. "
    "Я лично заберу этот шедевр и вывешу на главную доску, чтобы каждая живая душа могла им полюбоваться.\n\n"
    "А еще я иногда спонтанно прожариваю случайные мемы. Ничего личного. 🪓"
)

async def download_image(message: Message) -> bytes:
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.sticker:
        file_id = message.sticker.file_id
    else:
        raise ValueError("Unsupported media type")
    
    file = await bot.get_file(file_id)
    result = await bot.download_file(file.file_path)
    return result.read()

# ================= КОМАНДЫ (COMMANDS) =================

@dp.message(Command("start", "help"))
async def cmd_start_help(message: Message):
    """
    Приветственное сообщение и справка по боту.
    """
    await message.reply(WELCOME_TEXT)

@dp.message(Command("brigada"))
async def cmd_brigada(message: Message):
    if not message.reply_to_message or not (message.reply_to_message.photo or message.reply_to_message.sticker):
        await message.reply("Ответьте этой командой на сообщение с картинкой или стикером.")
        return
    
    processing_msg = await message.reply("Вызываю пояснительную бригаду ИИ...")
    try:
        image_bytes = await download_image(message.reply_to_message)
        explanation = await explain_meme(image_bytes)
        await processing_msg.edit_text(explanation)
    except Exception as e:
        await processing_msg.edit_text("Произошла ошибка при анализе мема.")

@dp.message(Command("vibe_check"))
async def cmd_vibe_check(message: Message):
    """
    Развлекательная функция: проверка вайба мема
    """
    if not message.reply_to_message or not (message.reply_to_message.photo or message.reply_to_message.sticker):
        await message.reply("Ответьте этой командой на сообщение с картинкой или стикером.")
        return
    
    processing_msg = await message.reply("Сканирую ауру мема...")
    try:
        image_bytes = await download_image(message.reply_to_message)
        vibe = await vibe_check(image_bytes)
        await processing_msg.edit_text(vibe)
    except Exception as e:
        await processing_msg.edit_text("Не удалось просканировать вайб. Слишком много помех.")

@dp.message(Command("post_to_best"))
async def cmd_post_to_best(message: Message):
    """
    Сохранение любимого мема в публичный канал
    """
    if not message.reply_to_message or not (message.reply_to_message.photo or message.reply_to_message.sticker):
        await message.reply("Ответьте этой командой на мем или стикер, который хотите вывесить на главную доску.")
        return
    
    if not config.CHANNEL_ID:
        await message.reply("Канал для мемов еще не настроен администратором.")
        return
        
    processing_msg = await message.reply("Проверяю мем на легальность перед публикацией...")
    
    try:
        image_bytes = await download_image(message.reply_to_message)
        is_pol = await is_political(image_bytes)
        
        if is_pol:
            await processing_msg.edit_text("Отказано. Этот мем содержит политику, жесть или запрещенный контент. На главную доску такое не вешаем.")
            return
            
        await bot.copy_message(
            chat_id=config.CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_id=message.reply_to_message.message_id
        )
        await processing_msg.edit_text("Шедевр вывешен на главную доску! 📜")
    except Exception as e:
        print(f"Error copying to channel: {e}")
        await processing_msg.edit_text("Не удалось сохранить мем. Возможно, я не являюсь администратором в канале или формат не поддерживается.")

# ================= СОБЫТИЯ (EVENTS) =================

@dp.message(F.new_chat_members)
async def welcome_new_members(message: Message):
    """
    Приветствие при добавлении бота в новую группу.
    """
    bot_me = await bot.get_me()
    for member in message.new_chat_members:
        if member.id == bot_me.id:
            await message.answer(WELCOME_TEXT)
            break

# ================= ОБЩИЕ ФИЛЬТРЫ (TEXT/PHOTO) =================
# Эти фильтры должны идти в самом конце, иначе они перехватят команды!

@dp.message(F.photo | F.sticker)
async def handle_media(message: Message):
    # 1. Check text caption for bad cat name
    if message.caption and BAD_CAT_NAME_PATTERN.search(message.caption):
        await message.delete()
        await message.answer("Воздержитесь от подобных оскорблений. Кошку зовут Маркиза, проявляйте уважение. P.S. Сам пиздюк ⚡")
        return
        
    # Skip animated/video stickers for AI checks
    if message.sticker and (message.sticker.is_animated or message.sticker.is_video):
        return

    # Download image bytes
    try:
        image_bytes = await download_image(message)
    except Exception as e:
        print(f"Failed to download media: {e}")
        return
    
    # 2. Check for political content
    is_pol = await is_political(image_bytes)
    if is_pol:
        if config.ADMIN_CHAT_ID:
            try:
                # Отправляем поясняющее сообщение
                await bot.send_message(
                    chat_id=config.ADMIN_CHAT_ID,
                    text=f"🚨 Шериф конфисковал политический мем от @{message.from_user.username}. Вот что пытались пронести в город:"
                )
                # Пересылаем мем админу перед удалением
                await message.forward(chat_id=config.ADMIN_CHAT_ID)
            except Exception as e:
                print(f"Не удалось переслать мем админу: {e}")
        
        await message.delete()
        await message.answer(f"@{message.from_user.username}, мем конфискован. Оставим политику для новостей.")
        return

    # 3. Random meme roast (1 in 20 chance in group, ALWAYS in private)
    if message.chat.type == "private" or random.randint(1, 20) == 1:
        roast = await roast_meme(image_bytes)
        await message.reply(roast)

@dp.message(F.text)
async def handle_text(message: Message):
    if BAD_CAT_NAME_PATTERN.search(message.text):
        await message.delete()
        await message.answer("Воздержитесь от подобных оскорблений. Кошку зовут Маркиза, проявляйте уважение. P.S. Сам пиздюк ⚡")
        return
        
    if "@meme_sheriff_bot" in message.text:
        await message.reply(random.choice(SHERIFF_PHRASES))
        return
        
    if message.chat.type == "private":
        phrase = random.choice(SHERIFF_PHRASES)
        await message.reply(f"{phrase}\n\n*(Кстати, скинь мне мем — и я его прожарю! Команды: /help)*", parse_mode="Markdown")

# ================= ВЕБ-СЕРВЕР (ДЛЯ RENDER) =================

from aiohttp import web

async def handle_ping(request):
    """Простой ответ сервера, чтобы Render видел, что бот жив"""
    return web.Response(text="Meme Sheriff is patrolling! 🤠")

async def start_web_server():
    """Запускает фоновый веб-сервер на порту, который выдаст Render"""
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render передает нужный порт через переменную окружения PORT. По умолчанию 8080.
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

async def keep_alive():
    """Фоновая задача, которая пингует собственный веб-сервер каждые 10 минут, чтобы Render не усыплял бота."""
    url = "https://meme-sheriff-bot.onrender.com/"
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    print(f"Self-ping successful: {response.status}")
        except Exception as e:
            print(f"Self-ping failed: {e}")
        # Ждем 10 минут (600 секунд)
        await asyncio.sleep(600)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="brigada", description="Вызвать пояснительную бригаду для мема"),
        BotCommand(command="vibe_check", description="Проверить ауру (вайб) мема"),
        BotCommand(command="post_to_best", description="Отправить мем на главную доску"),
        BotCommand(command="help", description="Показать правила Шерифа")
    ]
    await bot.set_my_commands(commands)

async def main():
    print("Meme Police Bot started")
    # Регистрируем команды в меню Telegram
    await set_commands(bot)
    # Запускаем веб-сервер параллельно с поллингом телеграм-бота
    asyncio.create_task(start_web_server())
    # Запускаем пинг самого себя, чтобы Render не спал
    asyncio.create_task(keep_alive())
    
    # Игнорируем старые апдейты, чтобы избежать конфликтов (TelegramConflictError)
    # при перезагрузке серверов Render
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
