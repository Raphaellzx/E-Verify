"""
操作工厂类
负责创建不同类型的操作实例
"""
from everify.core.models.auto_verify_operation import AutoVerifyOperation
from everify.core.models.manual_screenshot_operation import ManualScreenshotOperation
from everify.core.models.search_engine_query_operation import SearchEngineQueryOperation
from everify.core.services.url_generator import URLGenerator
from everify.core.services.verify_service import VerifyService
from everify.core.services.report_generator import ReportGenerator
from everify.core.base.browser import PlaywrightBrowser
from everify.core.utils.config import AppConfig


class OperationFactory:
    """操作工厂类，负责创建不同类型的操作实例"""

    @staticmethod
    def create_auto_verify_operation(
        url_generator: URLGenerator,
        verify_service: VerifyService,
        report_generator: ReportGenerator
    ) -> AutoVerifyOperation:
        """创建自动核查操作实例

        Args:
            url_generator: URL生成服务实例
            verify_service: 核查服务实例
            report_generator: 报告生成服务实例

        Returns:
            AutoVerifyOperation: 自动核查操作实例
        """
        return AutoVerifyOperation(
            url_generator=url_generator,
            verify_service=verify_service,
            report_generator=report_generator
        )

    @staticmethod
    def create_manual_screenshot_operation(
        report_generator: ReportGenerator,
        config: AppConfig
    ) -> ManualScreenshotOperation:
        """创建人工截图插入操作实例

        Args:
            report_generator: 报告生成服务实例
            config: 应用程序配置实例

        Returns:
            ManualScreenshotOperation: 人工截图插入操作实例
        """
        return ManualScreenshotOperation(
            report_generator=report_generator,
            config=config
        )

    @staticmethod
    def create_search_engine_query_operation(
        config: AppConfig
    ) -> SearchEngineQueryOperation:
        """创建搜索引擎查询操作实例

        Args:
            config: 应用程序配置实例

        Returns:
            SearchEngineQueryOperation: 搜索引擎查询操作实例
        """
        # 创建浏览器引擎实例
        browser_engine = PlaywrightBrowser(browser_config=config.browser)

        # 创建报告生成器实例（暂时不使用，但保持接口一致性）
        from everify.core.services.report_generator import ReportGenerator
        report_generator = ReportGenerator(config=config)

        return SearchEngineQueryOperation(
            browser_engine=browser_engine,
            report_generator=report_generator,
            config=config
        )
