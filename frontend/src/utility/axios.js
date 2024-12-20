import axios from 'axios';
import { LOGOUT_SUCCESS, LOGIN_SUCCESS, REFRESH_SUCCESS } from '../actions/types';
import store from '../store';
import { tokenConfig } from '../actions/auth'; // Assuming tokenConfig is defined for access token setup

// Create Axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request Interceptor
api.interceptors.request.use(
  (config) => {
    const state = store.getState();
    const token = state.auth?.access;
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Check for 401 Unauthorized and retry with refreshed token
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url.endsWith('/auth/logout/')) {
      originalRequest._retry = true; // Prevent infinite retry loop

      try {
        const refreshToken = store.getState().auth?.refresh;

        if (!refreshToken) {
            store.dispatch({ type: LOGOUT_SUCCESS });
            return Promise.reject(error);
        }

        // Refresh token API call
        const res = await axios.post('http://localhost:8000/api/auth/refresh/', {
          refresh: refreshToken,
        }, )
        console.log("refresh res", res.data);

        // Update tokens in Redux store
        store.dispatch({
          type: REFRESH_SUCCESS,
          payload: res.data, // Assuming the API returns new access and refresh tokens
        });

        // Retry the original request with the new token
        originalRequest.headers['Authorization'] = `Bearer ${res.data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh token fails, logout the user
        store.dispatch({ type: LOGOUT_SUCCESS });
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
