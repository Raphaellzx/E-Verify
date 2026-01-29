#!/usr/bin/env python3
"""
模板管理服务单元测试
"""
import unittest
import json
from pathlib import Path
from src.everify.core.services.template_manager import TemplateManager
from src.everify.core.utils.config import VerifyTemplate


class TestTemplateManager(unittest.TestCase):
    """模板管理服务测试"""

    def setUp(self):
        """初始化测试"""
        self.temp_file = Path("test_templates.json")
        self.valid_templates = {
            "baidu_search": {
                "name": "baidu_search",
                "description": "百度搜索核查模板",
                "url_pattern": "https://www.baidu.com/s?wd={}",
                "category": "search"
            },
            "tianyancha": {
                "name": "tianyancha",
                "description": "天眼查企业信息核查模板",
                "url_pattern": "https://www.tianyancha.com/search?key={}",
                "category": "enterprise"
            }
        }

    def tearDown(self):
        """清理测试"""
        if self.temp_file.exists():
            self.temp_file.unlink()

    def test_load_templates_from_file(self):
        """测试从文件加载模板"""
        # 创建测试模板文件
        with open(self.temp_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_templates, f)

        manager = TemplateManager(self.temp_file)
        templates = manager.load_templates()

        self.assertEqual(len(templates), 2)
        self.assertIn("baidu_search", templates)
        self.assertIn("tianyancha", templates)
        self.assertIsInstance(templates["baidu_search"], VerifyTemplate)
        self.assertEqual(templates["baidu_search"].name, "baidu_search")
        self.assertEqual(templates["baidu_search"].category, "search")

    def test_load_default_templates(self):
        """测试加载默认模板"""
        manager = TemplateManager(Path("nonexistent_file.json"))
        templates = manager.load_templates()

        self.assertGreater(len(templates), 0)

    def test_get_templates_by_category(self):
        """测试按分类获取模板"""
        with open(self.temp_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_templates, f)

        manager = TemplateManager(self.temp_file)
        manager.load_templates()

        search_templates = manager.get_templates_by_category("search")
        self.assertEqual(len(search_templates), 1)
        self.assertIn("baidu_search", search_templates)

        enterprise_templates = manager.get_templates_by_category("enterprise")
        self.assertEqual(len(enterprise_templates), 1)
        self.assertIn("tianyancha", enterprise_templates)

    def test_get_all_categories(self):
        """测试获取所有分类"""
        with open(self.temp_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_templates, f)

        manager = TemplateManager(self.temp_file)
        manager.load_templates()

        categories = manager.get_all_categories()
        self.assertEqual(len(categories), 2)
        self.assertIn("search", categories)
        self.assertIn("enterprise", categories)

    def test_validate_templates(self):
        """测试验证模板"""
        with open(self.temp_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_templates, f)

        manager = TemplateManager(self.temp_file)
        manager.load_templates()

        valid_templates = manager.validate_templates()
        self.assertEqual(len(valid_templates), 2)

    def test_invalid_templates(self):
        """测试无效模板的处理"""
        invalid_templates = {
            "invalid": {
                "name": "invalid",
                "description": "无效模板",
                "url_pattern": "https://example.com",  # 缺少占位符
                "category": "general"
            }
        }

        with open(self.temp_file, "w", encoding="utf-8") as f:
            json.dump(invalid_templates, f)

        manager = TemplateManager(self.temp_file)
        manager.load_templates()

        valid_templates = manager.validate_templates()
        self.assertEqual(len(valid_templates), 0)


if __name__ == "__main__":
    unittest.main()
