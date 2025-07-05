import requests
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import asyncio
import time
import aiofiles
import aiohttp
import os  # 引入os库来处理路径

async def get_first_links(url):
    async with Stealth().use_async(async_playwright()) as p:
        browser=await p.chromium.launch(headless=True)
        content=await browser.new_context()
        page=await content.new_page()
        await page.goto(url,timeout=6000,wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle")
        first_links=[]
        first_links_locator=page.locator(".d-player-list a")
        count=await first_links_locator.count()
        if count>0:
            for i in range(count):
                locator=first_links_locator.nth(i)
                links=await locator.get_attribute("href")
                links="https://www.manhuazhan.com"+links
                first_links.append(links)
            return first_links
        else:
            print("No links found")
async def download_page(url: str):
    # --- 调试信息 ---
    print("🚀 [1/7] 'download_page' 函数开始执行...")
    async  with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=True)  # 改为True在后台运行，通常更快
        # --- 调试信息 ---
        print("✅ [2/7] 浏览器已启动。")

        # 检查cookies文件是否存在
        if os.path.exists("cookies.json"):
            content = await browser.new_context(storage_state="cookies.json")
            print("ℹ️ 已加载 cookies.json 文件。")
        else:
            content = await browser.new_context()
            print("⚠️ 未找到 cookies.json 文件，将以未登录状态运行。")

        page = await content.new_page()

        # --- 调试信息 ---
        print(f"➡️ [3/7] 正在导航到页面: {url} ...")
        await page.goto(url=url, timeout=60000)  # 增加了超时时间
        print("✅ 页面导航初步完成。")

        # --- 调试信息 ---
        print("⏳ [4/7] 正在等待网络活动空闲...")
        await page.wait_for_load_state("networkidle")
        print("✅ 网络已空闲。")

        last_height = await page.evaluate("document.body.scrollHeight")

        button_locator = page.locator(".ViewAll-QuestionMainAction").first
        if await button_locator.count() > 0:
            print("🔍 找到“查看全部”按钮，准备点击...")
            await button_locator.click()
            print("👍 已点击“查看全部”按钮。")
        else:
            print("ℹ️ 未找到“查看全部”按钮。")

        # --- 调试信息 ---
        print("🔄 [5/7] 开始执行150次滚动循环...")
        for i in range(150):
            # --- 调试信息 ---
            print(f"    正在进行第 {i + 1}/150 次滚动...")
            next_button_locator = page.locator(".ContentItem-more").first
            if await next_button_locator.count() > 0:
                print("    🔍 找到“阅读全文”按钮，准备点击...")
                await next_button_locator.click()
                print("    👍 已点击“阅读全文”按钮。")
            await page.keyboard.press("PageDown")
            await asyncio.sleep(1)
        print("🟢 滚动循环完成。")

        all_pictures = []
        # --- 调试信息 ---
        print("🔍 [6/7] 开始提取所有图片链接...")
        #src_locator = page.locator(".RichContent-inner img[src^='https']")
        src_locator = page.locator(".chapterpic img")
        count = await src_locator.count()
        if count > 0:
            print(f"    共找到 {count} 个图片元素，开始逐个提取链接...")
            for i in range(count):
                locator = src_locator.nth(i)
                picture = await locator.get_attribute("src")
                all_pictures.append(picture)
                # --- 调试信息 ---
                print(f"        ({i + 1}/{count}) 提取到链接，正在等待1秒...")
                await asyncio.sleep(1)
            print(f"✅ 链接提取完毕，共获得 {len(all_pictures)} 个链接。")
        else:
            print("🤔 没有找到任何图片。")

    # --- 调试信息 ---
    print("✅ [7/7] 'download_page' 函数执行完毕，准备返回链接列表。")
    return all_pictures


async def main():
    # --- 调试信息 ---
    print("--- 程序开始 ---")
    url = "https://www.manhuazhan.com/comic/252419"
    first_links = await get_first_links(url)
    print(first_links)

    # 确保文件夹存在
    if not os.path.exists(all_output_path):
        os.makedirs(all_output_path)
        print(f"📂 已创建文件夹: {all_output_path}")

    all_pictures = await download_page(url)
    print(all_pictures)

    # --- 调试信息 ---
    if all_pictures:
        print(f"\n--- 开始下载任务，共 {len(all_pictures)} 张图片 ---")
    else:
        print("\n--- 未获取到图片链接，任务结束 ---")

    async with aiohttp.ClientSession() as session:
            for i, pictures in enumerate(all_pictures):
                # 增加一个对空链接的判断，防止报错
                try:
                    if not pictures:
                        print(f"⚠️ 第 {i + 1} 个链接为空，已跳过。")
                        continue

                    async with session.get(pictures) as response:
                        content = await response.read()
                        output_path = f"{all_output_path}/{i}.jpg"
                        async with aiofiles.open(output_path, "wb") as f:
                            await f.write(content)
                            # 您原有的成功信息已经很好了
                            print("第" + str(i + 1) + "张照片下载成功")
                except Exception as e:
                    continue






    # --- 调试信息 ---
    print("\n--- 所有任务完成，程序结束 ---")


if __name__ == "__main__":
    asyncio.run(main())