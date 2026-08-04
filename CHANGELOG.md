# Changelog

## 2026-08-04 (R2)
- **安全**: npm audit 0 vulns — 升级 Next.js 14.2.35→15.5.22 (修复 2 HIGH + 13 MODERATE 漏洞)
- **安全**: 升级 React 18→19, React-DOM 18→19, @types/react 18→19
- **安全**: 添加 npm overrides 强制 postcss≥8.5.0, sharp≥0.35.0
- **修复**: 修复 memories/page.tsx 中 if-else 语法导致 Next 15 构建失败
- **健康**: 全端点扫描 7/7 通过
- **提交**: [本次] - security: upgrade Next.js 15 + React 19, fix build

## 2026-08-04 (R1)
- **维护**: 全端点健康扫描 7/7 通过（首次扫描出现瞬时网络抖动后自愈）
- **修复**: 添加 `venv311/` 到 `.gitignore`，避免 1.3G 虚拟环境目录被跟踪
- **审计**: npm audit 发现 2 个 HIGH 级别漏洞（Next.js 14.2.35 → 需跨大版本升级至 16.x，暂缓）
- **提交**: bb6a1d7 - chore: add venv311/ to .gitignore
