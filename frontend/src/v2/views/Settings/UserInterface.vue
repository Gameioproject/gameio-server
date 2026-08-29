<script setup lang="ts">
import { RIcon } from "@v2/lib";
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useUISettings } from "@/composables/useUISettings";
import CrtWarmup from "@/v2/components/AppShell/CrtWarmup.vue";
import PlatformOrderSection from "@/v2/components/Settings/PlatformOrderSection.vue";
import SettingsSection from "@/v2/components/Settings/SettingsSection.vue";
import SettingsToggleRow from "@/v2/components/Settings/SettingsToggleRow.vue";
import LanguageSelector from "@/v2/components/shared/LanguageSelector.vue";
import { useCrtMode } from "@/v2/composables/useCrtMode";
import { useDebugMode } from "@/v2/composables/useDebugMode";
import { useReducedMotion } from "@/v2/composables/useReducedMotion";

const { t } = useI18n();
const { enabled: debugEnabled } = useDebugMode();

const { theme: selectedTheme } = useUISettings();

type Theme = "dark" | "light" | "auto";
const themeOptions: { value: Theme; label: string; icon: string }[] = [
  {
    value: "dark",
    label: t("settings.theme-dark"),
    icon: "mdi-moon-waning-crescent",
  },
  {
    value: "light",
    label: t("settings.theme-light"),
    icon: "mdi-white-balance-sunny",
  },
  {
    value: "auto",
    label: t("settings.theme-auto"),
    icon: "mdi-theme-light-dark",
  },
];

function setTheme(value: Theme) {
  selectedTheme.value = value;
}

// Cosmetic easter egg — toggle the persistent "CRT mode" shader; switching
// it ON also fires the one-shot power-on warm-up flash.
const { enabled: crtEnabled } = useCrtMode();
const crtWarmup = ref<InstanceType<typeof CrtWarmup> | null>(null);
function onCrtToggle(value: boolean) {
  crtEnabled.value = value;
  if (value) crtWarmup.value?.play();
}

// Reduced-motion mode — drop GPU-heavy decoration and animation (background
// blur, cover blur-up, spins, transitions) for smoother rendering on low-power
// devices. Per-device flag, defaults to the OS prefers-reduced-motion setting.
const { enabled: reducedMotion } = useReducedMotion();

// Selects --------------------------------------------------------------
</script>

<template>
  <div class="r-v2-section-stack">
    <SettingsSection :title="t('settings.language')" icon="mdi-translate">
      <div class="r-v2-ui__field">
        <LanguageSelector prefix-label />
      </div>
    </SettingsSection>

    <SettingsSection :title="t('settings.theme')" icon="mdi-brush-variant">
      <div class="r-v2-ui__theme-row">
        <button
          v-for="opt in themeOptions"
          :key="opt.value"
          type="button"
          class="r-v2-ui__theme-btn"
          :class="{
            'r-v2-ui__theme-btn--active': selectedTheme === opt.value,
          }"
          :aria-pressed="selectedTheme === opt.value"
          @click="setTheme(opt.value)"
        >
          <RIcon :icon="opt.icon" size="14" />
          <span>{{ opt.label }}</span>
        </button>
      </div>
      <div
        class="r-v2-ui__toggle-grid r-v2-ui__toggle-grid--single r-v2-ui__toggle-grid--bordered"
      >
        <SettingsToggleRow
          :model-value="crtEnabled"
          :title="t('common.crt-mode')"
          :description="t('settings.crt-mode-desc')"
          @update:model-value="onCrtToggle"
        />
        <SettingsToggleRow
          v-model="reducedMotion"
          :title="t('settings.reduced-motion')"
          :description="t('settings.reduced-motion-desc')"
        />
      </div>
    </SettingsSection>

    <!-- Developer — kept dead last, after UI version. Debug overlay is a
         per-device localStorage toggle (useDebugMode), not synced to the
         account, so it never follows you across machines. -->
    <PlatformOrderSection />

    <SettingsSection :title="t('settings.developer')" icon="mdi-bug-outline">
      <div class="r-v2-ui__toggle-grid r-v2-ui__toggle-grid--single">
        <SettingsToggleRow
          v-model="debugEnabled"
          :title="t('settings.debug-overlay')"
          :description="t('settings.debug-overlay-desc')"
        />
      </div>
    </SettingsSection>

    <!-- One-shot CRT power-on flash, fired when CRT mode is switched on
         from the Theme section above. -->
    <CrtWarmup ref="crtWarmup" />
  </div>
</template>

<style scoped>
/* Generic field row inside a section body. */
.r-v2-ui__field {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.r-v2-ui__field--bordered {
  border-top: 1px solid var(--r-color-border);
}

.r-v2-ui__advanced-toggle {
  align-self: flex-start;
}

.r-v2-ui__desc {
  margin: 0;
  color: var(--r-color-fg-muted);
  font-size: 13px;
  line-height: 1.5;
  max-width: 640px;
}

/* Toggle grid — 2 cols, hairline gap (the gap shows the section body's
   border colour through to give the divider effect). */
.r-v2-ui__toggle-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1px;
  background: var(--r-color-border);
}

.r-v2-ui__toggle-grid--single {
  grid-template-columns: 1fr;
}
/* Separate a toggle grid from the control row above it (e.g. the CRT
   toggle sitting under the theme picker) with a hairline divider. */
.r-v2-ui__toggle-grid--bordered {
  border-top: 1px solid var(--r-color-border);
}
html[data-bp~="xs"] .r-v2-ui__toggle-grid {
  grid-template-columns: 1fr;
}

/* Theme picker: 3 buttons in a flush row inside the section body. */
.r-v2-ui__theme-row {
  display: flex;
  gap: 10px;
  padding: 16px;
}
.r-v2-ui__theme-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid var(--r-color-border);
  background: var(--r-color-surface);
  color: var(--r-color-fg-muted);
  cursor: pointer;
  font-size: 13px;
  font-weight: var(--r-font-weight-medium);
  transition:
    background var(--r-motion-fast) var(--r-motion-ease-out),
    border-color var(--r-motion-fast) var(--r-motion-ease-out),
    color var(--r-motion-fast) var(--r-motion-ease-out);
}
.r-v2-ui__theme-btn:hover {
  background: var(--r-color-surface-hover);
  color: var(--r-color-fg);
}
.r-v2-ui__theme-btn--active {
  border-color: color-mix(
    in srgb,
    var(--r-color-brand-primary) 60%,
    transparent
  );
  background: color-mix(in srgb, var(--r-color-brand-primary) 14%, transparent);
  color: var(--r-color-brand-primary);
}
html[data-bp~="xs"] .r-v2-ui__theme-row {
  flex-direction: column;
}

/* UI version cards (v2-only). */
.r-v2-ui__version-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.r-v2-ui__version-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: var(--r-color-surface);
  border: 1px solid var(--r-color-border);
  border-radius: 10px;
  color: var(--r-color-fg-secondary);
  cursor: pointer;
  text-align: left;
  transition:
    background var(--r-motion-fast) var(--r-motion-ease-out),
    border-color var(--r-motion-fast) var(--r-motion-ease-out);
}
.r-v2-ui__version-card:hover {
  background: var(--r-color-surface-hover);
  border-color: var(--r-color-border-strong);
}
.r-v2-ui__version-card--active {
  background: color-mix(in srgb, var(--r-color-brand-primary) 12%, transparent);
  border-color: color-mix(
    in srgb,
    var(--r-color-brand-primary) 50%,
    transparent
  );
  color: var(--r-color-fg);
}

.r-v2-ui__version-icon {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
  background: color-mix(in srgb, var(--r-color-brand-primary) 14%, transparent);
  color: var(--r-color-brand-primary);
}

.r-v2-ui__version-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.r-v2-ui__version-titles {
  display: flex;
  align-items: center;
  gap: 8px;
}
.r-v2-ui__version-title {
  font-size: 14px;
  font-weight: var(--r-font-weight-semibold);
  color: var(--r-color-fg);
}
.r-v2-ui__version-blurb {
  font-size: 12px;
  color: var(--r-color-fg-muted);
  line-height: 1.4;
}

.r-v2-ui__version-dot {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--r-color-brand-primary);
  color: var(--r-color-overlay-emphasis-fg);
  display: grid;
  place-items: center;
  font-weight: var(--r-font-weight-bold);
}

html[data-bp~="xs"] .r-v2-ui__version-grid {
  grid-template-columns: 1fr;
}
</style>
