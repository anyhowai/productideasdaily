import {
    Box,
    Card,
    CardContent,
    Chip,
    Typography
} from '@mui/material';
import React from 'react';
import { ProductRequest } from '../types';

interface CategoryChartProps {
  productRequests: ProductRequest[];
}

const CategoryChart: React.FC<CategoryChartProps> = ({ productRequests }) => {
  const categoryCounts = productRequests.reduce((acc, request) => {
    const category = request.category;
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const sortedCategories = Object.entries(categoryCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5); // Show top 5 categories

  if (sortedCategories.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Category Distribution
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No data available
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Top Categories
        </Typography>
        <Box sx={{ mt: 2 }}>
          {sortedCategories.map(([category, count], index) => (
            <Box
              key={category}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                mb: 2,
                p: 1,
                borderRadius: 1,
                backgroundColor: 'action.hover'
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 'bold', mr: 1 }}>
                  #{index + 1}
                </Typography>
                <Typography variant="body2" sx={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {category}
                </Typography>
              </Box>
              <Chip
                label={count}
                size="small"
                color="primary"
                variant="outlined"
              />
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default CategoryChart;