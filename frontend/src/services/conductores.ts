/**
 * Servicio para gestión de conductores
 */
import { api } from './api';

export interface Conductor {
  id: string;
  dni: string;
  nombres: string;
  apellidos: string;
  fecha_nacimiento: string;
  direccion: string;
  telefono: string;
  email: string;
  licencia_numero: string;
  licencia_categoria: string;
  licencia_emision: string;
  licencia_vencimiento: string;
  certificado_medico_numero?: string;
  certificado_medico_vencimiento?: string;
  empresa_id: string;
  empresa?: {
    id: string;
    razon_social: string;
    ruc: string;
  };
  estado: 'pendiente' | 'habilitado' | 'observado' | 'suspendido' | 'revocado';
  created_at: string;
  updated_at: string;
}

export interface ConductorCreate {
  dni: string;
  nombres: string;
  apellidos: string;
  fecha_nacimiento: string;
  direccion: string;
  telefono: string;
  email: string;
  licencia_numero: string;
  licencia_categoria: string;
  licencia_emision: string;
  licencia_vencimiento: string;
  certificado_medico_numero?: string;
  certificado_medico_vencimiento?: string;
  empresa_id: string;
}

export interface ConductoresResponse {
  items: Conductor[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export const conductoresService = {
  /**
   * Obtener lista de conductores con paginación y filtros
   */
  async getAll(params?: {
    page?: number;
    size?: number;
    empresa_id?: string;
    estado?: string;
    search?: string;
  }): Promise<ConductoresResponse> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.size) queryParams.append('size', params.size.toString());
    if (params?.empresa_id) queryParams.append('empresa_id', params.empresa_id);
    if (params?.estado) queryParams.append('estado', params.estado);
    if (params?.search) queryParams.append('search', params.search);

    const query = queryParams.toString();
    return api.get<ConductoresResponse>(`/conductores${query ? `?${query}` : ''}`);
  },

  /**
   * Obtener un conductor por ID
   */
  async getById(id: string): Promise<Conductor> {
    return api.get<Conductor>(`/conductores/${id}`);
  },

  /**
   * Crear un nuevo conductor
   */
  async create(data: ConductorCreate): Promise<Conductor> {
    return api.post<Conductor>('/conductores', data);
  },

  /**
   * Actualizar un conductor
   */
  async update(id: string, data: Partial<ConductorCreate>): Promise<Conductor> {
    return api.put<Conductor>(`/conductores/${id}`, data);
  },

  /**
   * Eliminar un conductor (soft delete)
   */
  async delete(id: string): Promise<void> {
    return api.delete<void>(`/conductores/${id}`);
  },
};
