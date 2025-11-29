import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '@/lib/api';

interface User {
  user_id: string;
  email: string;
  full_name: string;
  organisation_id: string;
  role: string;
  created_at: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string, orgId: string, role?: string) => Promise<void>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }

    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setError(null);
      setIsLoading(true);

      const response = await fetch(API_ENDPOINTS.login, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();

      // Save to state and localStorage
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Navigate to dashboard
      navigate('/dashboard');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (
    email: string,
    password: string,
    fullName: string,
    orgId: string = 'org_001',
    role: string = 'user'
  ) => {
    try {
      setError(null);
      setIsLoading(true);

      const response = await fetch(API_ENDPOINTS.register, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
          organisation_id: orgId,
          role: role,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      const data = await response.json();

      // Save to state and localStorage
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Navigate to dashboard
      navigate('/dashboard');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Registration failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const value = {
    user,
    token,
    isAuthenticated: !!token,
    isLoading,
    login,
    register,
    logout,
    error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
