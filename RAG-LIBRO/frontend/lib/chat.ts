/** Estados del chat (fase 3b); el cliente SSE los actualiza en fase 3c. */
export type ChatStatus = "idle" | "streaming" | "done" | "error";

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  /** Páginas del libro citadas (evento SSE `sources`). */
  pages?: number[];
}

export const CHAT_STATUS_LABELS: Record<ChatStatus, string> = {
  idle: "Listo",
  streaming: "Generando…",
  done: "Completado",
  error: "Error",
};

export function canSendMessage(status: ChatStatus): boolean {
  return status === "idle" || status === "done" || status === "error";
}
