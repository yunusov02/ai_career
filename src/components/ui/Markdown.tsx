import React from 'react';

interface Block {
  type: 'code' | 'text';
  content: string;
  lang?: string;
}

function splitBlocks(raw: string): Block[] {
  const blocks: Block[] = [];
  const re = /```(\w*)\n?([\s\S]*?)```/g;
  let last = 0;
  let match: RegExpExecArray | null;
  while ((match = re.exec(raw)) !== null) {
    if (match.index > last) {
      blocks.push({ type: 'text', content: raw.slice(last, match.index) });
    }
    blocks.push({ type: 'code', lang: match[1] || undefined, content: match[2].trimEnd() });
    last = match.index + match[0].length;
  }
  if (last < raw.length) blocks.push({ type: 'text', content: raw.slice(last) });
  return blocks;
}

function parseInline(text: string): React.ReactNode[] {
  const out: React.ReactNode[] = [];
  const re = /\*\*(.+?)\*\*|`([^`]+)`/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let k = 0;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(text.slice(last, m.index));
    if (m[1] !== undefined) {
      out.push(<strong key={k++}>{m[1]}</strong>);
    } else {
      out.push(
        <code key={k++} className="rounded bg-slate-100 px-1 font-mono text-[11px] text-slate-800">
          {m[2]}
        </code>,
      );
    }
    last = m.index + m[0].length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

function renderText(text: string): React.ReactNode {
  const lines = text.split('\n');
  const nodes: React.ReactNode[] = [];
  let listItems: React.ReactNode[] = [];
  let listKind: 'ol' | 'ul' | null = null;
  let key = 0;

  const flush = () => {
    if (!listItems.length) return;
    if (listKind === 'ol') {
      nodes.push(
        <ol key={key++} className="my-2 ml-5 list-decimal space-y-1 text-sm leading-relaxed">
          {listItems.map((item, i) => <li key={i}>{item}</li>)}
        </ol>,
      );
    } else {
      nodes.push(
        <ul key={key++} className="my-2 ml-5 list-disc space-y-1 text-sm leading-relaxed">
          {listItems.map((item, i) => <li key={i}>{item}</li>)}
        </ul>,
      );
    }
    listItems = [];
    listKind = null;
  };

  for (const line of lines) {
    const ol = line.match(/^\d+\.\s+([\s\S]+)/);
    const ul = line.match(/^[-*]\s+([\s\S]+)/);
    if (ol) {
      if (listKind === 'ul') flush();
      listKind = 'ol';
      listItems.push(parseInline(ol[1]));
    } else if (ul) {
      if (listKind === 'ol') flush();
      listKind = 'ul';
      listItems.push(parseInline(ul[1]));
    } else {
      flush();
      if (line.trim()) {
        nodes.push(
          <p key={key++} className="my-1 text-sm leading-relaxed">
            {parseInline(line)}
          </p>,
        );
      } else {
        nodes.push(<div key={key++} className="my-1" />);
      }
    }
  }
  flush();
  return <>{nodes}</>;
}

export function Markdown({ content }: { content: string }) {
  return (
    <div>
      {splitBlocks(content).map((block, i) =>
        block.type === 'code' ? (
          <pre
            key={i}
            className="my-2 overflow-x-auto rounded-lg bg-slate-900 p-3 text-[11px] leading-5 text-slate-100"
          >
            <code>{block.content}</code>
          </pre>
        ) : (
          <div key={i}>{renderText(block.content)}</div>
        ),
      )}
    </div>
  );
}

export default Markdown;
