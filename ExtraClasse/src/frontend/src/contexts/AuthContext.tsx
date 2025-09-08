import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { User } from '../types'; // Importe sua interface User

// 1. Atualizamos a "forma" do contexto
interface AuthContextType {
  isLogged: boolean; 
  user: User | null;
  login: (userData: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLogged, setisLogged] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  // useEffect para carregar o estado do localStorage ao iniciar
  // Em: src/contexts/AuthContext.tsx

// ...

  // useEffect para carregar o estado do localStorage ao iniciar
  useEffect(() => {
    try {
      const storedUser = localStorage.getItem("user");
      
      // Verificação de segurança: só continue se storedUser não for nulo ou indefinido
      if (storedUser) {
        const userData: User = JSON.parse(storedUser);
        setUser(userData);
        setisLogged(true);
      }
    } catch (error) {
      console.error("Falha ao ler o usuário do localStorage", error);
      // Garante que o estado fique limpo se houver um erro
      localStorage.removeItem("user"); 
    }
  }, []);

// ...
  // Função para realizar o login
  const login = (userData: User) => {
    localStorage.setItem("user", JSON.stringify(userData)); // Salva o usuário como texto
    setUser(userData);
    setisLogged(true);
  };

  // Função para realizar o logout
  const logout = () => {
    localStorage.removeItem("user");
    setUser(null);
    setisLogged(false);
  };

  const value = {
    isLogged,
    user,
    login,
    logout,
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
