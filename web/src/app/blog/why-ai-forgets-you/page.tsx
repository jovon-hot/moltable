'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function ArticlePage() {
  return (
    <ArticleLayout title="为什么你的 AI 每次都不记得你是谁 —— 以及 2026 年的终极解决方案" date="2026-08-05">
      <p><strong>早上 9 点 27 分。你端着咖啡坐下，打开 Claude，准备继续昨天没调完的那个 bug。你打出：「早上好，帮我看一下昨天那个 Prisma 的报错。」</strong></p>
      <p><strong>它回你：「Hello! I don't have any context from previous conversations. Could you share the error message and your setup?」</strong></p>
      <p>你已经用了它六个月。它知道你喜欢 TypeScript、习惯 tab 缩进、部署走 Railway、讨厌冗长的解释。但每个新的一天——不，每一场新的对话——它都像第一次见到你一样，礼貌、专业、而且一无所知。</p>
      <p>这不是你的错觉，也不是 AI 变笨了。这是 2026 年 AI 行业最大的体验断层：<strong>你的 AI 有智能，但没有「你」。</strong></p>
      <p>这篇文章会告诉你三件事：为什么 AI 非失忆不可、失忆到底让你损失了什么，以及一个彻底终结这个问题的方案。</p>

      <h2>每天早上，你都在和一个陌生人说话</h2>
      <p>先别急着骂 AI。我们来盘点一下，这段「每天重新认识」的关系里，你到底在反复付出什么代价。</p>
      <p><strong>第一，你的偏好永远在重置。</strong>「用 TypeScript，不要 JavaScript」「tab 缩进，Prettier 默认配置」「部署到 Railway，别问我 Vercel」——这些话你六个月里说了至少两百遍。每次新会话，你都要像第一次面试一样，把自己的技术栈、代码风格、部署习惯重新背一遍。AI 听完点点头，然后第二天忘得干干净净。</p>
      <p><strong>第二，项目上下文说没就没。</strong>「user-service 是独立的微服务，数据库在 Supabase，环境变量在 .env.production 里」——这些你花了几周才沉淀下来的项目知识，一次会话结束就蒸发。昨天你俩还在讨论把 Redis Streams 换成 Kafka，今天它问你：「你的项目用的什么消息队列？」你只能叹气。</p>
      <p><strong>第三，工具配置跟着一起丢。</strong>你精心配置的 MCP Server、API Key、自定义指令，换一个 Agent、换一台电脑、甚至只是开个新会话，全部归零。上次你花了四十分钟把 Cursor 的 MCP 配置写对，下次重装系统，又是一个四十分钟。</p>
      <p><strong>第四，你的 Persona 被遗忘了。</strong>你费心调教出来的「严格代码审查员」人格——专挑边界条件、绝不客气——新会话里荡然无存。它又变回那个只会说「Looks good to me!」的老好人。你精心塑造的每一个角色，都像演员下了台，再也没回来。</p>
      <p><strong>第五，自我介绍永无止境。</strong>「我是做 SaaS 的独立开发者，单人团队，技术栈 Next.js + Prisma + PostgreSQL，目标用户是欧洲中小企业，预算敏感……」这段话你一天要复述好几遍，给不同的 AI、不同的会话。你的人生成了一部永远在播放的开场白。</p>
      <p>五件事，每天重复。算下来，一个开发者每周要花 3-5 个小时在「让 AI 重新认识自己」上。这不是效率问题，这是尊严问题——<strong>你明明是个有历史、有偏好、有判断的人，却在 AI 眼里永远是个第一天入职的新人。</strong></p>

      <h2>为什么 AI 非失忆不可？四个根因</h2>
      <p>理解根因，才能找到真正的解药。AI 失忆不是某个公司的产品缺陷，而是当前架构的必然结果。</p>
      <h3>根因一：无状态架构（Stateless Architecture）</h3>
      <p>大语言模型本质上是一个纯函数：同样的输入，永远产生同样的输出。它不「记得」任何东西——每一次推理都是从头开始。所谓「记忆」，只是把历史对话重新塞回输入里。这意味着：<strong>没有输入，就没有记忆。</strong>这是架构层面的先天设计，不是 bug。</p>
      <h3>根因二：上下文窗口的物理天花板</h3>
      <p>今天的模型有 20 万甚至 100 万 token 的上下文窗口，听起来很大，但你的整个项目、全部历史对话、所有偏好加起来，轻松超过这个量级。更致命的是：<strong>上下文窗口不是记忆，它是工作台。</strong>窗口一关，桌上的一切都被清空。模型厂商拼命扩窗口，但扩的是「一次能看多少」，不是「永远记得多少」。</p>
      <h3>根因三：没有持久化层</h3>
      <p>你的对话记录存在哪里？存在某个工具的本地数据库里，存在厂商的服务器上，存在浏览器的 localStorage 里。它们互不相通，格式各异，无法迁移。<strong>对话记录不是「记忆」，只是「日志」。</strong>日志可以被清空、被覆盖、被锁死在某个产品里。而真正的记忆，应该是结构化的、可查询的、属于你的数据资产。</p>
      <h3>根因四：会话即生命周期的设计</h3>
      <p>整个 AI 产品生态都建立在「会话」这个单位上。会话结束，一切归零。这个设计在 ChatGPT 时代是合理的——那时候 AI 只是个问答工具。但 2026 年的 AI 是你的协作者、你的队友、你的合伙人。<strong>合伙人会每天失忆吗？不会。因为合伙人有一个持续存在的「身份」。</strong></p>
      <p>四个根因，指向同一个结论：<strong>问题的本质不是「记忆不够大」，而是「身份不存在」。</strong>你给 AI 喂再多的对话，它记住的也只是片段；你给它一个身份，它才真正「认识」你。</p>

      <h2>解法：给 AI 一个 Identity Layer</h2>
      <p>Moltable 的答案，是在模型之上、Agent 之下，加一层独立的<strong>身份层（Identity Layer）</strong>。它不存对话，存的是关于「你是谁」的结构化数据。身份层分三层：</p>

      <div className="space-y-3 my-4">
        <div className="bg-ln-panel p-4 rounded-lg">
          <h3 className="text-base font-heading mb-1">Identity Layer（你是谁）</h3>
          <p className="text-sm text-ln-secondary">邮箱、设备指纹、API Key 绑定——你的身份锚点，跨设备、跨 Agent 唯一</p>
        </div>
        <div className="bg-ln-panel p-4 rounded-lg">
          <h3 className="text-base font-heading mb-1">Persona Layer（你怎么想）</h3>
          <p className="text-sm text-ln-secondary">角色特征、回答风格、模型偏好——你的「思维模式」可以被持久化加载</p>
        </div>
        <div className="bg-ln-panel p-4 rounded-lg">
          <h3 className="text-base font-heading mb-1">Memory Layer（你知道什么）</h3>
          <p className="text-sm text-ln-secondary">偏好、项目上下文、工具配置——你积累的所有「知识资产」</p>
        </div>
      </div>

      <p>这三层数据通过 MCP 协议暴露给任意 Agent。任何一个支持 MCP 的 AI——Claude、Cursor、Codex、Hermes——接入 Moltable 后，都会在会话开始时自动加载你的完整身份。<strong>对话还是那个对话，但 AI 不再是那个失忆的 AI。</strong></p>
      <p>一个简单的比喻：过去的 AI 是临时工，每天来上班，谁也不认识；接入 Moltable 后的 AI 是正式员工，入职第一天就拿到了你的全部档案。<Link href="/register" className="text-ln-accent hover:underline">免费注册</Link>，30 秒就能建好这份档案。</p>

      <h2>它怎么工作？一次配置，永久生效</h2>
      <p>接入流程短到不像真的。第一次使用时，你只需要让 AI 记录一次你的偏好：</p>

      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`你：帮我记录我的开发偏好。

Claude 调用 moltable 工具...

记录完成：
✅ 语言偏好：TypeScript > Python > Go
✅ 代码风格：Prettier 默认配置、tab 缩进
✅ 部署目标：Railway（主）、Vercel（前端）
✅ 项目路径：~/work/my-saas/
✅ 技术栈：Next.js 14 + Prisma + PostgreSQL + Redis`}
      </pre>

      <p>这些记录进入 Moltable 的持久化存储，成为你身份的一部分。之后每一次会话，Agent 通过 <code>auto_provision</code> 工具自动拉取身份数据，<strong>不需要你手动写任何 prompt、不需要复制粘贴任何 JSON。</strong></p>
      <p>换一台新电脑？一条命令：</p>

      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`# 一条命令接入 Claude Desktop
npx @moltable/connect claude --api-key molt_k7xq9p2v_xxxxx

# 同样适配其他 Agent
npx @moltable/connect cursor --api-key <your-key>
npx @moltable/connect hermes --api-key <your-key>`}
      </pre>

      <p>而且，身份数据是<strong>跨 Agent 同步</strong>的。你在 Claude 里记录的新偏好，Cursor 下次启动时自动就能读到。一次配置，所有 Agent 共享——这正是 Identity Layer 和单点记忆工具的本质区别。</p>

      <h2>一天的日常：当所有 Agent 都记得你</h2>
      <p>场景比理论更有说服力。这是接入 Moltable 之后，一个普通开发者的一天：</p>
      <h3>上午 9:30 — 写代码</h3>
      <p>你打开 Cursor，只说了一句：「继续昨天的 user-service 重构。」它知道你在重构认证模块、知道你要保持 Prisma schema 兼容、知道你不想用 any、知道代码风格是 tab 缩进。它直接给出了符合你所有约束的重构方案。<strong>没有铺垫，没有自我介绍，直接进入正题。</strong></p>
      <h3>下午 2:00 — 设计评审</h3>
      <p>你用 Claude 开了一个新会话做架构评审。你加载「严格审查员」Persona——这是你三个月前调教好的角色，专挑边界条件和竞态问题。它没有变成老好人，它上来就指出你的 Redis 缓存一致性方案在并发写场景下的三个漏洞。<strong>你的审查员，还是那个审查员。</strong></p>
      <h3>晚上 9:00 — 写作</h3>
      <p>你打开 Hermes，想写一篇技术博客。它知道你的文风偏好：短段落、少形容词、中文为主、偶尔夹一句英文术语。它甚至记得你上周写到一半的那篇关于 MCP 的文章，直接问：「要不要接着上次的提纲写？」<strong>你的 AI 不再只是工具，它开始像一位了解你的同事。</strong></p>
      <p>注意一个细节：这三个场景用了三个不同的 Agent，但它们的表现像同一个人——因为<strong>它们共享的是同一个身份。</strong>这就是 Moltable 想做的事：不是给某个 AI 加记忆，而是让你的「数字身份」独立于任何一家厂商、任何一个工具而存在。</p>

      <h2>有 Moltable 之前 vs 之后</h2>
      <table className="w-full text-xs my-6 border-collapse">
        <thead>
          <tr style={{ background: 'rgba(0,224,64,0.12)' }}>
            <th className="p-3 text-left font-medium">场景</th>
            <th className="p-3 text-left font-medium">没有 Moltable</th>
            <th className="p-3 text-left font-medium">有 Moltable</th>
          </tr>
        </thead>
        <tbody>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">新会话开始</td>
            <td className="p-3">重新自我介绍，重新陈述技术栈</td>
            <td className="p-3">auto_provision 自动加载，直接开工</td>
          </tr>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">换新电脑</td>
            <td className="p-3">全部配置手写，MCP JSON 逐个重建</td>
            <td className="p-3">一条 npx 命令，环境完整恢复</td>
          </tr>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">换一个 Agent</td>
            <td className="p-3">新 Agent 从零认识你</td>
            <td className="p-3">同一个身份，无缝迁移</td>
          </tr>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">自定义 Persona</td>
            <td className="p-3">每次会话手动加载 prompt</td>
            <td className="p-3">Persona 持久化，一键调用</td>
          </tr>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <td className="p-3">项目上下文</td>
            <td className="p-3">每次对话重新「教」一遍</td>
            <td className="p-3">长期沉淀，越用越懂你</td>
          </tr>
          <tr>
            <td className="p-3">每周隐性成本</td>
            <td className="p-3">3-5 小时重复沟通</td>
            <td className="p-3">几乎为零</td>
          </tr>
        </tbody>
      </table>

      <p>最值得注意的不是「省了 3 个小时」，而是「关系变了」。一个记得你的 AI，和一个不认识你的 AI，产出的质量完全不在一个量级——因为<strong>真正高质量的协作，建立在长期积累的默契上。</strong></p>

      <h2>现在就开始：让你的 AI 永远认识你</h2>
      <p>2026 年，AI 的能力已经足够强。唯一缺的，是让它认识你。</p>
      <pre className="bg-ln-panel rounded-lg p-4 text-xs overflow-x-auto my-4">
{`# 30 秒注册
open https://moltable.ai/register

# 60 秒接入你的 Agent
npx @moltable/connect claude --api-key <your-key>

# 说一句「记录我的偏好」
# 从此，你的 AI 不再失忆。`}
      </pre>
      <p>👉 <Link href="/register" className="text-ln-accent hover:underline">免费注册 Moltable — 一次配置，所有 Agent 共享</Link></p>
      <p>开源、MIT 协议、端到端加密。你的身份数据，永远属于你自己。</p>
      <p className="text-xs text-ln-tertiary mt-6">
        GitHub: <a href="https://github.com/jovon-hot/moltable" className="text-ln-accent hover:underline">jovon-hot/moltable</a> · MIT License
      </p>
      <p className="text-xs text-ln-tertiary mt-3">Built for developers, by developers. 💜</p>
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
