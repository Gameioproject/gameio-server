/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GameAssetKind } from './GameAssetKind';
export type ReconcileItem = {
    rom_id: number;
    kind: GameAssetKind;
    emulator?: string;
    channel?: string;
    slot?: number;
    has_local?: boolean;
    local_hash?: (string | null);
    base_hash?: (string | null);
    local_changed?: boolean;
};
