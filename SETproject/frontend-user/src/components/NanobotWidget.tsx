"use client";

import { useState, useRef, useEffect, type FormEvent } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

// Simple markdown renderer
function renderMarkdown(text: string): string {
  let html = text
    // Escape HTML
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    // Headers
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/^## (.+)$/gm, "<h2>$1</h2>")
    .replace(/^# (.+)$/gm, "<h1>$1</h1>")
    // Bold
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    // Italic
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    // Inline code
    .replace(/`(.+?)`/g, "<code>$1</code>")
    // Line breaks
    .replace(/\n/g, "<br>");
  return html;
}

function TypingIndicator() {
  return (
    <div className="msg assistant typing">
      <span className="typing-dot" />
      <span className="typing-dot" />
      <span className="typing-dot" />
    </div>
  );
}

export default function NanobotWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (!open) return;
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const accessKey = "projectset-secret-key";
    const wsUrl = `${protocol}//${window.location.host}/ws/chat?access_key=${accessKey}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    ws.onopen = () => { console.log("Nanobot connected"); setConnected(true); };
    ws.onclose = () => { console.log("Nanobot disconnected"); setConnected(false); };
    ws.onerror = () => setConnected(false);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const content = data.content ?? JSON.stringify(data);
        setMessages((prev) => [...prev, { role: "assistant", content }]);
      } catch {
        setMessages((prev) => [...prev, { role: "assistant", content: event.data }]);
      }
      setLoading(false);
    };
    return () => { ws.close(); wsRef.current = null; };
  }, [open]);

  const sendMessage = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const text = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ content: text }));
    }
  };

  if (!open) {
    return (
      <button className="nanobot-toggle" onClick={() => setOpen(true)} aria-label="Открыть ассистент">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
      </button>
    );
  }

  return (
    <div className="nanobot-window">
      <div className="nanobot-header">
        <span>
          Assistent
          <span className={`status-dot ${connected ? "online" : "offline"}`} />
        </span>
        <button className="nanobot-close" onClick={() => setOpen(false)}>&times;</button>
      </div>
      <div className="nanobot-messages">
        {messages.length === 0 && (
          <div className="msg assistant">
            👋 Hi! Ask me about games, prices, or recommendations.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            {m.role === "assistant"
              ? <span dangerouslySetInnerHTML={{ __html: renderMarkdown(m.content) }} />
              : m.content}
          </div>
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
      <form className="nanobot-input" onSubmit={sendMessage}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={connected ? "Send a message…" : "Connecting…"}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </form>
    </div>
  );
}
