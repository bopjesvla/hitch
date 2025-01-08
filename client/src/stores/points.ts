import { defineStore } from 'pinia';
import { ref, computed, shallowRef } from 'vue';
import axios from 'axios';

type Point = {
  ID: number;
  Latitude: number;
  Longitude: number;
  rating: number;
  wait: number;
};

export const usePointsStore = defineStore('points', () => {
  const loading = ref(false);
  const items = shallowRef<Point[]>([]);
  const selectedPoint = ref<Point | undefined>(undefined);

  const getSelectedPoint = computed(() => selectedPoint.value);

  const fetchPoints = async () => {
    loading.value = true;

    const response = await axios.get('http://localhost:5000/api/v1/points');
    items.value = JSON.parse(response.data) as Point[];

    loading.value = false;
  };

  const selectPoint = (point: Point) => {
    selectedPoint.value = point;
  };

  const createPoint = (point: Point) => {
    items.value.push(point);
  };

  return {
    loading,
    items,
    selectedPoint,
    getSelectedPoint,
    fetchPoints,
    selectPoint,
    createPoint,
  };
});
