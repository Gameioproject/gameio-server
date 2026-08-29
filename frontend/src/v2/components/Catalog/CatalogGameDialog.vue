<script setup lang="ts">
// CatalogGameDialog: the game sheet. Playable games are downloaded onto this
// device (IndexedDB) and run in the browser; the server never serves bytes.
import {
  RBtn,
  RDialog,
  RIcon,
  RProgressLinear,
  RSelect,
  RTag,
  RTextField,
} from "@v2/lib";
import { storeToRefs } from "pinia";
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import catalogApi, { type CatalogGame } from "@/services/api/catalog";
import collectionApi from "@/services/api/collection";
import storeCollections from "@/stores/collections";
import storeDeviceLibrary from "@/stores/deviceLibrary";
import { formatBytes } from "@/utils";
import { useCan } from "@/v2/composables/useCan";
import { useConfirm } from "@/v2/composables/useConfirm";
import { useIsAlive } from "@/v2/composables/useIsAlive";
import { usePlatformPlayableChecker } from "@/v2/composables/usePlatformPlayable";
import { useSnackbar } from "@/v2/composables/useSnackbar";

type GameSource = CatalogGame["sources"][number];

const props = defineProps<{
  modelValue: boolean;
  game: CatalogGame | null;
  /** Display names keyed by platform slug, from the catalog filters. */
  platformNames: Record<string, string>;
  /** When set, the sheet offers to remove the game from that collection. */
  collectionId?: number;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
  /** The game changed server-side; the owner replaces its copy. */
  (e: "update:game", value: CatalogGame): void;
  (e: "removed-from-collection", igdbId: number): void;
}>();

const { t } = useI18n();
const router = useRouter();
const snackbar = useSnackbar();
const confirm = useConfirm();
const alive = useIsAlive();
const canEditLinks = useCan("rom.edit");
const canCollect = useCan("collection.edit");
const { isPlayable } = usePlatformPlayableChecker();
const collectionsStore = storeCollections();
const { allCollections } = storeToRefs(collectionsStore);
const deviceLibrary = storeDeviceLibrary();

function errorText(err: unknown): string {
  const e = err as {
    response?: { data?: { detail?: string } };
    message?: string;
  };
  return e?.response?.data?.detail || e?.message || t("catalog.load-failed");
}

async function refreshGame(igdbId: number) {
  const res = await catalogApi.getCatalogGame({ igdbId });
  if (alive.value && props.game?.igdb_id === igdbId)
    emit("update:game", res.data);
}

// --- This device -----------------------------------------------------------

const igdbId = computed(() => props.game?.igdb_id ?? 0);
const onDevice = computed(() => deviceLibrary.has(igdbId.value));
const deviceGame = computed(() => deviceLibrary.get(igdbId.value));
const download = computed(() => deviceLibrary.progress[igdbId.value] ?? null);
const downloadPercent = computed(() => {
  const p = download.value;
  if (!p?.total) return null;
  return Math.min(100, Math.round((p.loaded / p.total) * 100));
});

// The first source on a platform the browser can emulate, if any.
const playableSource = computed(
  () =>
    props.game?.sources.find((s) => isPlayable.value(s.platform_slug)) ?? null,
);

async function downloadToDevice() {
  const game = props.game;
  const source = playableSource.value;
  if (!game || !source) return;
  try {
    await deviceLibrary.download(game, source);
  } catch (err) {
    if (!alive.value || (err as Error).name === "AbortError") return;
    snackbar.error(errorText(err));
  }
}

async function removeFromDevice() {
  const game = props.game;
  if (!game) return;
  const ok = await confirm({
    title: t("catalog.remove-device"),
    body: t("catalog.remove-device-body", { name: game.name }),
    confirmText: t("common.remove"),
    tone: "danger",
  });
  if (!ok) return;
  try {
    await deviceLibrary.remove(game.igdb_id);
  } catch (err) {
    if (alive.value) snackbar.error(errorText(err));
  }
}

function play() {
  const game = props.game;
  const source = playableSource.value;
  if (!game || !source) return;
  emit("update:modelValue", false);
  void router.push({
    name: "catalog-play",
    params: { igdb: game.igdb_id },
    query: { source: source.id },
  });
}

// --- Favorites and collections ---------------------------------------------

const togglingFavorite = ref(false);
const targetCollection = ref<number | null>(null);
const addingToCollection = ref(false);
const removingFromCollection = ref(false);

const collectionItems = computed(() =>
  allCollections.value
    .filter((c) => !c.is_favorite && c.id !== props.collectionId)
    .map((c) => ({ title: c.name, value: c.id })),
);

watch(
  () => props.modelValue,
  (open) => {
    if (open && canCollect.value && allCollections.value.length === 0) {
      void collectionsStore.fetchCollections();
    }
  },
  { immediate: true },
);

async function toggleFavorite() {
  const game = props.game;
  if (!game || togglingFavorite.value) return;
  togglingFavorite.value = true;
  try {
    await collectionApi.setFavoriteGames([game.igdb_id], !game.is_favorite);
    await collectionsStore.fetchCollections();
    await refreshGame(game.igdb_id);
  } catch (err) {
    if (alive.value) snackbar.error(errorText(err));
  } finally {
    if (alive.value) togglingFavorite.value = false;
  }
}

async function addToCollection() {
  const game = props.game;
  if (!game || targetCollection.value == null) return;
  addingToCollection.value = true;
  try {
    await collectionApi.addGamesToCollection(targetCollection.value, [
      game.igdb_id,
    ]);
    await collectionsStore.fetchCollections();
    snackbar.success(t("rom.add-to-collection"));
  } catch (err) {
    if (alive.value) snackbar.error(errorText(err));
  } finally {
    if (alive.value) addingToCollection.value = false;
  }
}

async function removeFromCollection() {
  const game = props.game;
  const collectionId = props.collectionId;
  if (!game || collectionId == null) return;
  removingFromCollection.value = true;
  try {
    await collectionApi.removeGamesFromCollection(collectionId, [game.igdb_id]);
    await collectionsStore.fetchCollections();
    emit("removed-from-collection", game.igdb_id);
    emit("update:modelValue", false);
  } catch (err) {
    if (alive.value) snackbar.error(errorText(err));
  } finally {
    if (alive.value) removingFromCollection.value = false;
  }
}

// --- Download links --------------------------------------------------------

const linkUrl = ref("");
const linkPlatform = ref("");
const addingLink = ref(false);
const showLinks = ref(false);

watch(
  () => props.game?.igdb_id,
  () => {
    linkUrl.value = "";
    linkPlatform.value = props.game?.platform_slugs[0] ?? "";
    showLinks.value = false;
  },
  { immediate: true },
);

const linkPlatformItems = computed(() =>
  (props.game?.platform_slugs ?? []).map((slug) => ({
    title: props.platformNames[slug] ?? slug,
    value: slug,
  })),
);

async function addLink() {
  const game = props.game;
  if (!game || !linkUrl.value.trim()) return;
  addingLink.value = true;
  try {
    await catalogApi.addCatalogGameSource({
      igdbId: game.igdb_id,
      url: linkUrl.value.trim(),
      platformSlug: linkPlatform.value || undefined,
    });
    linkUrl.value = "";
    snackbar.success(t("catalog.link-added"));
    await refreshGame(game.igdb_id);
  } catch (err) {
    if (alive.value) snackbar.error(errorText(err));
  } finally {
    if (alive.value) addingLink.value = false;
  }
}

async function removeLink(source: GameSource) {
  const game = props.game;
  if (!game) return;
  const ok = await confirm({
    title: t("catalog.link-remove"),
    body: t("catalog.link-remove-body", { filename: source.filename }),
    confirmText: t("common.delete"),
    tone: "danger",
  });
  if (!ok) return;
  try {
    await catalogApi.deleteCatalogGameSource({ sourceId: source.id });
    await refreshGame(game.igdb_id);
  } catch (err) {
    if (alive.value) snackbar.error(errorText(err));
  }
}

// --- Presentation ----------------------------------------------------------

const ratingLabel = computed(() =>
  props.game?.rating == null ? null : Math.round(props.game.rating),
);

const trailerUrl = computed(() =>
  props.game?.youtube_video_id
    ? `https://www.youtube.com/watch?v=${props.game.youtube_video_id}`
    : null,
);

function downloadUrl(sourceId: number): string {
  return catalogApi.getCatalogDownloadUrl({ igdbId: igdbId.value, sourceId });
}

function sourceLabel(source: GameSource): string {
  const parts = [source.filename];
  if (source.size != null) parts.push(formatBytes(source.size));
  parts.push(source.host_name);
  return parts.join(" · ");
}
</script>

<template>
  <RDialog
    :model-value="modelValue"
    width="900"
    scroll-content
    icon="mdi-compass-outline"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <template #header>
      <span>{{ game?.name }}</span>
    </template>

    <template #content>
      <div v-if="game" class="cat-dlg">
        <div class="cat-dlg__main">
          <div class="cat-dlg__cover">
            <img
              v-if="game.url_cover"
              class="cat-dlg__cover-img"
              :src="game.url_cover"
              :alt="game.name"
            />
            <span v-else class="cat-dlg__cover-placeholder">
              <RIcon icon="mdi-controller" size="40" />
            </span>
          </div>

          <div class="cat-dlg__body">
            <div class="cat-dlg__meta">
              <span v-if="game.release_year">{{ game.release_year }}</span>
              <RTag
                v-for="slug in game.platform_slugs"
                :key="slug"
                tone="neutral"
                size="small"
                :text="platformNames[slug] ?? slug"
              />
              <RTag
                v-if="onDevice"
                tone="brand"
                size="small"
                prepend-icon="mdi-check"
                :text="t('catalog.on-device')"
              />
            </div>

            <div v-if="ratingLabel != null" class="cat-dlg__rating">
              <RIcon icon="mdi-star" size="18" />
              <strong>{{ ratingLabel }}</strong>
              <span class="cat-dlg__rating-scale">/ 100</span>
              <span class="cat-dlg__rating-count">
                {{ t("catalog.rating-count", { count: game.rating_count }) }}
              </span>
            </div>

            <div v-if="game.genres.length" class="cat-dlg__genres">
              <RTag
                v-for="genre in game.genres"
                :key="genre"
                tone="brand"
                size="small"
                :text="genre"
              />
            </div>

            <p v-if="game.summary" class="cat-dlg__summary">
              {{ game.summary }}
            </p>

            <div class="cat-dlg__actions">
              <template v-if="playableSource">
                <RBtn color="primary" prepend-icon="mdi-play" @click="play">
                  {{ t("rom.play") }}
                </RBtn>
                <RBtn
                  v-if="onDevice"
                  variant="text"
                  prepend-icon="mdi-cellphone-remove"
                  @click="removeFromDevice"
                >
                  {{ t("catalog.remove-device") }}
                </RBtn>
                <RBtn
                  v-else-if="download"
                  variant="outlined"
                  prepend-icon="mdi-close"
                  @click="deviceLibrary.cancel(game.igdb_id)"
                >
                  {{ t("common.cancel") }}
                </RBtn>
                <RBtn
                  v-else
                  variant="outlined"
                  prepend-icon="mdi-download"
                  :disabled="!deviceLibrary.supported"
                  @click="downloadToDevice"
                >
                  {{ t("catalog.download-device") }}
                </RBtn>
              </template>
              <template v-else-if="game.owned">
                <RBtn
                  v-for="source in game.sources"
                  :key="source.id"
                  color="primary"
                  prepend-icon="mdi-download"
                  :href="downloadUrl(source.id)"
                >
                  {{ t("catalog.download-file") }}
                  <template v-if="game.sources.length > 1 && source.region">
                    ({{ source.region }})
                  </template>
                </RBtn>
              </template>
              <RTag
                v-else
                tone="neutral"
                prepend-icon="mdi-link-off"
                :text="t('catalog.no-link')"
              />

              <RBtn
                v-if="canCollect"
                variant="text"
                :icon="game.is_favorite ? 'mdi-heart' : 'mdi-heart-outline'"
                :aria-label="
                  game.is_favorite
                    ? t('rom.remove-from-favorites')
                    : t('rom.add-to-favorites')
                "
                :loading="togglingFavorite"
                @click="toggleFavorite"
              />

              <RBtn
                v-if="trailerUrl"
                variant="text"
                prepend-icon="mdi-youtube"
                :href="trailerUrl"
                target="_blank"
              >
                {{ t("catalog.trailer") }}
              </RBtn>
              <RBtn
                v-if="game.igdb_url"
                variant="text"
                prepend-icon="mdi-open-in-new"
                :href="game.igdb_url"
                target="_blank"
              >
                IGDB
              </RBtn>
            </div>

            <div v-if="download" class="cat-dlg__download">
              <RProgressLinear
                :model-value="downloadPercent ?? 0"
                :indeterminate="downloadPercent === null"
                :aria-label="t('catalog.downloading')"
              />
              <span class="cat-dlg__download-label">
                {{ t("catalog.downloading") }}
                <template v-if="download.total">
                  {{ formatBytes(download.loaded) }} /
                  {{ formatBytes(download.total) }}
                </template>
              </span>
            </div>

            <p v-if="deviceGame" class="cat-dlg__hint">
              {{ deviceGame.file_name }} · {{ formatBytes(deviceGame.size) }}
            </p>

            <div
              v-if="
                canCollect && (collectionItems.length || collectionId != null)
              "
              class="cat-dlg__row"
            >
              <form
                v-if="collectionItems.length"
                class="cat-dlg__row"
                @submit.prevent="addToCollection"
              >
                <RSelect
                  :model-value="targetCollection"
                  :items="collectionItems"
                  :placeholder="t('common.collections')"
                  density="compact"
                  hide-details
                  class="cat-dlg__select"
                  @update:model-value="targetCollection = $event as number"
                />
                <RBtn
                  type="submit"
                  variant="outlined"
                  prepend-icon="mdi-bookmark-plus-outline"
                  :loading="addingToCollection"
                  :disabled="targetCollection == null"
                >
                  {{ t("rom.add-to-collection") }}
                </RBtn>
              </form>
              <RBtn
                v-if="collectionId != null"
                variant="text"
                prepend-icon="mdi-bookmark-remove-outline"
                :loading="removingFromCollection"
                @click="removeFromCollection"
              >
                {{ t("catalog.remove-from-collection") }}
              </RBtn>
            </div>

            <template v-if="canEditLinks">
              <RBtn
                variant="text"
                size="small"
                class="cat-dlg__links-toggle"
                :prepend-icon="
                  showLinks ? 'mdi-chevron-down' : 'mdi-chevron-right'
                "
                :aria-expanded="showLinks"
                @click="showLinks = !showLinks"
              >
                {{ t("catalog.links", { count: game.sources.length }) }}
              </RBtn>
              <template v-if="showLinks">
                <ul v-if="game.sources.length" class="cat-dlg__sources">
                  <li
                    v-for="source in game.sources"
                    :key="source.id"
                    class="cat-dlg__source"
                  >
                    <span>{{ sourceLabel(source) }}</span>
                    <RBtn
                      variant="text"
                      size="x-small"
                      icon="mdi-link-off"
                      :aria-label="t('catalog.link-remove')"
                      @click="removeLink(source)"
                    />
                  </li>
                </ul>
                <form class="cat-dlg__row" @submit.prevent="addLink">
                  <RTextField
                    v-model="linkUrl"
                    :label="t('catalog.add-link-url')"
                    :placeholder="t('catalog.add-link-hint')"
                    density="compact"
                    hide-details
                    class="cat-dlg__url"
                  />
                  <RSelect
                    v-if="linkPlatformItems.length > 1"
                    :model-value="linkPlatform"
                    :items="linkPlatformItems"
                    density="compact"
                    hide-details
                    class="cat-dlg__select"
                    @update:model-value="linkPlatform = $event as string"
                  />
                  <RBtn
                    type="submit"
                    variant="outlined"
                    prepend-icon="mdi-link-plus"
                    :loading="addingLink"
                    :disabled="!linkUrl.trim()"
                  >
                    {{ t("catalog.add-link") }}
                  </RBtn>
                </form>
              </template>
            </template>
          </div>
        </div>

        <div v-if="game.url_screenshots.length" class="cat-dlg__shots">
          <img
            v-for="url in game.url_screenshots"
            :key="url"
            :src="url"
            :alt="game.name"
            loading="lazy"
            class="cat-dlg__shot"
          />
        </div>
      </div>
    </template>
  </RDialog>
</template>

<style scoped>
.cat-dlg {
  display: flex;
  flex-direction: column;
  gap: var(--r-space-4);
}

.cat-dlg__main {
  display: flex;
  gap: var(--r-space-5);
  align-items: flex-start;
}

.cat-dlg__cover {
  flex-shrink: 0;
  width: 200px;
  height: 267px;
  border-radius: var(--r-radius-card);
  overflow: hidden;
  background: var(--r-color-surface);
  box-shadow: var(--r-elev-2);
}

.cat-dlg__cover-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cat-dlg__cover-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: var(--r-color-fg-faint);
}

.cat-dlg__body {
  display: flex;
  flex-direction: column;
  gap: var(--r-space-3);
  min-width: 0;
  flex: 1;
}

.cat-dlg__meta,
.cat-dlg__genres,
.cat-dlg__actions,
.cat-dlg__row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--r-space-2);
}

.cat-dlg__meta {
  color: var(--r-color-fg-secondary);
  font-size: var(--r-font-size-sm);
}

.cat-dlg__rating {
  display: flex;
  align-items: baseline;
  gap: var(--r-space-1);
  color: var(--r-color-warning-fg);
  font-size: var(--r-font-size-lg);
}

.cat-dlg__rating-scale,
.cat-dlg__rating-count {
  color: var(--r-color-fg-muted);
  font-size: var(--r-font-size-sm);
}

.cat-dlg__rating-count {
  margin-left: var(--r-space-2);
}

.cat-dlg__summary {
  margin: 0;
  color: var(--r-color-fg);
  line-height: var(--r-line-height-relaxed);
}

.cat-dlg__download {
  display: flex;
  flex-direction: column;
  gap: var(--r-space-1);
}

.cat-dlg__download-label,
.cat-dlg__hint {
  margin: 0;
  color: var(--r-color-fg-muted);
  font-size: var(--r-font-size-sm);
}

.cat-dlg__links-toggle {
  align-self: flex-start;
}

.cat-dlg__sources {
  margin: 0;
  padding: 0;
  list-style: none;
  font-size: 12.5px;
  color: var(--r-color-fg-muted);
}

.cat-dlg__source {
  display: flex;
  align-items: center;
  gap: var(--r-space-1);
}

.cat-dlg__url {
  flex: 1 1 260px;
}

.cat-dlg__select {
  flex: 0 1 200px;
}

.cat-dlg__shots {
  display: flex;
  gap: var(--r-space-2);
  overflow-x: auto;
  padding-bottom: var(--r-space-1);
}

.cat-dlg__shot {
  height: 160px;
  flex-shrink: 0;
  border-radius: var(--r-radius-md);
  object-fit: cover;
}

html[data-bp~="xs"] .cat-dlg__main {
  flex-direction: column;
  align-items: center;
}
</style>
