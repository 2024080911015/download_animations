import requests
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import asyncio
import time
import aiofiles
import aiohttp
import os  # 引入os库来处理路径

async def get_bilibili_cookies():
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=False)
        content=await browser.new_context()
        page = await content.new_page()
        await page.goto("https://bilibili.com/")
        input()
        cookies=await content.storage_state(path="bilibili_cookies.json")
        await browser.close()
async def mai8n():
    await get_bilibili_cookies()
if __name__ == '__main__':
    asyncio.run(mai8n())