import type { Component } from "vue";

export type V2Route = () => Promise<Component>;

export const v2RouteComponents: Partial<Record<string, V2Route>> = {
  home: () => import("@/v2/views/Home.vue"),
  login: () => import("@/v2/views/Auth/Login.vue"),
  "reset-password": () => import("@/v2/views/Auth/ResetPassword.vue"),
  "forgot-password": () => import("@/v2/views/Auth/ForgotPassword.vue"),
  register: () => import("@/v2/views/Auth/Register.vue"),
  setup: () => import("@/v2/views/Auth/Setup.vue"),
  library: () => import("@/v2/views/Library.vue"),
  catalog: () => import("@/v2/views/CatalogIndex.vue"),
  "catalog-play": () => import("@/v2/views/CatalogPlay.vue"),
  "platforms-index": () => import("@/v2/views/CatalogPlatforms.vue"),
  "collections-index": () => import("@/v2/views/CollectionsIndex.vue"),
  collection: () => import("@/v2/views/Collection.vue"),
  "user-profile": () => import("@/v2/views/Settings/UserProfile.vue"),
  "user-interface": () => import("@/v2/views/Settings/UserInterface.vue"),
  "download-hosts": () => import("@/v2/views/Settings/DownloadHosts.vue"),
  "client-api-tokens": () => import("@/v2/views/Settings/ClientApiTokens.vue"),
  administration: () => import("@/v2/views/Settings/Administration.vue"),
  logs: () => import("@/v2/views/Settings/Logs.vue"),
  "controller-debug": () => import("@/v2/views/ControllerDebug.vue"),
  "404": () => import("@/v2/views/NotReady.vue"),
};

export const fallbackComponent: V2Route = () =>
  import("@/v2/views/NotReady.vue");

export const v2Layouts = {
  main: () => import("@/v2/layouts/AppLayout.vue"),
  auth: () => import("@/v2/layouts/AuthLayout.vue"),
  // Sub-layout mounted inside AppLayout via a grouping parent route; owns
  // the settings sidebar and renders the active child via `<router-view name="v2" />`.
  settings: () => import("@/v2/layouts/SettingsLayout.vue"),
};
