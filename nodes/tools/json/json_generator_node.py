import json
from typing import Union

class JSONGeneratorNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key_value_pairs": ("STRING", {"multiline": True}),
                "is_array": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("generated_json",)
    FUNCTION = "generate_json"
    CATEGORY = "utils"

    def generate_json(self, key_value_pairs: str, is_array: bool) -> tuple[str]:
        try:
            pairs = [line.strip() for line in key_value_pairs.split('\n') if line.strip()]
            
            if is_array:
                result = []
                for item in pairs:
                    try:
                        result.append(json.loads(item))
                    except json.JSONDecodeError:
                        result.append(item)
            else:
                result = {}
                for pair in pairs:
                    if ':' not in pair:
                        raise ValueError(f"Invalid key-value pair: {pair}")
                    
                    key, value = pair.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                        
                    result[key] = value
                    
            return (json.dumps(result, indent=2),)
        except Exception as e:
            raise ValueError(f"Error generating JSON: {str(e)}")
