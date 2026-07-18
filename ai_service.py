import config
from google import genai
from google.genai import types

if config.GEMINI_API_KEY:
    client = genai.Client(api_key=config.GEMINI_API_KEY)
else:
    client = None

async def is_political(image_bytes: bytes, mime_type: str = 'image/jpeg') -> bool:
    if not client: return False
    prompt = "Ты - строгий ИИ-модератор. Проанализируй это изображение (и любой текст на нем). Есть ли здесь политический подтекст, изображения политических деятелей, отсылки к государственным органам, выборам, законам, войне или оппозиции? Ответь строго одним словом: ДА или НЕТ."
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ]
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
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ]
        )
        return response.text
    except Exception as e:
        print(f"Error explaining meme: {e}")
        return "Не удалось объяснить мем. Мои нейроны запутались."

async def roast_meme(image_bytes: bytes, mime_type: str = 'image/jpeg') -> str:
    if not client: return "Я бы прожарил этот мем, но у меня нет API ключа."
    prompt = "Напиши короткую, саркастичную, токсичную (но дружелюбную) рецензию на этот мем на русском языке. Максимум 2 предложения. Сделай вид, что ты элитарный критик мемов."
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ]
        )
        return response.text
    except Exception as e:
        print(f"Error roasting meme: {e}")
        return "Мем настолько плох, что у меня сломался процессор."

async def vibe_check(image_bytes: bytes, mime_type: str = 'image/jpeg') -> str:
    if not client: return "Я бы проверил вайб, но нет ключа."
    prompt = "Проведи 'vibe check' (проверку вайба) этого мема или картинки. Выдай результат в формате:\nВайб: [короткое смешное название вайба]\nОписание: [почему от картинки такой вайб].\nПример: 'Вайб: Хаотично-депрессивный. Описание: Этот мем излучает энергию человека, который спит 3 часа в день.'"
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ]
        )
        return response.text
    except Exception as e:
        print(f"Error checking vibe: {e}")
        return "Не могу проверить вайб. Мои нейроны не настроились на эту волну."
