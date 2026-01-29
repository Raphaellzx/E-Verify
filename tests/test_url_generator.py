#!/usr/bin/env python3
"""
URL生成服务单元测试
"""
import unittest
from src.everify.core.services.url_generator import URLGenerator
from src.everify.core.utils.config import VerifyTemplate


class TestURLGenerator(unittest.TestCase):
    """URL生成服务测试"""

    def setUp(self):
        """初始化测试"""
        self.generator = URLGenerator()
        self.templates = {
            "baidu_search": VerifyTemplate(
                name="baidu_search",
                description="百度搜索核查模板",
                url_pattern="https://www.baidu.com/s?wd={}",
                category="search"
            ),
            "tianyancha": VerifyTemplate(
                name="tianyancha",
                description="天眼查企业信息核查模板",
                url_pattern="https://www.tianyancha.com/search?key={}",
                category="enterprise"
            )
        }

    def test_generate_verify_urls_normal(self):
        """测试正常情况下的URL生成"""
        entities = ["山西省人民政府", "晋能控股集团有限公司"]
        entity_urls = self.generator.generate_verify_urls(entities, self.templates)

        self.assertEqual(len(entity_urls), 2)
        self.assertIn("山西省人民政府", entity_urls)
        self.assertIn("晋能控股集团有限公司", entity_urls)
        self.assertEqual(len(entity_urls["山西省人民政府"]), 2)
        self.assertEqual(len(entity_urls["晋能控股集团有限公司"]), 2)

    def test_generate_verify_urls_empty_entities(self):
        """测试空主体列表的URL生成"""
        entities = []
        entity_urls = self.generator.generate_verify_urls(entities, self.templates)
        self.assertEqual(len(entity_urls), 0)

    def test_generate_verify_urls_empty_templates(self):
        """测试空模板列表的URL生成"""
        entities = ["山西省人民政府"]
        entity_urls = self.generator.generate_verify_urls(entities, {})
        self.assertEqual(len(entity_urls), 0)

    def test_validate_urls(self):
        """测试URL验证"""
        valid_urls = [
            "https://www.baidu.com/s?wd=山西省人民政府",
            "https://www.tianyancha.com/search?key=晋能控股集团有限公司"
        ]
        invalid_urls = [
            "www.baidu.com",
            "baidu.com",
            "http://",
            ""
        ]

        all_urls = valid_urls + invalid_urls
        valid = self.generator.validate_urls(all_urls)
        self.assertEqual(len(valid), 2)
        for url in valid_urls:
            self.assertIn(url, valid)

    def test_is_url_valid(self):
        """测试单个URL验证"""
        valid_urls = [
            "https://www.baidu.com",
            "http://example.com/page?param=value",
            "https://subdomain.example.co.uk:8080/path/to/resource"
        ]
        invalid_urls = [
            "www.baidu.com",
            "example.com",
            "http://",
            "",
            "ftp://example.com"
        ]

        for url in valid_urls:
            self.assertTrue(self.generator._is_url_valid(url))
        for url in invalid_urls:
            self.assertFalse(self.generator._is_url_valid(url))

    def test_url_encoding(self):
        """测试URL编码"""
        entity = "山西省人民政府"
        template = VerifyTemplate(
            name="test",
            description="测试模板",
            url_pattern="https://example.com/search?q={}",
            category="test"
        )

        url = self.generator._generate_single_url(entity, template)
        self.assertNotIn(entity, url)  # 应该已编码
        self.assertIn("%E5%B1%B1%E8%A5%BF%E7%9C%81", url)


if __name__ == "__main__":
    unittest.main()
