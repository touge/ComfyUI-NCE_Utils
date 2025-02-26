import random
from PIL import Image, ImageFilter, ImageChops, ImageDraw, ImageOps, ImageEnhance, ImageFont
import math
import os
import folder_paths
import shutil

def log(message:str, message_type:str='info'):
    if message_type == 'error':
        message = '\033[1;41m' + message + '\033[m'
    elif message_type == 'warning':
        message = '\033[1;31m' + message + '\033[m'
    elif message_type == 'finish':
        message = '\033[1;32m' + message + '\033[m'
    else:
        message = '\033[1;33m' + message + '\033[m'
    print(f"#{message}")

try:
    from cv2.ximgproc import guidedFilter
except ImportError as e:
    # print(e)
    log(f"Cannot import name 'guidedFilter' from 'cv2.ximgproc'"
        f"\nA few nodes cannot works properly, while most nodes are not affected. Please REINSTALL package 'opencv-contrib-python'."
        f"\nFor detail refer to \033[4mhttps://github.com/chflame163/ComfyUI_LayerStyle/issues/5\033[0m")
    
def generate_random_name(prefix: str, suffix: str, length: int) -> str:
    # 生成一个指定长度的随机字符串，并在其前后加上前缀和后缀
    # prefix: 字符串前缀
    # suffix: 字符串后缀
    # length: 随机字符串的长度
    
    # 使用列表生成式生成指定长度的随机字符串
    name = ''.join(random.choice("abcdefghijklmnopqrstupvxyz1234567890") for x in range(length))
    
    # 返回拼接前缀、随机字符串和后缀后的结果
    return prefix + name + suffix
