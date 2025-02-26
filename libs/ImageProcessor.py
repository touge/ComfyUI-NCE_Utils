from PIL import Image
import torch
import numpy as np

import os
import shutil
import math
from blind_watermark import WaterMark

import folder_paths
from ..libs.utils import generate_random_name,log

class ImageProcessor:
    # 类属性 CATEGORY
    CATEGORY = "Image Processing"

    @staticmethod
    def image_channel_split(image: Image, mode='RGBA') -> tuple:        
        # 将输入图像转换为指定模式，并分离图像通道
        _image = image.convert('RGBA')
        channel1 = Image.new('L', size=_image.size, color='black')
        channel2 = Image.new('L', size=_image.size, color='black')
        channel3 = Image.new('L', size=_image.size, color='black')
        channel4 = Image.new('L', size=_image.size, color='black')
        if mode == 'RGBA':
            channel1, channel2, channel3, channel4 = _image.split()
        elif mode == 'RGB':
            channel1, channel2, channel3 = _image.convert('RGB').split()
        elif mode == 'YCbCr':
            channel1, channel2, channel3 = _image.convert('YCbCr').split()
        elif mode == 'LAB':
            channel1, channel2, channel3 = _image.convert('LAB').split()
        elif mode == 'HSV':
            channel1, channel2, channel3 = _image.convert('HSV').split()
        return channel1, channel2, channel3, channel4

    @staticmethod
    def image_channel_merge(channels: tuple, mode='RGB') -> Image:        
        # 将输入的通道图像合并为指定模式的图像
        channel1 = channels[0].convert('L')
        channel2 = channels[1].convert('L')
        channel3 = channels[2].convert('L')
        channel4 = Image.new('L', size=channel1.size, color='white')
        if mode == 'RGBA':
            if len(channels) > 3:
                channel4 = channels[3].convert('L')
            ret_image = Image.merge('RGBA', [channel1, channel2, channel3, channel4])
        elif mode == 'RGB':
            ret_image = Image.merge('RGB', [channel1, channel2, channel3])
        elif mode == 'YCbCr':
            ret_image = Image.merge('YCbCr', [channel1, channel2, channel3]).convert('RGB')
        elif mode == 'LAB':
            ret_image = Image.merge('LAB', [channel1, channel2, channel3]).convert('RGB')
        elif mode == 'HSV':
            ret_image = Image.merge('HSV', [channel1, channel2, channel3]).convert('RGB')
        return ret_image

    @staticmethod
    def RGB2RGBA(image: Image, mask: Image) -> Image:        
        # 将输入的图像和遮罩转换为RGBA格式
        (R, G, B) = image.convert('RGB').split()
        return Image.merge('RGBA', (R, G, B, mask.convert('L')))

    @staticmethod
    def watermark_image_size(image: Image) -> int:
        # 根据图像的宽度和高度，计算水印的大小
        size = int(math.sqrt(image.width * image.height * 0.015625) * 0.9)
        return size

    @staticmethod
    def add_invisible_watermark(image: Image, watermark_image: Image) -> Image:
        """
        Adds an invisible watermark to an image.
        """        
        orig_image_mode = image.mode
        temp_dir = os.path.join(folder_paths.get_temp_directory(), generate_random_name('_watermark_', '_temp', 16))
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        image_dir = os.path.join(temp_dir, 'image')
        wm_dir = os.path.join(temp_dir, 'wm')
        result_dir = os.path.join(temp_dir, 'result')

        try:
            os.makedirs(image_dir)
            os.makedirs(wm_dir)
            os.makedirs(result_dir)
        except Exception as e:
            log(f"Error: {ImageProcessor.CATEGORY} skipped, because unable to create temporary folder.", message_type='error')
            return image

        image_file_name = os.path.join(generate_random_name('watermark_orig_', '_temp', 16) + '.png')
        wm_file_name = os.path.join(generate_random_name('watermark_image_', '_temp', 16) + '.png')
        output_file_name = os.path.join(generate_random_name('watermark_output_', '_temp', 16) + '.png')

        try:
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.save(os.path.join(image_dir, image_file_name))
            watermark_image.save(os.path.join(wm_dir, wm_file_name))
        except IOError as e:
            log(f"Error: {ImageProcessor.CATEGORY} skipped, because unable to create temporary file.", message_type='error')
            return image

        bwm1 = WaterMark(password_img=1, password_wm=1)
        bwm1.read_img(os.path.join(image_dir, image_file_name))
        bwm1.read_wm(os.path.join(wm_dir, wm_file_name))
        output_image = os.path.join(result_dir, output_file_name)
        bwm1.embed(output_image, compression_ratio=100)

        return Image.open(output_image).convert(orig_image_mode)

    @staticmethod
    def tensor2pil(t_image: torch.Tensor)  -> Image:
        return Image.fromarray(np.clip(255.0 * t_image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))
    
    @staticmethod
    def pil2tensor(image: Image) -> torch.Tensor:
        # 将PIL图像转换为Tensor
        return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)
        
    @staticmethod
    def decode_watermark(image: Image, watermark_image_size: int = 94) -> Image:
        temp_dir = os.path.join(folder_paths.get_temp_directory(), generate_random_name('_watermark_', '_temp', 16))
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        image_dir = os.path.join(temp_dir, 'decode_image')
        result_dir = os.path.join(temp_dir, 'decode_result')

        try:
            os.makedirs(image_dir)
            os.makedirs(result_dir)
        except Exception as e:
            log(f"Error: {ImageProcessor.CATEGORY} skipped, because unable to create temporary folder.", message_type='error')
            return image

        image_file_name = os.path.join(generate_random_name('watermark_decode_', '_temp', 16) + '.png')
        output_file_name = os.path.join(generate_random_name('watermark_decode_output_', '_temp', 16) + '.png')

        try:
            image.save(os.path.join(image_dir, image_file_name))
        except IOError as e:
            log(f"Error: {ImageProcessor.CATEGORY} skipped, because unable to create temporary file.", message_type='error')
            return image

        bwm1 = WaterMark(password_img=1, password_wm=1)
        decode_image = os.path.join(image_dir, image_file_name)
        output_image = os.path.join(result_dir, output_file_name)

        try:
            bwm1.extract(filename=decode_image, wm_shape=(watermark_image_size, watermark_image_size),
                         out_wm_name=os.path.join(output_image))
            ret_image = Image.open(output_image)
        except Exception as e:
            log(f"blind watermark extract fail, {e}")
            ret_image = Image.new("RGB", (64, 64), color="black")
        ret_image = ImageProcessor.normalize_gray(ret_image)
        return ret_image
    
    @staticmethod
    def normalize_gray(image: Image) -> Image:
        # 对灰度图像进行直方图均衡化
        if image.mode != 'L':
            image = image.convert('L')
        img = np.asarray(image)
        balanced_img = img.copy()
        hist, bins = np.histogram(img.reshape(-1), 256, (0, 256))
        bmin = np.min(np.where(hist > (hist.sum() * 0.0005)))
        bmax = np.max(np.where(hist > (hist.sum() * 0.0005)))
        balanced_img = np.clip(img, bmin, bmax)
        balanced_img = ((balanced_img - bmin) / (bmax - bmin) * 255)
        return Image.fromarray(balanced_img).convert('L')
