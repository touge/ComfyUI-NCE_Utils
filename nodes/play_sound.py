from ..libs.utils import AnyType
any = AnyType("*")

CATEGORY = "🐍 NCE/系统"

class NCEUtilsPlaySound:
    """
    播放提示音的节点
    
    功能说明:
        - 在工作流执行完成或特定时机在浏览器中播放提示音
        - 支持自定义音量和音频文件
    """

    def __init__(self):
        self.NODE_NAME = 'NCEUtilsPlaySound'

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any": (any, {}),
                "mode": (["always", "on empty queue"], {}),
                "volume": ("FLOAT", {"min": 0, "max": 1, "step": 0.1, "default": 0.5}),
                "file": ("STRING", { "default": "notify.mp3" })
            }
        }

    FUNCTION = "nop"
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True,)
    OUTPUT_NODE = True
    RETURN_TYPES = (any,)
    RETURN_NAMES = ("any",)
    CATEGORY = CATEGORY

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def nop(self, any, mode, volume, file):
        return {"ui": {"a": []}, "result": (any,)}
