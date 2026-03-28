# P.U.L.S.E Frontend (v2)

Welcome to the P.U.L.S.E (Personalized Universal Lifestyle & Sport Engine) Next.js Frontend.

## 🚀 Quick Start

1.  **Install dependencies**:
    ```bash
    npm install
    ```
2.  **Run in development**:
    ```bash
    npm run dev
    ```
3.  **Configure environment**:
    Create a `.env.local` if you need to override the default API URL:
    ```bash
    NEXT_PUBLIC_API_URL=http://localhost:8000/api
    ```

## 📂 Project Architecture

- **`src/app/`**: Next.js App Router (each folder is a URL route).
- **`src/components/`**: Reusable UI parts (Layouts, Forms, Charts).
- **`src/services/`**: Code for communicating with the FastAPI backend.
- **`src/store/`**: Global state management using Zustand.
- **`src/hooks/`**: Custom React logic (e.g., `useAuth`).
- **`src/config/`**: Central configuration for API endpoints.

## 📊 Development Status (64% Complete)

| Feature                 | Page Path     | Status         |
| ----------------------- | ------------- | -------------- |
| **Landing Page**        | `/`           | ✅ Done        |
| **Auth (Login/Reg)**    | `/auth/*`     | ✅ Done        |
| **Dashboard**           | `/dashboard`  | ✅ Done        |
| **Meal Log / Chat**     | `/chat`       | ✅ Done        |
| **Meal List**           | `/meals`      | ✅ Done        |
| **Settings**            | `/settings`   | ✅ Done        |
| **New Meal Form**       | `/meals/new`  | ⏳ In Progress |
| **Edit Meal Form**      | `/meals/edit` | ⏳ In Progress |
| **Nutritional Charts**  | `/analytics`  | ⏳ Planned     |

## 🛠️ Development Guidelines

- **Authentication**: All protected pages must use the `AuthLayout` component.
- **Data Fetching**: Use **TanStack Query** (React Query) for all API calls.
- **Form State**: Use **Zod** for data validation and consistency.
- **State Management**: Use **Zustand** for global shared data (like user profiles).
- **Styling**: Use **Tailwind CSS** for all UI components.

---

**Last Updated:** March 2026
**Framework:** Next.js 14 (App Router)
**Status:** Actively Under Development 🚀
