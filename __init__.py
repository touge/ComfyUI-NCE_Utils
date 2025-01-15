from .nodes.text_node import *
from .nodes.separation import *
from .nodes.video_style_generator import *

NODE_CONFIG = {
    "ShowText|pysssss": {
        "class": ShowText,
        "ShowText|pysssss": "ShowText"
    },
    "NCEUtilsMultilineText":{
        "class": NCEUtilsMultilineText,
        "name": "Multiline Text"  
    },

    "NCEAudioSeparation":{
        "class": NCEAudioSeparation,
        "name": "Separation of voices"  
    },

    "NCEVideoStylerGenerator": {
        "class": NCEVideoStylerGenerator,
        "name": "Video Style Generator"  
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
WEB_DIRECTORY = "./web"


__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

print('🐍 NCE Utils Loaded')



