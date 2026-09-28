<script setup lang="ts">
// ForgotPassword — the reset request on a page of its own.
// The launcher sends people straight here, and the web sign-in this form used
// to live behind is not reachable on the hosted service.
import { RAlert, RBtn } from "@v2/lib";
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import ResetForm from "@/v2/components/Auth/ResetForm.vue";
import AuthCard from "@/v2/components/shared/AuthCard.vue";

const { t } = useI18n();
const sent = ref(false);

function leave() {
  window.location.href = "/";
}
</script>

<template>
  <AuthCard>
    <h1 class="r-v2-forgot__title">{{ t("login.reset-password") }}</h1>

    <template v-if="sent">
      <RAlert type="success" density="compact" :text="t('login.reset-sent')" />
      <RBtn class="r-v2-forgot__back" variant="flat" color="primary" block @click="leave">
        {{ t("common.close") }}
      </RBtn>
    </template>

    <ResetForm v-else @done="sent = true" @cancel="leave" />
  </AuthCard>
</template>

<style scoped>
.r-v2-forgot__title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  text-align: center;
}

.r-v2-forgot__back {
  margin-top: 1rem;
}
</style>
