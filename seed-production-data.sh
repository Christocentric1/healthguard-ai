#!/bin/bash
# Seed production database with realistic data

echo "🌱 Seeding Production Database"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Install required packages if needed
echo "📦 Checking dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q motor pymongo python-dotenv 2>/dev/null

# Run the seed script
echo ""
echo "🚀 Running seed script..."
python3 scripts/seed_database.py

deactivate
cd ..

echo ""
echo "✅ Done! Your database is now populated with realistic data."
echo ""
echo "Next steps:"
echo "  1. Refresh your frontend"
echo "  2. Login with your test account"
echo "  3. You should now see live data from the API"
