import { createFileRoute, redirect } from '@tanstack/react-router';
import { Box, Grid, Heading, Text, Stat, StatLabel, StatNumber, StatHelpText, SimpleGrid, Card, CardBody, CardHeader } from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';

export const Route = createFileRoute('/')({
  beforeLoad: async ({ context }) => {
    // Redirect to login if not authenticated
    if (!context.auth?.user) {
      throw redirect({ to: '/login' });
    }
  },
  component: Dashboard,
});

function Dashboard() {
  // TODO: Replace with API call to /api/stats/dashboard
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      return {
        data: {
          totalImages: 1245,
          analyzedImages: 980,
          categories: [
            { name: 'Landscapes', count: 320 },
            { name: 'People', count: 280 },
            { name: 'Food', count: 150 },
            { name: 'Buildings', count: 110 },
            { name: 'Other', count: 120 },
          ],
          recentActivity: [
            { date: '2023-01-01', count: 12 },
            { date: '2023-01-02', count: 8 },
            { date: '2023-01-03', count: 15 },
            { date: '2023-01-04', count: 22 },
            { date: '2023-01-05', count: 18 },
            { date: '2023-01-06', count: 30 },
            { date: '2023-01-07', count: 25 },
          ],
        }
      };
    },
  });

  if (isLoading) {
    return <div>Loading dashboard...</div>;
  }

  const dashboardStats = stats?.data;

  return (
    <Box>
      <Heading mb={6}>Dashboard</Heading>

      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} mb={8}>
        <Stat>
          <StatLabel>Total Images</StatLabel>
          <StatNumber>{dashboardStats.totalImages}</StatNumber>
          <StatHelpText>In Google Drive</StatHelpText>
        </Stat>
        <Stat>
          <StatLabel>Analyzed Images</StatLabel>
          <StatNumber>{dashboardStats.analyzedImages}</StatNumber>
          <StatHelpText>
            {Math.round((dashboardStats.analyzedImages / dashboardStats.totalImages) * 100)}% of total
          </StatHelpText>
        </Stat>
        <Stat>
          <StatLabel>Categories</StatLabel>
          <StatNumber>{dashboardStats.categories.length}</StatNumber>
          <StatHelpText>Used for organization</StatHelpText>
        </Stat>
      </SimpleGrid>

      <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Recent Activity</Heading>
          </CardHeader>
          <CardBody>
            <Box h="300px">
              {/* TODO: Implement activity chart */}
              <Text>Activity Chart Here</Text>
            </Box>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Category Distribution</Heading>
          </CardHeader>
          <CardBody>
            <Box>
              {dashboardStats.categories.map((category) => (
                <Box key={category.name} mb={3}>
                  <Text mb={1}>
                    {category.name}: {category.count} images
                  </Text>
                  <Box
                    w="100%"
                    h="8px"
                    bg="gray.100"
                    borderRadius="full"
                    _dark={{ bg: 'gray.700' }}
                  >
                    <Box
                      h="100%"
                      bg="blue.500"
                      borderRadius="full"
                      w={`${(category.count / dashboardStats.analyzedImages) * 100}%`}
                    />
                  </Box>
                </Box>
              ))}
            </Box>
          </CardBody>
        </Card>
      </Grid>
    </Box>
  );
}
