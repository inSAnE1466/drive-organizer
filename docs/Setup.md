# Setup Guide and Development Environment

This document provides detailed instructions for setting up the development environment for the Drive Organizer project, including Google Cloud Console configuration, Redis setup, and local development environment configuration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Google Cloud Console Setup](#google-cloud-console-setup)
3. [Firebase Project Setup](#firebase-project-setup)
4. [Redis Installation and Configuration](#redis-installation-and-configuration)
5. [Backend Setup](#backend-setup)
6. [Frontend Setup](#frontend-setup)
7. [Running the Application](#running-the-application)
8. [Development Workflow](#development-workflow)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have the following installed:

- **Node.js** (v18+) and npm (v9+)
- **Python** (v3.10+) and pip
- **Git**
- **Docker** and Docker Compose (optional, for containerized development)
- **Redis** (v6+)

## Google Cloud Console Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click on "New Project"
4. Enter "Drive Organizer" as the project name
5. Click "Create"

### 2. Enable Required APIs

1. In your project, navigate to "APIs & Services" > "Library"
2. Search for and enable the following APIs:
   - Google Drive API
   - Identity Services API
   - Cloud Storage API
   - Gemini API

### 3. Create OAuth Credentials

1. Navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Set the application type to "Web application"
4. Add the following Authorized JavaScript origins:
   - `http://localhost:5173` (Vite dev server)
   - `http://localhost:3000` (Alternative frontend port)
   - `http://localhost:8000` (FastAPI backend)
5. Add the following Authorized redirect URIs:
   - `http://localhost:5173/auth/callback`
   - `http://localhost:8000/api/auth/callback`
6. Click "Create" and note down the Client ID and Client Secret

### 4. Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type
3. Fill in the required information:
   - App name: "Drive Organizer"
   - User support email: Your email
   - Developer contact information: Your email
4. Add the following scopes:
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
   - `https://www.googleapis.com/auth/drive.readonly`
5. Add test users (your Google account)

### 5. Obtain Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Note down the key for later use

## Firebase Project Setup

### 1. Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Select the Google Cloud project you created earlier
4. Follow the setup steps (enable Google Analytics if desired)

### 2. Enable Authentication

1. In Firebase console, go to "Build" > "Authentication"
2. Click "Get started"
3. Enable "Google" as a sign-in provider
4. Configure the provider with your OAuth Client ID and Client Secret

### 3. Add a Web App

1. In Firebase console, click on the gear icon (Project settings)
2. In the "Your apps" section, click the web icon (</>) to add a web app
3. Register your app with the name "Drive Organizer"
4. Note down the Firebase configuration object
5. Click "Continue to console"

### 4. Set Up Service Account (for Backend)

1. In Firebase console, go to Project settings > Service accounts
2. Click "Generate new private key" for Firebase Admin SDK
3. Download the JSON key file and keep it secure

## Redis Installation and Configuration

### Local Installation

#### Mac OS

```bash
# Using Homebrew
brew install redis
# Start Redis service
brew services start redis
```

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

#### Windows

Download the Windows release from the [Redis Downloads page](https://redis.io/download).

### Using Docker

```bash
docker run --name drive-organizer-redis -p 6379:6379 -d redis
```

### Testing Redis Connection

```bash
redis-cli ping
```

Should respond with `PONG` if the connection is working.

## Backend Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/drive-organizer.git
cd drive-organizer
```

### 2. Create a Virtual Environment

```bash
cd backend
python -m venv venv
```

### 3. Activate the Virtual Environment

#### On Windows:

```bash
venv\Scripts\activate
```

#### On macOS/Linux:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```
# API config
DEBUG=True
API_V1_STR=/api

# CORS settings
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000

# Redis settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Google API settings
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback

# Gemini API settings
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Firebase settings
FIREBASE_PROJECT_ID=your_project_id_here
FIREBASE_SERVICE_ACCOUNT={"type":"service_account",...}

# File storage
TEMP_DIR=/tmp/drive-organizer
```

Replace the placeholders with your actual credentials. For the `FIREBASE_SERVICE_ACCOUNT`, paste the entire JSON content of your service account key file as a string.

### 6. Create Temporary Directories

```bash
mkdir -p /tmp/drive-organizer
```

## Frontend Setup

### 1. Navigate to the Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```
VITE_API_URL=http://localhost:8000/api
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

Replace the placeholders with your actual Firebase configuration values.

## Running the Application

### Backend

From the `backend` directory with the virtual environment activated:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

From the `frontend` directory:

```bash
npm run dev
```

This will start the Vite development server on port 5173. You can access the application at [http://localhost:5173](http://localhost:5173).

## Development Workflow

### Backend Development

1. Activate the virtual environment
2. Make changes to the code
3. The server will automatically reload with `--reload` flag
4. Access the interactive API documentation at [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

### Frontend Development

1. Make changes to the code
2. Vite's hot module replacement will automatically update the application
3. Use the React DevTools and TanStack Router/Query DevTools for debugging

### Using Docker Compose

From the project root directory:

```bash
docker-compose up -d
```

This will start all services (frontend, backend, and Redis) in detached mode.

## Troubleshooting

### Backend Issues

**Problem**: Authentication fails with Google API  
**Solution**: Check that your OAuth credentials are correctly configured and that you've enabled the necessary APIs in Google Cloud Console.

**Problem**: Redis connection error  
**Solution**: Ensure Redis is running and check your Redis configuration in the `.env` file.

**Problem**: Firebase token verification fails  
**Solution**: Check that your service account key is valid and properly formatted in the `.env` file.

### Frontend Issues

**Problem**: "Network Error" when connecting to the backend  
**Solution**: Ensure the backend server is running and that CORS is correctly configured.

**Problem**: Authentication with Firebase fails  
**Solution**: Verify your Firebase configuration in the `.env` file and check that the Authentication service is enabled in the Firebase console.

**Problem**: TanStack Router not generating routes correctly  
**Solution**: Check that the TanStack Router Vite plugin is correctly configured in `vite.config.ts` and that your route files follow the correct naming convention.