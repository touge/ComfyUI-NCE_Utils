"""
基础类型常量节点
提供 INT 和 FLOAT 常量输入
"""

CATEGORY = "🐍 NCE/Utils"


class NCEIntConstant:
    """整数常量节点"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": ("INT", {
                    "default": 0, 
                    "min": -0xffffffffffffffff, 
                    "max": 0xffffffffffffffff
                }),
            },
        }
    
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_value"
    CATEGORY = CATEGORY

    def get_value(self, value):
        return (value,)


class NCEFloatConstant:
    """浮点数常量节点 - 显示两位小数"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": ("FLOAT", {
                    "default": 0.0, 
                    "min": -0xffffffffffffffff, 
                    "max": 0xffffffffffffffff, 
                    "step": 0.01,  # 步进0.01,显示两位小数
                    "round": 0.01  # 四舍五入到两位小数
                }),
            },
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_value"
    CATEGORY = CATEGORY

    def get_value(self, value):
        # 返回保留两位小数的值
        return (round(value, 2),)
