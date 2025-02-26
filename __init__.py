from .nodes.text_node import *
from .nodes.image_node import *
from .nodes.video_style_generator import *

NODE_CONFIG = {
    "NCEUtilsShowText": {
        "class": NCEUtilsShowText,
        "name": "展示文本"
    },
    "NCEUtilsMultilineText":{
        "class": NCEUtilsMultilineText,
        "name": "多行文本"  
    },
    "NCEVideoStylerGenerator": {
        "class": NCEVideoStylerGenerator,
        "name": "视频风格生成器"  
    },

    "NCEUtilsSaveImagePlus": {
        "class": NCEUtilsSaveImagePlus,
        "name": "保存图像+",
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



