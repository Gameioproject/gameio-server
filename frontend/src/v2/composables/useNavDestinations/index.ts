// useNavDestinations — single source of truth for the four primary
// content destinations (Home / Library / Platforms / Discover) and the
// route-path → active-tab derivation. Shared by `AppNav` (desktop top
// pill) and `BottomNav` (mobile bottom bar) so the two never drift in
// labels, icons, ordering, or active-state logic.
//
// Highlighting is derived from `route.path` (not route names) so gallery
// subroutes — e.g. `/rom/:id` reached from a platform — still light up
// their parent destination.
import { computed } from "vue";
import type { ComputedRef } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

export type NavDestinationId =
  "home" | "library" | "platforms" | "collections" | "catalog";

export interface NavDestination {
  id: NavDestinationId;
  label: string;
  // Mirrors `label` so the icon-only variants (xs top pill, bottom bar)
  // still name each link to screen readers / focus rings.
  ariaLabel: string;
  icon: string;
  to: string;
}

export function useNavDestinations(): {
  destinations: ComputedRef<NavDestination[]>;
  activeId: ComputedRef<NavDestinationId | null>;
} {
  const { t } = useI18n();
  const route = useRoute();

  const destinations = computed<NavDestination[]>(() => [
    {
      id: "home",
      label: t("common.home"),
      ariaLabel: t("common.home"),
      icon: "mdi-home-outline",
      to: "/",
    },
    {
      id: "library",
      label: t("common.library"),
      ariaLabel: t("common.library"),
      icon: "mdi-bookshelf",
      to: "/library",
    },
    {
      id: "platforms",
      label: t("common.platforms"),
      ariaLabel: t("common.platforms"),
      icon: "mdi-controller",
      to: "/platforms",
    },
    {
      id: "catalog",
      label: t("catalog.title"),
      ariaLabel: t("catalog.title"),
      icon: "mdi-compass-outline",
      to: "/catalog",
    },
  ]);

  const activeId = computed<NavDestinationId | null>(() => {
    const path = route.path;
    if (path === "/") return "home";
    if (path.startsWith("/library")) return "library";
    if (path.startsWith("/platform")) return "platforms";
    if (path.startsWith("/catalog") || path.startsWith("/game/"))
      return "catalog";
    return null;
  });

  return { destinations, activeId };
}
