---
name: company-financial-analysis
description: Comprehensive financial analysis system for listed companies (A-shares, Hong Kong stocks, and US stocks). Use when users want to analyze a company's investment value, business model, financial health, or industry position. Supports A-share codes (e.g., 600519, 000001), Hong Kong stock codes (e.g., 00700, 09992), and US tickers (e.g., AAPL, MSFT). Downloads annual reports, quarterly reports, and announcements from official sources. Market sentiment analysis via web_search (news). **Automatically prioritizes the latest quarterly reports** when the current year's annual report is not yet published.
---

# Company Financial Analysis

## Overview

This skill provides comprehensive investment analysis for listed companies, supporting A-shares, Hong Kong stocks, and US stocks. It downloads financial reports (annual + quarterly) and announcements from official sources and extracts data directly from the downloaded files.

**Supported Markets:**
- **A-shares**: Shanghai (6xxxxx), Shenzhen (0xxxxx, 3xxxxx), Beijing (4xxxxx, 8xxxxx)
- **Hong Kong**: HKEx listed stocks (5-digit codes like 00700, 09992)
- **US stocks**: NYSE/NASDAQ tickers (e.g., AAPL, MSFT, GOOGL)

**Data Sources:**
- **A股财报和公告**: 巨潮资讯网 (cninfo.com.cn)
- **港股财报和公告**: 巨潮资讯网港股频道 (cninfo.com.cn/hke)
- **US财报和公告**: SEC EDGAR (sec.gov)
- **实时行情**: 东方财富 (eastmoney.com) + 新浪财经 (备用)
- **新闻/市场情绪**: 通过 OpenClaw web_search 工具采集公开新闻

**Key Principles**:
- 财务数据只从下载的财报PDF中提取，不从网上搜索
- **自动优先分析最新季度报表**（当年年报未发布时）
- 市场情绪通过 web_search 采集公开新闻分析（无爬虫依赖）

## Workflow

### Step 1: Understand User Request

When a user asks to analyze a company, identify:
- **Stock code**:
  - A-shares: 6-digit code (e.g., 600519, 000001)
  - Hong Kong: 5-digit code (e.g., 00700, 09992)
  - US stocks: 1-5 letter ticker (e.g., AAPL, MSFT)
  - Or company name (e.g., 贵州茅台, 腾讯, Apple)

### Step 2: Run Data Collection

```bash
cd company-financial-analysis/scripts
python3 analyze_company.py <stock_code> [years] [--skip-news]
```

**Examples:**
```bash
# A股分析
python3 analyze_company.py 600519      # 贵州茅台
python3 analyze_company.py 000001      # 平安银行

# 港股分析
python3 analyze_company.py 09992       # 泡泡玛特
python3 analyze_company.py 00700       # 腾讯控股

# 美股分析
python3 analyze_company.py AAPL        # Apple
python3 analyze_company.py MSFT        # Microsoft
```

**What this does:**
1. Creates output directory: `company_analysis_<code>_<date>/`
2. Downloads financial reports (近5年):
   - **年报** (Annual Reports / 10-K)
   - **三季报** (Q3 Reports / 10-Q)
   - **半年报** (Semi-annual Reports)
   - **一季报** (Q1 Reports)
3. Downloads announcements/filings
4. Extracts financial data from downloaded PDF reports
5. Calculates DuPont analysis indicators
6. **Generates news search guidance** for web_search
7. Generates analysis prompt with latest data guidance

### Step 3: Execute News Search (NEW!)

After data collection, execute news search using the generated guidance:

1. Read `processed_data/news_search_prompt.md`
2. Use **web_search** tool to execute the recommended queries
3. Save results to `processed_data/news_analysis.json`

**Example news search:**
```python
# 推荐的搜索查询（从 news_search_prompt.md 获取）
queries = [
    "安踏体育 最新消息 2025",
    "安踏体育 业绩 财报",
    "安踏体育 投资 分析",
]

# 使用 web_search 工具搜索每个查询
# 汇总结果并分析市场情绪
```

### Step 4: Generate Analysis Report

After data collection and news search, generate the analysis report:
1. Read the analysis prompt from `analysis_prompt.txt`
2. Load news analysis from `processed_data/news_analysis.json` (if available)
3. Load the analysis framework: `references/analysis_framework.md`
4. Load DuPont analysis guide: `references/dupont_analysis.md`
5. **Prioritize analysis of latest quarterly data** if current year's annual report not available
6. Generate comprehensive analysis combining:
   - Historical annual reports
   - Latest quarterly data
   - News and market sentiment
7. Save report to `analysis_report.md`

### Step 5: Deliver Results

Present the analysis report to the user, highlighting:
- Executive summary with key investment points
- DuPont analysis (ROE decomposition)
- Key findings from announcements
- Market sentiment from news
- Critical risks
- Investment recommendation

## Analysis Framework

### DuPont Analysis

**Core Formula:**
```
ROE = 净利率 × 资产周转率 × 权益乘数
```

### Analysis Flow

```
下载财报/公告 → 提取财务数据 → 新闻采集 → 行业分析 → 商业模式分析 → 财务分析(杜邦) → 公告分析 → 市场情绪 → 风险分析 → 估值分析 → 投资建议
```

## Output Structure

```
company_analysis_<code>_<date>/
├── raw_data/
│   ├── annual_reports/           # 年报PDF (A股/港股) 或 10-K (美股)
│   ├── q3_reports/               # 三季报
│   ├── semi_annual_reports/      # 半年报
│   ├── q1_reports/               # 一季报
│   └── announcements/            # 公告
├── processed_data/
│   ├── company_info.json         # 公司信息 + 实时行情
│   ├── financial_data_with_source.json  # 带来源的财务数据
│   ├── metrics_tables.md         # 核心指标表格
│   ├── news_search_prompt.md     # 新闻采集指引 (NEW!)
│   ├── news_analysis.json        # 新闻分析结果 (NEW!)
│   ├── all_announcements.json    # 所有公告
│   └── important_announcements.json  # 重要公告
├── analysis_prompt.txt           # AI分析提示词
└── analysis_report.md            # 最终分析报告
```

## News Collection (NEW!)

### How It Works

The skill generates news search guidance that uses OpenClaw's `web_search` tool:

1. **No external dependencies** - Uses built-in web_search
2. **Public sources only** - News, articles, analyst reports
3. **Structured output** - JSON format for analysis integration

### News Analysis Format

```json
{
    "company": "安踏体育",
    "stock_code": "02020.HK",
    "fetch_time": "2026-01-31T02:30:00",
    "news": [
        {
            "title": "新闻标题",
            "url": "链接",
            "snippet": "摘要",
            "source": "来源"
        }
    ],
    "summary": {
        "total_count": 25,
        "sentiment": "positive",
        "key_topics": ["业绩增长", "品牌扩张"],
        "risk_signals": ["竞争加剧"]
    }
}
```

## Market Support Details

### A-shares (A股)
- **Source**: 巨潮资讯网 (cninfo.com.cn)
- **Reports**: 年报、季报、公告
- **Language**: Chinese

### Hong Kong (港股)
- **Source**: 巨潮资讯网港股频道
- **Reports**: 年度业绩、中期业绩、季度运营公告
- **Language**: Chinese/English

### US Stocks (美股)
- **Source**: SEC EDGAR (sec.gov)
- **Reports**: 10-K, 10-Q, 8-K, 20-F, 6-K
- **Language**: English
- **Note**: 行业数据获取受限（akshare 不支持美股）

## Reference Files

Load these as needed during analysis:
- **`references/analysis_framework.md`**: Complete analysis methodology
- **`references/dupont_analysis.md`**: Detailed DuPont analysis guide
- **`assets/report_template.md`**: Report structure template

## Quick Commands

```bash
# 完整分析（含新闻采集指引）
python3 analyze_company.py 09992

# 跳过新闻采集
python3 analyze_company.py 09992 --skip-news

# 指定年限
python3 analyze_company.py 09992 3

# 快速加载已分析公司
python3 quick_learn.py list
python3 quick_learn.py load 09992.HK
```

## Dependencies

```bash
pip install httpx pandas PyPDF2
```

或者使用项目的 requirements.txt：
```bash
pip install -r requirements.txt
```

## Changelog

### v3.0 (2026-01-31)
- **移除雪球依赖** - 不再使用雪球爬虫
- **新增新闻采集** - 通过 web_search 工具采集公开新闻
- **市场情绪分析** - 基于新闻内容分析市场情绪
- **美股支持** - SEC EDGAR 数据源

### v2.1
- 添加季度报表自动优先分析
- 添加实时股价获取

### v2.0
- 支持A股和港股
- 杜邦分析框架
- 公告分析
