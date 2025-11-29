# Authentication Testing Guide

Complete guide for testing user registration, login, and authentication in Cyber HealthGuard AI.

---

## 🔐 Authentication System Overview

The system uses **JWT (JSON Web Tokens)** for authentication with the following features:

- **User Registration**: Create new user accounts
- **User Login**: Authenticate and receive JWT tokens
- **Token-based Auth**: All protected endpoints require valid JWT tokens
- **Role-based Access**: Admin, User, and Analyst roles
- **Multi-tenancy**: Users are linked to organizations

---

## 🚀 Quick Start: Testing with cURL

### 1. Register a New User

```bash
curl -X POST https://YOUR-RAILWAY-URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@hospital.com",
    "password": "SecurePass123!",
    "full_name": "John Doe",
    "organisation_id": "org_001",
    "role": "user"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "user_abc123",
    "email": "john.doe@hospital.com",
    "full_name": "John Doe",
    "organisation_id": "org_001",
    "role": "user",
    "created_at": "2025-11-21T00:30:00Z",
    "is_active": true
  }
}
```

**Save the `access_token` - you'll need it for authenticated requests!**

---

### 2. Login with Existing Account

```bash
curl -X POST https://YOUR-RAILWAY-URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@hospital.com",
    "password": "SecurePass123!"
  }'
```

**Response:** Same as registration (returns token + user info)

---

### 3. Get Current User Info (Authenticated)

```bash
curl -X GET https://YOUR-RAILWAY-URL/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Replace `YOUR_ACCESS_TOKEN` with the token from registration/login.

**Response:**
```json
{
  "user_id": "user_abc123",
  "email": "john.doe@hospital.com",
  "full_name": "John Doe",
  "organisation_id": "org_001",
  "role": "user",
  "created_at": "2025-11-21T00:30:00Z",
  "is_active": true
}
```

---

### 4. Make Authenticated API Requests

Now you can use your token to access protected endpoints:

```bash
# Get alerts (with JWT token)
curl -X GET https://YOUR-RAILWAY-URL/api/alerts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get endpoints
curl -X GET https://YOUR-RAILWAY-URL/api/endpoints \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get compliance status
curl -X GET https://YOUR-RAILWAY-URL/api/compliance/status \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🌐 Testing with Swagger UI

### Step 1: Open API Documentation

Visit: **https://YOUR-RAILWAY-URL/docs**

### Step 2: Register a User

1. Scroll to **Authentication** section
2. Click **POST /api/auth/register**
3. Click **"Try it out"**
4. Fill in the request body:
   ```json
   {
     "email": "test@example.com",
     "password": "TestPass123!",
     "full_name": "Test User",
     "organisation_id": "org_test",
     "role": "user"
   }
   ```
5. Click **"Execute"**
6. **Copy the `access_token`** from the response

### Step 3: Authorize Swagger

1. Scroll to top of page
2. Click **"Authorize"** button (lock icon)
3. In the dialog:
   - **Value**: Paste your token (just the token, no "Bearer " prefix)
4. Click **"Authorize"**
5. Click **"Close"**

### Step 4: Test Protected Endpoints

Now all requests will include your JWT token automatically!

1. Try **GET /api/auth/me** to verify authentication
2. Try **GET /api/alerts** to fetch alerts
3. Try any other endpoint - they're all authenticated now!

---

## 🧪 Testing Scenarios

### Scenario 1: New User Registration

```bash
# Register new user
curl -X POST https://YOUR-RAILWAY-URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@hospital.com",
    "password": "AlicePass2024!",
    "full_name": "Alice Johnson",
    "organisation_id": "org_001",
    "role": "admin"
  }'
```

**Expected**: 201 Created, returns token + user info

---

### Scenario 2: Duplicate Email Registration

```bash
# Try to register with same email again
curl -X POST https://YOUR-RAILWAY-URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@hospital.com",
    "password": "DifferentPass!",
    "full_name": "Alice Smith",
    "organisation_id": "org_001",
    "role": "user"
  }'
```

**Expected**: 400 Bad Request, "Email already registered"

---

### Scenario 3: Invalid Login

```bash
# Try to login with wrong password
curl -X POST https://YOUR-RAILWAY-URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@hospital.com",
    "password": "WrongPassword"
  }'
```

**Expected**: 401 Unauthorized, "Incorrect email or password"

---

### Scenario 4: Access Without Token

```bash
# Try to access protected endpoint without token
curl -X GET https://YOUR-RAILWAY-URL/api/alerts
```

**Expected**: 403 Forbidden, "Not authenticated"

---

### Scenario 5: Access With Invalid Token

```bash
# Try with invalid/expired token
curl -X GET https://YOUR-RAILWAY-URL/api/auth/me \
  -H "Authorization: Bearer invalid_token_here"
```

**Expected**: 401 Unauthorized, "Could not validate credentials"

---

## 👥 User Roles

### Admin
- Full access to all resources
- Can manage users and organizations
- Can view all alerts and compliance data

### User (Default)
- Standard access to their organization's data
- Can view alerts and compliance
- Can create logs and endpoints

### Analyst
- Advanced access for security analysis
- Can view detailed threat data
- Can create and update alerts

---

## 🔑 Environment Variables

Add these to Railway:

```bash
SECRET_KEY=generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 days
```

**Generate a secure secret key:**
```bash
openssl rand -hex 32
```

---

## 📝 API Endpoints Summary

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/auth/register` | POST | No | Register new user |
| `/api/auth/login` | POST | No | Login and get token |
| `/api/auth/me` | GET | Yes | Get current user info |
| `/api/auth/logout` | POST | Yes | Logout (client-side) |
| `/api/alerts` | GET | Yes | Get alerts |
| `/api/endpoints` | GET | Yes | Get endpoints |
| `/api/compliance/status` | GET | Yes | Get compliance status |
| `/api/logs` | POST | Yes | Ingest logs |

---

## 🐛 Common Issues & Solutions

### Issue: "Email already registered"
**Solution**: Use a different email or login with existing credentials

### Issue: "Could not validate credentials"
**Solution**: Check that you're passing the token correctly:
- Header: `Authorization: Bearer YOUR_TOKEN`
- No extra spaces or quotes

### Issue: "Not authenticated"
**Solution**: Include Authorization header with valid JWT token

### Issue: "Invalid email format"
**Solution**: Ensure email follows format: `user@domain.com`

### Issue: Token expired
**Solution**: Login again to get a new token (tokens last 30 days)

---

## 🔄 Frontend Integration Example

### JavaScript/TypeScript

```typescript
// Register
const register = async (email: string, password: string, fullName: string) => {
  const response = await fetch('https://YOUR-RAILWAY-URL/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      password,
      full_name: fullName,
      organisation_id: 'org_001',
      role: 'user'
    })
  });

  const data = await response.json();

  // Save token to localStorage
  localStorage.setItem('access_token', data.access_token);

  return data;
};

// Login
const login = async (email: string, password: string) => {
  const response = await fetch('https://YOUR-RAILWAY-URL/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);

  return data;
};

// Make authenticated request
const fetchAlerts = async () => {
  const token = localStorage.getItem('access_token');

  const response = await fetch('https://YOUR-RAILWAY-URL/api/alerts', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  return response.json();
};

// Logout
const logout = () => {
  localStorage.removeItem('access_token');
};
```

---

## 🎯 Next Steps

1. ✅ Register a test user account
2. ✅ Login and save your JWT token
3. ✅ Test accessing protected endpoints
4. ✅ Integrate authentication in your frontend
5. ✅ Set up user management UI

---

## 📚 Additional Resources

- **API Docs (Swagger)**: https://YOUR-RAILWAY-URL/docs
- **ReDoc**: https://YOUR-RAILWAY-URL/redoc
- **JWT Debugger**: https://jwt.io

---

**Happy Testing! 🚀**

For questions or issues, check the logs in Railway dashboard or open a GitHub issue.
