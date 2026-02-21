#!/usr/bin/env python3
"""
生成带图表的周报/月报HTML
"""

import json
from datetime import datetime

def generate_chart_html(stats: dict, title: str, period: str) -> str:
    """生成带图表的HTML报告"""
    
    token_data = stats.get("token_usage", [])
    file_data = stats.get("file_count", [])
    task_data = stats.get("task_count", [])
    
    dates = [d["date"][-5:] for d in token_data]  # 取 MM-DD
    tokens = [d["value"] for d in token_data]
    files = [d["value"] for d in file_data]
    tasks = [d["value"] for d in task_data]
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        h1 {{
            color: #8B1E1E;
            font-size: 32px;
            margin-bottom: 10px;
        }}
        .period {{
            color: #666;
            font-size: 16px;
        }}
        .chart-container {{
            background: white;
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .chart-title {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 20px;
            padding-left: 10px;
            border-left: 4px solid #8B1E1E;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .stat-value {{
            font-size: 28px;
            font-weight: 700;
            color: #8B1E1E;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 {title}</h1>
        <div class="period">{period}</div>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{sum(tokens):,}</div>
            <div class="stat-label">总Token消耗</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{sum(files):,}</div>
            <div class="stat-label">新增文件</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{sum(tasks):,}</div>
            <div class="stat-label">完成任务</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(token_data)}</div>
            <div class="stat-label">工作天数</div>
        </div>
    </div>
    
    <div class="chart-container">
        <div class="chart-title">📈 Token消耗趋势</div>
        <canvas id="tokenChart" height="100"></canvas>
    </div>
    
    <div class="chart-container">
        <div class="chart-title">📁 文件增长趋势</div>
        <canvas id="fileChart" height="100"></canvas>
    </div>
    
    <div class="chart-container">
        <div class="chart-title">✅ 任务完成趋势</div>
        <canvas id="taskChart" height="100"></canvas>
    </div>
    
    <script>
        const dates = {json.dumps(dates)};
        const tokens = {json.dumps(tokens)};
        const files = {json.dumps(files)};
        const tasks = {json.dumps(tasks)};
        
        // Token Chart
        new Chart(document.getElementById('tokenChart'), {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [{{
                    label: 'Token消耗',
                    data: tokens,
                    borderColor: '#8B1E1E',
                    backgroundColor: 'rgba(139, 30, 30, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});
        
        // File Chart
        new Chart(document.getElementById('fileChart'), {{
            type: 'bar',
            data: {{
                labels: dates,
                datasets: [{{
                    label: '新增文件',
                    data: files,
                    backgroundColor: '#C89B3C',
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});
        
        // Task Chart
        new Chart(document.getElementById('taskChart'), {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [{{
                    label: '完成任务',
                    data: tasks,
                    borderColor: '#2D5A4A',
                    backgroundColor: 'rgba(45, 90, 74, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    return html


if __name__ == "__main__":
    # 示例：生成测试图表
    test_stats = {
        "token_usage": [
            {"date": "2026-02-14", "value": 12000},
            {"date": "2026-02-15", "value": 15000},
            {"date": "2026-02-16", "value": 8000},
            {"date": "2026-02-17", "value": 20000},
            {"date": "2026-02-18", "value": 18000},
            {"date": "2026-02-19", "value": 22000},
            {"date": "2026-02-20", "value": 15000},
        ],
        "file_count": [
            {"date": "2026-02-14", "value": 5},
            {"date": "2026-02-15", "value": 8},
            {"date": "2026-02-16", "value": 3},
            {"date": "2026-02-17", "value": 12},
            {"date": "2026-02-18", "value": 10},
            {"date": "2026-02-19", "value": 15},
            {"date": "2026-02-20", "value": 8},
        ],
        "task_count": [
            {"date": "2026-02-14", "value": 3},
            {"date": "2026-02-15", "value": 5},
            {"date": "2026-02-16", "value": 2},
            {"date": "2026-02-17", "value": 6},
            {"date": "2026-02-18", "value": 4},
            {"date": "2026-02-19", "value": 7},
            {"date": "2026-02-20", "value": 5},
        ]
    }
    
    html = generate_chart_html(test_stats, "第8周工作总结", "2026-02-14 ~ 2026-02-20")
    
    with open("/root/.openclaw/workspace/weekly_report_chart.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("✅ 周报图表已生成: weekly_report_chart.html")
