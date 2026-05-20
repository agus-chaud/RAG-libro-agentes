const DEFAULT_API_URL = "http://localhost:8000";

/** Base URL del backend FastAPI (solo vars NEXT_PUBLIC_* en cliente). */
export function getApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL?.trim() || DEFAULT_API_URL;
}
