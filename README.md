# Cyber HealthGuard AI

A comprehensive cybersecurity monitoring and compliance platform for healthcare organizations, providing real-time threat detection, alert management, and HIPAA compliance tracking.

## Project Info

**Frontend**: React + TypeScript + Vite
**Backend**: FastAPI + Python
**Database**: MongoDB
**Lovable Project**: https://lovable.dev/projects/a0b0db34-b085-40b7-bc4a-da61fd78e4fa

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/a0b0db34-b085-40b7-bc4a-da61fd78e4fa) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## Deployment Options

### 🚀 Quick Start: Complete Stack Deployment

**Deploy the entire application (Backend + Frontend) in 20 minutes:**

📘 **[Full Stack Deployment Guide](deployment/FULL_STACK_DEPLOYMENT.md)** - Railway (Backend) + Netlify (Frontend)

This comprehensive guide covers:
- Railway backend deployment (FastAPI + MongoDB)
- Netlify frontend deployment (React)
- Connecting frontend to backend
- Environment variables setup
- CORS configuration
- Testing and troubleshooting

**Perfect for:** Production deployments, FREE tier available

---

### Individual Deployment Options

#### Frontend Deployment

**Option 1: Netlify (Recommended)**
Deploy the frontend to Netlify for global CDN distribution, automatic SSL, and seamless CI/CD.

**Quick Start:**
1. Push your code to GitHub
2. Connect repository to Netlify
3. Set environment variables
4. Deploy!

**Guide**: [deployment/NETLIFY.md](deployment/NETLIFY.md)

**Option 2: Lovable**
Simply open [Lovable](https://lovable.dev/projects/a0b0db34-b085-40b7-bc4a-da61fd78e4fa) and click on Share → Publish.

#### Backend Deployment

**Option 1: Railway (Cloud)**
Deploy the FastAPI backend and MongoDB to Railway's cloud platform.

**Guide**: [deployment/RAILWAY.md](deployment/RAILWAY.md)

**Option 2: Homelab (Self-hosted)**
Deploy to your own infrastructure using Docker Compose and Nginx.

**Guide**: [deployment/README.md](deployment/README.md)

## Environment Variables

Create a `.env.local` file in the root directory (copy from `.env.example`):

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# Environment
VITE_ENV=development

# Use mock data (true/false)
VITE_USE_MOCK_DATA=true
```

For production deployments, set these in your hosting platform's environment variable settings.

## Features

- 🛡️ **Real-time Security Monitoring**: Track alerts, threats, and anomalies
- 📊 **Dashboard**: Visual overview of security posture and risk scores
- 🚨 **Alert Management**: Prioritize and respond to critical security events
- 🏥 **HIPAA Compliance**: Track compliance requirements and generate reports
- 🔍 **Endpoint Monitoring**: Monitor individual endpoint health and status
- 🌓 **Dark Mode**: Built-in theme switching for user preference
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile

## Custom Domain

### Netlify
Navigate to Domain settings in Netlify dashboard and add your custom domain. SSL is automatic.

### Lovable
Navigate to Project > Settings > Domains and click Connect Domain.
Read more: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)
