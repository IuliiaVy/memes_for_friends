import asyncio
import io
from PIL import Image, ImageDraw
import ai_service

def create_us_politics_image():
    # Large readable text
    img = Image.new('RGB', (600, 300), color='white')
    d = ImageDraw.Draw(img)
    # Simple large block text
    d.rectangle([10, 10, 590, 290], outline='black', width=3)
    d.text((30, 40), "US PRESIDENT ELECTION 2026", fill=(0, 0, 0))
    d.text((30, 100), "HOMER SIMPSON BLM DEMOCRATS", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()

def create_ru_politics_image():
    img = Image.new('RGB', (600, 300), color='white')
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, 590, 290], outline='black', width=3)
    d.text((30, 40), "ПРЕЗИДЕНТ РОССИИ ПУТИН ВЛАДИМИР", fill=(0, 0, 0))
    d.text((30, 100), "НОВОСТИ ПРАВИТЕЛЬСТВА РФ И СВО", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()

async def test_russia_only_filter():
    print("🚀 Testing Russia-only political filter...")
    
    us_img = create_us_politics_image()
    is_pol_us = await ai_service.is_political(us_img)
    print(f"US Politics Meme Result (Expected False): {is_pol_us}")
    assert is_pol_us == False, f"Expected False for US politics, got {is_pol_us}"
    
    ru_img = create_ru_politics_image()
    is_pol_ru = await ai_service.is_political(ru_img)
    print(f"RU Politics Meme Result (Expected True): {is_pol_ru}")
    assert is_pol_ru == True, f"Expected True for RU politics, got {is_pol_ru}"
    
    print("✅ RUSSIA-ONLY POLITICAL FILTER TEST PASSED PERFECTLY!")

if __name__ == "__main__":
    asyncio.run(test_russia_only_filter())
