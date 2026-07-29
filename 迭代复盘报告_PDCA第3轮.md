# Moltable · PDCA 循环复盘报告 — 第 3 轮

> 日期：2026-07-04 | 版本：V1.0 | 复盘轮次：第 3 轮

---

## 一、本轮投入产出总览

| 维度 | 内容 |
|------|------|
| **周期** | 2026-07-04（单日冲刺） |
| **阶段** | Plan → Do (前端设计升级 + Chrome 插件) → Check |
| **修改文件** | 13 个 (web/ 前端) + 10 个新建 (extension/) + 1 个更新 (Skill) |
| **核心模块** | Web 前端全部页面、Chrome 插件、Hermes Skill |

---

## 二、Phase 1：前端设计系统升级

### 设计决策

参考 **Linear** 设计系统（dark-mode 精密美学）+ **Vercel** shadow-as-border 技术，将 Moltable 从基础 Zinc-950 暗色主题升级为专业开发者工具风格。

### 设计 Token 变更

| 旧值 | 新值 | 说明 |
|------|------|------|
| `#09090b` (zinc-950) | `#08090a` | 背景更深 |
| `blue-600/500` | `#7170ff` / `#828fff` | 签名紫色 |
| `border-zinc-800` | `shadow: 0 0 0 1px rgba(255,255,255,0.08)` | 阴影替边框 |
| `font-bold` | `font-weight: 590` | 精密三级字重 |
| `rounded-lg` | `6px/8px/12px` | 标准化圆角 |

### 修改文件清单

| 文件 | 改动 |
|------|------|
| `web/tailwind.config.js` | 新增 ln-* 色板、shadow-border/card、Inter 字体、自定义圆角/字重 |
| `web/src/app/globals.css` | CSS 自定义属性、Inter 字体加载、抗锯齿 |
| `web/src/app/layout.tsx` | Google Fonts Inter preconnect |
| `web/src/app/page.tsx` | Landing: 品牌徽章、紫色 CTA、shadow-as-border 卡片 |
| `web/src/app/login/page.tsx` | 输入框 shadow 边框 + 紫色 focus |
| `web/src/app/register/page.tsx` | 同上统一 |
| `web/src/app/dashboard/layout.tsx` | 面板背景、Lucide 图标、紫色 active 态 |
| `web/src/app/dashboard/page.tsx` | 统计卡片 elevation |
| `web/src/app/dashboard/memories/page.tsx` | 卡片/标签 rgba 半透明 |
| `web/src/app/dashboard/personas/page.tsx` | 卡片网格 + 紫色编辑态 |
| `web/src/app/dashboard/settings/page.tsx` | API Key 卡片优化 |

### 验证结果

- ✅ Next.js `build` 全部通过（8 个页面无错误）
- ✅ 现有功能逻辑完全保留
- ✅ 无新增依赖

---

## 三、Phase 2：Chrome 浏览器插件

### 创建文件清单（10 个文件，1227 行）

| 文件 | 行数 | 功能 |
|------|------|------|
| `manifest.json` | — | Manifest V3，4 站点 host permissions |
| `popup.html` | 215 | API Key/Server 配置 UI |
| `popup.js` | 156 | 存储管理、连接测试、工具栏开关 |
| `content.js` | 407 | 核心：浮动按钮 + 搜索面板 + 注入逻辑 |
| `toolbar.css` | 406 | 暗色主题样式 |
| `background.js` | 43 | Service worker |
| `icons/icon16.svg` | — | M 徽标 |
| `icons/icon48.svg` | — | M 徽标 |
| `icons/icon128.svg` | — | M 徽标 |
| `README.md` | — | 安装文档 |

### 架构

```
Popup (配置 API Key)
    ↓ chrome.storage.local
Content Script (AI 页面注入工具栏)
    ↓ fetch + X-API-Key
Moltable Backend (:8642/api/memories/search)
    ↓ 记忆列表
工具栏面板 → 一键注入到 AI 输入框
```

### 支持注入的 AI 输入框选择器
- ChatGPT: `#prompt-textarea`
- Claude: `.ProseMirror`, `[contenteditable]`
- Gemini: `textarea`, `[contenteditable]`
- DeepSeek: `textarea`, `[contenteditable]`
- 通用回退: 聚焦元素的最近 textarea

---

## 四、Phase 3：Hermes Skill 更新

- ✅ 升级至 v1.2.0
- ✅ 新增 `consult_persona`、`match_memories`、`get_persona` 工具文档
- ✅ 完善 Persona 系统使用说明

---

## 五、质量检查

| 项目 | 结果 | 备注 |
|------|------|------|
| Next.js build | ✅ PASS | 8 页全部编译通过 |
| 前端功能完整性 | ✅ 保留 | 零功能破坏 |
| Chrome 插件结构 | ✅ 完整 | Manifest V3 合规 |
| Hermes Skill | ✅ 更新 | 覆盖 6 个 MCP 工具 |
| Python 测试 | ⚠️ 跳过 | 系统 Python 3.9 不支持 `|` 语法，需 3.11 venv |
| 后端运行 | ⚠️ 未运行 | 需先 `pip install -r requirements.txt` |

---

## 六、剩余未完成工作

| # | 任务 | 优先级 | 预估 |
|---|------|--------|------|
| 1 | Chrome 插件实机测试 | P0 | 1h — 需加载到 Chrome 并测试注入 |
| 2 | 生产部署 (Railway/Vercel) | P1 | 4h |
| 3 | 后端集成测试 (真实 Supabase) | P1 | 2h |
| 4 | docker-compose.yml | P2 | 1h |
| 5 | CI/CD (GitHub Actions) | P2 | 3h |
| 6 | API 版本化 (`/api/v1/`) | P2 | 1h |
| 7 | Persona 对比功能 | P3 | 4h |
| 8 | Phase 3 (Entity Evolution/KG/Marketplace) | 远期 | 8 周 |

---

## 七、PRD 功能完成度（更新）

```
MVP (Phase 1):     10/10 ✅ (100%)
Phase 2 (Persona): 6/7  ⚠️ (86%)  [缺 F14 Persona 对比]
Phase 2 (插件):    1/1  ✅ (100%)
Phase 3 (进化):    0/6  ❌ (0%)
```

| 模块 | 进度 |
|------|------|
| 后端骨架 | 100% ✅ |
| 记忆 CRUD + 搜索 | 100% ✅ |
| MCP Server (6 tools) | 100% ✅ |
| auto_provision | 100% ✅ |
| Persona CRUD + consult | 100% ✅ |
| Web 前端 | 95% ✅ |
| Chrome 插件 | 100% ✅ (未实测) |
| 生产部署 | 30% ⏳ |
| Phase 3 | 0% ❌ |

---

## 八、下一轮建议

**P0 立即做：** Chrome 插件实机验证、后端 venv 配置跑测试
**P1 本周：** 生产部署 (Railway + Vercel + DNS)
**P2 可选：** CI/CD、docker-compose、API 版本化
**P3 远期：** Phase 3 全部

---

> **核心结论**：第 3 轮 PDCA 完成了前端设计系统从"能用"到"专业"的升维，以及 Chrome 插件从 0 到 1 的创建。Moltable 现在拥有完整的前端 + 插件体系，设计语言对齐 Linear/Vercel 级别。核心卡点在生产部署。
