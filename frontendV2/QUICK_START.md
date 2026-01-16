# P.U.L.S.E Frontend - Quick Start Guide

## For Users

### Running the App Locally

1. **Start the Backend** (if not already running):
   ```bash
   cd /Users/saloni/GIT/P.U.L.S.E/backend
   python main.py
   ```
   Backend will run on `http://localhost:8000`

2. **Start the Frontend**:
   ```bash
   cd /Users/saloni/GIT/P.U.L.S.E/frontendV2
   npm run dev
   ```
   Frontend will run on `http://localhost:3000`

3. **Open in Browser**:
   Navigate to `http://localhost:3000`

### First Time Using the App

1. **Create Account**
   - Click "Sign Up" or go to `/register`
   - Enter username, email, password (8+ characters)
   - Confirm password
   - Set daily calorie goal (default: 2000 kcal)
   - Accept terms
   - Click "Create Account"
   - You'll be automatically logged in and redirected to dashboard

2. **Explore Dashboard**
   - View today's nutrition summary
   - See total calories, protein, carbs, fat
   - Quick action buttons to log meals or adjust settings

3. **Log Your First Meal**
   - Click "Log Meal" button
   - Enter meal details
   - Add food items with quantities
   - Save and see updated nutrition stats

4. **View Your Meals**
   - Go to "Meals" tab
   - Navigate dates with arrow buttons or date picker
   - See meal breakdown by type
   - Edit or delete meals as needed

5. **Configure Settings**
   - Go to "Settings" tab
   - Update profile information
   - Adjust daily calorie goal
   - Fine-tune macro targets (protein/carbs/fat percentages)
   - See estimated grams for each macro

### Key Pages

| Page | URL | Purpose |
|------|-----|---------|
| Landing | `/` | App overview, sign in/up links |
| Sign In | `/login` | User authentication |
| Sign Up | `/register` | Create new account |
| Dashboard | `/dashboard` | Nutrition overview, quick actions |
| Meals | `/meals` | View & manage meals by date |
| Settings | `/settings` | Profile & nutrition targets |

### Keyboard Shortcuts

- `Tab` - Navigate between form fields and buttons
- `Enter` - Submit forms, activate buttons
- `Escape` - Close dropdowns/modals (when implemented)

### Troubleshooting

**"Connection refused" error**
- Make sure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local` is set correctly

**"Unauthorized" (401) error**
- Your session may have expired
- Log out and log back in
- Clear localStorage if issues persist:
  ```javascript
  // In browser console:
  localStorage.clear()
  // Then refresh page
  ```

**Page shows "Loading..." forever**
- Check browser console (F12 → Console tab) for errors
- Verify backend is responding to API requests (Network tab)
- Try refreshing the page

**Form validation errors**
- Read error messages carefully
- Password must be at least 8 characters
- Email format: `name@example.com`
- Macro percentages must add up to 100%

---

## For Developers

### Project Structure Overview

```
frontendV2/
├── src/
│   ├── app/              # Next.js pages (routing)
│   ├── components/       # React components
│   ├── config/           # API configuration
│   ├── hooks/            # Custom TanStack Query hooks
│   ├── services/         # API service layer
│   ├── store/            # Zustand state management
│   ├── types/            # TypeScript type definitions
│   └── globals.css       # Global styles & design system
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── tailwind.config.ts    # Tailwind CSS config
└── next.config.js        # Next.js config
```

### Common Tasks

#### View Current API Types
```bash
# Edit this file to add new types:
cat src/types/api.ts
```

#### Add New API Endpoint
1. Add endpoint to `src/config/api.ts` under `API_ENDPOINTS`
2. Add service method in `src/services/your-service.ts`
3. Create hook in `src/hooks/useYourHook.ts`
4. Use hook in component

#### Check Build Status
```bash
npm run build
# If successful: .next/ folder created
# If errors: see TypeScript errors in output
```

#### Test Production Build Locally
```bash
npm run build
npm start
# Navigate to http://localhost:3000
```

### Development Environment

**Environment Variables** (`.env.local`):
```env
# API Base URL - points to backend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Debugging Tools

**Browser DevTools** (F12):
- **Console** - See errors and logs
- **Network** - Monitor API requests/responses
- **Application → LocalStorage** - View stored auth token
- **Application → Cookies** - View session data

**React DevTools** (Browser Extension):
- Inspect component tree
- View prop values
- Track component renders

**TanStack Query DevTools**:
- Already configured in the app
- Shows cache state and queries
- Available in development mode

### Code Examples

**Fetch data with loading state:**
```typescript
import { useMeals } from '@/hooks/useMeals'

export function MyComponent() {
  const { data: meals, isLoading, error } = useMeals()
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading meals</div>
  
  return (
    <div>
      {meals?.map(meal => (
        <div key={meal.meal_id}>{meal.meal_description}</div>
      ))}
    </div>
  )
}
```

**Call API with mutation:**
```typescript
import { useCreateMeal } from '@/hooks/useMeals'

export function CreateMealForm() {
  const createMeal = useCreateMeal()
  
  const handleSubmit = async (formData) => {
    try {
      await createMeal.mutateAsync(formData)
      alert('Meal created!')
    } catch (error) {
      alert('Failed to create meal')
    }
  }
  
  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
      <button disabled={createMeal.isPending}>
        {createMeal.isPending ? 'Creating...' : 'Create'}
      </button>
    </form>
  )
}
```

**Handle authentication:**
```typescript
import { useAuthStore } from '@/store/authStore'
import { useRouter } from 'next/navigation'

export function MyComponent() {
  const { user, logout } = useAuthStore()
  const router = useRouter()
  
  const handleLogout = () => {
    logout()
    router.push('/login')
  }
  
  return (
    <div>
      <p>Hello, {user?.username}</p>
      <button onClick={handleLogout}>Sign Out</button>
    </div>
  )
}
```

### Git Workflow

```bash
# View changes
git status

# Add files
git add src/app/your-page/page.tsx

# Commit
git commit -m "feat: add your page"

# Push
git push origin main
```

### Performance Tips

1. **Use `useMemo` for expensive calculations**
   ```typescript
   const totalCalories = useMemo(() => {
     return meals?.reduce((sum, meal) => sum + meal.calories, 0) || 0
   }, [meals])
   ```

2. **Lazy load components**
   ```typescript
   import dynamic from 'next/dynamic'
   const HeavyComponent = dynamic(() => import('./HeavyComponent'))
   ```

3. **Optimize re-renders**
   - Avoid creating objects/functions in render
   - Use callback hooks when passing functions to children

### Running Tests (When Added)

```bash
npm test
# or
npm run test:watch
```

### TypeScript Checking

```bash
npx tsc --noEmit
# or add to package.json:
# "type-check": "tsc --noEmit"
npm run type-check
```

---

## Deployment

### Build for Production
```bash
npm run build
```

### Environment for Production
Update `.env.production` or `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api
```

### Deploy to Vercel (Recommended)

1. Push code to GitHub
2. Connect GitHub repo to Vercel
3. Add environment variable in Vercel dashboard
4. Deploy automatically on push

### Deploy to Other Platforms

**Docker:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

**Standalone Server:**
```bash
npm run build
npm start
```

---

## Support & Resources

**Documentation:**
- [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) - Detailed architecture
- [Backend API Docs](http://localhost:8000/docs) - Swagger documentation

**Need Help?**
- Check browser console for error messages
- Review backend API logs
- Verify environment variables
- Check TypeScript errors: `npm run type-check`

---

**Last Updated:** Today
**Version:** 2.0.0
