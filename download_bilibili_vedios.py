import requests
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import asyncio
import time
import aiofiles
import aiohttp
import os  # 引入os库来处理路径

from urllib3.util import url


async def get_favorite_vedios(url:str):
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=False)
        content=await browser.new_context(storage_state="bilibili_cookies.json")
        page = await content.new_page()
        await page.goto(url,wait_until="networkidle")
        favorite_vedios=[]
        k=1
        while True:
            print("正在处理第"+str(k)+"页")
            for i in range(15):
                print("正在进行第"+str(i+1)+"次滚动")
                await page.keyboard.press("PageDown")
                await asyncio.sleep(1)
            first_link_locator = page.locator(".bili-video-card__title a")
            count = await first_link_locator.count()
            if count > 0:
                for i in range(count):
                    locator = first_link_locator.nth(i)
                    vedio_links =await locator.get_attribute("href")
                    favorite_vedios.append(vedio_links)
            new_button= page.get_by_text("下一页",exact=True)
            if await new_button.is_visible():
                await new_button.click()
                k=k+1
            else:
                break
    return favorite_vedios

async def download_bilibili_vedios(url:str):
    pass
async def main():
    url="https://space.bilibili.com/3546814376577843/favlist?fid=3427826043&ftype=create"
    vedios=await get_favorite_vedios(url)
    count=len(vedios)
    print(count)
if __name__ == "__main__":
    asyncio.run(main())




