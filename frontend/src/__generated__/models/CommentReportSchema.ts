/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CommentAuthorSchema } from './CommentAuthorSchema';
export type CommentReportSchema = {
    id: number;
    comment_id: number;
    game_title: string;
    igdb_id: number;
    reporter: CommentAuthorSchema;
    author: (CommentAuthorSchema | null);
    reason: string;
    body_snapshot: string;
    status: 'pending' | 'dismissed' | 'removed';
    created_at: string;
    updated_at: string;
};
