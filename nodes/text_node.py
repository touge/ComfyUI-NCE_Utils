import os
import re
import folder_paths
import config

from pathlib import Path

# 多行文本输入
class NCEUtilsMultilineText:
  @classmethod
  def INPUT_TYPES(s):
    return {"required": {"text": ("STRING", {
       "multiline": True, 
       "dynamicPrompts": True
      })}}


  RETURN_TYPES = ("STRING",)
  RETURN_NAMES = ("text",)  
  FUNCTION = "generate"
  CATEGORY = config.CATEGORY_NAME

  def generate(self,text):
    return (text, )
  
  
class ShowText:
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
    RETURN_TYPES = ("STRING",)
    FUNCTION = "process"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)

    CATEGORY = config.CATEGORY_NAME

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