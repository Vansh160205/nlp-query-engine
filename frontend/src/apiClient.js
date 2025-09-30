import axios from 'axios';

// Centralize API configuration
const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

export default apiClient;
