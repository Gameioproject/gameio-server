/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CollectionSchema = {
    id: number;
    name: string;
    description: string;
    game_igdb_ids?: Array<number>;
    game_count?: number;
    url_covers?: Array<string>;
    url_cover: (string | null);
    path_cover_small: (string | null);
    path_cover_large: (string | null);
    is_public?: boolean;
    is_favorite?: boolean;
    user_id: number;
    owner_username: string;
    created_at: string;
    updated_at: string;
};

