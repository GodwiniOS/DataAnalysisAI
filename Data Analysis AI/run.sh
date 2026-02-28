#!/bin/bash

# AI Data Lab - Unified Run Script
# This script performs health checks, environment validation, and starts both backend and frontend.

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI Data Lab Health Check & Launch ===${NC}"

# 0. Handle Arguments
if [ "$1" == "new" ]; then
    echo -e "${YELLOW}[0/4] Clearing History (New Session requested)...${NC}"
    rm -rf backend/data
    echo -e "  - backend/data cleared: OK"
fi

# 1. Sanity Checks: Dependencies
echo -e "\n${YELLOW}[1/4] Checking System Dependencies...${NC}"

check_cmd() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed.${NC}"
        exit 1
    else
        echo -e "  - $1: $( $1 --version )"
    fi
}

check_cmd "python3"
check_cmd "node"
check_cmd "npm"

# 2. Environment Sanitization
echo -e "\n${YELLOW}[2/4] Validating Environment...${NC}"

if [ ! -f "backend/.env" ]; then
    echo -e "${RED}Error: backend/.env not found.${NC}"
    echo -e "Please create a .env file in the backend directory with your OPENAI_API_KEY."
    exit 1
fi

# Check for OPENAI_API_KEY in .env
if ! grep -q "OPENAI_API_KEY" "backend/.env"; then
    echo -e "${RED}Error: OPENAI_API_KEY not found in backend/.env${NC}"
    exit 1
fi
echo -e "  - backend/.env: OK"

# Check and Kill ports if in use
kill_port() {
    local PORT=$1
    local PID=$(lsof -Pi :$PORT -sTCP:LISTEN -t)
    if [ ! -z "$PID" ]; then
        echo -e "${YELLOW}  - Port $PORT is in use by PID $PID. Killing it...${NC}"
        kill -9 $PID
        sleep 1
    fi
}

kill_port 8000 # Backend
kill_port 3000 # Frontend

# 3. Dependency Setup
echo -e "\n${YELLOW}[3/4] Ensuring Dependencies...${NC}"

# Backend Setup
echo "  - Setting up Backend (Python)..."
cd backend
if [ ! -d "venv" ]; then
    echo "    - Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null
cd ..

# Frontend Setup
echo "  - Setting up Frontend (Next.js)..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "    - Installing npm packages (this might take a minute)..."
    npm install > /dev/null
fi
cd ..

# 4. Unified Launch
echo -e "\n${YELLOW}[4/4] Launching Services...${NC}"

# Function to handle cleanup on exit
cleanup() {
    echo -e "\n${RED}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup SIGINT

# Start Backend
echo -e "${GREEN}Starting Backend...${NC}"
cd backend
source venv/bin/activate
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to be healthy
echo -n "Waiting for Backend to initialize..."
MAX_RETRIES=10
COUNT=0
while ! curl -s http://localhost:8000/ > /dev/null; do
    sleep 1
    echo -n "."
    COUNT=$((COUNT+1))
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo -e "\n${RED}Error: Backend failed to start in time.${NC}"
        kill $BACKEND_PID
        exit 1
    fi
done
echo -e " ${GREEN}Ready!${NC}"

# Start Frontend
echo -e "${GREEN}Starting Frontend...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "\n${GREEN}==========================================${NC}"
echo -e "${GREEN}  AI Data Lab is now running!${NC}"
echo -e "${GREEN}  - Frontend: ${NC}${YELLOW}http://localhost:3000${NC}"
echo -e "${GREEN}  - Backend:  ${NC}${YELLOW}http://localhost:8000${NC}"
echo -e "${GREEN}==========================================${NC}"
echo -e "Press ${YELLOW}Ctrl+C${NC} to stop both services."

# Keep script running
wait
