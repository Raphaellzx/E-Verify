#!/usr/bin/env python3
"""
模板管理服务模块
负责核查模板的加载、管理和验证
"""
from typing import List, Dict, Optional
from pathlib import Path
import json
from everify.core.utils import logger
from everify.core.utils.config import VerifyTemplate


class TemplateManager:
    """核查模板管理服务"""

    def __init__(self, templates_path: Optional[Path] = None):
        """初始化模板管理器

        Args:
            templates_path: 模板文件路径
        """
        self.templates_path = templates_path
        self.templates: Dict[str, VerifyTemplate] = {}

    def load_templates(self) -> Dict[str, VerifyTemplate]:
        """加载核查模板

        Returns:
            dict: 模板名称到模板对象的映射
        """
        if self.templates_path and self.templates_path.exists():
            return self._load_from_file()
        else:
            return self._load_default_templates()

    def _load_from_file(self) -> Dict[str, VerifyTemplate]:
        """从文件加载模板"""
        try:
            with open(self.templates_path, "r", encoding="utf-8") as f:
                template_data = json.load(f)

            templates = {}
            for name, data in template_data.items():
                try:
                    print(f"Debug: 加载模板 '{name}', InsertContext: {data.get('InsertContext')}")
                    template = VerifyTemplate(
                        name=data.get("name", name),
                        description=data.get("description", ""),
                        url_pattern=data.get("url_pattern", ""),
                        category=data.get("category", "general"),
                        InsertContext=data.get("InsertContext", "网页核查")
                    )
                    templates[name] = template
                except Exception as e:
                    logger.error(f"加载模板 '{name}' 失败: {e}")

            logger.info(f"从文件成功加载 {len(templates)} 个核查模板")
            self.templates = templates
            return templates

        except Exception as e:
            logger.error(f"加载模板文件失败: {e}")
            return self._load_default_templates()

    def _load_default_templates(self) -> Dict[str, VerifyTemplate]:
        """加载默认模板 - 从根目录下的 templates.json 文件加载"""
        # 根目录下的 templates.json 文件路径
        default_templates_path = Path(__file__).parent.parent.parent.parent.parent / "templates.json"

        if default_templates_path.exists():
            try:
                with open(default_templates_path, "r", encoding="utf-8") as f:
                    template_data = json.load(f)

                templates = {}
                for name, data in template_data.items():
                    try:
                        template = VerifyTemplate(
                            name=data.get("name", name),
                            description=data.get("description", ""),
                            url_pattern=data.get("url_pattern", ""),
                            category=data.get("category", "general"),
                            InsertContext=data.get("InsertContext", "网页核查")
                        )
                        templates[name] = template
                    except Exception as e:
                        logger.error(f"加载模板 '{name}' 失败: {e}")

                logger.warning(f"使用默认模板 ({len(templates)} 个)")
                self.templates = templates
                return templates

            except Exception as e:
                logger.error(f"加载默认模板文件失败: {e}")

        # 如果无法加载文件，返回空模板字典
        logger.error("无法加载默认模板文件，返回空模板字典")
        self.templates = {}
        return {}

    def get_templates_by_category(self, category: str) -> Dict[str, VerifyTemplate]:
        """按分类获取模板

        Args:
            category: 分类名称

        Returns:
            dict: 该分类下的模板
        """
        return {
            name: template for name, template in self.templates.items()
            if template.category == category
        }

    def get_all_categories(self) -> List[str]:
        """获取所有分类

        Returns:
            list: 分类名称列表
        """
        categories = set()
        for template in self.templates.values():
            categories.add(template.category)
        return sorted(list(categories))

    def validate_templates(self) -> Dict[str, VerifyTemplate]:
        """验证模板的有效性

        Returns:
            dict: 有效的模板
        """
        valid_templates = {}
        for name, template in self.templates.items():
            if self._is_template_valid(template):
                valid_templates[name] = template
            else:
                logger.warning(f"无效的模板: {name}")
        return valid_templates

    def _is_template_valid(self, template: VerifyTemplate) -> bool:
        """验证单个模板的有效性

        Args:
            template: 模板对象

        Returns:
            bool: 是否有效
        """
        return (
            template.name
            and template.url_pattern
            and "{}" in template.url_pattern  # 必须包含占位符
        )
