# AI Research Assistant Frontend

A modern React frontend for the AI Research Assistant Platform.

## Features

- **Modern UI/UX** with Tailwind CSS
- **Authentication** with JWT tokens
- **Research Interface** with real-time results
- **Subscription Management** with Stripe integration
- **Responsive Design** for all devices
- **Toast Notifications** for user feedback

## Quick Start

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running on `http://localhost:8002`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Project Structure

```
src/
├── components/          # Reusable UI components
├── pages/              # Page components
├── services/           # API services
├── store/              # State management (Zustand)
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── App.js              # Main app component
└── index.js            # App entry point
```

## Key Components

### Authentication
- **Login/Register** forms with validation
- **JWT token management**
- **Protected routes**

### Research Interface
- **Query input** with validation
- **Real-time results** display
- **AI summaries** and citations
- **Export functionality** (PDF, Markdown)

### Subscription Management
- **Plan comparison** table
- **Usage tracking** with progress bars
- **Stripe checkout** integration
- **Billing portal** access

## API Integration

The frontend communicates with the backend API through:

- **Axios** for HTTP requests
- **Request/Response interceptors** for auth
- **Error handling** with toast notifications

## Styling

- **Tailwind CSS** for utility-first styling
- **Custom components** with consistent design
- **Responsive design** for mobile/desktop
- **Dark mode** support (planned)

## State Management

- **Zustand** for global state
- **React Hook Form** for form management
- **Local storage** for persistence

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8002
```

## Deployment

The frontend can be deployed to:

- **Vercel** (recommended)
- **Netlify**
- **AWS S3 + CloudFront**
- **Any static hosting**

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation as needed
4. Use conventional commits

## License

MIT License - see LICENSE file for details 