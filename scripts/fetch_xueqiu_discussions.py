#!/usr/bin/env python3
"""
雪球讨论爬虫

使用Playwright无头浏览器爬取雪球讨论，并进行情感分析

反爬策略：
- 模拟真实浏览器（Playwright）
- 随机User-Agent
- 随机延时（2-4秒）
- 模拟滚动行为
"""
import sys
import os
from pathlib import Path
import json
import random
import re
from datetime import datetime
from typing import Dict, List, Optional
import asyncio

from utils import save_json, load_json, normalize_stock_code

# 尝试导入playwright
try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Install with: pip install playwright && playwright install chromium")


# 随机User-Agent池
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# 情感关键词
POSITIVE_KEYWORDS = [
    '看好', '利好', '增长', '超预期', '涨', '牛', '买入', '推荐',
    '优秀', '强劲', '突破', '创新高', '加仓', '抄底', '机会',
    '潜力', '成长', '价值', '低估', '龙头'
]

NEGATIVE_KEYWORDS = [
    '看空', '利空', '下跌', '不及预期', '跌', '熊', '卖出', '减持',
    '风险', '危机', '亏损', '暴雷', '割肉', '套牢', '高估',
    '泡沫', '崩盘', '见顶', '清仓', '警惕'
]


class XueqiuCrawler:
    """雪球爬虫"""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def init_browser(self):
        """初始化浏览器"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )

        # 创建上下文，设置User-Agent
        context = await self.browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
        )

        self.page = await context.new_page()

        # 注入脚本绕过自动化检测
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()

    async def random_delay(self, min_sec: float = 2.0, max_sec: float = 4.0):
        """随机延时"""
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)

    async def simulate_scroll(self, times: int = 3):
        """模拟滚动"""
        for _ in range(times):
            scroll_distance = random.randint(300, 700)
            await self.page.evaluate(f"window.scrollBy(0, {scroll_distance})")
            await self.random_delay(1.0, 2.0)

    def _convert_stock_code_for_xueqiu(self, stock_code: str) -> str:
        """
        转换股票代码为雪球格式

        Examples:
            600519 -> SH600519
            000001 -> SZ000001
            09992.HK -> 09992
            00700.HK -> 00700
        """
        # 去除后缀
        code = stock_code.replace('.SH', '').replace('.SZ', '').replace('.HK', '')

        # A股加前缀
        if len(code) == 6:
            if code.startswith('6'):
                return f"SH{code}"
            elif code.startswith(('0', '3')):
                return f"SZ{code}"

        # 港股直接返回
        return code

    async def fetch_stock_discussions(
        self,
        stock_code: str,
        max_pages: int = 5
    ) -> List[Dict]:
        """
        爬取股票讨论

        Args:
            stock_code: 股票代码
            max_pages: 最大爬取页数

        Returns:
            讨论列表
        """
        xueqiu_code = self._convert_stock_code_for_xueqiu(stock_code)
        url = f"https://xueqiu.com/S/{xueqiu_code}"

        print(f"  访问雪球页面: {url}")

        discussions = []

        try:
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            await self.random_delay()

            # 等待讨论区加载
            try:
                await self.page.wait_for_selector('.timeline__item', timeout=10000)
            except:
                print("  Warning: 未找到讨论内容，页面可能需要登录")
                return discussions

            # 滚动加载更多内容
            for page_num in range(max_pages):
                print(f"  正在爬取第 {page_num + 1} 页...")

                # 解析当前页面讨论
                page_discussions = await self._parse_discussions()
                discussions.extend(page_discussions)

                # 滚动加载更多
                await self.simulate_scroll()

                # 检查是否有更多内容
                await self.random_delay()

            print(f"  共爬取 {len(discussions)} 条讨论")

        except Exception as e:
            print(f"  爬取失败: {e}")

        return discussions

    async def _parse_discussions(self) -> List[Dict]:
        """解析讨论内容"""
        discussions = []

        try:
            # 获取所有讨论项
            items = await self.page.query_selector_all('.timeline__item')

            for item in items:
                try:
                    discussion = {}

                    # 提取作者
                    author_elem = await item.query_selector('.user__name')
                    if author_elem:
                        discussion['author'] = await author_elem.inner_text()

                    # 提取内容
                    content_elem = await item.query_selector('.timeline__item__content')
                    if content_elem:
                        discussion['content'] = await content_elem.inner_text()
                        discussion['content'] = discussion['content'].strip()[:500]  # 限制长度

                    # 提取时间
                    time_elem = await item.query_selector('.timeline__item__time')
                    if time_elem:
                        discussion['date'] = await time_elem.inner_text()

                    # 提取链接
                    link_elem = await item.query_selector('a[href*="/"]')
                    if link_elem:
                        href = await link_elem.get_attribute('href')
                        if href:
                            discussion['url'] = f"https://xueqiu.com{href}" if href.startswith('/') else href

                    # 提取互动数据
                    interaction = await item.query_selector('.timeline__item__action')
                    if interaction:
                        interaction_text = await interaction.inner_text()
                        # 解析点赞、评论数
                        likes_match = re.search(r'(\d+)\s*赞', interaction_text)
                        comments_match = re.search(r'(\d+)\s*评论', interaction_text)
                        discussion['likes'] = int(likes_match.group(1)) if likes_match else 0
                        discussion['comments'] = int(comments_match.group(1)) if comments_match else 0

                    if discussion.get('content'):
                        discussions.append(discussion)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"  解析讨论失败: {e}")

        return discussions


def analyze_sentiment(content: str) -> str:
    """
    分析单条内容的情感倾向

    Returns:
        'positive', 'negative', or 'neutral'
    """
    positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in content)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in content)

    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    return 'neutral'


def analyze_discussions(discussions: List[Dict]) -> Dict:
    """
    分析讨论列表，返回情感分析和关键观点

    Args:
        discussions: 讨论列表

    Returns:
        分析结果字典
    """
    analysis = {
        'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_discussions': len(discussions),
        'sentiment': {
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'score': 0.0,  # -1到1之间，-1最悲观，1最乐观
        },
        'hot_topics': [],
        'key_opinions': {
            'bullish': [],  # 看多观点
            'bearish': [],  # 看空观点
        },
        'risk_mentions': [],
        'discussions_sample': [],  # 保留部分原始讨论样本
    }

    if not discussions:
        return analysis

    # 分析每条讨论
    for disc in discussions:
        content = disc.get('content', '')
        sentiment = analyze_sentiment(content)
        disc['sentiment'] = sentiment
        analysis['sentiment'][sentiment] += 1

        likes = disc.get('likes', 0)

        # 收集看多/看空观点（按点赞数排序）
        if sentiment == 'positive':
            analysis['key_opinions']['bullish'].append({
                'content': content[:200],
                'likes': likes,
                'author': disc.get('author', ''),
                'date': disc.get('date', ''),
            })
        elif sentiment == 'negative':
            analysis['key_opinions']['bearish'].append({
                'content': content[:200],
                'likes': likes,
                'author': disc.get('author', ''),
                'date': disc.get('date', ''),
            })

        # 检测风险相关讨论
        risk_keywords = ['风险', '问题', '担心', '下跌', '亏损', '危机', '暴雷', '减持', '清仓']
        if any(kw in content for kw in risk_keywords):
            analysis['risk_mentions'].append({
                'content': content[:200],
                'likes': likes,
                'date': disc.get('date', ''),
            })

    # 计算情感得分
    total = analysis['sentiment']['positive'] + analysis['sentiment']['negative'] + analysis['sentiment']['neutral']
    if total > 0:
        score = (analysis['sentiment']['positive'] - analysis['sentiment']['negative']) / total
        analysis['sentiment']['score'] = round(score, 2)

    # 按点赞数排序关键观点
    analysis['key_opinions']['bullish'].sort(key=lambda x: x['likes'], reverse=True)
    analysis['key_opinions']['bearish'].sort(key=lambda x: x['likes'], reverse=True)
    analysis['risk_mentions'].sort(key=lambda x: x['likes'], reverse=True)

    # 只保留前10条
    analysis['key_opinions']['bullish'] = analysis['key_opinions']['bullish'][:10]
    analysis['key_opinions']['bearish'] = analysis['key_opinions']['bearish'][:10]
    analysis['risk_mentions'] = analysis['risk_mentions'][:10]

    # 保留部分原始讨论样本
    analysis['discussions_sample'] = discussions[:20]

    return analysis


async def crawl_xueqiu_async(stock_code: str, output_dir: Path, max_pages: int = 5) -> Dict:
    """异步爬取雪球讨论"""
    if not PLAYWRIGHT_AVAILABLE:
        print("  Playwright未安装，无法爬取")
        print("  安装方法: pip install playwright && playwright install chromium")
        return {'error': 'Playwright not installed'}

    crawler = XueqiuCrawler()

    try:
        print("  初始化浏览器...")
        await crawler.init_browser()

        print(f"  开始爬取讨论（最多{max_pages}页）...")
        discussions = await crawler.fetch_stock_discussions(stock_code, max_pages)

        # 保存原始讨论数据
        raw_dir = output_dir / 'raw_data' / 'xueqiu_discussions'
        raw_dir.mkdir(parents=True, exist_ok=True)
        save_json(discussions, raw_dir / 'discussions.json')

        # 分析讨论
        print("  分析讨论情感...")
        analysis = analyze_discussions(discussions)

        return analysis

    finally:
        await crawler.close()


def fetch_xueqiu_discussions(stock_code: str, output_dir: Path, max_pages: int = 5) -> Dict:
    """
    爬取雪球讨论（同步包装）

    Args:
        stock_code: 股票代码
        output_dir: 输出目录
        max_pages: 最大爬取页数

    Returns:
        分析结果字典
    """
    return asyncio.run(crawl_xueqiu_async(stock_code, output_dir, max_pages))


def main(stock_code: str, output_dir: Path, max_pages: int = 5) -> Dict:
    """主函数"""
    normalized_code, market, market_type = normalize_stock_code(stock_code)

    print(f"\n{'='*60}")
    print(f"爬取雪球讨论: {normalized_code}")
    print(f"{'='*60}\n")

    # 爬取并分析
    analysis = fetch_xueqiu_discussions(normalized_code, output_dir, max_pages)

    # 保存分析结果
    analysis_path = output_dir / 'processed_data' / 'xueqiu_analysis.json'
    save_json(analysis, analysis_path)
    print(f"\n  ✓ 分析结果已保存: {analysis_path}")

    # 打印摘要
    print(f"\n{'='*60}")
    print("雪球讨论分析摘要")
    print(f"{'='*60}")
    print(f"  讨论总数: {analysis.get('total_discussions', 0)}")

    sentiment = analysis.get('sentiment', {})
    print(f"  情感分布:")
    print(f"    - 看多: {sentiment.get('positive', 0)}")
    print(f"    - 看空: {sentiment.get('negative', 0)}")
    print(f"    - 中性: {sentiment.get('neutral', 0)}")
    print(f"    - 情感得分: {sentiment.get('score', 0)} (-1悲观 ~ 1乐观)")

    print(f"  风险提及: {len(analysis.get('risk_mentions', []))} 条")

    return analysis


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python fetch_xueqiu_discussions.py <stock_code> <output_dir> [max_pages]")
        print("Example: python fetch_xueqiu_discussions.py 600519 ./company_analysis_600519")
        print("         python fetch_xueqiu_discussions.py 09992.HK ./company_analysis_09992.HK 10")
        sys.exit(1)

    stock_code = sys.argv[1]
    output_dir = Path(sys.argv[2])
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    main(stock_code, output_dir, max_pages)
