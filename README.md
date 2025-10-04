# Make a Choice API

A TypeScript Express API server.

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

4. Start production server:
```bash
npm start
```

## Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build the TypeScript code
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /api/` - Welcome message
- `POST /api/test` - Test endpoint

## Development

The server runs on port 3000 by default. You can change this by setting the `PORT` environment variable.

Visit `http://localhost:3000/health` to verify the server is running.
