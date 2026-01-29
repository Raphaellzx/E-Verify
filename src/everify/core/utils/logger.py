"""
日志管理模块 - 提供统一的日志功能
"""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional


# 全局日志格式（简化显示，使其更规整）
DEFAULT_LOG_FORMAT = "[%(levelname)s] %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志级别映射（将字符串级别转为logging常量）
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def _get_log_level(log_level_str: str = "INFO") -> int:
    """从输入的日志级别字符串获取对应的logging常量（默认INFO）"""
    level_str = log_level_str.strip().upper()
    return LOG_LEVEL_MAP.get(level_str, logging.INFO)


def _ensure_log_dir() -> Path:
    """确保日志目录存在，返回日志目录路径"""
    # 直接使用固定路径，避免导入依赖问题
    log_dir = Path("output") / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)
    return log_dir


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None):
    """配置日志系统

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（可选，默认使用 config.output.output_dir/logs/app.log）
    """
    # 获取根logger
    logger = logging.getLogger()
    logger.setLevel(_get_log_level(log_level))
    logger.propagate = False

    # 创建格式器
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_DATE_FORMAT)

    # 控制台Handler
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(_get_log_level(log_level))
        logger.addHandler(console_handler)

    # 文件Handler（如果未提供路径则使用默认位置）
    if log_file is None:
        log_dir = _ensure_log_dir()
        log_file = log_dir / "app.log"

    if not any(isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers):
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 单个文件最大10MB
            backupCount=5,              # 保留5个备份文件
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(_get_log_level(log_level))
        logger.addHandler(file_handler)

    # 错误日志单独分离
    error_log_file = log_file.parent / "error.log"
    if not any(
        isinstance(h, logging.handlers.RotatingFileHandler) and h.baseFilename == str(error_log_file)
        for h in logger.handlers
    ):
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,   # 单个错误日志最大5MB
            backupCount=3,              # 保留3个备份
            encoding="utf-8",
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取logger实例
    :param name: logger名称（建议传__name__，即模块路径）
    :return: 配置好的logger
    """
    logger_name = name or "Everify"
    logger = logging.getLogger(logger_name)
    return logger


# 便捷导出：项目全局通用logger（非必需，推荐各模块用__name__）
logger = get_logger("Everify")
