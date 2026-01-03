import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 401 || status === 422) {
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
};

// User API
export const userAPI = {
  getProfile: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/users/profile', data),
  deleteAccount: () => api.delete('/users/profile'),
};

// City API
export const cityAPI = {
  search: (params) => api.get('/cities/search', { params }),
  getById: (id) => api.get(`/cities/${id}`),
  getAIInfo: (id) => api.get(`/cities/${id}/info`),
  getPopular: (limit = 10) => api.get('/popular-cities', { params: { limit } }),
};

// Activity API
export const activityAPI = {
  search: (params) => api.get('/activities/search', { params }),
  suggest: (data) => api.post('/activities/suggest', data),
};

// Trip API
export const tripAPI = {
  getAll: () => api.get('/trips'),
  getById: (id) => api.get(`/trips/${id}`),
  create: (data) => api.post('/trips', data),
  update: (id, data) => api.put(`/trips/${id}`, data),
  delete: (id) => api.delete(`/trips/${id}`),
  generateItinerary: (id, data) => api.post(`/trips/${id}/generate-itinerary`, data),
  getShared: (shareCode) => api.get(`/trips/shared/${shareCode}`),
  copy: (id) => api.post(`/trips/${id}/copy`),
};

// Stop API
export const stopAPI = {
  add: (tripId, data) => api.post(`/trips/${tripId}/stops`, data),
  update: (id, data) => api.put(`/stops/${id}`, data),
  delete: (id) => api.delete(`/stops/${id}`),
  addActivity: (stopId, data) => api.post(`/stops/${stopId}/activities`, data),
};

// Itinerary Activity API
export const itineraryActivityAPI = {
  remove: (id) => api.delete(`/itinerary-activities/${id}`),
};

// Budget API
export const budgetAPI = {
  get: (tripId) => api.get(`/trips/${tripId}/budget`),
  update: (tripId, data) => api.put(`/trips/${tripId}/budget`, data),
};

// Saved Destinations API
export const savedDestinationsAPI = {
  getAll: () => api.get('/saved-destinations'),
  save: (cityId) => api.post('/saved-destinations', { city_id: cityId }),
  remove: (id) => api.delete(`/saved-destinations/${id}`),
};

// Dashboard API
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
};

export default api;
