"""
文件操作工具模块 - 提供文件和目录的基本操作功能
"""
from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import os
from datetime import datetime


def validate_url(url: str) -> bool:
    """验证 URL 格式

    Args:
        url: 要验证的 URL

    Returns:
        bool: 格式是否有效
    """
    import re
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(url_pattern, url) is not None


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """清理文件名，去除无效字符

    Args:
        filename: 原始文件名
        max_length: 最大长度

    Returns:
        str: 清理后的文件名
    """
    # 替换无效字符
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # 截断到最大长度
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext

    return filename


def clean_filename(filename: str, max_length: int = 100) -> str:
    """清理文件名，去除无效字符（与 sanitize_filename 相同）

    Args:
        filename: 原始文件名
        max_length: 最大长度

    Returns:
        str: 清理后的文件名
    """
    return sanitize_filename(filename, max_length)


def generate_timestamp(format_str: str = "%Y%m%d_%H:%M:%S") -> str:
    """生成时间戳字符串

    Args:
        format_str: 时间格式化字符串

    Returns:
        str: 时间戳
    """
    return datetime.now().strftime(format_str)


def load_json_config(file_path: Path) -> Dict[str, Any]:
    """加载 JSON 配置文件

    Args:
        file_path: 配置文件路径

    Returns:
        Dict[str, Any]: 配置内容
    """
    if not file_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_config(data: Dict[str, Any], file_path: Path) -> None:
    """保存配置到 JSON 文件

    Args:
        data: 配置内容
        file_path: 输出路径
    """
    # 确保父目录存在
    file_path.parent.mkdir(exist_ok=True, parents=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_directory(directory: Path) -> Path:
    """创建目录（如果不存在）

    Args:
        directory: 目录路径

    Returns:
        Path: 创建的目录路径
    """
    directory.mkdir(exist_ok=True, parents=True)
    return directory


def clean_temp_files(temp_dir: Path, pattern: str = "*.tmp") -> int:
    """清理临时文件

    Args:
        temp_dir: 临时目录
        pattern: 文件匹配模式

    Returns:
        int: 清理的文件数量
    """
    if not temp_dir.exists():
        return 0

    count = 0
    for file in temp_dir.glob(pattern):
        file.unlink()
        count += 1

    return count


def format_entity_name(name: str) -> str:
    """格式化主体名称

    Args:
        name: 原始名称

    Returns:
        str: 格式化后的名称
    """
    # 去除首尾空格
    name = name.strip()

    # 替换特殊字符
    name = name.replace(' ', '_')
    name = name.replace('/', '_')
    name = name.replace('\\', '_')

    return name


def extract_domain(url: str) -> str:
    """从 URL 中提取域名

    Args:
        url: 完整 URL

    Returns:
        str: 域名
    """
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    return parsed_url.netloc


def escape_special_chars(text: str) -> str:
    """转义特殊字符

    Args:
        text: 原始文本

    Returns:
        str: 转义后的文本
    """
    # 简单的 HTML 转义
    escape_map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }

    for char, escape_char in escape_map.items():
        text = text.replace(char, escape_char)

    return text


def read_file(file_path: Path) -> str:
    """读取文本文件内容

    Args:
        file_path: 文件路径

    Returns:
        str: 文件内容
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(content: str, file_path: Path) -> None:
    """写入内容到文本文件

    Args:
        content: 要写入的内容
        file_path: 文件路径
    """
    file_path.parent.mkdir(exist_ok=True, parents=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def copy_file(src: Path, dst: Path) -> Path:
    """复制文件

    Args:
        src: 源文件路径
        dst: 目标文件路径

    Returns:
        Path: 目标文件路径
    """
    import shutil
    dst.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(src, dst)
    return dst


def move_file(src: Path, dst: Path) -> Path:
    """移动文件

    Args:
        src: 源文件路径
        dst: 目标文件路径

    Returns:
        Path: 目标文件路径
    """
    import shutil
    dst.parent.mkdir(exist_ok=True, parents=True)
    shutil.move(src, dst)
    return dst


def delete_file(file_path: Path) -> bool:
    """删除文件

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否成功删除
    """
    if file_path.exists():
        file_path.unlink()
        return True
    return False


def get_file_size(file_path: Path) -> int:
    """获取文件大小（字节）

    Args:
        file_path: 文件路径

    Returns:
        int: 文件大小（字节）
    """
    if file_path.exists() and file_path.is_file():
        return file_path.stat().st_size
    return 0


def get_file_extension(file_path: Path) -> str:
    """获取文件扩展名

    Args:
        file_path: 文件路径

    Returns:
        str: 文件扩展名（不含点）
    """
    return file_path.suffix[1:].lower()


def list_files(directory: Path, pattern: str = "*") -> List[Path]:
    """列出目录中的文件

    Args:
        directory: 目录路径
        pattern: 文件匹配模式

    Returns:
        List[Path]: 文件路径列表
    """
    if not directory.exists() or not directory.is_dir():
        return []

    return list(directory.glob(pattern))


def list_subdirectories(directory: Path) -> List[Path]:
    """列出目录中的子目录

    Args:
        directory: 目录路径

    Returns:
        List[Path]: 子目录路径列表
    """
    if not directory.exists() or not directory.is_dir():
        return []

    return [d for d in directory.iterdir() if d.is_dir()]


def get_file_modified_time(file_path: Path) -> datetime:
    """获取文件修改时间

    Args:
        file_path: 文件路径

    Returns:
        datetime: 文件修改时间
    """
    if file_path.exists() and file_path.is_file():
        return datetime.fromtimestamp(file_path.stat().st_mtime)
    return datetime.min
