import os
import re
import textwrap
import random
import aiofiles
import aiohttp
import asyncio
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageChops
from youtubesearchpython.__future__ import VideosSearch

MUSIC_BOT_NAME = "Xteam Music"
YOUTUBE_IMG_URL = "https://telegra.ph/file/95d96663b73dbf278f28c.jpg"

# --- PERBAIKAN 1: Pastikan Folder Cache & Thumbnail Ada ---
if not os.path.exists("cache"):
    os.makedirs("cache")
if not os.path.exists("thumbnail"):
    os.makedirs("thumbnail")

files = [] 
for filename in os.listdir("./thumbnail"): 
    if filename.endswith("png"): 
        files.append(filename[:-4])

# --- PERBAIKAN 2: Penanganan Jika Folder Thumbnail Kosong ---
if not files:
    # Jika kosong, tambahkan satu nama default agar random.choice tidak error
    files = ["default"]

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def add_corners(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
    # PERBAIKAN 3: Image.ANTIALIAS diganti ke Image.LANCZOS (Untuk Pillow terbaru)
    mask = mask.resize(im.size, Image.LANCZOS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)

async def gen_thumb(videoid):
    anime = random.choice(files)
    if os.path.isfile(f"cache/{videoid}_{anime}.png"):
        return f"cache/{videoid}_{anime}.png"
    
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        res = await results.next()
        if res["result"]:
            result = res["result"][0]
            title = re.sub("\W+", " ", result["title"]).title()
            duration = result.get("duration", "Unknown")
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        else:
            return YOUTUBE_IMG_URL

        # --- PERBAIKAN 4: Pastikan File Benar-benar Terunduh ---
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    async with aiofiles.open(f"cache/thumb{videoid}.png", mode="wb") as f:
                        await f.write(content)

        # Cek apakah file benar-benar ada sebelum dibuka PIL
        if not os.path.exists(f"cache/thumb{videoid}.png"):
             return YOUTUBE_IMG_URL

        youtube = Image.open(f"cache/thumb{videoid}.png")
        
        # Cek background, jika tidak ada pakai gambar kosong (blank)
        bg_path = f"thumbnail/{anime}.png"
        if os.path.exists(bg_path):
            bg = Image.open(bg_path)
        else:
            bg = Image.new('RGBA', (1280, 720), (0, 0, 0, 255))

        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(30))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)
        
        # Lingkaran overlay
        cir_path = "thumbnail/IMG_20221129_201846_195.png"
        if os.path.exists(cir_path):
            cir = Image.open(cir_path)
            circle = changeImageSize(1280, 720, cir)
        else:
            circle = Image.new('RGBA', (1280, 720), (255, 255, 255, 0))

        image3 = changeImageSize(1280, 720, bg)
        image5 = image3.convert("RGBA")
        Image.alpha_composite(background, image5).save(f"cache/temp{videoid}.png")

        Xcenter = youtube.width / 2
        Ycenter = youtube.height / 2
        x1 = Xcenter - 250
        y1 = Ycenter - 250
        x2 = Xcenter + 250
        y2 = Ycenter + 250
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((520, 520), Image.LANCZOS) # Ganti ANTIALIAS
        logo.save(f"cache/chop{videoid}.png")
        
        if not os.path.isfile(f"cache/cropped{videoid}.png"):
            im = Image.open(f"cache/chop{videoid}.png").convert('RGBA')
            add_corners(im)
            im.save(f"cache/cropped{videoid}.png")

        crop_img = Image.open(f"cache/cropped{videoid}.png")
        logo = crop_img.convert("RGBA")
        logo.thumbnail((365, 365), Image.LANCZOS) # Ganti ANTIALIAS
        width = int((1280 - 365)/ 2)
        background = Image.open(f"cache/temp{videoid}.png")
        background.paste(logo, (width + 2, 134), mask=logo)
        background.paste(circle, mask=circle)
        
        draw = ImageDraw.Draw(background)
        # --- PERBAIKAN 5: Penanganan Font ---
        # Pastikan file font ada, atau gunakan default
        def get_font(path, size):
            return ImageFont.truetype(path, size) if os.path.exists(path) else ImageFont.load_default()

        font = get_font("thumbnail/font2.ttf", 45)
        arial = get_font("thumbnail/font2.ttf", 30)

        para = textwrap.wrap(title, width=32)
        try:
            # PERBAIKAN 6: Menggunakan textbbox (Untuk Pillow terbaru)
            if para[0]:
                left, top, right, bottom = draw.textbbox((0, 0), para[0], font=font)
                draw.text(((1280 - (right - left))/2, 530), para[0], fill="white", stroke_width=1, stroke_fill="white", font=font)
            if len(para) > 1:
                left, top, right, bottom = draw.textbbox((0, 0), para[1], font=font)
                draw.text(((1280 - (right - left))/2, 580), para[1], fill="white", stroke_width=1, stroke_fill="white", font=font)
        except:
            pass

        duration_text = f"Duration: {duration} Mins"
        left, top, right, bottom = draw.textbbox((0, 0), duration_text, font=arial)
        draw.text(((1280 - (right - left))/2, 660), duration_text, fill="white", font=arial)

        # Bersihkan file sampah
        for temp in [f"cache/thumb{videoid}.png", f"cache/temp{videoid}.png", f"cache/chop{videoid}.png", f"cache/cropped{videoid}.png"]:
            if os.path.exists(temp):
                os.remove(temp)

        final_path = f"cache/{videoid}_{anime}.png"
        background.save(final_path)
        return final_path
    except Exception as e:
        print(f"Error gen_thumb: {e}")
        return YOUTUBE_IMG_URL
         
