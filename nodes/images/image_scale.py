"""
按宽高比缩放图像节点
"""
import torch
from PIL import Image
import math
from .image_utils import tensor2pil, pil2tensor, image2mask, num_round_up_to_multiple, fit_resize_image, is_valid_mask


CATEGORY = "🐍 NCE/Utils"


class NCEImageScaleByAspectRatio:

    def __init__(self):
        self.NODE_NAME = 'NCEImageScaleByAspectRatio'

    @classmethod
    def INPUT_TYPES(self):
        ratio_list = ['original', 'custom', '1:1', '3:2', '4:3', '16:9', '2:3', '3:4', '9:16']
        fit_mode = ['letterbox', 'crop', 'fill']
        method_mode = ['lanczos', 'bicubic', 'hamming', 'bilinear', 'box', 'nearest']
        multiple_list = ['8', '16', '32', '64', '128', '256', '512', 'None']
        scale_to_list = ['None', 'longest', 'shortest', 'width', 'height', 'total_pixel(kilo pixel)']
        return {
            "required": {
                "aspect_ratio": (ratio_list,),
                "proportional_width": ("INT", {"default": 1, "min": 1, "max": 100000000, "step": 1}),
                "proportional_height": ("INT", {"default": 1, "min": 1, "max": 100000000, "step": 1}),
                "fit": (fit_mode,),
                "method": (method_mode,),
                "round_to_multiple": (multiple_list,),
                "scale_to_side": (scale_to_list,),
                "scale_to_length": ("INT", {"default": 1024, "min": 4, "max": 100000000, "step": 1}),
                "background_color": ("STRING", {"default": "#000000"}),
            },
            "optional": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "BOX", "INT", "INT",)
    RETURN_NAMES = ("image", "mask", "original_size", "width", "height",)
    FUNCTION = 'image_scale_by_aspect_ratio'
    CATEGORY = CATEGORY

    def image_scale_by_aspect_ratio(self, aspect_ratio, proportional_width, proportional_height,
                                    fit, method, round_to_multiple, scale_to_side, scale_to_length,
                                    background_color,
                                    image=None, mask=None,
                                    ):
        orig_images = []
        orig_masks = []
        orig_width = 0
        orig_height = 0
        target_width = 0
        target_height = 0
        ratio = 1.0
        ret_images = []
        ret_masks = []
        
        if image is not None:
            for i in image:
                i = torch.unsqueeze(i, 0)
                orig_images.append(i)
            orig_width, orig_height = tensor2pil(orig_images[0]).size
            
        if mask is not None:
            if mask.dim() == 2:
                mask = torch.unsqueeze(mask, 0)
            for m in mask:
                m = torch.unsqueeze(m, 0)
                if not is_valid_mask(m) and m.shape == torch.Size([1, 64, 64]):
                    print(f"Warning: {self.NODE_NAME} input mask is empty, ignore it.")
                else:
                    orig_masks.append(m)

            if len(orig_masks) > 0:
                _width, _height = tensor2pil(orig_masks[0]).size
                if (orig_width > 0 and orig_width != _width) or (orig_height > 0 and orig_height != _height):
                    print(f"Error: {self.NODE_NAME} execute failed, because the mask doesn't match image.")
                    return (None, None, None, 0, 0,)
                elif orig_width + orig_height == 0:
                    orig_width = _width
                    orig_height = _height

        if orig_width + orig_height == 0:
            print(f"Error: {self.NODE_NAME} execute failed, because the image or mask at least one must be input.")
            return (None, None, None, 0, 0,)

        # 计算宽高比
        if aspect_ratio == 'original':
            ratio = orig_width / orig_height
        elif aspect_ratio == 'custom':
            ratio = proportional_width / proportional_height
        else:
            s = aspect_ratio.split(":")
            ratio = int(s[0]) / int(s[1])

        # 计算目标宽度和高度
        if ratio > 1:
            if scale_to_side == 'longest':
                target_width = scale_to_length
                target_height = int(target_width / ratio)
            elif scale_to_side == 'shortest':
                target_height = scale_to_length
                target_width = int(target_height * ratio)
            elif scale_to_side == 'width':
                target_width = scale_to_length
                target_height = int(target_width / ratio)
            elif scale_to_side == 'height':
                target_height = scale_to_length
                target_width = int(target_height * ratio)
            elif scale_to_side == 'total_pixel(kilo pixel)':
                target_width = math.sqrt(ratio * scale_to_length * 1000)
                target_height = target_width / ratio
                target_width = int(target_width)
                target_height = int(target_height)
            else:
                target_width = orig_width
                target_height = int(target_width / ratio)
        else:
            if scale_to_side == 'longest':
                target_height = scale_to_length
                target_width = int(target_height * ratio)
            elif scale_to_side == 'shortest':
                target_width = scale_to_length
                target_height = int(target_width / ratio)
            elif scale_to_side == 'width':
                target_width = scale_to_length
                target_height = int(target_width / ratio)
            elif scale_to_side == 'height':
                target_height = scale_to_length
                target_width = int(target_height * ratio)
            elif scale_to_side == 'total_pixel(kilo pixel)':
                target_width = math.sqrt(ratio * scale_to_length * 1000)
                target_height = target_width / ratio
                target_width = int(target_width)
                target_height = int(target_height)
            else:
                target_height = orig_height
                target_width = int(target_height * ratio)

        # 按倍数对齐
        if round_to_multiple != 'None':
            multiple = int(round_to_multiple)
            target_width = num_round_up_to_multiple(target_width, multiple)
            target_height = num_round_up_to_multiple(target_height, multiple)

        # 设置缩放采样器
        resize_sampler = Image.LANCZOS
        if method == "bicubic":
            resize_sampler = Image.BICUBIC
        elif method == "hamming":
            resize_sampler = Image.HAMMING
        elif method == "bilinear":
            resize_sampler = Image.BILINEAR
        elif method == "box":
            resize_sampler = Image.BOX
        elif method == "nearest":
            resize_sampler = Image.NEAREST

        # 处理图像
        if len(orig_images) > 0:
            for i in orig_images:
                _image = tensor2pil(i).convert('RGB')
                _image = fit_resize_image(_image, target_width, target_height, fit, resize_sampler, background_color)
                ret_images.append(pil2tensor(_image))
                
        # 处理蒙版
        if len(orig_masks) > 0:
            for m in orig_masks:
                _mask = tensor2pil(m).convert('L')
                _mask = fit_resize_image(_mask, target_width, target_height, fit, resize_sampler).convert('L')
                ret_masks.append(image2mask(_mask))
                
        # 返回结果
        if len(ret_images) > 0 and len(ret_masks) > 0:
            print(f"{self.NODE_NAME} Processed {len(ret_images)} image(s).")
            return (torch.cat(ret_images, dim=0), torch.cat(ret_masks, dim=0), [orig_width, orig_height], target_width, target_height,)
        elif len(ret_images) > 0 and len(ret_masks) == 0:
            print(f"{self.NODE_NAME} Processed {len(ret_images)} image(s).")
            return (torch.cat(ret_images, dim=0), None, [orig_width, orig_height], target_width, target_height,)
        elif len(ret_images) == 0 and len(ret_masks) > 0:
            print(f"{self.NODE_NAME} Processed {len(ret_masks)} mask(s).")
            return (None, torch.cat(ret_masks, dim=0), [orig_width, orig_height], target_width, target_height,)
        else:
            print(f"Error: {self.NODE_NAME} skipped, because the available image or mask is not found.")
            return (None, None, None, 0, 0,)
