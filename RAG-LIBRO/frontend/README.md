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
| **3f** | Preguntas sugeridas (one-click): 5 botones alineados al golden set; las ya enviadas desaparecen de la lista |

## Preguntas sugeridas (3f)

Lista canónica en `lib/suggestedQuestions.ts` (fuente de verdad del texto). Mapeo a `EVAL.md`: Q01, Q07, Q08, Q05, Q06.

| Comportamiento | Detalle |
|----------------|---------|
| Estado vacío | 5 botones bajo el texto intro; un clic envía la pregunta (mismo flujo que **Enviar**) |
| Tras cada respuesta | Siguen visibles solo las sugerencias **no** enviadas (match exacto con mensajes `user`) |
| Las 5 usadas | La sección de sugerencias desaparece |
| Durante `streaming` | Botones deshabilitados (igual que el input) |

Para cambiar las frases, editá solo `lib/suggestedQuestions.ts` y sincronizá la tabla en `EVAL.md` § UI.

## Probar el chat (manual, gate 3e / 3f)

1. Levantá API + frontend (README raíz).
2. Abrí `http://localhost:3000` y hacé clic en cualquier pregunta sugerida (recomendado: la de **Q01**).
3. Verificá: texto en streaming, chips de páginas, estado **Completado**, y que queden 4 sugerencias debajo del historial.

Checklist detallado (B1–B11): [`../CHECKLIST_E2E.md`](../CHECKLIST_E2E.md).

## Archivos principales

| Archivo | Rol |
|---------|-----|
| `components/ChatShell.tsx` | Estado, `streamChat`, mensajes |
| `components/SuggestedQuestions.tsx` | Botones one-click; modo vacío / compacto |
| `lib/suggestedQuestions.ts` | Lista + `getRemainingSuggestedQuestions()` |
| `lib/streamChat.ts` | Cliente SSE |
| `components/SourceBadges.tsx` | Fuentes (páginas) |
| `components/MessageList.tsx` | Historial + preview + sugerencias pendientes |
| `lib/chat.ts` | Tipos `ChatStatus`, `ChatMessage` |

## Scripts

```powershell
npm run dev
npm run build
npm run lint
```
