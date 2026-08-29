/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GameSourceSchema } from './GameSourceSchema';
export type CatalogGameSchema = {
    id: number;
    igdb_id: number;
    name: string;
    slug: (string | null);
    summary: (string | null);
    release_year: (number | null);
    first_release_date: (number | null);
    url_cover: (string | null);
    url_cover_small: (string | null);
    url_screenshots: Array<string>;
    genres: Array<string>;
    platform_slugs: Array<string>;
    rating: (number | null);
    rating_count: number;
    youtube_video_id: (string | null);
    igdb_url: (string | null);
    owned: boolean;
    sources: Array<GameSourceSchema>;
    is_favorite: boolean;
    last_played_at: (string | null);
    play_time_seconds: number;
};

