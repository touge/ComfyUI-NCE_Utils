import config
import random
import re

CATEGORY = "🐍 NCE/Utils"

#合并字符串
class NCEMergeTexts:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("OUTPUT",)
    FUNCTION = "process"
    CATEGORY = CATEGORY

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "merge_string": ("STRING", {"default": ""}),
                "input_1": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "",
                        "forceInput": True
                    },
                ),
            },
        }

    def process(self,**kwargs,):
        merged_text = ""
        sep = kwargs["merge_string"].replace("\\n", "\n")
        del kwargs["merge_string"]

        inputs = [value for value in kwargs.values()]

        merged_text = sep.join(inputs)
        return (merged_text.strip(),)
    
# 多行文本输入
class NCEUtilsMultilineText:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": (
                    "STRING",
                    {
                        "multiline": True,
                        "dynamicPrompts": False,
                    },
                ),
                "enable_dynamic": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "label_on": "开启动态解析 {a|b}",
                        "label_off": "关闭 (原样输出/支持JSON)",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = CATEGORY

    def generate(self, text, enable_dynamic=False):
        if not enable_dynamic or not text:
            return (text,)

        pattern = re.compile(r"\{([^{}]+)\}")
        result = text
        while True:
            match = pattern.search(result)
            if not match:
                break
            options = match.group(1).split("|")
            choice = random.choice(options)
            result = result[: match.start()] + choice + result[match.end() :]

        return (result,)
  
  
class NCEUtilsShowText:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    INPUT_IS_LIST = True
    RETURN_NAMES = ("string",)
    RETURN_TYPES = ("STRING",)
    FUNCTION = "process"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)

    # CATEGORY = config.CATEGORY_NAME
    CATEGORY = CATEGORY

    def process(self, text, unique_id=None, extra_pnginfo=None):
        if unique_id is not None and extra_pnginfo is not None:
            if not isinstance(extra_pnginfo, list):
                print("Error: extra_pnginfo is not a list")
            elif (
                not isinstance(extra_pnginfo[0], dict)
                or "workflow" not in extra_pnginfo[0]
            ):
                print("Error: extra_pnginfo[0] is not a dict or missing 'workflow' key")
            else:
                workflow = extra_pnginfo[0]["workflow"]
                node = next(
                    (x for x in workflow["nodes"] if str(x["id"]) == str(unique_id[0])),
                    None,
                )
                if node:
                    node["widgets_values"] = [text]
        return {"ui": {"text": text}, "result": (text,)}


# 列表转字符串
class NCEListToString:
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "list": ("STRING", {"forceInput": True}),
            },
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    OUTPUT_NODE = True
    FUNCTION = "make_list"
    CATEGORY = CATEGORY

    def make_list(self, list):
        if len(list) == 0:
            print("Error in List Variable")
            return ("",)

        file_string_list = '\n'.join(list)

        return (file_string_list,)


# 字符串转列表
class NCEStringToList:
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string": ("STRING", {"forceInput": True}),
                "remove_empty_lines": ("BOOLEAN", {"default": True, "forceInput": False}),
            },
        }

    # INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("list",)
    OUTPUT_IS_LIST = (True,)
    OUTPUT_NODE = True
    FUNCTION = "make_list"
    CATEGORY = CATEGORY

    def make_list(self, string, remove_empty_lines=True):
        if len(string) == 0:
            print("Error in string Variable")
            return ("",)

        file_paths = string.split('\n')
        
        # 如果选中去除空行选项，则过滤掉空字符串
        if remove_empty_lines:
            file_paths = [line for line in file_paths if line.strip()]

        return (file_paths,)

