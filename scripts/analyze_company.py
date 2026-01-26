#!/usr/bin/env python3
"""
Main analysis script - orchestrates data collection and AI analysis
"""
import sys
import os
from pathlib import Path
import json

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import create_output_directory, normalize_stock_code, save_json, load_json
import fetch_financial_data
import fetch_financial_from_reports
import fetch_announcements
import fetch_industry_data
import fetch_xueqiu_discussions


def collect_all_data(stock_code: str, output_dir: Path) -> dict:
    """Collect all data from various sources"""
    print("\n" + "="*80)
    print("PHASE 1: DATA COLLECTION")
    print("="*80 + "\n")

    all_data = {}

    # 1. Fetch financial data
    try:
        financial_data = fetch_financial_data.main(stock_code, output_dir)
        all_data['financial'] = financial_data
        company_info = financial_data.get('company_info', {})

        # 1.5 Try to enhance with manual/report data
        print("\n" + "="*60)
        print("Checking for enhanced financial data...")
        print("="*60 + "\n")
        try:
            # Get the last 5 years
            from datetime import datetime
            current_year = datetime.now().year
            years = list(range(current_year - 5, current_year))

            enhanced_data = fetch_financial_from_reports.main(stock_code, output_dir, years)
            if enhanced_data:
                all_data['enhanced_financial'] = enhanced_data
                print("✓ Enhanced financial data loaded successfully\n")
            else:
                print("ℹ Manual financial data template created")
                print("  Please fill in the template for more accurate analysis\n")
        except Exception as e:
            print(f"Note: Enhanced data collection skipped: {e}\n")
    except Exception as e:
        print(f"Error fetching financial data: {e}")
        company_info = {}

    # 2. Fetch announcements
    try:
        announcements = fetch_announcements.main(stock_code, output_dir)
        all_data['announcements'] = announcements
    except Exception as e:
        print(f"Error fetching announcements: {e}")
        all_data['announcements'] = []

    # 3. Fetch industry data
    try:
        industry_name = company_info.get('industry', '')
        if industry_name:
            industry_data = fetch_industry_data.main(stock_code, industry_name, output_dir)
            all_data['industry'] = industry_data
    except Exception as e:
        print(f"Error fetching industry data: {e}")
        all_data['industry'] = {}

    # 4. Fetch Xueqiu discussions
    try:
        xueqiu_data = fetch_xueqiu_discussions.main(stock_code, output_dir)
        all_data['xueqiu'] = xueqiu_data
    except Exception as e:
        print(f"Error fetching Xueqiu data: {e}")
        all_data['xueqiu'] = {}

    # Save consolidated data
    save_json(all_data, output_dir / 'processed_data' / 'all_data.json')

    return all_data


def prepare_analysis_context(output_dir: Path) -> str:
    """Prepare context for AI analysis"""
    context_parts = []

    # Load all processed data
    try:
        company_info = load_json(output_dir / 'processed_data' / 'company_info.json')
        context_parts.append(f"## Company Information\n{json.dumps(company_info, ensure_ascii=False, indent=2)}")
    except:
        pass

    try:
        indicators = load_json(output_dir / 'processed_data' / 'financial_indicators.json')
        # Limit to last 5 years
        if indicators and len(indicators) > 20:
            indicators = indicators[:20]
        context_parts.append(f"## Financial Indicators (Recent)\n{json.dumps(indicators, ensure_ascii=False, indent=2)}")
    except:
        pass

    # Try to load enhanced DuPont indicators if available
    try:
        dupont_indicators = load_json(output_dir / 'processed_data' / 'dupont_indicators.json')
        if dupont_indicators:
            context_parts.append(f"## DuPont Analysis Indicators (5 Years)\n{json.dumps(dupont_indicators, ensure_ascii=False, indent=2)}")
    except:
        pass

    try:
        announcements = load_json(output_dir / 'processed_data' / 'important_announcements.json')
        # Limit to top 20
        if announcements and len(announcements) > 20:
            announcements = announcements[:20]
        context_parts.append(f"## Important Announcements\n{json.dumps(announcements, ensure_ascii=False, indent=2)}")
    except:
        pass

    try:
        industry_info = load_json(output_dir / 'processed_data' / 'industry_info.json')
        context_parts.append(f"## Industry Information\n{json.dumps(industry_info, ensure_ascii=False, indent=2)}")
    except:
        pass

    try:
        peer_financials = load_json(output_dir / 'processed_data' / 'peer_financials.json')
        context_parts.append(f"## Peer Company Financials\n{json.dumps(peer_financials, ensure_ascii=False, indent=2)}")
    except:
        pass

    try:
        xueqiu_sentiment = load_json(output_dir / 'processed_data' / 'xueqiu_sentiment.json')
        context_parts.append(f"## Xueqiu Market Sentiment\n{json.dumps(xueqiu_sentiment, ensure_ascii=False, indent=2)}")
    except:
        pass

    return "\n\n".join(context_parts)


def generate_analysis_prompt(company_name: str, stock_code: str, context: str) -> str:
    """Generate prompt for AI analysis"""
    prompt = f"""# 投资分析任务

请基于以下数据，为 {company_name} ({stock_code}) 生成一份专业的投资分析报告。

## 分析框架

### 1. 执行摘要
- 核心投资逻辑（3-5个要点）
- 关键财务指标总览
- 主要风险提示
- 投资建议

### 2. 公司概况
- 基本信息
- 主营业务
- 发展历程

### 3. 行业分析
#### 3.1 行业定位
- 所属行业及细分领域
- 行业分类（申万行业）

#### 3.2 行业空间与增长
- 行业市场规模（TAM）
- 行业增长趋势（历史CAGR）
- 行业驱动因素
- 行业周期性特征

#### 3.3 竞争格局
- 行业集中度（CR5）
- 主要竞争对手
- 竞争态势

#### 3.4 公司行业地位
- 市场份额
- 行业排名
- 竞争优势

### 4. 商业模式分析
#### 4.1 价值主张
- 为客户创造的核心价值
- 产品/服务特点

#### 4.2 客户与市场
- 目标客户群体
- 客户类型（B2B/B2C/B2G）

#### 4.3 收入模式
- 收入来源结构
- 收入模式类型（一次性/订阅/佣金等）
- 收入稳定性

#### 4.4 成本结构
- 固定成本 vs 变动成本
- 主要成本项
- 成本优化空间

#### 4.5 竞争壁垒
- 技术壁垒
- 品牌壁垒
- 规模经济
- 网络效应
- 其他护城河

#### 4.6 商业模式评估
- 可持续性
- 可扩展性
- 盈利能力

### 5. 财务分析（杜邦分析框架）
#### 5.1 ROE 总览
- ROE 历史趋势（5年）
- ROE 行业对比
- ROE 驱动因素分解

#### 5.2 盈利能力分析（净利率）
- 毛利率趋势及分析
- 期间费用率（销售/管理/研发/财务）
- 净利率趋势
- 净利率与商业模式的关系

#### 5.3 运营效率分析（资产周转率）
- 应收账款周转率
- 存货周转率
- 总资产周转率
- 周转率与商业模式的关系

#### 5.4 财务杠杆分析（权益乘数）
- 资产负债率
- 有息负债率
- 杠杆水平评估
- 杠杆与商业模式的关系

#### 5.5 现金流质量分析
- 经营现金流 vs 净利润
- 自由现金流
- 现金流稳定性

#### 5.6 成长性分析
- 营收增长率（CAGR）
- 利润增长率
- 成长驱动因素

### 6. 风险分析
#### 6.1 财务风险
- 偿债能力风险（流动比率、速动比率）
- 现金流风险
- 应收账款风险
- 商誉减值风险
- 债务到期压力

#### 6.2 市场情绪风险（基于雪球讨论）
- 负面观点汇总
- 主要争议点
- 投资者关注的风险点

### 7. 估值分析
- 当前估值水平（PE/PB）
- 历史估值区间
- 同行业估值对比
- 合理估值区间判断

### 8. 投资建议
- 投资逻辑总结
- 风险收益比评估
- 建议操作策略
- 关注要点

---

## 数据上下文

{context}

---

## 输出要求

1. 使用中文撰写
2. 使用 Markdown 格式
3. 数据引用要准确
4. 分析要深入，结合商业模式和财务数据
5. 风险提示要明确
6. 结论要客观，避免过度乐观或悲观
7. 使用表格展示关键财务指标对比
8. 重点分析 ROE 的三因素拆解及其与商业模式的关系

请开始分析。
"""
    return prompt


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_company.py <stock_code>")
        print("Example: python analyze_company.py 600519")
        sys.exit(1)

    stock_code = sys.argv[1]
    normalized_code, market, market_type = normalize_stock_code(stock_code)

    print("\n" + "="*80)
    print(f"Company Financial Analysis System")
    print(f"Analyzing: {normalized_code}")
    print("="*80)

    # Create output directory
    output_dir = create_output_directory(normalized_code)
    print(f"\nOutput directory: {output_dir}\n")

    # Collect all data
    all_data = collect_all_data(normalized_code, output_dir)

    # Prepare analysis context
    print("\n" + "="*80)
    print("PHASE 2: PREPARING ANALYSIS CONTEXT")
    print("="*80 + "\n")

    context = prepare_analysis_context(output_dir)
    company_name = all_data.get('financial', {}).get('company_info', {}).get('company_name', normalized_code)

    # Generate analysis prompt
    analysis_prompt = generate_analysis_prompt(company_name, normalized_code, context)

    # Save prompt for manual analysis
    prompt_file = output_dir / 'analysis_prompt.txt'
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(analysis_prompt)

    print(f"Analysis prompt saved to: {prompt_file}")
    print("\n" + "="*80)
    print("PHASE 3: AI ANALYSIS")
    print("="*80 + "\n")

    print("To complete the analysis, please:")
    print("1. Copy the prompt from: " + str(prompt_file))
    print("2. Send it to Claude (Sonnet 4.5)")
    print("3. Save the response to: " + str(output_dir / 'analysis_report.md'))
    print("\nOr use the Claude API to automate this step.")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nAll results saved to: {output_dir}")


if __name__ == '__main__':
    main()
