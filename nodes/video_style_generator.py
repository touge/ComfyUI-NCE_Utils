import os
import json
import pathlib
from collections import defaultdict


CATEGORY = "🐍 NCE/Utils"
NCE_UTILS_NODE_PATH = pathlib.Path(__file__).parent.parent
STYLE_DATA_PATH = os.path.join(NCE_UTILS_NODE_PATH, "data", "video_styles")

class Template:
    def __init__(self, prompt, negative_prompt, **kwargs):
        self.prompt = prompt
        self.negative_prompt = negative_prompt

    def replace_prompts(self, positive_prompt, negative_prompt):
        positive_result = self.prompt.replace('{prompt}', positive_prompt)
        negative_result = ', '.join(x for x in (self.negative_prompt, negative_prompt) if x)
        return positive_result, negative_result

class StylerData:
    def __init__(self, datadir=None):
        self._data = defaultdict(dict)
        if datadir is None:
            datadir = pathlib.Path(__file__).parent.parent / 'data/video_styles'

        # print(f"data dir:{datadir}")

        # Add "None" option to each category
        none_template = Template("", "")
        
        for j in datadir.glob('*.json'):
            try:
                with j.open('r') as f:
                    content = json.load(f)
                    # print(f"content:{content}")
                    # group_name = f.name[0]  # 去掉文件后缀名
                    # group_name = os.path.splitext(os.path.basename(f.name))[0]

                    group = os.path.splitext(os.path.basename(f.name))[0]
                    # print(f"group:{group_name}")

                    # Add None as first option
                    self._data[group]["None"] = none_template

                    # Add all other templates
                    for template in content:
                        # print(f"template:{template}")
                        self._data[group][template['name']] = Template(**template)
            except Exception as e:
                print(f"Warning: Error loading {j}: {e}")

    def __getitem__(self, item):
        return self._data[item]

    def keys(self):
        return self._data.keys()

styler_data = StylerData()

class NCEVideoStylerGenerator:
    # Class attributes for ComfyUI
    RETURN_TYPES = ('STRING', )
    # RETURN_TYPES = ('STRING', 'STRING',)
    RETURN_NAMES = ('text_positive',)
    FUNCTION = 'process'
    CATEGORY = CATEGORY
    
    style_order = [
        'movie_scenes',    # 1. 电影场景 Base movie scene reference
        'timeofday',       # 2. 时间 Base environment - time
        'weather',         # 3. 天气 Base environment - conditions
        'lighting',        # 4. 光照 Light setup
        'shooting',        # 5. 拍摄风格 Basic shooting approach
        'camera',          # 6. 相机 Camera specifics
        'composition',     # 7. 构成规则 Composition rules
        'effects',         # 8. 特殊效果 Special effects
        'video_styles',    # 9. 整体风格 Overall style
        'cinematic_color'  # 10. 色彩风格 Color styles
    ]
    
    @classmethod
    def INPUT_TYPES(cls):

        menus = {}
        # Create menu options with "None" as first choice
        for menu in cls.style_order:
            options = list(styler_data[menu].keys())
            if "None" in options:
                options.remove("None")
                options = ["None"] + sorted(options)
            menus[menu] = (options,)

        return {
            "required": {
                "text_positive": ("STRING", {"default": "", "multiline": True}),
                # "text_negative": ("STRING", {"default": "", "multiline": True}),
                **menus,
                # "debug_prompt": ("BOOLEAN", {"default": False, "label": "Show Prompt Building"})
            }
        }

    # def process(self, text_positive, text_negative, debug_prompt, **kwargs):
    def process(self, text_positive, **kwargs):
        positive_result = text_positive
        # negative_result = print
        negative_result = ""
        
        for menu in self.style_order:
            if menu in kwargs and kwargs[menu] and kwargs[menu] != "None":
                style = styler_data[menu][kwargs[menu]]
                positive_result, negative_result = style.replace_prompts(
                    positive_result, negative_result
                )
        # return (positive_result, negative_result)
        return (positive_result, )