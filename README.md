# Credit Assistant

An AI-driven platform that helps users in India understand, track and improve their credit health. Users register, enter their financial data, and get personalised advice from Google Gemini, plus a dashboard that shows their progress over time.

**Stack:** FastAPI, Python, SQLAlchemy (SQLite by default, any SQL database works), React (Vite), Recharts, Google Gemini API, JWT auth.

## Scenarios covered

| Scenario | How it works |
|---|---|
| 1. Onboarding and initial assessment | `POST /records` saves the user's figures and calculates debt-to-income and utilization on the server |
| 2. AI-powered consultation | `POST /advice` sends the latest metrics to Gemini and returns a 5-step plan for Indian banking norms (falls back to rule-based advice if Gemini is unavailable) |
| 3. Progress tracking | `GET /dashboard` returns score history; the React dashboard draws it as a line chart |
| 4. Real-time monitoring | Each new update recalculates the improvement delta, bottlenecks and the utilization pie chart |

## Project structure

```
backend/
  main.py          API routes
  auth.py          password hashing + JWT
  models.py        SQLAlchemy tables
  schemas.py       request/response validation
  logic.py         DTI, utilization, categories, bottlenecks
  ai_service.py    Gemini integration + fallback
  schema.sql       reference SQL schema
frontend/
  src/components/  AuthPage, Dashboard, FinanceForm, ScoreChart, UtilizationPie, AdvisorPanel
```

## Run locally

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # add GEMINI_API_KEY and a random JWT_SECRET
uvicorn main:app --reload --port 8000
```
API docs: http://localhost:8000/docs. Get a Gemini key at https://aistudio.google.com/apikey. Without a key the app still works using the fallback advice.

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev                                          # http://localhost:5173
```

## API

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/register` | no | Create account, returns token |
| POST | `/auth/login` | no | Sign in, returns token |
| POST | `/records` | yes | Save a financial snapshot |
| GET | `/records` | yes | List snapshots |
| GET | `/dashboard` | yes | Latest metrics, history, pie data, bottlenecks |
| POST | `/advice` | yes | 5-step AI plan |

## Score bands used

Poor below 600, Fair 600-699, Good 700-749, Excellent 750 and above. Healthy targets: utilization under 30%, debt-to-income under 40%, zero missed payments.

## Notes

- Never commit `.env`. Set a strong `JWT_SECRET` before deploying.
- The app stores sensitive financial data. Use HTTPS, restrict CORS to your frontend URL, and add a privacy notice before real use.
- Advice is general guidance, not financial advice.

## License

MIT
