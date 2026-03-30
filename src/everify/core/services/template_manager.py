#!/usr/bin/env python3
"""
模板管理服务模块
负责核查模板的加载、管理、验证和选择
"""
from typing import List, Dict, Optional, Set
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
        self.selected_templates: Dict[str, VerifyTemplate] = {}
        self.user_templates_file = Path("user_templates.json")

    def load_templates(self) -> Dict[str, VerifyTemplate]:
        """加载核查模板

        Returns:
            dict: 模板名称到模板对象的映射
        """
        self.templates.clear()

        if self.templates_path and self.templates_path.exists():
            # 如果指定了模板文件，只加载该文件的模板
            self._load_from_file()
        else:
            # 否则加载默认模板和用户模板
            self._load_default_templates()
            self._load_user_templates()

        logger.info(f"成功加载 {len(self.templates)} 个核查模板")
        return self.templates

    def _load_from_file(self) -> None:
        """从文件加载模板"""
        try:
            with open(self.templates_path, "r", encoding="utf-8") as f:
                template_data = json.load(f)

            for name, data in template_data.items():
                try:
                    template = VerifyTemplate(
                        name=data.get("name", name),
                        description=data.get("description", ""),
                        url_pattern=data.get("url_pattern", ""),
                        category=data.get("category", "general"),
                        InsertContext=data.get("InsertContext", "网页核查")
                    )
                    self.templates[name] = template
                except Exception as e:
                    logger.error(f"加载模板 '{name}' 失败: {e}")

        except Exception as e:
            logger.error(f"加载模板文件失败: {e}")
            self._load_default_templates()

    def _load_default_templates(self) -> None:
        """加载默认模板 - 从数据目录下的 templates.json 文件加载"""
        default_templates_path = Path(__file__).parent.parent / "data" / "templates.json"

        if default_templates_path.exists():
            try:
                with open(default_templates_path, "r", encoding="utf-8") as f:
                    template_data = json.load(f)

                for name, data in template_data.items():
                    try:
                        template = VerifyTemplate(
                            name=data.get("name", name),
                            description=data.get("description", ""),
                            url_pattern=data.get("url_pattern", ""),
                            category=data.get("category", "general"),
                            InsertContext=data.get("InsertContext", "网页核查")
                        )
                        self.templates[name] = template
                    except Exception as e:
                        logger.error(f"加载模板 '{name}' 失败: {e}")

                logger.warning(f"使用默认模板 ({len(self.templates)} 个)")

            except Exception as e:
                logger.error(f"加载默认模板文件失败: {e}")

    def _load_user_templates(self) -> None:
        """加载用户自定义模板"""
        if self.user_templates_file.exists():
            try:
                with open(self.user_templates_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)

                for name, data in template_data.items():
                    try:
                        template = VerifyTemplate(
                            name=data.get("name", name),
                            description=data.get("description", ""),
                            url_pattern=data.get("url_pattern", ""),
                            category=data.get("category", "custom"),
                            InsertContext=data.get("InsertContext", "网页核查")
                        )
                        self.templates[name] = template
                    except Exception as e:
                        logger.error(f"加载用户模板 '{name}' 失败: {e}")

                logger.info(f"成功加载 {len(template_data)} 个用户自定义模板")

            except Exception as e:
                logger.error(f"加载用户模板文件失败: {e}")

    def save_user_template(self, name: str, template: VerifyTemplate) -> bool:
        """保存用户自定义模板

        Args:
            name: 模板名称
            template: 模板对象

        Returns:
            bool: 保存是否成功
        """
        try:
            user_templates = {}
            if self.user_templates_file.exists():
                with open(self.user_templates_file, "r", encoding="utf-8") as f:
                    user_templates = json.load(f)

            user_templates[name] = template.dict()

            with open(self.user_templates_file, "w", encoding="utf-8") as f:
                json.dump(user_templates, f, ensure_ascii=False, indent=2)

            self.templates[name] = template
            logger.info(f"用户模板 '{name}' 保存成功")
            return True

        except Exception as e:
            logger.error(f"保存用户模板 '{name}' 失败: {e}")
            return False

    def delete_user_template(self, name: str) -> bool:
        """删除用户自定义模板

        Args:
            name: 模板名称

        Returns:
            bool: 删除是否成功
        """
        try:
            if self.user_templates_file.exists():
                with open(self.user_templates_file, "r", encoding="utf-8") as f:
                    user_templates = json.load(f)

                if name in user_templates:
                    del user_templates[name]
                    with open(self.user_templates_file, "w", encoding="utf-8") as f:
                        json.dump(user_templates, f, ensure_ascii=False, indent=2)

                    if name in self.templates:
                        del self.templates[name]
                    if name in self.selected_templates:
                        del self.selected_templates[name]

                    logger.info(f"用户模板 '{name}' 删除成功")
                    return True

            logger.warning(f"用户模板 '{name}' 不存在")
            return False

        except Exception as e:
            logger.error(f"删除用户模板 '{name}' 失败: {e}")
            return False

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

    def get_category_display_name(self, category: str) -> str:
        """获取分类的显示名称

        Args:
            category: 分类名称

        Returns:
            str: 分类的显示名称
        """
        category_names = {
            "government": "政府网站",
            "association": "协会/行业组织",
            "search": "搜索引擎",
            "custom": "用户自定义",
            "general": "通用"
        }
        return category_names.get(category, category)

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

    def display_templates(self) -> None:
        """显示所有可用的模板（按分类）"""
        categories = self.get_all_categories()
        logger.info("\n------------------------------------------")
        logger.info("可用的核查模板:")

        for category in categories:
            category_templates = self.get_templates_by_category(category)
            if category_templates:
                logger.info(f"\n【{self.get_category_display_name(category)}】")
                for i, (name, template) in enumerate(category_templates.items(), 1):
                    logger.info(f"  {i:2d}. {template.description}")

        logger.info("\n------------------------------------------")

    def select_templates_interactively(self) -> Dict[str, VerifyTemplate]:
        """交互式选择模板

        Returns:
            dict: 选择的模板
        """
        self.display_templates()
        logger.info("\n请选择需要使用的模板：")
        logger.info("  a. 使用所有模板")
        logger.info("  c. 按分类选择")
        logger.info("  s. 选择特定模板")
        logger.info("  q. 返回主菜单")

        choice = input("请输入您的选择: ").strip().lower()

        if choice == "a":
            self.selected_templates = self.templates.copy()
            logger.info(f"已选择所有 {len(self.selected_templates)} 个模板")
        elif choice == "c":
            self.selected_templates = self._select_templates_by_category()
        elif choice == "s":
            self.selected_templates = self._select_specific_templates()
        elif choice == "q":
            return {}
        else:
            logger.warning("无效的选择，已取消模板选择")
            return {}

        return self.selected_templates

    def _select_templates_by_category(self) -> Dict[str, VerifyTemplate]:
        """按分类选择模板

        Returns:
            dict: 选择的模板
        """
        categories = self.get_all_categories()
        logger.info("\n可选择的分类:")
        for i, category in enumerate(categories, 1):
            count = len(self.get_templates_by_category(category))
            logger.info(f"  {i:2d}. {self.get_category_display_name(category)} ({count} 个模板)")

        logger.info("  0. 选择所有分类")
        logger.info("  q. 返回上一级")

        choice = input("请输入分类编号: ").strip()

        if choice == "0":
            selected = self.templates.copy()
            logger.info(f"已选择所有 {len(selected)} 个模板")
            return selected
        elif choice == "q":
            return self.select_templates_interactively()
        elif choice.isdigit() and 1 <= int(choice) <= len(categories):
            category = categories[int(choice) - 1]
            selected = self.get_templates_by_category(category)
            logger.info(f"已选择 {self.get_category_display_name(category)} 下的 {len(selected)} 个模板")
            return selected
        else:
            logger.warning("无效的分类编号")
            return self._select_templates_by_category()

    def _select_specific_templates(self) -> Dict[str, VerifyTemplate]:
        """选择特定模板

        Returns:
            dict: 选择的模板
        """
        logger.info("\n请输入需要选择的模板编号（用空格分隔）:")
        logger.info("例如: 1 3 5 或输入 a 选择所有，输入 q 返回上一级")

        input_str = input("请输入: ").strip()

        if input_str == "a":
            selected = self.templates.copy()
            logger.info(f"已选择所有 {len(selected)} 个模板")
            return selected
        elif input_str == "q":
            return self.select_templates_interactively()

        try:
            indices = list(map(int, input_str.split()))
            all_templates = list(self.templates.values())
            selected = {}

            for idx in indices:
                if 1 <= idx <= len(all_templates):
                    template = all_templates[idx - 1]
                    selected[template.name] = template

            logger.info(f"已选择 {len(selected)} 个模板")
            return selected

        except ValueError:
            logger.warning("输入格式无效，请输入数字")
            return self._select_specific_templates()

    def create_custom_template(self) -> Optional[VerifyTemplate]:
        """创建自定义模板

        Returns:
            Optional[VerifyTemplate]: 创建的模板对象
        """
        logger.info("\n------------------------------------------")
        logger.info("创建自定义模板")

        name = input("请输入模板名称: ").strip()
        if not name:
            logger.warning("模板名称不能为空")
            return None

        description = input("请输入模板描述: ").strip()
        url_pattern = input("请输入URL模板 ({} 为主体名称占位符): ").strip()
        if "{}" not in url_pattern:
            logger.warning("URL模板必须包含 {} 占位符")
            return None

        category = input("请输入分类 (默认: custom): ").strip() or "custom"

        template = VerifyTemplate(
            name=name,
            description=description,
            url_pattern=url_pattern,
            category=category,
            InsertContext=name
        )

        if self.save_user_template(name, template):
            logger.info("自定义模板创建成功")
            return template
        else:
            logger.error("自定义模板创建失败")
            return None

    def manage_user_templates(self) -> None:
        """管理用户自定义模板"""
        while True:
            logger.info("\n------------------------------------------")
            logger.info("用户模板管理:")
            logger.info("  1. 查看所有用户模板")
            logger.info("  2. 创建新的用户模板")
            logger.info("  3. 删除用户模板")
            logger.info("  4. 返回主菜单")

            choice = input("请输入您的选择: ").strip()

            if choice == "1":
                self._display_user_templates()
            elif choice == "2":
                self.create_custom_template()
            elif choice == "3":
                self._delete_user_template()
            elif choice == "4":
                break
            else:
                logger.warning("无效的选择，请重新输入")

    def _display_user_templates(self) -> None:
        """显示用户自定义模板"""
        user_templates = self.get_templates_by_category("custom")
        if user_templates:
            logger.info("\n------------------------------------------")
            logger.info("用户自定义模板:")
            for i, (name, template) in enumerate(user_templates.items(), 1):
                logger.info(f"  {i:2d}. {template.description}")
                logger.info(f"     URL: {template.url_pattern}")
        else:
            logger.info("暂无用户自定义模板")

    def _delete_user_template(self) -> None:
        """删除用户自定义模板"""
        user_templates = self.get_templates_by_category("custom")
        if not user_templates:
            logger.info("暂无用户自定义模板")
            return

        logger.info("\n------------------------------------------")
        logger.info("选择要删除的用户模板:")
        for i, (name, template) in enumerate(user_templates.items(), 1):
            logger.info(f"  {i:2d}. {template.description}")

        choice = input("请输入模板编号: ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(user_templates):
            template_names = list(user_templates.keys())
            template_name = template_names[int(choice) - 1]
            confirm = input(f"确定要删除 '{template_name}' 吗? (y/n): ").strip().lower()

            if confirm == "y":
                self.delete_user_template(template_name)
            else:
                logger.info("已取消删除")
        else:
            logger.warning("无效的选择")

    def get_selected_templates(self) -> Dict[str, VerifyTemplate]:
        """获取当前选择的模板

        Returns:
            dict: 选择的模板
        """
        return self.selected_templates

    def set_selected_templates(self, templates: Dict[str, VerifyTemplate]) -> None:
        """设置选择的模板

        Args:
            templates: 模板字典
        """
        self.selected_templates = templates

    def reset_selection(self) -> None:
        """重置模板选择"""
        self.selected_templates = {}

    def search_templates(self, keyword: str) -> Dict[str, VerifyTemplate]:
        """搜索模板

        Args:
            keyword: 搜索关键词

        Returns:
            dict: 匹配的模板
        """
        results = {}
        keyword = keyword.lower()

        for name, template in self.templates.items():
            if (
                keyword in template.name.lower()
                or keyword in template.description.lower()
                or keyword in template.url_pattern.lower()
                or keyword in self.get_category_display_name(template.category).lower()
            ):
                results[name] = template

        return results
