/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GameHostKind } from './GameHostKind';
export type GameHostCreateSchema = {
    name: string;
    kind: GameHostKind;
    base: string;
    platform_slug?: (string | null);
    enabled?: boolean;
};

