# 🚀 P.U.L.S.E Quick Start Guide

> [!TIP]
> For a detailed technical overview and onboarding, see the [**Master Onboarding Guide**](./docs/PROJECT_ONBOARDING.md).

Get up and running with P.U.L.S.E in 5 minutes!

---

## 🚦 System Requirements

- **Python:** 3.9 or higher
- **Node.js:** 18 or higher (for the modern frontend)
- **SQLite3:** Pre-installed on macOS/Linux
- **Google Gemini API Key:** (Recommended) For chat meal logging

---

## 🛠️ Step 1: Clone & Setup

```bash
# Navigate to project
cd /Users/saloni/GIT/P.U.L.S.E

# Setup Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py  # First run initializes database

# Setup Frontend (New terminal)
cd frontendV2
npm install
npm run dev
```

---

## ⚙️ Step 2: Configuration

### Backend Setup
Create or update `backend/.env`:
```env
# Database
DATABASE_URL=sqlite:///./pulse.db

# JWT & Security
SECRET_KEY=your-super-secret-key
ENCRYPTION_KEY=<fernet-encryption-key-see-onboarding-doc>

# AI Engine (Recommended approach)
BYOK_ENABLED=true
REQUIRE_USER_KEY=true
GEMINI_MODEL=gemini-1.5-pro
```

### Frontend Setup
Create or update `frontendV2/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🏃 Step 3: Running the Application

1. **Start Backend Server**:
   ```bash
   cd backend
   python main.py
   ```
   *Dashboard available at: http://localhost:8000/docs*

2. **Start Frontend Server**:
   ```bash
   cd frontendV2
   npm run dev
   ```
   *Application available at: http://localhost:3000*

---

## 💡 Step 4: First-Time Use

1. **Login**: Go to http://localhost:3000/register and create an account.
2. **Setup AI**: Go to **Settings → Gemini API** and paste your API key from [Google AI Studio](https://aistudio.google.com/).
3. **Log a Meal**: Go to **Meals** and click a "Chat" button for any meal type.
4. **Chat**: Input naturally: *"I had 2 scrambled eggs, wheat toast, and a glass of orange juice"* and watch P.U.L.S.E parse it!

---

## ❓ Troubleshooting

### Port Conflicts
- **Port 8000**: Used by backend. Change in `main.py` if needed.
- **Port 3000**: Used by frontend. Change with `npm run dev -- -p 3001`.

### Database Issues
If you encounter database errors:
```bash
rm backend/pulse.db
cd backend
python main.py  # Re-initializes fresh database
```

---
*For more help, consult the [Onboarding Guide](./docs/PROJECT_ONBOARDING.md).*
