/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GameAssetKind } from './GameAssetKind';
export type Body_upload_game_asset_api_catalog__igdb_id__assets_post = {
    kind: GameAssetKind;
    /**
     * The save file or state
     */
    file: string;
    emulator?: string;
    file_name?: (string | null);
    /**
     * Optional thumbnail
     */
    screenshot?: (string | null);
};

