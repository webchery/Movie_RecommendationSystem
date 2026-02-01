import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:5000/api',
    withCredentials: true // 关键：允许跨域携带 Session
});
export default api;
export const getHome = () => api.get('/movies/home');
export const getDetail = (id) => api.get(`/movies/detail/${id}`);
export const login = (data) => api.post('/auth/login', data);
export const getFootprints = () => api.get('/user/footprints');