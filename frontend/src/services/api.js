import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health & Status
export const getHealth = () => api.get('/health');

// Usuarios
export const getUsuarios = (params) => api.get('/usuarios/', { params });
export const getUsuario = (id) => api.get(`/usuarios/${id}`);
export const createUsuario = (data) => api.post('/usuarios/', data);
export const updateUsuario = (id, data) => api.put(`/usuarios/${id}`, data);
export const deleteUsuario = (id) => api.delete(`/usuarios/${id}`);

// Estabelecimentos
export const getEstabelecimentos = (params) => api.get('/estabelecimentos/', { params });
export const getEstabelecimento = (id) => api.get(`/estabelecimentos/${id}`);
export const createEstabelecimento = (data) => api.post('/estabelecimentos/', data);
export const updateEstabelecimento = (id, data) => api.put(`/estabelecimentos/${id}`, data);
export const deleteEstabelecimento = (id) => api.delete(`/estabelecimentos/${id}`);

// Preferencias
export const getPreferencias = (params) => api.get('/preferencias/', { params });
export const getPreferencia = (id) => api.get(`/preferencias/${id}`);
export const createPreferencia = (data) => api.post('/preferencias/', data);
export const updatePreferencia = (id, data) => api.put(`/preferencias/${id}`, data);
export const deletePreferencia = (id) => api.delete(`/preferencias/${id}`);

// Universidades
export const getUniversidades = (params) => api.get('/universidades/', { params });
export const getUniversidade = (id) => api.get(`/universidades/${id}`);
export const createUniversidade = (data) => api.post('/universidades/', data);
export const updateUniversidade = (id, data) => api.put(`/universidades/${id}`, data);
export const deleteUniversidade = (id) => api.delete(`/universidades/${id}`);

// Categorias
export const getCategorias = (params) => api.get('/categorias-estabelecimentos/', { params });
export const getCategoria = (id) => api.get(`/categorias-estabelecimentos/${id}`);
export const createCategoria = (data) => api.post('/categorias-estabelecimentos/', data);
export const updateCategoria = (id, data) => api.put(`/categorias-estabelecimentos/${id}`, data);
export const deleteCategoria = (id) => api.delete(`/categorias-estabelecimentos/${id}`);

// Usuario-Preferencias
export const getUsuarioPreferencias = (params) => api.get('/usuario-preferencias/', { params });
export const createUsuarioPreferencia = (data) => api.post('/usuario-preferencias/', data);
export const updateUsuarioPreferencia = (id, data) => api.put(`/usuario-preferencias/${id}`, data);
export const deleteUsuarioPreferencia = (id) => api.delete(`/usuario-preferencias/${id}`);

// Estabelecimento-Preferencias
export const getEstabelecimentoPreferencias = (params) => api.get('/estabelecimento-preferencias/', { params });
export const createEstabelecimentoPreferencia = (data) => api.post('/estabelecimento-preferencias/', data);
export const updateEstabelecimentoPreferencia = (id, data) => api.put(`/estabelecimento-preferencias/${id}`, data);
export const deleteEstabelecimentoPreferencia = (id) => api.delete(`/estabelecimento-preferencias/${id}`);

// Recomendacoes
export const getRecomendacoes = (usuarioId, params) => api.get(`/recomendacoes/usuario/${usuarioId}`, { params });
export const treinarModelo = (data) => api.post('/recomendacoes/treinar', data);
export const registrarInteracao = (data) => api.post('/recomendacoes/interacao', data);
export const getColdStartUsuario = (usuarioId, params) => api.get(`/recomendacoes/cold-start/usuario/${usuarioId}`, { params });
export const compararAlgoritmos = (usuarioId, params) => api.get(`/recomendacoes/comparar/${usuarioId}`, { params });

export default api;

