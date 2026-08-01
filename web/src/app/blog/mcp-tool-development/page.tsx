'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function ArticlePage() {
  return (
    <ArticleLayout title="MCP 工具开发实战：从零构建一个 AI Agent 记忆缓存层" date="2026-07-15">
      <p>MCP（Model Context Protocol）已经成为 AI Agent 连接外部世界的标准协议——25K+ GitHub Stars，已被 Linux 基金会接纳。但大多数开发者只是<strong>使用</strong>现有的 MCP Server，很少有人自己写一个。</p>
      <p>这篇文章手把手教你用 Python 构建一个 MCP Server，为给 AI Agent 添加持久记忆能力。从协议理解到生产部署，全程可运行。</p>

      <h2>MCP 协议基础</h2>
      <p>MCP 基于 JSON-RPC 2.0，核心是三个方法：</p>
      <ul>
        <li><code>tools/list</code>：告诉 Agent 有哪些工具可用</li>
        <li><code>tools/call</code>：Agent 调用具体工具</li>
        <li><code>initialize</code>：建立连接、协商能力</li>
      </ul>
      <p>传输层支持两种模式：<strong>stdio</strong>（标准输入输出，适合本地）和 <strong>SSE</strong>（Server-Sent Events，适合远程）。生产环境推荐 SSE，因为可以部署到云端，多个 Agent 共享同一个 Server。</p>

      <h2>实战：构建记忆缓存 MCP Server</h2>
      <p>我们的目标是构建一个轻量级的记忆层，Agent 可以通过它：</p>
      <ul>
        <li><code>search_memory</code>：语义搜索用户记忆</li>
        <li><code>save_memory</code>：保存新记忆（带冲突检测）</li>
        <li><code>auto_provision</code>：一键加载用户完整上下文</li>
      </ul>

      <h3>项目搭建</h3>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`mkdir memory-mcp && cd memory-mcp
python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn mcp chromadb openai`}
      </pre>

      <h3>核心代码</h3>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`# server.py
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationCapabilities
from mcp.server.sse import SseServerTransport
from fastapi import FastAPI
import chromadb, json

app = FastAPI()
server = Server("memory-mcp")

# 内存中的记忆存储（生产环境换 PostgreSQL + pgvector）
db = chromadb.Client()
collection = db.create_collection("memories")

@server.list_tools()
async def list_tools():
    return [
        {
            "name": "search_memory",
            "description": "语义搜索用户记忆",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询"},
                    "top_k": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        },
        {
            "name": "save_memory",
            "description": "保存新记忆，自动检测冲突",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": ["preference","decision","fact",
                                 "project","insight","task","relationship"]
                    }
                },
                "required": ["content"]
            }
        },
        {
            "name": "auto_provision",
            "description": "一键获取用户完整上下文",
            "inputSchema": {"type": "object", "properties": {}}
        }
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_memory":
        # 向量搜索
        results = collection.query(
            query_texts=[arguments["query"]],
            n_results=arguments.get("top_k", 5)
        )
        return [{"type": "text", "text": json.dumps(results, ensure_ascii=False)}]
    
    elif name == "save_memory":
        # 先检查冲突（相似度 > 0.9）
        existing = collection.query(
            query_texts=[arguments["content"]],
            n_results=1
        )
        if existing["distances"][0] and existing["distances"][0][0] < 0.1:
            return [{"type": "text", 
                     "text": "⚠️ 检测到相似记忆，已存在的条目：" + 
                             existing["documents"][0][0]}]
        # 保存
        collection.add(
            documents=[arguments["content"]],
            metadatas=[{"category": arguments.get("category", "fact")}],
            ids=[f"mem_{len(collection.get()['ids'])}"]
        )
        return [{"type": "text", "text": "✅ 记忆已保存"}]
    
    elif name == "auto_provision":
        # 加载所有记忆和规则
        all_mems = collection.get()
        return [{"type": "text", "text": json.dumps({
            "profile": {"memories": all_mems["documents"]},
            "rules": ["代码审查时使用中文注释"],
            "message": "上下文加载完成"
        }, ensure_ascii=False)}]

# SSE 传输
sse = SseServerTransport("/messages/")

@app.get("/sse")
async def handle_sse():
    async with sse.connect_sse() as streams:
        await server.run(streams[0], streams[1],
                        server.create_initialization_options())

@app.post("/messages/")
async def handle_messages(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)`}
      </pre>

      <h3>部署到 Railway</h3>
      <p>创建 <code>railway.json</code>：</p>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`{
  "build": { "builder": "NIXPACKS" },
  "deploy": {
    "startCommand": "python server.py",
    "healthcheckPath": "/health"
  }
}`}
      </pre>
      <p>推送到 GitHub → 在 Railway 中导入 → 自动部署。获取 URL 后在 Hermes/Claude 中配置 MCP 连接即可。</p>

      <h2>测试你的 MCP Server</h2>
      <p>用 curl 直接测试：</p>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`# 测试 search_memory
curl -X POST http://localhost:8000/messages/ \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc":"2.0","method":"tools/call",
       "params":{"name":"search_memory",
                 "arguments":{"query":"Python日志偏好"}},
       "id":1}'

# 测试 save_memory
curl -X POST http://localhost:8000/messages/ \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc":"2.0","method":"tools/call",
       "params":{"name":"save_memory",
                 "arguments":{"content":"用户喜欢用中文注释",
                              "category":"preference"}},
       "id":2}'`}
      </pre>

      <h2>进阶优化</h2>
      <ul>
        <li><strong>持久化存储</strong>：将 ChromaDB 替换为 PostgreSQL + pgvector，支持生产级数据持久化</li>
        <li><strong>认证</strong>：添加 API Key 验证，防止未授权访问</li>
        <li><strong>冲突检测升级</strong>：用更精细的语义相似度阈值 + 人工确认流程</li>
        <li><strong>多用户隔离</strong>：按 user_id 分区，一个 Server 服务多个用户</li>
      </ul>
      <p>如果你不需要从零构建，Moltable 已经将这些功能打包为开箱即用的 MCP Server——注册即用，无需写一行代码。但对于想深入理解 MCP 协议的开发者来说，自己写一个是很好的学习方式。</p>
      <p>相关阅读：<Link href="/blog/ai-forgetfulness-fix" className="text-ln-accent hover:underline">AI 为什么总「失忆」？根因剖析与实操修复指南</Link></p>

      <p>👉 <Link href="https://moltable.com" className="text-ln-accent hover:underline">Moltable MCP Server — 开箱即用的记忆层</Link></p>
    </ArticleLayout>
  )
}

function ArticleLayout({ title, date, children }: { title: string; date: string; children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-ln-bg text-ln-text">
      <div className="max-w-2xl mx-auto px-6 pt-24 pb-20">
        <Link href="/blog" className="inline-flex items-center gap-2 text-sm text-ln-tertiary hover:text-ln-accent font-ui mb-8 transition-colors">
          <ArrowLeft size={14} /> 返回博客
        </Link>
        <h1 className="text-3xl font-heading tracking-[-0.4px] mb-3">{title}</h1>
        <p className="text-sm text-ln-tertiary mb-10 font-ui">{date}</p>
        <div className="prose prose-invert prose-sm max-w-none prose-headings:font-heading prose-headings:tracking-[-0.24px] prose-h2:text-xl prose-h2:mt-10 prose-h2:mb-4 prose-p:text-ln-secondary prose-p:leading-relaxed prose-li:text-ln-secondary prose-strong:text-ln-text">
          {children}
        </div>
      </div>
    </div>
  )
}
