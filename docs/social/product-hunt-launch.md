# Product Hunt Launch — Moltable

> **Target Launch Window**: August 2026
> **Status**: Draft / Preparation
> **Last Updated**: 2026-08-06

---

## 🎯 Tagline (Pick One — A/B Test in Community)

1. **"Your AI agents share one identity. Finally."**
2. **"Stop re-teaching your AI who you are. Every. Single. Session."**
3. **"Identity Layer for AI Agents — because memory alone isn't enough."**
4. **"One identity. All your agents. Zero context pollution."**

🥇 **Primary Pick**: #3 — "Identity Layer for AI Agents — because memory alone isn't enough."

---

## 📝 Short Description (260 characters max for PH)

> Moltable is the Identity Layer for AI agents. Give your Claude, Cursor, and Codex a shared identity — preferences, Personas, project context, and MCP configs — that persists across devices and sessions. Open source. MIT license. Free for personal use.

*Character count: 259*

---

## 📄 Long Description

### The Problem

You use 3-4 AI agents daily. Claude for architecture. Cursor for coding. Codex for reviews.

And every single session, every new device, every new project — you start from zero. You re-explain your tech stack, your preferences, your project context. Over and over.

The average AI-native developer wastes **3.2 hours per week** re-teaching their agents who they are.

### Our Solution

Moltable is the **Identity Layer** for AI agents — a structured layer that sits between you and your AI tools, giving every agent a shared understanding of:

- **Who you are** (Identity)
- **What role you're in** (Persona)
- **How you work** (Preferences)
- **What you're working on** (Project context)
- **What tools you use** (MCP configurations)

One setup. Every agent. Every device. Zero repetition.

### What Makes It Different

| Other Solutions | Moltable |
|---|---|
| Memory Layer: stores facts | Identity Layer: understands context |
| Vector search: "find similar facts" | Identity Graph: "find relevant facts for this Persona" |
| Agent-specific configs | Cross-agent identity sync |
| Manual setup per device | Auto-provision via MCP |

### Key Features

- 🔐 **Persistent Identity**: Your agents recognize you across sessions, devices, and tools
- 🎭 **Multi-Persona**: Switch between "architect," "developer," "reviewer" — each with its own context
- 🔄 **MCP Auto-Provision**: One command to restore everything: `npx @moltable/connect`
- 📊 **Identity Graph**: Structured relationships, temporal awareness, project scoping
- 🌍 **Open Source**: MIT license. Self-host or use our cloud.
- 💰 **Free Tier**: 100 memories, 2 Personas — enough for most individual developers

### Tech Stack

- **Protocol**: MCP (Model Context Protocol)
- **Backend**: FastAPI + PostgreSQL + Redis
- **Identity Layer**: Neo4j-backed Identity Graph
- **Vector Store**: pgvector for memory embeddings
- **Frontend**: Next.js 14 + Tailwind CSS

---

## 🖼️ Media Assets

### Primary Image
- **Concept**: A hexagonal hub (Moltable logo) with lines radiating outward to Claude, Cursor, and Codex icons — representing the centralized identity layer connecting all AI agents.
- **Format**: PNG (2400×1260 for PH)
- **Status**: ⚠️ TO BE CREATED

### Screenshots (5 recommended for PH)
1. **Dashboard** — Identity overview with Persona switcher
2. **Persona Configuration** — Creating a "code-reviewer" Persona with preference overrides
3. **MCP Auto-Provision** — Terminal showing `npx @moltable/connect` restoring full environment
4. **Multi-Agent View** — Showing Claude, Cursor, Codex all connected to the same Identity
5. **Memory Graph Visualization** — (Coming soon) Identity Graph explorer

### GIF/Demo Video
- **Concept**: 30-second screen recording showing:
  1. Open Claude on new Mac → "Hello, I don't know you"
  2. Run `npx @moltable/connect claude`
  3. Reopen Claude → "Welcome back, John. Continuing Project X in code-reviewer mode."
- **Status**: ⚠️ TO BE RECORDED

---

## 🗣️ Maker Comment (First Comment After Launch)

> Hey Product Hunt! 👋
>
> I built Moltable because I was tired of having the same conversation every morning:
>
> "Hi Claude, remember me? I use TypeScript, deploy to Railway, and prefer tabs over spaces."
>
> Every. Single. Day.
>
> Moltable gives your AI agents a shared identity. Set it up once, and Claude, Cursor, Codex — they all know who you are, what you're working on, and how you like to work.
>
> It's open source (MIT), free for personal use, and takes <60 seconds to set up.
>
> I'd love to hear what you think — especially if you use multiple AI agents in your workflow. What's the most annoying "re-teaching" moment you've had?
>
> — Jovon & the Moltable team

---

## 🎤 Launch Day Checklist

- [ ] Product Hunt page fully set up (tagline, description, images, links)
- [ ] 5 screenshots uploaded
- [ ] Demo GIF/video finalized
- [ ] Maker comment drafted (✅ above)
- [ ] Social media posts scheduled (Twitter/X, LinkedIn, 即刻, Reddit r/programming)
- [ ] Email newsletter announcing launch prepared
- [ ] GitHub README polished with PH badge
- [ ] moltable.ai/blog/launch post published
- [ ] Team on standby for Q&A responses (first 4 hours critical)
- [ ] HN "Show HN" post prepared (launch 2-3 days before or after PH for staggered exposure)

---

## 🏷️ Tags (PH allows up to 5)

1. **Developer Tools**
2. **Artificial Intelligence**
3. **Open Source**
4. **Productivity**
5. **API**

---

## 👥 Target Upvote Channels

- Moltable existing user base (email + in-app notification)
- Twitter/X followers
- GitHub stargazers
- 即刻 (Chinese developer community)
- Hacker News cross-promotion
- AI/ML Discord communities
- r/programming, r/MachineLearning, r/opensource

---

## 📈 Success Metrics

| Metric | Target |
|---|---|
| Upvotes (Day 1) | 300+ |
| Upvotes (Week 1) | 500+ |
| Comments | 50+ (quality discussions) |
| New signups (launch week) | 1,000+ |
| GitHub stars (launch week) | 200+ new |
| Newsletter subs (launch week) | 150+ |

---

## 🔄 Post-Launch: Iteration Plan

- **Day 1-3**: Respond to every comment. Update PH page based on feedback.
- **Week 1**: Publish "What we learned from launching on Product Hunt" blog post.
- **Week 2**: Implement top-3 feature requests from PH comments.
- **Month 1**: Apply for PH "Golden Kitty" awards (Developer Tools category).

---

*Prepared by Moltable Marketing · Updated 2026-08-06*
