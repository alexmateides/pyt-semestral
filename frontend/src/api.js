// src/api.js
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'api-key': 'TEST',
        'Content-Type': 'application/json',
    },
});

export default api;
