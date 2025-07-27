import {
    Dashboard as DashboardIcon,
    History as HistoryIcon,
    TrendingUp as TrendingIcon
} from '@mui/icons-material';
import {
    Box,
    Divider,
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    useMediaQuery,
    useTheme
} from '@mui/material';
import React from 'react';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  selectedDate: string;
  onDateSelect: (date: string) => void;
  availableDates: string[];
}

const drawerWidth = 240;

const Sidebar: React.FC<SidebarProps> = ({
  open,
  onClose,
  selectedDate,
  onDateSelect,
  availableDates
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const drawer = (
    <Box>
      <Box sx={{ p: 2 }}>
        <Box sx={{ height: 64 }} /> {/* Spacer for AppBar */}
      </Box>
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton>
            <ListItemIcon>
              <DashboardIcon />
            </ListItemIcon>
            <ListItemText primary="Dashboard" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton>
            <ListItemIcon>
              <TrendingIcon />
            </ListItemIcon>
            <ListItemText primary="Trends" />
          </ListItemButton>
        </ListItem>
      </List>
      <Divider />
      <List>
        <ListItem>
          <ListItemText primary="Historical Data" />
        </ListItem>
        {availableDates.map((date) => (
          <ListItem key={date} disablePadding>
            <ListItemButton
              selected={selectedDate === date}
              onClick={() => onDateSelect(date)}
            >
              <ListItemIcon>
                <HistoryIcon />
              </ListItemIcon>
              <ListItemText primary={date} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'permanent'}
      open={open}
      onClose={onClose}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box'
        }
      }}
    >
      {drawer}
    </Drawer>
  );
};

export default Sidebar;