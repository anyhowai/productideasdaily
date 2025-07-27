import {
    Alert,
    Box,
    CircularProgress,
    Container,
    Grid,
    Paper,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import CategoryChart from '../components/CategoryChart';
import IdeaCard from '../components/IdeaCard';
import StatsCard from '../components/StatsCard';
import { AnalysisData } from '../types';
import { formatDate, loadAnalysisData } from '../utils/dataLoader';

interface DashboardProps {
  selectedDate: string;
}

const Dashboard: React.FC<DashboardProps> = ({ selectedDate }) => {
  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const analysisData = await loadAnalysisData(selectedDate);
        if (analysisData) {
          setData(analysisData);
        } else {
          setError('No data available for the selected date');
        }
      } catch (err) {
        setError('Failed to load data');
        console.error('Error loading data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedDate]);

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '50vh'
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  if (!data) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="info">
          No data available for the selected date
        </Alert>
      </Container>
    );
  }

  const top10Ideas = data.product_requests.slice(0, 10);

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Top 10 Product Ideas
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          {formatDate(selectedDate)}
        </Typography>
      </Box>

      {/* Stats and Chart Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <StatsCard summary={data.summary} />
        </Grid>
        <Grid item xs={12} md={4}>
          <CategoryChart productRequests={data.product_requests} />
        </Grid>
      </Grid>

      {/* Ideas Grid */}
      <Grid container spacing={3}>
        {top10Ideas.map((idea, index) => (
          <Grid item xs={12} md={6} lg={4} key={index}>
            <IdeaCard idea={idea} index={index} />
          </Grid>
        ))}
      </Grid>

      {top10Ideas.length === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            No product ideas found for this date
          </Typography>
        </Paper>
      )}
    </Container>
  );
};

export default Dashboard;