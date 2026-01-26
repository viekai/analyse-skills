---
name: company-financial-analysis
description: Comprehensive financial analysis system for Chinese listed companies (A-shares and Hong Kong stocks). Use when users want to analyze a company's investment value, business model, financial health, or industry position. Supports A-share codes (e.g., 600519, 000001) and Hong Kong stock codes (e.g., 00700, 09988). Generates professional investment analysis reports covering industry analysis, business model evaluation, DuPont financial analysis (ROE decomposition), risk assessment, and valuation. Collects data from financial statements, company announcements, industry data, and market sentiment (Xueqiu discussions).
---

# Company Financial Analysis

## Overview

This skill provides comprehensive investment analysis for Chinese listed companies, supporting both A-shares and Hong Kong stocks. It automates data collection from multiple sources and generates professional analysis reports using the DuPont framework, business model analysis, and industry research.

**Supported Markets:**
- **A-shares**: Shanghai (6xxxxx), Shenzhen (0xxxxx, 3xxxxx), Beijing (4xxxxx, 8xxxxx)
- **Hong Kong**: HKEx listed stocks (5-digit codes like 00700, 09988)

**Key Capabilities:**
- Automated financial data collection (5-year history for A-shares)
- Industry analysis and peer comparison
- Business model evaluation
- DuPont ROE analysis (decomposition into profit margin, asset turnover, equity multiplier)
- Risk assessment (financial + market sentiment)
- Investment recommendations

**Note**: Hong Kong stock data collection has limitations due to API availability. Manual data collection templates are provided for HK stocks.

## Workflow

### Step 1: Understand User Request

When a user asks to analyze a company, identify:
- **Stock code**:
  - A-shares: 6-digit code (e.g., 600519, 000001)
  - Hong Kong: 5-digit code (e.g., 00700, 09988)
  - Or company name (e.g., 贵州茅台, 腾讯)
- **Analysis focus** (if specified): full analysis, specific aspect, or quick overview

### Step 2: Data Collection

Run the analysis script to collect all data:

```bash
cd company-financial-analysis/scripts
python3 analyze_company.py <stock_code>
```

**What this does:**
1. Creates output directory: `company_analysis_<code>_<date>/`
2. Fetches financial data (AkShare):
   - Company information
   - Balance sheet, income statement, cash flow (5 years)
   - Financial indicators (ROE, margins, turnover ratios)
3. Fetches company announcements (重大事项)
4. Fetches industry data and peer companies
5. Prepares Xueqiu discussion template (manual input required)
6. Generates analysis prompt

**Output:**
- `raw_data/`: All downloaded data (CSV format)
- `processed_data/`: Structured JSON files
- `analysis_prompt.txt`: Ready-to-use prompt for AI analysis

### Step 3: Generate Analysis Report

**Option A: Automated (if Claude API available)**
Use the generated prompt with Claude API to generate the report automatically.

**Option B: Manual**
1. Read the analysis prompt from `analysis_prompt.txt`
2. Load the analysis framework: Read `references/analysis_framework.md`
3. Load DuPont analysis guide: Read `references/dupont_analysis.md`
4. Generate comprehensive analysis following the framework
5. Save report to `analysis_report.md`

### Step 4: Deliver Results

Present the analysis report to the user, highlighting:
- Executive summary with key investment points
- Critical risks
- Investment recommendation

## Analysis Framework

The analysis follows a structured framework covering:

### 1. Industry Analysis
- Industry positioning and classification
- Market size and growth (TAM, CAGR)
- Competitive landscape (CR5, market share)
- Company's industry position

### 2. Business Model Analysis
- Value proposition
- Customer segments (B2B/B2C/B2G)
- Revenue model
- Cost structure
- Competitive moats (technology, brand, scale, network effects)

### 3. Financial Analysis (DuPont Framework)

**Core Formula:**
```
ROE = Net Profit Margin × Asset Turnover × Equity Multiplier
```

**Analysis Dimensions:**
- **Profit Margin**: Gross margin, operating expenses, net margin trends
- **Asset Turnover**: Receivables, inventory, total asset turnover
- **Equity Multiplier**: Leverage, debt structure, solvency

**Key Insight**: Connect financial metrics to business model
- High margin + low turnover = Brand/tech premium model (e.g., Moutai)
- Low margin + high turnover = Scale/efficiency model (e.g., retail)
- High leverage = Capital-intensive model (e.g., real estate, banks)

For detailed DuPont analysis guidance, see `references/dupont_analysis.md`.

### 4. Risk Analysis

**Financial Risks:**
- Solvency: Current ratio < 1, quick ratio < 0.8
- Cash flow: Operating cash flow < net profit
- Receivables: A/R growth > revenue growth
- Goodwill: Goodwill / equity > 30%
- Debt maturity: High short-term debt

**Market Sentiment Risks (Xueqiu):**
- Negative opinions summary
- Controversial topics
- Investor concerns

### 5. Valuation & Recommendation
- Current valuation (PE, PB, PS)
- Historical valuation range
- Peer comparison
- Investment recommendation with risk/reward assessment

## Reference Files

Load these as needed during analysis:

- **`references/analysis_framework.md`**: Complete analysis methodology
- **`references/dupont_analysis.md`**: Detailed DuPont analysis guide with examples
- **`assets/report_template.md`**: Report structure template

## Important Notes

### Data Sources
- **A-share financial data**: AkShare (free, no API key required)
- **A-share announcements**: AkShare
- **A-share industry data**: AkShare + manual research
- **Hong Kong stock data**: Manual collection required (templates provided)
  - HKEx website (www.hkexnews.hk) for announcements and reports
  - Financial data providers (Bloomberg, Wind, etc.)
- **Xueqiu discussions**: Manual collection (template provided)

### Dependencies
Required Python packages:
```bash
pip install akshare pandas
```

### Xueqiu Data Collection
The script creates a template for Xueqiu discussions. Users can:
1. Manually collect discussions from xueqiu.com
2. Fill in the template JSON file
3. Or implement full scraping with Playwright (advanced)

### Output Structure
```
company_analysis_<code>_<date>/
├── raw_data/
│   ├── financial_reports/     # CSV files
│   ├── announcements/          # CSV files
│   ├── industry_data/          # JSON files
│   └── xueqiu_discussions/     # JSON template
├── processed_data/
│   ├── company_info.json
│   ├── financial_indicators.json
│   ├── important_announcements.json
│   ├── industry_info.json
│   └── xueqiu_sentiment.json
├── analysis_prompt.txt         # Generated prompt
└── analysis_report.md          # Final report
```

## Best Practices

1. **Always start with data collection**: Run the script first to gather all data
2. **Read reference files**: Load analysis framework and DuPont guide before analyzing
3. **Connect financials to business model**: Don't just report numbers, explain why
4. **Be objective**: Present both opportunities and risks
5. **Use tables**: Display key metrics in tables for clarity
6. **Cite sources**: Reference specific data points from collected data

## Example Usage

**Example 1: A-share Analysis**

**User**: "帮我分析一下贵州茅台的投资价值"

**Response**:
1. Run data collection: `python3 analyze_company.py 600519`
2. Load analysis framework and DuPont guide
3. Generate comprehensive analysis covering:
   - Industry: Baijiu industry analysis, Moutai's dominant position
   - Business model: Premium brand model with pricing power
   - DuPont analysis: High ROE driven by exceptional profit margins (50%+)
   - Risks: Valuation risk, consumption slowdown, policy changes
   - Recommendation: Based on current valuation and growth prospects
4. Deliver report with executive summary and key insights

**Example 2: Hong Kong Stock Analysis**

**User**: "分析腾讯控股（00700）"

**Response**:
1. Run data collection: `python3 analyze_company.py 00700`
2. Note: System will create templates for manual data collection
3. Guide user to collect data from:
   - HKEx website for financial reports
   - Company investor relations page
   - Financial data providers
4. Once data is collected, proceed with analysis
5. Generate report focusing on:
   - Internet platform business model
   - Global competitive position
   - Revenue diversification (gaming, advertising, fintech)
   - Regulatory risks and market dynamics

## Troubleshooting

**Issue**: AkShare data fetch fails
- **Solution**: Check internet connection, try again (data sources may be temporarily unavailable)

**Issue**: No peer company data
- **Solution**: Industry classification may be too specific, analysis can proceed without peer comparison

**Issue**: Missing Xueqiu data
- **Solution**: Use template for manual input, or proceed with financial analysis only

**Issue**: Hong Kong stock data not available
- **Solution**:
  1. Use the generated template to collect data manually
  2. Visit HKEx website (www.hkexnews.hk) for official reports
  3. Check company investor relations page
  4. Consider using specialized financial data providers (Bloomberg, Wind, etc.)
  5. Analysis can proceed with manually collected data

## Quality Checklist

Before delivering the report, verify:
- [ ] All data sources attempted (financial, announcements, industry)
- [ ] ROE decomposed into three factors
- [ ] Financial metrics connected to business model
- [ ] Risks clearly identified and assessed
- [ ] Investment recommendation is clear and justified
- [ ] Report follows the structured framework
- [ ] Tables used for key metrics
- [ ] Language is clear and professional
