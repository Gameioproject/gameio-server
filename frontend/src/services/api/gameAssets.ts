import type { GameAssetKind, GameAssetSchema } from "@/__generated__";
import api from "@/services/api";

export type GameAsset = GameAssetSchema;

async function listAssets({
  igdbId,
  kind,
  emulator,
}: {
  igdbId: number;
  kind?: GameAssetKind;
  emulator?: string;
}) {
  return api.get<GameAsset[]>(`/catalog/${igdbId}/assets`, {
    params: { kind, emulator },
  });
}

/** Store or replace the user's save/state for one game and core. */
async function uploadAsset({
  igdbId,
  kind,
  data,
  emulator,
  fileName,
  screenshot,
}: {
  igdbId: number;
  kind: GameAssetKind;
  data: ArrayBuffer | Uint8Array;
  emulator: string;
  fileName: string;
  screenshot?: ArrayBuffer | null;
}) {
  const bytes: ArrayBuffer =
    data instanceof ArrayBuffer ? data : data.slice().buffer;
  const form = new FormData();
  form.append("kind", kind);
  form.append("emulator", emulator);
  form.append("file_name", fileName);
  form.append("file", new Blob([bytes]), fileName);
  if (screenshot) {
    form.append(
      "screenshot",
      new Blob([screenshot], { type: "image/png" }),
      "screenshot.png",
    );
  }
  return api.post<GameAsset>(`/catalog/${igdbId}/assets`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

async function getAssetContent(assetId: number): Promise<Uint8Array> {
  const res = await api.get<ArrayBuffer>(`/assets/${assetId}/content`, {
    responseType: "arraybuffer",
  });
  return new Uint8Array(res.data);
}

function getAssetScreenshotUrl(assetId: number): string {
  return `/api/assets/${assetId}/screenshot`;
}

async function deleteAsset(assetId: number) {
  return api.delete(`/assets/${assetId}`);
}

export default {
  listAssets,
  uploadAsset,
  getAssetContent,
  getAssetScreenshotUrl,
  deleteAsset,
};
