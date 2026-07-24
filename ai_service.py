import config
from groq import AsyncGroq
import base64
import re
import asyncio

if config.GROQ_API_KEY:
    client = AsyncGroq(api_key=config.GROQ_API_KEY)
else:
    client = None

def strip_think_tags(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

async def _generate_with_retry(image_bytes, prompt, temperature=0.7, max_tokens=300, max_retries=3, delay=2.0):
    """Обертка для вызова API с автоматическим повтором"""
    if not client:
        raise Exception("API ключ Groq не настроен.")

    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    image_url = f"data:image/jpeg;base64,{base64_image}"

    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(
                model="qwen/qwen3.6-27b",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            raw_text = response.choices[0].message.content
            return strip_think_tags(raw_text)
        except Exception as e:
            err_msg = str(e)
            if ("503" in err_msg or "429" in err_msg or "rate limit" in err_msg.lower()) and attempt < max_retries - 1:
                print(f"API busy (Attempt {attempt+1}/{max_retries}). Retrying in {delay}s...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
                continue
            raise e

async def is_political(image_bytes: bytes, mime_type: str = 'image/jpeg') -> bool:
    if not client: return False
    prompt = (
        "Ты - модератор дружеского чата. Твоя задача — блокировать настоящую политику и жесть, но пропускать безобидные мемы.\n\n"
        "ОТВЕЧАЙ 'ДА' (заблокировать), если видишь:\n"
        "1. Современных политиков (Путин, Байден, Зеленский, Трамп и т.д.).\n"
        "2. Настоящие политические призывы, агитацию, обсуждение реальных выборов и митингов.\n"
        "3. Отсылки к реальным современным войнам и военным конфликтам.\n\n"
        "ОТВЕЧАЙ 'НЕТ' (пропустить), если это:\n"
        "1. Случайные флаги на фоне (например, флаг на номере автомобиля, нашивка на одежде, эмодзи).\n"
        "2. Упоминание законов в бытовом смысле (штраф за скорость, лишение прав, законы физики).\n"
        "3. Исторические личности (Наполеон, Юлий Цезарь).\n"
        "4. Кадры из видеоигр, кино, аниме или вымышленные битвы (Звездные Войны), НО ТОЛЬКО ЕСЛИ в них нет политического подтекста.\n\n"
        "ВАЖНОЕ ПРАВИЛО (ПРИОРИТЕТ): Если мем использует безобидный кадр из игры, мультика или фильма как шаблон, но текст на картинке или ее явный подтекст отсылает к актуальной политической ситуации, современным войнам или политикам — такой мем нужно заблокировать (отвечай ДА).\n\n"
        "Ответь строго одним словом: ДА или НЕТ."
    )
    try:
        text = await _generate_with_retry(
            image_bytes=image_bytes,
            prompt=prompt,
            temperature=0.0,
            max_tokens=10
        )
        text = text.strip().lower()
        return 'да' in text or 'yes' in text
    except Exception as e:
        print(f"Error checking political content: {e}")
        return False

async def explain_meme(image_bytes: bytes, mime_type: str = 'image/jpeg') -> str:
    if not client: return "API ключ Groq не настроен."
    prompt = (
        "Объясни смысл этого мема. Если на картинке есть текст на английском или другом языке - обязательно переведи его на русский. Объясни юмор коротко и смешно. "
        "ВАЖНО: Твоя персона — это суровый шериф Дикого Запада, который на самом деле ворчливый добряк. Ты ругаешься на глупые мемы, но в глубине души очень любишь жителей своего города. "
        "Если мем откровенно оскорбительный или содержит жесть, не отказывайся отвечать, но обязательно начни свой ответ с ворчания (например: 'Даже мой револьвер покраснел от такой грязи, но если хотите знать, оболтусы...')."
    )
    try:
        text = await _generate_with_retry(
            image_bytes=image_bytes,
            prompt=prompt,
            temperature=0.7,
            max_tokens=500
        )
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        return text
    except Exception as e:
        print(f"Error explaining meme: {e}")
        return "Не удалось объяснить мем. Мои нейроны запутались."

async def roast_meme(image_bytes: bytes, mime_type: str = 'image/jpeg') -> str:
    if not client: return "Я бы прожарил этот мем, но у меня нет API ключа."
    prompt = "Подшути над этим мемом. Твоя персона — это суровый шериф Дикого Запада, который на самом деле ворчливый добряк. Ты ворчишь на жителей, но любишь их. Используй легкий сарказм, ковбойский сленг и иронию, но БЕЗ грубости, токсичности или реальных оскорблений. Максимум 2 предложения. Должно быть смешно и по-отечески тепло."
    try:
        text = await _generate_with_retry(
            image_bytes=image_bytes,
            prompt=prompt,
            temperature=0.9,
            max_tokens=300
        )
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
        "ВАЖНО: Твоя персона — суровый шериф Дикого Запада, ворчливый добряк, который любит своих жителей, хоть и постоянно на них ругается. "
        "Если мем грязный, отрази это в названии вайба и добавь по-отечески ворчливый комментарий."
    )
    try:
        text = await _generate_with_retry(
            image_bytes=image_bytes,
            prompt=prompt,
            temperature=0.8,
            max_tokens=300
        )
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        return text
    except Exception as e:
        print(f"Error checking vibe: {e}")
        return "Не могу проверить вайб. Мои нейроны не настроились на эту волну."
