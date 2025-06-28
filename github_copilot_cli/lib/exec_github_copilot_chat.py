
import io
import os
import subprocess
import sys
import time

import pytesseract
from PIL import Image
import pyautogui
import pygetwindow as gw

from github_copilot_cli.lib.logger import logger
from github_copilot_cli.config.config import load_and_validate_config_file

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yml")
sleep_config = load_and_validate_config_file("sleep_seconds", CONFIG_PATH)


def open_vscode_with_file(file: str = None):
    if sys.platform == "darwin":
        args = ["open", "-a", "/Applications/Visual Studio Code.app"]
        if file:
            args.append(file)
        subprocess.Popen(args)

    # elif sys.platform.startswith("win"):
    #     code_path = shutil.which("code")
    #     if code_path and os.path.exists(code_path):
    #         args = [code_path]
    #         if file:
    #             args.append(file)
    #         subprocess.Popen(args)
    #     else:
    #         # Try default install paths for VS Code
    #         possible_paths = [
    #             r"C:\\Users\\{}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe".format(os.getlogin()),
    #             r"C:\\Program Files\\Microsoft VS Code\\Code.exe",
    #             r"C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe"
    #         ]
    #         for path in possible_paths:
    #             if os.path.exists(path):
    #                 args = [path]
    #                 if file:
    #                     args.append(file)
    #                 subprocess.Popen(args)
    #                 break
    #         else:
    #             logger.error('VS Code executable not found. Please install VS Code or specify its path.')
    #             return

    else:
        logger.error("Unsupported platform for opening Visual Studio Code.")
        exit(1)

    for _ in range(30):
        titles = gw.getAllTitles()
        if any("Code" in t for t in titles):
            break
        time.sleep(sleep_config.get("wait_close_retry"))
        logger.info(f"Window titles: {titles}")


def exec_github_copilot_chat(chat_message: str, working_directory: str, file: str, wait_response_time: int = 60):
    # Raise error if multibyte characters are included
    if any(ord(c) > 127 for c in chat_message):
        raise ValueError("chat_message contains multibyte characters. Please use only ASCII alphanumeric characters.")

    try:

        # Open Visual Studio Code
        open_vscode_with_file(working_directory)
        time.sleep(sleep_config.get("after_open_vscode"))

        # Open the file
        open_vscode_with_file(file)
        time.sleep(sleep_config.get("after_open_vscode"))

        # Open GitHub Copilot Chat
        pyautogui.keyDown("command")
        pyautogui.keyDown("shift")
        pyautogui.keyDown("i")
        pyautogui.keyUp("i")
        pyautogui.keyUp("shift")
        pyautogui.keyUp("command")
        time.sleep(sleep_config.get("after_open_chat"))

        # Open a new chat
        pyautogui.keyDown("ctrl")
        pyautogui.keyDown("l")
        pyautogui.keyUp("l")
        pyautogui.keyUp("ctrl")

        # Approve changes
        pyautogui.keyDown("command")
        pyautogui.keyDown("enter")
        pyautogui.keyUp("enter")
        pyautogui.keyUp("command")

        logger.info(f"Opened GitHub Copilot Chat. file: {file}")
        time.sleep(sleep_config.get("after_open_chat"))

        # Switch to ASCII input mode
        if sys.platform.startswith("win"):
            pyautogui.press("f12")
        else:
            pyautogui.press("eisuu")

        # Enter chat message
        time.sleep(sleep_config.get("before_write_message"))
        chat_message_no_newline = chat_message.replace("\n", " ").replace("\r", " ")
        pyautogui.write(chat_message_no_newline, interval=0.005)
        pyautogui.press("enter")
        time.sleep(sleep_config.get("wait_second_enter"))
        pyautogui.press("enter")
        logger.info(f"Entered instruction. file: {file}")

        # Wait for Copilot Chat response to complete
        completed_keywords_pattern = ["file changed", "files changed"]
        ignored_keywords_pattern = ["Applying"]
        found = False
        max_wait = wait_response_time
        interval = 2
        elapsed = 0

        while elapsed < max_wait:
            # Capture only VSCode window (fallback if getWindowsWithTitle is not available)
            try:
                vscode_windows = gw.getWindowsWithTitle("Code")
            except AttributeError:
                # Get all window titles and filter by title
                all_windows = []
                if hasattr(gw, 'getAllWindows'):
                    all_windows = gw.getAllWindows()
                elif hasattr(gw, '_getAllWindows'):
                    all_windows = gw._getAllWindows()
                vscode_windows = [w for w in all_windows if hasattr(w, 'title') and w.title and "Code" in w.title]

            if vscode_windows:
                win = vscode_windows[0]
                x, y, width, height = win.left, win.top, win.width, win.height
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
            else:
                screenshot = pyautogui.screenshot()
            buf = io.BytesIO()
            screenshot.save(buf, format='PNG')
            buf.seek(0)
            img = Image.open(buf)
            text = pytesseract.image_to_string(img)

            logger.debug(text.lower())

            if any(k.lower() in text.lower() for k in completed_keywords_pattern) and not any(k.lower() in text.lower() for k in ignored_keywords_pattern):
                found = True
                logger.info(f"Copilot Chat response detected as complete. file: {file}")
                break

            time.sleep(interval)
            elapsed += interval
        time.sleep(sleep_config.get("after_copilot_chat_response"))

        if not found:
            logger.warning(f"Copilot Chat response was not detected as complete within the wait time. file: {file}")

        # Approve changes
        pyautogui.keyDown("command")
        pyautogui.keyDown("enter")
        pyautogui.keyUp("enter")
        pyautogui.keyUp("command")

        # Save all
        pyautogui.keyDown("command")
        pyautogui.keyDown("k")
        pyautogui.keyUp("k")
        pyautogui.keyUp("command")
        pyautogui.keyDown("command")
        pyautogui.keyDown("a")
        pyautogui.keyUp("a")

        # Close all windows
        pyautogui.keyDown("command")
        pyautogui.keyDown("k")
        pyautogui.keyUp("k")
        pyautogui.keyUp("command")
        pyautogui.keyDown("command")
        pyautogui.keyDown("w")
        pyautogui.keyUp("w")
        pyautogui.keyUp("command")

        logger.info(f"Executed instruction. file: {file}")

        time.sleep(sleep_config.get("after_save"))

    finally:
        while True:
            if sys.platform == "darwin":
                os.system("pgrep -f 'Visual Studio Code.app/Contents/MacOS/Electron' | awk '{print $NF}' | xargs -r kill")
            # elif sys.platform.startswith("win"):
            #     os.system("taskkill /IM Code.exe /F")
            else:
                logger.warning("Unsupported platform for closing Visual Studio Code.")

            logger.info(f"Exited Visual Studio Code. file: {file}")
            time.sleep(sleep_config.get("after_close_vscode"))

            if os.system("pgrep -f 'Visual Studio Code.app/Contents/MacOS/Electron'") == 0:
                logger.info("Visual Studio Code is still running. Waiting to close...")
                time.sleep(sleep_config.get("wait_close_retry"))
                continue
            else:
                logger.info("Visual Studio Code has been closed.")
                break
