import os
import asyncio
import uuid
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp
from keep_alive import keep_alive

bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()

url_cache = {}


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Hello! Send me a link from YouTube, TikTok, Instagram, OK.ru, X.com, or Pinterest, and I'll download it for you."
    )


@dp.message()
async def download_video(message: types.Message):
    url = message.text.strip()
    
    if not url.startswith(('http://', 'https://')):
        await message.answer("❌ Invalid link")
        return
    
    supported_platforms = [
        'youtube.com', 'youtu.be', 'tiktok.com', 'instagram.com',
        'ok.ru', 'x.com', 'twitter.com', 'pinterest.com'
    ]
    
    if not any(platform in url.lower() for platform in supported_platforms):
        await message.answer("❌ Invalid link")
        return
    
    is_youtube = 'youtube.com' in url.lower() or 'youtu.be' in url.lower()
    
    if is_youtube:
        url_id = str(uuid.uuid4())[:8]
        url_cache[url_id] = url
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎬 HD 1080p", callback_data=f"q:1080:{url_id}"),
                InlineKeyboardButton(text="📺 HD 720p", callback_data=f"q:720:{url_id}")
            ],
            [
                InlineKeyboardButton(text="📱 SD 480p", callback_data=f"q:480:{url_id}"),
                InlineKeyboardButton(text="⚡ Low 360p", callback_data=f"q:360:{url_id}")
            ],
            [
                InlineKeyboardButton(text="✨ Best Quality", callback_data=f"q:best:{url_id}")
            ]
        ])
        await message.answer("🎥 Select video quality:", reply_markup=keyboard)
    else:
        await process_download(message, url, "best")


async def process_download(message: types.Message, url: str, quality: str):
    status_msg = await message.answer("⏳ Downloading video...")
    downloaded_file = None
    
    try:
        if quality == "best":
            format_string = 'best[ext=mp4]/best'
        else:
            format_string = f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best[height<={quality}]'
        
        ydl_opts = {
            'format': format_string,
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            video_id = info['id']
            ext = info.get('ext', 'mp4')
            downloaded_file = f"{video_id}.{ext}"
        
        if downloaded_file and os.path.exists(downloaded_file):
            await status_msg.edit_text("⬆️ Uploading video...")
            
            video_file = FSInputFile(downloaded_file)
            await message.answer_video(video_file)
            
            os.remove(downloaded_file)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Download failed")
    
    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit_text("❌ Invalid link")
        
        if downloaded_file and os.path.exists(downloaded_file):
            try:
                os.remove(downloaded_file)
            except:
                pass


@dp.callback_query(F.data.startswith("q:"))
async def quality_callback(callback: CallbackQuery):
    await callback.answer()
    
    data_parts = callback.data.split(":", 2)
    quality = data_parts[1]
    url_id = data_parts[2]
    
    url = url_cache.get(url_id)
    if not url:
        await callback.message.edit_text("❌ Link expired. Please send the link again.")
        return
    
    quality_text = quality if quality == "best" else f"{quality}p"
    await callback.message.edit_text(f"✅ Selected: {quality_text} quality")
    
    await process_download(callback.message, url, quality)
    
    if url_id in url_cache:
        del url_cache[url_id]


async def main():
    keep_alive()
    
    await asyncio.sleep(1)
    
    print("Bot started successfully!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
