import {
    ExpandMore as ExpandMoreIcon,
    Group as GroupIcon,
    Launch as LaunchIcon,
    TrendingUp as TrendingIcon,
    Warning as WarningIcon
} from '@mui/icons-material';
import {
    Box,
    Button,
    Card,
    CardActions,
    CardContent,
    Chip,
    Collapse,
    Link,
    List,
    ListItem,
    ListItemText,
    Typography
} from '@mui/material';
import React from 'react';
import { ProductRequest } from '../types';

interface IdeaCardProps {
  idea: ProductRequest;
  index: number;
}

const IdeaCard: React.FC<IdeaCardProps> = ({ idea, index }) => {
  const [expanded, setExpanded] = React.useState(false);

  const getUrgencyColor = (urgency: string) => {
    switch (urgency.toLowerCase()) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const totalEngagement = idea.tweets.reduce(
    (sum, tweet) => sum + tweet.engagement_score,
    0
  );

  return (
    <Card sx={{ mb: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6" component="h3" gutterBottom>
            #{index + 1} {idea.category}
          </Typography>
          <Chip
            label={idea.urgency_level}
            color={getUrgencyColor(idea.urgency_level) as any}
            size="small"
            icon={<WarningIcon />}
          />
        </Box>

        <Typography variant="body2" color="text.secondary" paragraph>
          {idea.description}
        </Typography>

        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Pain Point:
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {idea.pain_point}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          <Chip
            icon={<GroupIcon />}
            label={idea.target_audience}
            size="small"
            variant="outlined"
          />
          <Chip
            icon={<TrendingIcon />}
            label={`${totalEngagement} engagement`}
            size="small"
            variant="outlined"
          />
        </Box>

        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Source Tweets ({idea.tweets.length}):
            </Typography>
            <List dense>
              {idea.tweets.map((tweet) => (
                <ListItem key={tweet.id} sx={{ px: 0 }}>
                  <ListItemText
                    primary={
                      <Link
                        href={tweet.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
                      >
                        @{tweet.user_handle}
                        <LaunchIcon fontSize="small" />
                      </Link>
                    }
                    secondary={
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {tweet.text}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        </Collapse>
      </CardContent>

      <CardActions>
        <Button
          size="small"
          onClick={() => setExpanded(!expanded)}
          endIcon={<ExpandMoreIcon />}
        >
          {expanded ? 'Hide' : 'Show'} Tweets
        </Button>
      </CardActions>
    </Card>
  );
};

export default IdeaCard;