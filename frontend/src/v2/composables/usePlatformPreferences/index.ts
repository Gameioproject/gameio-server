// usePlatformPreferences: the user's platform order and hidden platforms,
// stored as comma-separated slugs in the synced UI settings.
import { computed } from "vue";
import { useUISettings } from "@/composables/useUISettings";

function parse(value: string): string[] {
  return value.split(",").filter(Boolean);
}

export function usePlatformPreferences() {
  const { platformOrder, hiddenPlatforms } = useUISettings();

  const order = computed(() => parse(platformOrder.value));
  const hidden = computed(() => new Set(parse(hiddenPlatforms.value)));

  function isHidden(slug: string): boolean {
    return hidden.value.has(slug);
  }

  /** Stable sort: ordered slugs first (in order), then the rest as given. */
  function sortPlatforms<T extends { slug: string }>(platforms: T[]): T[] {
    const rank = new Map(order.value.map((slug, i) => [slug, i]));
    return [...platforms].sort((a, b) => {
      const ra = rank.get(a.slug) ?? Number.MAX_SAFE_INTEGER;
      const rb = rank.get(b.slug) ?? Number.MAX_SAFE_INTEGER;
      return ra - rb;
    });
  }

  function visiblePlatforms<T extends { slug: string }>(platforms: T[]): T[] {
    return sortPlatforms(platforms).filter((p) => !isHidden(p.slug));
  }

  /** Persist a full order (slugs not listed keep their catalog order after it). */
  function setOrder(slugs: string[]) {
    platformOrder.value = slugs.join(",");
  }

  function move(slugs: string[], slug: string, delta: -1 | 1) {
    const index = slugs.indexOf(slug);
    const target = index + delta;
    if (index === -1 || target < 0 || target >= slugs.length) return;
    const next = [...slugs];
    [next[index], next[target]] = [next[target], next[index]];
    setOrder(next);
  }

  function setHidden(slug: string, value: boolean) {
    const next = new Set(hidden.value);
    if (value) next.add(slug);
    else next.delete(slug);
    hiddenPlatforms.value = [...next].join(",");
  }

  return {
    order,
    hidden,
    isHidden,
    sortPlatforms,
    visiblePlatforms,
    setOrder,
    move,
    setHidden,
  };
}
