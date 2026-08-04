'use client'

interface Content {
  title: string
  date: string
  author: string
  tags: string[]
  body: string
}

function renderMarkdown(md: string) {
  let html = md
  // headings
  html = html.replace(/^### (.+)$/gm, '<h3 class="text-lg font-heading tracking-[-0.24px] mt-8 mb-3">$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2 class="text-xl font-heading tracking-[-0.24px] mt-10 mb-4">$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h2 class="text-xl font-heading tracking-[-0.24px] mt-10 mb-4">$1</h2>')
  // bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="text-ln-text">$1</strong>')
  // italic
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  // inline code
  html = html.replace(/`([^`]+)`/g, '<code class="bg-ln-border/30 px-1 py-0.5 rounded text-sm font-mono">$1</code>')
  // horizontal rule
  html = html.replace(/^---$/gm, '<hr class="border-ln-border my-8" />')
  // links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-ln-accent hover:underline" target="_blank" rel="noopener">$1</a>')
  // blockquotes
  html = html.replace(/^> (.+)$/gm, '<blockquote class="border-l-2 border-ln-accent pl-4 my-4 text-ln-tertiary italic">$1</blockquote>')
  // unordered lists
  html = html.replace(/^- (.+)$/gm, '<li class="text-ln-secondary leading-relaxed ml-4 list-disc">$1</li>')
  // ordered lists
  html = html.replace(/^\d+\. (.+)$/gm, '<li class="text-ln-secondary leading-relaxed ml-4 list-decimal">$1</li>')
  // paragraphs (lines that aren't tags)
  const lines = html.split('\n')
  const out: string[] = []
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (line.startsWith('<') || line.trim() === '') {
      out.push(line)
    } else if (line.trim()) {
      out.push(`<p class="text-ln-secondary leading-relaxed my-3">${line}</p>`)
    }
  }
  return out.join('\n')
}

export default function BlogPost({ content }: { content: { zh: Content } }) {
  const c = content.zh

  return (
    <>
      <h1 className="text-3xl font-heading tracking-[-0.4px] mb-3">{c.title}</h1>
      <div className="flex items-center gap-4 text-sm text-ln-tertiary mb-4 font-ui">
        <span>{c.date}</span>
        <span>·</span>
        <span>{c.author}</span>
      </div>
      <div className="flex flex-wrap gap-2 mb-10">
        {c.tags.map((tag) => (
          <span
            key={tag}
            className="text-xs px-2 py-0.5 rounded-full bg-ln-border/30 text-ln-tertiary font-ui"
          >
            {tag}
          </span>
        ))}
      </div>
      <div
        className="prose prose-invert prose-sm max-w-none prose-headings:font-heading prose-headings:tracking-[-0.24px] prose-h2:text-xl prose-h2:mt-10 prose-h2:mb-4 prose-p:text-ln-secondary prose-p:leading-relaxed prose-li:text-ln-secondary prose-strong:text-ln-text"
        dangerouslySetInnerHTML={{ __html: renderMarkdown(c.body) }}
      />
    </>
  )
}
