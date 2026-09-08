/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GameHostKind } from './GameHostKind';
export type GameHostSchema = {
    id: number;
    name: string;
    kind: GameHostKind;
    base: string;
    info_hash?: (string | null);
    platform_slug: (string | null);
    enabled: boolean;
    source_count: number;
    indexing: boolean;
    last_indexed_at: (string | null);
    last_index_stats: (Record<string, any> | null);
};

