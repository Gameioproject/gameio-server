import { defineStore } from "pinia";
import type { CollectionSchema } from "@/__generated__";
import collectionApi from "@/services/api/collection";

export type Collection = CollectionSchema;

export default defineStore("collections", {
  state: () => ({
    allCollections: [] as Collection[],
    fetchingCollections: false,
  }),

  getters: {
    favoriteCollection: (state) =>
      state.allCollections.find((c) => c.is_favorite),
  },

  actions: {
    async fetchCollections() {
      this.fetchingCollections = true;
      try {
        const { data } = await collectionApi.getCollections();
        this.allCollections = data;
      } finally {
        this.fetchingCollections = false;
      }
    },
    async refreshCollection(id: number): Promise<Collection | null> {
      try {
        const { data } = await collectionApi.getCollection(id);
        this.updateCollection(data);
        return data;
      } catch {
        return null;
      }
    },
    addCollection(collection: Collection) {
      if (!this.allCollections.some((c) => c.id === collection.id)) {
        this.allCollections.push(collection);
      }
    },
    updateCollection(collection: Collection) {
      const index = this.allCollections.findIndex(
        (c) => c.id === collection.id,
      );
      if (index === -1) this.allCollections.push(collection);
      else this.allCollections[index] = collection;
    },
    removeCollection(collection: Collection) {
      this.allCollections = this.allCollections.filter(
        (c) => c.id !== collection.id,
      );
    },
    getCollection(id: number) {
      return this.allCollections.find((c) => c.id === id);
    },
    reset() {
      this.allCollections = [];
      this.fetchingCollections = false;
    },
  },
});
