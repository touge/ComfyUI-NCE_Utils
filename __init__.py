from .nodes.text_node import *
from .nodes.image_node import *
# from .nodes.TextOnImage import *
from .nodes.video_style_generator import *

from .nodes.video_style_generator import *
from .nodes.cache_node import *

from .nodes.prompt_enhancer_nodes import *

NODE_CONFIG = {
    "NCEVideoStylerGenerator": {
        "class": NCEVideoStylerGenerator,
        "name": "视频风格生成器"  
    },

    "NCEVideoPromptEnhancer": {
        "class": NCEVideoPromptEnhancer,
        "name": "视频提示增强器"
    },  
    "NCEVideoPromptEnhancerLoader": {
        "class": NCEVideoPromptEnhancerLoader,
        "name": "视频提示器模型加载"
    },

    ###########################string/text tools#######################
    "NCEUtilsShowText": {
        "class": NCEUtilsShowText,
        "name": "展示文本"
    },
    "NCEUtilsMultilineText":{
        "class": NCEUtilsMultilineText,
        "name": "多行文本"  
    },
    "NCEMergeTexts":{
        "class": NCEMergeTexts,
        "name": "合并字符串"  
    },
    "NCEListToString": {
        "class": NCEListToString,
        "name": "列表转字符串"
    },
    "NCEStringToList": {
        "class": NCEStringToList,
        "name": "字符串转列表"
    },
    ###########################image tools#######################
    "NCEUtilsSaveImagePlus": {
        "class": NCEUtilsSaveImagePlus,
        "name": "保存图像+",
    },
    "NCEEncodeBlindWaterMark": {
        "class": NCEEncodeBlindWaterMark,
        "name": "图像写入不可见水印",
    },
    "NCEDecodeBlindWaterMark": {
        "class": NCEDecodeBlindWaterMark,
        "name": "提取图像中不可见水印",
    },
    "NCECropFace":{
        "class": NCECropFace,
        "name": "人脸识别剪切"
    },
    "NCETextOnImage":{
        "class": NCETextOnImage,
        "name": "图片上写文宇"
    },
    ###########################logic/cache tools#######################
    "NCECleanGPUUsed": {
        "class": NCECleanGPUUsed,
        "name": "清除显存"
    },
    "NCECleanRAM": {
        "class": NCECleanRAM,
        "name": "清除内存"
    },
    "NCEClearCacheAll": {
        "class": NCEClearCacheAll,
        "name": "清除所有缓存"
    }
}

def generate_node_mappings(node_config):
    node_class_mappings = {}
    node_display_name_mappings = {}

    for node_name, node_info in node_config.items():
        node_class_mappings[node_name] = node_info["class"]
        node_display_name_mappings[node_name] = node_info.get("name", node_info["class"].__name__)

    return node_class_mappings, node_display_name_mappings

NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = generate_node_mappings(NODE_CONFIG)
WEB_DIRECTORY = "./js"


__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

print('🐍 NCE Utils Loaded')



