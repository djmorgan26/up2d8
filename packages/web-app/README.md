# UP2D8 Web Application

A personalized news digest application that keeps you up to date with AI-powered news aggregation and insights.

## Project Overview

UP2D8 is a modern web application built with React, TypeScript, and Vite that provides users with a personalized news experience powered by Azure AI services.

## Technologies Used

This project is built with:

- **Vite** - Fast build tool and development server
- **TypeScript** - Type-safe JavaScript
- **React** - UI component library
- **shadcn/ui** - High-quality UI components
- **Tailwind CSS** - Utility-first CSS framework
- **Azure MSAL** - Microsoft Authentication Library for user authentication
- **TanStack Query** - Data fetching and caching
- **React Router** - Client-side routing

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```sh
git clone <repository-url>
```

2. Navigate to the web-app directory:
```sh
cd packages/web-app
```

3. Install dependencies:
```sh
npm install
```

4. Start the development server:
```sh
npm run dev
```

The application will be available at `http://localhost:8080`

## Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build for production
- `npm run build:dev` - Build in development mode
- `npm run preview` - Preview the production build
- `npm run lint` - Run ESLint

## Project Structure

```
packages/web-app/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page components
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Utility functions and configurations
│   └── main.tsx       # Application entry point
├── public/            # Static assets
└── index.html         # HTML entry point
```

## Development

The application uses:
- **MSAL** for Azure AD authentication
- **React Query** for efficient data fetching and caching
- **React Router** for navigation
- **shadcn/ui** components for consistent UI

## Building for Production

To create a production build:

```sh
npm run build
```

The built files will be in the `dist` directory.

## License

Copyright © 2024 UP2D8. All rights reserved.
