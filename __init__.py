from .nodes.text_node import *
from .nodes.images import *
# from .nodes.TextOnImage import *
from .nodes.audios import *
from .nodes.logic import *
from .nodes.primitive_node import *
from .nodes.image_info import *
from .nodes.latent_node import *

NODE_CONFIG = {

    ###########################文本节点#######################
    "NCEUtilsShowText": {
        "class": NCEUtilsShowText,
        "name": "展示文本",
        "category": "🐍 NCE/文本"
    },
    "NCEUtilsMultilineText":{
        "class": NCEUtilsMultilineText,
        "name": "多行文本",
        "category": "🐍 NCE/文本"
    },
    "NCEMergeTexts":{
        "class": NCEMergeTexts,
        "name": "合并字符串",
        "category": "🐍 NCE/文本"
    },
    "NCEListToString": {
        "class": NCEListToString,
        "name": "列表转字符串",
        "category": "🐍 NCE/文本"
    },
    "NCEStringToList": {
        "class": NCEStringToList,
        "name": "字符串转列表",
        "category": "🐍 NCE/文本"
    },
    ###########################图像节点#######################
    "NCEUtilsSaveImagePlus": {
        "class": NCEUtilsSaveImagePlus,
        "name": "保存图像+",
        "category": "🐍 NCE/图像"
    },
    "NCEEncodeBlindWaterMark": {
        "class": NCEEncodeBlindWaterMark,
        "name": "图像写入不可见水印",
        "category": "🐍 NCE/图像"
    },
    "NCEDecodeBlindWaterMark": {
        "class": NCEDecodeBlindWaterMark,
        "name": "提取图像中不可见水印",
        "category": "🐍 NCE/图像"
    },
    "NCECropFace":{
        "class": NCECropFace,
        "name": "人脸识别剪切",
        "category": "🐍 NCE/图像"
    },
    "NCETextOnImage":{
        "class": NCETextOnImage,
        "name": "图片上写文字",
        "category": "🐍 NCE/图像"
    },
    "NCEImageScaleByAspectRatio": {
        "class": NCEImageScaleByAspectRatio,
        "name": "按宽高比缩放图像",
        "category": "🐍 NCE/图像"
    },
    "NCEGetImageSize": {
        "class": NCEGetImageSize,
        "name": "获取图像尺寸",
        "category": "🐍 NCE/图像"
    },
    "NCELatentPresetResolution": {
        "class": NCELatentPresetResolution,
        "name": "预设分辨率 (Latent)",
        "category": "🐍 NCE/图像"
    },
    "NCEImageComparer": {
        "class": NCEImageComparer,
        "name": "图像对比",
       "category": "🐍 NCE/图像"
    },
    ###########################音频节点#######################
    "NCEGetAudioInfo": {
        "class": NCEGetAudioInfo,
        "name": "获取音频信息",
        "category": "🐍 NCE/音频"
    },
    "NCEUtilsPlaySound": {
        "class": NCEUtilsPlaySound,
        "name": "播放声音",
        "category": "🐍 NCE/音频"
    },
    ###########################逻辑节点#######################
    "NCEShowAnything": {
        "class": NCEShowAnything,
        "name": "显示任意类型",
        "category": "🐍 NCE/逻辑"
    },
    ###########################基础节点#######################
    "NCEIntConstant": {
        "class": NCEIntConstant,
        "name": "整数常量",
        "category": "🐍 NCE/基础"
    },
    "NCEFloatConstant": {
        "class": NCEFloatConstant,
        "name": "浮点数常量",
        "category": "🐍 NCE/基础"
    }
}

def generate_node_mappings(node_config):
    node_class_mappings = {}
    node_display_name_mappings = {}

    for node_name, node_info in node_config.items():
        node_class = node_info["class"]
        node_class_mappings[node_name] = node_class
        node_display_name_mappings[node_name] = node_info.get("name", node_class.__name__)
        
        # 如果配置中指定了分类,覆盖节点类的 CATEGORY
        if "category" in node_info:
            node_class.CATEGORY = node_info["category"]

    return node_class_mappings, node_display_name_mappings

NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = generate_node_mappings(NODE_CONFIG)
WEB_DIRECTORY = "./js"


__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

NCE_BANNER = r"""
 _  _  ____ _____   _  _ _____ _____ _     ____ 
| \| |/ ___| ____| | || |_   _|_   _| |   / ___|
| .` | |   |  _|   | || | | |   | | | |   \___ \
|_|\_|_|   |_____|  \__/  |_|   |_| |____|____/
"""
print(NCE_BANNER)
print('[NCE Utils] Loaded')



