import type { MDXComponents } from 'mdx/types'

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    h1: (props) => (
      <h1 style={{ fontSize: '1.75rem', fontWeight: 600, color: '#F5F4F8', marginBottom: '0.75rem', letterSpacing: '-0.3px' }} {...props} />
    ),
    h2: (props) => (
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#F5F4F8', marginTop: '2rem', marginBottom: '0.75rem' }} {...props} />
    ),
    h3: (props) => (
      <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#A8A5B8', marginTop: '1.5rem', marginBottom: '0.5rem' }} {...props} />
    ),
    p: (props) => (
      <p style={{ fontSize: '0.9375rem', lineHeight: '1.75', color: '#A8A5B8', marginBottom: '1rem' }} {...props} />
    ),
    strong: (props) => (
      <strong style={{ color: '#F5F4F8', fontWeight: 600 }} {...props} />
    ),
    a: (props) => (
      <a style={{ color: '#818CF8', textDecoration: 'underline', textUnderlineOffset: '2px' }} {...props} />
    ),
    ul: (props) => (
      <ul style={{ paddingLeft: '1.25rem', marginBottom: '1rem' }} {...props} />
    ),
    ol: (props) => (
      <ol style={{ paddingLeft: '1.25rem', marginBottom: '1rem' }} {...props} />
    ),
    li: (props) => (
      <li style={{ fontSize: '0.9375rem', lineHeight: '1.75', color: '#A8A5B8', marginBottom: '0.25rem' }} {...props} />
    ),
    blockquote: (props) => (
      <blockquote
        style={{
          borderLeft: '3px solid #4338CA',
          paddingLeft: '1rem',
          margin: '1.5rem 0',
          fontStyle: 'italic',
          color: '#85829E',
        }}
        {...props}
      />
    ),
    code: (props) => (
      <code
        style={{
          background: '#14141E',
          padding: '0.15em 0.4em',
          borderRadius: '4px',
          fontSize: '0.85em',
          fontFamily: "'Geist Mono', 'SF Mono', monospace",
          color: '#FB6B4B',
        }}
        {...props}
      />
    ),
    pre: (props) => (
      <pre
        style={{
          background: '#0D0D14',
          border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: '8px',
          padding: '1rem',
          overflow: 'auto',
          fontSize: '0.8125rem',
          lineHeight: '1.6',
          margin: '1.25rem 0',
        }}
        {...props}
      />
    ),
    hr: (props) => (
      <hr style={{ border: 'none', borderTop: '1px solid rgba(255,255,255,0.06)', margin: '2rem 0' }} {...props} />
    ),
    img: (props) => (
      <img style={{ maxWidth: '100%', borderRadius: '8px', margin: '1.5rem 0' }} {...props} />
    ),
    table: (props) => (
      <div style={{ overflow: 'auto', margin: '1.25rem 0' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }} {...props} />
      </div>
    ),
    th: (props) => (
      <th style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', padding: '0.5rem 0.75rem', textAlign: 'left', color: '#F5F4F8', fontWeight: 600 }} {...props} />
    ),
    td: (props) => (
      <td style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', padding: '0.5rem 0.75rem', color: '#A8A5B8' }} {...props} />
    ),
    ...components,
  }
}
