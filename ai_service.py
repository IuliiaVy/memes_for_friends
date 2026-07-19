import config
from google import genai
from google.genai import types
import re

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

async def is_political(image_bytes: bytes, mime_type: str = 'image/jpeg') -> bool:
    if not client: return False
    prompt = (
        "Ты - строгий ИИ-модератор. Внимательно изучи каждый пиксель, даже если это мыльный скриншот или обрезанная картинка. "
        "Есть ли здесь любой политический подтекст, лица или фигуры политических деятелей (Путин, Байден и т.д.), "
        "отсылки к государственным органам, выборам, законам, войне, флагам или оппозиции? "
        "Ответь строго одним словом: ДА или НЕТ."
    )
    try:
        response = await client.aio.models.generate_content(
            model='gemini-3.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ],
            config=types.GenerateContentConfig(
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
    prompt = "Объясни смысл этого мема. Если на картинке есть текст на английском или другом языке - обязательно переведи его на русский. Объясни юмор коротко и смешно."
    try:
        response = await client.aio.models.generate_content(
            model='gemini-3.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ],
            config=types.GenerateContentConfig(
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
    prompt = "Напиши короткую, саркастичную, токсичную (но дружелюбную) рецензию на этот мем на русском языке. Максимум 2 предложения. Сделай вид, что ты элитарный критик мемов."
    try:
        response = await client.aio.models.generate_content(
            model='gemini-3.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ],
            config=types.GenerateContentConfig(
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
    prompt = "Проведи 'vibe check' (проверку вайба) этого мема или картинки. Выдай результат в формате:\nВайб: [короткое смешное название вайба]\nОписание: [почему от картинки такой вайб].\nПример: 'Вайб: Хаотично-депрессивный. Описание: Этот мем излучает энергию человека, который спит 3 часа в день.'"
    try:
        response = await client.aio.models.generate_content(
            model='gemini-3.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ],
            config=types.GenerateContentConfig(
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
