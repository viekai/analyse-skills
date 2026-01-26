#!/usr/bin/env python3
"""
从公司年报PDF中提取财务数据
支持从巨潮资讯网下载最新年报并解析关键财务指标
"""
import sys
import os
from pathlib import Path
import re
import json
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: requests not installed. Install with: pip install requests")
    sys.exit(1)

try:
    import PyPDF2
except ImportError:
    print("Warning: PyPDF2 not installed. PDF parsing will be limited.")
    print("Install with: pip install PyPDF2")


def download_annual_report(stock_code: str, year: int, output_dir: Path) -> Path:
    """
    从巨潮资讯网下载年报PDF

    Args:
        stock_code: 股票代码（不含后缀）
        year: 年份
        output_dir: 输出目录

    Returns:
        下载的PDF文件路径
    """
    print(f"正在下载 {stock_code} {year}年年报...")

    # 巨潮资讯网API（示例，实际需要根据网站结构调整）
    # 注意：实际使用时需要处理验证码、登录等反爬虫机制

    pdf_dir = output_dir / 'raw_data' / 'annual_reports'
    pdf_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = pdf_dir / f"{stock_code}_{year}_annual_report.pdf"

    # 这里是占位实现，实际需要：
    # 1. 访问巨潮资讯网搜索页面
    # 2. 搜索公司年报
    # 3. 找到对应年份的年报下载链接
    # 4. 下载PDF文件

    print(f"  提示：自动下载功能需要处理反爬虫机制")
    print(f"  请手动从以下网站下载年报：")
    print(f"  1. 巨潮资讯网: http://www.cninfo.com.cn/")
    print(f"  2. 搜索股票代码: {stock_code}")
    print(f"  3. 下载 {year} 年年报")
    print(f"  4. 保存到: {pdf_path}")

    return pdf_path


def extract_financial_data_from_pdf(pdf_path: Path) -> dict:
    """
    从PDF中提取财务数据

    使用正则表达式匹配关键财务指标
    """
    if not pdf_path.exists():
        print(f"  PDF文件不存在: {pdf_path}")
        return {}

    print(f"正在解析PDF: {pdf_path.name}")

    try:
        financial_data = {
            'revenue': None,  # 营业收入
            'net_profit': None,  # 净利润
            'total_assets': None,  # 总资产
            'total_equity': None,  # 股东权益
            'operating_cash_flow': None,  # 经营现金流
            'roe': None,  # ROE
            'gross_margin': None,  # 毛利率
            'net_margin': None,  # 净利率
            'asset_liability_ratio': None,  # 资产负债率
        }

        # 读取PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""

            # 提取前100页的文本（财务数据通常在前面）
            for page_num in range(min(100, len(pdf_reader.pages))):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()

        # 使用正则表达式提取关键指标
        # 营业收入
        revenue_pattern = r'营业收入[^\d]*([\d,]+\.?\d*)'
        match = re.search(revenue_pattern, text)
        if match:
            financial_data['revenue'] = float(match.group(1).replace(',', ''))

        # 净利润
        net_profit_pattern = r'净利润[^\d]*([\d,]+\.?\d*)'
        match = re.search(net_profit_pattern, text)
        if match:
            financial_data['net_profit'] = float(match.group(1).replace(',', ''))

        # ROE
        roe_pattern = r'净资产收益率[^\d]*([\d.]+)%'
        match = re.search(roe_pattern, text)
        if match:
            financial_data['roe'] = float(match.group(1))

        print(f"  ✓ 成功提取 {len([v for v in financial_data.values() if v is not None])} 个指标")

        return financial_data

    except Exception as e:
        print(f"  ✗ PDF解析失败: {e}")
        return {}


def create_manual_input_template(output_dir: Path, stock_code: str, years: list) -> Path:
    """
    创建手动输入财务数据的模板
    """
    template_path = output_dir / 'raw_data' / 'manual_financial_data.json'

    template = {
        "stock_code": stock_code,
        "data_source": "手动输入",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "instructions": "请填写以下财务数据，单位：亿元，比率用百分比",
        "years": {}
    }

    for year in years:
        template["years"][str(year)] = {
            "revenue": None,  # 营业收入（亿元）
            "net_profit": None,  # 净利润（亿元）
            "total_assets": None,  # 总资产（亿元）
            "total_equity": None,  # 股东权益（亿元）
            "total_liabilities": None,  # 总负债（亿元）
            "operating_cash_flow": None,  # 经营现金流（亿元）
            "current_assets": None,  # 流动资产（亿元）
            "current_liabilities": None,  # 流动负债（亿元）
            "inventory": None,  # 存货（亿元）
            "accounts_receivable": None,  # 应收账款（亿元）
            "roe": None,  # ROE (%)
            "gross_margin": None,  # 毛利率 (%)
            "net_margin": None,  # 净利率 (%)
            "asset_turnover": None,  # 资产周转率
            "equity_multiplier": None,  # 权益乘数
            "asset_liability_ratio": None,  # 资产负债率 (%)
            "current_ratio": None,  # 流动比率
            "quick_ratio": None,  # 速动比率
        }

    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 手动输入模板已创建: {template_path}")
    print(f"\n📝 使用说明：")
    print(f"1. 打开文件: {template_path}")
    print(f"2. 填写各年度的财务数据")
    print(f"3. 保存文件")
    print(f"4. 重新运行分析脚本")

    return template_path


def load_manual_financial_data(output_dir: Path) -> dict:
    """
    加载手动输入的财务数据
    """
    manual_data_path = output_dir / 'raw_data' / 'manual_financial_data.json'

    if not manual_data_path.exists():
        return None

    try:
        with open(manual_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 检查是否有填写数据
        has_data = False
        for year_data in data.get('years', {}).values():
            if any(v is not None for v in year_data.values()):
                has_data = True
                break

        if has_data:
            print(f"✅ 已加载手动输入的财务数据")
            return data
        else:
            print(f"⚠️  手动输入模板存在但未填写数据")
            return None

    except Exception as e:
        print(f"✗ 加载手动数据失败: {e}")
        return None


def calculate_dupont_indicators(financial_data: dict) -> dict:
    """
    根据基础财务数据计算杜邦分析指标
    """
    indicators = {}

    for year, data in financial_data.get('years', {}).items():
        year_indicators = {}

        # 如果已经有计算好的指标，直接使用
        if data.get('roe') is not None:
            year_indicators['roe'] = data['roe']
        elif data.get('net_profit') and data.get('total_equity'):
            # 计算 ROE
            year_indicators['roe'] = (data['net_profit'] / data['total_equity']) * 100

        # 净利率
        if data.get('net_margin') is not None:
            year_indicators['net_margin'] = data['net_margin']
        elif data.get('net_profit') and data.get('revenue'):
            year_indicators['net_margin'] = (data['net_profit'] / data['revenue']) * 100

        # 资产周转率
        if data.get('asset_turnover') is not None:
            year_indicators['asset_turnover'] = data['asset_turnover']
        elif data.get('revenue') and data.get('total_assets'):
            year_indicators['asset_turnover'] = data['revenue'] / data['total_assets']

        # 权益乘数
        if data.get('equity_multiplier') is not None:
            year_indicators['equity_multiplier'] = data['equity_multiplier']
        elif data.get('total_assets') and data.get('total_equity'):
            year_indicators['equity_multiplier'] = data['total_assets'] / data['total_equity']

        # 资产负债率
        if data.get('asset_liability_ratio') is not None:
            year_indicators['asset_liability_ratio'] = data['asset_liability_ratio']
        elif data.get('total_liabilities') and data.get('total_assets'):
            year_indicators['asset_liability_ratio'] = (data['total_liabilities'] / data['total_assets']) * 100

        # 流动比率
        if data.get('current_ratio') is not None:
            year_indicators['current_ratio'] = data['current_ratio']
        elif data.get('current_assets') and data.get('current_liabilities'):
            year_indicators['current_ratio'] = data['current_assets'] / data['current_liabilities']

        # 速动比率
        if data.get('quick_ratio') is not None:
            year_indicators['quick_ratio'] = data['quick_ratio']
        elif data.get('current_assets') and data.get('inventory') and data.get('current_liabilities'):
            year_indicators['quick_ratio'] = (data['current_assets'] - data['inventory']) / data['current_liabilities']

        indicators[year] = year_indicators

    return indicators


def main(stock_code: str, output_dir: Path, years: list = None):
    """
    主函数：获取和处理财务数据

    Args:
        stock_code: 股票代码
        output_dir: 输出目录
        years: 要获取的年份列表，默认最近5年
    """
    if years is None:
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year))

    print(f"\n{'='*60}")
    print(f"增强财务数据获取")
    print(f"股票代码: {stock_code}")
    print(f"年份: {years}")
    print(f"{'='*60}\n")

    # 1. 尝试加载手动输入的数据
    manual_data = load_manual_financial_data(output_dir)

    if manual_data:
        # 使用手动输入的数据
        print("\n使用手动输入的财务数据")
        indicators = calculate_dupont_indicators(manual_data)

        # 保存计算后的指标
        output_path = output_dir / 'processed_data' / 'dupont_indicators.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(indicators, f, ensure_ascii=False, indent=2)

        print(f"✅ 杜邦分析指标已保存: {output_path}")
        return indicators

    # 2. 如果没有手动数据，创建模板
    print("\n未找到手动输入的数据，创建输入模板...")
    template_path = create_manual_input_template(output_dir, stock_code, years)

    print(f"\n{'='*60}")
    print("下一步操作：")
    print(f"{'='*60}")
    print(f"1. 从以下渠道获取财务数据：")
    print(f"   - 巨潮资讯网: http://www.cninfo.com.cn/")
    print(f"   - 东方财富网: http://www.eastmoney.com/")
    print(f"   - 公司官网投资者关系页面")
    print(f"\n2. 填写模板文件: {template_path}")
    print(f"\n3. 重新运行分析脚本")

    return None


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python fetch_financial_from_reports.py <stock_code> <output_dir>")
        sys.exit(1)

    stock_code = sys.argv[1]
    output_dir = Path(sys.argv[2])

    main(stock_code, output_dir)
