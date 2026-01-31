#!/usr/bin/env python3
"""
生成投资分析 Canvas 可视化文件

基于 JSON Canvas 规范: https://jsoncanvas.org/spec/1.0/
输出到 Obsidian canvases 目录
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime


def create_investment_canvas(company_name, stock_code, data):
    """
    创建投资分析 Canvas
    
    Args:
        company_name: 公司名称
        stock_code: 股票代码
        data: 分析数据字典，包含:
            - current_price: 当前价格
            - target_price: 目标价
            - rating: 评级
            - revenue: 营收
            - revenue_yoy: 营收同比
            - net_income: 净利润
            - net_income_yoy: 净利润同比
            - gross_margin: 毛利率
            - net_margin: 净利率
            - roe: ROE
            - pe: PE
            - pb: PB
            - market_cap: 市值
            - risks: 风险列表
            - catalysts: 催化剂列表
            - quarters: 季度数据列表
    """
    
    nodes = []
    edges = []
    
    # 颜色定义
    # 1=红色(风险), 2=橙色, 3=黄色(业务), 4=绿色(正面), 5=青色(核心), 6=紫色(标题)
    
    # 标题节点
    nodes.append({
        "id": "title",
        "type": "text",
        "text": f"# {company_name}\n## 综合投资价值分析\n\n**{stock_code}**\n\n当前价: {data.get('current_price', '-')}\n目标价: {data.get('target_price', '-')}\n评级: **{data.get('rating', '-')}**",
        "x": 0,
        "y": 0,
        "width": 280,
        "height": 200,
        "color": "6"
    })
    
    # 估值指标
    pe = data.get('pe', '-')
    pb = data.get('pb', '-')
    market_cap = data.get('market_cap', '-')
    nodes.append({
        "id": "valuation",
        "type": "text",
        "text": f"## 估值指标\n\n| 指标 | 数值 |\n|------|------|\n| 市值 | {market_cap} |\n| PE | {pe} |\n| PB | {pb} |",
        "x": 350,
        "y": 0,
        "width": 280,
        "height": 180,
        "color": "4"
    })
    
    # 业绩数据
    revenue = data.get('revenue', '-')
    revenue_yoy = data.get('revenue_yoy', '-')
    net_income = data.get('net_income', '-')
    net_income_yoy = data.get('net_income_yoy', '-')
    nodes.append({
        "id": "performance",
        "type": "text",
        "text": f"## 业绩数据\n\n- 营收: {revenue} ({revenue_yoy})\n- 净利润: {net_income} ({net_income_yoy})\n- 毛利率: {data.get('gross_margin', '-')}\n- 净利率: {data.get('net_margin', '-')}\n- ROE: {data.get('roe', '-')}",
        "x": -350,
        "y": 0,
        "width": 280,
        "height": 200,
        "color": "4"
    })
    
    # 季度数据
    quarters = data.get('quarters', [])
    if quarters:
        quarter_text = "## 季度趋势\n\n| 季度 | 营收 | 同比 |\n|------|------|------|\n"
        for q in quarters[:4]:
            quarter_text += f"| {q.get('quarter', '-')} | {q.get('revenue', '-')} | {q.get('revenue_yoy', '-')} |\n"
        
        nodes.append({
            "id": "quarters",
            "type": "text",
            "text": quarter_text,
            "x": -350,
            "y": 270,
            "width": 280,
            "height": 180,
            "color": "5"
        })
    
    # 杜邦分析
    nodes.append({
        "id": "dupont",
        "type": "text",
        "text": f"## 杜邦分析\n\n**ROE = 净利率 × 周转率 × 杠杆**\n\n- 净利率: {data.get('net_margin', '-')}\n- 资产周转率: {data.get('asset_turnover', '-')}\n- 权益乘数: {data.get('equity_multiplier', '-')}\n- **ROE: {data.get('roe', '-')}**",
        "x": 0,
        "y": 270,
        "width": 280,
        "height": 180,
        "color": "5"
    })
    
    # 投资亮点
    catalysts = data.get('catalysts', ['待补充'])
    catalyst_text = "## 投资亮点\n\n"
    for i, c in enumerate(catalysts[:5], 1):
        catalyst_text += f"{i}. {c}\n"
    
    nodes.append({
        "id": "catalysts",
        "type": "text",
        "text": catalyst_text,
        "x": 350,
        "y": 270,
        "width": 280,
        "height": 180,
        "color": "4"
    })
    
    # 风险提示
    risks = data.get('risks', ['待补充'])
    risk_text = "## 风险提示\n\n"
    for i, r in enumerate(risks[:5], 1):
        risk_text += f"{i}. {r}\n"
    
    nodes.append({
        "id": "risks",
        "type": "text",
        "text": risk_text,
        "x": 700,
        "y": 0,
        "width": 280,
        "height": 180,
        "color": "1"
    })
    
    # 投资建议
    nodes.append({
        "id": "recommendation",
        "type": "text",
        "text": f"## 投资建议\n\n**评级: {data.get('rating', '-')}**\n\n- 目标价: {data.get('target_price', '-')}\n- 预期收益: {data.get('expected_return', '-')}\n- 建议: {data.get('suggestion', '待补充')}",
        "x": 700,
        "y": 270,
        "width": 280,
        "height": 180,
        "color": "4"
    })
    
    # 添加连接线
    edges.extend([
        {"id": "e1", "fromNode": "title", "fromSide": "right", "toNode": "valuation", "toSide": "left"},
        {"id": "e2", "fromNode": "title", "fromSide": "left", "toNode": "performance", "toSide": "right"},
        {"id": "e3", "fromNode": "title", "fromSide": "bottom", "toNode": "dupont", "toSide": "top"},
        {"id": "e4", "fromNode": "valuation", "fromSide": "bottom", "toNode": "catalysts", "toSide": "top"},
        {"id": "e5", "fromNode": "valuation", "fromSide": "right", "toNode": "risks", "toSide": "left"},
        {"id": "e6", "fromNode": "catalysts", "fromSide": "right", "toNode": "recommendation", "toSide": "left"},
    ])
    
    if quarters:
        edges.append({"id": "e7", "fromNode": "performance", "fromSide": "bottom", "toNode": "quarters", "toSide": "top"})
    
    canvas = {
        "nodes": nodes,
        "edges": edges
    }
    
    return canvas


def extract_data_from_report(report_path):
    """从分析报告中提取数据"""
    data = {
        "current_price": "-",
        "target_price": "-",
        "rating": "-",
        "revenue": "-",
        "revenue_yoy": "-",
        "net_income": "-",
        "net_income_yoy": "-",
        "gross_margin": "-",
        "net_margin": "-",
        "roe": "-",
        "pe": "-",
        "pb": "-",
        "market_cap": "-",
        "risks": [],
        "catalysts": [],
        "quarters": [],
    }
    
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        
        # 提取股价
        price_patterns = [
            r'当前股价[：:]\s*([^\n|]+)',
            r'股价[：:\s]+([$￥]?[0-9.]+)',
            r'当前价[：:\s]+([$￥港]?[0-9.]+)',
        ]
        for pattern in price_patterns:
            match = re.search(pattern, content)
            if match:
                data["current_price"] = match.group(1).strip()
                break
        
        # 提取目标价
        target_patterns = [
            r'目标价[：:]\s*([^\n|]+)',
            r'目标价区间[：:]\s*([^\n|]+)',
            r'合理估值[：:]\s*([^\n|]+)',
        ]
        for pattern in target_patterns:
            match = re.search(pattern, content)
            if match:
                data["target_price"] = match.group(1).strip()
                break
        
        # 提取评级
        rating_patterns = [
            r'\*\*评级[：:]\s*([^*\n]+)\*\*',
            r'评级[：:]\s*\*\*([^*]+)\*\*',
            r'综合评级[：:]\s*([^\n]+)',
            r'投资评级[：:]\s*([^\n]+)',
        ]
        for pattern in rating_patterns:
            match = re.search(pattern, content)
            if match:
                data["rating"] = match.group(1).strip()
                break
        
        # 提取 ROE
        roe_patterns = [
            r'\*\*ROE\*\*[：:\s|]+\*\*~?([0-9.]+%?)\*\*',
            r'ROE[：:\s|]+([0-9.]+%?)',
        ]
        for pattern in roe_patterns:
            match = re.search(pattern, content)
            if match:
                data["roe"] = match.group(1)
                break
        
        # 提取毛利率
        gm_patterns = [
            r'毛利率[：:\s|]+([0-9.]+%?)',
            r'毛利率.*?([0-9.]+%)',
        ]
        for pattern in gm_patterns:
            match = re.search(pattern, content)
            if match:
                data["gross_margin"] = match.group(1)
                break
        
        # 提取净利率
        nm_patterns = [
            r'净利率[：:\s|]+([0-9.]+%?)',
            r'Non-GAAP净利率[：:\s|]+([0-9.]+%?)',
        ]
        for pattern in nm_patterns:
            match = re.search(pattern, content)
            if match:
                data["net_margin"] = match.group(1)
                break
        
        # 提取 PE
        pe_patterns = [
            r'PE[：:\s|]+~?([0-9.]+)x?',
            r'2025E?\s*PE[：:\s|]+([0-9.]+)',
        ]
        for pattern in pe_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                data["pe"] = match.group(1) + "x"
                break
        
        # 提取市值
        cap_patterns = [
            r'市值[：:\s|]+([^\n|]+)',
            r'市值.*?([0-9,]+亿)',
        ]
        for pattern in cap_patterns:
            match = re.search(pattern, content)
            if match:
                data["market_cap"] = match.group(1).strip()
                break
        
        # 提取风险
        risks = []
        risk_section = re.search(r'风险[分提]析.*?\n(.*?)(?=\n##|\n---|\Z)', content, re.DOTALL)
        if risk_section:
            risk_items = re.findall(r'[-•]\s*\*\*([^*]+)\*\*', risk_section.group(1))
            if not risk_items:
                risk_items = re.findall(r'[-•\d.]\s*([^:\n]+)', risk_section.group(1))
            risks = [r.strip() for r in risk_items[:5] if r.strip()]
        data["risks"] = risks if risks else ["详见报告"]
        
        # 提取投资亮点
        catalysts = []
        catalyst_section = re.search(r'核心投资逻辑.*?\n(.*?)(?=\n##|\n###|\Z)', content, re.DOTALL)
        if catalyst_section:
            catalyst_items = re.findall(r'\d+\.\s*\*\*([^*]+)\*\*', catalyst_section.group(1))
            catalysts = [c.strip() for c in catalyst_items[:5] if c.strip()]
        data["catalysts"] = catalysts if catalysts else ["详见报告"]
        
    except Exception as e:
        print(f"提取数据出错: {e}")
    
    return data


def main():
    if len(sys.argv) < 3:
        print("""用法: python3 generate_canvas.py <公司名称> <股票代码> [报告路径] [输出目录]

示例:
    python3 generate_canvas.py 拼多多 PDD
    python3 generate_canvas.py 安踏体育 02020.HK report.md ~/ai/obsidian-notes/canvases
""")
        sys.exit(1)
    
    company_name = sys.argv[1]
    stock_code = sys.argv[2]
    report_path = sys.argv[3] if len(sys.argv) > 3 else None
    output_dir = sys.argv[4] if len(sys.argv) > 4 else os.path.expanduser("~/ai/obsidian-notes/canvases")
    
    print(f"生成 Canvas: {company_name} ({stock_code})")
    
    # 提取数据
    if report_path and os.path.exists(report_path):
        data = extract_data_from_report(report_path)
        print(f"从报告提取数据: {report_path}")
    else:
        data = {
            "current_price": "待补充",
            "target_price": "待补充",
            "rating": "待评估",
            "risks": ["待分析"],
            "catalysts": ["待分析"],
        }
        print("使用默认数据模板")
    
    # 生成 Canvas
    canvas = create_investment_canvas(company_name, stock_code, data)
    
    # 保存文件
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{company_name}-综合投资价值分析.canvas")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(canvas, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Canvas 已保存: {output_file}")
    print(f"   节点数: {len(canvas['nodes'])}")
    print(f"   连接数: {len(canvas['edges'])}")


if __name__ == "__main__":
    main()
