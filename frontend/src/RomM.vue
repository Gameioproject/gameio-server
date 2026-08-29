<script setup lang="ts">
// Root shell: theme + locale bootstrap, then the v2 layout tree through the
// `v2` named router view.
import { useLocalStorage } from "@vueuse/core";
import { storeToRefs } from "pinia";
import {
  computed,
  defineAsyncComponent,
  onMounted,
  onUnmounted,
  ref,
  watch,
} from "vue";
import { useI18n } from "vue-i18n";
import { useTheme } from "vuetify";
import storeLanguage from "@/stores/language";

const BackendStatusBanner = defineAsyncComponent(
  () => import("@/v2/components/AppShell/BackendStatusBanner.vue"),
);

const { locale } = useI18n({ useScope: "global" });
const languageStore = storeLanguage();
const vuetifyTheme = useTheme();
const { languages } = storeToRefs(languageStore);
const storedLocale = useLocalStorage("settings.locale", "");
const selectedLanguage = ref(
  languages.value.find((lang) => lang.value === storedLocale.value) ||
    languageStore.detectBrowserLanguage(),
);
locale.value = selectedLanguage.value.value;
languageStore.setLanguage(selectedLanguage.value);

const themeSetting = useLocalStorage<"auto" | "dark" | "light">(
  "settings.theme",
  "dark",
);

const mediaMatch = window.matchMedia("(prefers-color-scheme: dark)");
const systemPrefersDark = ref(mediaMatch.matches);

function handleSystemThemeChange(event: MediaQueryListEvent) {
  systemPrefersDark.value = event.matches;
}

onMounted(() => {
  mediaMatch.addEventListener("change", handleSystemThemeChange);
});

onUnmounted(() => {
  mediaMatch.removeEventListener("change", handleSystemThemeChange);
});

const prefersDark = computed(
  () =>
    themeSetting.value === "dark" ||
    (themeSetting.value === "auto" && systemPrefersDark.value),
);

const activeThemeName = computed<"dark" | "light">(() =>
  prefersDark.value ? "dark" : "light",
);

watch(
  activeThemeName,
  (name) => {
    if (vuetifyTheme.global.name.value !== name) {
      vuetifyTheme.change(name);
    }
  },
  { immediate: true },
);

watch(
  prefersDark,
  (dark) => {
    const root = document.documentElement;
    root.classList.add("r-v2");
    root.classList.toggle("r-v2-dark", dark);
    root.classList.toggle("r-v2-light", !dark);
  },
  { immediate: true },
);
</script>

<template>
  <v-app id="application">
    <v-main id="main" class="no-transition">
      <router-view name="v2" />
    </v-main>
    <BackendStatusBanner />
  </v-app>
</template>
