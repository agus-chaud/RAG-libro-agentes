import {
  EventStreamContentType,
  fetchEventSource,
} from "@microsoft/fetch-event-source";
import { getApiUrl } from "@/lib/api";

export type StreamChatCallbacks = {
  onSources: (pages: number[]) => void;
  onToken: (token: string) => void;
  onDone: () => void;
  onError: (message: string) => void;
};

class StreamChatError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "StreamChatError";
  }
}

/** Detiene reintentos automáticos de fetch-event-source. */
class FatalStreamError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "FatalStreamError";
  }
}

function parseSourcesData(raw: string): number[] {
  const parsed: unknown = JSON.parse(raw);
  if (!Array.isArray(parsed) || !parsed.every((p) => typeof p === "number")) {
    throw new StreamChatError("Evento sources con formato inválido.");
  }
  return parsed;
}

function parseTokenData(raw: string): string {
  const parsed: unknown = JSON.parse(raw);
  if (typeof parsed !== "string") {
    throw new StreamChatError("Evento token con formato inválido.");
  }
  return parsed;
}

async function readErrorDetail(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map((d) => JSON.stringify(d)).join("; ");
    }
  } catch {
    /* respuesta no JSON */
  }
  return `HTTP ${response.status}`;
}

/**
 * Cliente SSE (fase 3c): POST a /chat/stream con { message }.
 * Protocolo: sources → token* → done (FastAPI + sse-starlette).
 */
export async function streamChat(
  message: string,
  callbacks: StreamChatCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  const url = `${getApiUrl()}/chat/stream`;
  let sawDone = false;

  try {
    await fetchEventSource(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
      signal,
      openWhenHidden: true,
      async onopen(response) {
        if (
          response.ok &&
          response.headers.get("content-type")?.includes(EventStreamContentType)
        ) {
          return;
        }
        const detail = await readErrorDetail(response);
        throw new FatalStreamError(detail);
      },
      onmessage(ev) {
        if (!ev.event) return;

        try {
          if (ev.event === "sources") {
            callbacks.onSources(parseSourcesData(ev.data));
            return;
          }
          if (ev.event === "token") {
            callbacks.onToken(parseTokenData(ev.data));
            return;
          }
          if (ev.event === "done") {
            sawDone = true;
            callbacks.onDone();
          }
        } catch (err) {
          const msg =
            err instanceof StreamChatError
              ? err.message
              : "Error al interpretar un evento SSE.";
          throw new FatalStreamError(msg);
        }
      },
      onerror(err) {
        if (signal?.aborted) return;
        throw err;
      },
    });
  } catch (err) {
    if (signal?.aborted) return;
    const msg =
      err instanceof StreamChatError || err instanceof FatalStreamError
        ? err.message
        : err instanceof Error
          ? err.message
          : "No se pudo conectar con el backend.";
    callbacks.onError(msg);
    return;
  }

  if (!sawDone && !signal?.aborted) {
    callbacks.onError("El stream terminó sin evento done.");
  }
}
