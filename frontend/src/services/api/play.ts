import type {
  PlaySessionSchema,
  PlaySessionStartSchema,
} from "@/__generated__";
import api from "@/services/api";

export type PlaySession = PlaySessionSchema;

/** Report a sitting so every device shares the same "continue playing" list. */
async function startSession(igdbId: number) {
  const body: PlaySessionStartSchema = { igdb_id: igdbId };
  return api.post<PlaySession>("/play/sessions", body);
}

async function heartbeatSession(sessionId: number) {
  return api.post<PlaySession>(`/play/sessions/${sessionId}/heartbeat`);
}

async function stopSession(sessionId: number) {
  return api.post<PlaySession>(`/play/sessions/${sessionId}/stop`);
}

export default { startSession, heartbeatSession, stopSession };
