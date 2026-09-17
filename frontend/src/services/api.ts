import axios from 'axios';
import { HealthStatus, DbHealthStatus } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor to attach JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const systemApi = {
  checkHealth: async (): Promise<HealthStatus> => {
    const res = await apiClient.get<HealthStatus>('/health/');
    return res.data;
  },
  checkDbHealth: async (): Promise<DbHealthStatus> => {
    const res = await apiClient.get<DbHealthStatus>('/health/db');
    return res.data;
  },
};
