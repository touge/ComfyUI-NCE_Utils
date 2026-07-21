"""
Latent 预设分辨率节点
提供常用分辨率预设，支持空 Latent 生成及现有 Latent 缩放
"""

import torch
import comfy.model_management
import comfy.utils

CATEGORY = "🐍 NCE/图像"
class NCELatentPresetResolution:
    """预设分辨率 (Latent)"""
    
    RESOLUTIONS = [
        "480*832 (9:16)",
        "832*480 (16:9)",
        "576*1024 (9:16)",
        "1024*576 (16:9)",
        "640*1138 (9:16)",
        "1138*640 (16:9)",
        "720*1280 (9:16)",
        "1280*720 (16:9)",
        "1024*1024 (1:1)",
        "768*1024 (3:4)",
        "1024*768 (4:3)",
        "1080*1920 (9:16)",
        "1920*1080 (16:9)",
        # 其他常见尺寸
        "512*512 (1:1)",
        "768*768 (1:1)",
        "512*768 (2:3)",
        "768*512 (3:2)",
        "896*1152 (3:4)",
        "1152*896 (4:3)",
        "832*1216 (2:3)",
        "1216*832 (3:2)",
        "768*1344 (9:16)",
        "1344*768 (16:9)",
        "704*1408 (1:2)",
        "1408*704 (2:1)",
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "resolution": (cls.RESOLUTIONS,),
            }
        }

    RETURN_TYPES = ("LATENT", "INT", "INT",)
    RETURN_NAMES = ("latent", "width", "height",)
    FUNCTION = "get_resolution"
    CATEGORY = CATEGORY

    def get_resolution(self, resolution):
        # 1. 确定宽度 and 高度并解析预设
        parts = resolution.split("*")
        target_width = int(parts[0].strip())
        
        height_part = parts[1].split()[0].split("(")[0].strip()
        target_height = int(height_part)

        # 确保 latent 的宽度和高度为 8 的倍数
        target_width = round(target_width / 8) * 8
        target_height = round(target_height / 8) * 8

        # 宽度和高度最小限制为 8
        latent_w = max(8, target_width // 8)
        latent_h = max(8, target_height // 8)

        # 生成新的空 latent (批次大小固定为 1)
        device = comfy.model_management.intermediate_device()
        dtype = comfy.model_management.intermediate_dtype()
        
        latent_tensor = torch.zeros([1, 4, latent_h, latent_w], device=device, dtype=dtype)
        s = {"samples": latent_tensor, "downscale_ratio_spacial": 8}
        out_width = latent_w * 8
        out_height = latent_h * 8

        return (s, out_width, out_height,)
