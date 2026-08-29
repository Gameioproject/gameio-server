<script setup lang="ts">
import { useI18n } from "vue-i18n";
import DownloadHostsSection from "@/v2/components/Settings/DownloadHostsSection.vue";
import { usePageTitle } from "@/v2/composables/usePageTitle";

const { t } = useI18n();
usePageTitle(() => t("catalog.hosts-title"));
</script>

<template>
  <DownloadHostsSection />
</template>
