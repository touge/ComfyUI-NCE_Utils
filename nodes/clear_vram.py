import torch.cuda
import gc
import comfy.model_management

from ..libs.utils import AnyType, clear_memory
any = AnyType("*")

CATEGORY = "🐍 NCE/Utils"

class ClearVRAM:
    """
    清理VRAM和系统内存的节点
    
    功能说明:
        - 卸载已加载的模型
        - 清理GPU显存缓存
        - 执行Python垃圾回收
    """

    def __init__(self):
        self.NODE_NAME = 'ClearVRAM'

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "anything": (any, {}),
                "clear_cache": ("BOOLEAN", {"default": True}),
                "clear_models": ("BOOLEAN", {"default": True}),
            },
            "optional": {
            }
        }

    RETURN_TYPES = (any,)
    RETURN_NAMES = ("any",)
    FUNCTION = "clear_vram"
    CATEGORY = CATEGORY
    OUTPUT_NODE = True

    def clear_vram(self, anything, clear_cache, clear_models):
        """
        清理显存和内存
        
        Args:
            anything: 任意输入，用于连接工作流
            clear_cache: 是否清理GPU缓存
            clear_models: 是否卸载所有模型
        """
        # 卸载所有模型
        if clear_models:
            comfy.model_management.unload_all_models()
            comfy.model_management.cleanup_models()
        
        # 清理GPU缓存
        if clear_cache:
            clear_memory()
            comfy.model_management.soft_empty_cache()
        
        # 执行垃圾回收
        gc.collect()
        
        return (anything,)

