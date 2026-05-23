import request from './index'

export const projectsApi = {
  list: (params?: { project_type?: string; status?: string }) => request.get('/api/v1/projects', { params }),
  get: (id: string) => request.get(`/api/v1/projects/${id}`),
  create: (data: any) => request.post('/api/v1/projects', data),
  update: (id: string, data: any) => request.put(`/api/v1/projects/${id}`, data),
  delete: (id: string) => request.delete(`/api/v1/projects/${id}`),
}
