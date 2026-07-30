"""
图像对比节点
"""
from nodes import PreviewImage

CATEGORY = "🐍 NCE/图像"


class NCEImageComparer(PreviewImage):
    """图像对比节点，用于在 UI 中对比两张图像"""

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
            saved_a = self.save_images(image_a, filename_prefix, prompt, extra_pnginfo)
            result['ui']['a_images'] = saved_a.get('ui', {}).get('images', [])

        if image_b is not None and len(image_b) > 0:
            saved_b = self.save_images(image_b, filename_prefix, prompt, extra_pnginfo)
            result['ui']['b_images'] = saved_b.get('ui', {}).get('images', [])

        return result
