import { createFileRoute, redirect } from '@tanstack/react-router';
import { Button, Box, Heading, Text, VStack, Center, useColorMode } from '@chakra-ui/react';
import { FcGoogle } from 'react-icons/fc';
import { useAuth } from '../context/AuthContext';

export const Route = createFileRoute('/login')({
  beforeLoad: async ({ context }) => {
    // Redirect to dashboard if already authenticated
    if (context.auth?.user) {
      throw redirect({ to: '/' });
    }
  },
  component: LoginPage,
});

function LoginPage() {
  const { signInWithGoogle, isLoading } = useAuth();
  const { colorMode } = useColorMode();

  const handleSignIn = async () => {
    await signInWithGoogle();
    // No need to navigate manually as beforeLoad will handle redirect
  };

  return (
    <Center minH="100vh" bg={colorMode === 'light' ? 'gray.50' : 'gray.900'}>
      <Box
        p={8}
        maxW="md"
        borderWidth={1}
        borderRadius="lg"
        boxShadow="lg"
        bg={colorMode === 'light' ? 'white' : 'gray.800'}
      >
        <VStack spacing={8}>
          <VStack spacing={2} textAlign="center">
            <Heading>Welcome to Drive Organizer</Heading>
            <Text color={colorMode === 'light' ? 'gray.600' : 'gray.400'}>
              Organize your Google Drive images with AI
            </Text>
          </VStack>

          <Button
            w="full"
            size="lg"
            leftIcon={<FcGoogle />}
            onClick={handleSignIn}
            isLoading={isLoading}
            loadingText="Signing in..."
          >
            Sign in with Google
          </Button>
        </VStack>
      </Box>
    </Center>
  );
}
