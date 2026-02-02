"""
自动核查操作模型
负责执行自动核查任务
"""
from typing import List, Dict
from everify.core.models.base_operation import BaseOperation, OperationResult
from everify.core.services.url_generator import URLGenerator
from everify.core.services.verify_service import VerifyService
from everify.core.services.report_generator import ReportGenerator
import asyncio


class AutoVerifyOperation(BaseOperation):
    """自动核查操作类"""

    def __init__(
        self,
        url_generator: URLGenerator,
        verify_service: VerifyService,
        report_generator: ReportGenerator
    ):
        """初始化自动核查操作

        Args:
            url_generator: URL生成服务实例
            verify_service: 核查服务实例
            report_generator: 报告生成服务实例
        """
        self.url_generator = url_generator
        self.verify_service = verify_service
        self.report_generator = report_generator

    def execute(self, entities: List[str], templates: Dict) -> OperationResult:
        """执行自动核查操作

        Args:
            entities: 需要核查的主体列表
            templates: 核查模板字典

        Returns:
            OperationResult: 操作结果
        """
        try:
            # 生成待核查的 URL 列表
            entity_urls = self.url_generator.generate_verify_urls(entities, templates)
            if not entity_urls:
                return OperationResult.error_result("未能为任何主体生成有效的核查URL")

            # 异步执行核查
            results = asyncio.run(self.verify_service.process_all_entities(entity_urls))

            # 生成报告
            report_paths = self.report_generator.generate_report(results, templates=templates)
            if report_paths:
                return OperationResult.success_result({
                    'report_paths': report_paths,
                    'message': f"所有报告已生成！共 {len(report_paths)} 个报告"
                })
            else:
                return OperationResult.error_result("未能生成任何报告")
        except Exception as e:
            return OperationResult.error_result(f"自动核查操作执行失败: {str(e)}")
