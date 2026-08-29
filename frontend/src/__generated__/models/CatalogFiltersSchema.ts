/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CatalogGenreSchema } from './CatalogGenreSchema';
import type { CatalogPlatformSchema } from './CatalogPlatformSchema';
export type CatalogFiltersSchema = {
    total_games: number;
    owned_games: number;
    platforms: Array<CatalogPlatformSchema>;
    genres: Array<CatalogGenreSchema>;
};

