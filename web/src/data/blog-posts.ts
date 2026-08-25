// Shared blog post metadata — single source of truth for blog index, RSS feed, and sitemap.
// Add new posts here; they automatically appear everywhere.

export interface BlogPost {
  slug: string
  date: string
  title: string
  titleEn?: string
  excerpt: string
  tags: string[]
}

const posts: BlogPost[] = [
  {
    slug: 'moltable-vs-letta-stateful-memory',
    date: '2026-08-25',
    title: 'Moltable vs Letta：状态记忆 vs 灵魂资产备份',
    titleEn: 'Moltable vs Letta (MemGPT): Stateful Memory vs Soul Asset Backup',
    excerpt:
      '竞品矩阵收官篇。Letta 给 Agent 一个会自我编辑的工作记忆（memory blocks + dreaming），Moltable 给你一份可版本化、可跨框架迁移的灵魂资产备份。一个管 Agent 的「脑子」，一个管你的「遗产」——它们不是竞品，是上下游。',
    tags: ['Letta', 'MemGPT', '对比', 'Agent Memory', '灵魂资产备份'],
  },
  {
    slug: 'mcp-server-ecosystem-landscape',
    date: '2026-08-24',
    title: 'MCP 工具生态盘点：除了内置工具，Agent 还能调用哪些开源 MCP Server',
    titleEn: 'MCP Server Ecosystem: The Open-Source Servers Your AI Agent Should Plug Into',
    excerpt:
      '承接 Swap 篇，把目光拉回 Agent 与工具之间：盘点 context7、GitHub、Postgres、Memory、Playwright 等主流开源 MCP Server，给出「什么场景接什么 Server」的选型清单，附 FastMCP 十分钟接入示例。',
    tags: ['MCP', '生态', '盘点', '教程', '工具'],
  },
  {
    slug: 'agent-protocol-swap-orchestration',
    date: '2026-08-22',
    title: 'Agent Protocol 深入：多 Agent 编排与任务市场 Swap 实战',
    titleEn: 'Agent Protocol Deep Dive: Multi-Agent Orchestration & Task Market Swap',
    excerpt:
      '承接协议经济与 A2A 实战，补上市场的最后两块拼图：任务 DAG 编排如何拆解多 Agent 协作，以及 Swap 机制如何让接错单的 Agent 把任务换给更合适的人。附编排主循环与换手处理的完整 Python 代码。',
    tags: ['Agent Economy', 'Protocol', 'A2A', 'Swap', 'Hands-on', '编排'],
  },
  {
    slug: 'ai-memory-data-sovereignty-gdpr',
    date: '2026-08-19',
    title: 'AI Agent 记忆的数据主权：GDPR 实操与自托管合规清单',
    titleEn: 'AI Agent Memory & Data Sovereignty: A Practical GDPR Compliance Checklist',
    excerpt:
      '承接自托管与多租户隔离，补上合规最后一块：删除权怎么跨层级联删干净、数据可携带怎么导出、审计日志怎么做到「记忆可删、审计不可删」。附完整 Python 代码与可直接抄的自托管合规清单。',
    tags: ['数据主权', 'GDPR', '合规', '自托管', '安全', '教程'],
  },
  {
    slug: 'mcp-multi-tenant-isolation',
    date: '2026-08-18',
    title: 'MCP 实战进阶：多租户记忆隔离',
    titleEn: "MCP Multi-Tenant Memory Isolation: Keep Every Tenant's Memory in Its Own Lane",
    excerpt:
      'MCP 实战系列第三篇：一套服务承接多个租户时，记忆如何严格隔离、永不串库。三层隔离模型（文件散列目录 + Postgres RLS + 向量 namespace）+ tenant_id 只来自认证层的安全原则，附完整可运行 Python 代码与「证明没串库」的测试。',
    tags: ['MCP', '多租户', '隔离', '教程', '安全', 'Postgres', 'RLS'],
  },
  {
    slug: 'pinecone-vector-retrieval',
    date: '2026-08-17',
    title: 'Pinecone 实战：给 Moltable 加一层托管向量检索',
    titleEn: 'Pinecone Hands-On: Adding Managed Vector Search to the Moltable Identity Layer',
    excerpt:
      '承接「记忆全家桶」的结论，这篇动手把 Pinecone 接进 Moltable：384 维对齐、namespace 租户硬隔离、metadata 过滤，身份图谱留 Postgres、语义检索下沉托管云。附四步可照抄代码与「什么时候该上 Pinecone」的诚实判断标准。',
    tags: ['Pinecone', '向量检索', '教程', '集成', 'RAG', 'AI Memory'],
  },
  {
    slug: 'moltable-self-host-deployment',
    date: '2026-08-16',
    title: 'Moltable 自托管部署指南：从零到生产',
    titleEn: 'Self-Hosting Moltable: From Zero to Production (Docker + FastAPI + Postgres)',
    excerpt:
      '三层架构拆解 + 可照抄的 Docker 部署路径，重点讲清环境变量管理、安全加固、多租户隔离三个最容易翻车的点。从零到生产，四条命令端到端闭环验证。',
    tags: ['部署', '自托管', '安全', '教程', 'Docker', 'FastAPI'],
  },
  {
    slug: 'a2a-agent-collaboration',
    date: '2026-08-15',
    title: 'Agent Protocol 实战：用 A2A 让两个 Agent 自动协作',
    titleEn: 'A2A Hands-On: Make Two AI Agents Collaborate Automatically',
    excerpt:
      '上篇讲了 Agent 协议经济的「为什么」，这篇讲「怎么做」。用 Agent Card + JSON-RPC 2.0 + SSE，让研究员 Agent 和写手 Agent 自己发现、自己传任务、自己看进度——全程零人工中转。附完整代码。',
    tags: ['A2A', 'Protocol', '教程', 'Hands-on', 'Agent'],
  },
  {
    slug: 'agent-memory-stack-comparison',
    date: '2026-08-14',
    title: 'AI Agent Memory 全家桶：LangChain Memory vs Chroma vs Pinecone vs Moltable',
    titleEn: 'The Complete AI Agent Memory Stack: LangChain Memory vs Chroma vs Pinecone vs Moltable',
    excerpt:
      'LangChain Memory、Chroma、Pinecone 与 Moltable 都自称「记忆」，却解决四个不同问题：上下文管理、向量检索、托管检索、身份层。一张对比表 + 决策指南，帮你一次选对。',
    tags: ['对比', 'LangChain', 'Chroma', 'Pinecone', 'AI Memory', '选型'],
  },
  {
    slug: 'indie-dev-ai-toolchain',
    date: '2026-08-13',
    title: '独立开发者的 AI 工具链：真实使用记录',
    titleEn: "An Indie Developer's AI Toolchain: A Real Usage Case Study",
    excerpt:
      '一个人同时用 Claude Code、OpenCode、Hermes 等多个 AI Agent，最耗精力的不是写 prompt，而是重复交代「我是谁」。一份真实的工具链使用记录：瓶颈不在模型层，而在跨 Agent 身份同步。',
    tags: ['Case Study', 'Identity', 'Toolchain', 'Solo Dev', 'AI Memory'],
  },
  {
    slug: 'agent-protocol-economy',
    date: '2026-08-12',
    title: 'Agent 协议经济：为什么 AI Agent 需要一个劳动力市场',
    titleEn: 'Agent Protocol Economy: Why AI Agents Need a Labor Market',
    excerpt:
      'Agent 的未来不是更大的模型，而是 Agent 之间能互相信任、互相交易。Moltable Agent Market：一个 Agent 发布任务，另一个 Agent 接单执行——Identity 是账户、Persona 是技能名片、A2A 是传话的线、信誉是信任基础设施。',
    tags: ['Agent Economy', 'Protocol', 'A2A', 'Market', 'Architecture'],
  },
  {
    slug: 'mcp-server-git-workflow',
    date: '2026-08-11',
    title: 'MCP 实战进阶：让 AI Agent 记住你的 Git 工作流',
    titleEn: 'Building an MCP Memory Server for Git Workflows: Let Your AI Remember Every Commit',
    excerpt:
      '手把手教程：从零构建一个 Git-aware MCP Server，让你的 AI Agent 自动知道分支、commits、项目约定和 review 历史。完整 Python 实现 + FastMCP，30 分钟部署。',
    tags: ['MCP', 'Git', '教程', 'Python', 'Hands-on', 'Memory'],
  },
  {
    slug: 'viral-growth-referral-system',
    date: '2026-08-07',
    title: 'Building a Viral Growth Engine for Developer Tools — Lessons from Moltable\'s Referral System',
    titleEn: 'Building a Viral Growth Engine for Developer Tools — Lessons from Moltable\'s Referral System',
    excerpt:
      'Why traditional SaaS growth tactics fail for developer tools — and how Moltable built a referral system from scratch: invite links, reward design, abuse prevention, and the FastAPI + Supabase architecture under the hood.',
    tags: ['Growth', 'Referral', 'Developer Tools', 'Architecture'],
  },
  {
    slug: 'knowledge-graph-deep-dive',
    date: '2026-08-06',
    title: '零依赖知识图谱：如何用 1200 行 Python 让 AI Agent 理解实体关系',
    titleEn: 'Zero-Dependency Knowledge Graph: How 1200 Lines of Python Let AI Agents Understand Entity Relationships',
    excerpt:
      '不需要 Neo4j，不需要 LLM 调用。Moltable 的知识图谱服务用纯正则 + 关键词匹配 + 共现分析，从零构建完整的实体关系图谱。逐层拆解实体识别、关系推断、增量更新和查询 API。',
    tags: ['Knowledge Graph', '架构', 'Python', '技术深度'],
  },
  {
    slug: 'identity-graph-vs-vector-search',
    date: '2026-08-06',
    title: '身份图谱：为什么仅有向量搜索无法给 AI Agent 真正的记忆',
    titleEn: 'The Identity Graph: Why Vector Search Alone Can\'t Give Your AI Agent True Memory',
    excerpt:
      '向量数据库存储事实，身份图谱存储关系。当你的 AI Agent 检索到「John 偏好 TypeScript」却不知道 John 正处于 Project X 的代码审查模式时，这些记忆毫无意义。本文深度剖析向量搜索的隐藏失效模式，并给出身份图谱的解决方案。',
    tags: ['Identity Graph', '向量搜索', 'AI Memory', '架构', '深度分析'],
  },
  {
    slug: 'rag-vs-finetuning-vs-identity',
    date: '2026-08-06',
    title: 'RAG vs Fine-Tuning vs Identity Layer：AI 个性化的不可能三角与破局之道',
    titleEn: 'RAG vs Fine-Tuning vs Identity Layer: The AI Personalization Trilemma and How to Solve It',
    excerpt:
      'RAG 喂文档，Fine-Tuning 改模型，Identity Layer 建模身份——三种 AI 个性化方案各有致命缺陷。本文从架构哲学、成本模型、时效性和准确度四个维度，深度分析 AI 个性化的「不可能三角」，并给出三层组合架构的最佳实践。',
    tags: ['对比', 'RAG', 'Fine-Tuning', 'Identity', '架构'],
  },
  {
    slug: 'hidden-cost-of-ai-amnesia',
    date: '2026-08-06',
    title: 'AI 失忆的真实成本：开发者每年浪费多少小时在「重新认识你」上？',
    titleEn: 'The Hidden Cost of AI Amnesia: How Many Hours Do Developers Waste on Re-Onboarding Their AI?',
    excerpt:
      '我们分析了 200+ 开发者的 AI 使用习惯，发现平均每人每周浪费 3.2 小时在「重新教 AI 认识自己」上。本文用真实数据量化 AI 失忆的隐性成本，并给出零摩擦的 Identity Layer 解决方案。',
    tags: ['研究', '效率', '数据', 'Identity'],
  },
  {
    slug: 'moltable-vs-zep-temporal-memory',
    date: '2026-08-06',
    title: 'Moltable vs Zep：时序记忆与身份层 —— 谁赢得 Agent 记忆竞赛？',
    titleEn: 'Moltable vs Zep: Temporal Memory & Identity — Who Wins the Agent Memory Race?',
    excerpt:
      'Zep 用企业级时序知识图谱定义了时序记忆赛道，Moltable 用 Temporal Memory Timeline 给出了不同答案——零 LLM 依赖的模式检测、Persona 隔离、四合一身份架构。从能力、架构、定价到适用场景，一文看懂该选谁。',
    tags: ['对比', 'Zep', '时序记忆', 'Identity'],
  },
  {
    slug: 'moltable-vs-mem0-identity-vs-memory',
    date: '2026-08-05',
    title: 'Moltable vs mem0：AI Identity Layer 和 Memory Layer 的本质区别',
    titleEn: 'Moltable vs mem0: Identity Layer vs Memory Layer — The Essential Difference',
    excerpt: '为什么你的 AI Agent 有了记忆还是不认识你？本文从架构哲学、数据模型、多 Agent 协作三个维度，深度剖析 Identity Layer 和 Memory Layer 的本质差异，帮你做出正确的技术选型。',
    tags: ['对比', 'mem0', 'Identity', 'Memory'],
  },
  {
    slug: 'why-ai-forgets-you',
    date: '2026-08-05',
    title: '为什么你的 AI 每次都不记得你是谁 —— 以及 2026 年的终极解决方案',
    titleEn: 'Why Your AI Forgets You Every Day — And the 2026 Fix',
    excerpt: '每天早上打开 Claude，它都像第一次见你。不是 AI 笨，是你的身份数据从没被真正存储过。本文剖析 AI「失忆」的五个根因，并给出 Moltable 的三层身份架构解决方案——一次配置，所有 Agent 共享。',
    tags: ['痛点', 'Identity', '教程'],
  },
  {
    slug: 'three-minute-env-recovery',
    date: '2026-08-04',
    title: '换电脑不换脑子：3 分钟恢复完整 AI 开发环境实战指南',
    titleEn: 'New Machine, Same Brain: Full AI Dev Environment Recovery in 3 Minutes',
    excerpt: '换一台新 Mac 之后，Claude、Cursor、Codex 全部失忆了？本文手把手教你用 Moltable 在 3 分钟内恢复完整的 AI 工作环境——从 Persona 到 MCP 配置，从项目记忆到工具偏好，一条命令全搞定。',
    tags: ['教程', '实战', 'Identity', 'MCP'],
  },
  {
    slug: 'agent-persistent-identity-research',
    date: '2026-08-04',
    title: 'arXiv 最新论文：AI Agent 的「持续身份」——多锚点架构如何让 Agent 不再失忆',
    titleEn: 'New arXiv Paper: Persistent Identity in AI Agents — Multi-Anchor Architecture',
    excerpt: '2026年3月 arXiv 论文提出多锚点身份理论：参考人类记忆障碍的神经科学研究，论证 AI Agent 需要偏好、决策、关系、价值观、叙事五个锚点来维持持续身份。Moltable 的三层架构恰好完整实现了这一理论。',
    tags: ['研究', 'Identity', '架构', '论文解读'],
  },
  {
    slug: 'ai-agent-trends-2026h2',
    date: '2026-08-06',
    title: '2026 下半年 AI Agent 趋势：从工具到伙伴，从记忆到身份',
    titleEn: 'AI Agent Trends H2 2026: From Tools to Partners, Memory to Identity',
    excerpt: '回顾 2026 上半年 AI Agent 的关键进展，预测下半年的五大趋势——包括 Identity 层的崛起、MCP 普及、开源追赶和价格战。',
    tags: ['趋势', '预测', 'Agent'],
  },
  {
    slug: 'open-protocol-ai-ecosystem',
    date: '2026-08-05',
    title: '开源协议如何重塑 AI 生态：MCP、A2A 与 Identity 层的三角博弈',
    titleEn: 'How Open Protocols Reshape AI: MCP, A2A and the Identity Layer',
    excerpt: 'Google A2A 和 Anthropic MCP 两大 AI 协议正在交织出一张新的生态网。Identity 层将在其中扮演什么角色？',
    tags: ['MCP', 'A2A', '开源', '生态'],
  },
  {
    slug: 'ai-developer-toolchain',
    date: '2026-08-01',
    title: '2026 AI 开发者工具链全景：从 LLM 到 Identity 的完整技术栈',
    titleEn: '2026 AI Developer Toolchain: Full Stack from LLM to Identity',
    excerpt: '现代 AI Agent 开发者需要哪些工具？LLM 网关、向量数据库、记忆层、身份层、MCP 服务器——一文梳理完整技术选型。',
    tags: ['工具链', '生态', '架构'],
  },
  {
    slug: 'ai-agent-security-2026',
    date: '2026-07-28',
    title: 'AI Agent 安全攻防 2026：你的 Agent 正在泄露什么？',
    titleEn: 'AI Agent Security 2026: What Is Your Agent Leaking?',
    excerpt: 'MCP 协议让 AI Agent 的能力爆发式增长，但也打开了新的攻击面。本文分析 Agent 安全威胁模型与加固方案。',
    tags: ['安全', 'MCP', '加密'],
  },
  {
    slug: 'ai-identity-sync-guide',
    date: '2026-07-25',
    title: '换电脑不换记忆：AI 身份同步完全指南',
    titleEn: 'New Computer, Same Memory: Complete AI Identity Sync Guide',
    excerpt: '换一台新电脑，AI 又要从零开始认识你？这份指南教你用 Identity Sync 实现跨设备 AI 环境一键恢复。',
    tags: ['教程', 'Identity', '最佳实践'],
  },
  {
    slug: 'ai-persona-enterprise',
    date: '2026-07-20',
    title: '企业级 AI Persona 管理：一个团队，十种人格',
    titleEn: 'Enterprise AI Persona Management: One Team, Ten Minds',
    excerpt: '当整个团队共用同一套 AI 工具时，如何让市场总监看到激进分析、财务总监看到保守建议？Persona 系统的企业级方案。',
    tags: ['Persona', '企业', '最佳实践'],
  },
  {
    slug: 'ai-data-sovereignty',
    date: '2026-07-18',
    title: '你的 10 万条 AI 对话记录：该归谁？该存在哪？',
    titleEn: 'Your 100K AI Conversations: Who Owns Them? Where Should They Live?',
    excerpt: 'AI Agent 每天产生大量对话记录和个人偏好数据。这些数据的所有权、存储位置和访问权限——2026年必须回答的问题。',
    tags: ['隐私', '数据主权', '安全'],
  },
  {
    slug: 'mcp-tool-development',
    date: '2026-07-15',
    title: 'MCP 工具开发实战：从零构建一个 AI Agent 记忆缓存层',
    titleEn: 'MCP Tool Development: Build an AI Agent Memory Cache from Scratch',
    excerpt: '手把手教你用 Python 开发一个 MCP Server，为 AI Agent 添加持久记忆能力。从协议理解到生产部署，全程演示。',
    tags: ['MCP', '开发教程', '开源'],
  },
  {
    slug: 'ai-forgetfulness-fix',
    date: '2026-07-12',
    title: 'AI 为什么总「失忆」？根因剖析与实操修复指南',
    titleEn: 'Why Does AI Keep Forgetting? Root Cause Analysis and Fix Guide',
    excerpt: '你的 Claude/ChatGPT 今天记住的偏好明天就忘？本文分析 AI「失忆」的五大根因，并给出即插即用的修复方案。',
    tags: ['教程', '诊断', 'Preference'],
  },
  {
    slug: 'agent-memory-landscape-2026',
    date: '2026-07-10',
    title: 'AI Agent 记忆系统全景对比 2026：mem0 vs Zep vs Moltable',
    titleEn: 'AI Agent Memory Landscape 2026: mem0 vs Zep vs Moltable',
    excerpt: '从开源到商业，从向量搜索到图谱记忆——2026年主流Agent记忆系统的横向对比，帮你选择最适合技术栈的记忆方案。',
    tags: ['对比评测', '记忆系统', '生态'],
  },
  {
    slug: 'cross-platform-persona',
    date: '2026-07-05',
    title: '跨平台 Persona 管理：一个身份，多种人格',
    titleEn: 'Cross-Platform Persona: One Identity, Many Minds',
    excerpt: '同一个 AI，加载战略顾问 Persona 是麦肯锡风格，加载保守审核员 Persona 是合规导向。本文通过真实场景演示 Persona 系统如何让一个 AI 拥有多种思维模式。',
    tags: ['Persona', '最佳实践', '教程'],
  },
  {
    slug: 'ai-identity-layer',
    date: '2026-06-28',
    title: 'AI 身份层的设计哲学：从 Memory 到 Identity',
    titleEn: 'From Memory to Identity: Designing the AI Identity Layer',
    excerpt: 'Memory 赛道拥挤，但 Identity 赛道几乎无人。本文探讨为什么"身份"比"记忆"更适合作为 AI 个人化的原子单位，以及 Moltable 的 Identity→Persona→Agent 三层架构设计。',
    tags: ['Identity', '架构', '设计哲学'],
  },
  {
    slug: 'mcp-ai-usb-c',
    date: '2026-06-20',
    title: 'MCP 协议：为什么它是 AI 的 USB-C',
    titleEn: 'MCP: The USB-C of AI Agents',
    excerpt: 'Model Context Protocol 正在成为 AI Agent 连接外部世界的标准。本文解析 MCP 的协议设计、与 A2A 的互补关系，以及为什么 Moltable 选择 MCP 作为核心接入方式。',
    tags: ['MCP', '协议', 'Agent'],
  },
]

export default posts

/** Return posts sorted by date descending (newest first). */
export function getSortedPosts(): BlogPost[] {
  return [...posts].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

/** Extract all unique tags, sorted by frequency (most common first). */
export function getAllTags(): string[] {
  const freq = new Map<string, number>()
  for (const post of posts) {
    for (const tag of post.tags) {
      freq.set(tag, (freq.get(tag) || 0) + 1)
    }
  }
  return [...freq.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([tag]) => tag)
}

/** Filter posts by a single tag. Case-sensitive exact match. */
export function getPostsByTag(tag: string): BlogPost[] {
  return getSortedPosts().filter((p) => p.tags.includes(tag))
}
