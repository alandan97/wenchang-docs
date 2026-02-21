# 文创指南项目

文创文旅政策与案例平台 - 汇聚政策文件与成功案例，为文创文旅从业者提供专业决策支持

## 项目架构

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  wenchang-data  │  │ wenchang-site   │  │ wenchang-docs   │
│  数据仓库       │  │  网站展示       │  │  文档资料       │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    政策/案例数据        GitHub Pages         代码/配置/记录
```

## 仓库列表

| 仓库 | 用途 | 链接 |
|------|------|------|
| **wenchang-data** | 数据存储（政策、案例、分析） | https://github.com/alandan97/wenchang-data |
| **wenchang-site** | 网站展示（GitHub Pages） | https://github.com/alandan97/wenchang-site |
| **wenchang-docs** | 项目文档和配置 | https://github.com/alandan97/wenchang-docs |
| **wenchang-code** | 源码和脚本 | https://github.com/alandan97/wenchang-code |

## 在线访问

🌐 **网站**: https://alandan97.github.io/wenchang-site

## 项目数据

- 📜 政策文件：200+ / 目标 1000
- 🏆 成功案例：180+ / 目标 1000
- 📊 总体进度：约 20%
- 🗺️ 覆盖省份：34个

## 技术栈

- **数据收集**: Python + GitHub API
- **前端展示**: Next.js + Tailwind CSS
- **部署**: GitHub Pages
- **自动化**: GitHub Actions + Cron

## 自动化流程

每小时自动执行：
1. 收集政策和案例数据
2. 推送到 wenchang-data 仓库
3. 更新统计数据
4. 触发网站重新部署

## 项目文档

- [AGENTS.md](https://github.com/alandan97/wenchang-docs/blob/main/AGENTS.md) - 工作规范
- [IDENTITY.md](https://github.com/alandan97/wenchang-docs/blob/main/IDENTITY.md) - 身份配置
- [SOUL.md](https://github.com/alandan97/wenchang-docs/blob/main/SOUL.md) - 性格设定
- [github_manager.py](https://github.com/alandan97/wenchang-docs/blob/main/github_manager.py) - GitHub API 管理器
- [collect_to_github.py](https://github.com/alandan97/wenchang-docs/blob/main/collect_to_github.py) - 数据收集脚本

## 更新日志

- 2025-02-21: 项目初始化，完成 GitHub 架构部署
- 2025-02-21: 启用自动化数据收集

---

© 2025 文旅智库
