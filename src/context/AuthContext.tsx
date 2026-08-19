import React, { createContext, useContext, useState } from 'react';

export interface User {
  id: string;
  organization_id: string;
  full_name: string;
  email: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (emailOrToken: string, passwordOrRefresh?: string, userOrRemember?: any) => Promise<void> | void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user_data');
    return saved ? JSON.parse(saved) : null;
  });

  const login = async (arg1: string, arg2?: string, arg3?: any) => {
    let accessToken = arg1;
    let refreshToken = arg2 || '';
    let userData: User = typeof arg3 === 'object' && arg3 !== null ? arg3 : {
      id: 'usr_default',
      organization_id: 'org_default',
      full_name: arg1 ? arg1.split('@')[0] : 'Executive User',
      email: arg1.includes('@') ? arg1 : 'executive@organization.com',
      role: 'SYSTEM_ADMIN'
    };

    if (arg1.includes('@')) {
      // Credentials login mock or real token setting
      accessToken = 'demo_token_' + Date.now();
      refreshToken = 'demo_refresh_' + Date.now();
    }

    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    localStorage.setItem('user_data', JSON.stringify(userData));
    setToken(accessToken);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
