import { Brightness4, Brightness7, Menu as MenuIcon } from '@mui/icons-material';
import {
    Box,
    IconButton,
    AppBar as MuiAppBar,
    Toolbar,
    Typography,
    useMediaQuery,
    useTheme
} from '@mui/material';
import React from 'react';

interface AppBarProps {
  onMenuClick: () => void;
  onThemeToggle: () => void;
}

const AppBar: React.FC<AppBarProps> = ({ onMenuClick, onThemeToggle }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <MuiAppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
      <Toolbar>
        {isMobile && (
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={onMenuClick}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}
        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
          Startup Idea Discovery
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton color="inherit" onClick={onThemeToggle}>
            {theme.palette.mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
        </Box>
      </Toolbar>
    </MuiAppBar>
  );
};

export default AppBar;