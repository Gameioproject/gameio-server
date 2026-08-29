<script setup lang="ts">
// CollectionsIndex: every collection the user can see, with inline creation.
import { RSkeletonBlock, RTextField } from "@v2/lib";
import { storeToRefs } from "pinia";
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import collectionApi from "@/services/api/collection";
import storeCollections from "@/stores/collections";
import CollectionTile from "@/v2/components/Collections/CollectionTile.vue";
import NewCollectionRow from "@/v2/components/Collections/NewCollectionRow.vue";
import EmptyState from "@/v2/components/shared/EmptyState.vue";
import IndexShell from "@/v2/components/shared/IndexShell.vue";
import PageHeader from "@/v2/components/shared/PageHeader.vue";
import { useCan } from "@/v2/composables/useCan";
import { useSnackbar } from "@/v2/composables/useSnackbar";
import { useWrapGridNav } from "@/v2/composables/useWrapGridNav";

const { t } = useI18n();
const snackbar = useSnackbar();
const collectionsStore = storeCollections();
const { allCollections, fetchingCollections } = storeToRefs(collectionsStore);
const canCreate = useCan("collection.create");
const searchTerm = ref("");

const gridRoot = ref<HTMLElement | null>(null);
useWrapGridNav(gridRoot, { cellSelector: ".coll-tile" });

const visible = computed(() => {
  const term = searchTerm.value.trim().toLowerCase();
  return [...allCollections.value]
    .filter((c) => !term || c.name.toLowerCase().includes(term))
    .sort((a, b) => a.name.localeCompare(b.name));
});

const creating = ref(false);
const createExpanded = ref(false);
const newName = ref("");

async function createCollection() {
  const name = newName.value.trim();
  if (!name || creating.value) return;
  creating.value = true;
  try {
    const created = await collectionApi.createCollection({ name });
    collectionsStore.addCollection(created);
    newName.value = "";
    createExpanded.value = false;
  } catch {
    snackbar.error(t("collection.create-failed"));
  } finally {
    creating.value = false;
  }
}

onMounted(() => {
  if (allCollections.value.length === 0) {
    void collectionsStore.fetchCollections();
  }
});
</script>

<template>
  <IndexShell>
    <template #header>
      <PageHeader
        :title="t('common.collections')"
        :count="allCollections.length"
      >
        <RTextField
          v-model="searchTerm"
          class="r-v2-collections__search"
          density="compact"
          hide-details
          clearable
          prepend-inner-icon="mdi-magnify"
          :placeholder="t('common.search')"
        />
      </PageHeader>
    </template>

    <div ref="gridRoot" class="r-v2-collections">
      <NewCollectionRow
        v-if="canCreate"
        v-model:expanded="createExpanded"
        v-model:name="newName"
        :creating="creating"
        @create="createCollection"
        @cancel="createExpanded = false"
      />

      <div
        v-if="fetchingCollections && !allCollections.length"
        class="r-v2-collections__grid"
      >
        <RSkeletonBlock
          v-for="n in 8"
          :key="`cs-${n}`"
          width="150px"
          height="150px"
          rounded="card"
        />
      </div>

      <EmptyState
        v-else-if="!visible.length"
        variant="boxed"
        icon="mdi-bookmark-off-outline"
        :message="
          searchTerm
            ? t('common.no-results')
            : t('collection.no-collections-yet')
        "
      />

      <div v-else class="r-v2-collections__grid">
        <CollectionTile
          v-for="c in visible"
          :id="c.id"
          :key="c.id"
          class="coll-tile"
          :name="c.name"
          :rom-count="c.game_count ?? 0"
          :covers="c.url_covers ?? []"
          :to="`/collection/${c.id}`"
          :is-public="c.is_public"
          variant="row"
        />
      </div>
    </div>
  </IndexShell>
</template>

<style scoped>
.r-v2-collections {
  display: flex;
  flex-direction: column;
  gap: var(--r-space-5);
  padding: var(--r-space-4) var(--r-row-pad) 60px;
}

.r-v2-collections__grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--r-space-4);
}

.r-v2-collections__search {
  min-width: 220px;
}
</style>
