import type { CollectionSchema } from "@/__generated__";
import api from "@/services/api";

export type Collection = CollectionSchema;

export interface CollectionInput {
  name: string;
  description?: string;
  is_public?: boolean;
  url_cover?: string;
  artwork?: File | null;
}

function toFormData(input: Partial<CollectionInput>): FormData {
  const form = new FormData();
  if (input.name !== undefined) form.append("name", input.name);
  if (input.description !== undefined)
    form.append("description", input.description);
  if (input.url_cover !== undefined) form.append("url_cover", input.url_cover);
  if (input.artwork) form.append("artwork", input.artwork);
  return form;
}

async function getCollections() {
  return api.get<Collection[]>("/collections");
}

async function getCollection(id: number) {
  return api.get<Collection>(`/collections/${id}`);
}

async function createCollection(input: CollectionInput) {
  const { data } = await api.post<Collection>(
    "/collections",
    toFormData(input),
    {
      headers: { "Content-Type": "multipart/form-data" },
      params: { is_public: input.is_public ?? false },
    },
  );
  return data;
}

async function updateCollection({
  id,
  removeCover = false,
  ...input
}: Partial<CollectionInput> & { id: number; removeCover?: boolean }) {
  return api.put<Collection>(`/collections/${id}`, toFormData(input), {
    headers: { "Content-Type": "multipart/form-data" },
    params: { is_public: input.is_public, remove_cover: removeCover },
  });
}

async function deleteCollection({ id }: { id: number }) {
  return api.delete(`/collections/${id}`);
}

async function addGamesToCollection(collectionId: number, igdbIds: number[]) {
  return api.post<Collection>(`/collections/${collectionId}/games`, {
    igdb_ids: igdbIds,
  });
}

async function removeGamesFromCollection(
  collectionId: number,
  igdbIds: number[],
) {
  return api.delete<Collection>(`/collections/${collectionId}/games`, {
    data: { igdb_ids: igdbIds },
  });
}

/** Toggle catalog games in the user's favorites (created on first use). */
async function setFavoriteGames(igdbIds: number[], favorite: boolean) {
  return favorite
    ? api.post<Collection>("/collections/favorites/games", {
        igdb_ids: igdbIds,
      })
    : api.delete<Collection>("/collections/favorites/games", {
        data: { igdb_ids: igdbIds },
      });
}

export default {
  getCollections,
  getCollection,
  createCollection,
  updateCollection,
  deleteCollection,
  addGamesToCollection,
  removeGamesFromCollection,
  setFavoriteGames,
};
