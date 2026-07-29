export type Lang = 'zh' | 'en'

export const translations = {
  zh: {
    nav: { features: '功能', pricing: '定价', about: '关于', docs: '文档', login: '登录', start: '免费开始' },
    hero: { badge: 'AI Identity Protocol', title: '你的 AI 为什么每次都要重新认识你？', subtitle: '一个身份，所有 AI 都认识你。不再重复。', desc: 'Moltable 是 AI 时代的身份层。在任何 AI 里加载你的 Moltable，AI 就自动认识你。' },
    features: {
      title: '核心能力',
      items: [
        { title: '跨 AI 身份', desc: '在 Hermes、Claude、ChatGPT 之间无缝切换，AI 永远认识你。' },
        { title: '自动配置', desc: '连接 Moltable 即完成配置。Agent 自动加载你的偏好、记忆和规则。' },
        { title: '多 Persona', desc: '创建不同的人格——战略顾问、审核员、创意伙伴，共享同一套记忆。' },
        { title: '渐进记忆', desc: '每次对话自动积累。30 天后，AI 比你自己更了解你的工作方式。' },
        { title: '你拥有数据', desc: '随时随地导出或删除全部数据。你的 AI 身份只属于你。' },
        { title: '开放协议', desc: '基于 MCP 开放标准。任何支持 MCP 的 Agent 都可以接入。' },
      ]
    },
    how: { title: '三步开始', steps: [{ title: '注册 Moltable', desc: '30 秒创建账号，获取 API Key。' },{ title: '加载 Skill', desc: '在 Hermes / Claude 中加载 Moltable Skill，输入 API Key。' },{ title: '开始工作', desc: 'AI 自动认识你。像往常一样工作，所有偏好自动同步。' }] },
    pricing: { title: '定价', free: { name: 'Free', price: '¥0', desc: '1 个身份 · 2 个 Persona · 100 条记忆 · 1 个 Agent · 基础 MCP', cta: '免费注册' }, pro: { name: 'Pro', price: '¥19/月', priceYearly: '¥149/年', priceYearlyMonthly: '¥12.4/月', desc: '3 个身份 · 10 个 Persona · 10,000 条记忆 · 5 个 Agent · 浏览器插件 · 优先支持', descShort: '10K 记忆 · 10 Persona · 万事俱备', cta: '开始试用', ctaYearly: '¥149/年 · 省 ¥79', badge: '最受欢迎' }, team: { name: 'Team', price: '¥39/月/人', desc: '10 个身份 · 无限 Persona · 50K 记忆 · 团队记忆库 · 管理面板', descShort: '团队协作 · 共享记忆', cta: '联系咨询' }, viewAll: '查看完整定价方案 →' },
    about: { title: '关于 Moltable', mission: 'Own your AI identity, not just your chats.', architecture: { title: '三层架构', layers: [{ name: 'Identity', desc: '用户本人 · 不可复制 · 拥有所有数据' },{ name: 'Persona', desc: '人格面具 · 行为模式 · 共享记忆' },{ name: 'Agent', desc: '执行体 · 工具调用 · 不拥有人格' }] }, opensource: '开源 MIT 协议 — 你的数据永远属于你。' },
    privacy: { title: '隐私与安全', items: [{ title: '加密存储', desc: '所有记忆在传输和存储中加密。API Key 使用 SHA-256 哈希存储。' },{ title: '你的数据你做主', desc: '随时导出或删除全部数据。我们不会用你的数据训练模型。' },{ title: '合规', desc: '遵守 GDPR 和《个人信息保护法》。' }] },
    footer: { product: '产品', resources: '资源', legal: '法律', copyright: 'Moltable · AI Identity Protocol' },
    dashboard: { demoBanner: '演示模式 — 注册后开始使用', stats: { memories: '记忆条目', personas: 'Persona', projects: '项目数', decisions: '决策记录' }, quickStart: '快速接入', getKey: '获取 API Key', step1: '创建 API Key', step2: '加载 Skill', step3: '开始工作' },
    common: { loading: '加载中...', empty: '暂无数据', save: '保存', cancel: '取消', delete: '删除', edit: '编辑', search: '搜索', add: '添加', confirm: '确定', openMenu: '打开菜单', closeMenu: '关闭菜单' },
  },
  en: {
    nav: { features: 'Features', pricing: 'Pricing', about: 'About', docs: 'Docs', login: 'Sign In', start: 'Get Started' },
    hero: { badge: 'AI Identity Protocol', title: 'Why does your AI have to relearn who you are every time?', subtitle: 'One identity. Every AI knows you. No repeats.', desc: 'Moltable is the identity layer for the AI age. Load your Moltable into any AI, and it instantly knows you.' },
    features: {
      title: 'Core Capabilities',
      items: [
        { title: 'Cross-AI Identity', desc: 'Seamlessly switch between Hermes, Claude, ChatGPT — your AI always knows you.' },
        { title: 'Auto-Provision', desc: 'Connect once, fully configured. Agents auto-load your preferences, memories, and rules.' },
        { title: 'Multi-Persona', desc: 'Create different personas — strategist, auditor, creative partner — sharing one memory base.' },
        { title: 'Progressive Memory', desc: 'Every conversation adds up. After 30 days, your AI knows your workflow better than you do.' },
        { title: 'You Own Your Data', desc: 'Export or delete everything anytime. Your AI identity belongs to you alone.' },
        { title: 'Open Protocol', desc: 'Built on MCP open standards. Any MCP-compatible agent can connect.' },
      ]
    },
    how: { title: 'Get Started in 3 Steps', steps: [{ title: 'Sign Up', desc: 'Create your account in 30 seconds. Get your API Key.' },{ title: 'Load the Skill', desc: 'Load Moltable Skill in Hermes / Claude. Enter your API Key.' },{ title: 'Start Working', desc: 'Your AI knows you instantly. Work as usual — all preferences sync automatically.' }] },
    pricing: { title: 'Pricing', free: { name: 'Free', price: '$0', desc: '1 Identity · 2 Personas · 100 memories · 1 Agent · Basic MCP', cta: 'Get Started' }, pro: { name: 'Pro', price: '$12/mo', priceYearly: '$99/yr', priceYearlyMonthly: '$8.25/mo', desc: '3 Identities · 10 Personas · 10K memories · 5 Agents · Browser extension · Priority support', descShort: '10K memories · 10 Personas · Full suite', cta: 'Start Trial', ctaYearly: '$99/yr · Save $45', badge: 'Most Popular' }, team: { name: 'Team', price: '$25/mo/seat', desc: '10 Identities · Unlimited Personas · 50K memories · Team memory · Admin panel', descShort: 'Team memory · Shared Personas', cta: 'Contact Us' }, viewAll: 'View full pricing →' },
    about: { title: 'About Moltable', mission: 'Own your AI identity, not just your chats.', architecture: { title: 'Three-Layer Architecture', layers: [{ name: 'Identity', desc: 'The real you · Unique · Owns all data' },{ name: 'Persona', desc: 'Personality mask · Behavioral rules · Shared memory' },{ name: 'Agent', desc: 'Executor · Tool-calling · No personality of its own' }] }, opensource: 'Open source under MIT — your data always belongs to you.' },
    privacy: { title: 'Privacy & Security', items: [{ title: 'Encrypted Storage', desc: 'All memories encrypted in transit and at rest. API Keys stored with SHA-256 hashing.' },{ title: 'Your Data, Your Control', desc: 'Export or delete all your data anytime. We never use your data to train models.' },{ title: 'Compliance', desc: 'GDPR and data protection compliant.' }] },
    footer: { product: 'Product', resources: 'Resources', legal: 'Legal', copyright: 'Moltable · AI Identity Protocol' },
    dashboard: { demoBanner: 'Demo Mode — Sign up to get started', stats: { memories: 'Memories', personas: 'Personas', projects: 'Projects', decisions: 'Decisions' }, quickStart: 'Quick Start', getKey: 'Get API Key', step1: 'Create API Key', step2: 'Load Skill', step3: 'Start Working' },
    common: { loading: 'Loading...', empty: 'No data', save: 'Save', cancel: 'Cancel', delete: 'Delete', edit: 'Edit', search: 'Search', add: 'Add', confirm: 'Confirm', openMenu: 'Open Menu', closeMenu: 'Close Menu' },
  }
} as const
