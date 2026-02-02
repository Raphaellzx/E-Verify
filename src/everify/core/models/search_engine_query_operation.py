"""
搜索引擎查询操作模型
负责执行搜索引擎查询任务，如百度搜索主体相关信息
"""
from everify.core.models.base_operation import BaseOperation, OperationResult
from everify.core.base.browser import BrowserEngine
from everify.core.services.report_generator import ReportGenerator
from everify.core.utils.config import AppConfig
from pathlib import Path
from typing import List, Dict
import asyncio
import urllib.parse


class SearchEngineQueryOperation(BaseOperation):
    """搜索引擎查询操作类"""

    def __init__(
        self,
        browser_engine: BrowserEngine,
        report_generator: ReportGenerator,
        config: AppConfig
    ):
        """初始化搜索引擎查询操作

        Args:
            browser_engine: 浏览器引擎实例
            report_generator: 报告生成服务实例
            config: 应用程序配置实例
        """
        self.browser_engine = browser_engine
        self.report_generator = report_generator
        self.config = config

    def execute(self, entities: List[str]) -> OperationResult:
        """执行搜索引擎查询操作

        Args:
            entities: 需要查询的主体列表

        Returns:
            OperationResult: 操作结果
        """
        try:
            results = asyncio.run(self._async_execute(entities))

            # 生成搜索引擎查询报告
            report_paths = self.report_generator.generate_search_engine_report(results)

            return OperationResult.success_result({
                'results': results,
                'report_paths': report_paths,
                'message': f"搜索引擎查询完成！共查询 {len(entities)} 个主体，报告已生成"
            })
        except Exception as e:
            return OperationResult.error_result(f"搜索引擎查询操作执行失败: {str(e)}")

    async def _async_execute(self, entities: List[str]) -> Dict:
        """异步执行搜索引擎查询操作

        Args:
            entities: 需要查询的主体列表

        Returns:
            Dict: 查询结果
        """
        # 初始化浏览器引擎
        await self.browser_engine.initialize()

        # 定义需要搜索的关键词前缀
        search_keywords = ['舆情', '查封', '冻结', '收购']

        results = {}

        # 创建搜索引擎查询结果的子文件夹
        search_screenshots_dir = self.config.screenshots_dir / "search_engine"
        search_screenshots_dir.mkdir(exist_ok=True)

        # 为每个主体执行搜索
        for entity in entities:
            entity_results = {}

            # 为每个主体创建一个子文件夹
            from everify.utils.file import clean_filename
            entity_dir = search_screenshots_dir / clean_filename(entity)
            entity_dir.mkdir(exist_ok=True)

            # 为每个关键词执行搜索
            for keyword in search_keywords:
                query = f"{entity} {keyword}"
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://www.baidu.com/s?wd={encoded_query}"

                # 创建截图文件名
                clean_keyword = clean_filename(keyword)
                screenshot_path = entity_dir / f"{clean_keyword}.png"

                try:
                    # 使用浏览器引擎进行搜索和截图
                    await self.browser_engine.navigate(search_url)
                    await self.browser_engine.screenshot(str(screenshot_path))
                    entity_results[keyword] = str(screenshot_path)
                except Exception as e:
                    entity_results[keyword] = str(e)

            results[entity] = entity_results

        # 关闭浏览器引擎
        await self.browser_engine.close()

        return results
