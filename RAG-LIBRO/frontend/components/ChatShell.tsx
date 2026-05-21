"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiUrlBadge } from "@/components/ApiUrlBadge";
import { ChatInput } from "@/components/ChatInput";
import { ChatStatusBar } from "@/components/ChatStatusBar";
import { MessageList } from "@/components/MessageList";
import type { ChatMessage, ChatStatus } from "@/lib/chat";
import { streamChat } from "@/lib/streamChat";

function nextId(): string {
  return crypto.randomUUID();
}

export function ChatShell() {
  const [status, setStatus] = useState<ChatStatus>("idle");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streamingPreview, setStreamingPreview] = useState<string | null>(null);
  const [streamingPages, setStreamingPages] = useState<number[] | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  const handleSubmit = useCallback(async (text: string) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setErrorMessage(null);
    setStreamingPreview(null);
    setStreamingPages(null);

    const userMessage: ChatMessage = {
      id: nextId(),
      role: "user",
      content: text,
    };
    setMessages((prev) => [...prev, userMessage]);
    setStatus("streaming");

    let accumulated = "";
    let pages: number[] = [];

    await streamChat(
      text,
      {
        onSources: (received) => {
          pages = received;
          setStreamingPages(received);
        },
        onToken: (token) => {
          accumulated += token;
          setStreamingPreview(accumulated);
        },
        onDone: () => {
          if (controller.signal.aborted) return;

          setStreamingPreview(null);
          setStreamingPages(null);

          const assistantMessage: ChatMessage = {
            id: nextId(),
            role: "assistant",
            content: accumulated,
            pages: pages.length > 0 ? pages : undefined,
          };
          setMessages((prev) => [...prev, assistantMessage]);
          setStatus("done");
        },
        onError: (message) => {
          if (controller.signal.aborted) return;

          setStreamingPreview(null);
          setStreamingPages(null);
          setStatus("error");
          setErrorMessage(message);
        },
      },
      controller.signal,
    );
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
              streaming SSE + fuentes
            </p>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <ApiUrlBadge />
            <ChatStatusBar status={status} errorMessage={errorMessage} />
          </div>
        </div>
      </header>

      <MessageList
        messages={messages}
        status={status}
        streamingPreview={streamingPreview}
        streamingPages={streamingPages}
        onSuggestedQuestion={handleSubmit}
      />

      <ChatInput status={status} onSubmit={handleSubmit} />
    </div>
  );
}
