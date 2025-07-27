import { AnalysisData } from '../types';

const loadAnalysisData = async (date: string): Promise<AnalysisData | null> => {
  try {
    // For now, we'll load from the public directory
    // In production, this would be an API call
    const response = await fetch(`/data/analysis/${date}_analysis.json`);
    if (!response.ok) {
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error('Error loading analysis data:', error);
    return null;
  }
};

const getAvailableDates = (): string[] => {
  // This would typically come from an API or file system scan
  // For now, we'll hardcode the available dates
  return ['260725']; // Add more dates as they become available
};

const formatDate = (dateString: string): string => {
  // Convert YYMMDD format to readable date
  const year = '20' + dateString.substring(0, 2);
  const month = dateString.substring(2, 4);
  const day = dateString.substring(4, 6);
  return new Date(`${year}-${month}-${day}`).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const getTodayDate = (): string => {
  const today = new Date();
  const year = today.getFullYear().toString().slice(-2);
  const month = (today.getMonth() + 1).toString().padStart(2, '0');
  const day = today.getDate().toString().padStart(2, '0');
  return `${year}${month}${day}`;
};

export { formatDate, getAvailableDates, getTodayDate, loadAnalysisData };
