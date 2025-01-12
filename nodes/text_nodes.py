
# COSYVOICE_NODE_DIR        = os.path.dirname(os.path.abspath(__file__))

CATEGORY             = "🐍 NCE/Utils"

# 多行文本输入
class NCEUtilsText:
  @classmethod
  def INPUT_TYPES(s):
    return {"required": {"text": ("STRING", {
       "multiline": True, 
       "dynamicPrompts": True
      })}}


  RETURN_TYPES = ("STRING",)
  RETURN_NAMES = ("text",)  
  FUNCTION = "generate"
  CATEGORY = CATEGORY

  def generate(self,text):
    return (text, )

