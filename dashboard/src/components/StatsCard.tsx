import {
    Analytics as AnalyticsIcon,
    Speed as SpeedIcon,
    TrendingUp as TrendingIcon
} from '@mui/icons-material';
import {
    Box,
    Card,
    CardContent,
    LinearProgress,
    Typography
} from '@mui/material';
import React from 'react';
import { AnalysisSummary } from '../types';

interface StatsCardProps {
  summary: AnalysisSummary;
}

const StatsCard: React.FC<StatsCardProps> = ({ summary }) => {
  const analysisRate = (summary.product_requests_found / summary.total_tweets_analyzed) * 100;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Analysis Summary
        </Typography>

        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2, mt: 2 }}>
          <Box sx={{ textAlign: 'center' }}>
            <AnalyticsIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h4" component="div">
              {summary.total_tweets_analyzed}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Tweets Analyzed
            </Typography>
          </Box>

          <Box sx={{ textAlign: 'center' }}>
            <TrendingIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
            <Typography variant="h4" component="div">
              {summary.product_requests_found}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Product Ideas Found
            </Typography>
          </Box>

          <Box sx={{ textAlign: 'center' }}>
            <SpeedIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
            <Typography variant="h4" component="div">
              {summary.token_usage.total_tokens.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Tokens Used
            </Typography>
          </Box>
        </Box>

        <Box sx={{ mt: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2">Idea Discovery Rate</Typography>
            <Typography variant="body2">{analysisRate.toFixed(1)}%</Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(analysisRate, 100)}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default StatsCard;