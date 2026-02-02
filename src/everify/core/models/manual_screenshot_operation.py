"""
人工截图插入操作模型
负责插入人工核查的截图
"""
from everify.core.models.base_operation import BaseOperation, OperationResult
from everify.core.services.report_generator import ReportGenerator
from everify.core.utils.config import AppConfig
from pathlib import Path
from typing import List, Dict


class ManualScreenshotOperation(BaseOperation):
    """人工截图插入操作类"""

    def __init__(
        self,
        report_generator: ReportGenerator,
        config: AppConfig
    ):
        """初始化人工截图插入操作

        Args:
            report_generator: 报告生成服务实例
            config: 应用程序配置实例
        """
        self.report_generator = report_generator
        self.config = config

    def execute(
        self,
        entities: List[str],
        report_paths: Dict[str, Path],
        screenshot_dir: Path
    ) -> OperationResult:
        """执行人工截图插入操作

        Args:
            entities: 需要核查的主体列表
            report_paths: 报告文件路径字典
            screenshot_dir: 截图保存目录

        Returns:
            OperationResult: 操作结果
        """
        try:
            # 插入人工核查的截图
            for entity, report_path in report_paths.items():
                self.report_generator.insert_manual_screenshots(
                    entity, report_path, screenshot_dir, entities
                )

            return OperationResult.success_result({
                'message': "人工核查截图插入完成！"
            })
        except Exception as e:
            return OperationResult.error_result(f"插入人工核查截图失败: {str(e)}")
