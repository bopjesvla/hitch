<template>
  <div v-if="isSidebarOpen && currentComponent" class="Sidebar" :class="sidebarClass">
    <a class="Sidebar__Close" @click="uiStore.closeSidebar">
      <svg width="14" height="14" version="1.1" xmlns="http://www.w3.org/2000/svg">
        <line x1="1" y1="13" x2="13" y2="1" stroke="black" stroke-width="2"></line>
        <line x1="1" y1="1" x2="13" y2="13" stroke="black" stroke-width="2"></line>
      </svg>
    </a>
    <component :is="MenuViews[currentComponent as keyof typeof MenuViews]" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { storeToRefs } from 'pinia';

import { useUiStore } from '@/stores/ui';

// Import your components here
import Menu from './Views/Menu.vue';
import ViewSpot from './Views/ViewSpot.vue';
import AddSpotForm from './Views/AddSpotForm.vue';
// import SpotFormContainer from '@/components/SpotFormContainer.vue';
// import ShowSpot from '@/components/ShowSpot.vue';
// import SuccessMessage from '@/components/SuccessMessage.vue';
// import SuccessDuplicateMessage from '@/components/SuccessDuplicateMessage.vue';
const uiStore = useUiStore();

const MenuViews = {
  Menu,
  ViewSpot,
  AddSpotForm,
};

const isSpotFormContainer = ref(false);
const isShowSpot = ref(false);
const isSuccess = ref(false);
const isSuccessDuplicate = ref(false);
const isMenu = ref(false);

const sidebarClass = computed(() => ({
  'spot-form-container': isSpotFormContainer.value,
  'show-spot': isShowSpot.value,
  success: isSuccess.value,
  'success-duplicate': isSuccessDuplicate.value,
  menu: isMenu.value,
}));

const { isSidebarOpen, currentComponent } = storeToRefs(uiStore);
</script>

<style scoped>
/* Add your styles here */
.Sidebar {
  @apply fixed right-0 top-0 bottom-0 w-96 max-w-full p-6 bg-white text-black shadow-lg overflow-y-auto z-50;
}

.Sidebar__Close {
  @apply absolute top-6 right-6 border-none cursor-pointer;
}

.spot-form-container {
  @apply p-4;
}
.show-spot {
  @apply p-4;
}
.success {
  @apply p-4;
}
.success-duplicate {
  @apply p-4;
}
.menu {
  @apply p-4;
}
</style>
