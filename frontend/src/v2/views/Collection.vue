<script setup lang="ts">
// Collection: the catalog games in one collection.
import { RBtn, RDivider } from "@v2/lib";
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { ROUTES } from "@/plugins/router";
import collectionApi from "@/services/api/collection";
import storeCollections from "@/stores/collections";
import CatalogGrid from "@/v2/components/Catalog/CatalogGrid.vue";
import EmptyState from "@/v2/components/shared/EmptyState.vue";
import IndexShell from "@/v2/components/shared/IndexShell.vue";
import PageHeader from "@/v2/components/shared/PageHeader.vue";
import { useCan } from "@/v2/composables/useCan";
import { useConfirm } from "@/v2/composables/useConfirm";
import { useIsAlive } from "@/v2/composables/useIsAlive";
import { usePageTitle } from "@/v2/composables/usePageTitle";
import { useSnackbar } from "@/v2/composables/useSnackbar";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const alive = useIsAlive();
const confirm = useConfirm();
const snackbar = useSnackbar();
const collectionsStore = storeCollections();
const canDelete = useCan("collection.delete");

const collectionId = computed(() => Number(route.params.collection));
const collection = computed(() =>
  collectionsStore.getCollection(collectionId.value),
);
const missing = ref(false);
const total = ref(0);

usePageTitle(() => collection.value?.name ?? null);

async function load() {
  missing.value = false;
  const found = await collectionsStore.refreshCollection(collectionId.value);
  if (alive.value && !found) missing.value = true;
}

onMounted(load);
watch(collectionId, load);

const query = computed(() => ({
  collectionId: collectionId.value,
  orderBy: "name" as const,
  orderDir: "asc" as const,
}));

const deleting = ref(false);

async function remove() {
  const c = collection.value;
  if (!c) return;
  const ok = await confirm({
    title: t("collection.delete-collection"),
    body: t("collection.delete-body", { name: c.name }),
    confirmText: t("common.delete"),
    tone: "danger",
  });
  if (!ok) return;
  deleting.value = true;
  try {
    await collectionApi.deleteCollection({ id: c.id });
    collectionsStore.removeCollection(c);
    void router.push({ name: ROUTES.COLLECTIONS_INDEX });
  } catch {
    if (alive.value) snackbar.error(t("collection.delete-failed"));
  } finally {
    if (alive.value) deleting.value = false;
  }
}
</script>

<template>
  <IndexShell>
    <template #header>
      <PageHeader :title="collection?.name ?? ''" :count="total">
        <RBtn
          v-if="collection && canDelete && !collection.is_favorite"
          class="r-v2-coll__delete"
          variant="text"
          prepend-icon="mdi-delete-outline"
          :loading="deleting"
          @click="remove"
        >
          {{ t("common.delete") }}
        </RBtn>
      </PageHeader>
      <p v-if="collection?.description" class="r-v2-coll__desc">
        {{ collection.description }}
      </p>
      <RDivider class="r-v2-coll__divider" />
    </template>

    <EmptyState
      v-if="missing"
      icon="mdi-bookmark-off-outline"
      :message="t('collection.not-found')"
    />
    <CatalogGrid
      v-else
      :query="query"
      :collection-id="collectionId"
      empty-icon="mdi-bookmark-outline"
      :empty-message="t('collection.empty')"
      @update:total="total = $event"
    />
  </IndexShell>
</template>

<style scoped>
.r-v2-coll__delete {
  margin-left: auto;
}

.r-v2-coll__desc {
  margin: -12px 0 0;
  padding-bottom: var(--r-space-4);
  font-size: 13.5px;
  color: var(--r-color-fg-muted);
}

.r-v2-coll__divider {
  margin-bottom: var(--r-space-4);
}
</style>
