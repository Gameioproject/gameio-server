/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CommentAuthorSchema } from './CommentAuthorSchema';
export type CommentSchema = {
    id: number;
    igdb_id: number;
    parent_id: (number | null);
    author: (CommentAuthorSchema | null);
    body: string;
    spoiler: boolean;
    created_at: string;
    updated_at: string;
    edited: boolean;
    deleted: boolean;
    like_count: number;
    reply_count: number;
    liked: boolean;
    can_edit: boolean;
    can_delete: boolean;
};
