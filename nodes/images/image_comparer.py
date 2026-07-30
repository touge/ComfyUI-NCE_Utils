"""
图像对比节点
"""
import os
import random
import json
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import folder_paths
from comfy.cli_args import args

CATEGORY = "🐍 NCE/图像"


class NCEImageComparer:
    """图像对比节点，用于在 UI 中对比两张图像"""

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for _ in range(5))
        self.compress_level = 1

    OUTPUT_NODE = True
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    CATEGORY = CATEGORY
    FUNCTION = "compare_images"
    DESCRIPTION = "在 UI 中对比两张图像（支持滑块拖动对比）"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "image_a": ("IMAGE",),
                "image_b": ("IMAGE",),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    def preview_images(self, images, filename_prefix="nce.compare", prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0]
        )
        results = list()
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

        return { "ui": { "images": results }, "result" : (images,) }

    def compare_images(
        self,
        image_a=None,
        image_b=None,
        filename_prefix="nce.compare",
        prompt=None,
        extra_pnginfo=None
    ):
        result = {"ui": {"a_images": [], "b_images": []}}
        if image_a is not None and len(image_a) > 0:
            saved_a = self.preview_images(image_a, filename_prefix, prompt, extra_pnginfo)
            result['ui']['a_images'] = saved_a.get('ui', {}).get('images', [])

        if image_b is not None and len(image_b) > 0:
            saved_b = self.preview_images(image_b, filename_prefix, prompt, extra_pnginfo)
            result['ui']['b_images'] = saved_b.get('ui', {}).get('images', [])

        return result
