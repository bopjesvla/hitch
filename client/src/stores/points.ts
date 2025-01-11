import { defineStore } from 'pinia';
import { ref, computed, shallowRef } from 'vue';
import axios from 'axios';

export type Point = {
  ID: number;
  Latitude: number;
  Longitude: number;
  Rating: number;
  Duration: number;
  ReviewCount: number;
  Reviews: Review[];
  CreatedAt: Date;
};

type PointInput = {
  Latitude: number;
  Longitude: number;
};

type Review = {
  ID: number;
  Rating: number;
  Duration: number;
  Comment: string;
  Name: string;
  PointId: number;
  CreatedAt: Date;
};

type ReviewInput = {
  Rating: number;
  Duration?: number;
  Comment?: string;
  Name?: string;
  PointId?: number;
};

export const usePointsStore = defineStore('points', () => {
  const isLoading = ref(false);
  const isSubmitting = ref(false);
  const items = shallowRef<Point[]>([]);
  const selectedPoint = ref<Point | undefined>(undefined);

  const getSelectedPoint = computed(() => selectedPoint.value);

  const fetchPoints = async (params: { bounds?: L.LatLngBounds } | null = null) => {
    isLoading.value = true;

    const response = await axios.get('http://localhost:5000/api/v1/points', {
      params: {
        ...params,
        bounds: params?.bounds ? JSON.stringify(params.bounds) : undefined,
      },
    });
    items.value = response.data as Point[];

    isLoading.value = false;
  };

  const selectPoint = (point: Point) => {
    selectedPoint.value = point;
  };

  const createPoint = async (
    pointInput: PointInput & {
      Review: ReviewInput;
    },
  ) => {
    isSubmitting.value = true;

    const response = await axios.post('http://localhost:5000/api/v1/points', pointInput);
    items.value = [...items.value, response.data];

    isSubmitting.value = false;
    return response.data;
  };

  const createReview = async (reviewInput: ReviewInput) => {
    isSubmitting.value = true;

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

    isSubmitting.value = false;
    return response.data;
  };

  const markDuplicate = async (point: Point) => {
    if (!selectedPoint.value) {
      return alert('There was an error.');
    }

    isSubmitting.value = true;

    await axios.post(`http://localhost:5000/api/v1/points/${selectedPoint.value.ID}/duplicate`, {
      duplicateId: point.ID,
    });

    isSubmitting.value = false;
  };

  return {
    isLoading,
    isSubmitting,
    items,
    selectedPoint,
    getSelectedPoint,
    fetchPoints,
    selectPoint,
    createPoint,
    createReview,
    markDuplicate,
  };
});
