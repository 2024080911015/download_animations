import os
import subprocess
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# Global variable to store the found M3U8 link
m3u8_link = None

def download_vedioes(m3u8_url: str, output_path: str):
    """
    Downloads a video from an m3u8 URL using ffmpeg and provides detailed debugging output.
    """
    print("\n--- 调试信息: 开始下载视频 ---")
    print(f"➡️ M3U8 URL: {m3u8_url}")
    print(f"➡️ 输出文件路径: {output_path}")

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"📂 已创建目录: {output_dir}")
        except OSError as e:
            print(f"❌ 创建目录失败: {e}")
            return  # Exit if directory creation fails

    command = [
        'ffmpeg',
        '-protocol_whitelist', 'file,http,https,tcp,tls,crypto',
        '-i', m3u8_url,
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        output_path
    ]

    # Print the exact command being executed for easy debugging
    # Using ' '.join is for display purposes only
    print(f"🔧 执行的 FFmpeg 命令: {' '.join(command)}")

    try:
        print("\n🚀 开始执行 ffmpeg 命令... (这可能需要一些时间)")
        # Execute the command
        result = subprocess.run(
            command,
            check=True,       # Raise an exception for non-zero exit codes (errors)
            capture_output=True, # Capture stdout and stderr
            text=True,          # Decode stdout/stderr as text
            encoding="utf-8"    # Specify the encoding
        )
        print("✅ ffmpeg 命令成功执行。")

        # Print ffmpeg's output, which is often useful for verification
        print("\n--- FFmpeg 标准输出 (stdout) ---")
        print(result.stdout if result.stdout.strip() else "无")
        print("\n--- FFmpeg 标准错误/日志 (stderr) ---")
        print(result.stderr if result.stderr.strip() else "无")
        print(f"🎉 视频已成功下载到: {output_path}")

    except FileNotFoundError:
        print("\n❌ 错误: 'ffmpeg' 命令未找到。")
        print("   请确保 FFmpeg 已安装并将其可执行文件所在的目录添加到了系统的 PATH 环境变量中。")

    except subprocess.CalledProcessError as e:
        # This block runs if ffmpeg returns an error (non-zero exit code)
        print(f"\n❌ ffmpeg 命令执行失败，返回码: {e.returncode}")
        print("\n--- FFmpeg 标准输出 (stdout) ---")
        print(e.stdout if e.stdout and e.stdout.strip() else "无")
        print("\n--- FFmpeg 错误详情 (stderr) ---")
        print(e.stderr if e.stderr and e.stderr.strip() else "没有可用的错误详情。")

    except Exception as e:
        print(f"\n❌ 下载过程中发生未知错误: {e}")

    finally:
        print("--- 调试信息: 视频下载函数结束 ---\n")


def get_links(url: str):
    """
    Uses Playwright to navigate to a page and capture the first M3U8 link requested.
    """
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        def get_m3u8_link(request):
            global m3u8_link
            # Check if the URL contains .m3u8 and we haven't found one yet
            if ".m3u8" in request.url and not m3u8_link:
                print(f"🕵️‍♂️ 捕获到 M3U8 链接: {request.url}")
                m3u8_link = request.url
                # Optional: Once found, you can stop listening to further requests to be efficient
                # page.remove_listener("request", get_m3u8_link)

        page.on("request", get_m3u8_link)

        try:
            print(f"🖥️ 正在打开页面: {url}")
            page.goto(url, timeout=60000, wait_until="networkidle")
            # Add a small extra wait just in case some scripts run after networkidle
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"❌ 打开页面时出错: {e}")
        finally:
            browser.close()

        return m3u8_link

def main():
    url = "https://www.xhsiu122.vip:2024/videoplay/72979"
    # IMPORTANT: ffmpeg needs a full FILE path, not just a directory.
    # We will create a file name based on the video ID from the URL.
    output_dir = "C:/Users/iiijj/Desktop/vedios"
    try:
        video_id = url.strip().split('/')[-1] or "video"
    except IndexError:
        video_id = "video"
    output_file_path = os.path.join(output_dir, f"{video_id}.mp4")

    print(f"🎬 任务开始 - 目标URL: {url}")
    link = get_links(url)

    if link:
        download_vedioes(link, output_file_path)
    else:
        print("❌ 未能获取到 m3u8 链接。程序退出。")

if __name__ == '__main__':
    main()




