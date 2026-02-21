#!/usr/bin/env python3
"""
GitHub 数据管理器
用于读写 wenchang-data 仓库的数据
"""
import os
import json
import base64
import requests
from datetime import datetime

# 配置
TOKEN = os.getenv('GITHUB_TOKEN', '')
USERNAME = os.getenv('GITHUB_USERNAME', 'alandan97')
DATA_REPO = os.getenv('DATA_REPO', 'wenchang-data')
SITE_REPO = os.getenv('SITE_REPO', 'wenchang-site')

BASE_URL = 'https://api.github.com'
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

class GitHubDataManager:
    def __init__(self):
        self.token = TOKEN
        self.username = USERNAME
        self.data_repo = DATA_REPO
        self.site_repo = SITE_REPO
        
    def _request(self, method, endpoint, data=None):
        """发送 GitHub API 请求"""
        url = f'{BASE_URL}{endpoint}'
        try:
            if method == 'GET':
                response = requests.get(url, headers=HEADERS, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=HEADERS, json=data, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=HEADERS, timeout=30)
            else:
                response = requests.request(method, url, headers=HEADERS, json=data, timeout=30)
            
            if response.status_code in [200, 201]:
                return response.json() if response.text else True
            elif response.status_code == 404:
                return None
            else:
                print(f'API Error: {response.status_code} - {response.text}')
                return None
        except Exception as e:
            print(f'Request Error: {e}')
            return None
    
    def get_file(self, path, repo=None):
        """获取文件内容"""
        repo = repo or self.data_repo
        endpoint = f'/repos/{self.username}/{repo}/contents/{path}'
        result = self._request('GET', endpoint)
        if result and 'content' in result:
            import base64
            return base64.b64decode(result['content']).decode('utf-8')
        return None
    
    def get_file_sha(self, path, repo=None):
        """获取文件 SHA（用于更新）"""
        repo = repo or self.data_repo
        endpoint = f'/repos/{self.username}/{repo}/contents/{path}'
        result = self._request('GET', endpoint)
        return result.get('sha') if result else None
    
    def create_or_update_file(self, path, content, message, repo=None):
        """创建或更新文件"""
        repo = repo or self.data_repo
        endpoint = f'/repos/{self.username}/{repo}/contents/{path}'
        
        # 获取现有文件 SHA（如果存在）
        sha = self.get_file_sha(path, repo)
        
        # 编码内容
        if isinstance(content, dict):
            content = json.dumps(content, ensure_ascii=False, indent=2)
        content_bytes = content.encode('utf-8')
        content_b64 = base64.b64encode(content_bytes).decode('utf-8')
        
        data = {
            'message': message,
            'content': content_b64
        }
        if sha:
            data['sha'] = sha
        
        return self._request('PUT', endpoint, data)
    
    def delete_file(self, path, message, repo=None):
        """删除文件"""
        repo = repo or self.data_repo
        sha = self.get_file_sha(path, repo)
        if not sha:
            return False
        
        endpoint = f'/repos/{self.username}/{repo}/contents/{path}'
        data = {
            'message': message,
            'sha': sha
        }
        return self._request('DELETE', endpoint, data)
    
    def list_files(self, path='', repo=None):
        """列出目录文件"""
        repo = repo or self.data_repo
        endpoint = f'/repos/{self.username}/{repo}/contents/{path}'
        return self._request('GET', endpoint)
    
    # ========== 业务方法 ==========
    
    def save_policy(self, policy_data):
        """保存政策数据"""
        date = datetime.now()
        year = date.strftime('%Y')
        month = date.strftime('%m')
        filename = f"{policy_data.get('id', 'unknown')}.json"
        path = f"policies/{year}/{month}/{filename}"
        
        return self.create_or_update_file(
            path, 
            policy_data, 
            f"Add policy: {policy_data.get('title', 'Unknown')}"
        )
    
    def save_case(self, case_data):
        """保存案例数据"""
        case_id = case_data.get('id', 'unknown')
        path = f"cases/{case_id}.json"
        
        return self.create_or_update_file(
            path,
            case_data,
            f"Add/Update case: {case_data.get('name', 'Unknown')}"
        )
    
    def save_analysis(self, case_id, analysis_data):
        """保存案例分析"""
        path = f"analysis/{case_id}.json"
        
        return self.create_or_update_file(
            path,
            analysis_data,
            f"Add analysis for: {case_id}"
        )
    
    def update_stats(self, stats_data):
        """更新统计数据"""
        path = 'stats/progress.json'
        
        # 获取现有数据合并
        existing = self.get_file(path)
        if existing:
            try:
                existing_data = json.loads(existing)
                existing_data.update(stats_data)
                existing_data['last_update'] = datetime.now().isoformat()
                stats_data = existing_data
            except:
                pass
        
        return self.create_or_update_file(
            path,
            stats_data,
            f"Update stats: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
    
    def get_all_cases(self):
        """获取所有案例"""
        files = self.list_files('cases')
        if not files:
            return []
        
        cases = []
        for file in files:
            if file.get('name', '').endswith('.json'):
                content = self.get_file(f"cases/{file['name']}")
                if content:
                    try:
                        cases.append(json.loads(content))
                    except:
                        pass
        return cases
    
    def get_all_policies(self):
        """获取所有政策"""
        # 递归获取所有政策文件
        all_policies = []
        
        years = self.list_files('policies')
        if not years:
            return all_policies
        
        for year_item in years:
            if year_item.get('type') != 'dir':
                continue
            year = year_item['name']
            months = self.list_files(f"policies/{year}")
            
            if not months:
                continue
            
            for month_item in months:
                if month_item.get('type') != 'dir':
                    continue
                month = month_item['name']
                files = self.list_files(f"policies/{year}/{month}")
                
                if not files:
                    continue
                
                for file in files:
                    if file.get('name', '').endswith('.json'):
                        content = self.get_file(f"policies/{year}/{month}/{file['name']}")
                        if content:
                            try:
                                all_policies.append(json.loads(content))
                            except:
                                pass
        
        return all_policies
    
    def trigger_site_deploy(self):
        """触发网站仓库的 GitHub Actions 重新部署"""
        # 创建一个空提交来触发部署
        readme = self.get_file('README.md', self.site_repo) or '# Wenchang Site'
        return self.create_or_update_file(
            'README.md',
            readme + '\n',
            f'Trigger deploy: {datetime.now().isoformat()}',
            self.site_repo
        )


if __name__ == '__main__':
    # 测试连接
    manager = GitHubDataManager()
    
    print('Testing GitHub API connection...')
    
    # 测试获取仓库信息
    endpoint = f'/repos/{manager.username}/{manager.data_repo}'
    result = manager._request('GET', endpoint)
    
    if result:
        print(f"✅ Connected to GitHub!")
        print(f"   Repository: {result.get('full_name')}")
        print(f"   URL: {result.get('html_url')}")
        
        # 测试写入
        test_data = {
            'test': True,
            'timestamp': datetime.now().isoformat(),
            'message': 'GitHub API test successful'
        }
        
        result = manager.create_or_update_file(
            'test/connection.json',
            test_data,
            'Test GitHub API connection'
        )
        
        if result:
            print("✅ Write test successful!")
        else:
            print("❌ Write test failed")
    else:
        print("❌ Failed to connect to GitHub")
        print("   Please check your token and repository settings")
