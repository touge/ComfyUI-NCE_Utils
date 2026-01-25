import random
# from PIL import Image, ImageFilter, ImageChops, ImageDraw, ImageOps, ImageEnhance, ImageFont
import math
import torch
from torchvision.utils import make_grid
import cv2
import numpy as np
import os
import folder_paths
# import shutil

def clear_memory():
    """
    清理内存和GPU缓存
    
    功能说明:
        - 执行Python垃圾回收
        - 清空CUDA缓存（如果可用）
        - 清理CUDA进程间通信缓存
    """
    import gc
    # Cleanup
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        
class AnyType(str):
  """
  特殊类型类，用于类型比较时始终返回相等
  
  说明:
      这是一个特殊的字符串子类，在比较操作中总是返回True（相等）或False（不相等）
      主要用于ComfyUI节点系统中的类型匹配
      Credit to pythongosssss
  """
  def __eq__(self, __value: object) -> bool:
    """
    相等比较运算符重载
    
    Args:
        __value: 要比较的对象
    
    Returns:
        bool: 始终返回True
    """
    return True
    
  def __ne__(self, __value: object) -> bool:
    """
    不等比较运算符重载
    
    Args:
        __value: 要比较的对象
    
    Returns:
        bool: 始终返回False
    """
    return False
    
def node_path():
    """
    获取当前节点的根目录路径
    
    Returns:
        str: 节点根目录的绝对路径（当前文件的上两级目录）
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def log(message:str, message_type:str='info'):
    """
    带颜色的日志输出函数
    
    Args:
        message (str): 要输出的日志消息
        message_type (str): 消息类型，可选值:
            - 'error': 错误消息（红色背景）
            - 'warning': 警告消息（红色文字）
            - 'finish': 完成消息（绿色文字）
            - 'info': 普通信息（黄色文字，默认值）
    
    功能说明:
        使用ANSI转义码为不同类型的消息添加颜色，便于在终端中区分
    """
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
    print(e)
    
def generate_random_name(prefix: str, suffix: str, length: int) -> str:
    """
    生成一个指定长度的随机字符串，并在其前后加上前缀和后缀
    
    Args:
        prefix (str): 字符串前缀
        suffix (str): 字符串后缀
        length (int): 随机字符串的长度
    
    Returns:
        str: 拼接后的完整字符串（前缀 + 随机字符串 + 后缀）
    
    示例:
        >>> generate_random_name("file_", ".txt", 8)
        'file_a3b7k9m2.txt'
    """
    # 使用列表生成式生成指定长度的随机字符串
    name = ''.join(random.choice("abcdefghijklmnopqrstupvxyz1234567890") for x in range(length))
    
    # 返回拼接前缀、随机字符串和后缀后的结果
    return prefix + name + suffix

def img2tensor(imgs, bgr2rgb=True, float32=True):
    """
    将Numpy数组转换为PyTorch张量

    Args:
        imgs (list[ndarray] | ndarray): 输入图像，可以是单个numpy数组或数组列表
        bgr2rgb (bool): 是否将BGR颜色空间转换为RGB，默认True
        float32 (bool): 是否转换为float32类型，默认True

    Returns:
        list[tensor] | tensor: 转换后的张量图像
            - 如果输入是列表，返回张量列表
            - 如果输入是单个数组，返回单个张量
    
    功能说明:
        - 自动处理颜色空间转换（BGR -> RGB）
        - 调整维度顺序从HWC到CHW格式
        - 支持批量处理多张图像
    """

    def _totensor(img, bgr2rgb, float32):
        """
        内部函数：将单个图像转换为张量
        
        Args:
            img (ndarray): 输入的numpy图像数组
            bgr2rgb (bool): 是否进行BGR到RGB的转换
            float32 (bool): 是否转换为float32类型
        
        Returns:
            tensor: 转换后的PyTorch张量
        """
        if img.shape[2] == 3 and bgr2rgb:
            if img.dtype == 'float64':
                img = img.astype('float32')
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = torch.from_numpy(img.transpose(2, 0, 1))
        if float32:
            img = img.float()
        return img

    if isinstance(imgs, list):
        return [_totensor(img, bgr2rgb, float32) for img in imgs]
    else:
        return _totensor(imgs, bgr2rgb, float32)


def tensor2img(tensor, rgb2bgr=True, out_type=np.uint8, min_max=(0, 1)):
    """
    将PyTorch张量转换为图像numpy数组

    功能说明:
        首先将值裁剪到[min, max]范围，然后归一化到[0, 1]

    Args:
        tensor (Tensor or list[Tensor]): 输入张量，支持以下形状:
            1) 4D批量张量，形状为 (B x 3/1 x H x W)
            2) 3D张量，形状为 (3/1 x H x W)
            3) 2D张量，形状为 (H x W)
            张量通道顺序应为RGB
        rgb2bgr (bool): 是否将RGB转换为BGR，默认True
        out_type (numpy type): 输出类型
            - np.uint8: 转换为uint8类型，范围[0, 255]
            - 其他: 浮点类型，范围[0, 1]
            默认为np.uint8
        min_max (tuple[int]): 用于裁剪的最小值和最大值，默认(0, 1)

    Returns:
        (ndarray or list): 转换后的numpy数组
            - 3D数组，形状为 (H x W x C)，通道顺序为BGR
            - 或2D数组，形状为 (H x W)（灰度图）
    
    Raises:
        TypeError: 如果输入不是张量或张量列表
        TypeError: 如果张量维度不是2D、3D或4D
    """
    if not (torch.is_tensor(tensor) or (isinstance(tensor, list) and all(torch.is_tensor(t) for t in tensor))):
        raise TypeError(f'tensor or list of tensors expected, got {type(tensor)}')

    if torch.is_tensor(tensor):
        tensor = [tensor]
    result = []
    for _tensor in tensor:
        _tensor = _tensor.squeeze(0).float().detach().cpu().clamp_(*min_max)
        _tensor = (_tensor - min_max[0]) / (min_max[1] - min_max[0])

        n_dim = _tensor.dim()
        if n_dim == 4:
            img_np = make_grid(_tensor, nrow=int(math.sqrt(_tensor.size(0))), normalize=False).numpy()
            img_np = img_np.transpose(1, 2, 0)
            if rgb2bgr:
                img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        elif n_dim == 3:
            img_np = _tensor.numpy()
            img_np = img_np.transpose(1, 2, 0)
            if img_np.shape[2] == 1:  # gray image
                img_np = np.squeeze(img_np, axis=2)
            else:
                if rgb2bgr:
                    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        elif n_dim == 2:
            img_np = _tensor.numpy()
        else:
            raise TypeError('Only support 4D, 3D or 2D tensor. ' f'But received with dimension: {n_dim}')
        if out_type == np.uint8:
            # Unlike MATLAB, numpy.unit8() WILL NOT round by default.
            img_np = (img_np * 255.0).round()
        img_np = img_np.astype(out_type)
        result.append(img_np)
    if len(result) == 1:
        result = result[0]
    return result