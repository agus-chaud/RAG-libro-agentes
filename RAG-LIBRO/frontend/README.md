# Frontend RAG-LIBRO

Interfaz del chat sobre el libro. Stack: **Next.js 14**, App Router, Tailwind, SSE vía `@microsoft/fetch-event-source`.

## Arranque rápido

```powershell
copy .env.example .env.local
npm install
npm run dev
```

Abrí [http://localhost:3000](http://localhost:3000). El backend debe estar en `http://localhost:8000` (ver README raíz).

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Fases completadas

| Fase | Entregable |
|------|------------|
| **3a** | Scaffold Next 14 + `NEXT_PUBLIC_API_URL` + `ApiUrlBadge` |
| **3b** | `ChatShell`, estados `idle \| streaming \| done \| error`, input bloqueado en stream |
| **3c** | `lib/streamChat.ts` — POST `/chat/stream`, handlers `sources` / `token` / `done` |
| **3d** | `SourceBadges` — chips `p. N` bajo asistente (stream + historial) |
| **3e** | Gate E2E: smoke API en `../scripts/smoke_ui_e2e.py`; checklist UI en `../CHECKLIST_E2E.md` |

## Probar el chat (manual, gate 3e)

1. Levantá API + frontend (README raíz).
2. Enviá Q01 de `EVAL.md`: *What is an AI agent according to this book?*
3. Verificá: texto en streaming, chips de páginas, estado **Completado**.

## Archivos principales

| Archivo | Rol |
|---------|-----|
| `components/ChatShell.tsx` | Estado, `streamChat`, mensajes |
| `lib/streamChat.ts` | Cliente SSE |
| `components/SourceBadges.tsx` | Fuentes (páginas) |
| `components/MessageList.tsx` | Historial + preview |
| `lib/chat.ts` | Tipos `ChatStatus`, `ChatMessage` |

## Scripts

```powershell
npm run dev
npm run build
npm run lint
```
