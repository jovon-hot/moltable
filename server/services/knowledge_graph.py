from __future__ import annotations

"""Knowledge graph service — zero-dependency entity & relationship extraction.

Extracts named entities (person / org / project / tool / language / concept /
location) from memory text using regex + keyword matching, then builds a
per-user graph where entities are connected by:

  * co-occurrence edges  — weight = number of memories mentioning both
  * pattern edges        — simple verb patterns (works at, founded, uses, ...)

The service is self-contained (stdlib only) and integrates with the existing
memory store by accepting memory dicts ``{id, content, category, tags,
created_at}`` and building the graph incrementally.
"""
import logging
import re
import threading
import uuid
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("moltable.knowledge_graph")

# ── Entity types ───────────────────────────────────────────
PERSON = "person"
ORG = "org"
PROJECT = "project"
TOOL = "tool"
LANGUAGE = "language"
CONCEPT = "concept"
LOCATION = "location"

# ── Keyword dictionaries (lowercase key → display name) ────
LANGUAGES: Dict[str, str] = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "rust": "Rust",
    "golang": "Go",
    "java": "Java",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "ruby": "Ruby",
    "php": "PHP",
    "scala": "Scala",
    "haskell": "Haskell",
    "elixir": "Elixir",
    "clojure": "Clojure",
    "dart": "Dart",
    "c++": "C++",
    "c#": "C#",
    "objective-c": "Objective-C",
    "perl": "Perl",
    "lua": "Lua",
    "matlab": "MATLAB",
    "julia": "Julia",
    "groovy": "Groovy",
    "solidity": "Solidity",
    "bash": "Bash",
    "zsh": "Zsh",
    "powershell": "PowerShell",
    "html": "HTML",
    "css": "CSS",
    "sass": "Sass",
    "less": "Less",
    "json": "JSON",
    "yaml": "YAML",
    "toml": "TOML",
    "markdown": "Markdown",
    "graphql": "GraphQL",
    "protobuf": "Protobuf",
    "assembly": "Assembly",
    "vb": "Visual Basic",
    "fortran": "Fortran",
    "cobol": "COBOL",
}

# Case-sensitive language names (would over-match if lowercased)
LANGUAGES_CASE_SENSITIVE: Dict[str, str] = {
    "Go": "Go",
    "C": "C",
    "R": "R",
    "SQL": "SQL",
}

TOOLS: Dict[str, str] = {
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "supabase": "Supabase",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "bitbucket": "Bitbucket",
    "redis": "Redis",
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "elasticsearch": "Elasticsearch",
    "kafka": "Kafka",
    "rabbitmq": "RabbitMQ",
    "celery": "Celery",
    "airflow": "Airflow",
    "nginx": "Nginx",
    "grafana": "Grafana",
    "prometheus": "Prometheus",
    "sentry": "Sentry",
    "vercel": "Vercel",
    "netlify": "Netlify",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "react": "React",
    "react native": "React Native",
    "vue": "Vue",
    "vue.js": "Vue",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "nuxt": "Nuxt",
    "svelte": "Svelte",
    "tailwind": "Tailwind",
    "tailwind css": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "vite": "Vite",
    "webpack": "Webpack",
    "rollup": "Rollup",
    "jest": "Jest",
    "pytest": "Pytest",
    "playwright": "Playwright",
    "cypress": "Cypress",
    "selenium": "Selenium",
    "postman": "Postman",
    "figma": "Figma",
    "slack": "Slack",
    "discord": "Discord",
    "notion": "Notion",
    "linear": "Linear",
    "jira": "Jira",
    "confluence": "Confluence",
    "zoom": "Zoom",
    "vscode": "VS Code",
    "visual studio code": "VS Code",
    "pycharm": "PyCharm",
    "intellij": "IntelliJ IDEA",
    "datagrip": "DataGrip",
    "dbeaver": "DBeaver",
    "pgadmin": "pgAdmin",
    "homebrew": "Homebrew",
    "npm": "npm",
    "pnpm": "pnpm",
    "yarn": "Yarn",
    "pip": "pip",
    "poetry": "Poetry",
    "uv": "uv",
    "conda": "Conda",
    "jupyter": "Jupyter",
    "colab": "Google Colab",
    "streamlit": "Streamlit",
    "gradio": "Gradio",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    "llamaindex": "LlamaIndex",
    "pgvector": "pgvector",
    "chroma": "Chroma",
    "pinecone": "Pinecone",
    "weaviate": "Weaviate",
    "qdrant": "Qdrant",
    "milvus": "Milvus",
    "faiss": "FAISS",
    "firebase": "Firebase",
    "appwrite": "Appwrite",
    "n8n": "n8n",
    "zapier": "Zapier",
    "airtable": "Airtable",
    "excel": "Excel",
    "google sheets": "Google Sheets",
    "google docs": "Google Docs",
    "obsidian": "Obsidian",
    "chrome": "Chrome",
    "safari": "Safari",
    "firefox": "Firefox",
    "telegram": "Telegram",
    "whatsapp": "WhatsApp",
    "wechat": "WeChat",
    "钉钉": "钉钉",
    "飞书": "飞书",
    "腾讯会议": "腾讯会议",
    "linux": "Linux",
    "ubuntu": "Ubuntu",
    "debian": "Debian",
    "centos": "CentOS",
    "alpine": "Alpine",
    "windows": "Windows",
    "macos": "macOS",
    "ios": "iOS",
    "android": "Android",
    "stripe": "Stripe",
    "twilio": "Twilio",
    "huggingface": "Hugging Face",
    "ray": "Ray",
    "spark": "Spark",
    "hadoop": "Hadoop",
    "datadog": "Datadog",
    "pagerduty": "PagerDuty",
}

PROJECTS: Dict[str, str] = {
    "moltable": "Moltable",
    "hermes": "Hermes",
    "chatgpt": "ChatGPT",
    "claude": "Claude",
    "cursor": "Cursor",
    "copilot": "GitHub Copilot",
    "midjourney": "Midjourney",
    "stable diffusion": "Stable Diffusion",
    "llama": "Llama",
    "gpt-4": "GPT-4",
    "gpt-4o": "GPT-4o",
    "gpt-5": "GPT-5",
    "deepseek-chat": "DeepSeek Chat",
    "deepseek-reasoner": "DeepSeek Reasoner",
    "airbnb": "Airbnb",
    "uber": "Uber",
    "doordash": "DoorDash",
    "notion": "Notion",
}

LOCATIONS: Dict[str, str] = {
    # Chinese cities / regions
    "北京": "北京",
    "上海": "上海",
    "深圳": "深圳",
    "杭州": "杭州",
    "广州": "广州",
    "成都": "成都",
    "重庆": "重庆",
    "武汉": "武汉",
    "南京": "南京",
    "西安": "西安",
    "苏州": "苏州",
    "天津": "天津",
    "长沙": "长沙",
    "郑州": "郑州",
    "青岛": "青岛",
    "大连": "大连",
    "厦门": "厦门",
    "福州": "福州",
    "合肥": "合肥",
    "昆明": "昆明",
    "香港": "香港",
    "澳门": "澳门",
    "台北": "台北",
    "中国": "中国",
    "美国": "美国",
    "日本": "日本",
    "德国": "德国",
    "英国": "英国",
    "法国": "法国",
    "加拿大": "加拿大",
    "澳大利亚": "澳大利亚",
    "韩国": "韩国",
    "新加坡": "新加坡",
    # English cities / countries
    "beijing": "Beijing",
    "shanghai": "Shanghai",
    "shenzhen": "Shenzhen",
    "hangzhou": "Hangzhou",
    "guangzhou": "Guangzhou",
    "chengdu": "Chengdu",
    "new york": "New York",
    "san francisco": "San Francisco",
    "seattle": "Seattle",
    "los angeles": "Los Angeles",
    "austin": "Austin",
    "london": "London",
    "berlin": "Berlin",
    "paris": "Paris",
    "tokyo": "Tokyo",
    "singapore": "Singapore",
    "hong kong": "Hong Kong",
    "taiwan": "Taiwan",
    "china": "China",
    "united states": "United States",
    "usa": "USA",
    "uk": "UK",
    "germany": "Germany",
    "japan": "Japan",
    "india": "India",
    "canada": "Canada",
    "australia": "Australia",
    "south korea": "South Korea",
    "france": "France",
    "netherlands": "Netherlands",
    "sweden": "Sweden",
    "switzerland": "Switzerland",
    "israel": "Israel",
    "dubai": "Dubai",
    "barcelona": "Barcelona",
    "amsterdam": "Amsterdam",
    "toronto": "Toronto",
    "sydney": "Sydney",
}

ORG_KEYWORDS: Dict[str, str] = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "google": "Google",
    "microsoft": "Microsoft",
    "apple": "Apple",
    "amazon": "Amazon",
    "meta": "Meta",
    "netflix": "Netflix",
    "stripe": "Stripe",
    "deepseek": "DeepSeek",
    "hugging face": "Hugging Face",
    "cohere": "Cohere",
    "mistral": "Mistral",
    "meta ai": "Meta AI",
    "xai": "xAI",
    "github": "GitHub",
    "gitlab": "GitLab",
    "vercel": "Vercel",
    "supabase": "Supabase",
    "mongodb": "MongoDB",
    "datadog": "Datadog",
    "salesforce": "Salesforce",
    "oracle": "Oracle",
    "ibm": "IBM",
    "intel": "Intel",
    "nvidia": "NVIDIA",
    "amd": "AMD",
    "tesla": "Tesla",
    "spacex": "SpaceX",
    "airbnb": "Airbnb",
    "uber": "Uber",
    "lyft": "Lyft",
    "stripe": "Stripe",
    "square": "Square",
    "shopify": "Shopify",
    "figma": "Figma",
    "notion": "Notion",
    "slack": "Slack",
    "zoom": "Zoom",
    "字节跳动": "字节跳动",
    "阿里巴巴": "阿里巴巴",
    "腾讯": "腾讯",
    "百度": "百度",
    "华为": "华为",
    "小米": "小米",
    "美团": "美团",
    "京东": "京东",
    "拼多多": "拼多多",
    "网易": "网易",
    "滴滴": "滴滴",
    "蚂蚁集团": "蚂蚁集团",
    "科大讯飞": "科大讯飞",
    "商汤科技": "商汤科技",
    "旷视科技": "旷视科技",
}

CONCEPTS: Dict[str, str] = {
    "architecture": "Architecture",
    "scalability": "Scalability",
    "performance": "Performance",
    "security": "Security",
    "privacy": "Privacy",
    "design": "Design",
    "onboarding": "Onboarding",
    "migration": "Migration",
    "refactoring": "Refactoring",
    "refactor": "Refactoring",
    "debugging": "Debugging",
    "deployment": "Deployment",
    "infrastructure": "Infrastructure",
    "identity": "Identity",
    "authentication": "Authentication",
    "authorization": "Authorization",
    "database": "Database",
    "cache": "Cache",
    "caching": "Caching",
    "indexing": "Indexing",
    "search": "Search",
    "ranking": "Ranking",
    "recommendation": "Recommendation",
    "personalization": "Personalization",
    "knowledge": "Knowledge",
    "knowledge graph": "Knowledge Graph",
    "vector search": "Vector Search",
    "semantic search": "Semantic Search",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "natural language processing": "Natural Language Processing",
    "large language model": "Large Language Model",
    "data pipeline": "Data Pipeline",
    "data warehouse": "Data Warehouse",
    "data lake": "Data Lake",
    "etl": "ETL",
    "analytics": "Analytics",
    "observability": "Observability",
    "monitoring": "Monitoring",
    "alerting": "Alerting",
    "rate limiting": "Rate Limiting",
    "quota": "Quota",
    "billing": "Billing",
    "subscription": "Subscription",
    "login": "Login",
    "session": "Session",
    "token": "Token",
    "jwt": "JWT",
    "encryption": "Encryption",
    "hashing": "Hashing",
    "concurrency": "Concurrency",
    "latency": "Latency",
    "throughput": "Throughput",
    "reliability": "Reliability",
    "availability": "Availability",
    "consistency": "Consistency",
    "replication": "Replication",
    "sharding": "Sharding",
    "backup": "Backup",
    "recovery": "Recovery",
    "testing": "Testing",
    "unit testing": "Unit Testing",
    "integration testing": "Integration Testing",
    "ci/cd": "CI/CD",
    "code review": "Code Review",
    "documentation": "Documentation",
    "roadmap": "Roadmap",
    "milestone": "Milestone",
    "sprint": "Sprint",
    "agile": "Agile",
    "scrum": "Scrum",
    "demo": "Demo",
    "prototype": "Prototype",
    "mvp": "MVP",
    "poc": "PoC",
    "production": "Production",
    "staging": "Staging",
    "development": "Development",
    "tech debt": "Tech Debt",
    "technical debt": "Tech Debt",
    "hiring": "Hiring",
    "recruitment": "Recruitment",
    "interview": "Interview",
    "team": "Team",
    "culture": "Culture",
    "growth": "Growth",
    "retention": "Retention",
    "churn": "Churn",
    "conversion": "Conversion",
    "engagement": "Engagement",
    "revenue": "Revenue",
    "pricing": "Pricing",
    "startup": "Startup",
    "enterprise": "Enterprise",
    "saas": "SaaS",
    "digital identity": "Digital Identity",
    "identity sync": "Identity Sync",
    "identity layer": "Identity Layer",
    "knowledge management": "Knowledge Management",
    "memory system": "Memory System",
    "memory": "Memory",
    "reasoning": "Reasoning",
    "agent": "Agent",
    "workflow": "Workflow",
    "automation": "Automation",
    "integration": "Integration",
    "plugin": "Plugin",
    "extension": "Extension",
    "open source": "Open Source",
    "open-source": "Open Source",
    "protocol": "Protocol",
    "framework": "Framework",
    "sdk": "SDK",
    "frontend": "Frontend",
    "backend": "Backend",
    "full-stack": "Full-Stack",
    "full stack": "Full-Stack",
    "mobile": "Mobile",
    "cloud": "Cloud",
    "serverless": "Serverless",
    "microservices": "Microservices",
    "monolith": "Monolith",
    "event-driven": "Event-Driven",
    "event driven": "Event-Driven",
    "real-time": "Real-Time",
    "realtime": "Real-Time",
    "recommender system": "Recommender System",
    "chatbot": "Chatbot",
    "rag": "RAG",
    "fine-tuning": "Fine-Tuning",
    "fine tuning": "Fine-Tuning",
    "embeddings": "Embeddings",
    "embedding": "Embedding",
    "semantic": "Semantic",
    "sustainability": "Sustainability",
    "strategy": "Strategy",
    "vision": "Vision",
    "mission": "Mission",
    "goal": "Goal",
}

# Case-sensitive concepts (uppercase acronyms)
CONCEPTS_CASE_SENSITIVE: Dict[str, str] = {
    "AI": "AI",
    "ML": "ML",
    "LLM": "LLM",
    "API": "API",
    "SDK": "SDK",
    "CLI": "CLI",
    "UI": "UI",
    "UX": "UX",
    "JWT": "JWT",
    "RAG": "RAG",
    "SaaS": "SaaS",
    "CRM": "CRM",
    "ERP": "ERP",
    "CMS": "CMS",
    "GPU": "GPU",
    "CPU": "CPU",
    "DB": "DB",
}

# Role words — promoted to concept nodes when matched by is_a / role_of patterns
ROLE_WORDS: Dict[str, str] = {
    "engineer": "Engineer",
    "developer": "Developer",
    "designer": "Designer",
    "founder": "Founder",
    "co-founder": "Co-Founder",
    "ceo": "CEO",
    "cto": "CTO",
    "coo": "COO",
    "researcher": "Researcher",
    "scientist": "Scientist",
    "manager": "Manager",
    "product manager": "Product Manager",
    "writer": "Writer",
    "analyst": "Analyst",
    "consultant": "Consultant",
    "architect": "Architect",
    "operator": "Operator",
    "student": "Student",
    "teacher": "Teacher",
    "professor": "Professor",
    "freelancer": "Freelancer",
}

# ── Stopwords ──────────────────────────────────────────────
_EN_NAME_STOPWORDS = {
    "the", "a", "an", "this", "that", "these", "those", "i", "we", "you",
    "he", "she", "it", "they", "my", "your", "his", "her", "our", "their",
    "when", "where", "what", "how", "why", "if", "but", "and", "or", "so",
    "for", "with", "from", "into", "after", "before", "during", "since",
    "until", "then", "now", "today", "tomorrow", "yesterday", "monday",
    "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december", "please",
    "thanks", "thank", "hello", "hi", "yes", "no", "ok", "okay", "also",
    "however", "therefore", "meanwhile", "moreover", "furthermore", "well",
    "actually", "basically", "definitely", "really", "probably", "maybe",
    "someone", "something", "everyone", "everything", "anyone", "anything",
    "nothing", "nobody", "any", "every", "each", "some", "many", "much",
    "more", "most", "few", "several", "both", "all", "one", "two", "three",
    "first", "second", "next", "last", "new", "old", "good", "great", "best",
}

_ZH_NAME_STOPWORDS = {
    "王子", "王国", "国王", "王后", "皇后", "太后", "孙子", "老子", "孔子",
    "孟子", "庄子", "时候", "时间", "时代", "小时", "先生", "小姐", "老师",
    "学生", "同学", "医生", "律师", "经理", "老板", "孩子", "女儿", "儿子",
    "妈妈", "爸爸", "姐姐", "妹妹", "哥哥", "弟弟", "朋友", "同事", "客户",
    "用户", "问题", "项目", "公司", "团队", "产品", "市场", "商业", "金融",
    "基金", "银行", "保险", "股票", "期货", "编程", "代码", "算法", "数据",
    "信息", "内容", "平台", "系统", "服务", "技术", "科技", "研究", "发展",
    "设计", "开发", "测试", "部署", "上线", "发布", "更新", "版本", "功能",
    "需求", "方案", "计划", "目标", "结果", "过程", "方法", "方式", "方向",
    "领域", "行业", "趋势", "机会", "挑战", "风险", "成本", "收入", "利润",
    "用户", "客户", "流量", "转化", "增长", "运营", "管理", "支持", "帮助",
    "关于", "对于", "根据", "通过", "进行", "需要", "可以", "应该", "必须",
    "可能", "能够", "希望", "觉得", "认为", "知道", "了解", "发现", "决定",
    "选择", "使用", "利用", "采用", "提供", "实现", "完成", "开始", "结束",
    "继续", "保持", "改变", "提高", "降低", "增加", "减少", "扩大", "缩小",
    "建立", "创建", "组织", "参加", "参与", "合作", "交流", "沟通", "讨论",
    "分享", "学习", "工作", "生活", "吃饭", "睡觉", "今天", "明天", "昨天",
    "现在", "目前", "未来", "过去", "以前", "以后", "最近", "之前", "之后",
    "每天", "每周", "每月", "每年", "第一", "第二", "第三", "最后", "首先",
}

# Trailing chars never part of a Chinese name (trimmed off candidates)
_ZH_NON_NAME_CHARS = set(
    "是在和与及或的得了着过会能不能要不要想说说做去来到从对给让把被向为于之以而所其该这那每某个"
    "今昨前后上下中里外内间时候个种些样般场次遍回趟点之也都很太不没又再更最还就但且"
    "师生们啊吧吗呢哦唉呀哈哇嗯嘛"
)

# Leading chars that cannot start a Chinese organization name (stripped off)
_ZH_ORG_PREFIX_CHARS = set(
    "我在去来从把被让给对向为于以之其这那每某个谁他她它你我我们你们他们正在是也都又再更最还就但"
    "且及与或和叫喊找看看见过问想爱喜欢讨厌"
)

# ── Regexes ────────────────────────────────────────────────
# Common Chinese surnames (百家姓 subset) + compound surnames
_ZH_SURNAMES = (
    "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏窦章苏潘葛奚范彭"
    "郎鲁韦昌马苗凤花方俞任袁柳鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟"
    "平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危"
    "江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸"
    "左石崔吉钮龚程嵇邢滑裴陆荣翁荀羊惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全"
    "郗班仰秋仲伊宫宁仇栾暴甘厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙"
    "池乔阴郁胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍郤璩桑桂濮牛寿通边扈燕冀浦尚农温别庄晏柴瞿阎"
    "充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁"
    "勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰巢关蒯相查后荆红游竺权逯盖益桓公"
)
_ZH_COMPOUND_SURNAMES = (
    "欧阳|上官|司马|诸葛|东方|皇甫|尉迟|公孙|慕容|长孙|宇文|司徒|令狐|独孤|夏侯|南宫|西门|呼延|端木|轩辕|百里"
)

_ZH_PERSON_RE = re.compile(
    rf"(?<![\u4e00-\u9fff])((?:{_ZH_COMPOUND_SURNAMES})|[{_ZH_SURNAMES}])[\u4e00-\u9fff]{{1,2}}"
)

_EN_PERSON_PAIR_RE = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+))\b", re.ASCII)
_EN_PERSON_TITLE_RE = re.compile(r"\b(?:Mr|Mrs|Ms|Dr|Prof)\.? ([A-Z][a-z]+)\b", re.ASCII)
_EN_PERSON_VERB_RE = re.compile(
    r"\b([A-Z][a-z]+)\s+(?:works|likes|uses|leads|founded|co-founded|built|"
    r"created|said|prefers|wants|joined|left|is|was|has)\b",
    re.ASCII,
)

_ORG_SUFFIX_RE = re.compile(
    r"\b([A-Z][A-Za-z0-9&.]*(?: [A-Z][A-Za-z0-9&.]+)*)\s+"
    r"(?:Inc\.?|Corp\.?|Corporation|Ltd\.?|Limited|LLC|LLP|GmbH|Labs?|"
    r"Laboratories|Technologies?|Systems?|Group|Company|University|"
    r"Institute|AI|Software|Holdings|Co\.?)\b",
    re.ASCII,
)

_ZH_ORG_RE = re.compile(
    r"([\u4e00-\u9fff]{2,10}(?:公司|集团|科技|研究院|实验室|大学|银行|证券|基金|工作室|协会))"
)


def _clean_zh_org(name: str) -> str:
    """Strip leading function-word chars from a Chinese org candidate,
    then strip any leading person-name prefix (surname + 1-2 chars)
    that the greedy regex may have swallowed.
    """
    import re as _re_local
    # Strip function-word prefixes
    while name and name[0] in _ZH_ORG_PREFIX_CHARS:
        name = name[1:]
    # Strip leading person name if regex swallowed it
    # e.g. "王小明在腾讯科技" → strip "王小明在" → "腾讯科技"
    person_stripped = _re_local.sub(
        rf"^(?:{_ZH_COMPOUND_SURNAMES}|[{_ZH_SURNAMES}])[\u4e00-\u9fff]{{1,2}}",
        "", name
    )
    if person_stripped and len(person_stripped) >= 2:
        name = person_stripped
    # Re-strip any newly-exposed prefix chars
    while name and name[0] in _ZH_ORG_PREFIX_CHARS:
        name = name[1:]
    return name

_CONCEPT_CAMEL_RE = re.compile(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b", re.ASCII)
_CONCEPT_UPPER_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9]*[A-Z]{2,}\b", re.ASCII)

# ── Relation patterns (subj/obj captured; resolved against extracted entities) ──
_RELATION_PATTERNS: List[Tuple[re.Pattern, str]] = [
    # X works at/for Y
    (re.compile(
        r"(?P<subj>[A-Z][a-z]+(?: [A-Z][a-z]+)?|[\u4e00-\u9fff]{2,4})"
        r"\s+(?:works|is working|is currently working|has been working|"
        r"is now working)\s+(?:at|for)\s+"
        r"(?P<obj>[A-Z][\w&.]*(?: [A-Z][\w&.]*){0,2}(?: (?:Inc|Corp|Ltd|LLC|"
        r"Labs|Technologies|Systems|Group|Company|University|AI))?)",
        re.ASCII,
    ), "works_at"),
    # X founded/created/built/launched Y
    (re.compile(
        r"(?P<subj>[A-Z][a-z]+(?: [A-Z][a-z]+)?|[\u4e00-\u9fff]{2,4})"
        r"\s+(?:founded|co-founded|created|built|launched|started)\s+"
        r"(?P<obj>[A-Z][\w&.]*(?: [A-Z][\w&.]*){0,2}(?: (?:Inc|Corp|Ltd|LLC|"
        r"Labs|Technologies|Systems|Group|Company|University|AI))?)",
        re.ASCII,
    ), "founded"),
    # X uses Y
    (re.compile(
        r"(?P<subj>[A-Z][a-z]+(?: [A-Z][a-z]+)?|[\u4e00-\u9fff]{2,4})"
        r"\s+(?:uses|used|is using|has been using)\s+"
        r"(?P<obj>[\w .-]{2,40}?)\b",
        re.ASCII,
    ), "uses"),
    # X likes/prefers/enjoys Y
    (re.compile(
        r"(?P<subj>[A-Z][a-z]+(?: [A-Z][a-z]+)?|[\u4e00-\u9fff]{2,4})"
        r"\s+(?:likes|prefers|enjoys|is interested in)\s+"
        r"(?P<obj>[\w .-]{2,40}?)\b",
        re.ASCII,
    ), "likes"),
    # X leads/manages Y
    (re.compile(
        r"(?P<subj>[A-Z][a-z]+(?: [A-Z][a-z]+)?|[\u4e00-\u9fff]{2,4})"
        r"\s+(?:leads|manages|is leading|is managing|runs)\s+"
        r"(?P<obj>[A-Z][\w&.]*(?: [A-Z][\w&.]*){0,2}|[\u4e00-\u9fff]{2,10})",
        re.ASCII,
    ), "manages"),
    # X collaborates with Y
    (re.compile(
        r"(?P<subj>[A-Z][a-z]+(?: [A-Z][a-z]+)?|[\u4e00-\u9fff]{2,4})"
        r"\s+(?:collaborates|collaborated|works|worked)\s+(?:with|alongside)\s+"
        r"(?P<obj>[A-Z][a-z]+(?: [A-Z][a-z]+)?|[\u4e00-\u9fff]{2,4})",
        re.ASCII,
    ), "collaborates_with"),
    # X is a/an Y
    (re.compile(
        r"(?P<subj>[A-Z][a-z]+(?: [A-Z][a-z]+)?|[\u4e00-\u9fff]{2,4})"
        r"\s+is\s+(?:a|an)\s+(?P<obj>[a-z][\w-]+)",
        re.ASCII,
    ), "is_a"),
    # X is the CEO/CTO/founder of Y
    (re.compile(
        r"(?P<subj>[A-Z][a-z]+(?: [A-Z][a-z]+)?|[\u4e00-\u9fff]{2,4})"
        r"\s+is\s+(?:the\s+)?(?:CEO|CTO|COO|founder|co-founder|engineer|"
        r"developer|designer)\s+of\s+"
        r"(?P<obj>[A-Z][\w&.]*(?: [A-Z][\w&.]*){0,2}(?: (?:Inc|Corp|Ltd|LLC|"
        r"Labs|Technologies|Systems|Group|Company|University|AI))?)",
        re.ASCII,
    ), "role_at"),
    # Chinese: X 在 Y 工作
    (re.compile(
        r"(?P<subj>[\u4e00-\u9fff]{2,4})在(?P<obj>[A-Za-z][\w.]*|[\u4e00-\u9fff]{2,10}"
        r"(?:公司|集团|科技|大学|研究院))工作"
    ), "works_at"),
    # Chinese: X 喜欢/使用/创建 Y
    (re.compile(
        r"(?P<subj>[\u4e00-\u9fff]{2,4}|[A-Z][a-z]+)(?:喜欢|使用|创建|创办|领导)"
        r"(?P<obj>[\u4e00-\u9fff]{2,4}|[A-Za-z][\w.-]+)"
    ), "likes"),
]


# ASCII-only word boundary (Python 3 \w matches CJK chars)
_ASCII_B = r"(?<![a-zA-Z0-9_])"
_ASCII_E = r"(?![a-zA-Z0-9_])"

# ── Entity extraction ──────────────────────────────────────
def _keyword_matches(text: str, keywords: Dict[str, str], case_sensitive: bool = False):
    """Yield (name, start, end) for keyword matches in text.

    Keys are processed longest-first so multiword phrases (e.g. "identity
    sync") claim their span before overlapping single words ("identity").
    Uses ASCII-only word boundaries to work correctly when adjacent
    to CJK characters (Python 3 regex \\w includes Unicode letters).
    """
    items = sorted(keywords.items(), key=lambda kv: len(kv[0]), reverse=True)
    if case_sensitive:
        for key, display in items:
            for m in re.finditer(rf"{_ASCII_B}{re.escape(key)}{_ASCII_E}", text):
                yield display, m.start(), m.end()
    else:
        low = text.lower()
        for key, display in items:
            for m in re.finditer(rf"{_ASCII_B}{re.escape(key)}{_ASCII_E}", low):
                yield display, m.start(), m.end()


def _trim_zh_name(name: str) -> str:
    """Strip trailing chars that cannot be part of a Chinese name."""
    while name and name[-1] in _ZH_NON_NAME_CHARS:
        name = name[:-1]
    return name


def extract_entities(text: str) -> List[Tuple[str, str, int, int]]:
    """Extract (name, type, start, end) entities from memory text.

    Precedence: language > tool > project > location > org > concept > person.
    Earlier categories claim spans; later matches overlapping a claimed span
    are skipped.
    """
    if not text:
        return []

    claimed: List[Tuple[int, int]] = []
    entities: List[Tuple[str, str, int, int]] = []

    def _add(name: str, etype: str, start: int, end: int):
        for s, e in claimed:
            if start < e and s < end:
                return
        claimed.append((start, end))
        entities.append((name, etype, start, end))

    # 1. Languages
    for name, s, e in _keyword_matches(text, LANGUAGES_CASE_SENSITIVE, case_sensitive=True):
        _add(name, LANGUAGE, s, e)
    for name, s, e in _keyword_matches(text, LANGUAGES):
        _add(name, LANGUAGE, s, e)

    # 2. Tools
    for name, s, e in _keyword_matches(text, TOOLS):
        _add(name, TOOL, s, e)

    # 3. Projects
    for name, s, e in _keyword_matches(text, PROJECTS):
        _add(name, PROJECT, s, e)

    # 4. Locations
    for name, s, e in _keyword_matches(text, LOCATIONS):
        _add(name, LOCATION, s, e)

    # 5. Organizations (regexes first — more specific — then keywords as fallback)
    for m in _ORG_SUFFIX_RE.finditer(text):
        _add(m.group(1).strip().rstrip("."), ORG, *m.span())
    for m in _ZH_ORG_RE.finditer(text):
        name = _clean_zh_org(m.group(1))
        if len(name) >= 2:
            start, end = m.span()
            _add(name, ORG, start + (len(m.group(1)) - len(name)), end)
    for name, s, e in _keyword_matches(text, ORG_KEYWORDS):
        _add(name, ORG, s, e)

    # 6. Concepts (keywords, camel-case terms, uppercase acronym terms)
    for name, s, e in _keyword_matches(text, CONCEPTS_CASE_SENSITIVE, case_sensitive=True):
        _add(name, CONCEPT, s, e)
    for name, s, e in _keyword_matches(text, CONCEPTS):
        _add(name, CONCEPT, s, e)
    for m in _CONCEPT_CAMEL_RE.finditer(text):
        _add(m.group(0), CONCEPT, *m.span())
    for m in _CONCEPT_UPPER_RE.finditer(text):
        _add(m.group(0), CONCEPT, *m.span())

    # 7. Persons (English pairs/titles/verb-adjacent, then Chinese names)
    for m in _EN_PERSON_PAIR_RE.finditer(text):
        name = m.group(1)
        if name.lower() not in _EN_NAME_STOPWORDS:
            _add(name, PERSON, *m.span())
    for m in _EN_PERSON_TITLE_RE.finditer(text):
        _add(m.group(1), PERSON, *m.span())
    for m in _EN_PERSON_VERB_RE.finditer(text):
        name = m.group(1)
        if name.lower() not in _EN_NAME_STOPWORDS:
            _add(name, PERSON, *m.span())
    for m in _ZH_PERSON_RE.finditer(text):
        raw = m.group(0)
        start, end = m.span()
        name = _trim_zh_name(raw)
        if name != raw:
            end = start + len(name)
        if len(name) >= 2 and name not in _ZH_NAME_STOPWORDS:
            _add(name, PERSON, start, end)

    entities.sort(key=lambda e: e[2])
    return entities


def _resolve_entity(group_text: str, names: "set[str]") -> Optional[Tuple[str, Optional[str]]]:
    """Resolve a pattern capture group to an extracted entity name (+ type).

    Returns (canonical_name, type) for an existing entity whose name appears
    in the group text, or a role/concept word promoted to a concept node.
    """
    low = group_text.strip().strip(".,;:!?()\"'").lower()
    if not low:
        return None
    candidates = [n for n in names if n.lower() in low]
    if candidates:
        name = max(candidates, key=len)
        return (name, None)  # type resolved by caller from node
    if low in ROLE_WORDS:
        return (ROLE_WORDS[low], CONCEPT)
    if low in CONCEPTS:
        return (CONCEPTS[low], CONCEPT)
    return None


def extract_relations(text: str, entities: List[Tuple[str, str, int, int]]
                      ) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str]]]:
    """Extract (subject, object, relation) triples from text via verb patterns.

    Returns (relations, extra_entities) where extra_entities are role/concept
    nodes promoted from pattern objects that were not extracted as entities.
    """
    names = {e[0] for e in entities}
    relations: List[Tuple[str, str, str]] = []
    extras: List[Tuple[str, str]] = []

    for pattern, relation in _RELATION_PATTERNS:
        for m in pattern.finditer(text):
            try:
                subj = _resolve_entity(m.group("subj"), names)
                obj = _resolve_entity(m.group("obj"), names)
            except IndexError:
                continue
            if not subj or not obj:
                continue
            subj_name, subj_type = subj
            obj_name, obj_type = obj
            if subj_name == obj_name:
                continue
            relations.append((subj_name, obj_name, relation))
            if subj_type:
                extras.append((subj_name, subj_type))
            if obj_type:
                extras.append((obj_name, obj_type))

    # Dedupe
    seen = set()
    unique: List[Tuple[str, str, str]] = []
    for r in relations:
        if r not in seen:
            seen.add(r)
            unique.append(r)
    return unique, list(dict.fromkeys(extras))


# ── Graph storage ──────────────────────────────────────────
class _UserGraph:
    """Per-user knowledge graph: nodes + weighted undirected edges."""

    def __init__(self):
        self.nodes: Dict[str, dict] = {}            # name → {name, type, count, memories}
        self.edges: Dict[Tuple[str, str], dict] = {}  # (a, b) sorted → {source, target, weight, memories, relation}
        self.memory_entities: Dict[str, set] = {}   # memory_id → set of entity names


class KnowledgeGraphService:
    """In-memory per-user knowledge graph, built incrementally from memories."""

    def __init__(self):
        self._graphs: Dict[str, _UserGraph] = {}
        self._lock = threading.Lock()

    # ── Graph lifecycle ──────────────────────────────────
    def _get_graph(self, user_id: str) -> _UserGraph:
        graph = self._graphs.get(user_id)
        if graph is None:
            graph = _UserGraph()
            self._graphs[user_id] = graph
        return graph

    def add_memory(self, user_id: str, memory: dict) -> bool:
        """Incrementally add one memory dict to the user's graph.

        Idempotent: re-adding the same memory_id is a no-op.
        Returns True if the memory was newly added.
        """
        content = (memory.get("content") or "").strip()
        if not content:
            return False
        mid = str(memory.get("id") or "")
        if not mid:
            mid = "mem-" + uuid.uuid5(uuid.NAMESPACE_URL, content).hex[:12]

        entities = extract_entities(content)
        names = list(dict.fromkeys(e[0] for e in entities))
        relations, extras = extract_relations(content, entities)
        for name, etype in extras:
            if name not in names:
                names.append(name)

        with self._lock:
            graph = self._get_graph(user_id)
            if mid in graph.memory_entities:
                return False  # already processed

            graph.memory_entities[mid] = set(names)

            # Nodes
            for name in names:
                node = graph.nodes.get(name)
                if node is None:
                    etype = next((t for n, t, _, _ in entities if n == name), CONCEPT)
                    # extras carry their own type; look it up from extras too
                    for en, et in extras:
                        if en == name:
                            etype = et
                            break
                    node = {"name": name, "type": etype, "count": 0, "memories": []}
                    graph.nodes[name] = node
                node["count"] += 1
                node["memories"].append(mid)

            # Co-occurrence edges
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a, b = names[i], names[j]
                    key = tuple(sorted((a, b)))
                    edge = graph.edges.get(key)
                    if edge is None:
                        edge = {"source": key[0], "target": key[1],
                                "weight": 0, "memories": [], "relation": None}
                        graph.edges[key] = edge
                    edge["weight"] += 1
                    edge["memories"].append(mid)

            # Pattern (typed) relations
            for subj, obj, relation in relations:
                key = tuple(sorted((subj, obj)))
                edge = graph.edges.get(key)
                if edge is None:
                    edge = {"source": key[0], "target": key[1],
                            "weight": 0, "memories": [], "relation": None}
                    graph.edges[key] = edge
                edge["relation"] = relation

            logger.debug("KG add_memory user=%s memory=%s entities=%d", user_id, mid, len(names))
            return True

    def add_memories(self, user_id: str, memories: List[dict]) -> dict:
        """Add many memories; returns stats."""
        added = 0
        for memory in memories:
            if self.add_memory(user_id, memory):
                added += 1
        graph = self._get_graph(user_id)
        return {"added": added, "nodes": len(graph.nodes), "edges": len(graph.edges)}

    def rebuild(self, user_id: str, memories: List[dict]) -> dict:
        """Clear the user's graph and rebuild from a full memory list."""
        with self._lock:
            self._graphs[user_id] = _UserGraph()
        return self.add_memories(user_id, memories)

    def remove_memory(self, user_id: str, memory_id: str) -> bool:
        """Remove a memory from the graph (decrements counts/weights)."""
        with self._lock:
            graph = self._graphs.get(user_id)
            if graph is None or memory_id not in graph.memory_entities:
                return False
            names = graph.memory_entities.pop(memory_id)

            for name in names:
                node = graph.nodes.get(name)
                if node:
                    node["count"] = max(0, node["count"] - 1)
                    if memory_id in node["memories"]:
                        node["memories"].remove(memory_id)
                    if node["count"] == 0:
                        del graph.nodes[name]

            for key in list(graph.edges.keys()):
                edge = graph.edges[key]
                if memory_id in edge["memories"]:
                    edge["memories"].remove(memory_id)
                    edge["weight"] = max(0, edge["weight"] - 1)
                if edge["weight"] == 0 and not edge["memories"]:
                    del graph.edges[key]
            return True

    def clear(self, user_id: Optional[str] = None):
        """Clear one user's graph (or all graphs)."""
        with self._lock:
            if user_id is None:
                self._graphs.clear()
            else:
                self._graphs.pop(user_id, None)

    # ── Queries ──────────────────────────────────────────
    def get_graph(self, user_id: str, min_weight: int = 1,
                  limit: int = 200) -> dict:
        """Full graph in API format: {nodes, edges, stats}."""
        graph = self._get_graph(user_id)
        nodes = sorted(graph.nodes.values(), key=lambda n: n["count"], reverse=True)
        nodes = nodes[:limit]
        node_names = {n["name"] for n in nodes}

        edges = []
        for edge in graph.edges.values():
            if edge["weight"] < min_weight:
                continue
            if edge["source"] not in node_names or edge["target"] not in node_names:
                continue
            edges.append({
                "source": edge["source"],
                "target": edge["target"],
                "weight": edge["weight"],
                "relation": edge.get("relation"),
                "memories": edge["memories"],
            })

        return {
            "user_id": user_id,
            "nodes": [{"id": n["name"], "name": n["name"],
                       "type": n["type"], "count": n["count"]} for n in nodes],
            "edges": edges,
            "stats": {"nodes": len(nodes), "edges": len(edges)},
        }

    def _resolve_node(self, graph: _UserGraph, name: str) -> Optional[str]:
        if name in graph.nodes:
            return name
        low = name.lower()
        for n in graph.nodes:
            if n.lower() == low:
                return n
        return None

    def find_entity_connections(self, user_id: str, name: str) -> Optional[dict]:
        """Entity details + all its edges (connections)."""
        graph = self._get_graph(user_id)
        resolved = self._resolve_node(graph, name)
        if resolved is None:
            return None
        node = graph.nodes[resolved]

        connections = []
        for key, edge in graph.edges.items():
            if resolved not in key:
                continue
            other = key[1] if key[0] == resolved else key[0]
            other_node = graph.nodes.get(other)
            connections.append({
                "entity": other,
                "entity_type": other_node["type"] if other_node else None,
                "weight": edge["weight"],
                "relation": edge.get("relation"),
                "memories": edge["memories"],
            })
        connections.sort(key=lambda c: c["weight"], reverse=True)

        return {
            "entity": {"id": resolved, "name": resolved,
                       "type": node["type"], "count": node["count"]},
            "connections": connections,
            "total_connections": len(connections),
        }

    def find_related_entities(self, user_id: str, name: str,
                              limit: int = 10) -> List[dict]:
        """Entities connected to `name`, ranked by edge weight."""
        result = self.find_entity_connections(user_id, name)
        if result is None:
            return []
        related = [{"entity": c["entity"], "type": c["entity_type"],
                    "weight": c["weight"], "relation": c["relation"]}
                   for c in result["connections"]]
        return related[:limit]

    def find_path(self, user_id: str, source: str, target: str,
                  max_depth: int = 6) -> Optional[dict]:
        """Shortest path (BFS) between two entities; None if unreachable."""
        graph = self._get_graph(user_id)
        src = self._resolve_node(graph, source)
        tgt = self._resolve_node(graph, target)
        if src is None or tgt is None:
            return None
        if src == tgt:
            return {"path": [src], "edges": [], "length": 0}

        visited = {src: None}
        queue = [src]
        while queue and len(visited) <= max_depth + 1:
            cur = queue.pop(0)
            if cur == tgt:
                break
            for a, b in graph.edges:
                if a == cur and b not in visited:
                    visited[b] = cur
                    queue.append(b)
                elif b == cur and a not in visited:
                    visited[a] = cur
                    queue.append(a)

        if tgt not in visited:
            return None

        path = [tgt]
        cur = tgt
        while visited[cur] is not None:
            cur = visited[cur]
            path.append(cur)
        path.reverse()

        edges = []
        for i in range(len(path) - 1):
            key = tuple(sorted((path[i], path[i + 1])))
            edge = graph.edges.get(key)
            if edge:
                edges.append({
                    "source": edge["source"], "target": edge["target"],
                    "weight": edge["weight"], "relation": edge.get("relation"),
                })
        return {"path": path, "edges": edges, "length": len(path) - 1}


# ── Module-level singleton (shared by routes) ─────────────
knowledge_graph_service = KnowledgeGraphService()
