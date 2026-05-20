"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiUrlBadge } from "@/components/ApiUrlBadge";
import { ChatInput } from "@/components/ChatInput";
import { ChatStatusBar } from "@/components/ChatStatusBar";
import { MessageList } from "@/components/MessageList";
import type { ChatMessage, ChatStatus } from "@/lib/chat";

const MOCK_STREAM_MS = 1400;
const MOCK_ERROR_TRIGGER = "__mock_error__";

function nextId(): string {
  return crypto.randomUUID();
}

/**
 * Simula streaming hasta fase 3c (SSE).
 * Mensaje exacto `__mock_error__` fuerza estado error para probar la UI.
 */
async function mockStreamReply(
  userText: string,
  onToken: (chunk: string) => void,
): Promise<{ ok: true; answer: string } | { ok: false; message: string }> {
  if (userText === MOCK_ERROR_TRIGGER) {
    await new Promise((r) => setTimeout(r, 400));
    return { ok: false, message: "Error simulado (fase 3b)." };
  }

  const answer =
    "Respuesta de ejemplo del asistente. En la fase 3c llegará el stream real desde /chat/stream.";
  const words = answer.split(" ");

  for (let i = 0; i < words.length; i++) {
    await new Promise((r) => setTimeout(r, MOCK_STREAM_MS / words.length));
    onToken((i === 0 ? "" : " ") + words[i]);
  }

  return { ok: true, answer };
}

export function ChatShell() {
  const [status, setStatus] = useState<ChatStatus>("idle");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streamingPreview, setStreamingPreview] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const streamAbort = useRef(false);

  useEffect(() => {
    return () => {
      streamAbort.current = true;
    };
  }, []);

  const handleSubmit = useCallback(async (text: string) => {
    streamAbort.current = false;
    setErrorMessage(null);
    setStreamingPreview(null);

    const userMessage: ChatMessage = {
      id: nextId(),
      role: "user",
      content: text,
    };
    setMessages((prev) => [...prev, userMessage]);
    setStatus("streaming");

    let accumulated = "";

    const result = await mockStreamReply(text, (chunk) => {
      if (streamAbort.current) return;
      accumulated += chunk;
      setStreamingPreview(accumulated);
    });

    if (streamAbort.current) return;

    setStreamingPreview(null);

    if (!result.ok) {
      setStatus("error");
      setErrorMessage(result.message);
      return;
    }

    const assistantMessage: ChatMessage = {
      id: nextId(),
      role: "assistant",
      content: result.answer,
    };
    setMessages((prev) => [...prev, assistantMessage]);
    setStatus("done");
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-zinc-50">
      <header className="shrink-0 border-b border-zinc-200 bg-white px-4 py-4">
        <div className="mx-auto flex max-w-2xl flex-col gap-3">
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-zinc-900">
              RAG-LIBRO
            </h1>
            <p className="text-sm text-zinc-600">
              Chat sobre &quot;30 Agents Every AI Engineer Must Build&quot; —
              fase 3b (shell)
            </p>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <ApiUrlBadge />
            <ChatStatusBar status={status} errorMessage={errorMessage} />
          </div>
        </div>
      </header>

      <MessageList messages={messages} streamingPreview={streamingPreview} />

      <ChatInput status={status} onSubmit={handleSubmit} />
    </div>
  );
}
