import { Outlet, createRootRoute, Link, useRouter } from '@tanstack/react-router';
import { Box, Flex, VStack, HStack, Text, Button, Icon, useColorMode } from '@chakra-ui/react';
import { FiHome, FiFolder, FiSearch, FiSettings, FiLogOut, FiMoon, FiSun } from 'react-icons/fi';
import { IconType } from 'react-icons';
import { useAuth } from '../context/AuthContext';

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();
  const { colorMode, toggleColorMode } = useColorMode();

  const handleLogout = async () => {
    await logout();
    router.navigate({ to: '/login' });
  };

  // Show loading state
  if (isLoading) {
    return (
      <Flex h="100vh" align="center" justify="center">
        <Text>Loading...</Text>
      </Flex>
    );
  }

  // Redirect to login if not authenticated
  if (!user) {
    return <Outlet />;
  }

  return (
    <Flex h="100vh">
      {/* Sidebar */}
      <VStack
        w="240px"
        h="full"
        p={4}
        bg="gray.100"
        _dark={{ bg: 'gray.800' }}
        spacing={6}
        align="stretch"
      >
        <Box>
          <Text fontSize="xl" fontWeight="bold">
            Drive Organizer
          </Text>
        </Box>

        <VStack spacing={2} align="stretch">
          <NavLink to="/" icon={FiHome} label="Dashboard" />
          <NavLink to="/drive" icon={FiFolder} label="My Drive" />
          <NavLink to="/analyze" icon={FiSearch} label="Analyze" />
          <NavLink to="/organize" icon={FiFolder} label="Organize" />
          <NavLink to="/settings" icon={FiSettings} label="Settings" />
        </VStack>

        <Box mt="auto">
          <Button 
            variant="ghost" 
            w="full" 
            justifyContent="flex-start" 
            leftIcon={<Icon as={colorMode === 'light' ? FiMoon : FiSun} />}
            onClick={toggleColorMode}
          >
            {colorMode === 'light' ? 'Dark Mode' : 'Light Mode'}
          </Button>
          <Button 
            variant="ghost" 
            w="full" 
            justifyContent="flex-start" 
            leftIcon={<Icon as={FiLogOut} />}
            onClick={handleLogout}
          >
            Logout
          </Button>
        </Box>
      </VStack>

      {/* Main content area */}
      <Box flex="1" p={6} overflow="auto">
        <Outlet />
      </Box>
    </Flex>
  );
}

function NavLink({ to, icon, label }: { to: string; icon: IconType; label: string }) {
  return (
    <Link
      to={to}
      activeProps={{
        style: {
          fontWeight: 'bold',
        },
      }}
      style={{ textDecoration: 'none' }}
    >
      {({ isActive }) => (
        <Button
          variant="ghost"
          w="full"
          justifyContent="flex-start"
          leftIcon={<Icon as={icon} />}
          bg={isActive ? 'blue.100' : undefined}
          _dark={{
            bg: isActive ? 'blue.800' : undefined,
          }}
        >
          {label}
        </Button>
      )}
    </Link>
  );
}
