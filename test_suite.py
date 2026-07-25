import asyncio
import os
import aiosqlite
import datetime
import html
import re

# Import functions from ai_service and db
from ai_service import strip_think_tags, format_telegram_html
import db

def test_think_tag_stripping():
    print("Testing strip_think_tags...")
    # Case 1: Closed think tag
    t1 = "<think>Some English reasoning here</think>\nПривет, партнер!"
    res1 = strip_think_tags(t1)
    assert res1 == "Привет, партнер!", f"Expected 'Привет, партнер!', got '{res1}'"
    
    # Case 2: Unclosed think tag (token limit hit)
    t2 = "<think>Unclosed reasoning in English..."
    res2 = strip_think_tags(t2)
    assert res2 == "", f"Expected empty string, got '{res2}'"
    
    # Case 3: No think tag
    t3 = "Просто ковбойский юмор"
    res3 = strip_think_tags(t3)
    assert res3 == "Просто ковбойский юмор", f"Expected 'Просто ковбойский юмор', got '{res3}'"
    print("✅ strip_think_tags tests passed!")

def test_html_formatting():
    print("Testing format_telegram_html...")
    inp = "Формула 5 < 10 & 2 > 1 **жирный текст**"
    res = format_telegram_html(inp)
    expected = "Формула 5 &lt; 10 &amp; 2 &gt; 1 <b>жирный текст</b>"
    assert res == expected, f"Expected '{expected}', got '{res}'"
    print("✅ format_telegram_html tests passed!")

async def test_db_separate_limits():
    print("Testing db separate action limits...")
    # Backup DB_NAME
    original_db = db.DB_NAME
    db.DB_NAME = 'test_sheriff.db'
    if os.path.exists('test_sheriff.db'):
        os.remove('test_sheriff.db')
        
    try:
        await db.init_db()
        user_id = 99999
        
        user = await db.get_or_create_user(user_id)
        assert user['free_roasts_used'] == 0
        assert user['free_brigada_used'] == 0
        assert user['free_vibe_used'] == 0
        
        # Increment roasts
        await db.use_free_action(user_id, 'roast')
        user = await db.get_or_create_user(user_id)
        assert user['free_roasts_used'] == 1
        assert user['free_brigada_used'] == 0
        assert user['free_vibe_used'] == 0
        
        # Increment brigada
        await db.use_free_action(user_id, 'brigada')
        user = await db.get_or_create_user(user_id)
        assert user['free_roasts_used'] == 1
        assert user['free_brigada_used'] == 1
        assert user['free_vibe_used'] == 0
        
        # Increment vibe
        await db.use_free_action(user_id, 'vibe')
        user = await db.get_or_create_user(user_id)
        assert user['free_roasts_used'] == 1
        assert user['free_brigada_used'] == 1
        assert user['free_vibe_used'] == 1
        
        print("✅ DB separate limits tests passed!")
    finally:
        db.DB_NAME = original_db
        if os.path.exists('test_sheriff.db'):
            os.remove('test_sheriff.db')

async def main():
    test_think_tag_stripping()
    test_html_formatting()
    await test_db_separate_limits()
    print("\n🎉 ALL UNIT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
