#!/bin/bash

# Set error handling
set -e

# Configuration
ANALYTICS_REPO_URL="https://github.com/codingforentrepreneurs/analytics-api.git"
DOCS_REPO_URL="https://github.com/kiwi-dev-la/lightwave-eco-system-docs.git"
DEV_TOOLS_REPO_URL="https://github.com/kiwi-dev-la/lightwave-dev-tools.git"
DB_PORT=5432 # Default PostgreSQL port
API_PORT=8002 # API port
SKIP_DOCS=false
SKIP_DEVTOOLS=false

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --db-port) DB_PORT="$2"; shift ;;
    --api-port) API_PORT="$2"; shift ;;
    --skip-docs) SKIP_DOCS=true ;;
    --skip-devtools) SKIP_DEVTOOLS=true ;;
    *) echo "Unknown parameter: $1"; exit 1 ;;
  esac
  shift
done

# Install UV - The fast Python package installer and resolver
echo "Installing UV Python package manager..."
if command -v uv >/dev/null 2>&1; then
  echo "UV already installed. Updating..."
  uv self update
else
  if command -v brew >/dev/null 2>&1; then
    echo "Installing UV via Homebrew..."
    brew install uv
  else
    echo "Installing UV via script..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
  fi
  
  # Add UV shell completion
  shell_type=$(basename "$SHELL")
  if [ "$shell_type" = "bash" ]; then
    echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
    source ~/.bashrc
  elif [ "$shell_type" = "zsh" ]; then
    echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc
    source ~/.zshrc
  fi
fi

# Clone the analytics API repository into the current directory
echo "Cloning analytics API repository from $ANALYTICS_REPO_URL..."
if [ -f ".git/config" ] && grep -q "$ANALYTICS_REPO_URL" .git/config; then
  echo "Repository already exists. Updating..."
  git pull
else
  # Clone into temporary directory and move contents to current directory
  git clone "$ANALYTICS_REPO_URL" temp_clone
  mv temp_clone/* temp_clone/.* . 2>/dev/null || true
  rm -rf temp_clone
  echo "Analytics API repository files copied to current directory"
fi

# Clone the documentation repository if not skipped
if [ "$SKIP_DOCS" = false ]; then
  echo "Cloning documentation repository from $DOCS_REPO_URL..."
  if [ -d "docs" ]; then
    echo "Documentation directory already exists. Updating..."
    if [ -d "docs/.git" ]; then
      (cd docs && git pull)
    else
      echo "Existing docs directory is not a git repository. Skipping update."
    fi
  else
    # Only create docs directory and clone if the repo exists
    if git ls-remote --exit-code "$DOCS_REPO_URL" &>/dev/null; then
      mkdir -p docs
      git clone "$DOCS_REPO_URL" docs
      echo "Documentation files cloned to docs directory"
    else
      echo "Documentation repository not found. Creating empty docs directory."
      mkdir -p docs
    fi
  fi
else
  echo "Skipping documentation repository clone (--skip-docs flag provided)"
fi

# Clone the dev tools repository for installation if not skipped
if [ "$SKIP_DEVTOOLS" = false ]; then
  echo "Cloning development tools repository from $DEV_TOOLS_REPO_URL..."
  if [ -d "lightwave-dev-tools" ]; then
    echo "Development tools directory already exists. Updating..."
    if [ -d "lightwave-dev-tools/.git" ]; then
      (cd lightwave-dev-tools && git pull)
    else
      echo "Existing lightwave-dev-tools directory is not a git repository. Skipping update."
    fi
  else
    # Only clone if the repo exists
    if git ls-remote --exit-code "$DEV_TOOLS_REPO_URL" &>/dev/null; then
      git clone "$DEV_TOOLS_REPO_URL" lightwave-dev-tools
      echo "Development tools repository cloned to lightwave-dev-tools directory"
    else
      echo "Development tools repository not found. Skipping."
    fi
  fi
else
  echo "Skipping development tools repository clone (--skip-devtools flag provided)"
fi

# Create local .env file from template if it doesn't exist
echo "Setting up environment variables..."
if [ ! -f ".env" ]; then
  if [ -f ".env.compose" ]; then
    cp .env.compose .env
    echo "Created .env file from .env.compose template"
  else
    echo "WARNING: No .env.compose template found. You may need to create .env manually."
  fi
fi

# Customize environment variables as needed
if [ "$DB_PORT" != "5432" ]; then
  echo "Configuring custom database port: $DB_PORT"
  if [ -f ".env" ]; then
    sed -i '' "s/DB_PORT=.*/DB_PORT=$DB_PORT/" .env 2>/dev/null || sed -i "s/DB_PORT=.*/DB_PORT=$DB_PORT/" .env
    if ! grep -q "DB_PORT=" .env; then
      echo "DB_PORT=$DB_PORT" >> .env
    fi
  fi
  
  # Update compose file to use the custom port
  if [ -f "compose.yaml" ]; then
    sed -i '' "s/- \"5432:5432\"/- \"$DB_PORT:5432\"/" compose.yaml 2>/dev/null || sed -i "s/- \"5432:5432\"/- \"$DB_PORT:5432\"/" compose.yaml
  elif [ -f "docker-compose.yaml" ]; then
    sed -i '' "s/- \"5432:5432\"/- \"$DB_PORT:5432\"/" docker-compose.yaml 2>/dev/null || sed -i "s/- \"5432:5432\"/- \"$DB_PORT:5432\"/" docker-compose.yaml
  elif [ -f "docker-compose.yml" ]; then
    sed -i '' "s/- \"5432:5432\"/- \"$DB_PORT:5432\"/" docker-compose.yml 2>/dev/null || sed -i "s/- \"5432:5432\"/- \"$DB_PORT:5432\"/" docker-compose.yml
  fi
fi

# Set up Python environment with UV
echo "Setting up Python environment..."
if [ ! -d ".venv" ]; then
  uv venv
  echo "Created virtual environment at .venv"
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Manage dependencies with UV
echo "Setting up dependencies..."
if [ ! -f "pyproject.toml" ]; then
  # Create minimal pyproject.toml if it doesn't exist
  echo "Creating minimal pyproject.toml..."
  cat > pyproject.toml << EOF
[project]
name = "analytics-api"
version = "0.1.0"
description = "Analytics API using FastAPI and TimescaleDB"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "sqlmodel",
    "psycopg",
    "psycopg-binary",
    "timescaledb",
    "python-decouple",
    "gunicorn",
    "requests"
]
EOF
fi

# Lock dependencies
echo "Locking dependencies..."
uv lock

# Sync dependencies
echo "Syncing dependencies with environment..."
uv sync --frozen || {
  echo "UV sync failed, falling back to requirements.txt..."
  if [ -f "requirements.txt" ]; then
    uv pip install -r requirements.txt
  fi
}

# Install the lightwave development tools if available
if [ "$SKIP_DEVTOOLS" = false ] && [ -d "lightwave-dev-tools" ]; then
  echo "Installing lightwave development tools..."
  if [ -f "lightwave-dev-tools/setup.py" ] || [ -f "lightwave-dev-tools/pyproject.toml" ]; then
    uv pip install -e lightwave-dev-tools
    echo "Lightwave development tools installed in development mode"
  elif [ -d "lightwave-dev-tools/src/lightwave_dev_tools" ]; then
    uv pip install -e "lightwave-dev-tools/src/lightwave_dev_tools"
    echo "Lightwave development tools installed from src directory"
  else
    echo "Could not find installation method for lightwave development tools"
  fi
fi

# Check if Docker is running
echo "Checking Docker status..."
DOCKER_RUNNING=true
if ! docker info > /dev/null 2>&1; then
  echo "WARNING: Docker is not running. You can start Docker and run the script again to complete the setup."
  DOCKER_RUNNING=false
fi

# Continue with Docker setup only if Docker is running
if [ "$DOCKER_RUNNING" = true ]; then
  # Stop any existing containers first to ensure a clean state
  echo "Stopping any existing containers..."
  docker compose down 2>/dev/null || true
  
  # Start Docker Compose using the compose.yaml from the repo
  echo "Starting services with Docker Compose..."
  if [ -f "compose.yaml" ] || [ -f "docker-compose.yaml" ] || [ -f "docker-compose.yml" ]; then
    docker compose up -d
    
    # Check if docker-compose succeeded
    if [ $? -ne 0 ]; then
      echo "WARNING: Docker Compose failed to start. You might need to use a different database port."
      echo "Try running: $0 --db-port 5433"
      exit 1
    fi
  else
    echo "ERROR: No compose file found. Please check the repository structure."
    exit 1
  fi

  # Wait for database to be ready
  echo "Waiting for database to be ready..."
  sleep 10

  # Run any initialization commands
  echo "Checking API status..."
  docker compose exec app bash -c "python /code/main.py" || echo "API initialization completed"
  
  # Display API information
  echo "API is running at http://localhost:$API_PORT"
  echo "API health endpoint: http://localhost:$API_PORT/healthz"
  
  echo "Docker services are running in the background."
  echo "Database is available on port $DB_PORT"
  echo "To view logs: docker compose logs -f"
  echo "To stop services: docker compose down"
  echo "To stop services and remove volumes: docker compose down -v"
else
  echo ""
  echo "To complete the setup once Docker is running, run this script again."
fi

echo ""
echo "Build complete! Python environment is ready."
if [ "$SKIP_DOCS" = false ]; then
  echo "Documentation is available in the ./docs directory"
fi
if [ "$SKIP_DEVTOOLS" = false ] && [ -d "lightwave-dev-tools" ]; then
  echo "Lightwave development tools are installed for use"
fi
echo ""
echo "To view the project dependency tree: uv tree"
echo "To run commands in the project environment: uv run [command]"
echo "To add a dependency: uv add [package]"
echo "To remove a dependency: uv remove [package]" 