import {
    Box,
    createTheme,
    CssBaseline,
    ThemeProvider,
    useMediaQuery
} from '@mui/material';
import React, { useMemo, useState } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import AppBar from './components/AppBar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import { getAvailableDates, getTodayDate } from './utils/dataLoader';

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedDate, setSelectedDate] = useState(getTodayDate());

  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  const availableDates = getAvailableDates();

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: darkMode ? 'dark' : 'light',
          primary: {
            main: '#1976d2'
          },
          secondary: {
            main: '#dc004e'
          }
        },
        typography: {
          fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif'
        }
      }),
    [darkMode]
  );

  const handleThemeToggle = () => {
    setDarkMode(!darkMode);
  };

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleDateSelect = (date: string) => {
    setSelectedDate(date);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          <AppBar onMenuClick={handleSidebarToggle} onThemeToggle={handleThemeToggle} />
          <Sidebar
            open={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            selectedDate={selectedDate}
            onDateSelect={handleDateSelect}
            availableDates={availableDates}
          />
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              width: { sm: `calc(100% - ${240}px)` },
              mt: 8
            }}
          >
            <Dashboard selectedDate={selectedDate} />
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App;