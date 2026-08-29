<script setup lang="ts">
// CatalogPlay: run a game from this device in EmulatorJS. The file is
// downloaded into IndexedDB first if it is not here yet; play sessions and
// saves/states go to the server so every device continues the same game.
import { RBtn, RIcon, RProgressLinear, RSelect, RSpinner } from "@v2/lib";
import { storeToRefs } from "pinia";
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { useTheme } from "vuetify";
import type { GameAssetKind } from "@/__generated__";
import catalogApi, { type CatalogGame } from "@/services/api/catalog";
import gameAssetsApi from "@/services/api/gameAssets";
import playApi from "@/services/api/play";
import storeConfig from "@/stores/config";
import storeDeviceLibrary from "@/stores/deviceLibrary";
import storeLanguage from "@/stores/language";
import storePlaying from "@/stores/playing";
import {
  areThreadsRequiredForEJSCore,
  formatBytes,
  getControlSchemeForPlatform,
  getSupportedEJSCores,
} from "@/utils";
import EmptyState from "@/v2/components/shared/EmptyState.vue";
import { useCatalogFilters } from "@/v2/composables/useCatalogFilters";
import { useIsAlive } from "@/v2/composables/useIsAlive";
import { usePageTitle } from "@/v2/composables/usePageTitle";
import { usePlatformPlayableChecker } from "@/v2/composables/usePlatformPlayable";
import { useSnackbar } from "@/v2/composables/useSnackbar";
import { rememberCore, resolveRememberedCore } from "@/v2/utils/coreStorage";
import {
  installEJSDefaultOptionsTrap,
  loadEmulatorJSSave,
  loadEmulatorJSState,
  readEmulatorJSSave,
} from "@/v2/utils/ejs";
import { loadEmulatorJS } from "@/v2/utils/ejsLoader";

const HEARTBEAT_MS = 30_000;

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const theme = useTheme();
const snackbar = useSnackbar();
const configStore = storeConfig();
const languageStore = storeLanguage();
const playingStore = storePlaying();
const deviceLibrary = storeDeviceLibrary();
const { selectedLanguage } = storeToRefs(languageStore);
const alive = useIsAlive();
const { isPlayable } = usePlatformPlayableChecker();
const { platformNames, load: loadFilters } = useCatalogFilters();

const igdbId = computed(() => Number(route.params.igdb));
const game = ref<CatalogGame | null>(null);
const loading = ref(true);
const running = ref(false);
const booting = ref(false);
const error = ref<string | null>(null);

usePageTitle(() => game.value?.name ?? null);

const sources = computed(() => game.value?.sources ?? []);
const selectedSourceId = ref<number | null>(null);
const source = computed(
  () =>
    sources.value.find((s) => s.id === selectedSourceId.value) ??
    sources.value[0] ??
    null,
);
const platformSlug = computed(() => source.value?.platform_slug ?? null);
const playable = computed(() => isPlayable.value(platformSlug.value));

const onDevice = computed(() => deviceLibrary.has(igdbId.value));
const download = computed(() => deviceLibrary.progress[igdbId.value] ?? null);
const downloadPercent = computed(() => {
  const p = download.value;
  if (!p?.total) return null;
  return Math.min(100, Math.round((p.loaded / p.total) * 100));
});

const supportedCores = computed(() =>
  platformSlug.value
    ? getSupportedEJSCores(
        platformSlug.value,
        configStore.config.EJS_NETPLAY_ENABLED,
      )
    : [],
);
const selectedCore = ref<string | null>(null);

const sourceItems = computed(() =>
  sources.value.map((s) => ({
    title: [s.filename, s.region, s.host_name].filter(Boolean).join(" · "),
    value: s.id,
  })),
);
const coreItems = computed(() =>
  supportedCores.value.map((core) => ({ title: core, value: core })),
);

onMounted(async () => {
  loadFilters().catch(() => {
    // Platform names fall back to slugs.
  });
  void deviceLibrary.init();
  try {
    const res = await catalogApi.getCatalogGame({ igdbId: igdbId.value });
    if (!alive.value) return;
    game.value = res.data;
    const wanted = Number(route.query.source);
    const stored = deviceLibrary.get(res.data.igdb_id);
    selectedSourceId.value =
      res.data.sources.find((s) => s.id === wanted)?.id ??
      res.data.sources.find((s) => s.id === stored?.source_id)?.id ??
      res.data.sources.find((s) => isPlayable.value(s.platform_slug))?.id ??
      res.data.sources[0]?.id ??
      null;
    if (platformSlug.value) {
      selectedCore.value = resolveRememberedCore(
        res.data.igdb_id,
        platformSlug.value,
        supportedCores.value,
      );
    }
  } catch {
    if (alive.value) error.value = t("catalog.load-failed");
  } finally {
    if (alive.value) loading.value = false;
  }
});

// --- Server sync: play session, saves and states ---------------------------

let sessionId: number | null = null;
let heartbeatTimer: ReturnType<typeof setInterval> | null = null;
let activeCore = "";

async function startSession() {
  try {
    const res = await playApi.startSession(igdbId.value);
    sessionId = res.data.id;
    heartbeatTimer = setInterval(() => {
      if (sessionId != null) {
        playApi.heartbeatSession(sessionId).catch(() => {
          // A missed beat only delays "continue playing" by a tick.
        });
      }
    }, HEARTBEAT_MS);
  } catch (err) {
    console.error("[Play] Could not start the play session", err);
  }
}

function stopSession() {
  if (heartbeatTimer) clearInterval(heartbeatTimer);
  heartbeatTimer = null;
  if (sessionId == null) return;
  const id = sessionId;
  sessionId = null;
  playApi.stopSession(id).catch(() => {
    // The heartbeat timeout closes it server-side anyway.
  });
}

async function uploadAsset(
  kind: GameAssetKind,
  data: ArrayBuffer | Uint8Array,
  screenshot?: ArrayBuffer,
) {
  const g = game.value;
  if (!g) return;
  try {
    await gameAssetsApi.uploadAsset({
      igdbId: g.igdb_id,
      kind,
      data,
      emulator: activeCore,
      fileName: `${g.igdb_id}.${kind === "save" ? "srm" : "state"}`,
      screenshot,
    });
  } catch (err) {
    console.error(`[Play] Could not upload the ${kind}`, err);
    if (alive.value) snackbar.error(t("catalog.sync-failed"));
  }
}

async function fetchLatest(kind: GameAssetKind): Promise<Uint8Array | null> {
  const g = game.value;
  if (!g) return null;
  const res = await gameAssetsApi.listAssets({
    igdbId: g.igdb_id,
    kind,
    emulator: activeCore,
  });
  const latest = res.data[0];
  return latest ? gameAssetsApi.getAssetContent(latest.id) : null;
}

async function restoreSave() {
  try {
    const save = await fetchLatest("save");
    if (save) loadEmulatorJSSave(save);
  } catch (err) {
    console.error("[Play] Could not restore the save", err);
  }
}

function flushSave() {
  if (!running.value) return;
  try {
    const save = readEmulatorJSSave();
    if (save) void uploadAsset("save", save);
  } catch (err) {
    console.error("[Play] Could not read the save", err);
  }
}

function installCallbacks() {
  window.EJS_onGameStart = () => {
    void restoreSave();
    void startSession();
  };
  window.EJS_onSaveSave = ({ save, screenshot }) => {
    void uploadAsset("save", save, screenshot);
  };
  window.EJS_onLoadSave = () => {
    void restoreSave();
  };
  window.EJS_onSaveState = ({ state, screenshot }) => {
    void uploadAsset("state", state, screenshot);
  };
  window.EJS_onLoadState = () => {
    fetchLatest("state")
      .then((state) => {
        if (state) loadEmulatorJSState(state);
        else snackbar.info(t("catalog.no-state"));
      })
      .catch((err) => {
        console.error("[Play] Could not load the state", err);
        snackbar.error(t("catalog.sync-failed"));
      });
  };
}

// --- Boot ------------------------------------------------------------------

async function ensureOnDevice(): Promise<Blob | null> {
  const g = game.value;
  const s = source.value;
  if (!g || !s) return null;
  if (!deviceLibrary.has(g.igdb_id)) {
    await deviceLibrary.download(g, s);
  }
  return deviceLibrary.getFile(g.igdb_id);
}

async function play() {
  const g = game.value;
  const s = source.value;
  const slug = platformSlug.value;
  if (!g || !s || !slug || booting.value) return;
  booting.value = true;
  error.value = null;

  let file: Blob | null = null;
  try {
    file = await ensureOnDevice();
  } catch (err) {
    booting.value = false;
    if (!alive.value || (err as Error).name === "AbortError") return;
    snackbar.error(t("catalog.download-failed"));
    return;
  }
  if (!alive.value) return;
  if (!file) {
    booting.value = false;
    error.value = t("catalog.download-failed");
    return;
  }

  const core =
    supportedCores.value.find((c) => c === selectedCore.value) ??
    supportedCores.value[0];
  rememberCore(g.igdb_id, slug, core);
  activeCore = core;

  window.EJS_core = core;
  window.EJS_controlScheme = getControlSchemeForPlatform(slug);
  window.EJS_threads = areThreadsRequiredForEJSCore(core);
  window.EJS_gameID = g.igdb_id;
  window.EJS_gameName = deviceLibrary.get(g.igdb_id)?.file_name ?? s.filename;
  window.EJS_gameUrl = file;
  window.EJS_biosUrl = "";
  window.EJS_player = "#game";
  window.EJS_color = "#A453FF";
  window.EJS_alignStartButton = "center";
  window.EJS_startOnLoaded = true;
  window.EJS_fullscreenOnLoaded = false;
  window.EJS_backgroundImage = `${window.location.origin}/assets/logos/romm_logo_xbox_one_circle_boot.svg`;
  window.EJS_backgroundColor = theme.current.value.colors.background;
  window.EJS_Buttons = { exitEmulation: false };
  window.EJS_defaultOptions = {
    "save-state-location": "browser",
    rewindEnabled: "enabled",
    ...configStore.getEJSCoreOptions(core),
  };
  const controls = configStore.getEJSControls(core);
  if (controls) window.EJS_defaultControls = controls;
  window.EJS_language = selectedLanguage.value.value.replace("_", "-");
  window.EJS_disableAutoLang = true;
  window.EJS_netplayServer = "";
  window.EJS_netplayICEServers = [];
  const {
    EJS_DEBUG,
    EJS_CACHE_LIMIT,
    EJS_DISABLE_AUTO_UNLOAD,
    EJS_DISABLE_BATCH_BOOTUP,
  } = configStore.config;
  window.EJS_DEBUG_XX = EJS_DEBUG;
  window.EJS_disableAutoUnload = EJS_DISABLE_AUTO_UNLOAD;
  window.EJS_disableBatchBootup = EJS_DISABLE_BATCH_BOOTUP;
  if (EJS_CACHE_LIMIT !== null) window.EJS_CacheLimit = EJS_CACHE_LIMIT;
  installEJSDefaultOptionsTrap();
  installCallbacks();

  running.value = true;
  playingStore.setPlaying(true);
  try {
    await loadEmulatorJS(configStore.config.EJS_NETPLAY_ENABLED);
  } catch (err) {
    console.error("[Play] Emulator load failure:", err);
    running.value = false;
    playingStore.setPlaying(false);
    error.value = t("catalog.play-failed");
  } finally {
    booting.value = false;
  }
}

function teardown() {
  flushSave();
  stopSession();
  if (running.value) window.EJS_emulator?.callEvent("exit");
  playingStore.setPlaying(false);
  running.value = false;
}

function stop() {
  teardown();
  router.back();
}

function onPageHide() {
  flushSave();
  stopSession();
}

onMounted(() => window.addEventListener("pagehide", onPageHide));
onBeforeUnmount(() => {
  window.removeEventListener("pagehide", onPageHide);
  teardown();
});
</script>

<template>
  <section class="r-v2-cplay">
    <div v-if="loading" class="r-v2-cplay__center"><RSpinner /></div>

    <EmptyState
      v-else-if="error || !game"
      icon="mdi-alert-circle-outline"
      :message="error ?? t('catalog.load-failed')"
    />

    <EmptyState
      v-else-if="!source"
      icon="mdi-link-off"
      :message="t('catalog.no-link')"
    />

    <EmptyState
      v-else-if="!playable"
      icon="mdi-controller-off"
      :message="
        t('catalog.play-unsupported', {
          platform: platformNames[platformSlug ?? ''] ?? platformSlug,
        })
      "
    />

    <div v-else-if="!running" class="r-v2-cplay__setup">
      <div class="r-v2-cplay__cover">
        <img
          v-if="game.url_cover"
          class="r-v2-cplay__cover-img"
          :src="game.url_cover"
          :alt="game.name"
        />
        <span v-else class="r-v2-cplay__cover-placeholder">
          <RIcon icon="mdi-controller" size="40" />
        </span>
      </div>
      <div class="r-v2-cplay__panel">
        <h1 class="r-v2-cplay__title">{{ game.name }}</h1>
        <p class="r-v2-cplay__meta">
          {{ platformNames[platformSlug ?? ""] ?? platformSlug }}
          <template v-if="onDevice"> · {{ t("catalog.on-device") }}</template>
          <template v-else-if="source.size">
            · {{ formatBytes(source.size) }}
          </template>
        </p>
        <RSelect
          v-if="sources.length > 1 && !onDevice"
          :model-value="selectedSourceId"
          :items="sourceItems"
          :label="t('catalog.play-source')"
          density="compact"
          hide-details
          @update:model-value="selectedSourceId = $event as number"
        />
        <RSelect
          v-if="coreItems.length > 1"
          :model-value="selectedCore"
          :items="coreItems"
          :label="t('common.core')"
          density="compact"
          hide-details
          @update:model-value="selectedCore = $event as string"
        />
        <div v-if="download" class="r-v2-cplay__download">
          <RProgressLinear
            :model-value="downloadPercent ?? 0"
            :indeterminate="downloadPercent === null"
            :aria-label="t('catalog.downloading')"
          />
          <span class="r-v2-cplay__hint">
            {{ t("catalog.downloading") }}
            <template v-if="download.total">
              {{ formatBytes(download.loaded) }} /
              {{ formatBytes(download.total) }}
            </template>
          </span>
        </div>
        <p v-else class="r-v2-cplay__hint">
          <RIcon icon="mdi-information-outline" size="14" />
          {{ t("catalog.play-hint") }}
        </p>
        <div class="r-v2-cplay__actions">
          <RBtn
            color="primary"
            size="large"
            :prepend-icon="onDevice ? 'mdi-play' : 'mdi-download'"
            :loading="booting"
            :disabled="!deviceLibrary.supported"
            @click="play"
          >
            {{ onDevice ? t("rom.play") : t("catalog.play-and-download") }}
          </RBtn>
          <RBtn
            v-if="download"
            variant="text"
            @click="deviceLibrary.cancel(game.igdb_id)"
          >
            {{ t("common.cancel") }}
          </RBtn>
          <RBtn v-else variant="text" @click="router.back()">
            {{ t("common.cancel") }}
          </RBtn>
        </div>
      </div>
    </div>

    <div v-else class="r-v2-cplay__stage">
      <div id="game" class="r-v2-cplay__game" />
      <RBtn
        class="r-v2-cplay__exit"
        variant="translucent"
        size="small"
        prepend-icon="mdi-exit-to-app"
        @click="stop"
      >
        {{ t("catalog.play-exit") }}
      </RBtn>
    </div>
  </section>
</template>

<style scoped>
.r-v2-cplay {
  min-height: calc(100dvh - var(--r-nav-h));
  padding: 32px var(--r-row-pad) 60px;
}

.r-v2-cplay__center {
  display: flex;
  justify-content: center;
  padding: var(--r-space-8) 0;
}

.r-v2-cplay__setup {
  display: flex;
  flex-wrap: wrap;
  gap: var(--r-space-6);
  align-items: flex-start;
}

.r-v2-cplay__cover {
  flex-shrink: 0;
  width: 200px;
  height: 267px;
  border-radius: var(--r-radius-card);
  overflow: hidden;
  background: var(--r-color-surface);
  box-shadow: var(--r-elev-2);
}

.r-v2-cplay__cover-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.r-v2-cplay__cover-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: var(--r-color-fg-faint);
}

.r-v2-cplay__panel {
  flex: 1 1 320px;
  display: flex;
  flex-direction: column;
  gap: var(--r-space-3);
  max-width: 520px;
}

.r-v2-cplay__title {
  margin: 0;
  font-size: var(--r-font-size-2xl);
  font-weight: var(--r-font-weight-extrabold);
  color: var(--r-color-fg-heading);
}

.r-v2-cplay__meta {
  margin: 0;
  color: var(--r-color-fg-muted);
  font-size: 13px;
}

.r-v2-cplay__download {
  display: flex;
  flex-direction: column;
  gap: var(--r-space-1);
}

.r-v2-cplay__hint {
  display: flex;
  align-items: center;
  gap: var(--r-space-1);
  margin: 0;
  font-size: 12.5px;
  color: var(--r-color-fg-faint);
}

.r-v2-cplay__actions {
  display: flex;
  gap: var(--r-space-2);
  align-items: center;
}

.r-v2-cplay__stage {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  max-height: calc(100dvh - var(--r-nav-h) - 96px);
  background: black;
  border-radius: var(--r-radius-lg);
  overflow: hidden;
}

.r-v2-cplay__game {
  width: 100%;
  height: 100%;
}

.r-v2-cplay__exit {
  position: absolute;
  top: var(--r-space-2);
  right: var(--r-space-2);
  z-index: 2;
}
</style>
