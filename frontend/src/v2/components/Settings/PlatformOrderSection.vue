<script setup lang="ts">
// PlatformOrderSection: which systems the user sees and in what order.
import { RBtn, RIcon } from "@v2/lib";
import { computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import SettingsSection from "@/v2/components/Settings/SettingsSection.vue";
import CachedPlatformIcon from "@/v2/components/shared/CachedPlatformIcon.vue";
import { useCatalogFilters } from "@/v2/composables/useCatalogFilters";
import { usePlatformPreferences } from "@/v2/composables/usePlatformPreferences";

const { t } = useI18n();
const { filters, load } = useCatalogFilters();
const { sortPlatforms, isHidden, move, setHidden } = usePlatformPreferences();

onMounted(() => {
  load().catch(() => {
    // The section stays empty when the catalog cannot be read.
  });
});

const platforms = computed(() =>
  sortPlatforms(
    [...(filters.value?.platforms ?? [])].sort((a, b) =>
      a.name.localeCompare(b.name),
    ),
  ),
);
const slugs = computed(() => platforms.value.map((p) => p.slug));
</script>

<template>
  <SettingsSection :title="t('settings.platforms-order')" icon="mdi-controller">
    <p class="r-v2-porder__desc">{{ t("settings.platforms-order-desc") }}</p>
    <ul class="r-v2-porder__list">
      <li
        v-for="(platform, index) in platforms"
        :key="platform.slug"
        class="r-v2-porder__row"
        :class="{ 'r-v2-porder__row--hidden': isHidden(platform.slug) }"
      >
        <CachedPlatformIcon
          :slug="platform.slug"
          :name="platform.name"
          :size="28"
        />
        <span class="r-v2-porder__name">{{ platform.name }}</span>
        <span class="r-v2-porder__count">{{ platform.game_count }}</span>
        <RBtn
          variant="text"
          size="x-small"
          icon="mdi-chevron-up"
          :aria-label="t('settings.platform-move-up')"
          :disabled="index === 0"
          @click="move(slugs, platform.slug, -1)"
        />
        <RBtn
          variant="text"
          size="x-small"
          icon="mdi-chevron-down"
          :aria-label="t('settings.platform-move-down')"
          :disabled="index === platforms.length - 1"
          @click="move(slugs, platform.slug, 1)"
        />
        <RBtn
          variant="text"
          size="x-small"
          :icon="isHidden(platform.slug) ? 'mdi-eye-off' : 'mdi-eye'"
          :aria-label="
            isHidden(platform.slug)
              ? t('settings.platform-show')
              : t('settings.platform-hide')
          "
          :aria-pressed="isHidden(platform.slug)"
          @click="setHidden(platform.slug, !isHidden(platform.slug))"
        />
      </li>
    </ul>
    <p v-if="!platforms.length" class="r-v2-porder__desc">
      <RIcon icon="mdi-information-outline" size="14" />
      {{ t("catalog.empty") }}
    </p>
  </SettingsSection>
</template>

<style scoped>
.r-v2-porder__desc {
  margin: 0;
  padding: var(--r-space-3) var(--r-space-4) 0;
  font-size: var(--r-font-size-sm);
  color: var(--r-color-fg-muted);
}

.r-v2-porder__list {
  margin: 0;
  padding: var(--r-space-2) var(--r-space-2) var(--r-space-3);
  list-style: none;
  display: flex;
  flex-direction: column;
}

.r-v2-porder__row {
  display: flex;
  align-items: center;
  gap: var(--r-space-2);
  padding: var(--r-space-1) var(--r-space-2);
  border-radius: var(--r-radius-md);
}

.r-v2-porder__row:hover {
  background: var(--r-color-surface-hover);
}

.r-v2-porder__row--hidden .r-v2-porder__name,
.r-v2-porder__row--hidden .r-v2-porder__count {
  color: var(--r-color-fg-faint);
  text-decoration: line-through;
}

.r-v2-porder__name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--r-font-size-sm);
  color: var(--r-color-fg);
}

.r-v2-porder__count {
  font-size: var(--r-font-size-xs);
  color: var(--r-color-fg-muted);
  margin-right: var(--r-space-2);
}
</style>
