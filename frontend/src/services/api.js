import axios from 'axios';

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeProject = async (data) => {
  try {
    const response = await api.post('/analyze-project', data);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Analysis failed. Please check the server.');
    }
    throw new Error('Network error. Ensure the FastAPI backend is running.');
  }
};
