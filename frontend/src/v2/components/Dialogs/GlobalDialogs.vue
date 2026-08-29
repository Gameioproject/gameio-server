<script setup lang="ts">
// GlobalDialogs — app-wide overlays mounted once in AppLayout so any view
// can raise them through the emitter.
import AboutDialog from "@/v2/components/Dialogs/AboutDialog.vue";
import ChangelogDialog from "@/v2/components/Dialogs/ChangelogDialog.vue";
import NewVersionBanner from "@/v2/components/Notifications/NewVersionBanner.vue";
import NotificationHost from "@/v2/components/Notifications/NotificationHost.vue";
import ConfirmDialog from "@/v2/components/shared/ConfirmDialog.vue";
</script>

<template>
  <NotificationHost />
  <NewVersionBanner />
  <ConfirmDialog />
  <AboutDialog />
  <ChangelogDialog />
</template>
