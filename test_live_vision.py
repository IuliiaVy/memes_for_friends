import asyncio
import io
from PIL import Image, ImageDraw
import ai_service

def create_sample_image():
    # Create a simple red JPEG image with text
    img = Image.new('RGB', (200, 200), color='red')
    d = ImageDraw.Draw(img)
    d.text((10, 10), "Meme Test", fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()

async def test_live_ai_responses():
    print("🚀 Starting LIVE Groq API Vision Tests...")
    img_bytes = create_sample_image()
    
    # 1. Test roast_meme
    print("\n--- Testing roast_meme ---")
    roast = await ai_service.roast_meme(img_bytes)
    print("Roast Output:\n", roast)
    assert len(roast) > 0
    assert "<think>" not in roast
    assert "</think>" not in roast
    
    # 2. Test vibe_check
    print("\n--- Testing vibe_check ---")
    vibe = await ai_service.vibe_check(img_bytes)
    print("Vibe Output:\n", vibe)
    assert len(vibe) > 0
    assert "<think>" not in vibe
    
    # 3. Test praise_pet
    print("\n--- Testing praise_pet ---")
    pet = await ai_service.praise_pet(img_bytes)
    print("Pet Praise Output:\n", pet)
    assert len(pet) > 0
    assert "<think>" not in pet
    
    # 4. Test is_political
    print("\n--- Testing is_political ---")
    is_pol = await ai_service.is_political(img_bytes)
    print("Is Political Output:\n", is_pol)
    assert isinstance(is_pol, bool)
    
    print("\n✅ LIVE VISION TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    asyncio.run(test_live_ai_responses())
