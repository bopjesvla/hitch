import { defineStore } from 'pinia';
import { ref, computed, shallowRef } from 'vue';
import axios from 'axios';

type Point = {
  ID: number;
  Latitude: number;
  Longitude: number;
  Rating: number;
  Duration: number;
  ReviewCount: number;
  Reviews: Review[];
};

type PointInput = {
  Latitude: number;
  Longitude: number;
};

type Review = {
  ID: number;
  // TODO: Remaining attributes
};

type ReviewInput = {
  Rating: number;
  Duration: number;
  Comment: string;
  Name: string;
  PointId: number;
};

export const usePointsStore = defineStore('points', () => {
  const loading = ref(false);
  const items = shallowRef<Point[]>([]);
  const selectedPoint = ref<Point | undefined>(undefined);

  const getSelectedPoint = computed(() => selectedPoint.value);

  const fetchPoints = async () => {
    loading.value = true;

    const response = await axios.get('http://localhost:5000/api/v1/points');
    items.value = response.data as Point[];

    loading.value = false;
  };

  const selectPoint = (point: Point) => {
    selectedPoint.value = point;
  };

  const createPoint = async (
    pointInput: PointInput & {
      Review: ReviewInput;
    },
  ) => {
    loading.value = true;

    const response = await axios.post('http://localhost:5000/api/v1/points', pointInput);
    items.value = [...items.value, response.data];

    loading.value = false;
    return response.data;
  };

  const createReview = async (reviewInput: ReviewInput) => {
    loading.value = true;

    const response = await axios.post(
      `http://localhost:5000/api/v1/points/${reviewInput.PointId}/review`,
      reviewInput,
    );

    const pointIndex = items.value.findIndex((p) => p.ID === response.data.PointId);
    const point = items.value[pointIndex];

    point.Reviews = [...(point.Reviews || []), response.data];
    point.Rating = Math.round(
      point.Rating + (response.data.Rating - point.Rating) / (point.ReviewCount + 1),
    );

    loading.value = false;
    return response.data;
  };

  return {
    loading,
    items,
    selectedPoint,
    getSelectedPoint,
    fetchPoints,
    selectPoint,
    createPoint,
    createReview,
  };
});
