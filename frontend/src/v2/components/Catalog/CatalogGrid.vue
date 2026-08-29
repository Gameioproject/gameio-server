<script setup lang="ts">
// CatalogGrid — offset-paged grid of catalog tiles for one query, with
// the game sheet wired in. The catalog page, the platform "All games"
// tab and any other surface that lists catalog games render this and
// only decide the query.
import { RBtn, RSkeletonBlock } from "@v2/lib";
import { useIntersectionObserver } from "@vueuse/core";
import axios from "axios";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import catalogApi, {
  type CatalogGame,
  type CatalogQuery,
} from "@/services/api/catalog";
import CatalogCard from "@/v2/components/Catalog/CatalogCard.vue";
import CatalogGameDialog from "@/v2/components/Catalog/CatalogGameDialog.vue";
import EmptyState from "@/v2/components/shared/EmptyState.vue";
import { useCatalogFilters } from "@/v2/composables/useCatalogFilters";
import { useIsAlive } from "@/v2/composables/useIsAlive";
import { useSnackbar } from "@/v2/composables/useSnackbar";
import { useWrapGridNav } from "@/v2/composables/useWrapGridNav";

const PAGE_SIZE = 36;
const SKELETON_COUNT = 18;
const RELOAD_DEBOUNCE_MS = 250;
// Fetch the next page this far before the sentinel scrolls into view.
const PREFETCH_MARGIN = "800px";

const props = withDefaults(
  defineProps<{
    query: CatalogQuery;
    emptyMessage?: string;
    emptyIcon?: string;
    /** The collection this grid lists, so the sheet can remove games from it. */
    collectionId?: number;
  }>(),
  {
    emptyMessage: undefined,
    emptyIcon: "mdi-magnify-close",
    collectionId: undefined,
  },
);

const emit = defineEmits<{
  (e: "update:total", value: number): void;
}>();

const { t } = useI18n();
const snackbar = useSnackbar();
const alive = useIsAlive();
const { filters, platformNames, load: loadFilters } = useCatalogFilters();

const games = ref<CatalogGame[]>([]);
const total = ref(0);
const loading = ref(true);
const loadingMore = ref(false);

const hasMore = computed(() => games.value.length < total.value);
const catalogEmpty = computed(
  () => !!filters.value && filters.value.total_games === 0,
);

let controller: AbortController | null = null;
let reloadTimer: ReturnType<typeof setTimeout> | null = null;

function scheduleReload() {
  if (reloadTimer) clearTimeout(reloadTimer);
  reloadTimer = setTimeout(() => void reload(), RELOAD_DEBOUNCE_MS);
}

async function reload() {
  controller?.abort();
  controller = new AbortController();
  const { signal } = controller;
  loading.value = true;
  try {
    const res = await catalogApi.getCatalogGames({
      ...props.query,
      limit: PAGE_SIZE,
      offset: 0,
      signal,
    });
    if (!alive.value || signal.aborted) return;
    games.value = res.data.items;
    total.value = res.data.total;
    emit("update:total", total.value);
  } catch (error) {
    if (axios.isCancel(error) || !alive.value) return;
    snackbar.error(t("catalog.load-failed"));
  } finally {
    if (alive.value && !signal.aborted) loading.value = false;
  }
}

async function loadMore() {
  if (loading.value || loadingMore.value || !hasMore.value) return;
  loadingMore.value = true;
  const offset = games.value.length;
  try {
    const res = await catalogApi.getCatalogGames({
      ...props.query,
      limit: PAGE_SIZE,
      offset,
    });
    // A query change while this page was in flight already replaced the
    // list; appending would mix two result sets.
    if (!alive.value || games.value.length !== offset) return;
    games.value.push(...res.data.items);
    total.value = res.data.total;
    emit("update:total", total.value);
  } catch (error) {
    if (axios.isCancel(error) || !alive.value) return;
    snackbar.error(t("catalog.load-failed"));
  } finally {
    if (alive.value) loadingMore.value = false;
  }
}

watch(() => props.query, scheduleReload, { deep: true });

onMounted(() => {
  loadFilters().catch(() => {
    // Facets only feed the empty-state copy and the sheet's platform
    // names; the grid itself does not need them.
  });
  void reload();
});

onBeforeUnmount(() => {
  if (reloadTimer) clearTimeout(reloadTimer);
  controller?.abort();
});

const gridRoot = ref<HTMLElement | null>(null);
useWrapGridNav(gridRoot, { cellSelector: ".cat-card" });

// The grid lives inside a shell-owned scroller, so the observer must root
// there: against the viewport the sentinel is clipped away by the scroller
// and the prefetch margin would never apply.
function nearestScrollParent(el: HTMLElement | null): HTMLElement | null {
  for (let node = el?.parentElement; node; node = node.parentElement) {
    const { overflowY } = getComputedStyle(node);
    if (overflowY === "auto" || overflowY === "scroll") return node;
  }
  return null;
}

const scrollRoot = ref<HTMLElement | null>(null);
onMounted(() => {
  scrollRoot.value = nearestScrollParent(gridRoot.value);
});

const moreSentinel = ref<HTMLElement | null>(null);
useIntersectionObserver(
  moreSentinel,
  ([entry]) => {
    if (entry?.isIntersecting) void loadMore();
  },
  { root: scrollRoot, rootMargin: PREFETCH_MARGIN },
);

const selected = ref<CatalogGame | null>(null);
const dialogOpen = ref(false);

function openGame(game: CatalogGame) {
  selected.value = game;
  dialogOpen.value = true;
}

function replaceGame(game: CatalogGame) {
  const index = games.value.findIndex((g) => g.igdb_id === game.igdb_id);
  if (index !== -1) games.value[index] = game;
  if (selected.value?.igdb_id === game.igdb_id) selected.value = game;
}

function dropGame(igdbId: number) {
  const index = games.value.findIndex((g) => g.igdb_id === igdbId);
  if (index === -1) return;
  games.value.splice(index, 1);
  total.value = Math.max(0, total.value - 1);
  emit("update:total", total.value);
}
</script>

<template>
  <div ref="gridRoot" class="cat-grid">
    <div v-if="loading" class="cat-grid__cells">
      <RSkeletonBlock
        v-for="n in SKELETON_COUNT"
        :key="`sk-${n}`"
        width="calc(var(--r-card-art-h) * 0.75)"
        height="var(--r-card-art-h)"
        rounded="card"
      />
    </div>

    <EmptyState
      v-else-if="!total && catalogEmpty"
      icon="mdi-compass-off-outline"
      :message="t('catalog.empty')"
    />

    <EmptyState
      v-else-if="!total"
      :icon="emptyIcon"
      :message="emptyMessage ?? t('catalog.no-results')"
    />

    <template v-else>
      <div class="cat-grid__cells">
        <CatalogCard
          v-for="game in games"
          :key="game.igdb_id"
          :game="game"
          @select="openGame(game)"
        />
      </div>
      <div ref="moreSentinel" class="cat-grid__more">
        <RBtn
          v-if="hasMore"
          variant="outlined"
          :loading="loadingMore"
          @click="loadMore"
        >
          {{ t("gallery.load-more") }}
        </RBtn>
        <span v-else class="cat-grid__all-loaded">
          {{ t("gallery.all-loaded") }}
        </span>
      </div>
    </template>

    <CatalogGameDialog
      v-model="dialogOpen"
      :game="selected"
      :platform-names="platformNames"
      :collection-id="collectionId"
      @update:game="replaceGame"
      @removed-from-collection="dropGame"
    />
  </div>
</template>

<style scoped>
.cat-grid__cells {
  display: flex;
  flex-wrap: wrap;
  gap: var(--r-space-5) var(--r-space-4);
}

html[data-bp~="xs"] .cat-grid__cells {
  justify-content: center;
}

.cat-grid__more {
  display: flex;
  justify-content: center;
  padding: var(--r-space-6) 0;
}

.cat-grid__all-loaded {
  font-size: 13px;
  color: var(--r-color-fg-faint);
}
</style>
