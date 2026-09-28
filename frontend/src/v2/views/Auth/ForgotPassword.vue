<script setup lang="ts">
// The launcher sends people straight here, and the web sign-in the reset
// request used to live behind is not reachable on the hosted service.
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import identityApi from "@/services/api/identity";

const { t } = useI18n();

const username = ref("");
const sending = ref(false);
const sent = ref(false);
const failed = ref(false);

async function submit() {
  if (!username.value) return;
  sending.value = true;
  failed.value = false;
  try {
    await identityApi.requestPasswordReset(username.value);
    username.value = "";
    sent.value = true;
  } catch (error) {
    console.error("Error sending reset link: ", error);
    failed.value = true;
  } finally {
    sending.value = false;
  }
}

function leave() {
  window.location.href = "/";
}
</script>

<template>
  <h1 class="g-title">{{ t("login.forgot-password") }}</h1>

  <div v-if="sent" class="g-form">
    <p class="g-status" data-kind="done" role="status">
      {{ t("login.reset-sent") }}
    </p>
    <button class="g-btn" type="button" @click="leave">
      {{ t("common.close") }}
    </button>
  </div>

  <form v-else class="g-form" @submit.prevent="submit">
    <label class="g-field" for="g-username">
      {{ t("login.username") }}
      <input
        id="g-username"
        v-model="username"
        type="text"
        autocomplete="username"
        autocapitalize="none"
        required
        :disabled="sending"
      />
    </label>
    <button class="g-btn" type="submit" :disabled="sending || !username">
      {{ t("login.send-reset-link") }}
    </button>
    <button class="g-btn g-btn--quiet" type="button" @click="leave">
      {{ t("common.cancel") }}
    </button>
    <p class="g-status" data-kind="error" role="status" aria-live="polite">
      {{ failed ? t("login.reset-link-failed") : "" }}
    </p>
  </form>
</template>
