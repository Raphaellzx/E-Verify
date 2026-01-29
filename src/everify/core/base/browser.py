"""
浏览器控制引擎 - 提供统一的网页访问和操作接口
"""
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from everify.core.utils import logger
from everify.core.utils import config


class BrowserEngine:
    """浏览器引擎接口"""

    def __init__(self, browser_config: Optional[Any] = None):
        self.config = browser_config or config.browser
        self.browser = None
        self.page = None
        logger.debug("浏览器引擎初始化")

    async def __aenter__(self):
        """异步上下文管理器进入"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()

    async def initialize(self) -> None:
        """初始化浏览器引擎"""
        pass

    async def close(self) -> None:
        """关闭浏览器引擎"""
        pass

    async def navigate(self, url: str) -> None:
        """导航到指定 URL"""
        pass

    async def screenshot(self, path: Path, full_page: bool = True) -> Path:
        """截图"""
        pass

    async def fill_form(self, selector: str, value: str) -> None:
        """填写表单"""
        pass

    async def click_element(self, selector: str) -> None:
        """点击元素"""
        pass

    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """等待元素出现"""
        pass

    async def wait_for_loading(self, timeout: int = 10000) -> None:
        """等待页面加载完成"""
        pass


class PlaywrightBrowser(BrowserEngine):
    """基于 Playwright 的浏览器引擎实现"""

    async def initialize(self) -> None:
        """初始化 Playwright 浏览器"""
        from playwright.async_api import async_playwright
        try:
            self.playwright = await async_playwright().start()
            # 根据配置选择浏览器类型（默认为 Chromium）
            browser_type = "chromium"
            # 启动浏览器
            self.browser = await getattr(self.playwright, browser_type).launch(
                headless=self.config.headless,
                args=["--no-sandbox"]
            )
            # 创建新页面
            self.page = await self.browser.new_page()
            # 设置视口大小
            if self.config.viewport:
                width, height = map(int, self.config.viewport.split("x"))
                await self.page.set_viewport_size({"width": width, "height": height})
            logger.debug("Playwright 浏览器引擎初始化成功")
        except Exception as e:
            logger.error(f"Playwright 浏览器引擎初始化失败: {e}")
            raise

    async def close(self) -> None:
        """关闭浏览器"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            if hasattr(self, "playwright") and self.playwright:
                await self.playwright.stop()
            logger.debug("Playwright 浏览器引擎已关闭")
        except Exception as e:
            logger.error(f"关闭 Playwright 浏览器引擎失败: {e}")

    async def navigate(self, url: str) -> None:
        """导航到 URL"""
        try:
            if not self.page:
                logger.error("页面未初始化，无法导航")
                return

            # 增加超时时间并改进等待策略，以应对页面加载问题
            await self.page.goto(url, timeout=30000, wait_until="domcontentloaded")
            logger.debug(f"导航到 URL: {url}")

            # 根据网站设置不同的等待时间
            if "nea.gov.cn" in url:  # 国家能源局网站
                await asyncio.sleep(15)
            elif "samr.gov.cn" in url:  # 国家市场监督管理总局网站
                await asyncio.sleep(8)
            else:
                await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"导航到 URL 失败: {url}, 错误: {e}")
            # 不抛出异常，而是继续执行，避免整个任务失败
            pass

    async def screenshot(self, path: Path, full_page: bool = False) -> Path:
        """截图 - 设置固定尺寸为 1920×1200"""
        try:
            if not self.page:
                logger.error("页面未初始化，无法截图")
                return path

            # 设置固定的视口尺寸
            await self.page.set_viewport_size({"width": 1920, "height": 1200})
            # 等待页面内容加载完成
            await asyncio.sleep(2)
            await self.page.screenshot(path=str(path), full_page=full_page)
            logger.debug(f"截图保存到: {path}")
            return path
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return path

    async def fill_form(self, selector: str, value: str) -> None:
        """填写表单"""
        try:
            await self.page.fill(selector, value)
            logger.debug(f"填写表单: {selector} = {value}")
        except Exception as e:
            logger.error(f"填写表单失败: {selector}, 错误: {e}")
            raise

    async def click_element(self, selector: str) -> None:
        """点击元素"""
        try:
            await self.page.click(selector)
            logger.debug(f"点击元素: {selector}")
        except Exception as e:
            logger.error(f"点击元素失败: {selector}, 错误: {e}")
            raise

    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """等待元素出现"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            logger.debug(f"元素出现: {selector}")
            return True
        except Exception as e:
            logger.warning(f"等待元素出现超时: {selector}, 错误: {e}")
            return False

    async def wait_for_loading(self, timeout: int = 10000) -> None:
        """等待页面加载完成"""
        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.debug("页面加载完成")
        except Exception as e:
            logger.warning(f"等待页面加载超时: {e}")


async def create_browser_engine() -> BrowserEngine:
    """创建浏览器引擎实例"""
    browser = PlaywrightBrowser()
    await browser.initialize()
    return browser
