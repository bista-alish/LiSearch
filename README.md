---
title: LiSearch - Liquor Store AI Assistant
emoji: 🍷
colorFrom: purple
colorTo: blue
sdk: streamlit
sdk_version: "1.29.0"
app_file: app.py
pinned: false
---

# LiSearch - Liquor Store AI Assistant 🍷

An AI-powered chat assistant for liquor store inventory and sales analytics.

## Features
- 📈 Top selling products analysis
- 🔥 Trending items detection
- 🔍 Natural language product search
- 📦 Inventory status monitoring
- 📊 Sales analytics by category

## Tech Stack
- Streamlit for UI
- Gemini AI for natural language processing
- Supabase (PostgreSQL) for database
- Python 3.10+

## Setup
1. Add your environment variables in HuggingFace Spaces Settings:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `GEMINI_API_KEY`

2. The app will start automatically!

## Usage
Ask natural language questions like:
- "What are the top 5 selling wines?"
- "Show me trending beers this week"
- "What products are low in stock?"
- "Search for citrus flavor drinks"