import os
from secrets import choice
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont

themes = ["rrc", "hejo", "black"]

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    ratio = min(widthRatio, heightRatio)
    newWidth = int(ratio * image.size[0])
    newHeight = int(ratio * image.size[1])
    return image.resize((newWidth, newHeight))


def create_circular_mask(h, w):
    center = (int(w / 2), int(h / 2))
    radius = min(center[0], center[1])
    mask = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, w, h), fill=255)
    return mask

async def gen_thumb(thumbnail, title, videoid, ctitle):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open(
                    f"resources/thumb_original_{videoid}.png", mode="wb"
                )
                await f.write(await resp.read())
                await f.close()

    FINAL_WIDTH = 1280
    FINAL_HEIGHT = 720
    CIRCLE_SIZE = 300 
    CIRCLE_CENTER_X = int(FINAL_WIDTH / 2)
    CIRCLE_CENTER_Y = int(FINAL_HEIGHT / 2)
    THUMB_X = CIRCLE_CENTER_X - int(CIRCLE_SIZE / 2)
    THUMB_Y = CIRCLE_CENTER_Y - int(CIRCLE_SIZE / 2)
    
    background_image = Image.open(f"resources/abstract_black_gold.png")
    background_image = background_image.resize((FINAL_WIDTH, FINAL_HEIGHT)).convert("RGBA")

    original_thumb = Image.open(f"resources/thumb_original_{videoid}.png")
    original_thumb = original_thumb.resize((CIRCLE_SIZE, CIRCLE_SIZE)) 

    mask = create_circular_mask(CIRCLE_SIZE, CIRCLE_SIZE)
    original_thumb.putalpha(mask)

    background_image.paste(original_thumb, (THUMB_X, THUMB_Y), original_thumb)
    
    background_image.save(f"resources/temp{videoid}.png")
    
    img = Image.open(f"resources/temp{videoid}.png")
    draw = ImageDraw.Draw(img)
    
    font = ImageFont.truetype("resources/Roboto-Light.ttf", 52)
    font2 = ImageFont.truetype("resources/Roboto-Medium.ttf", 76)
    
    draw.text((27, 538), f"Playing on {ctitle[:15]}...", (255, 255, 255), font=font) 
    draw.text((27, 612), f"{title[:20]}...", (255, 255, 255), font=font2)
    
    img.save(f"resources/final{videoid}.png")
    os.remove(f"resources/temp{videoid}.png")
    os.remove(f"resources/thumb_original_{videoid}.png")
    final = f"resources/final{videoid}.png"
    
    return final
  
