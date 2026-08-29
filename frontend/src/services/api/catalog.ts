import type {
  CatalogFiltersSchema,
  CatalogGameSchema,
  CatalogOrderBy,
  CatalogOrderDir,
  CatalogPageSchema,
  GameSourceSchema,
} from "@/__generated__";
import api from "@/services/api";

export type CatalogGame = CatalogGameSchema;
export type CatalogFilters = CatalogFiltersSchema;
export type CatalogPage = CatalogPageSchema;

export interface GetCatalogGamesParams {
  search?: string;
  platformSlug?: string;
  excludePlatforms?: string[];
  genre?: string;
  minRating?: number;
  yearFrom?: number;
  yearTo?: number;
  owned?: boolean;
  ownedPlatforms?: boolean;
  collectionId?: number;
  favorite?: boolean;
  played?: boolean;
  orderBy?: CatalogOrderBy;
  orderDir?: CatalogOrderDir;
  limit?: number;
  offset?: number;
  signal?: AbortSignal;
}

/** The filter half of a catalog request; paging and cancellation are the caller's. */
export type CatalogQuery = Omit<
  GetCatalogGamesParams,
  "limit" | "offset" | "signal"
>;

async function getCatalogGames({
  search,
  platformSlug,
  excludePlatforms,
  genre,
  minRating,
  yearFrom,
  yearTo,
  owned,
  ownedPlatforms,
  collectionId,
  favorite,
  played,
  orderBy,
  orderDir,
  limit,
  offset,
  signal,
}: GetCatalogGamesParams) {
  const params = {
    search: search || undefined,
    platform_slug: platformSlug || undefined,
    exclude_platform: excludePlatforms?.length ? excludePlatforms : undefined,
    genre: genre || undefined,
    min_rating: minRating,
    year_from: yearFrom,
    year_to: yearTo,
    owned,
    owned_platforms: ownedPlatforms || undefined,
    collection_id: collectionId,
    favorite: favorite || undefined,
    played: played || undefined,
    order_by: orderBy,
    order_dir: orderDir,
    limit,
    offset,
  };
  return api.get<CatalogPage>("/catalog", {
    params,
    signal,
    // FastAPI reads repeated keys, not the `key[]` form axios defaults to.
    paramsSerializer: { indexes: null },
  });
}

async function getCatalogFilters() {
  return api.get<CatalogFilters>("/catalog/filters");
}

async function getCatalogGame({ igdbId }: { igdbId: number }) {
  return api.get<CatalogGame>(`/catalog/${igdbId}`);
}

async function addCatalogGameSource({
  igdbId,
  url,
  platformSlug,
}: {
  igdbId: number;
  url: string;
  platformSlug?: string;
}) {
  return api.post<GameSourceSchema>(`/catalog/${igdbId}/sources`, {
    url,
    platform_slug: platformSlug,
  });
}

async function deleteCatalogGameSource({ sourceId }: { sourceId: number }) {
  return api.delete(`/catalog/sources/${sourceId}`);
}

/** The server answers with a redirect to the file's host. */
function getCatalogDownloadUrl({
  igdbId,
  sourceId,
}: {
  igdbId: number;
  sourceId?: number;
}) {
  const query = sourceId ? `?source_id=${sourceId}` : "";
  return `/api/catalog/${igdbId}/download${query}`;
}

/** Same file relayed through the server, for in-browser play (hosts rarely allow CORS). */
function getCatalogStreamUrl({
  igdbId,
  sourceId,
}: {
  igdbId: number;
  sourceId?: number;
}) {
  const query = sourceId ? `?source_id=${sourceId}` : "";
  return `/api/catalog/${igdbId}/stream${query}`;
}

export default {
  getCatalogGames,
  getCatalogFilters,
  getCatalogGame,
  getCatalogDownloadUrl,
  getCatalogStreamUrl,
  addCatalogGameSource,
  deleteCatalogGameSource,
};
