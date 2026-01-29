#!/usr/bin/env python3
"""
主体管理服务单元测试
"""
import unittest
from pathlib import Path
from src.everify.core.services.entity_manager import EntityManager


class TestEntityManager(unittest.TestCase):
    """主体管理服务测试"""

    def setUp(self):
        """初始化测试"""
        self.entity_manager = EntityManager()

    def test_validate_entities_normal(self):
        """测试验证正常的主体列表"""
        entities = ["山西省人民政府", "晋能控股集团有限公司", ""]
        validated = self.entity_manager.validate_entities(entities)
        self.assertEqual(len(validated), 2)
        self.assertIn("山西省人民政府", validated)
        self.assertIn("晋能控股集团有限公司", validated)

    def test_validate_entities_empty(self):
        """测试验证空列表"""
        entities = []
        validated = self.entity_manager.validate_entities(entities)
        self.assertEqual(len(validated), 0)

    def test_validate_entities_with_invalid(self):
        """测试包含无效主体的列表"""
        entities = ["", "   ", "a" * 101]
        validated = self.entity_manager.validate_entities(entities)
        self.assertEqual(len(validated), 0)

    def test_load_entities_from_file(self):
        """测试从文件加载主体列表"""
        # 创建临时测试文件
        test_file = Path("test_entities.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("山西省人民政府\n晋能控股集团有限公司\n")

        entities = self.entity_manager.load_entities_from_file(str(test_file))
        self.assertEqual(len(entities), 2)
        self.assertIn("山西省人民政府", entities)
        self.assertIn("晋能控股集团有限公司", entities)

        # 清理临时文件
        test_file.unlink()

    def test_load_entities_from_nonexistent_file(self):
        """测试加载不存在的文件"""
        entities = self.entity_manager.load_entities_from_file("nonexistent.txt")
        self.assertEqual(len(entities), 0)


if __name__ == "__main__":
    unittest.main()
