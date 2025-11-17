/**
 * Servicio para gestión de empresas
 */
import { api } from './api';

export interface Empresa {
  id: string;
  ruc: string;
  razon_social: string;
  direccion: string;
  telefono: string;
  email: string;
  activo: boolean;
}

export interface EmpresasResponse {
  items: Empresa[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export const empresasService = {
  /**
   * Obtener lista de empresas activas
   */
  async getAll(params?: {
    page?: number;
    size?: number;
    activo?: boolean;
  }): Promise<EmpresasResponse> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.size) queryParams.append('size', params.size.toString());
    if (params?.activo !== undefined) queryParams.append('activo', params.activo.toString());

    const query = queryParams.toString();
    return api.get<EmpresasResponse>(`/empresas${query ? `?${query}` : ''}`);
  },

  /**
   * Obtener una empresa por ID
   */
  async getById(id: string): Promise<Empresa> {
    return api.get<Empresa>(`/empresas/${id}`);
  },
};
