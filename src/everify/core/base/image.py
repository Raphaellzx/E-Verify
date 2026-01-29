"""
图片处理引擎 - 提供图片编辑和水印添加功能
"""
from typing import Optional, Dict, Any
from pathlib import Path
from everify.core.utils import logger
from everify.core.utils import config


class ImageEngine:
    """图片处理引擎接口"""

    def __init__(self, image_config: Optional[Any] = None):
        self.config = image_config or config.watermark
        logger.debug("图片处理引擎初始化")

    def add_watermark(self, image_path: Path, watermark_text: str, output_path: Optional[Path] = None) -> Path:
        """添加水印到图片"""
        pass

    def resize_image(self, image_path: Path, width: int, height: int, output_path: Optional[Path] = None) -> Path:
        """调整图片大小"""
        pass

    def optimize_image(self, image_path: Path, quality: int = 85, output_path: Optional[Path] = None) -> Path:
        """优化图片大小和质量"""
        pass

    def convert_format(self, image_path: Path, target_format: str, output_path: Optional[Path] = None) -> Path:
        """转换图片格式"""
        pass

    def get_image_info(self, image_path: Path) -> Dict[str, Any]:
        """获取图片信息"""
        pass


class PillowImageEngine(ImageEngine):
    """基于 Pillow 的图片处理引擎实现"""

    def add_watermark(self, image_path: Path, watermark_text: str, output_path: Optional[Path] = None) -> Path:
        """添加水印到图片"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import datetime

            # 打开图片
            image = Image.open(image_path)

            # 创建绘图对象
            draw = ImageDraw.Draw(image)

            # 解析水印配置
            font_size = self.config.font_size
            color = self.config.color
            opacity = self.config.opacity
            position = self.config.position

            # 尝试加载字体
            try:
                # 首先尝试加载系统字体（Windows系统使用微软雅黑）
                import platform

                system = platform.system()
                if system == "Windows":
                    font_path = "C:/Windows/Fonts/msyh.ttc"
                elif system == "Darwin":
                    font_path = "/System/Library/Fonts/PingFang.ttc"
                else:  # Linux
                    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

                font = ImageFont.truetype(font_path, font_size)
            except:
                # 如果无法加载系统字体，使用默认字体
                font = ImageFont.load_default()

            # 格式化水印文本（支持时间戳格式）
            try:
                watermark_text = datetime.datetime.now().strftime(watermark_text)
            except:
                pass

            # 计算文本尺寸
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 计算水印位置
            img_width, img_height = image.size
            padding = 20

            if position == "top_left":
                x = padding
                y = padding
            elif position == "top_right":
                x = img_width - text_width - padding
                y = padding
            elif position == "bottom_left":
                x = padding
                y = img_height - text_height - padding
            elif position == "bottom_right":
                x = img_width - text_width - padding
                y = img_height - text_height - padding
            elif position == "center":
                x = (img_width - text_width) // 2
                y = (img_height - text_height) // 2
            else:
                # 默认右下角
                x = img_width - text_width - padding
                y = img_height - text_height - padding

            # 处理颜色和透明度
            # 将颜色字符串转换为 RGB
            if color.startswith("#"):
                # 十六进制颜色
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
            else:
                # 颜色名称
                from PIL import ImageColor

                r, g, b = ImageColor.getrgb(color)

            # 转换为 RGBA
            rgba_color = (r, g, b, int(opacity * 255))

            # 创建水印图层
            watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw_layer = ImageDraw.Draw(watermark_layer)

            # 计算斜向水印位置（从左下到右上，旋转45度）
            angle = 45
            # 创建旋转后的文字图像
            text_image = Image.new('RGBA', (text_width + 40, text_height + 40), (0, 0, 0, 0))
            draw_text = ImageDraw.Draw(text_image)
            draw_text.text((20, 20), watermark_text, font=font, fill=rgba_color)
            rotated_text = text_image.rotate(angle, expand=True)

            # 计算水印在图片上的位置
            rx, ry = rotated_text.size
            # 斜向排列，从左下到右上
            x = (image.width - rx) // 2
            y = (image.height - ry) // 2

            # 将旋转后的文字粘贴到水印图层
            watermark_layer.paste(rotated_text, (x, y), rotated_text)

            # 合并水印图层到原始图片
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            image = Image.alpha_composite(image, watermark_layer)

            # 保存图片
            if output_path is None:
                output_path = image_path.parent / f"{image_path.stem}_watermarked{image_path.suffix}"

            image.save(output_path)
            logger.debug(f"水印已添加到图片: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"添加水印失败: {e}")
            raise

    def resize_image(self, image_path: Path, width: int, height: int, output_path: Optional[Path] = None) -> Path:
        """调整图片大小"""
        try:
            from PIL import Image

            image = Image.open(image_path)
            resized_image = image.resize((width, height))

            if output_path is None:
                output_path = image_path.parent / f"{image_path.stem}_resized{image_path.suffix}"

            resized_image.save(output_path)
            logger.debug(f"图片已调整大小: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"调整图片大小失败: {e}")
            raise

    def optimize_image(self, image_path: Path, quality: int = 85, output_path: Optional[Path] = None) -> Path:
        """优化图片大小和质量"""
        try:
            from PIL import Image

            image = Image.open(image_path)

            if output_path is None:
                output_path = image_path.parent / f"{image_path.stem}_optimized{image_path.suffix}"

            image.save(output_path, optimize=True, quality=quality)
            logger.debug(f"图片已优化: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"优化图片失败: {e}")
            raise

    def convert_format(self, image_path: Path, target_format: str, output_path: Optional[Path] = None) -> Path:
        """转换图片格式"""
        try:
            from PIL import Image

            image = Image.open(image_path)

            # 确定输出格式
            format_map = {
                "png": "PNG",
                "jpg": "JPEG",
                "jpeg": "JPEG",
                "gif": "GIF",
                "bmp": "BMP",
                "webp": "WEBP"
            }

            if target_format.lower() not in format_map:
                raise ValueError(f"不支持的目标格式: {target_format}")

            if output_path is None:
                output_path = image_path.parent / f"{image_path.stem}.{target_format.lower()}"

            image.save(output_path, format=format_map[target_format.lower()])
            logger.debug(f"图片格式已转换: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"转换图片格式失败: {e}")
            raise

    def get_image_info(self, image_path: Path) -> Dict[str, Any]:
        """获取图片信息"""
        try:
            from PIL import Image

            image = Image.open(image_path)
            info = {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size": image_path.stat().st_size
            }
            logger.debug(f"图片信息: {info}")
            return info

        except Exception as e:
            logger.error(f"获取图片信息失败: {e}")
            raise


def create_image_engine() -> ImageEngine:
    """创建图片处理引擎实例"""
    return PillowImageEngine()
