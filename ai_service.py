import config
from groq import AsyncGroq
import base64
import re
import asyncio
import html

if config.GROQ_API_KEY:
    client = AsyncGroq(api_key=config.GROQ_API_KEY)
else:
    client = None

def strip_think_tags(text):
    """Гарантированно отрезает внутренние рассуждения ИИ, даже если тег </think> не был закрыт"""
    if '</think>' in text:
        text = text.split('</think>')[-1]
    elif '<think>' in text:
        # Если тег <think> открыт, но не закрыт, всё после <think> — это недописанный черновик, отрезаем его полностью
        text = text.split('<think>')[0]
    return text.strip()

def format_telegram_html(text: str) -> str:
    """Безопасно экранирует спецсимволы HTML и форматирует **текст** в <b>текст</b>"""
    text = html.escape(text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text

async def _generate_with_retry(image_bytes, prompt, temperature=0.7, max_tokens=800, max_retries=3, delay=2.0):
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
        "Ты — модератор чата. Твоя задача — блокировать исключительно политику России (РФ).\n\n"
        "Отвечай 'ДА' (заблокировать), если картинка или её текст касается политики России (Путин, Кадыров, СВО, правительство РФ, чиновники РФ, новости РФ).\n\n"
        "Отвечай 'НЕТ' (пропустить) для всей зарубежной политики (США, Трамп, Байден, Симпсоны), бытового юмора и котиков.\n\n"
        "Рассуждай кратко. Ответь строго одним словом в конце: ДА или НЕТ."
    )
    try:
        text = await _generate_with_retry(
            image_bytes=image_bytes,
            prompt=prompt,
            temperature=0.0,
            max_tokens=600
        )
        text = text.strip().lower()
        return 'да' in text or 'yes' in text
    except Exception as e:
        print(f"Error checking political content: {e}")
        return False

async def explain_meme(image_bytes: bytes, mime_type: str = 'image/jpeg') -> str:
    if not client: return "API ключ Groq не настроен."
    prompt = (
        "Ты — суровый Шериф Дикого Запада, который на самом деле является ворчливым добряком и очень любит жителей своего города. "
        "Рассуждай кратко (до 10 слов в <think>). "
        "Объясни смысл этого мема коротко и понятными словами. Если на картинке есть текст на иностранном языке, переведи его на русский язык. "
        "Начни свой ответ с легкого ковбойского ворчания, за которым следует заботливое объяснение юмора. "
        "Пиши все свои мысли, рассуждения и итоговый текст исключительно на русском языке от начала и до конца."
    )
    try:
        text = await _generate_with_retry(
            image_bytes=image_bytes,
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )
        return format_telegram_html(text)
    except Exception as e:
        print(f"Error explaining meme: {e}")
        return "Не удалось объяснить мем. Мои нейроны запутались."

async def roast_meme(image_bytes: bytes, mime_type: str = 'image/jpeg') -> str:
    if not client: return "Я бы прожарил этот мем, но у меня нет API ключа."
    prompt = (
        "Ты — суровый Шериф Дикого Запада, ворчливый добряк. "
        "Рассуждай кратко (до 10 слов в <think>). "
        "Твой ответ — это короткая (ровно 1–2 предложения), по-отечески теплая и добродушная шутка. "
        "Выражай дружескую иронию исключительно к ситуации на картинке, поддерживая автора и сохраняя уютный ковбойский вайб. "
        "Пиши все свои мысли, рассуждения и итоговый текст исключительно на русском языке от начала и до конца."
    )
    try:
        text = await _generate_with_retry(
            image_bytes=image_bytes,
            prompt=prompt,
            temperature=0.9,
            max_tokens=1000
        )
        return format_telegram_html(text)
    except Exception as e:
        print(f"Error roasting meme: {e}")
        return "Мем настолько плох, что у меня сломался процессор."

async def vibe_check(image_bytes: bytes, mime_type: str = 'image/jpeg') -> str:
    if not client: return "Я бы проверил вайб, но нет ключа."
    prompt = (
        "Ты — суровый Шериф Дикого Запада, ворчливый добряк. "
        "Рассуждай кратко (до 10 слов в <think>). "
        "Проведи 'vibe check' (проверку вайба) этого мема. Выдай результат ровно в двух коротких строках:\n"
        "Вайб: [2-3 слова]\n"
        "Аура: [короткая фраза на 4-7 слов].\n"
        "Сохраняй образ ворчливого добряка-шерифа. "
        "Пиши все свои мысли, рассуждения и итоговый текст исключительно на русском языке от начала и до конца."
    )
    try:
        text = await _generate_with_retry(
            image_bytes=image_bytes,
            prompt=prompt,
            temperature=0.8,
            max_tokens=1000
        )
        return format_telegram_html(text)
    except Exception as e:
        print(f"Error checking vibe: {e}")
        return "Не могу проверить вайб. Мои нейроны не настроились на эту волну."

async def praise_pet(image_bytes: bytes, mime_type: str = 'image/jpeg') -> str:
    if not client: return "Какая замечательная тушка! 10/10 ковбойских шляп 🐱🤠"
    prompt = (
        "Ты — суровый Шериф Дикого Запада, который обожает котиков, собак и любых домашних питомцев. "
        "Рассуждай кратко (до 10 слов в <think>). "
        "Похвали питомца на фото теплой ковбойской фразой (1-2 предложения). Поставь оценку (например, 10/10 ковбойских шляп или 100/10 ворсинок). "
        "Пиши все свои мысли и итоговый текст исключительно на русском языке."
    )
    try:
        text = await _generate_with_retry(
            image_bytes=image_bytes,
            prompt=prompt,
            temperature=0.8,
            max_tokens=1000
        )
        return format_telegram_html(text)
    except Exception as e:
        print(f"Error praising pet: {e}")
        return "Какая замечательная пушистая тушка! 10/10 ковбойских шляп 🐱🤠"

