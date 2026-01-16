import torch
from comfy import model_management
import gc
import os

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any_type = AnyType("*")

CATEGORY = "🐍 NCE/Utils"

class NCECleanGPUUsed:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "anything": (any_type, {})
            },
            "optional": {},
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    OUTPUT_NODE = True
    FUNCTION = "empty_cache"
    CATEGORY = CATEGORY

    def empty_cache(self, anything, unique_id=None, extra_pnginfo=None):
        # 1. Clear VRAM cache managed by ComfyUI
        model_management.soft_empty_cache()
        
        # 2. Clear PyTorch Cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            
        # 3. Garbage Collection to free Python objects holding VRAM
        gc.collect()
        return (anything,)

class NCECleanRAM:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "anything": (any_type, {})
            },
            "optional": {},
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    OUTPUT_NODE = True
    FUNCTION = "empty_ram"
    CATEGORY = CATEGORY

    def empty_ram(self, anything, unique_id=None, extra_pnginfo=None):
        # 1. Unload all models from VRAM and RAM
        model_management.unload_all_models()
        
        # 2. Aggressive Garbage Collection
        gc.collect()
        
        # 3. Attempt to clear system memory further (Windows specific)
        try:
            import ctypes
            if os.name == 'nt':
                ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
        except Exception:
            pass
            
        return (anything,)

class NCEClearCacheAll:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "anything": (any_type, {}),
            },
            "optional": {},
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    OUTPUT_NODE = True
    FUNCTION = "empty_cache"
    CATEGORY = CATEGORY

    def empty_cache(self, anything, unique_id=None, extra_pnginfo=None):
        # 1. Unload all models
        model_management.unload_all_models()
        
        # 2. Clear ComfyUI internal VRAM cache
        model_management.soft_empty_cache()
        
        # 3. Clear PyTorch VRAM Cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        
        # 4. Aggressive Garbage Collection
        gc.collect()
        
        # 5. Clear System Memory (Windows)
        try:
            import ctypes
            if os.name == 'nt': 
                ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
        except Exception:
            pass

        return (anything,)
