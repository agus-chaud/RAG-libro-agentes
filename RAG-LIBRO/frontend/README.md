# Frontend RAG-LIBRO

Interfaz del chat sobre el libro. Stack: **Next.js 14**, App Router, Tailwind.

## Arranque rápido

```powershell
copy .env.example .env.local
npm install
npm run dev
```

Abrí [http://localhost:3000](http://localhost:3000).

En `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Esa URL aparece en el header del chat (componente `ApiUrlBadge`). Todavía no se usa para enviar mensajes — eso viene en la fase **3c**.

## Fases completadas

### 3a — Base del proyecto

- Proyecto creado con `create-next-app` (TypeScript, Tailwind, App Router).
- Configuración de la URL del backend con `NEXT_PUBLIC_API_URL`.
- Helper `lib/api.ts` y badge en pantalla para confirmar que la variable llega al navegador.

**Gate:** `npm run dev` levanta la app en el puerto 3000.

### 3b — Pantalla de chat (UI)

Pantalla completa de conversación, **sin llamar al backend todavía**:

- **Lista de mensajes** — tus preguntas a la derecha, respuestas del asistente a la izquierda.
- **Entrada** — textarea + botón **Enviar** (Enter envía, Shift+Enter nueva línea).
- **Estados visibles** — pill en el header: Listo → Generando… → Completado (o Error).

Mientras está en *Generando…*, el input y el botón quedan deshabilitados. La respuesta del asistente se **simula** palabra por palabra (`ChatShell.tsx`); en **3c** eso se reemplaza por el stream SSE de `/chat/stream`.

| Estado | Cuándo |
|--------|--------|
| Listo (`idle`) | Al cargar la página |
| Generando… (`streaming`) | Después de enviar un mensaje |
| Completado (`done`) | Cuando termina la respuesta simulada |
| Error (`error`) | Si enviás el texto `__mock_error__` (solo para probar la UI) |

## Archivos principales

| Archivo | Rol |
|---------|-----|
| `app/page.tsx` | Página principal → `ChatShell` |
| `components/ChatShell.tsx` | Estado del chat y envío (mock hasta 3c) |
| `components/MessageList.tsx` | Historial de burbujas |
| `components/ChatInput.tsx` | Formulario de mensaje |
| `components/ChatStatusBar.tsx` | Indicador de estado |
| `lib/chat.ts` | Tipos y reglas (`canSendMessage`, etc.) |
| `lib/api.ts` | `getApiUrl()` |

## Scripts

```powershell
npm run dev      # desarrollo
npm run build    # build de producción
npm run lint     # ESLint
```

## Siguiente fase (3c)

Instalar `@microsoft/fetch-event-source`, hacer `POST` a `{API_URL}/chat/stream` y manejar eventos `sources`, `token` y `done` para mostrar la respuesta real del backend.
