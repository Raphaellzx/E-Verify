#!/usr/bin/env python3
"""
Everify 主入口模块
负责程序启动和流程调度
实现菜单式流程：输入主体 → 选择操作 → 执行任务 → 重新选择
使用操作模型架构，便于功能扩展和代码管理
"""
import argparse
from pathlib import Path
from everify.core.utils import logger, setup_logging
from everify.core.utils.config import AppConfig
from everify.core.services.entity_manager import EntityManager
from everify.core.services.template_manager import TemplateManager
from everify.core.services.url_generator import URLGenerator
from everify.core.services.verify_service import VerifyService
from everify.core.services.report_generator import ReportGenerator
from everify.core.models.operation_factory import OperationFactory
from everify.core.models.base_operation import OperationResult


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
        self.entities = []
        self.templates = {}
        self.report_paths = {}

        # 初始化操作工厂，用于创建不同类型的操作实例
        self.operation_factory = OperationFactory()

    def run(self, entities_file: str = None):
        """运行应用程序

        Args:
            entities_file: 主体列表文件路径（可选）
        """
        # 加载模板
        self.templates = self.template_manager.load_templates()
        if not self.templates:
            logger.error("未加载到任何核查模板，程序退出")
            return

        logger.info(f"成功加载 {len(self.templates)} 个核查模板")

        # 获取需要核查的主体
        if entities_file:
            self.entities = self.entity_manager.load_entities_from_file(entities_file)
        else:
            self.entities = self.entity_manager.get_entities_from_input()

        if not self.entities:
            logger.warning("未输入任何需要核查的主体，程序退出")
            return

        self.entities = self.entity_manager.validate_entities(self.entities)
        logger.info(f"共输入 {len(self.entities)} 个有效的主体需要核查")

        # 显示菜单
        while True:
            self._show_menu()
            choice = input("请输入您的选择 (1-4): ").strip()

            if choice == "1":
                self._perform_auto_verify()
            elif choice == "2":
                self._perform_insert_manual_screenshots()
            elif choice == "3":
                self._perform_search_engine_query()
            elif choice == "4":
                logger.info("程序已退出")
                break
            else:
                logger.warning("无效的选择，请输入 1、2、3 或 4")

    def _show_menu(self):
        """显示菜单"""
        logger.info("\n------------------------------------------")
        logger.info("请选择操作：")
        logger.info("1. 进行自动核查部分")
        logger.info("   - 自动访问网页")
        logger.info("   - 截取网页截图")
        logger.info("   - 生成包含自动化截图的报告")
        logger.info("2. 插入人工核查图片")
        logger.info("   - 为已生成的报告插入人工核查的截图")
        logger.info("3. 搜索引擎查询")
        logger.info("   - 分别搜索主体+舆情、查封、冻结、收购")
        logger.info("   - 为每个主体生成搜索结果截图")
        logger.info("4. 退出程序")
        logger.info("------------------------------------------")

    def _perform_auto_verify(self):
        """执行自动核查部分"""
        logger.info("开始执行自动核查操作...")
        auto_verify_operation = self.operation_factory.create_auto_verify_operation(
            self.url_generator, self.verify_service, self.report_generator
        )
        result: OperationResult = auto_verify_operation.execute(
            self.entities, self.templates
        )

        if result.success:
            logger.info(result.data['message'])
            self.report_paths = result.data['report_paths']
            for entity, path in self.report_paths.items():
                logger.info(f"{entity}: {path}")
        else:
            logger.error(result.error)

    def _perform_insert_manual_screenshots(self):
        """执行插入人工核查图片"""
        # 检查是否有当前会话的报告路径
        if not self.report_paths:
            logger.info("未找到当前会话的报告信息，正在检查报告目录...")
            self._load_existing_reports()

        if not self.report_paths:
            logger.warning("未找到已生成的报告，请先执行自动核查部分（选择选项1）")
            return

        # 等待用户完成人工核查
        logger.info("\n------------------------------------------")
        logger.info("请确保已完成人工核查并准备好截图")
        logger.info("人工核查顺序：网页1主体1 → 网页1主体2 → 网页2主体1 → ...")
        logger.info("请输入截图保存目录（留空则使用默认目录：当前工作目录下的 screenshots/）：")
        screenshot_dir_input = input().strip()
        if screenshot_dir_input:
            self.config.screenshots_dir = Path(screenshot_dir_input)
        logger.info(f"截图将从: {self.config.screenshots_dir} 读取")
        logger.info("确认已完成截图后，按 Enter 键继续...")
        try:
            input()
        except EOFError:
            logger.warning("未检测到用户输入，返回菜单")
            return

        logger.info("开始插入人工核查截图...")
        manual_screenshot_operation = self.operation_factory.create_manual_screenshot_operation(
            self.report_generator, self.config
        )
        result: OperationResult = manual_screenshot_operation.execute(
            self.entities, self.report_paths, self.config.screenshots_dir
        )

        if result.success:
            logger.info(result.data['message'])
        else:
            logger.error(result.error)

    def _perform_search_engine_query(self):
        """执行搜索引擎查询操作"""
        logger.info("开始执行搜索引擎查询操作...")
        search_engine_query_operation = self.operation_factory.create_search_engine_query_operation(
            self.config
        )
        result: OperationResult = search_engine_query_operation.execute(
            self.entities
        )

        if result.success:
            logger.info(result.data['message'])
            # 可以在这里添加搜索结果的处理逻辑，如显示或保存
            # for entity, entity_results in result.data['results'].items():
            #     logger.info(f"主体 '{entity}' 的搜索结果：")
            #     for keyword, screenshot_path in entity_results.items():
            #         logger.info(f"  {keyword}: {screenshot_path}")
        else:
            logger.error(result.error)

    def _load_existing_reports(self):
        """从报告目录加载已存在的报告文件"""
        report_dir = self.config.reports_dir
        if not report_dir.exists() or not report_dir.is_dir():
            logger.debug("报告目录不存在")
            return

        # 遍历报告目录，查找与主体匹配的报告文件
        # 报告文件命名格式：{clean_filename(entity)} 诚信核查.docx
        self.report_paths = {}
        for entity in self.entities:
            # 生成预期的报告文件名（使用与 generate_report 相同的命名规则）
            from everify.utils.file import clean_filename
            expected_filename = f"{clean_filename(entity)} 诚信核查.docx"
            report_path = report_dir / expected_filename

            if report_path.exists() and report_path.is_file():
                logger.info(f"找到已存在的报告: {report_path}")
                self.report_paths[entity] = report_path
            else:
                logger.debug(f"未找到主体 '{entity}' 的报告文件")

        if self.report_paths:
            logger.info(f"共找到 {len(self.report_paths)} 个已生成的报告")
        else:
            logger.debug("未找到与输入主体匹配的报告文件")


def main() -> None:
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="网页核查自动化工具")
    parser.add_argument("-c", "--config", help="配置文件路径")
    parser.add_argument("-o", "--output", help="输出目录")
    parser.add_argument("-t", "--templates", help="模板文件路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细日志")
    parser.add_argument("-e", "--entities", help="主体列表文件路径（批量模式）")
    parser.add_argument("-s", "--screenshots-dir", help="截图保存目录")
    args = parser.parse_args()

    # 初始化配置
    setup_logging("DEBUG" if args.verbose else "INFO")
    logger.info("Everify 网页核查自动化工具启动")

    # 加载配置
    config = AppConfig()
    if args.config:
        config.load_from_file(args.config)
    if args.output:
        config.output_dir = Path(args.output)
        config.reports_dir = config.output_dir / "reports"
        if not args.screenshots_dir:
            config.screenshots_dir = config.output_dir / "screenshots"
    if args.screenshots_dir:
        config.screenshots_dir = Path(args.screenshots_dir)
    if args.templates:
        config.templates_path = Path(args.templates)

    # 创建应用程序实例并运行
    app = EverifyApplication(config)
    app.run(args.entities)


if __name__ == "__main__":
    main()
