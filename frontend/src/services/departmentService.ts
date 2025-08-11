import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Department {
  id: string;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DepartmentCreate {
  name: string;
  code: string;
  description?: string;
  is_active?: boolean;
}

class DepartmentService {
  private baseURL = `${API_URL}/departments`;

  async getDepartments(): Promise<Department[]> {
    const token = localStorage.getItem('token');
    const response = await axios.get(this.baseURL, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  }

  async getDepartment(id: string): Promise<Department> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${this.baseURL}/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  }

  async createDepartment(department: DepartmentCreate): Promise<Department> {
    const token = localStorage.getItem('token');
    const response = await axios.post(this.baseURL, department, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  }

  async updateDepartment(id: string, department: Partial<DepartmentCreate>): Promise<Department> {
    const token = localStorage.getItem('token');
    const response = await axios.put(`${this.baseURL}/${id}`, department, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  }

  async deleteDepartment(id: string): Promise<void> {
    const token = localStorage.getItem('token');
    await axios.delete(`${this.baseURL}/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
  }
}

export const departmentService = new DepartmentService();
