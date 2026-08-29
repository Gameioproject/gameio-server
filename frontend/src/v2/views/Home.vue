<script setup lang="ts">
// Home: what to pick up next (server-side play history), what is on this
// device, and a few doors into the catalog.
import { RBtn, RIcon, RSkeletonBlock } from "@v2/lib";
import { storeToRefs } from "pinia";
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { ROUTES } from "@/plugins/router";
import catalogApi, { type CatalogGame } from "@/services/api/catalog";
import storeCollections from "@/stores/collections";
import storeDeviceLibrary from "@/stores/deviceLibrary";
import CatalogCard, {
  type CatalogCardGame,
} from "@/v2/components/Catalog/CatalogCard.vue";
import CatalogGameDialog from "@/v2/components/Catalog/CatalogGameDialog.vue";
import CollectionTile from "@/v2/components/Collections/CollectionTile.vue";
import CardRow from "@/v2/components/Home/CardRow.vue";
import EmptyState from "@/v2/components/shared/EmptyState.vue";
import { useCan } from "@/v2/composables/useCan";
import { useCatalogFilters } from "@/v2/composables/useCatalogFilters";
import { useGridNav } from "@/v2/composables/useGridNav";
import { useIsAlive } from "@/v2/composables/useIsAlive";
import { usePlatformPreferences } from "@/v2/composables/usePlatformPreferences";
import { useSnackbar } from "@/v2/composables/useSnackbar";

const ROW_LIMIT = 12;

const { t } = useI18n();
const alive = useIsAlive();
const snackbar = useSnackbar();
const collectionsStore = storeCollections();
const deviceLibrary = storeDeviceLibrary();
const { allCollections, fetchingCollections } = storeToRefs(collectionsStore);
const { games: deviceGames } = storeToRefs(deviceLibrary);
const { filters, platformNames, load: loadFilters } = useCatalogFilters();
const canManageHosts = useCan("rom.edit");
const { hidden: hiddenPlatforms } = usePlatformPreferences();

const gridRoot = ref<HTMLElement | null>(null);
useGridNav(gridRoot);

const continueGames = ref<CatalogGame[]>([]);
const favoriteGames = ref<CatalogGame[]>([]);
const topGames = ref<CatalogGame[]>([]);
const topIsPersonal = ref(true);
const fetchingContinue = ref(true);
const fetchingTop = ref(true);
const initialLoadDone = ref(false);

const catalogEmpty = computed(
  () => !!filters.value && filters.value.total_games === 0,
);
const noHosts = computed(
  () => !!filters.value && filters.value.owned_games === 0,
);

const recentDeviceGames = computed(() =>
  [...deviceGames.value]
    .sort((a, b) => b.added_at.localeCompare(a.added_at))
    .slice(0, ROW_LIMIT),
);

async function fetchRow(
  params: Parameters<typeof catalogApi.getCatalogGames>[0],
): Promise<CatalogGame[]> {
  try {
    const { data } = await catalogApi.getCatalogGames({
      limit: ROW_LIMIT,
      ...params,
    });
    return data.items;
  } catch {
    // A missing row is better than an error toast on the home page.
    return [];
  }
}

async function fetchTop() {
  const excludePlatforms = [...hiddenPlatforms.value];
  const personal = await fetchRow({
    ownedPlatforms: true,
    excludePlatforms,
    orderBy: "rating",
    orderDir: "desc",
  });
  if (personal.length) return personal;
  topIsPersonal.value = false;
  return fetchRow({ excludePlatforms, orderBy: "rating", orderDir: "desc" });
}

onMounted(async () => {
  void deviceLibrary.init();
  loadFilters(true).catch(() => {
    // The rows still render; only the empty-state copy needs the totals.
  });
  const loads: Promise<unknown>[] = [
    fetchRow({ played: true, orderBy: "last_played", orderDir: "desc" })
      .then((items) => {
        if (alive.value) continueGames.value = items;
      })
      .finally(() => {
        if (alive.value) fetchingContinue.value = false;
      }),
    fetchRow({ favorite: true, orderBy: "name", orderDir: "asc" }).then(
      (items) => {
        if (alive.value) favoriteGames.value = items;
      },
    ),
    fetchTop()
      .then((items) => {
        if (alive.value) topGames.value = items;
      })
      .finally(() => {
        if (alive.value) fetchingTop.value = false;
      }),
  ];
  if (allCollections.value.length === 0) {
    loads.push(collectionsStore.fetchCollections());
  }
  await Promise.allSettled(loads);
  if (alive.value) initialLoadDone.value = true;
});

// --- Game sheet --------------------------------------------------------

const selected = ref<CatalogGame | null>(null);
const dialogOpen = ref(false);

function openGame(game: CatalogGame) {
  selected.value = game;
  dialogOpen.value = true;
}

async function openDeviceGame(game: CatalogCardGame) {
  const known = [
    ...continueGames.value,
    ...favoriteGames.value,
    ...topGames.value,
  ].find((g) => g.igdb_id === game.igdb_id);
  if (known) return openGame(known);
  try {
    const res = await catalogApi.getCatalogGame({ igdbId: game.igdb_id });
    if (alive.value) openGame(res.data);
  } catch {
    if (alive.value) snackbar.error(t("catalog.load-failed"));
  }
}

function replaceIn(list: CatalogGame[], game: CatalogGame) {
  const index = list.findIndex((g) => g.igdb_id === game.igdb_id);
  if (index !== -1) list[index] = game;
  return index;
}

function replaceGame(game: CatalogGame) {
  replaceIn(continueGames.value, game);
  replaceIn(topGames.value, game);
  const favIndex = replaceIn(favoriteGames.value, game);
  if (game.is_favorite && favIndex === -1) favoriteGames.value.push(game);
  else if (!game.is_favorite && favIndex !== -1)
    favoriteGames.value.splice(favIndex, 1);
  selected.value = game;
}
</script>

<template>
  <div ref="gridRoot" class="r-v2-home">
    <EmptyState
      v-if="initialLoadDone && catalogEmpty"
      variant="boxed"
      icon="mdi-compass-off-outline"
      :message="t('catalog.empty')"
    />

    <template v-else>
      <!-- Admins see where downloads come from before any game has a link. -->
      <EmptyState
        v-if="initialLoadDone && noHosts && canManageHosts"
        variant="boxed"
        icon="mdi-cloud-download-outline"
        :message="t('catalog.hosts-none')"
      >
        <p class="r-v2-home__empty-msg">{{ t("catalog.hosts-none") }}</p>
        <RBtn
          color="primary"
          prepend-icon="mdi-cloud-download-outline"
          :to="{ name: ROUTES.DOWNLOAD_HOSTS }"
        >
          {{ t("catalog.hosts-title") }}
        </RBtn>
      </EmptyState>

      <CardRow
        v-if="fetchingContinue || continueGames.length"
        :title="t('home.continue-playing')"
        :count="continueGames.length"
      >
        <template #icon>
          <RIcon icon="mdi-play-circle-outline" size="20" />
        </template>
        <template v-if="fetchingContinue && !continueGames.length">
          <RSkeletonBlock
            v-for="n in 6"
            :key="`cs-${n}`"
            width="calc(var(--r-card-art-h) * 0.75)"
            height="var(--r-card-art-h)"
            rounded="card"
          />
        </template>
        <template v-else>
          <CatalogCard
            v-for="(game, i) in continueGames"
            :key="`cont-${game.igdb_id}`"
            class="r-v2-card-fade"
            :style="{ '--card-fade-i': i }"
            :game="game"
            @select="openGame(game)"
          />
        </template>
      </CardRow>

      <CardRow
        v-if="recentDeviceGames.length"
        :title="t('catalog.on-device')"
        :count="deviceGames.length"
      >
        <template #icon>
          <RIcon icon="mdi-cellphone-check" size="20" />
        </template>
        <template #title-append>
          <RBtn variant="text" size="small" :to="{ name: ROUTES.LIBRARY }">
            {{ t("common.library") }}
          </RBtn>
        </template>
        <CatalogCard
          v-for="(game, i) in recentDeviceGames"
          :key="`dev-${game.igdb_id}`"
          class="r-v2-card-fade"
          :style="{ '--card-fade-i': i }"
          :game="game"
          @select="openDeviceGame"
        />
      </CardRow>

      <CardRow
        v-if="favoriteGames.length"
        :title="t('catalog.favorites')"
        :count="favoriteGames.length"
      >
        <template #icon>
          <RIcon icon="mdi-heart" size="20" />
        </template>
        <CatalogCard
          v-for="(game, i) in favoriteGames"
          :key="`fav-${game.igdb_id}`"
          class="r-v2-card-fade"
          :style="{ '--card-fade-i': i }"
          :game="game"
          @select="openGame(game)"
        />
      </CardRow>

      <CardRow
        v-if="fetchingTop || topGames.length"
        :title="
          topIsPersonal ? t('catalog.top-for-you') : t('catalog.top-rated')
        "
        :count="topGames.length"
      >
        <template #icon>
          <RIcon icon="mdi-compass-outline" size="20" />
        </template>
        <template #title-append>
          <RBtn variant="text" size="small" :to="{ name: ROUTES.CATALOG }">
            {{ t("catalog.browse-all") }}
          </RBtn>
        </template>
        <template v-if="fetchingTop && !topGames.length">
          <RSkeletonBlock
            v-for="n in 6"
            :key="`ts-${n}`"
            width="calc(var(--r-card-art-h) * 0.75)"
            height="var(--r-card-art-h)"
            rounded="card"
          />
        </template>
        <template v-else>
          <CatalogCard
            v-for="(game, i) in topGames"
            :key="`top-${game.igdb_id}`"
            class="r-v2-card-fade"
            :style="{ '--card-fade-i': i }"
            :game="game"
            @select="openGame(game)"
          />
        </template>
      </CardRow>

      <CardRow
        v-if="allCollections.length || fetchingCollections"
        :title="t('common.collections')"
        :count="allCollections.length"
        gap="16px"
      >
        <template #icon>
          <RIcon icon="mdi-bookmark-outline" size="20" />
        </template>
        <CollectionTile
          v-for="(c, i) in allCollections"
          :id="c.id"
          :key="`coll-${c.id}`"
          class="r-v2-card-fade"
          :style="{ '--card-fade-i': i }"
          :name="c.name"
          :rom-count="c.game_count ?? 0"
          :covers="c.url_covers ?? []"
          :to="`/collection/${c.id}`"
          :is-public="c.is_public"
          variant="row"
        />
      </CardRow>
    </template>

    <CatalogGameDialog
      v-model="dialogOpen"
      :game="selected"
      :platform-names="platformNames"
      @update:game="replaceGame"
    />
  </div>
</template>

<style scoped>
.r-v2-home {
  display: flex;
  flex-direction: column;
  gap: var(--r-space-6);
  padding: 24px var(--r-row-pad) 60px;
}

.r-v2-home__empty-msg {
  margin: 0 0 var(--r-space-3);
}
</style>
