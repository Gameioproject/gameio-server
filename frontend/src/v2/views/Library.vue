<script setup lang="ts">
// Library: the games stored on this device, one section per system in the
// user's platform order. Only the sheet talks to the server.
import { RBtn, RSkeletonBlock, RTextField } from "@v2/lib";
import { storeToRefs } from "pinia";
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { ROUTES } from "@/plugins/router";
import catalogApi, { type CatalogGame } from "@/services/api/catalog";
import storeDeviceLibrary, { type DeviceGame } from "@/stores/deviceLibrary";
import { formatBytes } from "@/utils";
import CatalogCard from "@/v2/components/Catalog/CatalogCard.vue";
import CatalogGameDialog from "@/v2/components/Catalog/CatalogGameDialog.vue";
import CachedPlatformIcon from "@/v2/components/shared/CachedPlatformIcon.vue";
import EmptyState from "@/v2/components/shared/EmptyState.vue";
import IndexShell from "@/v2/components/shared/IndexShell.vue";
import PageHeader from "@/v2/components/shared/PageHeader.vue";
import { useCatalogFilters } from "@/v2/composables/useCatalogFilters";
import { useIsAlive } from "@/v2/composables/useIsAlive";
import { usePageTitle } from "@/v2/composables/usePageTitle";
import { usePlatformPreferences } from "@/v2/composables/usePlatformPreferences";
import { useSnackbar } from "@/v2/composables/useSnackbar";
import { useWrapGridNav } from "@/v2/composables/useWrapGridNav";

interface PlatformGroup {
  slug: string;
  name: string;
  games: DeviceGame[];
}

const { t } = useI18n();
const alive = useIsAlive();
const snackbar = useSnackbar();
const deviceLibrary = storeDeviceLibrary();
const { games, ready, totalBytes } = storeToRefs(deviceLibrary);
const { platformNames, load: loadFilters } = useCatalogFilters();
const { sortPlatforms } = usePlatformPreferences();

usePageTitle(() => t("common.library"));

const search = ref("");
const visible = computed(() => {
  const term = search.value.trim().toLowerCase();
  return games.value.filter(
    (g) => !term || g.name.toLowerCase().includes(term),
  );
});

const groups = computed<PlatformGroup[]>(() => {
  const bySlug = new Map<string, DeviceGame[]>();
  for (const game of visible.value) {
    bySlug.set(game.platform_slug, [
      ...(bySlug.get(game.platform_slug) ?? []),
      game,
    ]);
  }
  const unordered = [...bySlug.entries()].map(([slug, list]) => ({
    slug,
    name: platformNames.value[slug] ?? slug,
    games: [...list].sort((a, b) => a.name.localeCompare(b.name)),
  }));
  unordered.sort((a, b) => a.name.localeCompare(b.name));
  return sortPlatforms(unordered);
});

const gridRoot = ref<HTMLElement | null>(null);
useWrapGridNav(gridRoot, { cellSelector: ".cat-card" });

onMounted(() => {
  void deviceLibrary.init();
  loadFilters().catch(() => {
    // Platform names fall back to slugs.
  });
});

const selected = ref<CatalogGame | null>(null);
const dialogOpen = ref(false);

async function openGame(game: Pick<DeviceGame, "igdb_id">) {
  try {
    const res = await catalogApi.getCatalogGame({ igdbId: game.igdb_id });
    if (!alive.value) return;
    selected.value = res.data;
    dialogOpen.value = true;
  } catch {
    if (alive.value) snackbar.error(t("catalog.load-failed"));
  }
}
</script>

<template>
  <IndexShell>
    <template #header>
      <PageHeader :title="t('common.library')" :count="games.length">
        <RTextField
          v-if="games.length"
          v-model="search"
          class="r-v2-lib__search"
          variant="outlined"
          density="compact"
          prepend-inner-icon="mdi-magnify"
          :placeholder="t('common.search')"
          clearable
          hide-details
        />
      </PageHeader>
      <p v-if="games.length" class="r-v2-lib__subtitle">
        {{
          t("catalog.library-size", {
            count: games.length,
            size: formatBytes(totalBytes),
          })
        }}
      </p>
    </template>

    <div ref="gridRoot" class="r-v2-lib">
      <div v-if="!ready" class="r-v2-lib__cells">
        <RSkeletonBlock
          v-for="n in 6"
          :key="`sk-${n}`"
          width="calc(var(--r-card-art-h) * 0.75)"
          height="var(--r-card-art-h)"
          rounded="card"
        />
      </div>

      <EmptyState
        v-else-if="!games.length"
        variant="boxed"
        icon="mdi-cellphone-arrow-down"
        :message="t('catalog.library-empty')"
      >
        <p class="r-v2-lib__empty-msg">{{ t("catalog.library-empty") }}</p>
        <RBtn
          color="primary"
          prepend-icon="mdi-compass-outline"
          :to="{ name: ROUTES.CATALOG }"
        >
          {{ t("catalog.browse-all") }}
        </RBtn>
      </EmptyState>

      <EmptyState
        v-else-if="!visible.length"
        icon="mdi-magnify-close"
        :message="t('common.no-results')"
      />

      <section
        v-for="group in groups"
        v-else
        :key="group.slug"
        class="r-v2-lib__group"
      >
        <h2 class="r-v2-lib__group-title">
          <CachedPlatformIcon
            :slug="group.slug"
            :name="group.name"
            :size="24"
          />
          <span>{{ group.name }}</span>
          <span class="r-v2-lib__group-count">{{ group.games.length }}</span>
        </h2>
        <div class="r-v2-lib__cells">
          <CatalogCard
            v-for="(game, i) in group.games"
            :key="game.igdb_id"
            class="r-v2-card-fade"
            :style="{ '--card-fade-i': i }"
            :game="game"
            @select="openGame"
          />
        </div>
      </section>
    </div>

    <CatalogGameDialog
      v-model="dialogOpen"
      :game="selected"
      :platform-names="platformNames"
      @update:game="selected = $event"
    />
  </IndexShell>
</template>

<style scoped>
.r-v2-lib {
  display: flex;
  flex-direction: column;
  gap: var(--r-space-6);
}

.r-v2-lib__search {
  margin-left: auto;
  flex: 0 1 260px;
  min-width: 180px;
}

.r-v2-lib__subtitle {
  margin: -12px 0 0;
  padding-bottom: var(--r-space-4);
  font-size: 13.5px;
  color: var(--r-color-fg-muted);
}

.r-v2-lib__group {
  display: flex;
  flex-direction: column;
  gap: var(--r-space-3);
}

.r-v2-lib__group-title {
  display: flex;
  align-items: center;
  gap: var(--r-space-2);
  margin: 0;
  font-size: var(--r-font-size-md);
  font-weight: var(--r-font-weight-semibold);
  color: var(--r-color-fg-heading);
}

.r-v2-lib__group-count {
  font-size: var(--r-font-size-xs);
  font-weight: var(--r-font-weight-medium);
  color: var(--r-color-fg-muted);
}

.r-v2-lib__cells {
  display: flex;
  flex-wrap: wrap;
  gap: var(--r-space-5) var(--r-space-4);
}

html[data-bp~="xs"] .r-v2-lib__cells {
  justify-content: center;
}

.r-v2-lib__empty-msg {
  margin: 0 0 var(--r-space-3);
}
</style>
