# FinLens API & Auth Contracts

## 1. Environment Variables (.env)
Required keys across services:
- SUPABASE_URL=your_supabase_url
- SUPABASE_ANON_KEY=your_supabase_anon_key
- SUPABASE_JWT_SECRET=your_jwt_secret
- GROQ_API_KEY=your_groq_key

## 2. Authentication Header
All requests from Frontend to Backend MUST include:
Authorization: Bearer <SUPABASE_ACCESS_TOKEN>

## 3. Endpoints

### Endpoint A: Upload & Analyze Invoice
- Route: POST /api/v1/analyze
- Request Headers: 
  - Authorization: Bearer <SUPABASE_ACCESS_TOKEN>
- Request Body (Form Data):
  - file: (PDF or image file)
- Expected Response (JSON):
{
  "status": "success",
  "data": {
    "filename": "receipt_01.pdf",
    "risk_score": 85,
    "audit_flags": [
      "Tax rate higher than standard 18%",
      "Unregistered Vendor ID"
    ],
    "mcp_deduction_result": 45.00
  }
}

### Endpoint B: Fetch History
- Route: GET /api/v1/history
- Request Headers:
  - Authorization: Bearer <SUPABASE_ACCESS_TOKEN>
- Expected Response (JSON):
[
  {
    "id": "uuid-1",
    "filename": "receipt_01.pdf",
    "risk_score": 85,
    "created_at": "2026-08-27T10:30:00Z"
  }
]
