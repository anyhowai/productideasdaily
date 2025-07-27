# Startup Idea Discovery Dashboard

A React-based dashboard for visualizing product ideas extracted from X (Twitter) using AI analysis.

## Features

- **Top 10 Product Ideas**: View the most promising product ideas for each day
- **Historical Data**: Browse ideas from past dates
- **Category Analysis**: Top categories visualization
- **Detailed Analytics**: Statistics on tweet analysis and idea discovery
- **Dark/Light Theme**: Toggle between themes
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React 18** with TypeScript
- **Material-UI (MUI) v5** for components and theming
- **React Router v6** for navigation
- **Webpack** for bundling

## Getting Started

### Prerequisites

- Node.js 18+ (recommended 20+)
- npm or yarn

### Installation

1. Install dependencies:

   ```bash
   npm install
   ```

2. Start the development server:

   ```bash
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Data Structure

The dashboard expects analysis data in the following format:

```json
{
  "summary": {
    "total_tweets_analyzed": 438,
    "product_requests_found": 10,
    "token_usage": {
      "input_tokens": 28646,
      "output_tokens": 2022,
      "total_tokens": 37426
    }
  },
  "product_requests": [
    {
      "category": "Developer Tool / AI Development Platform",
      "description": "A tool that...",
      "pain_point": "Existing backend services...",
      "target_audience": "App Developers, Startups, Indie Hackers",
      "urgency_level": "High",
      "tweets": [...]
    }
  ]
}
```

## Deployment

This app is configured for deployment on Vercel. The `vercel.json` file handles routing and build configuration.

### Quick Deploy to Vercel

1. Install Vercel CLI:

   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   npm run deploy
   ```

### Manual Deployment

1. Build the project:

   ```bash
   npm run build
   ```

2. Deploy the `dist` directory to your hosting provider.

## Project Structure

```
dashboard/
├── public/
│   ├── data/analysis/     # Analysis JSON files
│   └── index.html         # HTML template
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── AppBar.tsx     # Main navigation bar
│   │   ├── Sidebar.tsx    # Side navigation
│   │   ├── IdeaCard.tsx   # Product idea display card
│   │   ├── StatsCard.tsx  # Analytics summary
│   │   └── CategoryChart.tsx # Category distribution
│   ├── pages/            # Page components
│   │   └── Dashboard.tsx # Main dashboard page
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── App.tsx           # Main app component
│   └── index.tsx         # Entry point
├── package.json
├── tsconfig.json
├── webpack.config.js
└── vercel.json
```

## Current Status

✅ **Completed Features:**

- React app with Material-UI components
- Dashboard displaying top 10 product ideas
- Date selection for historical data
- Theme toggle (dark/light mode)
- Responsive design
- Statistics and analytics display
- Category distribution visualization
- Source tweet display with links

🔄 **Ready for Deployment:**

- Build process working
- Vercel configuration ready
- Data loading from JSON files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the ISC License.
