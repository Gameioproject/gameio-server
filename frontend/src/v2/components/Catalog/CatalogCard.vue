<script setup lang="ts">
// CatalogCard: one cover tile. The only state it shows is whether the game
// is stored on this device (or on its way there).
import { RIcon, RProgressLinear } from "@v2/lib";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import type { CatalogGame } from "@/services/api/catalog";
import storeDeviceLibrary from "@/stores/deviceLibrary";

export type CatalogCardGame = Pick<
  CatalogGame,
  "igdb_id" | "name" | "url_cover_small"
> & { rating?: number | null };

defineOptions({ inheritAttrs: false });

const props = defineProps<{
  game: CatalogCardGame;
}>();

const emit = defineEmits<{
  (e: "select", game: CatalogCardGame): void;
}>();

const { t } = useI18n();
const deviceLibrary = storeDeviceLibrary();

const onDevice = computed(() => deviceLibrary.has(props.game.igdb_id));
const download = computed(
  () => deviceLibrary.progress[props.game.igdb_id] ?? null,
);
const downloadPercent = computed(() => {
  const p = download.value;
  if (!p?.total) return null;
  return Math.min(100, Math.round((p.loaded / p.total) * 100));
});

const ratingLabel = computed(() =>
  props.game.rating == null ? null : Math.round(props.game.rating).toString(),
);
</script>

<template>
  <button
    v-bind="$attrs"
    type="button"
    class="cat-card"
    :class="{ 'cat-card--device': onDevice }"
    :aria-label="game.name"
    @click="emit('select', game)"
  >
    <span class="cat-card__art">
      <img
        v-if="game.url_cover_small"
        class="cat-card__img"
        :src="game.url_cover_small"
        :alt="game.name"
        loading="lazy"
        decoding="async"
      />
      <span v-else class="cat-card__placeholder">
        <RIcon icon="mdi-controller" size="28" />
      </span>

      <span class="cat-card__overlay">
        <span
          v-if="onDevice"
          class="cat-card__badge"
          :title="t('catalog.on-device')"
        >
          <RIcon icon="mdi-check-bold" size="12" />
        </span>
        <span v-else />
        <span v-if="ratingLabel" class="cat-card__pill cat-card__pill--rating">
          <RIcon icon="mdi-star" size="11" />
          {{ ratingLabel }}
        </span>
      </span>

      <RProgressLinear
        v-if="download"
        class="cat-card__progress"
        :model-value="downloadPercent ?? 0"
        :indeterminate="downloadPercent === null"
        :height="4"
        :rounded="false"
        :aria-label="t('catalog.downloading')"
      />
    </span>
    <span class="cat-card__title">{{ game.name }}</span>
  </button>
</template>

<style scoped>
.cat-card {
  --cat-card-w: calc(var(--r-card-art-h) * 0.75);
  display: flex;
  flex-direction: column;
  gap: var(--r-space-2);
  width: var(--cat-card-w);
  flex: 0 0 auto;
  padding: 0;
  border: 0;
  background: none;
  color: inherit;
  text-align: left;
  cursor: pointer;
  border-radius: var(--r-radius-card);
}

.cat-card:focus-visible {
  outline: var(--r-focus-ring-width) solid var(--r-color-brand-primary);
  outline-offset: var(--r-focus-ring-offset);
}

.cat-card__art {
  position: relative;
  display: block;
  width: var(--cat-card-w);
  height: var(--r-card-art-h);
  border-radius: var(--r-radius-card);
  overflow: hidden;
  background: var(--r-color-surface);
  box-shadow: var(--r-elev-1);
  transition:
    transform var(--r-motion-fast) var(--r-motion-ease-out),
    box-shadow var(--r-motion-fast) var(--r-motion-ease-out);
}

html[data-input="mouse"] .cat-card:hover .cat-card__art,
.cat-card:focus-visible .cat-card__art {
  transform: translateY(-3px);
  box-shadow: var(--r-elev-3);
}

.cat-card__img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cat-card__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: var(--r-color-fg-faint);
}

.cat-card__overlay {
  position: absolute;
  top: 6px;
  left: 6px;
  right: 6px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  pointer-events: none;
}

.cat-card__pill {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 7px 2px 5px;
  border-radius: var(--r-radius-chip);
  font-size: 9.5px;
  font-weight: var(--r-font-weight-bold);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--r-color-overlay-fg);
}

.cat-card__badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--r-color-brand-primary);
  color: var(--r-color-overlay-fg);
  box-shadow: var(--r-elev-1);
}

.cat-card__pill--rating {
  background: color-mix(in srgb, black 65%, transparent);
}

.cat-card__progress {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
}

.cat-card__title {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 12.5px;
  line-height: 1.3;
  font-weight: var(--r-font-weight-medium);
  color: var(--r-color-fg-secondary);
}

.cat-card--device .cat-card__title {
  color: var(--r-color-fg);
}
</style>
