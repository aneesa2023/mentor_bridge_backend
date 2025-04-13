# 🧠 MentorBridge Backend

Welcome to the **FastAPI backend** for **MentorBridge** — an AI-powered, women-first mentorship platform that facilitates safe, role-aware connections between mentors and mentees across industries, levels, and lived experiences.

This backend powers features like profile-based AI matching, secure role-specific onboarding, daily affirmations, anonymous ask walls, and emotional conversation coaching — all backed by a modular, privacy-conscious, serverless infrastructure.

---

## 🌟 Key Features

- 🔐 **Auth0 Role-Based Authentication**: Secure onboarding and access control for mentors and mentees, with support for Safe Mode to hide sensitive profile details like contact info and photos.
- 🤝 **AI-Powered Matching Engine**:
  - Phase 1: Rule-based matching based on language, industry, availability, tags, and vector similarity.
  - Phase 2: Gemini refinement adds emotional intelligence with final score + reasoned matches.
- 🧠 **Gemini-Powered AI Tools**:
  - **Intro Assistant**: Helps mentees craft confident first messages.
  - **Conversation Coach**: Reframes difficult career questions with empathy and clarity.
  - **Affirmation Mode**: Daily AI-generated affirmations for motivation and emotional support.
- 💬 **Anonymous Ask Wall**: Allows mentees to post questions anonymously, receive community support and AI-generated replies without revealing their identity.
- 🎉 **Celebrate Your Win**: Users log wins and receive a custom encouragement message generated via Gemini.
- 📜 **AI Summary Generator**: Fetches profile data and creates a thoughtful mentor summary using Gemini for better discovery.

---

## 🏗️ Tech Stack

| Layer               | Tech Used                        |
|---------------------|----------------------------------|
| **API Framework**   | FastAPI (Python 3.11)            |
| **Deployment**      | AWS Lambda via Serverless Framework |
| **Authentication**  | Auth0 with JWT role-based control |
| **Database**        | MongoDB Atlas (NoSQL)            |
| **AI Integration**  | Google Gemini API (v1beta)       |
| **Storage**         | AWS S3 (for profile photo hosting) |
| **Routing & Access**| AWS API Gateway, IAM             |
| **Monitoring**      | AWS CloudWatch                   |

---

## 🔐 Authentication & Security

- Secure Auth0 JWT validation with role-based access
- Profile visibility can be controlled via `safe_mode`
- Only select fields exposed publicly via `visible_fields`
- Anonymous posting is handled without storing PII

---

## 🚀 Endpoints Overview (Highlights)

| Endpoint              | Description                              |
|-----------------------|------------------------------------------|
| `/affirmation`        | Generates AI affirmations via Gemini     |
| `/intro-message`      | Generates a warm intro message           |
| `/coach`              | Reframes a hard question empathetically  |
| `/ask-reply`          | Returns an anonymous, kind reply         |
| `/celebrate`          | Sends an encouraging win message         |
| `/gemini-summary`     | Generates mentor summary for frontend    |
| `/api/users/init`     | Auth0 token validation & role extraction |

---

## 🧩 Matching Logic

### Phase 1: Score Calculation (Out of 100)

- Language match: 15 points
- Industry/domain match: 15 points each
- Tech stack overlap: 15 points
- Mentee type alignment: 10 points
- Availability overlap: 10 points
- Profile vector cosine similarity: 20 points

### Phase 2: Gemini Refinement

- Compares goals, values, communication/mentoring style, and experience
- Returns final score + 2–3 human-like reasons for the match

---

## 📦 Structure & Organization

- `main.py`: FastAPI entrypoint with all routes
- `query_gemini()`: Generic Gemini wrapper
- Modular endpoints for `ask-reply`, `affirmation`, `coach`, `intro-message`, and `celebrate`
- `TEMPLATES`: Predefined prompt templates used across features

---

## 🧠 Design Philosophy

- ✨ Human-first AI: Gemini is used only where it enhances emotional connection and safety
- 🔐 Safety by default: Minimal data exposure, anonymous posting, and secure storage
- 🪄 Empathy in architecture: Every feature is shaped by real mentorship experiences and pain points

---

## 🛠 Deployment

The backend is deployed using the **Serverless Framework** targeting AWS Lambda. Environment variables (Auth0 keys, Gemini API key, MongoDB URI) are managed securely via `.env` and AWS Secrets Manager.

---

## 👩‍💻 Built With Love For

- Women navigating career growth, transitions, and identity
- Mentors who want to give back meaningfully and safely
- Communities that value emotional support as much as technical guidance

---

> For questions or contributions, feel free to open an issue or pull request. Let's build a better mentorship experience — together.
