import pyautogui as pag
import pygetwindow as pgw
import time
import PIL.Image
import sys
import pystray
import threading
import numpy as np
import cv2

# 加载图标
image = PIL.Image.open("icon.png")

stop_all = threading.Event()
monitoring_running = True  # 将默认状态置为 True

def captureScreen(region = None):
    return cv2.cvtColor(np.array(pag.screenshot(region=region)), cv2.COLOR_RGB2BGR)

def detectClarity(image):
    return cv2.Laplacian(cv2.cvtColor(image, cv2.COLOR_RGB2BGR), cv2.CV_64F).var()

def tray_icon_thread():
    def on_start(icon, item):
        global monitoring_running
        monitoring_running = True

    def on_stop(icon, item):
        global monitoring_running
        monitoring_running = False

    def on_quit(icon, item):
        stop_all.set()
        icon.stop()
        sys.exit(0)

    menu = pystray.Menu(
        pystray.MenuItem('开始', on_start),
        pystray.MenuItem('停止', on_stop),
        pystray.MenuItem('退出', on_quit)
    )
    icon = pystray.Icon("Seewo Light to Photo Helper", image, menu=menu)
    icon.run()

def monitoring_thread():
    while not stop_all.is_set():
        try:
            if monitoring_running:
                if "希沃视频展台" == pgw.getActiveWindowTitle():
                    time.sleep(3)
                    photoPos = pag.locateCenterOnScreen("photo.png", confidence=0.8)
                    while monitoring_running and not stop_all.is_set():
                        time.sleep(1)
                        lightPos = pag.locateCenterOnScreen("lighted.png", confidence=0.8)
                        if lightPos is not None and detectClarity(captureScreen((760, 340, 400, 400))):
                            pag.leftClick(photoPos)
                            pag.leftClick(lightPos)
                else:
                    time.sleep(1)
            else:
                time.sleep(1)
        except Exception:
            pass

tray_thread = threading.Thread(target=tray_icon_thread)
monitoring_thread = threading.Thread(target=monitoring_thread)

tray_thread.start()
monitoring_thread.start()

tray_thread.join()
monitoring_thread.join()
