import config
from google import genai
from google.genai import types
import re
import asyncio

if config.GEMINI_API_KEY:
    client = genai.Client(api_key=config.GEMINI_API_KEY)
else:
    client = None

# Настройки безопасности: отключаем фильтры цензуры, чтобы бот не "глотал" жесткие мемы
safety_settings = [
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
]

async def _generate_with_retry(contents, config_params, max_retries=3, delay=2.0):
    """Обертка для вызова API с автоматическим повтором при перегрузке серверов (503/429)"""
    for attempt in range(max_retries):
        try:
            response = await client.aio.models.generate_content(
                model='gemini-3.5-flash',
                contents=contents,
                config=config_params
            )
            return response
        except Exception as e:
            err_msg = str(e)
            if ("503" in err_msg or "UNAVAILABLE" in err_msg or "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg) and attempt < max_retries - 1:
                print(f"API busy (Attempt {attempt+1}/{max_retries}). Retrying in {delay}s...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
                continue
            raise e

async def is_political(image_bytes: bytes, mime_type: str = 'image/jpeg') -> bool:
    if not client: return False
    prompt = (
        "Ты - строгий ИИ-модератор. Внимательно изучи каждый пиксель, даже если это мыльный скриншот или обрезанная картинка. "
        "Есть ли здесь любой политический подтекст, лица или фигуры политических деятелей (Путин, Байден и т.д.), "
        "отсылки к государственным органам, выборам, законам, войне, флагам или оппозиции? "
        "Ответь строго одним словом: ДА или НЕТ."
    )
    try:
        response = await _generate_with_retry(
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ],
            config_params=types.GenerateContentConfig(
                temperature=0.0, # Нулевая креативность для строгой проверки
                safety_settings=safety_settings
            )
        )
        text = response.text.strip().lower()
        return 'да' in text or 'yes' in text
    except Exception as e:
        print(f"Error checking political content: {e}")
        return False

async def explain_meme(image_bytes: bytes, mime_type: str = 'image/jpeg') -> str:
    if not client: return "API ключ Gemini не настроен."
    prompt = (
        "Объясни смысл этого мема. Если на картинке есть текст на английском или другом языке - обязательно переведи его на русский. Объясни юмор коротко и смешно. "
        "ВАЖНО: Если мем откровенно оскорбительный, аморальный или содержит жесть, не отказывайся отвечать, но обязательно начни свой ответ с возмущения в стиле сурового шерифа Дикого Запада "
        "(например: 'Даже мой револьвер покраснел от такой грязи, но если хотите знать...')."
    )
    try:
        response = await _generate_with_retry(
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ],
            config_params=types.GenerateContentConfig(
                temperature=0.7,
                safety_settings=safety_settings
            )
        )
        text = response.text
        # Превращаем маркдаун-звездочки в HTML-жирность
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        return text
    except Exception as e:
        print(f"Error explaining meme: {e}")
        return "Не удалось объяснить мем. Мои нейроны запутались."

async def roast_meme(image_bytes: bytes, mime_type: str = 'image/jpeg') -> str:
    if not client: return "Я бы прожарил этот мем, но у меня нет API ключа."
    prompt = "Подшути над этим мемом в стиле сурового, слегка ворчливого шерифа Дикого Запада. Используй легкий сарказм, ковбойский сленг и иронию, но БЕЗ грубости, токсичности или реальных оскорблений. Максимум 2 предложения. Должно быть смешно, а не обидно."
    try:
        response = await _generate_with_retry(
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ],
            config_params=types.GenerateContentConfig(
                temperature=0.9,
                safety_settings=safety_settings
            )
        )
        text = response.text
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        return text
    except Exception as e:
        print(f"Error roasting meme: {e}")
        return "Мем настолько плох, что у меня сломался процессор."

async def vibe_check(image_bytes: bytes, mime_type: str = 'image/jpeg') -> str:
    if not client: return "Я бы проверил вайб, но нет ключа."
    prompt = (
        "Проведи 'vibe check' (проверку вайба) этого мема или картинки. Выдай результат в формате:\n"
        "Вайб: [короткое смешное название вайба]\n"
        "Описание: [почему от картинки такой вайб].\n"
        "Пример: 'Вайб: Хаотично-депрессивный. Описание: Этот мем излучает энергию человека, который спит 3 часа в день.'\n"
        "ВАЖНО: Если мем оскорбительный, токсичный или грязный, отрази это в названии вайба (например 'Вайб: Аморальный мусор') и добавь комментарий от лица сурового шерифа."
    )
    try:
        response = await _generate_with_retry(
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ],
            config_params=types.GenerateContentConfig(
                temperature=0.8,
                safety_settings=safety_settings
            )
        )
        text = response.text
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        return text
    except Exception as e:
        print(f"Error checking vibe: {e}")
        return "Не могу проверить вайб. Мои нейроны не настроились на эту волну."
