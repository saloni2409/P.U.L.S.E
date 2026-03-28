# 🥗 P.U.L.S.E - Personal Unified Lifestyle & Sustenance Engine

> [!IMPORTANT]
> **New to the project?** Please read the [**Master Onboarding Guide**](./docs/PROJECT_ONBOARDING.md) for a comprehensive overview of the architecture, features, and setup instructions.

A comprehensive health app for tracking meals, analyzing macronutrients, and managing nutritional goals with AI-powered meal parsing and BYOK (Bring Your Own Key) security.

---

## ✨ Features

- 🤖 **AI-Powered Chat logging**: Natural language meal extraction through conversation.
- 🔐 **BYOK Security**: Use your own Gemini API key for total privacy and zero server-side costs.
- 📊 **Nutrition Analytics**: Automatic macro and calorie tracking with daily/weekly summaries.
- 📱 **Modern UI**: Clean, responsive dashboard built with Next.js 14 and Tailwind CSS.
- 🔌 **Extensible API**: Fully documented FastAPI backend for integration.

---

## 🚦 Quick Start

### 1. Requirements
- Python 3.9+
- Node.js 18+
- [Ollama](https://ollama.ai) (optional, for local LLM support)

### 2. Setup (5-Minute Installation)
```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend Setup
cd frontendV2
npm install
npm run dev
```

For full configuration (Encryption keys, Gemini API keys), see the [**Master Onboarding Guide**](./docs/PROJECT_ONBOARDING.md).

---

## 🏗️ Project Structure

```
P.U.L.S.E/
├── backend/            # FastAPI Backend
│   ├── app/            # Core logic, agents, and routes
│   └── tests/          # Comprehensive test suite
├── frontendV2/         # Next.js 14 Frontend
│   └── src/            # Components, hooks, and services
├── docs/               # System documentation & design
└── .github/            # Copilot & CI instructions
```

---

## 🔌 API & Development

- **Local Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs

---

## 🎓 Documentation Index

For deep dives into specific topics, refer to:
- [System Architecture](./docs/PHASE_1_DESIGN.md)
- [Chat Architecture & Diagrams](./docs/CHAT_ARCHITECTURE_DIAGRAMS.md)
- [Data Flow & sequence](./docs/CHAT_DATA_FLOW.md)
- [Data Models](./docs/CHAT_DATA_MODELS.md)
- [UI & Visual Design](./docs/CHAT_UI_DESIGN.md)
- [Developer Guide](./docs/CHAT_DEVELOPER_GUIDE.md)

---

## 📜 License
MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Support
For technical issues, check the [Onboarding Guide](./docs/PROJECT_ONBOARDING.md) or open an issue.
