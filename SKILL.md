---
name: company-financial-analysis
description: Comprehensive financial analysis system for Chinese listed companies (A-shares and Hong Kong stocks). Use when users want to analyze a company's investment value, business model, financial health, or industry position. Supports A-share codes (e.g., 600519, 000001) and Hong Kong stock codes (e.g., 00700, 09992). Downloads annual reports, quarterly reports (Q1, semi-annual, Q3), and announcements from official sources (巨潮资讯网 for A-shares, 港交所披露易 for HK stocks). **Automatically prioritizes the latest quarterly reports** when the current year's annual report is not yet published, ensuring analysis reflects the most recent financial performance.
---

# Company Financial Analysis

## Overview

This skill provides comprehensive investment analysis for Chinese listed companies, supporting both A-shares and Hong Kong stocks. It downloads financial reports (annual + quarterly) and announcements from official sources and extracts data directly from the downloaded PDFs.

**Supported Markets:**
- **A-shares**: Shanghai (6xxxxx), Shenzhen (0xxxxx, 3xxxxx), Beijing (4xxxxx, 8xxxxx)
- **Hong Kong**: HKEx listed stocks (5-digit codes like 00700, 09992)

**Data Sources:**
- **A股财报和公告**: 巨潮资讯网 (cninfo.com.cn)
- **港股财报和公告**: 巨潮资讯网港股频道 (cninfo.com.cn/hke)

**核心依赖**: CnInfoReports - 开源财报下载库，支持A股和港股

**Key Principles**:
- 财务数据只从下载的财报PDF中提取，不从网上搜索
- **自动优先分析最新季度报表**（当年年报未发布时）

## Workflow

### Step 1: Understand User Request

When a user asks to analyze a company, identify:
- **Stock code**:
  - A-shares: 6-digit code (e.g., 600519, 000001)
  - Hong Kong: 5-digit code (e.g., 00700, 09992)
  - Or company name (e.g., 贵州茅台, 腾讯, 泡泡玛特)

### Step 2: Run Data Collection

```bash
cd company-financial-analysis/scripts
python3 analyze_company.py <stock_code> [years]
```

**Examples:**
```bash
# A股分析
python3 analyze_company.py 600519      # 贵州茅台
python3 analyze_company.py 000001      # 平安银行

# 港股分析
python3 analyze_company.py 09992       # 泡泡玛特
python3 analyze_company.py 00700       # 腾讯控股
```

**What this does:**
1. Creates output directory: `company_analysis_<code>_<date>/`
2. Downloads financial reports (近5年):
   - **年报** (Annual Reports)
   - **三季报** (Q3 Reports)
   - **半年报** (Semi-annual Reports)
   - **一季报** (Q1 Reports)
   - A股: 从巨潮资讯网下载
   - 港股: 从港交所披露易下载
3. Downloads all announcements (近5年所有公告)
4. Extracts financial data from downloaded PDF reports
5. Calculates DuPont analysis indicators
6. **Automatically detects and prioritizes latest quarterly reports**
7. Generates analysis prompt with latest data guidance

### Step 3: Generate Analysis Report

After data collection, generate the analysis report using the prompt:
1. Read the analysis prompt from `analysis_prompt.txt`
2. **System automatically detects latest quarterly reports** (Q3/Semi/Q1)
3. Load the analysis framework: `references/analysis_framework.md`
4. Load DuPont analysis guide: `references/dupont_analysis.md`
5. **Prioritize analysis of latest quarterly data** if current year's annual report not available
6. Generate comprehensive analysis combining historical annual reports and latest quarterly data
7. Save report to `analysis_report.md`

### Step 4: Deliver Results

Present the analysis report to the user, highlighting:
- Executive summary with key investment points
- DuPont analysis (ROE decomposition)
- Key findings from announcements
- Critical risks
- Investment recommendation

### Step 5: Knowledge Summarization and Archiving (NEW!)

After completing the analysis, automatically generate knowledge summary and archive data:

```bash
cd company-financial-analysis/scripts
python3 summarize_and_archive.py <analysis_directory>
```

**What this does:**
1. Generates `knowledge_summary.json` - Structured summary for quick loading
2. Generates `KNOWLEDGE_SUMMARY.md` - Human-readable summary
3. Creates `company_index.json` - Global index of all analyzed companies
4. Compresses raw data to `.tar.gz` archive (optional: delete originals to save space)

**Or use the all-in-one command:**
```bash
python3 analyze_and_summarize.py <stock_code>
```

This runs the full pipeline: data collection → analysis → summarization → archiving

### Step 6: Quick Learning from Previous Analysis (NEW!)

Load knowledge from previously analyzed companies:

```bash
cd company-financial-analysis/scripts

# List all analyzed companies
python3 quick_learn.py list

# Load specific company knowledge
python3 quick_learn.py load 09992.HK

# Compare multiple companies
python3 quick_learn.py compare 09992.HK 00700.HK

# Generate learning summary (for Claude context)
python3 quick_learn.py summary 09992.HK

# Search companies
python3 quick_learn.py search 泡泡
```

**Benefits:**
- Fast context loading for follow-up questions
- Company comparison without re-downloading data
- Efficient knowledge reuse across sessions

## Analysis Framework

### DuPont Analysis

**Core Formula:**
```
ROE = 净利率 × 资产周转率 × 权益乘数
```

### Analysis Flow

```
下载财报/公告 → 提取财务数据 → 行业分析 → 商业模式分析 → 财务分析(杜邦) → 公告分析 → 风险分析 → 估值分析 → 投资建议
```

## Output Structure

```
company_analysis_<code>_<date>/
├── raw_data/
│   ├── annual_reports/           # 下载的年报PDF
│   │   ├── <code>_2023_annual_report.pdf
│   │   ├── <code>_2022_annual_report.pdf
│   │   └── ...
│   └── announcements/            # 公告JSON
│       └── all_announcements.json
├── processed_data/
│   ├── company_info.json
│   ├── financial_data_from_reports.json  # 从年报提取的财务数据
│   ├── dupont_indicators.json           # 杜邦分析指标
│   ├── dupont_summary.json              # 杜邦分析摘要
│   ├── all_announcements.json           # 所有公告
│   ├── important_announcements.json     # 重要公告
│   └── download_summary.json            # 下载摘要
├── analysis_prompt.txt                  # AI分析提示词
├── analysis_report.md                   # 最终分析报告
├── knowledge_summary.json               # 知识摘要 (NEW!)
├── KNOWLEDGE_SUMMARY.md                 # 可读摘要 (NEW!)
├── LEARNING_SUMMARY.md                  # 学习摘要 (NEW!)
└── <code>_raw_data_<date>.tar.gz       # 压缩的原始数据 (NEW!)
```

## New Features

### 1. Knowledge Summarization

After analysis, the system automatically generates:
- **knowledge_summary.json**: Structured summary with metadata, financial highlights, report sections
- **KNOWLEDGE_SUMMARY.md**: Human-readable markdown summary
- **company_index.json**: Global index in scripts/ directory for quick lookup

### 2. Data Archiving

- Compresses raw_data/ to `.tar.gz` (typically 70-90% size reduction)
- Option to keep or delete original files
- Preserves all data for future reference

### 3. Quick Learning

- Load previous analysis instantly without re-downloading
- Compare multiple companies side-by-side
- Generate learning summaries optimized for Claude context
- Search across all analyzed companies

## Reference Files

Load these as needed during analysis:
- **`references/analysis_framework.md`**: Complete analysis methodology
- **`references/dupont_analysis.md`**: Detailed DuPont analysis guide
- **`assets/report_template.md`**: Report structure template

## Important Notes

### Data Collection
- All financial data is extracted from downloaded annual reports
- No web scraping for financial indicators
- Announcements include all disclosures from the past 5 years

### A-share Data (巨潮资讯网)
- Annual reports downloaded automatically
- All announcements downloaded (业绩、重组、诉讼等)
- Data in Chinese

### Hong Kong Data (巨潮资讯网港股频道)
- Annual reports downloaded from 巨潮资讯网 (年度业绩公布)
- All announcements downloaded
- May include English and Chinese content

### Announcement Analysis
The skill downloads all announcements for comprehensive analysis:
- 业绩公告（年报、季报、快报）
- 重大事项（重组、并购、收购）
- 股东行为（增持、减持、质押）
- 风险提示（诉讼、处罚、调查）
- 管理层变动

## Example Usage

**Example: A-share Analysis**

**User**: "帮我分析贵州茅台"

**Response**:
1. Run: `python3 analyze_company.py 600519`
2. Downloads 5 years of annual reports from 巨潮资讯网
3. Downloads all announcements from 巨潮资讯网
4. Extracts financial data from PDF reports
5. Generate analysis covering:
   - DuPont analysis: High ROE driven by exceptional profit margins
   - Announcement analysis: Dividend policies, business updates
   - Risks: Valuation, consumption trends
6. Deliver report

**Example: Hong Kong Stock Analysis**

**User**: "分析泡泡玛特"

**Response**:
1. Run: `python3 analyze_company.py 09992`
2. Downloads annual reports from 巨潮资讯网港股频道 (年度业绩公布)
3. Downloads all announcements
4. Extracts financial data
5. Generate analysis covering:
   - IP-based consumer goods business model
   - Global expansion strategy
   - Revenue growth and profitability trends
6. Deliver report

## Dependencies

```bash
pip install httpx pandas PyPDF2
```

或者使用项目的 requirements.txt：
```bash
pip install -r requirements.txt
```

## Troubleshooting

**Issue**: Annual report download fails
- **Solution**: Check network connection, reports will be saved for manual download if needed

**Issue**: PDF parsing extracts incomplete data
- **Solution**: Financial data extraction from PDFs may be partial; the analysis can proceed with available data

**Issue**: No announcements found
- **Solution**: Check stock code format; HK stocks use 5-digit codes

## Quality Checklist

Before delivering the report, verify:
- [ ] Annual reports downloaded successfully
- [ ] Announcements downloaded (近5年)
- [ ] Financial data extracted from reports
- [ ] ROE decomposed into three factors
- [ ] Announcement analysis completed
- [ ] Risks clearly identified
- [ ] Investment recommendation is justified
