<script setup lang="ts">
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { refetchCSRFToken } from "@/services/api";
import identityApi from "@/services/api/identity";
import storeAuth from "@/stores/auth";

const { t } = useI18n();
const authStore = storeAuth();
const route = useRoute();
const router = useRouter();
const token = route.query.token as string;

const newPassword = ref("");
const confirmPassword = ref("");
const submitting = ref(false);
const failure = ref("");

const passwordsMismatch = computed(
  () =>
    newPassword.value.length > 0 &&
    confirmPassword.value.length > 0 &&
    newPassword.value !== confirmPassword.value,
);

const status = computed(() =>
  passwordsMismatch.value ? t("login.passwords-do-not-match") : failure.value,
);

async function resetPassword() {
  if (passwordsMismatch.value || !newPassword.value) return;
  submitting.value = true;
  failure.value = "";
  try {
    await identityApi.resetPassword(token, newPassword.value);
    await refetchCSRFToken();
    try {
      await authStore.fetchCurrentUser();
    } catch (error) {
      console.error("Error setting a new password: ", error);
    }
    const params = new URLSearchParams(window.location.search);
    router.push(params.get("next") ?? "/");
  } catch (err: unknown) {
    const { response, message } = err as {
      response?: {
        data?: { detail?: string };
        statusText?: string;
        status?: number;
      };
      message?: string;
    };
    const errorMessage =
      response?.data?.detail ||
      message ||
      response?.statusText ||
      t("login.reset-failed");
    failure.value = t("login.unable-to-reset-password", {
      error: errorMessage,
    });
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <h1 class="g-title">{{ t("login.reset-password") }}</h1>
  <form class="g-form" @submit.prevent="resetPassword">
    <label class="g-field" for="g-new-password">
      {{ t("login.new-password") }}
      <input
        id="g-new-password"
        v-model="newPassword"
        type="password"
        autocomplete="new-password"
        required
        :disabled="submitting"
      />
    </label>
    <label class="g-field" for="g-confirm-password">
      {{ t("login.confirm-new-password") }}
      <input
        id="g-confirm-password"
        v-model="confirmPassword"
        type="password"
        autocomplete="new-password"
        required
        :disabled="submitting"
      />
    </label>

    <button
      class="g-btn"
      type="submit"
      :disabled="
        submitting || passwordsMismatch || !newPassword || !confirmPassword
      "
    >
      {{ t("login.reset-password") }}
    </button>

    <p class="g-status" data-kind="error" role="status" aria-live="polite">
      {{ status }}
    </p>
  </form>
</template>
