#!/usr/bin/env python3
"""
网页核查服务模块
负责异步执行网页核查任务
"""
import asyncio
from typing import Dict, List, Optional
from pathlib import Path
from everify.core.utils import logger
from everify.core.base.browser import BrowserEngine, PlaywrightBrowser


class VerifyService:
    """网页核查服务"""

    def __init__(self, config=None):
        """初始化核查服务

        Args:
            config: 配置对象
        """
        self.config = config
        self.browser: Optional[BrowserEngine] = None

    async def verify_single_entity(self, entity: str, urls: List[str]) -> Dict[str, str]:
        """核查单个主体的所有 URL

        Args:
            entity: 主体名称
            urls: 需要核查的 URL 列表

        Returns:
            dict: {URL: 截图路径}
        """
        results = {}

        # 创建浏览器实例
        browser = PlaywrightBrowser(browser_config=self.config.browser)

        try:
            async with browser:
                # 检查浏览器页面是否成功初始化
                if not browser.page:
                    logger.error(f"浏览器页面未初始化，无法核查主体 '{entity}'")
                    return results

                for url in urls:
                    try:
                        screenshot_path = await self._verify_single_url(entity, url, browser)
                        if screenshot_path:
                            results[url] = screenshot_path
                    except Exception as e:
                        logger.error(f"核查URL '{url}' 失败: {e}")
                        results[url] = ""
        except Exception as e:
            logger.error(f"浏览器引擎初始化失败: {e}")

        logger.info(f"主体 '{entity}' 核查完成，成功 {len([p for p in results.values() if p])} 个，失败 {len([p for p in results.values() if not p])} 个")
        return results

    async def _verify_single_url(self, entity: str, url: str, browser: BrowserEngine) -> str:
        """核查单个URL并截图

        Args:
            entity: 主体名称
            url: URL地址
            browser: 浏览器引擎实例

        Returns:
            str: 截图路径
        """
        # 创建输出目录
        screenshot_dir = self.config.screenshots_dir / entity
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        # 生成截图文件名
        from everify.utils.file import clean_filename
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"{clean_filename(entity)}_{url_hash}.png"
        screenshot_path = screenshot_dir / filename

        try:
            # 检查浏览器是否已经初始化
            if not browser.page:
                logger.error(f"浏览器页面未初始化，无法访问 URL '{url}'")
                return ""

            # 导航到URL并截图
            await browser.navigate(url)
            await browser.screenshot(str(screenshot_path))
            logger.debug(f"URL '{url}' 截图成功: {screenshot_path}")
            return str(screenshot_path)
        except Exception as e:
            logger.error(f"URL '{url}' 截图失败: {e}")
            return ""

    async def process_all_entities(self, entity_urls: Dict[str, List[str]]) -> Dict[str, Dict[str, str]]:
        """处理所有需要核查的主体

        Args:
            entity_urls: {主体名称: [URL1, URL2, ...]}

        Returns:
            dict: {主体名称: {URL: 截图路径}}
        """
        results = {}

        # 创建任务列表
        tasks = []
        for entity, urls in entity_urls.items():
            task = self.verify_single_entity(entity, urls)
            tasks.append(task)

        # 并发执行所有任务
        task_results = await asyncio.gather(*tasks)

        # 整理结果
        for i, entity in enumerate(entity_urls.keys()):
            results[entity] = task_results[i]

        return results

    async def verify_batch(self, entity_urls: Dict[str, List[str]], batch_size: int = 5) -> Dict[str, Dict[str, str]]:
        """批量核查主体，控制并发数量

        Args:
            entity_urls: {主体名称: [URL1, URL2, ...]}
            batch_size: 批次大小

        Returns:
            dict: {主体名称: {URL: 截图路径}}
        """
        results = {}
        entities = list(entity_urls.keys())

        for i in range(0, len(entities), batch_size):
            batch = entities[i:i+batch_size]
            logger.info(f"处理批次 {i//batch_size + 1}/{(len(entities) + batch_size - 1)//batch_size}，包含 {len(batch)} 个主体")

            # 创建批次任务
            tasks = []
            for entity in batch:
                task = self.verify_single_entity(entity, entity_urls[entity])
                tasks.append(task)

            # 执行批次任务
            batch_results = await asyncio.gather(*tasks)

            # 保存结果
            for j, entity in enumerate(batch):
                results[entity] = batch_results[j]

        return results
