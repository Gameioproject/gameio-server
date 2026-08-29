// useCatalogFilters — session-wide cache of the catalog facets (platforms,
// genres, totals). Several surfaces need the slug → name map or a per
// platform count at once, so one fetch is shared across all of them.
import { computed, ref } from "vue";
import catalogApi, { type CatalogFilters } from "@/services/api/catalog";

const filters = ref<CatalogFilters | null>(null);
let inflight: Promise<void> | null = null;

export function useCatalogFilters() {
  /** Resolves once the facets are cached; `force` refetches stale totals. */
  function load(force = false): Promise<void> {
    if (filters.value && !force) return Promise.resolve();
    if (!inflight) {
      inflight = catalogApi
        .getCatalogFilters()
        .then((res) => {
          filters.value = res.data;
        })
        .finally(() => {
          inflight = null;
        });
    }
    return inflight;
  }

  const platformNames = computed<Record<string, string>>(() =>
    Object.fromEntries(
      (filters.value?.platforms ?? []).map((p) => [p.slug, p.name]),
    ),
  );

  function platformGameCount(slug: string | null | undefined): number | null {
    if (!slug) return null;
    const hit = filters.value?.platforms.find((p) => p.slug === slug);
    return hit ? hit.game_count : null;
  }

  return { filters, platformNames, platformGameCount, load };
}
