"use client";

import type { ChatMessage } from "@/lib/chat";

type MessageListProps = {
  messages: ChatMessage[];
  streamingPreview?: string | null;
};

export function MessageList({ messages, streamingPreview }: MessageListProps) {
  const isEmpty = messages.length === 0 && !streamingPreview;

  return (
    <div
      className="flex-1 overflow-y-auto px-4 py-6"
      aria-label="Historial de mensajes"
    >
      {isEmpty ? (
        <p className="mx-auto max-w-md text-center text-sm text-zinc-500">
          Preguntá sobre el libro. En la fase 3c se conectará el stream SSE al
          backend.
        </p>
      ) : (
        <ul className="mx-auto flex max-w-2xl flex-col gap-4">
          {messages.map((msg) => (
            <li
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-zinc-900 text-white"
                    : "border border-zinc-200 bg-white text-zinc-800 shadow-sm"
                }`}
              >
                <span className="sr-only">
                  {msg.role === "user" ? "Tú" : "Asistente"}:{" "}
                </span>
                {msg.content}
              </div>
            </li>
          ))}
          {streamingPreview ? (
            <li className="flex justify-start">
              <div className="max-w-[85%] rounded-2xl border border-sky-200 bg-sky-50 px-4 py-2.5 text-sm leading-relaxed text-zinc-800">
                <span className="sr-only">Asistente: </span>
                {streamingPreview}
                <span
                  className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-sky-600 align-middle"
                  aria-hidden
                />
              </div>
            </li>
          ) : null}
        </ul>
      )}
    </div>
  );
}
