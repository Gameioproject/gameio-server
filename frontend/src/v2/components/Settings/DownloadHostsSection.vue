<script setup lang="ts">
// DownloadHostsSection — where owned games live. A host is an Internet
// Archive item (indexable: its files become sources automatically) or a
// plain HTTP server (sources are added by hand from the game sheet).
import {
  RBtn,
  RIcon,
  RSelect,
  RSpinner,
  RSwitch,
  RTag,
  RTextField,
} from "@v2/lib";
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import type { GameHostKind } from "@/__generated__";
import hostsApi, { type GameHost } from "@/services/api/hosts";
import { formatTimestamp } from "@/utils";
import SettingsSection from "@/v2/components/Settings/SettingsSection.vue";
import { useCatalogFilters } from "@/v2/composables/useCatalogFilters";
import { useConfirm } from "@/v2/composables/useConfirm";
import { useIsAlive } from "@/v2/composables/useIsAlive";
import { useSnackbar } from "@/v2/composables/useSnackbar";

defineOptions({ inheritAttrs: false });

const POLL_MS = 3000;

const { t, locale } = useI18n();
const snackbar = useSnackbar();
const confirm = useConfirm();
const alive = useIsAlive();
const { filters, load: loadFilters } = useCatalogFilters();

const hosts = ref<GameHost[]>([]);
const loading = ref(true);
const showUnmatched = ref<Set<number>>(new Set());

const name = ref("");
const kind = ref<GameHostKind>("internet_archive");
const base = ref("");
const platformSlug = ref("");
const submitting = ref(false);

const kindItems = computed(() => [
  { title: t("catalog.hosts-kind-ia"), value: "internet_archive" },
  { title: t("catalog.hosts-kind-torrent"), value: "torrent" },
  { title: t("catalog.hosts-kind-http"), value: "http" },
]);

const kindLabel = (value: GameHostKind) =>
  value === "internet_archive"
    ? "Internet Archive"
    : value === "torrent"
      ? "MiNERVA torrent"
      : "HTTP";
const kindIcon = (value: GameHostKind) =>
  value === "internet_archive"
    ? "mdi-archive-outline"
    : value === "torrent"
      ? "mdi-magnet"
      : "mdi-server";

const platformItems = computed(() => [
  { title: t("catalog.hosts-any-platform"), value: "" },
  ...(filters.value?.platforms ?? []).map((p) => ({
    title: p.name,
    value: p.slug,
  })),
]);

const platformName = (slug: string | null) =>
  filters.value?.platforms.find((p) => p.slug === slug)?.name ?? slug ?? "";

const anyIndexing = computed(() => hosts.value.some((h) => h.indexing));

let pollTimer: ReturnType<typeof setInterval> | null = null;

function schedulePoll() {
  if (pollTimer || !anyIndexing.value) return;
  pollTimer = setInterval(() => {
    void load();
  }, POLL_MS);
}

function stopPoll() {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = null;
}

async function load() {
  try {
    const { data } = await hostsApi.getHosts();
    if (!alive.value) return;
    hosts.value = data;
    if (anyIndexing.value) schedulePoll();
    else stopPoll();
  } catch {
    if (alive.value) snackbar.error(t("catalog.load-failed"));
  } finally {
    if (alive.value) loading.value = false;
  }
}

function errorText(err: unknown): string {
  const e = err as {
    response?: { data?: { detail?: string } };
    message?: string;
  };
  return e?.response?.data?.detail || e?.message || t("catalog.load-failed");
}

async function addHost() {
  if (!name.value.trim() || !base.value.trim()) return;
  submitting.value = true;
  try {
    await hostsApi.createHost({
      name: name.value.trim(),
      kind: kind.value,
      base: base.value.trim(),
      platform_slug: platformSlug.value || null,
      enabled: true,
    });
    name.value = "";
    base.value = "";
    snackbar.success(t("catalog.hosts-created"));
    await load();
  } catch (err) {
    snackbar.error(errorText(err));
  } finally {
    submitting.value = false;
  }
}

async function setEnabled(host: GameHost, enabled: boolean) {
  host.enabled = enabled;
  try {
    await hostsApi.updateHost({ id: host.id, enabled });
  } catch (err) {
    host.enabled = !enabled;
    snackbar.error(errorText(err));
  }
}

async function index(host: GameHost) {
  try {
    await hostsApi.indexHost({ id: host.id });
    host.indexing = true;
    snackbar.info(t("catalog.hosts-index-started", { name: host.name }));
    schedulePoll();
  } catch (err) {
    snackbar.error(errorText(err));
  }
}

async function remove(host: GameHost) {
  const ok = await confirm({
    title: t("catalog.hosts-delete"),
    body: t("catalog.hosts-delete-body", {
      name: host.name,
      count: host.source_count,
    }),
    confirmText: t("common.delete"),
    tone: "danger",
  });
  if (!ok) return;
  try {
    await hostsApi.deleteHost({ id: host.id });
    hosts.value = hosts.value.filter((h) => h.id !== host.id);
  } catch (err) {
    snackbar.error(errorText(err));
  }
}

function toggleUnmatched(id: number) {
  const next = new Set(showUnmatched.value);
  if (next.has(id)) next.delete(id);
  else next.add(id);
  showUnmatched.value = next;
}

function statsLine(host: GameHost): string | null {
  const s = host.last_index_stats as {
    matched?: number;
    unmatched?: number;
    files_skipped?: number;
  } | null;
  if (!s) return null;
  return t("catalog.hosts-stats", {
    matched: s.matched ?? 0,
    unmatched: s.unmatched ?? 0,
    skipped: s.files_skipped ?? 0,
  });
}

function unmatchedSample(host: GameHost): string[] {
  const s = host.last_index_stats as { unmatched_sample?: string[] } | null;
  return s?.unmatched_sample ?? [];
}

onMounted(() => {
  void load();
  loadFilters().catch(() => {
    // The platform picker just falls back to "any platform".
  });
});

onBeforeUnmount(stopPoll);
</script>

<template>
  <SettingsSection
    :title="t('catalog.hosts-title')"
    icon="mdi-cloud-download-outline"
  >
    <p class="r-v2-hosts__intro">{{ t("catalog.hosts-intro") }}</p>

    <form class="r-v2-hosts__form" @submit.prevent="addHost">
      <RTextField
        v-model="name"
        :label="t('catalog.hosts-name')"
        density="compact"
        hide-details
        class="r-v2-hosts__field"
      />
      <RSelect
        :model-value="kind"
        :items="kindItems"
        :label="t('catalog.hosts-kind')"
        density="compact"
        hide-details
        class="r-v2-hosts__field r-v2-hosts__field--narrow"
        @update:model-value="kind = $event as GameHostKind"
      />
      <RTextField
        v-model="base"
        :label="
          kind === 'internet_archive'
            ? t('catalog.hosts-base-ia')
            : kind === 'torrent'
              ? t('catalog.hosts-base-torrent')
              : t('catalog.hosts-base-http')
        "
        :placeholder="
          kind === 'internet_archive'
            ? 'https://archive.org/details/roms-bestset-nintendo-64'
            : kind === 'torrent'
              ? 'https://minerva-archive.org/browse/./Redump/Sony - PlayStation 2/'
              : 'https://files.example.com/roms'
        "
        density="compact"
        hide-details
        class="r-v2-hosts__field r-v2-hosts__field--wide"
      />
      <RSelect
        :model-value="platformSlug"
        :items="platformItems"
        :label="t('catalog.hosts-default-platform')"
        density="compact"
        searchable
        hide-details
        class="r-v2-hosts__field r-v2-hosts__field--narrow"
        @update:model-value="platformSlug = ($event as string) || ''"
      />
      <RBtn
        type="submit"
        color="primary"
        prepend-icon="mdi-plus"
        :loading="submitting"
        :disabled="!name.trim() || !base.trim()"
      >
        {{ t("catalog.hosts-add") }}
      </RBtn>
    </form>

    <div v-if="loading" class="r-v2-hosts__empty"><RSpinner /></div>
    <p v-else-if="!hosts.length" class="r-v2-hosts__empty">
      {{ t("catalog.hosts-none") }}
    </p>

    <ul v-else class="r-v2-hosts__list">
      <li v-for="host in hosts" :key="host.id" class="r-v2-hosts__row">
        <div class="r-v2-hosts__main">
          <div class="r-v2-hosts__title">
            <RIcon :icon="kindIcon(host.kind)" size="18" />
            <span class="r-v2-hosts__name">{{ host.name }}</span>
            <RTag
              size="x-small"
              tone="neutral"
              :text="kindLabel(host.kind)"
            />
            <RTag
              v-if="host.platform_slug"
              size="x-small"
              tone="brand"
              :text="platformName(host.platform_slug)"
            />
          </div>
          <div class="r-v2-hosts__base">{{ host.base }}</div>
          <div class="r-v2-hosts__meta">
            <span>{{
              t("catalog.hosts-sources", { count: host.source_count })
            }}</span>
            <span v-if="host.last_indexed_at">
              · {{ t("catalog.hosts-last-indexed") }}
              {{ formatTimestamp(host.last_indexed_at, locale) }}
            </span>
            <span v-if="statsLine(host)">· {{ statsLine(host) }}</span>
            <RBtn
              v-if="unmatchedSample(host).length"
              variant="text"
              size="x-small"
              @click="toggleUnmatched(host.id)"
            >
              {{ t("catalog.hosts-unmatched-sample") }}
            </RBtn>
          </div>
          <ul v-if="showUnmatched.has(host.id)" class="r-v2-hosts__unmatched">
            <li v-for="file in unmatchedSample(host)" :key="file">
              {{ file }}
            </li>
          </ul>
        </div>
        <div class="r-v2-hosts__actions">
          <RSwitch
            :model-value="host.enabled"
            :label="t('catalog.hosts-enabled')"
            hide-details
            density="compact"
            @update:model-value="setEnabled(host, !!$event)"
          />
          <RBtn
            v-if="host.kind !== 'http'"
            variant="outlined"
            size="small"
            prepend-icon="mdi-refresh"
            :loading="host.indexing"
            @click="index(host)"
          >
            {{
              host.indexing
                ? t("catalog.hosts-indexing")
                : t("catalog.hosts-index")
            }}
          </RBtn>
          <RBtn
            variant="text"
            size="small"
            icon="mdi-delete-outline"
            :aria-label="t('catalog.hosts-delete')"
            @click="remove(host)"
          />
        </div>
      </li>
    </ul>
  </SettingsSection>
</template>

<style scoped>
.r-v2-hosts__intro {
  margin: 0 0 var(--r-space-4);
  color: var(--r-color-fg-muted);
  font-size: 13px;
}

.r-v2-hosts__form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--r-space-2);
  margin-bottom: var(--r-space-5);
}

.r-v2-hosts__field {
  flex: 1 1 180px;
}
.r-v2-hosts__field--narrow {
  flex: 0 1 200px;
}
.r-v2-hosts__field--wide {
  flex: 2 1 260px;
}

.r-v2-hosts__empty {
  padding: var(--r-space-6) 0;
  text-align: center;
  color: var(--r-color-fg-faint);
}

.r-v2-hosts__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--r-space-2);
}

.r-v2-hosts__row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--r-space-3);
  padding: var(--r-space-3) var(--r-space-4);
  border: 1px solid var(--r-color-border);
  border-radius: var(--r-radius-lg);
  background: var(--r-color-surface);
}

.r-v2-hosts__main {
  flex: 1 1 320px;
  min-width: 0;
}

.r-v2-hosts__title {
  display: flex;
  align-items: center;
  gap: var(--r-space-2);
}

.r-v2-hosts__name {
  font-weight: var(--r-font-weight-semibold);
}

.r-v2-hosts__base {
  font-size: 12.5px;
  color: var(--r-color-fg-muted);
  word-break: break-all;
}

.r-v2-hosts__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--r-space-1);
  margin-top: var(--r-space-1);
  font-size: 12px;
  color: var(--r-color-fg-secondary);
}

.r-v2-hosts__unmatched {
  margin: var(--r-space-2) 0 0;
  padding-left: var(--r-space-4);
  font-size: 12px;
  color: var(--r-color-fg-muted);
  max-height: 200px;
  overflow: auto;
}

.r-v2-hosts__actions {
  display: flex;
  align-items: center;
  gap: var(--r-space-2);
}
</style>
