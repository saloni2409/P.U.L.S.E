# 🥗 P.U.L.S.E - Master Onboarding Guide
## Personal Unified Lifestyle & Sustenance Engine

Welcome to the **P.U.L.S.E** project! This document serves as the single source of truth for onboarding, architecture, and development across the entire system.

---

## 📋 Table of Contents
1. [🚀 Project Overview](#-project-overview)
2. [✨ Key Features](#-key-features)
3. [🛠️ Technology Stack](#️-technology-stack)
4. [🏗️ System Architecture](#️-system-architecture)
5. [🔐 Security & BYOK](#-security--byok)
6. [🚦 Getting Started](#-getting-started)
7. [🔌 API Reference](#-api-reference)
8. [🗄️ Database Schema](#️-database-schema)
9. [🧪 Testing & Quality](#-testing--quality)
10. [📈 Implementation Roadmap](#-implementation-roadmap)

---

## 🚀 Project Overview

**P.U.L.S.E** is an AI-powered health and nutrition management platform designed to make meal logging as natural as sending a text. By leveraging Large Language Models (LLMs) and a modular agent-based architecture, it transforms unstructured user descriptions into precise nutritional data.

### Mission
To provide a seamless, private, and intelligent experience for tracking nutrition without the friction of traditional manual entry.

---

## ✨ Key Features

- 🤖 **AI-Powered Chat Logging**: Natural language meal extraction using Google Gemini.
- 🔐 **BYOK (Bring Your Own Key)**: Users provide their own API keys for total privacy and zero server-side LLM costs.
- 📊 **Nutrition Tracking**: Automatic calculation of calories, proteins, carbs, and fats.
- 💬 **Multi-turn Conversations**: Context-aware AI that asks clarifying questions.
- ✏️ **Editable Meals**: Review and refine AI-parsed items before they hit your log.
- 📱 **Responsive Design**: Modern, premium UI built for both desktop and mobile.

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python (FastAPI), SQLAlchemy, Pydantic |
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS |
| **AI/LLM** | Google Gemini 1.5 Pro |
| **Database** | SQLite (with migration support via Alembic) |
| **Auth** | JWT (JSON Web Tokens) |
| **Security** | AES-256 (Fernet) for API key encryption |

---

## 🏗️ System Architecture

### 1. High-Level Data Flow
The system follows a modular flow from the user's message to the final database record:
1. **Frontend**: User sends a natural language message (e.g., "I had 2 eggs and toast").
2. **API Layer**: FastAPI receives the message, validates the JWT, and loads the user's session.
3. **Agent Orchestrator**: Manages the conversation state and coordinates individual agents.
4. **GoogleAIService**: Decrypts the user's Gemini key and calls the AI for parsing.
5. **Database**: Stores messages, session states, and finally the validated meal entry.

### 2. Multi-Agent Design
Our AI implementation is split into specialized agents for better reliability:
- **Root Agent**: Handles the "human" side—greeting, asking questions, and gathering info.
- **Parser Agent**: Takes the conversation and turns it into a structured list of food items.
- **Nutrition Agent**: Looks up nutritional data for each parsed item and calculates totals.

---

## 🔐 Security & BYOK

P.U.L.S.E uses a **"Bring Your Own Key" (BYOK)** model. This ensures that users retain control over their data and costs.

### Key Management Lifecycle:
1. **Input**: User enters their Google Gemini API key in the settings.
2. **Encryption**: The backend encrypts the key using **AES-256 (Fernet)** before it touches the disk.
3. **Storage**: Only the encrypted string is stored in the database.
4. **Usage**: The key is decrypted *only in memory* during an active AI request and immediately wiped afterward.
5. **Privacy**: P.U.L.S.E developers never see or store unencrypted user keys.

---

## 🚦 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- A Google Gemini API Key (get one at [Google AI Studio](https://aistudio.google.com/))

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Generate your master encryption key (DO NOT LOSE THIS)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Configure your `.env` file:
```env
# backend/.env
ENCRYPTION_KEY=<your-generated-fernet-key>
BYOK_ENABLED=true
REQUIRE_USER_KEY=true
GEMINI_MODEL=gemini-1.5-pro
```

### 2. Frontend Setup
```bash
cd frontendV2
npm install
npm run dev
```

### 3. First Login
1. Register/Login at `http://localhost:3000`.
2. Navigate to **Settings → Gemini API**.
3. Paste your Gemini API key and save.
4. Go to **Meals** and click a "Chat" button to start logging!

---

## 🔌 API Reference

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/meals-ai/chat/start` | POST | Initialize a new chat session | JWT |
| `/api/meals-ai/chat/send-message` | POST | Send a message to the AI agent | JWT |
| `/api/meals-ai/chat/summary` | GET | Retrieve current parsed meal items | JWT |
| `/api/meals-ai/chat/save` | POST | Finalize and save meal to log | JWT |
| `/api/user/gemini-key` | POST | Securely save the user's API key | JWT |

---

## 🗄️ Database Schema

### `chat_sessions`
| Field | Type | Description |
|-------|------|-------------|
| `session_id` | UUID (PK) | Unique identifier for the chat session |
| `user_id` | FK | Link to the User model |
| `session_state` | ENUM | `COLLECTING`, `CONFIRMING`, `SAVED`, `CANCELLED` |
| `parsed_meal_items` | JSON | Structured data for meal items |

### `chat_messages`
| Field | Type | Description |
|-------|------|-------------|
| `message_id` | UUID (PK) | Unique message identifier |
| `role` | STRING | `user`, `assistant`, or `system` |
| `content` | TEXT | The actual message text |

---

## 🧪 Testing & Quality

We maintain high standards with comprehensive testing:
- **Backend Tests**: Run `pytest` in the `backend/` directory.
- **AI Integration**: Specific test suites for the Google AIService and Agent logic.
- **BYOK Verification**: Dedicated tests for encryption/decryption roundtrips.

```bash
cd backend
pytest tests/test_byok.py -v
```

---

## 📈 Implementation Roadmap

### Phase 1: Core BYOK (Status: ✅ Complete)
- AES-256 Encryption Service.
- Secure Key Settings UI.
- UserGeminiKey Database Integration.

### Phase 2: AI Agents (Status: ✅ Complete)
- Google Gemini Integration.
- Root, Parser, and Nutrition Agents.
- Chat Session Management.

### Phase 3: Advanced UI (Status: 🔄 In Progress)
- Real-time message polling.
- Inline editable meal tables.
- Enhanced nutrition visualizations.

### Phase 4: Production Polish (Status: 📋 Planned)
- WebSocket support for real-time streaming.
- Voice-to-meal processing.
- Image-based meal recognition.

---

## 📞 Support & Resources

- **Main Repository**: `saloni2409/P.U.L.S.E`
- **Architecture Docs**: [docs/CHAT_DATA_FLOW.md](CHAT_DATA_FLOW.md)
- **Technical Guide**: [docs/CHAT_IMPLEMENTATION.md](CHAT_IMPLEMENTATION.md)
- **Design Visuals**: [docs/CHAT_ARCHITECTURE_DIAGRAMS.md](CHAT_ARCHITECTURE_DIAGRAMS.md)

---
*Created by the P.U.L.S.E Development Team | 2026*
