import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createRouter } from '@tanstack/react-router';
import { ChakraProvider } from '@chakra-ui/react';
import { AuthProvider } from './context/AuthContext';
import { routeTree } from './routeTree.gen';

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

// Create a router instance
const router = createRouter({
  routeTree,
  context: {
    queryClient,
    auth: undefined, // Will be set by AuthProvider
  },
  defaultPreload: 'intent',
  defaultPreloadStaleTime: 1000 * 60 * 5, // 5 minutes
});

// Register the router for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

type AuthState = {
  user: { id: string; email: string; name: string; picture?: string } | null;
  isLoading: boolean;
};

// Create a modified AuthProvider that injects auth info into router context
function AuthProviderWithRouter({ children }: { children: React.ReactNode }) {
  const [auth, setAuth] = React.useState<AuthState>({ user: null, isLoading: true });
  
  // Update router context with auth data
  React.useEffect(() => {
    router.context.auth = auth;
  }, [auth]);
  
  return (
    <AuthProvider value={{ ...auth, setAuth }}>
      {children}
    </AuthProvider>
  );
}

// Create the root element
const rootElement = document.getElementById('root');
if (!rootElement) throw new Error('No root element found');
const root = ReactDOM.createRoot(rootElement);

// Render the app
root.render(
  <React.StrictMode>
    <ChakraProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProviderWithRouter>
          <RouterProvider router={router} />
        </AuthProviderWithRouter>
      </QueryClientProvider>
    </ChakraProvider>
  </React.StrictMode>,
);
