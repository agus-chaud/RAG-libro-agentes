"use client";

import { SourceBadges } from "@/components/SourceBadges";
import { SuggestedQuestions } from "@/components/SuggestedQuestions";
import type { ChatMessage, ChatStatus } from "@/lib/chat";
import { canSendMessage } from "@/lib/chat";
import { getRemainingSuggestedQuestions } from "@/lib/suggestedQuestions";

type MessageListProps = {
  messages: ChatMessage[];
  status: ChatStatus;
  streamingPreview?: string | null;
  streamingPages?: number[] | null;
  onSuggestedQuestion?: (question: string) => void;
};

export function MessageList({
  messages,
  status,
  streamingPreview,
  streamingPages,
  onSuggestedQuestion,
}: MessageListProps) {
  const isEmpty = messages.length === 0 && !streamingPreview;
  const userContents = messages
    .filter((m) => m.role === "user")
    .map((m) => m.content);
  const remainingSuggestions = getRemainingSuggestedQuestions(userContents);
  const showSuggestions =
    remainingSuggestions.length > 0 && Boolean(onSuggestedQuestion);
  const suggestionsDisabled = !canSendMessage(status);

  return (
    <div
      className="flex-1 overflow-y-auto px-4 py-6"
      aria-label="Historial de mensajes"
    >
      <div className="mx-auto flex max-w-2xl flex-col">
        {!isEmpty ? (
          <ul className="flex flex-col gap-4">
            {messages.map((msg) => (
              <li
                key={msg.id}
                className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
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
                {msg.role === "assistant" &&
                msg.pages &&
                msg.pages.length > 0 ? (
                  <div className="max-w-[85%] px-1">
                    <SourceBadges pages={msg.pages} />
                  </div>
                ) : null}
              </li>
            ))}
            {streamingPreview ? (
              <li className="flex flex-col items-start">
                <div className="max-w-[85%] rounded-2xl border border-sky-200 bg-sky-50 px-4 py-2.5 text-sm leading-relaxed text-zinc-800">
                  <span className="sr-only">Asistente: </span>
                  {streamingPreview}
                  <span
                    className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-sky-600 align-middle"
                    aria-hidden
                  />
                </div>
                {streamingPages && streamingPages.length > 0 ? (
                  <div className="max-w-[85%] px-1">
                    <SourceBadges pages={streamingPages} />
                  </div>
                ) : null}
              </li>
            ) : null}
          </ul>
        ) : null}

        {showSuggestions && onSuggestedQuestion ? (
          <SuggestedQuestions
            questions={remainingSuggestions}
            compact={!isEmpty}
            disabled={suggestionsDisabled}
            onSelect={onSuggestedQuestion}
          />
        ) : isEmpty ? (
          <p className="text-center text-sm text-zinc-500">
            Preguntá sobre el libro. Las respuestas llegan en streaming desde el
            backend con las páginas citadas.
          </p>
        ) : null}
      </div>
    </div>
  );
}
