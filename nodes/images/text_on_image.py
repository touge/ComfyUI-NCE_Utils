import os
from PIL import Image, ImageDraw, ImageFont, ImageChops
import numpy as np
import torch
import logging
import comfy.model_management as mm
from ...libs.utils import node_path

CATEGORY = "🐍 NCE/图像"


class NCETextOnImage:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        font_dir = os.path.join(node_path(), "font")
        if not os.path.exists(font_dir):
            font_dir = os.path.join(os.path.dirname(__file__), "font")
        font_files = [f for f in os.listdir(font_dir) if f.endswith(('.ttc', '.ttf', '.otf'))] if os.path.exists(font_dir) else []
        if not font_files:
            font_files = ["default"]

        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "image": ("IMAGE",),
                "x": ("INT", {"default": 0, "min": -4096, "max": 4096, "step": 1}),
                "y": ("INT", {"default": 0, "min": -4096, "max": 4096, "step": 1}),

                "font_size": ("INT", {"default": 40, "min": 1, "max": 320, "step": 1}),
                "line_spacing": ("INT", {"default": 10, "min": 0, "max": 200, "step": 1}),
                "align": (["left", "center", "right"], {"default": "left"}),

                "horizontal_align": (["left", "center", "right"], {"default": "left"}),
                "vertical_align": (["top", "middle", "bottom"], {"default": "top"}),

                "text_color": ("STRING", {"default": "#ffffff"}),
                "text_opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "stroke_width": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
                "stroke_color": ("STRING", {"default": "#000000"}),
                "stroke_opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "shadow_x": ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                "shadow_y": ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                "shadow_color": ("STRING", {"default": "#000000"}),
                "shadow_opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "font_file": (font_files, {"default": font_files[0]}),

                # -------------------------
                # Multiply 黑条 + 渐隐
                # -------------------------
                "text_bg_top": ("INT", {"default": 800, "min": -2000, "max": 4000, "step": 1}),
                "text_bg_height": ("INT", {"default": 400, "min": 10, "max": 4000, "step": 1}),
                "text_bg_opacity": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01}),
                "text_bg_fade_top": ("INT", {"default": 80, "min": 0, "max": 2000, "step": 1}),
                "text_bg_fade_bottom": ("INT", {"default": 80, "min": 0, "max": 2000, "step": 1}),

                "cleanup_mode": (
                    ["soft", "medium", "full"],
                    {"default": "soft"}
                ),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_text"
    CATEGORY = CATEGORY

    # -------------------------
    # 工具方法
    # -------------------------

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _compute_horizontal_offset(self, img_width, block_width, x_offset, mode):
        if mode == "left":
            return x_offset
        elif mode == "center":
            return (img_width - block_width) // 2 + x_offset
        elif mode == "right":
            return img_width - block_width + x_offset

    def _compute_vertical_offset(self, img_height, block_height, y_offset, mode):
        if mode == "top":
            return y_offset
        elif mode == "middle":
            return (img_height - block_height) // 2 + y_offset
        elif mode == "bottom":
            return img_height - block_height + y_offset

    # -------------------------
    # Multiply 黑条 + 上下渐隐
    # -------------------------

    def _apply_multiply_black_strip(self, base_img, top, height, opacity, fade_top, fade_bottom):
        img_width, img_height = base_img.size

        # 取出底图对应区域
        region = base_img.crop((0, top, img_width, top + height)).convert("RGB")

        # 创建纯黑层
        black_layer = Image.new("RGB", (img_width, height), (0, 0, 0))

        # Multiply 混合（纯黑，不发灰）
        multiplied = ImageChops.multiply(region, black_layer)

        # 创建渐隐 mask
        mask = Image.new("L", (img_width, height), 255)
        mp = mask.load()

        for y in range(height):
            if y < fade_top:
                alpha = int(255 * (y / fade_top))
            elif y > height - fade_bottom:
                alpha = int(255 * ((height - y) / fade_bottom))
            else:
                alpha = 255

            alpha = int(alpha * opacity)

            for x in range(img_width):
                mp[x, y] = alpha

        # 混合
        final = Image.composite(multiplied, region, mask)

        # 贴回去
        base_img.paste(final, (0, top))

    # -------------------------
    # 主逻辑
    # -------------------------

    def apply_text(self, text, image, x, y, font_size, line_spacing, align,
                  text_color, text_opacity, stroke_width, stroke_color, stroke_opacity,
                  shadow_x, shadow_y, shadow_color, shadow_opacity, font_file,
                  text_bg_top, text_bg_height, text_bg_opacity, text_bg_fade_top, text_bg_fade_bottom,
                  cleanup_mode, horizontal_align, vertical_align):

        if text.strip() == "":
            return (image,)

        # 转换图像
        img = image[0].cpu().numpy()
        img = (img * 255).astype(np.uint8)
        base_img = Image.fromarray(img).convert('RGBA')
        img_width, img_height = base_img.size

        # 加载字体
        font_dir = os.path.join(node_path(), "font")
        if not os.path.exists(font_dir):
            font_dir = os.path.join(os.path.dirname(__file__), "font")
        font_path = os.path.join(font_dir, font_file)
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        # 颜色
        text_color_rgb = self.hex_to_rgb(text_color)
        stroke_color_rgb = self.hex_to_rgb(stroke_color)
        shadow_color_rgb = None if shadow_color == "none" else self.hex_to_rgb(shadow_color)

        # 多行处理
        lines = text.split("\n")

        temp_img = Image.new("RGBA", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)

        line_sizes = []
        max_width = 0
        total_height = 0

        for line in lines:
            bbox = temp_draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            line_sizes.append((w, h))
            max_width = max(max_width, w)
            total_height += h + line_spacing

        total_height -= line_spacing

        # 文字块画布
        canvas = Image.new("RGBA", (max_width + 200, total_height + 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        current_y = 0
        for idx, line in enumerate(lines):
            w, h = line_sizes[idx]

            if align == "left":
                line_x = 0
            elif align == "center":
                line_x = (max_width - w) // 2
            else:
                line_x = max_width - w

            if shadow_color_rgb and (shadow_x != 0 or shadow_y != 0):
                draw.text((line_x + shadow_x, current_y + shadow_y), line, font=font,
                          fill=shadow_color_rgb + (int(255 * shadow_opacity),))

            if stroke_width > 0:
                for dx in range(-stroke_width, stroke_width + 1):
                    for dy in range(-stroke_width, stroke_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((line_x + dx, current_y + dy), line, font=font,
                                      fill=stroke_color_rgb + (int(255 * stroke_opacity),))

            draw.text((line_x, current_y), line, font=font,
                      fill=text_color_rgb + (int(255 * text_opacity),))

            current_y += h + line_spacing

        # 计算文字位置
        final_x = self._compute_horizontal_offset(img_width, canvas.width, x, horizontal_align)
        final_y = self._compute_vertical_offset(img_height, canvas.height, y, vertical_align)

        # -------------------------
        # Multiply 黑条 + 渐隐
        # -------------------------
        self._apply_multiply_black_strip(
            base_img,
            text_bg_top,
            text_bg_height,
            text_bg_opacity,
            text_bg_fade_top,
            text_bg_fade_bottom
        )

        # 粘贴文字
        base_img.paste(canvas, (final_x, final_y), canvas)

        # 转回 tensor
        out = np.array(base_img).astype(np.float32) / 255.0
        out = torch.from_numpy(out)[None,]

        # 清理
        try:
            if cleanup_mode == "soft":
                mm.soft_empty_cache()
            elif cleanup_mode == "medium":
                mm.soft_empty_cache()
                mm.cleanup()
            elif cleanup_mode == "full":
                mm.unload_all_models()
                mm.cleanup()
        except Exception as e:
            logging.warning(f"Cleanup failed: {e}")

        return (out,)
