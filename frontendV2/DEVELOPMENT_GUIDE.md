# P.U.L.S.E Frontend (V2) - Development Guide

## Project Overview

This is a complete frontend redesign of the P.U.L.S.E health and nutrition tracking application using **Next.js 14 (App Router)**, **TypeScript**, **Tailwind CSS**, and **TanStack Query v5**. The application is fully type-safe and integrates with the FastAPI backend.

## Tech Stack

- **Framework:** Next.js 14 (App Router, SSR/SSG capable)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS v3.4+ with custom design system
- **State Management:** TanStack Query v5 (server state) + Zustand (auth state)
- **HTTP Client:** Axios with JWT interceptors
- **UI Components:** shadcn/ui (Radix UI + Tailwind)
- **Date Utilities:** date-fns
- **Validation:** Zod (installed, not yet used)

## Project Structure

```
src/
├── app/                      # Next.js App Router pages
│   ├── layout.tsx           # Root layout with QueryProvider
│   ├── page.tsx             # Landing page (/)
│   ├── login/
│   │   └── page.tsx         # User sign-in (/login)
│   ├── register/
│   │   └── page.tsx         # Account creation (/register)
│   ├── dashboard/
│   │   └── page.tsx         # Nutrition summary & quick actions (/dashboard)
│   ├── meals/
│   │   ├── page.tsx         # Meal list with date navigation (/meals)
│   │   ├── new/
│   │   │   └── page.tsx     # Create new meal (not yet created)
│   │   └── [id]/
│   │       └── edit/
│   │           └── page.tsx # Edit meal (not yet created)
│   └── settings/
│       └── page.tsx         # User profile & macro targets (/settings)
├── components/
│   ├── layout/
│   │   └── AuthLayout.tsx   # Protected page wrapper with header/nav
│   ├── providers/
│   │   └── QueryProvider.tsx # TanStack Query provider
│   ├── ui/                  # shadcn/ui components (placeholder)
│   └── forms/               # Form components (placeholder)
├── config/
│   └── api.ts              # API endpoints & query keys
├── hooks/
│   ├── useAuth.ts          # Authentication hooks
│   ├── useMeals.ts         # Meal management hooks
│   ├── useNutrition.ts     # Nutrition data hooks
│   └── useFoods.ts         # Food database hooks
├── lib/
│   └── cn.ts               # Tailwind class merger utility
├── services/
│   ├── api-client.ts       # Axios wrapper with JWT interceptors
│   ├── auth.ts             # Authentication methods
│   ├── meals.ts            # Meal CRUD methods
│   ├── nutrition.ts        # Nutrition data methods
│   └── foods.ts            # Food search/category methods
├── store/
│   └── authStore.ts        # Zustand auth state store
├── types/
│   └── api.ts              # 100+ TypeScript interfaces from backend
├── utils/
│   └── (utilities placeholder)
├── globals.css             # Global Tailwind styles & design system
└── ...
```

## Getting Started

### 1. Installation

```bash
cd /Users/saloni/GIT/P.U.L.S.E/frontendV2
npm install
```

### 2. Environment Configuration

Create a `.env.local` file (or verify existing one):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

This points to the FastAPI backend running locally on port 8000.

### 3. Starting the Development Server

```bash
npm run dev
```

The application will start at `http://localhost:3000`

### 4. Building for Production

```bash
npm run build
npm start
```

## Architecture Overview

### Authentication Flow

```
1. User visits /login or /register
2. Form submission → useLogin/useRegister hook
3. Hook calls authService method (login/register)
4. authService calls API_ENDPOINTS via apiClient
5. On success: token stored, user data in Zustand store
6. Protected pages checked via AuthLayout component
7. Redirect to /login if not authenticated
```

### State Management Strategy

**TanStack Query (Server State):**
- Meals data, nutrition summaries, food database
- Automatic caching, invalidation on mutations
- Stale times: 5 min (meals), 10 min (daily nutrition), 15 min (weekly nutrition), 30 min (macro targets)

**Zustand (Client State):**
- Authentication status, user data, loading/error states
- Minimal state to avoid over-engineering
- Single source of truth for auth flag

**Local State (React):**
- Form inputs, temporary UI state (modals, dropdowns)
- Used in settings page for macro target adjustments

### API Integration

All API calls are **100% type-safe**:

1. **Type Definitions** (`src/types/api.ts`)
   - Generated from backend Swagger spec
   - 100+ interfaces covering all DTOs

2. **API Endpoints** (`src/config/api.ts`)
   - Centralized endpoint definitions
   - Query key factory for cache management

3. **Services** (`src/services/`)
   - Static methods for API calls
   - Return fully-typed responses

4. **Hooks** (`src/hooks/`)
   - TanStack Query wrappers
   - Auto-invalidation on mutations

5. **Client** (`src/services/api-client.ts`)
   - Axios instance with JWT interceptors
   - Token management and 401 redirect

## Features Implemented

### ✅ Authentication Pages
- **Login** (`/login`) - Email/password form with validation, error handling, loading state
- **Register** (`/register`) - Account creation with password confirmation, calorie goal setup, auto-login
- **Protected Layout** - AuthLayout component wraps authenticated pages with header, navigation, auth checks

### ✅ Dashboard (`/dashboard`)
- Daily nutrition summary (calories, protein, carbs, fat)
- Quick action buttons (Log Meal, View Meals, Settings)
- Recent meals list with calories
- Empty state with CTA

### ✅ Meals (`/meals`)
- Meal list with date navigation (previous/next/today)
- Date picker for historical data
- Summary cards (total meals, total calories, items logged)
- Meal detail display (type, description, items breakdown)
- Edit/Delete actions per meal
- Empty state with "Log Meal" CTA
- Sticky "Add Meal" button at bottom

### ✅ Settings (`/settings`)
- Profile section (display name, email, daily calorie goal)
- Macro targets editor (protein/carbs/fat percentages)
- Real-time gram calculations per macro
- Progress bars for percentage visualization
- Percentage total validation (must add up to 100%)
- Account information (username, member since)
- Success/error messaging

### ✅ Design System
- **9-Color Palette:** Primary, Accent, Success, Warning, Danger, Neutral (each with 50-900 variants)
- **Typography:** Tailwind defaults + semantic scaling
- **Spacing:** Tailwind scale 0-96, custom steps for common patterns
- **Components:** `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.badge` with color variants
- **Animations:** Fade, spin, pulse built-in
- **Responsive:** Mobile-first, breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)

## Page Development Status

| Page | Status | Notes |
|------|--------|-------|
| / (Landing) | ✅ Complete | Sign In/Sign Up CTAs |
| /login | ✅ Complete | Form validation, error handling, loading state |
| /register | ✅ Complete | Password confirmation, calorie goal, auto-login |
| /dashboard | ✅ Complete | Nutrition summary, quick actions, recent meals |
| /meals | ✅ Complete | Date navigation, meal list, edit/delete |
| /meals/new | ⏳ Pending | Meal creation form with AI logging |
| /meals/[id]/edit | ⏳ Pending | Meal editing form |
| /settings | ✅ Complete | Profile & macro target editing |

## API Integration Checklist

### Currently Integrated:
- ✅ User authentication (register, login)
- ✅ Meal CRUD (list by date, create, update, delete)
- ✅ Nutrition data (daily, weekly, range)
- ✅ Macro targets (get, update)
- ✅ User profile (read, update calorie goal)
- ✅ Food search (placeholder, needs backend endpoint)

### Endpoints Used:
```typescript
POST   /auth/register
POST   /auth/login
GET    /meals/all
GET    /meals/date/{date}
GET    /meals/{id}
POST   /meals
PUT    /meals/{id}
DELETE /meals/{id}
GET    /nutrition/daily/{date}
GET    /nutrition/weekly
GET    /nutrition/range
GET    /macro-targets
PUT    /macro-targets
PUT    /users/me
GET    /foods/search
```

## Form Validation Approach

**Current Implementation:**
- Client-side validation with real-time error clearing
- Form-level and field-level error handling
- Loading states during submission
- API error integration (backend validation errors displayed to user)

**Future Enhancement:**
- Integrate Zod for schema validation (package already installed)
- Create reusable form components with validation

## Styling Guide

### Button Classes
```tsx
// Primary action
<button className="btn-primary py-2 px-4 rounded-lg">Submit</button>

// Secondary action
<button className="btn-secondary py-2 px-4 rounded-lg">Cancel</button>

// Danger action
<button className="btn-danger py-2 px-4 rounded-lg">Delete</button>
```

### Card/Container
```tsx
<div className="bg-white rounded-xl shadow p-6">
  {/* content */}
</div>
```

### Color Palette Usage
```tsx
// Text colors
<p className="text-neutral-900">Primary text</p>
<p className="text-neutral-600">Secondary text</p>

// Background colors
<div className="bg-primary-50">Light primary</div>
<div className="bg-success-100">Light success</div>

// Border colors
<div className="border-l-4 border-primary-500">Accent border</div>

// Status badges
<span className="badge badge-success">Active</span>
<span className="badge badge-danger">Inactive</span>
```

## TypeScript Best Practices

1. **Always import types** - Use `import type` for types-only imports
2. **Type function parameters** - Explicit parameter and return types
3. **Use interfaces for APIs** - Matches backend DTOs
4. **Path aliases** - `@/` points to `src/` root

Example:
```typescript
import type { MealEntry, MealEntryCreateRequest } from '@/types/api'

export const useMeals = (): UseQueryResult<MealEntry[]> => {
  return useQuery({
    queryKey: QUERY_KEYS.MEALS_ALL,
    queryFn: () => mealsService.getAllMeals(),
  })
}
```

## Common Development Tasks

### Add a New Page

1. Create folder in `src/app/` with page name
2. Create `page.tsx` with 'use client' directive
3. Wrap with `AuthLayout` for protected pages
4. Import hooks and services as needed
5. Add TypeScript types from `src/types/api.ts`

Example:
```typescript
'use client'

import AuthLayout from '@/components/layout/AuthLayout'
import { useYourHook } from '@/hooks/useYourHook'

export default function YourPage() {
  const { data, isLoading } = useYourHook()
  
  return (
    <AuthLayout title="Your Page">
      {/* content */}
    </AuthLayout>
  )
}
```

### Add a New API Method

1. Add to `src/services/your-service.ts`:
```typescript
async yourMethod(param: string): Promise<YourType> {
  return apiClient.get(`/endpoint/${param}`)
}
```

2. Add to `src/hooks/useYourHook.ts`:
```typescript
export const useYourData = () => {
  return useQuery({
    queryKey: ['your-data'],
    queryFn: () => yourService.yourMethod('param'),
    staleTime: 5 * 60 * 1000,
  })
}
```

3. Use in component:
```typescript
const { data, isLoading, error } = useYourData()
```

### Handle API Errors

Errors are automatically handled by axios interceptor:
- 401 (Unauthorized) → redirects to /login
- Other errors → caught by TanStack Query
- Display in UI with error state:

```typescript
const { data, error } = useYourHook()

if (error) {
  return <div className="text-danger-600">Error: {error.message}</div>
}
```

## Debugging

### Enable TanStack Query DevTools

Already configured in `src/components/providers/QueryProvider.tsx`:

```bash
# DevTools will show in development
# Click the React Query icon in the browser
```

### Check Token in LocalStorage

```javascript
// In browser console
localStorage.getItem('auth_token')
```

### Verify API Calls

1. Open browser DevTools → Network tab
2. Filter by XHR/Fetch
3. Check request headers for `Authorization: Bearer <token>`
4. Verify response status codes

### Common Issues

**401 Unauthorized:**
- Token expired or invalid
- Check localStorage for auth_token
- Try logout and login again

**CORS Errors:**
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`

**Type Errors:**
- Ensure types in `src/types/api.ts` match backend responses
- Check backend Swagger documentation

## Performance Optimizations

1. **Code Splitting:** Next.js automatically splits per route
2. **Image Optimization:** Use `next/image` for images
3. **Query Caching:** TanStack Query handles invalidation
4. **Memoization:** Components wrapped with `useMemo`/`useCallback` where needed

## Accessibility (a11y)

- ✅ Semantic HTML (`<button>`, `<form>`, `<label>`)
- ✅ ARIA labels on interactive elements
- ✅ Keyboard navigation (Tab, Enter, Escape)
- ✅ Color contrast ratios meet WCAG AA
- ✅ Focus states on all interactive elements

## Deployment Preparation

### Pre-Deployment Checklist

- [ ] All pages tested locally
- [ ] API integration verified with backend
- [ ] Environment variables configured
- [ ] Build completes without errors: `npm run build`
- [ ] No console errors or warnings in dev tools
- [ ] TypeScript strict mode passes: `npm run type-check` (if added)

### Build Output

```bash
npm run build
# Outputs to: .next/
# Run with: npm start
```

### Environment Variables for Production

```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api
```

## Resources

- [Next.js Docs](https://nextjs.org/docs)
- [TanStack Query Docs](https://tanstack.com/query/latest)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com)

## Next Steps

1. **Meal Creation Pages** - `/meals/new` and `/meals/[id]/edit` with AI logging
2. **Add Modal Components** - Reusable modal wrapper with Tailwind
3. **Form Components** - Standardized input/select/textarea with validation
4. **Charts/Graphs** - Weekly nutrition trends visualization
5. **Mobile Navigation** - Hamburger menu for sm screens
6. **Dark Mode** - Toggle theme with CSS variables
7. **Error Boundaries** - React error boundaries for graceful failures
8. **Loading Skeletons** - Better UX during data fetching
9. **Toast Notifications** - Success/error alerts for mutations
10. **PWA Features** - Offline support, installable app

---

**Last Updated:** [Today's Date]
**Frontend Version:** 2.0.0 (Next.js Redesign)
**Backend Compatibility:** Phase 1 API (FastAPI)
