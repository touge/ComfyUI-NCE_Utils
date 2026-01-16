import json

CATEGORY = "🐍 NCE/Logic"

# 定义 any_type,用于接受任意类型的输入
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any_type = AnyType("*")


# 显示任意类型
class NCEShowAnything:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {}, 
            "optional": {
                "anything": (any_type, {}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID", 
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ('output',)
    INPUT_IS_LIST = True
    OUTPUT_NODE = True
    FUNCTION = "log_input"
    CATEGORY = CATEGORY

    def log_input(self, unique_id=None, extra_pnginfo=None, **kwargs):
        values = []
        if "anything" in kwargs:
            for val in kwargs['anything']:
                try:
                    if isinstance(val, str):
                        values.append(val)
                    elif isinstance(val, (int, float, bool)):
                        values.append(str(val))
                    else:
                        val = json.dumps(val, indent=4)
                        values.append(str(val))
                except Exception:
                    values.append(str(val))
                    pass

        if not extra_pnginfo:
            pass
        elif (not isinstance(extra_pnginfo[0], dict) or "workflow" not in extra_pnginfo[0]):
            pass
        else:
            workflow = extra_pnginfo[0]["workflow"]
            node = next((x for x in workflow["nodes"] if str(x["id"]) == unique_id[0]), None)
            if node:
                node["widgets_values"] = [values]
        
        if isinstance(values, list) and len(values) == 1:
            return {"ui": {"text": values}, "result": (values[0],)}
        else:
            return {"ui": {"text": values}, "result": (values,)}
