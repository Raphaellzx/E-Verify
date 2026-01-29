#!/usr/bin/env python3
"""
文档处理引擎单元测试
"""
import unittest
from pathlib import Path
from src.everify.core.base.document import DocxDocumentEngine, create_document_engine


class TestDocxDocumentEngine(unittest.TestCase):
    """基于 python-docx 的文档处理引擎测试"""

    def setUp(self):
        """初始化测试"""
        self.engine = DocxDocumentEngine()
        self.test_output_path = Path("test_output.docx")

    def tearDown(self):
        """清理测试"""
        if self.test_output_path.exists():
            self.test_output_path.unlink()

    def test_engine_creation(self):
        """测试文档引擎创建"""
        engine = create_document_engine()
        self.assertIsInstance(engine, DocxDocumentEngine)

    def test_create_document(self):
        """测试创建文档"""
        title = "测试文档"
        output_path = self.engine.create_document(title)
        self.assertIsNotNone(output_path)

    def test_add_title(self):
        """测试添加标题"""
        title = "测试文档"
        self.engine.create_document(title)
        self.engine.add_title("一级标题")
        self.engine.add_title("二级标题", level=2)
        self.engine.add_title("三级标题", level=3)

    def test_add_paragraph(self):
        """测试添加段落"""
        title = "测试文档"
        self.engine.create_document(title)
        self.engine.add_paragraph("这是一个测试段落。")
        self.engine.add_paragraph("这是另一个测试段落，包含更多内容。")

    def test_add_image_without_image(self):
        """测试在图片不存在时添加图片"""
        title = "测试文档"
        self.engine.create_document(title)
        non_existent_image = Path("non_existent_image.png")
        self.engine.add_image(non_existent_image)

    def test_add_table(self):
        """测试添加表格"""
        title = "测试文档"
        self.engine.create_document(title)

        # 无表头的表格
        data = [
            ["张三", "男", "25"],
            ["李四", "女", "28"],
            ["王五", "男", "30"]
        ]
        self.engine.add_table(data)

    def test_add_table_with_headers(self):
        """测试添加带表头的表格"""
        title = "测试文档"
        self.engine.create_document(title)

        data = [
            ["张三", "男", "25"],
            ["李四", "女", "28"],
            ["王五", "男", "30"]
        ]
        headers = ["姓名", "性别", "年龄"]
        self.engine.add_table(data, headers)

    def test_add_section(self):
        """测试添加章节"""
        title = "测试文档"
        self.engine.create_document(title)
        self.engine.add_section("第一章 概述")

    def test_save_document(self):
        """测试保存文档"""
        title = "测试文档"
        self.engine.create_document(title)
        self.engine.add_title("测试标题")
        self.engine.add_paragraph("这是测试内容。")

        output_path = self.engine.save_document(self.test_output_path)
        self.assertIsNotNone(output_path)
        self.assertTrue(output_path.exists())

    def test_save_document_with_automatic_filename(self):
        """测试自动生成文件名的保存"""
        title = "测试文档"
        self.engine.create_document(title)
        self.engine.add_title("测试标题")

        output_path = self.engine.save_document()
        self.assertIsNotNone(output_path)
        self.assertTrue(output_path.exists())
        output_path.unlink()

    def test_document_operations_chain(self):
        """测试完整的文档操作链"""
        title = "完整文档测试"
        self.engine.create_document(title)

        self.engine.add_title("诚信核查报告")
        self.engine.add_paragraph("本报告包含以下内容：")

        data = [
            ["核查项目", "结果"],
            ["百度搜索", "通过"],
            ["天眼查", "通过"],
            ["企查查", "未通过"]
        ]
        self.engine.add_table(data[1:], data[0])

        self.engine.add_section("结论")
        self.engine.add_paragraph("经过核查，该主体存在部分风险。")

        output_path = self.engine.save_document(self.test_output_path)
        self.assertTrue(output_path.exists())

    def test_close_document(self):
        """测试关闭文档"""
        title = "测试文档"
        self.engine.create_document(title)
        self.engine.add_title("标题")
        self.engine.close_document()

    def test_image_caption(self):
        """测试图片说明功能"""
        title = "测试文档"
        self.engine.create_document(title)

        # 使用一个实际存在的图片文件（创建临时文件）
        temp_image = Path("temp_test_image.png")
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(temp_image)

        self.engine.add_image(temp_image, "红色测试图片")

        temp_image.unlink()


if __name__ == "__main__":
    unittest.main()
