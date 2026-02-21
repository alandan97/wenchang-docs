#!/usr/bin/env python3
"""
任务记录管理器
记录每日任务执行情况，生成周报月报
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

RECORDS_FILE = "/root/.openclaw/workspace/task_records.json"

class TaskRecorder:
    """任务记录管理器"""
    
    def __init__(self):
        self.records = self._load_records()
    
    def _load_records(self) -> dict:
        """加载记录文件"""
        if os.path.exists(RECORDS_FILE):
            with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "version": "1.0",
            "daily_records": [],
            "weekly_summaries": [],
            "monthly_summaries": [],
            "stats": {
                "token_usage": [],
                "workspace_size": [],
                "file_count": [],
                "task_count": []
            }
        }
    
    def _save_records(self):
        """保存记录文件"""
        with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
    
    def add_daily_record(self, date: str, tasks: list, token_usage: int, 
                        workspace_size: str, file_count: int, notes: str = ""):
        """添加每日记录"""
        record = {
            "date": date,
            "tasks": tasks,
            "token_usage": token_usage,
            "workspace_size": workspace_size,
            "file_count": file_count,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        # 检查是否已存在该日期的记录
        existing = [r for r in self.records["daily_records"] if r["date"] == date]
        if existing:
            # 更新现有记录
            idx = self.records["daily_records"].index(existing[0])
            self.records["daily_records"][idx] = record
        else:
            self.records["daily_records"].append(record)
        
        # 更新统计数据
        self.records["stats"]["token_usage"].append({"date": date, "value": token_usage})
        self.records["stats"]["workspace_size"].append({"date": date, "value": workspace_size})
        self.records["stats"]["file_count"].append({"date": date, "value": file_count})
        self.records["stats"]["task_count"].append({"date": date, "value": len(tasks)})
        
        self._save_records()
        print(f"✅ 已记录 {date} 的任务执行情况")
    
    def generate_weekly_summary(self, year: int, week: int) -> dict:
        """生成周报"""
        # 获取该周的所有日期
        start_date = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w').date()
        week_dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') 
                      for i in range(7)]
        
        # 筛选该周的记录
        week_records = [r for r in self.records["daily_records"] 
                       if r["date"] in week_dates]
        
        if not week_records:
            return None
        
        # 汇总数据
        all_tasks = []
        total_tokens = 0
        total_files = 0
        
        for r in week_records:
            all_tasks.extend(r["tasks"])
            total_tokens += r.get("token_usage", 0)
            total_files += r.get("file_count", 0)
        
        # 去重任务
        unique_tasks = list(set(all_tasks))
        
        summary = {
            "year": year,
            "week": week,
            "period": f"{week_dates[0]} ~ {week_dates[-1]}",
            "total_tasks": len(unique_tasks),
            "total_tokens": total_tokens,
            "total_files": total_files,
            "daily_records": week_records,
            "key_tasks": unique_tasks[:10],  # 前10个关键任务
            "generated_at": datetime.now().isoformat()
        }
        
        # 保存周报
        self.records["weekly_summaries"].append(summary)
        self._save_records()
        
        return summary
    
    def generate_monthly_summary(self, year: int, month: int) -> dict:
        """生成月报"""
        # 获取该月的所有日期
        month_str = f"{year}-{month:02d}"
        month_records = [r for r in self.records["daily_records"] 
                        if r["date"].startswith(month_str)]
        
        if not month_records:
            return None
        
        # 汇总数据
        all_tasks = []
        total_tokens = 0
        total_files = 0
        
        for r in month_records:
            all_tasks.extend(r["tasks"])
            total_tokens += r.get("token_usage", 0)
            total_files += r.get("file_count", 0)
        
        # 去重任务
        unique_tasks = list(set(all_tasks))
        
        # 计算统计数据
        token_data = [r.get("token_usage", 0) for r in month_records]
        avg_tokens = sum(token_data) / len(token_data) if token_data else 0
        max_tokens = max(token_data) if token_data else 0
        min_tokens = min(token_data) if token_data else 0
        
        summary = {
            "year": year,
            "month": month,
            "period": month_str,
            "total_days": len(month_records),
            "total_tasks": len(unique_tasks),
            "total_tokens": total_tokens,
            "avg_daily_tokens": round(avg_tokens, 2),
            "max_daily_tokens": max_tokens,
            "min_daily_tokens": min_tokens,
            "total_files": total_files,
            "daily_records": month_records,
            "key_tasks": unique_tasks[:15],  # 前15个关键任务
            "stats": self.records["stats"],
            "generated_at": datetime.now().isoformat()
        }
        
        # 保存月报
        self.records["monthly_summaries"].append(summary)
        self._save_records()
        
        return summary
    
    def get_stats_for_chart(self, days: int = 30) -> dict:
        """获取用于图表的统计数据"""
        stats = self.records["stats"]
        
        # 取最近N天的数据
        result = {
            "token_usage": stats["token_usage"][-days:] if len(stats["token_usage"]) > days else stats["token_usage"],
            "file_count": stats["file_count"][-days:] if len(stats["file_count"]) > days else stats["file_count"],
            "task_count": stats["task_count"][-days:] if len(stats["task_count"]) > days else stats["task_count"],
        }
        
        return result


def get_workspace_stats():
    """获取工作空间统计信息"""
    import subprocess
    
    stats = {
        "workspace_size": "0M",
        "file_count": 0,
        "wenlu_app_size": "0M"
    }
    
    try:
        # 获取 workspace 总大小
        result = subprocess.run(
            ["du", "-sh", "/root/.openclaw/workspace"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            stats["workspace_size"] = result.stdout.split()[0]
        
        # 获取 wenlu-app 大小
        result = subprocess.run(
            ["du", "-sh", "/root/.openclaw/workspace/wenlu-app"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            stats["wenlu_app_size"] = result.stdout.split()[0]
        
        # 获取文件总数
        result = subprocess.run(
            ["find", "/root/.openclaw/workspace", "-type", "f"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            stats["file_count"] = len(result.stdout.strip().split('\n'))
        
    except Exception as e:
        print(f"⚠️ 获取存储统计失败: {e}")
    
    return stats


def get_session_token_usage():
    """获取当前会话的 token 使用情况"""
    # 尝试从网关获取 session 统计
    try:
        import urllib.request
        import urllib.error
        
        # 网关默认地址
        gateway_url = "ws://127.0.0.1:18789"
        
        # 尝试获取 sessions 列表（如果有 HTTP API）
        # 由于网关主要是 WebSocket，这里使用 session_status 工具的概念
        # 实际 token 统计需要通过网关暴露的接口
        
        # 备选方案：读取环境变量或本地缓存的统计
        token_cache_file = "/root/.openclaw/workspace/.token_stats.json"
        if os.path.exists(token_cache_file):
            with open(token_cache_file, 'r') as f:
                cache = json.load(f)
                today = datetime.now().strftime('%Y-%m-%d')
                return cache.get(today, 0)
    except Exception as e:
        print(f"⚠️ 获取 token 统计失败: {e}")
    
    return 0


def estimate_token_usage(task_count: int, avg_tokens_per_task: int = 5000) -> int:
    """基于任务数量估算 token 使用量
    
    Args:
        task_count: 任务数量
        avg_tokens_per_task: 每个任务的平均 token 消耗（默认 5000）
    
    Returns:
        估算的 token 总数
    """
    return task_count * avg_tokens_per_task


def update_token_stats(usage: int):
    """更新今日 token 使用统计到缓存文件"""
    token_cache_file = "/root/.openclaw/workspace/.token_stats.json"
    today = datetime.now().strftime('%Y-%m-%d')
    
    cache = {}
    if os.path.exists(token_cache_file):
        with open(token_cache_file, 'r') as f:
            cache = json.load(f)
    
    # 累加今日用量
    cache[today] = cache.get(today, 0) + usage
    
    with open(token_cache_file, 'w') as f:
        json.dump(cache, f, indent=2)
    
    return cache[today]


def record_today(tasks: list, token_usage: int = None, 
                 workspace_size: str = None, file_count: int = None,
                 use_estimate: bool = True):
    """记录今天的任务，自动获取存储统计
    
    Args:
        tasks: 任务列表
        token_usage: 指定 token 使用量（为 None 则自动获取或估算）
        workspace_size: 工作空间大小
        file_count: 文件数量
        use_estimate: 是否使用估算值（当无法获取实际值时）
    """
    recorder = TaskRecorder()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 自动获取存储统计（如果未提供）
    if workspace_size is None or file_count is None:
        stats = get_workspace_stats()
        workspace_size = workspace_size or stats["workspace_size"]
        file_count = file_count or stats["file_count"]
    
    # 获取 token 使用（如果未提供）
    if token_usage is None:
        token_usage = get_session_token_usage()
        # 如果获取不到实际值，使用估算
        if token_usage == 0 and use_estimate:
            token_usage = estimate_token_usage(len(tasks))
    
    recorder.add_daily_record(
        date=today,
        tasks=tasks,
        token_usage=token_usage,
        workspace_size=workspace_size,
        file_count=file_count
    )
    
    # 打印统计信息
    print(f"\n📊 今日统计:")
    print(f"   💾 存储占用: {workspace_size}")
    print(f"   📁 文件总数: {file_count}")
    print(f"   🔤 Token消耗: {token_usage:,} (估算)" if use_estimate and token_usage > 0 else f"   🔤 Token消耗: {token_usage:,}")


def generate_this_week_summary():
    """生成本周周报"""
    recorder = TaskRecorder()
    now = datetime.now()
    year, week, _ = now.isocalendar()
    
    summary = recorder.generate_weekly_summary(year, week)
    
    if summary:
        print(f"\n📊 第{week}周工作总结已生成")
        print(f"📅 周期: {summary['period']}")
        print(f"✅ 完成任务: {summary['total_tasks']} 项")
        print(f"📈 Token消耗: {summary['total_tokens']}")
        return summary
    else:
        print("⚠️ 本周暂无记录")
        return None


def generate_this_month_summary():
    """生成本月月报"""
    recorder = TaskRecorder()
    now = datetime.now()
    
    summary = recorder.generate_monthly_summary(now.year, now.month)
    
    if summary:
        print(f"\n📊 {now.month}月工作总结已生成")
        print(f"📅 工作天数: {summary['total_days']} 天")
        print(f"✅ 完成任务: {summary['total_tasks']} 项")
        print(f"📈 总Token消耗: {summary['total_tokens']}")
        print(f"📊 日均Token: {summary['avg_daily_tokens']}")
        return summary
    else:
        print("⚠️ 本月暂无记录")
        return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "record":
            # 自动获取统计并记录
            record_today(
                tasks=["完成任务1", "完成任务2"]
            )
        elif command == "today":
            # 记录今日实际任务（从命令行参数读取任务列表）
            task_list = sys.argv[2:] if len(sys.argv) > 2 else ["日常任务"]
            record_today(tasks=task_list, use_estimate=True)
        elif command == "token":
            # 手动添加 token 使用量
            if len(sys.argv) > 2:
                try:
                    usage = int(sys.argv[2])
                    update_token_stats(usage)
                    print(f"✅ 已添加 {usage:,} tokens 到今日统计")
                except ValueError:
                    print("❌ 请提供有效的数字: python task_recorder.py token 5000")
            else:
                # 显示今日 token 统计
                total = get_session_token_usage()
                print(f"📊 今日 Token 消耗: {total:,}")
        elif command == "weekly":
            generate_this_week_summary()
        elif command == "monthly":
            generate_this_month_summary()
    else:
        print("Usage: python task_recorder.py [record|today|token|weekly|monthly]")
        print("  record        - 使用示例数据记录今天")
        print("  today [任务...] - 记录今天（可附加任务列表）")
        print("  token [数量]  - 添加/查看 token 使用量")
        print("  weekly        - 生成本周周报")
        print("  monthly       - 生成本月月报")
