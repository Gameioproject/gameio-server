import { storeToRefs } from "pinia";
import { watch } from "vue";
import {
  createRouter,
  createWebHistory,
  type RouteLocationNormalized,
  type RouteRecordRaw,
} from "vue-router";
import i18n, { loadLocale } from "@/locales";
import { startViewTransition } from "@/plugins/transition";
import storeAuth from "@/stores/auth";
import storeHeartbeat from "@/stores/heartbeat";
import type { User } from "@/stores/users";
import {
  fallbackComponent,
  v2Layouts,
  v2RouteComponents,
} from "@/v2/router/routes";

export const ROUTES = {
  SETUP: "setup",
  LOGIN: "login",
  RESET_PASSWORD: "reset-password",
  FORGOT_PASSWORD: "forgot-password",
  REGISTER: "register",
  HOME: "home",
  LIBRARY: "library",
  CATALOG: "catalog",
  CATALOG_PLAY: "catalog-play",
  PLATFORMS_INDEX: "platforms-index",
  COLLECTIONS_INDEX: "collections-index",
  COLLECTION: "collection",
  USER_PROFILE: "user-profile",
  USER_INTERFACE: "user-interface",
  DOWNLOAD_HOSTS: "download-hosts",
  CLIENT_API_TOKENS: "client-api-tokens",
  ADMINISTRATION: "administration",
  LOGS: "logs",
  CONTROLLER_DEBUG: "controller-debug",
  PAIR: "pair",
  PAIR_DEVICE: "pair-device",
  NOT_FOUND: "404",
} as const;

function v2For(routeName: string) {
  return v2RouteComponents[routeName] ?? fallbackComponent;
}

// Every view renders through the `v2` named view: the layouts mount
// `<router-view name="v2" />`, so routes only declare that component.
function view(routeName: string) {
  return { v2: v2For(routeName) };
}

function authRoute(
  path: string,
  name: string,
  title: string,
  layout: keyof typeof v2Layouts = "auth",
): RouteRecordRaw {
  return {
    path,
    components: { v2: v2Layouts[layout] },
    children: [{ path: "", name, meta: { title }, components: view(name) }],
  };
}

const routes: RouteRecordRaw[] = [
  authRoute("/setup", ROUTES.SETUP, "login.setup-wizard"),
  authRoute("/login", ROUTES.LOGIN, "login.login"),
  authRoute(
    "/reset-password",
    ROUTES.RESET_PASSWORD,
    "login.reset-password",
    "gameioAuth",
  ),
  authRoute(
    "/forgot-password",
    ROUTES.FORGOT_PASSWORD,
    "login.forgot-password",
    "gameioAuth",
  ),
  authRoute("/register", ROUTES.REGISTER, "login.register"),
  {
    path: "/",
    components: { v2: v2Layouts.main },
    children: [
      {
        path: "",
        name: ROUTES.HOME,
        meta: { title: "settings.home" },
        components: view(ROUTES.HOME),
      },
      {
        // Games downloaded into this browser.
        path: "library",
        name: ROUTES.LIBRARY,
        meta: { title: "common.library" },
        components: view(ROUTES.LIBRARY),
      },
      {
        // The whole catalog, downloaded or not.
        path: "catalog",
        name: ROUTES.CATALOG,
        meta: { title: "catalog.title" },
        components: view(ROUTES.CATALOG),
      },
      {
        path: "game/:igdb/play",
        name: ROUTES.CATALOG_PLAY,
        components: view(ROUTES.CATALOG_PLAY),
      },
      {
        path: "platforms",
        name: ROUTES.PLATFORMS_INDEX,
        meta: { title: "common.platforms" },
        components: view(ROUTES.PLATFORMS_INDEX),
      },
      {
        path: "collections",
        name: ROUTES.COLLECTIONS_INDEX,
        meta: { title: "common.collections" },
        components: view(ROUTES.COLLECTIONS_INDEX),
      },
      {
        path: "collection/:collection",
        name: ROUTES.COLLECTION,
        components: view(ROUTES.COLLECTION),
      },
      {
        // Settings group: sidebar + content panel shared by every child.
        path: "",
        components: { v2: v2Layouts.settings },
        children: [
          {
            path: "user/:user",
            name: ROUTES.USER_PROFILE,
            meta: { bare: true },
            components: view(ROUTES.USER_PROFILE),
          },
          {
            path: "user-interface",
            name: ROUTES.USER_INTERFACE,
            meta: { title: "common.user-interface", bare: true },
            components: view(ROUTES.USER_INTERFACE),
          },
          {
            path: "download-hosts",
            name: ROUTES.DOWNLOAD_HOSTS,
            meta: { title: "catalog.hosts-title", bare: true },
            components: view(ROUTES.DOWNLOAD_HOSTS),
          },
          {
            path: "client-api-tokens",
            name: ROUTES.CLIENT_API_TOKENS,
            meta: { title: "settings.client-api-tokens", bare: true },
            components: view(ROUTES.CLIENT_API_TOKENS),
          },
          {
            path: "administration",
            name: ROUTES.ADMINISTRATION,
            meta: { title: "common.administration", bare: true },
            components: view(ROUTES.ADMINISTRATION),
          },
          {
            path: "logs",
            name: ROUTES.LOGS,
            meta: { title: "common.logs", bare: true },
            components: view(ROUTES.LOGS),
          },
          {
            path: "controller-debug",
            name: ROUTES.CONTROLLER_DEBUG,
            meta: { title: "settings.controller-debug", bare: true },
            components: view(ROUTES.CONTROLLER_DEBUG),
          },
        ],
      },
      {
        path: ":pathMatch(.*)*",
        name: ROUTES.NOT_FOUND,
        components: view(ROUTES.NOT_FOUND),
      },
    ],
  },
  {
    path: "/pair/device",
    name: ROUTES.PAIR_DEVICE,
    components: { v2: () => import("@/v2/views/DevicePairShell.vue") },
  },
  {
    path: "/pair",
    name: ROUTES.PAIR,
    components: { v2: () => import("@/v2/views/PairDispatcher.vue") },
  },
];

interface RoutePermissions {
  path: string;
  requiredScopes: string[];
}

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition;
    // Same path: only query/hash changed (filters, tabs); keep the offset.
    if (to.path === from.path) return false;
    return { left: 0, top: 0 };
  },
});

const routePermissions: RoutePermissions[] = [
  { path: ROUTES.CLIENT_API_TOKENS, requiredScopes: ["me.write"] },
  { path: ROUTES.DOWNLOAD_HOSTS, requiredScopes: ["roms.write"] },
  { path: ROUTES.ADMINISTRATION, requiredScopes: ["users.write"] },
  { path: ROUTES.LOGS, requiredScopes: ["logs.read"] },
];

const authExemptRoutes = [
  ROUTES.LOGIN,
  ROUTES.SETUP,
  ROUTES.RESET_PASSWORD,
  ROUTES.FORGOT_PASSWORD,
  ROUTES.REGISTER,
  ROUTES.PAIR,
] as const;

type AuthExemptRoute = (typeof authExemptRoutes)[number];

export function isAuthExemptRoute(route: string): route is AuthExemptRoute {
  return (authExemptRoutes as readonly string[]).includes(route);
}

function checkRoutePermissions(route: string, user: User | null): boolean {
  if (isAuthExemptRoute(route)) return true;
  if (!user) return false;
  const routeConfig = routePermissions.find((config) => config.path === route);
  if (!routeConfig) return true;
  return routeConfig.requiredScopes.every((scope) =>
    user.oauth_scopes.includes(scope),
  );
}

function applyRouteTitle(route: RouteLocationNormalized) {
  document.title = route.meta.title
    ? i18n.global.t(route.meta.title as string)
    : "RomM";
}

router.beforeEach(async (to, _from, next) => {
  const heartbeat = storeHeartbeat();
  const auth = storeAuth();
  const { user } = storeToRefs(auth);
  const currentRoute = to.name?.toString();

  try {
    if (!heartbeat.connected) {
      applyRouteTitle(to);
      return next();
    }

    if (heartbeat.value.SYSTEM.SHOW_SETUP_WIZARD) {
      return currentRoute !== "setup" ? next({ name: ROUTES.SETUP }) : next();
    }

    if (!user.value && (!currentRoute || !isAuthExemptRoute(currentRoute))) {
      return next({
        name: ROUTES.LOGIN,
        query: { next: to.query.next ?? to.fullPath },
      });
    }

    if (currentRoute === ROUTES.SETUP) {
      return next({ name: user.value ? ROUTES.HOME : ROUTES.LOGIN });
    }

    if (currentRoute && !checkRoutePermissions(currentRoute, user.value)) {
      return next({ name: ROUTES.NOT_FOUND });
    }

    if (
      currentRoute === ROUTES.LOGS &&
      heartbeat.value.FRONTEND.DISABLE_LOGS_VIEWER
    ) {
      return next({ name: ROUTES.NOT_FOUND });
    }

    applyRouteTitle(to);
    next();
  } catch (error) {
    console.error("Navigation guard error:", error);
    document.title = "RomM";
    next({ name: ROUTES.LOGIN });
  }
});

watch(i18n.global.locale, async (locale) => {
  await loadLocale(locale);
  const route = router.currentRoute.value;
  if (route.meta.title) applyRouteTitle(route);
});

router.beforeResolve(async (to, from) => {
  if (to.path === from.path) return;
  const viewTransition = startViewTransition();
  await viewTransition.captured;
});

export default router;
