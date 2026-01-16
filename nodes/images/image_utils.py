"""
图像处理辅助函数
包含图像转换、缩放等常用工具函数
"""
import torch
import numpy as np
from PIL import Image
import math


def pil2tensor(image: Image) -> torch.Tensor:
    """将 PIL Image 转换为 torch.Tensor"""
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


def tensor2pil(t_image: torch.Tensor) -> Image:
    """将 torch.Tensor 转换为 PIL Image"""
    if t_image.dtype != torch.float32:
        t_image = t_image.float()
    return Image.fromarray(
        np.clip(
            255.0 * t_image.cpu().numpy().squeeze(),
            0,
            255
        ).astype(np.uint8)
    )


def image2mask(image: Image) -> torch.Tensor:
    """将 PIL Image 转换为 mask tensor"""
    if image.mode == 'L':
        return torch.tensor([pil2tensor(image)[0, :, :].tolist()])
    else:
        image = image.convert('RGB').split()[0]
        return torch.tensor([pil2tensor(image)[0, :, :].tolist()])


def is_valid_mask(tensor: torch.Tensor) -> bool:
    """检查 mask 是否有效(不是全黑)"""
    return not bool(torch.all(tensor == 0).item())


def num_round_up_to_multiple(number: int, multiple: int) -> int:
    """向上取整到指定倍数"""
    remainder = number % multiple
    if remainder == 0:
        return number
    else:
        factor = (number + multiple - 1) // multiple  # 向上取整的计算方式
        return factor * multiple


def fit_resize_image(image: Image, target_width: int, target_height: int, 
                     fit: str, resize_sampler, background_color: str = '#000000') -> Image:
    """
    按指定模式缩放图像
    
    Args:
        image: 输入图像
        target_width: 目标宽度
        target_height: 目标高度
        fit: 适配模式 ('letterbox', 'crop', 'fill')
        resize_sampler: PIL 缩放采样器
        background_color: 背景颜色(用于 letterbox 模式)
    
    Returns:
        缩放后的图像
    """
    image = image.convert('RGB')
    orig_width, orig_height = image.size
    
    if image is not None:
        if fit == 'letterbox':
            # 保持宽高比,留黑边
            if orig_width / orig_height > target_width / target_height:  # 更宽,上下留黑
                fit_width = target_width
                fit_height = int(target_width / orig_width * orig_height)
            else:  # 更瘦,左右留黑
                fit_height = target_height
                fit_width = int(target_height / orig_height * orig_width)
            fit_image = image.resize((fit_width, fit_height), resize_sampler)
            ret_image = Image.new('RGB', size=(target_width, target_height), color=background_color)
            ret_image.paste(fit_image, box=((target_width - fit_width)//2, (target_height - fit_height)//2))
        elif fit == 'crop':
            # 裁剪以填充目标尺寸
            if orig_width / orig_height > target_width / target_height:  # 更宽,裁左右
                fit_width = int(orig_height * target_width / target_height)
                fit_image = image.crop(
                    ((orig_width - fit_width)//2, 0, (orig_width - fit_width)//2 + fit_width, orig_height))
            else:   # 更瘦,裁上下
                fit_height = int(orig_width * target_height / target_width)
                fit_image = image.crop(
                    (0, (orig_height-fit_height)//2, orig_width, (orig_height-fit_height)//2 + fit_height))
            ret_image = fit_image.resize((target_width, target_height), resize_sampler)
        else:
            # 直接拉伸填充
            ret_image = image.resize((target_width, target_height), resize_sampler)
    
    return ret_image
