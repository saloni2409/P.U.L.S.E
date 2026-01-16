# P.U.L.S.E Quick Start Guide

Get up and running with P.U.L.S.E in 5 minutes!

## System Requirements

- **Python:** 3.9 or higher
- **SQLite3:** Pre-installed on macOS/Linux
- **Ollama:** (Optional) For AI meal parsing features

## Step 1: Clone & Setup

```bash
# Navigate to project
cd /Users/saloni/GIT/P.U.L.S.E

# Create virtual environment
# python3.12 -m venv venv

python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -e .
cd ..

# Install frontend dependencies
cd frontend
pip install -e .
cd ..
```

## Step 2: Configure Environment

### Backend Setup

```bash
cd backend

# Create .env file
cat > .env << EOF
# LLM Configuration
LLM_SERVICE=local
LLM_LOCAL_ENDPOINT=http://localhost:11434
LLM_LOCAL_MODEL=llama2

# Database
DATABASE_URL=sqlite:///./pulse.db

# JWT
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
```

### Frontend Setup

```bash
cd frontend

# Create .env file
cat > .env << EOF
BACKEND_URL=http://localhost:8000
DEBUG=true
EOF
```

## Step 3: Optional - Setup Ollama (For AI Features)

```bash
# macOS
brew install ollama

# Start Ollama service
ollama serve

# In another terminal, pull a model
ollama pull llama2
```

## Step 4: Start Backend

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Step 5: Start Frontend (New Terminal)

```bash
cd frontend
python -m uvicorn app:app --host 0.0.0.0 --port 8001
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

## Step 5B: Start Next.js Frontend V2 (Alternative - New Terminal)

The new Next.js frontend is available in `frontendV2/` and provides a modern React experience.

```bash
# Install dependencies (first time only)
cd frontendV2
pnpm install

# Start development server
pnpm dev
```

You should see:
```
✓ Ready in X.Xs
- Local:        http://localhost:3000
```

**Frontend V2 Features:**
- Modern Next.js 14 with App Router
- TanStack Query for data fetching
- TypeScript strict mode
- Tailwind CSS styling
- JWT authentication

## Step 6: Access the Application

Open your browser:
- **Frontend (Legacy):** http://localhost:8001
- **Frontend V2 (Next.js):** http://localhost:3000
- **API Docs:** http://localhost:8000/docs

## Testing the Application

### 1. Register a New Account
1. Go to http://localhost:8001
2. Click "Register"
3. Enter email, password
4. Click "Create Account"

### 2. Log In
1. Enter your credentials
2. Click "Login"
3. You should see the dashboard

### 3. Test Meal Logging (AI Mode)
1. Click "Log Meal" on dashboard
2. Select "AI Parsing" tab
3. Enter meal description: "I had 2 scrambled eggs with whole wheat toast and orange juice"
4. Select meal type: "BREAKFAST"
5. Click "Log Meal with AI"
6. The AI will parse the meal and calculate macros

### 4. Check Dashboard
1. Navigate back to dashboard
2. You should see updated nutrition stats
3. Today's meals will show below the stats

### 5. View Meal History
1. Click "History" in the navigation
2. See all your logged meals

## API Testing with cURL

### Register
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Log Meal with AI
```bash
TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/meals-ai/log-ai \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "meal_description": "Grilled chicken breast with brown rice and broccoli",
    "meal_type": "LUNCH",
    "meal_date": "2025-12-23",
    "auto_enrich": true
  }'
```

### Get Daily Summary
```bash
TOKEN="your_access_token_here"

curl -X GET http://localhost:8000/api/nutrition/daily \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### Port Already in Use

If port 8000 or 8001 is already in use:

```bash
# Find process using port
lsof -i :8000
lsof -i :8001

# Kill process
kill -9 <PID>

# Or use different ports
python main.py --port 9000
python -m uvicorn app:app --port 9001
```

### LLM Not Available

If AI meal parsing fails:
1. Make sure Ollama is running: `ollama serve`
2. Check model is downloaded: `ollama list`
3. Falls back to manual entry if AI unavailable

### Database Issues

If database seems corrupted:

```bash
cd backend
rm pulse.db  # Delete old database
python main.py  # Creates fresh database
```

### Import Errors

Make sure virtual environment is activated:
```bash
source venv/bin/activate
```

## File Locations

| Component | Path |
|-----------|------|
| Backend Config | `backend/.env` |
| Backend Dependencies | `backend/pyproject.toml` |
| Frontend Config | `frontend/.env` |
| Frontend Dependencies | `frontend/pyproject.toml` |
| Database | `backend/pulse.db` |
| Backend Code | `backend/app/` |
| Frontend Code | `frontend/app/` |
| API Docs | `http://localhost:8000/docs` |

## Documentation

- **Full Overview:** `README.md`
- **Phase 1 Summary:** `docs/PHASE_1_COMPLETE.md`
- **System Design:** `docs/PHASE_1_DESIGN.md`
- **Frontend Details:** `docs/STAGE_4_COMPLETE.md`
- **Backend Details:** `docs/STAGE_3_COMPLETE.md`

## Common Workflows

### Logging a Meal (AI Mode)
1. Click "Log Meal" → AI Parsing tab
2. Enter description naturally (e.g., "Breakfast: eggs, toast, OJ")
3. Select meal type and date
4. AI automatically extracts items and macros
5. Saves to database

### Logging a Meal (Manual Mode)
1. Click "Log Meal" → Manual Entry tab
2. Enter meal description
3. Add food items individually
4. Enter quantities and servings
5. System calculates macros
6. Save to database

### Checking Progress
1. Go to Dashboard
2. See today's calorie/macro totals
3. View meal breakdown
4. Check weekly trends

## Next Steps

- Explore the API documentation: `http://localhost:8000/docs`
- Read the full design document: `docs/PHASE_1_DESIGN.md`
- Check out the detailed completion guides: `docs/STAGE_*_COMPLETE.md`

## Support

For issues or questions:
1. Check the relevant documentation in `docs/`
2. Review API docs at `http://localhost:8000/docs`
3. Check application logs in the terminal

---

**Enjoy tracking your nutrition with P.U.L.S.E!** 🫀
