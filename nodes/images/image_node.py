import os.path
import shutil
from PIL.PngImagePlugin import PngInfo
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json
import datetime
import folder_paths
import torch
from comfy import model_management
from torchvision.transforms.functional import normalize
import cv2
import logging
import math

from ...libs.utils import log, generate_random_name, node_path
from ...libs.ImageProcessor import ImageProcessor
from ...libs.face_restoration_helper import FaceRestoreHelper

from ...libs.utils import img2tensor, tensor2img

CATEGORY = "🐍 NCE/Utils"

class NCECropFace:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "image": ("IMAGE",),
                "facedetection": (["retinaface_resnet50", "retinaface_mobile0.25", "YOLOv5l", "YOLOv5n"],)
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "crop_face"
    CATEGORY = CATEGORY

    def __init__(self):
        self.face_helper = None

    def crop_face(self, image, facedetection):
        device = model_management.get_torch_device()
        if self.face_helper is None:
            self.face_helper = FaceRestoreHelper(1, face_size=512, crop_ratio=(1, 1), det_model=facedetection, save_ext='png', use_parse=True, device=device)

        image_np = 255. * image.cpu().numpy()

        total_images = image_np.shape[0]
        out_images = np.ndarray(shape=(total_images, 512, 512, 3))
        next_idx = 0

        for i in range(total_images):

            cur_image_np = image_np[i,:, :, ::-1]

            original_resolution = cur_image_np.shape[0:2]

            if self.face_helper is None:
                return image

            self.face_helper.clean_all()
            self.face_helper.read_image(cur_image_np)
            self.face_helper.get_face_landmarks_5(only_center_face=False, resize=640, eye_dist_threshold=5)
            self.face_helper.align_warp_face()

            faces_found = len(self.face_helper.cropped_faces)
            if faces_found == 0:
                next_idx += 1 # output black image for no face
            if out_images.shape[0] < next_idx + faces_found:
                print(out_images.shape)
                print((next_idx + faces_found, 512, 512, 3))
                print('aaaaa')
                out_images = np.resize(out_images, (next_idx + faces_found, 512, 512, 3))
                print(out_images.shape)
            for j in range(faces_found):
                cropped_face_1 = self.face_helper.cropped_faces[j]
                cropped_face_2 = img2tensor(cropped_face_1 / 255., bgr2rgb=True, float32=True)
                normalize(cropped_face_2, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=True)
                cropped_face_3 = cropped_face_2.unsqueeze(0).to(device)
                cropped_face_4 = tensor2img(cropped_face_3, rgb2bgr=True, min_max=(-1, 1)).astype('uint8')
                cropped_face_5 = cv2.cvtColor(cropped_face_4, cv2.COLOR_BGR2RGB)
                out_images[next_idx] = cropped_face_5
                next_idx += 1

        cropped_face_6 = np.array(out_images).astype(np.float32) / 255.0
        cropped_face_7 = torch.from_numpy(cropped_face_6)
        return (cropped_face_7,)
    

class NCEEncodeBlindWaterMark:
    #将不可见水印嵌入到图像中
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE", ),  #
                "watermark_image": ("IMAGE",),  #
            },
            "optional": {
            }
        }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = 'watermark_encode'
    CATEGORY = CATEGORY

    def watermark_encode(self, image, watermark_image):
        l_images = []
        w_images = []
        ret_images = []

        for l in image:
            l_images.append(torch.unsqueeze(l, 0))
        for w in watermark_image:
            w_images.append(torch.unsqueeze(w, 0))

        for i in range(len(l_images)):
            _image = ImageProcessor.tensor2pil(l_images[i])
            wm_size = ImageProcessor.watermark_image_size(_image)
            _wm_image = w_images[i] if i < len(w_images) else w_images[-1]
            _wm_image = ImageProcessor.tensor2pil(_wm_image)
            _wm_image = _wm_image.resize((wm_size, wm_size), Image.LANCZOS)
            _wm_image = _wm_image.convert("L")

            y, u, v, _ = ImageProcessor.image_channel_split(_image, mode='YCbCr')
            _u = ImageProcessor.add_invisible_watermark(u, _wm_image)
            ret_image = ImageProcessor.image_channel_merge((y, _u, v), mode='YCbCr')

            if _image.mode == "RGBA":
                ret_image = ImageProcessor.RGB2RGBA(ret_image, _image.split()[-1])
            ret_images.append(ImageProcessor.pil2tensor(ret_image))

        # log(f"{CATEGORY} Processed {len(ret_images)} image(s).", message_type='finish')
        return (torch.cat(ret_images, dim=0),)
    
class NCEDecodeBlindWaterMark:
    #从带有不可见水印的图像中提取水印信息
    @classmethod
    def INPUT_TYPES(self):

        return {
            "required": {
                "image": ("IMAGE",),  #
            },
            "optional": {
            }
        }

    RETURN_TYPES = ("IMAGE", )
    RETURN_NAMES = ("watermark_image",)
    FUNCTION = 'watermark_decode'
    CATEGORY = CATEGORY

    def watermark_decode(self, image):

        NODE_NAME = 'Decode BlindWaterMark'

        ret_images = []

        for i in image:
            _image = torch.unsqueeze(i,0)
            _image = ImageProcessor.tensor2pil(_image)
            wm_size = ImageProcessor.watermark_image_size(_image)
            y, u, v, _ = ImageProcessor.image_channel_split(_image, mode='YCbCr')
            ret_image = ImageProcessor.decode_watermark(u, wm_size)
            ret_image = ret_image.resize((512, 512), Image.LANCZOS)
            ret_image = ImageProcessor.normalize_gray(ret_image)
            ret_images.append(ImageProcessor.pil2tensor(ret_image.convert('RGB')))

        # log(f"{CATEGORY} Processed {len(ret_images)} image(s).", message_type='finish')
        return (torch.cat(ret_images, dim=0), )
    

class NCEUtilsSaveImagePlus:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"images": ("IMAGE", ),
                     "custom_path": ("STRING", {"default": ""}),
                     "filename_prefix": ("STRING", {"default": "comfyui"}),
                     "timestamp": (["None", "second", "millisecond"],),
                     "format": (["png", "jpg"],),
                     "quality": ("INT", {"default": 80, "min": 10, "max": 100, "step": 1}),
                     "meta_data": ("BOOLEAN", {"default": False}),
                     "blind_watermark": ("STRING", {"default": ""}),
                     "save_workflow_as_json": ("BOOLEAN", {"default": False}),
                     "preview": ("BOOLEAN", {"default": True}),
                     },
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
                }

    RETURN_TYPES = ()
    FUNCTION = "save_image_plus"
    OUTPUT_NODE = True
    CATEGORY = CATEGORY

    def save_image_plus(self, images, custom_path, filename_prefix, timestamp, format, quality,
                           meta_data, blind_watermark, preview, save_workflow_as_json,
                           prompt=None, extra_pnginfo=None):
        
        ImageProcessor.CATEGORY = CATEGORY

        now = datetime.datetime.now()
        custom_path = custom_path.replace("%date", now.strftime("%Y-%m-%d"))
        custom_path = custom_path.replace("%time", now.strftime("%H-%M-%S"))
        filename_prefix = filename_prefix.replace("%date", now.strftime("%Y-%m-%d"))
        filename_prefix = filename_prefix.replace("%time", now.strftime("%H-%M-%S"))
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        temp_sub_dir = generate_random_name('_savepreview_', '_temp', 16)
        temp_dir = os.path.join(folder_paths.get_temp_directory(), temp_sub_dir)
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            if blind_watermark != "":
                img_mode = img.mode
                wm_size = ImageProcessor.watermark_image_size(img) #watermark_image_size(img)
                import qrcode
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=20,
                    border=1,
                )
                qr.add_data(blind_watermark.encode('utf-8'))
                qr.make(fit=True)
                qr_image = qr.make_image(fill_color="black", back_color="white")
                qr_image = qr_image.resize((wm_size, wm_size), Image.BICUBIC).convert("L")

                y, u, v, _ = ImageProcessor.image_channel_split(img, mode='YCbCr')
                _u = ImageProcessor.add_invisible_watermark(u, qr_image)
                wm_img = ImageProcessor.image_channel_merge((y, _u, v), mode='YCbCr')

                if img.mode == "RGBA":
                    img = ImageProcessor.RGB2RGBA(wm_img, img.split()[-1])
                else:
                    img = wm_img.convert(img_mode)

            metadata = None
            if meta_data:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            if timestamp == "millisecond":
                file = f'{filename}_{now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]}'
            elif timestamp == "second":
                file = f'{filename}_{now.strftime("%Y-%m-%d_%H-%M-%S")}'
            else:
                file = f'{filename}_{counter:05}'


            preview_filename = ""
            if custom_path != "":
                if not os.path.exists(custom_path):
                    try:
                        os.makedirs(custom_path)
                    except Exception as e:
                        log(f"Error: {CATEGORY} skipped, because unable to create temporary folder.",
                            message_type='warning')
                        raise FileNotFoundError(f"cannot create custom_path {custom_path}, {e}")

                full_output_folder = os.path.normpath(custom_path)
                # save preview image to temp_dir
                if os.path.isdir(temp_dir):
                    shutil.rmtree(temp_dir)
                try:
                    os.makedirs(temp_dir)
                except Exception as e:
                    print(e)
                    log(f"Error: {CATEGORY} skipped, because unable to create temporary folder.",
                        message_type='warning')
                try:
                    preview_filename = os.path.join(generate_random_name('saveimage_preview_', '_temp', 16) + '.png')
                    img.save(os.path.join(temp_dir, preview_filename))
                except Exception as e:
                    print(e)
                    log(f"Error: {CATEGORY} skipped, because unable to create temporary file.", message_type='warning')

            # check if file exists, change filename
            while os.path.isfile(os.path.join(full_output_folder, f"{file}.{format}")):
                counter += 1
                if timestamp == "millisecond":
                    file = f'{filename}_{now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]}_{counter:05}'
                elif timestamp == "second":
                    file = f'{filename}_{now.strftime("%Y-%m-%d_%H-%M-%S")}_{counter:05}'
                else:
                    file = f"{filename}_{counter:05}"

            image_file_name = os.path.join(full_output_folder, f"{file}.{format}")
            json_file_name = os.path.join(full_output_folder, f"{file}.json")

            if format == "png":
                img.save(image_file_name, pnginfo=metadata, compress_level= (100 - quality) // 10)
            else:
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                img.save(image_file_name, quality=quality)
            log(f"{CATEGORY} -> Saving image to {image_file_name}")

            if save_workflow_as_json:
                try:
                    workflow = (extra_pnginfo or {}).get('workflow')
                    if workflow is None:
                        log('No workflow found, skipping saving of JSON')
                    with open(f'{json_file_name}', 'w') as workflow_file:
                        json.dump(workflow, workflow_file)
                        log(f'Saved workflow to {json_file_name}')
                except Exception as e:
                    log(
                        f'Failed to save workflow as json due to: {e}, proceeding with the remainder of saving execution', message_type="warning")

            if preview:
                if custom_path == "":
                    results.append({
                        "filename": f"{file}.{format}",
                        "subfolder": subfolder,
                        "type": self.type
                    })
                else:
                    results.append({
                        "filename": preview_filename,
                        "subfolder": temp_sub_dir,
                        "type": "temp"
                    })

            counter += 1

        return { "ui": { "images": results } }

class NCETextOnImage:
    @classmethod
    def INPUT_TYPES(s):
        font_dir = os.path.join(node_path(), "font")
        font_files = [f for f in os.listdir(font_dir) if f.endswith(('.ttc', '.ttf'))]
        if not font_files:
            font_files = ["default"]

        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "image": ("IMAGE",),
                "x": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 1}),
                "y": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 1}),
                "font_size": ("INT", {"default": 12, "min": 0, "max": 320, "step": 1}),
                "text_color": ("STRING", {"default": "#ffffff"}),
                "text_opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "use_gradient": ("BOOLEAN", {"default": False}),
                "start_color": ("STRING", {"default": "#ff0000"}),
                "end_color": ("STRING", {"default": "#0000ff"}),
                "angle": ("INT", {"default": 0, "min": -180, "max": 180, "step": 1}),
                "stroke_width": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
                "stroke_color": ("STRING", {"default": "#000000"}),
                "stroke_opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "shadow_x": ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                "shadow_y": ("INT", {"default": 0, "min": -100, "max": 100, "step": 1}),
                "shadow_color": ("STRING", {"default": "#000000"}),
                "shadow_opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "font_file": (font_files, {"default": font_files[0]}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_text"
    CATEGORY = CATEGORY

    def hex_to_rgb(self, hex_color):
        """将 HEX 色值转换为 RGB 元组"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def create_gradient(self, width, height, start_color_rgb, end_color_rgb, angle):
        """创建渐变图像"""
        # 创建一个空白的 RGBA 图像
        gradient_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient_img)

        # 计算渐变方向
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        # 确定渐变方向上的投影长度
        proj_width = abs(width * cos_a) + abs(height * sin_a)
        proj_height = abs(width * sin_a) + abs(height * cos_a)
        length = max(proj_width, proj_height)

        if length == 0:
            length = 1  # 防止除以零

        # 遍历图像的每个像素，计算其在渐变方向上的投影位置
        for x in range(width):
            for y in range(height):
                # 计算当前点在渐变方向上的投影距离
                t = (x * cos_a + y * sin_a + length / 2) / length
                t = max(0, min(1, t))  # 限制 t 在 [0, 1] 范围内

                # 插值计算颜色
                r = int(start_color_rgb[0] + (end_color_rgb[0] - start_color_rgb[0]) * t)
                g = int(start_color_rgb[1] + (end_color_rgb[1] - start_color_rgb[1]) * t)
                b = int(start_color_rgb[2] + (end_color_rgb[2] - start_color_rgb[2]) * t)
                draw.point((x, y), fill=(r, g, b, 255))

        return gradient_img

    def apply_text(self, text, image, x, y, font_size, text_color, text_opacity,
                  stroke_width, stroke_color, stroke_opacity,
                  shadow_x, shadow_y, shadow_color, shadow_opacity,
                  font_file, use_gradient, start_color, end_color, angle):
        if text == "":
            logging.info("Text is empty, returning original image.")
            return (image,)

        # 将输入的 torch.Tensor 转换为 PIL 图像
        img = image[0].cpu().numpy()
        img = (img * 255).astype(np.uint8)
        base_img = Image.fromarray(img).convert('RGBA')
        img_width, img_height = base_img.size
        logging.info(f"Image size: {img_width}x{img_height}")

        # 构建字体文件路径
        font_dir = os.path.join(node_path(), "font")
        # font_dir = os.path.join(os.path.dirname(__file__), "font")
        font_path = os.path.join(font_dir, font_file)
        logging.info(f"Font path: {font_path}")

        # 加载字体
        try:
            font = ImageFont.truetype(font_path, font_size)
            logging.info(f"Font loaded successfully: {font_path}")
        except IOError as e:
            logging.warning(f"Failed to load font {font_path}: {e}, using default font.")
            font = ImageFont.load_default()

        # 转换颜色
        text_color_rgb = self.hex_to_rgb(text_color)
        stroke_color_rgb = self.hex_to_rgb(stroke_color)
        shadow_color_rgb = None if shadow_color == "none" else self.hex_to_rgb(shadow_color)
        start_color_rgb = self.hex_to_rgb(start_color)
        end_color_rgb = self.hex_to_rgb(end_color)

        # 使用 ImageDraw.textbbox 精确计算文字区域
        temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        text_bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # 增加安全高度
        safety_margin = font_size // 2
        text_height += safety_margin

        logging.info(f"Text dimensions: width={text_width}, height={text_height}")

        # 计算总padding（包括描边和投影）
        padding = max(stroke_width * 2, abs(shadow_x), abs(shadow_y))

        # 调整文字位置
        text_left = max(0, x - padding)
        text_top = max(0, y - padding)
        text_right = min(img_width, x + text_width + padding)
        text_bottom = min(img_height, y + text_height + padding)

        # 如果文字超出图像底部，向上调整
        if text_bottom > img_height:
            offset = text_bottom - img_height
            text_top = max(0, text_top - offset)
            text_bottom = img_height

        logging.info(f"Canvas bounds: left={text_left}, top={text_top}, right={text_right}, bottom={text_bottom}")

        # 创建文字层
        canvas_width = text_right - text_left
        canvas_height = text_bottom - text_top
        if canvas_width <= 0 or canvas_height <= 0:
            logging.warning("Canvas dimensions are invalid, returning original image.")
            return (image,)
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        canvas_draw = ImageDraw.Draw(canvas)
        logging.info(f"Canvas created: {canvas_width}x{canvas_height}")

        # 计算文字在画布中的相对位置（y 作为顶部位置）
        relative_x = x - text_left
        relative_y = y - text_top
        logging.info(f"Relative text position: x={relative_x}, y={relative_y}")

        # 绘制投影
        if shadow_color_rgb and (shadow_x != 0 or shadow_y != 0):
            try:
                shadow_pos = (relative_x + shadow_x, relative_y + shadow_y)
                canvas_draw.text(shadow_pos, text, font=font, 
                               fill=shadow_color_rgb + (int(255 * shadow_opacity),))
                logging.info("Shadow drawn successfully.")
            except Exception as e:
                logging.error(f"Failed to draw shadow: {e}")

        # 绘制描边
        if stroke_width > 0:
            try:
                for dx in range(-stroke_width, stroke_width + 1):
                    for dy in range(-stroke_width, stroke_width + 1):
                        if dx != 0 or dy != 0:
                            stroke_pos = (relative_x + dx, relative_y + dy)
                            canvas_draw.text(stroke_pos, text, font=font, 
                                           fill=stroke_color_rgb + (int(255 * stroke_opacity),))
                logging.info(f"Stroke drawn with width {stroke_width}.")
            except Exception as e:
                logging.error(f"Failed to draw stroke: {e}")

        # 绘制主文字
        try:
            if use_gradient:
                # 创建渐变图像
                gradient_img = self.create_gradient(text_width, text_height, start_color_rgb, end_color_rgb, angle)
                
                # 创建文字蒙版
                text_mask = Image.new('L', (text_width, text_height), 0)
                mask_draw = ImageDraw.Draw(text_mask)
                mask_draw.text((0, 0), text, font=font, fill=255)
                
                # 将渐变应用到文字上
                gradient_text = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
                gradient_text.paste(gradient_img, (0, 0), text_mask)
                
                # 应用透明度
                gradient_text_data = np.array(gradient_text)
                gradient_text_data[..., 3] = (gradient_text_data[..., 3] * text_opacity).astype(np.uint8)
                gradient_text = Image.fromarray(gradient_text_data)
                
                # 将渐变文字粘贴到画布上
                canvas.paste(gradient_text, (relative_x, relative_y), gradient_text)
            else:
                # 使用单一颜色绘制文字
                canvas_draw.text((relative_x, relative_y), text, font=font, 
                               fill=text_color_rgb + (int(255 * text_opacity),))
            logging.info("Main text drawn successfully.")
        except Exception as e:
            logging.error(f"Failed to draw main text: {e}")
            return (image,)

        # 将文字画布粘贴到主图像上
        try:
            base_img.paste(canvas, (text_left, text_top), canvas)
            logging.info("Canvas pasted to base image successfully.")
        except Exception as e:
            logging.error(f"Failed to paste canvas to base image: {e}")
            return (image,)

        # 将 PIL.Image 转换回 torch.Tensor
        img = np.array(base_img).astype(np.float32) / 255.0
        img = torch.from_numpy(img)[None,]
        logging.info("Image converted back to tensor.")

        return (img,)