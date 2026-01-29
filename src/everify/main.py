#!/usr/bin/env python3
"""
Everify 主入口模块
负责程序启动和流程调度
"""
import argparse
import asyncio
from pathlib import Path
from everify.core.utils import logger, setup_logging
from everify.core.utils.config import AppConfig
from everify.core.services.entity_manager import EntityManager
from everify.core.services.template_manager import TemplateManager
from everify.core.services.url_generator import URLGenerator
from everify.core.services.verify_service import VerifyService
from everify.core.services.report_generator import ReportGenerator


class EverifyApplication:
    """Everify 应用程序主类"""

    def __init__(self, config: AppConfig):
        """初始化应用程序

        Args:
            config: 应用程序配置
        """
        self.config = config
        self.entity_manager = EntityManager()
        self.template_manager = TemplateManager(config.templates_path)
        self.url_generator = URLGenerator()
        self.verify_service = VerifyService(config)
        self.report_generator = ReportGenerator(config)

    def run(self):
        """运行应用程序"""
        # 加载模板
        templates = self.template_manager.load_templates()
        if not templates:
            logger.error("未加载到任何核查模板，程序退出")
            return

        logger.info(f"成功加载 {len(templates)} 个核查模板")

        # 获取需要核查的主体
        entities = self.entity_manager.get_entities_from_input()
        if not entities:
            logger.warning("未输入任何需要核查的主体，程序退出")
            return

        entities = self.entity_manager.validate_entities(entities)
        logger.info(f"共输入 {len(entities)} 个有效的主体需要核查")

        # 生成待核查的 URL 列表
        entity_urls = self.url_generator.generate_verify_urls(entities, templates)
        if not entity_urls:
            logger.error("未能为任何主体生成有效的核查URL，程序退出")
            return

        logger.info(f"成功为 {len(entity_urls)} 个主体生成核查URL")

        # 异步执行核查
        logger.info("开始执行网页核查...")
        results = asyncio.run(self.verify_service.process_all_entities(entity_urls))

        # 生成报告
        report_paths = self.report_generator.generate_report(results, templates=templates)
        if report_paths:
            logger.info(f"所有报告已生成！共 {len(report_paths)} 个报告")
            for entity, path in report_paths.items():
                logger.info(f"{entity}: {path}")
        else:
            logger.error("未能生成任何报告")

        logger.info("程序执行完毕")

    def run_batch_mode(self, entities_file: str, output_dir: str = None):
        """批量模式运行应用程序

        Args:
            entities_file: 主体列表文件路径
            output_dir: 输出目录
        """
        # 加载模板
        templates = self.template_manager.load_templates()
        if not templates:
            logger.error("未加载到任何核查模板，程序退出")
            return

        logger.info(f"成功加载 {len(templates)} 个核查模板")

        # 从文件加载主体列表
        entities = self.entity_manager.load_entities_from_file(entities_file)
        entities = self.entity_manager.validate_entities(entities)
        if not entities:
            logger.error("未加载到有效的主体列表，程序退出")
            return

        logger.info(f"共加载到 {len(entities)} 个有效的主体需要核查")

        # 生成待核查的 URL 列表
        entity_urls = self.url_generator.generate_verify_urls(entities, templates)
        if not entity_urls:
            logger.error("未能为任何主体生成有效的核查URL，程序退出")
            return

        logger.info(f"成功为 {len(entity_urls)} 个主体生成核查URL")

        # 异步执行核查（控制并发数量）
        logger.info("开始执行网页核查...")
        results = asyncio.run(self.verify_service.verify_batch(entity_urls, batch_size=3))

        # 生成报告
        report_paths = self.report_generator.generate_report(
            results,
            Path(output_dir) if output_dir else None,
            templates=templates
        )
        if report_paths:
            logger.info(f"所有报告已生成！共 {len(report_paths)} 个报告")
            for entity, path in report_paths.items():
                logger.info(f"{entity}: {path}")

            # 不生成综合报告

        else:
            logger.error("未能生成任何报告")

        logger.info("程序执行完毕")


def main() -> None:
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="网页核查自动化工具")
    parser.add_argument("-c", "--config", help="配置文件路径")
    parser.add_argument("-o", "--output", help="输出目录")
    parser.add_argument("-t", "--templates", help="模板文件路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细日志")
    parser.add_argument("-e", "--entities", help="主体列表文件路径（批量模式）")
    args = parser.parse_args()

    # 初始化配置
    setup_logging("DEBUG" if args.verbose else "INFO")
    logger.info("Everify 网页核查自动化工具启动")

    # 加载配置
    config = AppConfig()
    if args.config:
        config.load_from_file(args.config)
    if args.output:
        config.output.reports_dir = Path(args.output) / "reports"
        config.output.screenshots_dir = Path(args.output) / "screenshots"
    if args.templates:
        config.templates_path = Path(args.templates)

    # 创建应用程序实例
    app = EverifyApplication(config)

    # 运行程序
    if args.entities:
        logger.info("批量模式运行")
        app.run_batch_mode(args.entities, args.output)
    else:
        logger.info("交互模式运行")
        app.run()


if __name__ == "__main__":
    main()
