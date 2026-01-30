"""
配置管理模块
"""
from typing import Dict, List, Optional
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 延迟导入 logger 以避免循环导入
logger = None


class BrowserConfig(BaseModel):
    """浏览器配置"""
    headless: bool = True
    viewport: str = "1920x1080"
    timeout: int = 30000
    user_agent: Optional[str] = None
    proxy: Optional[str] = None


class WatermarkConfig(BaseModel):
    """水印配置"""
    text: str = "%Y-%m-%d %H:%M:%S"
    font_size: int = 24
    color: str = "#808080"
    opacity: float = 0.5
    position: str = "bottom_right"




class VerifyTemplate(BaseModel):
    """核查模板"""
    name: str
    description: str
    url_pattern: str
    category: str = "general"
    InsertContext: str = "网页核查"


class AppConfig(BaseModel):
    """应用程序配置"""
    browser: BrowserConfig = BrowserConfig()
    watermark: WatermarkConfig = WatermarkConfig()
    # 输出路径配置（直接在AppConfig中定义，不再使用OutputConfig子模型）
    output_dir: Path = Path("output")
    screenshots_dir: Path = Path("output") / "screenshots"
    reports_dir: Path = Path("output") / "reports"
    temp_dir: Path = Path("output") / "temp"
    templates: Dict[str, VerifyTemplate] = {}
    templates_path: Optional[Path] = None

    def __post_init__(self):
        """初始化后确保所有目录存在"""
        self.output_dir.mkdir(exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)

    def load_templates(self, template_file: Optional[Path] = None) -> None:
        """加载核查模板

        Args:
            template_file: 模板配置文件路径（可选，默认加载项目根目录下的 templates.json）
        """
        global logger
        if logger is None:
            from everify.core.utils import logger

        if template_file is None:
            template_file = Path("templates.json")

        if not template_file.exists():
            if logger:
                logger.warning(f"模板配置文件 {template_file} 不存在，使用空模板")
            self.templates = {}
            return

        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                import json
                template_data = json.load(f)
                self.templates = {}
                for name, data in template_data.items():
                    self.templates[name] = VerifyTemplate(**data)
            if logger:
                logger.info(f"成功加载 {len(self.templates)} 个核查模板")
        except Exception as e:
            if logger:
                logger.error(f"加载核查模板失败: {e}")
            self.templates = {}

    def save_templates(self, template_file: Path) -> None:
        """保存核查模板到配置文件

        Args:
            template_file: 模板配置文件路径
        """
        global logger
        if logger is None:
            from everify.core.utils import logger

        try:
            template_data = {name: template.dict() for name, template in self.templates.items()}
            with open(template_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            if logger:
                logger.debug(f"核查模板已保存到 {template_file}")
        except Exception as e:
            if logger:
                logger.error(f"保存核查模板失败: {e}")

    def add_template(self, name: str, template: VerifyTemplate) -> None:
        """添加核查模板

        Args:
            name: 模板名称
            template: 模板对象
        """
        self.templates[name] = template
        global logger
        if logger:
            logger.debug(f"添加核查模板: {name}")

    def get_template(self, name: str) -> Optional[VerifyTemplate]:
        """获取核查模板

        Args:
            name: 模板名称

        Returns:
            Optional[VerifyTemplate]: 模板对象，不存在则返回 None
        """
        return self.templates.get(name)


# 全局配置实例
config = AppConfig()
