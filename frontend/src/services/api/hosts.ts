import type {
  GameHostCreateSchema,
  GameHostIndexSchema,
  GameHostSchema,
  GameHostUpdateSchema,
} from "@/__generated__";
import api from "@/services/api";

export type GameHost = GameHostSchema;
export type GameHostCreate = GameHostCreateSchema;
export type GameHostUpdate = GameHostUpdateSchema;

async function getHosts() {
  return api.get<GameHost[]>("/hosts");
}

async function createHost(body: GameHostCreate) {
  return api.post<GameHost>("/hosts", body);
}

async function updateHost({ id, ...body }: GameHostUpdate & { id: number }) {
  return api.patch<GameHost>(`/hosts/${id}`, body);
}

async function deleteHost({ id }: { id: number }) {
  return api.delete(`/hosts/${id}`);
}

async function indexHost({ id }: { id: number }) {
  return api.post<GameHostIndexSchema>(`/hosts/${id}/index`);
}

export default { getHosts, createHost, updateHost, deleteHost, indexHost };
