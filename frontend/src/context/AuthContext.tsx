import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from 'firebase/auth';

// TODO: Replace mock auth with Firebase implementation
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

type AuthState = {
  user: User | null;
  isLoading: boolean;
};

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  signInWithGoogle: () => Promise<User | null>;
  logout: () => Promise<void>;
  getToken: () => Promise<string | null>;
  setAuth?: React.Dispatch<React.SetStateAction<AuthState>>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  signInWithGoogle: async () => null,
  logout: async () => {},
  getToken: async () => null,
});

export function AuthProvider({ children, value }: { children: React.ReactNode, value?: AuthContextType }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  if (value) {
    return (
      <AuthContext.Provider value={value}>
        {children}
      </AuthContext.Provider>
    );
  }

  useEffect(() => {
    setTimeout(() => {
      const mockUser = {
        uid: 'mock-uid',
        email: 'user@example.com',
        displayName: 'Test User',
        photoURL: '',
        getIdToken: async () => 'mock-token',
      } as User;

      setUser(mockUser);
      setIsLoading(false);
    }, 1000);
  }, []);

  const signInWithGoogle = async (): Promise<User | null> => {
    const mockUser = {
      uid: 'mock-uid',
      email: 'user@example.com',
      displayName: 'Test User',
      photoURL: '',
      getIdToken: async () => 'mock-token',
    } as User;

    setUser(mockUser);
    return mockUser;
  };

  const logout = async (): Promise<void> => {
    setUser(null);
  };

  const getToken = async (): Promise<string | null> => {
    if (!user) return null;
    return 'mock-token';
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, signInWithGoogle, logout, getToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
