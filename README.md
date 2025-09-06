# Civic Reporting Platform

This repository contains the full source code for a comprehensive civic issue reporting platform. It is a monorepo that includes a mobile application for citizens, a web-based dashboard for municipal authorities, and a backend server to power both.

The platform enables citizens to report local issues (e.g., potholes, broken streetlights) by submitting a description and photos from their mobile devices. Municipal staff can then view, manage, and track these issues through a central dashboard.

## Project Architecture

The project is divided into three main components, each in its own directory:

-   `frontend/`: A **React Native (Expo)** mobile application for citizens to report issues.
-   `dashboard/`: A **Next.js** web application for municipal staff to view and manage reported issues.
-   `backend/`: A **FastAPI (Python)** backend server that provides a REST API for the frontend and dashboard.
-   `supabase/`: Contains the **PostgreSQL** schema for the database, managed by Supabase.

### Technology Stack

-   **Backend**: Python, FastAPI, Uvicorn
-   **Frontend (Mobile)**: JavaScript, React Native, Expo
-   **Frontend (Dashboard)**: TypeScript, React, Next.js
-   **Database**: Supabase (PostgreSQL)
-   **Image Storage**: Cloudinary (via backend)

## Getting Started

To run the full platform, you will need to set up the backend, the database, and at least one of the frontends.

### 1. Database Setup (Supabase)

The project uses Supabase for its database and authentication services.

1.  Create a new project on [Supabase](https://supabase.com/).
2.  Navigate to the **SQL Editor** in your Supabase project dashboard.
3.  Copy the entire content of `supabase/schema.sql` and run it in the SQL editor. This will create all the necessary tables and seed them with initial data (e.g., departments, sample users).

### 2. Backend Setup

The backend server is built with FastAPI.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    -   Copy the example `.env.example` file to a new `.env` file: `cp .env.example .env`
    -   Open `.env` and fill in the required values:
        -   `SUPABASE_URL`: Your Supabase project URL.
        -   `SUPABASE_KEY`: Your Supabase project's `anon` key.
        -   `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase project's `service_role` key (for admin-level operations).
        -   (Optional) `CLOUDINARY_*`: If you want to enable image uploads, create a Cloudinary account and fill in your cloud name, API key, and secret.

4.  **Run the backend server:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The API will now be running at `http://localhost:8000`.

### 3. Dashboard Setup (Next.js)

The dashboard is a web application for staff.

1.  **Navigate to the dashboard directory:**
    ```bash
    cd dashboard
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The dashboard will be available at `http://localhost:3000`.

### 4. Mobile App Setup (React Native/Expo)

The mobile app is built with Expo.

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Configure environment variables:**
    -   The mobile app uses the same Supabase credentials as the backend. You need to expose them to Expo. Create a `.env` file in the `frontend` directory and add the following:
        ```
        EXPO_PUBLIC_SUPABASE_URL=YOUR_SUPABASE_URL
        EXPO_PUBLIC_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
        ```
        Replace the values with your actual Supabase URL and `anon` key.

4.  **Run the app:**
    ```bash
    npm start
    ```
    This will open the Expo developer tools. You can run the app on a physical device using the Expo Go app or in an emulator.

## Core Features

-   **User Authentication**: Users can sign up and log in using a "magic link" sent to their email, powered by Supabase Auth.
-   **Issue Reporting**: Authenticated users can submit new issues, including a description, photos, and their current location.
-   **Issue Management**: The dashboard provides a view of all reported issues.
-   **AI-Powered Assistance**:
    -   A simple spam detection model flags potentially unwanted submissions.
    -   An FAQ model can answer basic user questions.
    -   An automatic routing engine suggests the correct municipal department for a new issue based on its description.
-   **Analytics**: The admin dashboard includes analytics on issue volume, response times, and geographic hotspots.
-   **Push Notifications**: The system is set up to register devices and send push notifications for status updates (requires integration with a service like FCM or Expo Push).
