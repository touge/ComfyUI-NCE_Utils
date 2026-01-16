"""
图像信息节点
获取图像的尺寸和数量信息
"""

CATEGORY = "🐍 NCE/图像"


class NCEGetImageSize:
    """获取图像尺寸和数量"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT",)
    RETURN_NAMES = ("image", "width", "height", "count",)
    FUNCTION = "get_size"
    CATEGORY = CATEGORY
    DESCRIPTION = """
获取图像的宽度、高度和批次数量,
并将图像原样传递。
"""

    def get_size(self, image):
        width = image.shape[2]
        height = image.shape[1]
        count = image.shape[0]
        
        return {
            "ui": {
                "text": [f"{count}x{width}x{height}"]
            }, 
            "result": (image, width, height, count) 
        }
