# Nexus Backend

FastAPI backend for the Nexus dashboard.

## Prerequisites

- Python 3.10+
- A MongoDB Atlas cluster (or local MongoDB)

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create a .env file in this directory
cp .env.example .env   # then fill in your values
```

**.env file:**

```env
SECRET_KEY=your_secret_key_here
MONGODB_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/nexus

# Optional — only needed for Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Optional — only needed for profile image uploads
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

## Run

```bash
uvicorn main:app --reload
```

API runs at **http://localhost:8000**  
Interactive docs at **http://localhost:8000/docs**
