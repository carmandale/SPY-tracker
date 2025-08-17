#!/bin/bash

# Render CLI Setup Script for SPY TA Tracker
# This script installs the Render CLI, handles authentication, and sets up production access

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RENDER_SERVICE_NAME="SPY-tracker"
PRODUCTION_URL="https://spy-tracker.onrender.com"

echo -e "${BLUE}🚀 SPY TA Tracker - Render CLI Setup${NC}"
echo "================================================="

# Function to print status messages
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check if Node.js is installed (required for Render CLI)
check_nodejs() {
    print_info "Checking Node.js installation..."
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first:"
        echo "  macOS: brew install node"
        echo "  Ubuntu: sudo apt-get install nodejs npm"
        echo "  Windows: Download from https://nodejs.org"
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    print_status "Node.js found: $NODE_VERSION"
}

# Install Render CLI
install_render_cli() {
    print_info "Checking Render CLI installation..."
    
    if command -v render &> /dev/null; then
        RENDER_VERSION=$(render --version 2>/dev/null || echo "unknown")
        print_status "Render CLI already installed: $RENDER_VERSION"
        return 0
    fi
    
    print_info "Installing Render CLI via npm..."
    if npm install -g @render/cli; then
        print_status "Render CLI installed successfully"
    else
        print_error "Failed to install Render CLI"
        print_info "You may need to run with sudo: sudo npm install -g @render/cli"
        exit 1
    fi
}

# Authenticate with Render
authenticate_render() {
    print_info "Checking Render authentication..."
    
    # Check if already authenticated
    if render auth status &> /dev/null; then
        AUTH_INFO=$(render auth status 2>/dev/null | head -1 || echo "authenticated")
        print_status "Already authenticated with Render: $AUTH_INFO"
        return 0
    fi
    
    print_info "Starting Render authentication process..."
    echo
    echo "You have two options to authenticate:"
    echo "1. Interactive login (opens browser)"
    echo "2. API token login (if you have a token)"
    echo
    
    while true; do
        read -p "Choose authentication method [1/2]: " auth_choice
        case $auth_choice in
            1)
                print_info "Opening browser for authentication..."
                if render auth login; then
                    print_status "Authentication successful!"
                    break
                else
                    print_error "Interactive authentication failed"
                    return 1
                fi
                ;;
            2)
                read -s -p "Enter your Render API token: " api_token
                echo
                if render auth login --token "$api_token"; then
                    print_status "Token authentication successful!"
                    break
                else
                    print_error "Token authentication failed. Please check your token."
                    return 1
                fi
                ;;
            *)
                print_warning "Please enter 1 or 2"
                ;;
        esac
    done
}

# Discover SPY-tracker service
discover_service() {
    print_info "Discovering SPY-tracker service..."
    
    # Get list of services
    if ! SERVICES_JSON=$(render services list --json 2>/dev/null); then
        print_error "Failed to list Render services. Please check your authentication."
        return 1
    fi
    
    # Parse JSON to find SPY-tracker service
    if command -v jq &> /dev/null; then
        SERVICE_ID=$(echo "$SERVICES_JSON" | jq -r '.[] | select(.name == "SPY-tracker") | .id' 2>/dev/null)
        SERVICE_STATUS=$(echo "$SERVICES_JSON" | jq -r '.[] | select(.name == "SPY-tracker") | .status' 2>/dev/null)
        SERVICE_URL=$(echo "$SERVICES_JSON" | jq -r '.[] | select(.name == "SPY-tracker") | .url' 2>/dev/null)
    else
        print_warning "jq not found. Using basic parsing (install jq for better JSON handling)"
        SERVICE_ID=$(echo "$SERVICES_JSON" | grep -o '"id":"[^"]*"' | grep -A1 -B1 "SPY-tracker" | head -1 | cut -d'"' -f4)
        SERVICE_STATUS="unknown"
        SERVICE_URL="$PRODUCTION_URL"
    fi
    
    if [ -n "$SERVICE_ID" ] && [ "$SERVICE_ID" != "null" ]; then
        print_status "Found SPY-tracker service: $SERVICE_ID"
        print_status "Status: $SERVICE_STATUS"
        print_status "URL: $SERVICE_URL"
        
        # Save service info for other scripts
        echo "RENDER_SERVICE_ID=$SERVICE_ID" > "scripts/.render-config"
        echo "RENDER_SERVICE_URL=$SERVICE_URL" >> "scripts/.render-config"
        echo "RENDER_SERVICE_STATUS=$SERVICE_STATUS" >> "scripts/.render-config"
        
        print_status "Service configuration saved to scripts/.render-config"
    else
        print_error "SPY-tracker service not found. Please check:"
        echo "  1. Service name matches exactly: $RENDER_SERVICE_NAME"
        echo "  2. You have access to the service"
        echo "  3. The service exists in your Render account"
        return 1
    fi
}

# Verify production connection
verify_production_connection() {
    print_info "Verifying production connection..."
    
    # Test health endpoint
    if command -v curl &> /dev/null; then
        print_info "Testing health endpoint: $PRODUCTION_URL/healthz"
        if HEALTH_RESPONSE=$(curl -s --max-time 10 "$PRODUCTION_URL/healthz"); then
            if echo "$HEALTH_RESPONSE" | grep -q '"status":"ok"'; then
                print_status "Health check passed"
            else
                print_warning "Health check returned unexpected response: $HEALTH_RESPONSE"
            fi
        else
            print_warning "Health check failed - service may be down or unreachable"
        fi
        
        # Test scheduler endpoint
        print_info "Testing scheduler endpoint: $PRODUCTION_URL/scheduler/status"
        if SCHEDULER_RESPONSE=$(curl -s --max-time 10 "$PRODUCTION_URL/scheduler/status"); then
            if echo "$SCHEDULER_RESPONSE" | grep -q '"status":"running"'; then
                print_status "Scheduler is running"
            else
                print_warning "Scheduler may not be running: $SCHEDULER_RESPONSE"
            fi
        else
            print_warning "Scheduler endpoint test failed"
        fi
    else
        print_warning "curl not found. Cannot test endpoints. Install curl for connection verification."
    fi
}

# Set up read-only database access configuration
setup_readonly_access() {
    print_info "Setting up read-only database access configuration..."
    
    # Create a template for database configuration
    cat > "scripts/.env.production-readonly" << 'EOF'
# Production Database Configuration (Read-Only)
# Copy this file and update with actual production values

# Get this from: render services env <service-id>
DATABASE_URL_READONLY="postgresql://readonly_user:password@host:5432/database"

# Production service information
PRODUCTION_SERVICE_ID=""
PRODUCTION_SERVICE_URL="https://spy-tracker.onrender.com"

# Safety flag to prevent accidental writes
READONLY_MODE=true
EOF

    print_status "Created scripts/.env.production-readonly template"
    print_info "Update this file with actual production database credentials"
}

# Install helpful tools
install_helper_tools() {
    print_info "Checking for helpful tools..."
    
    # Check for jq (JSON processor)
    if ! command -v jq &> /dev/null; then
        print_warning "jq not found. Installing jq for better JSON handling..."
        if command -v brew &> /dev/null; then
            brew install jq
            print_status "jq installed via brew"
        elif command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y jq
            print_status "jq installed via apt-get"
        else
            print_warning "Could not install jq automatically. Please install it manually:"
            echo "  macOS: brew install jq"
            echo "  Ubuntu: sudo apt-get install jq"
        fi
    else
        print_status "jq is available"
    fi
    
    # Check for curl
    if ! command -v curl &> /dev/null; then
        print_warning "curl not found. Please install curl for API testing."
    else
        print_status "curl is available"
    fi
}

# Create helper scripts
create_helper_scripts() {
    print_info "Creating helper scripts..."
    
    # Create production database connection script
    cat > "scripts/connect-production-db.sh" << 'EOF'
#!/bin/bash
# Quick script to connect to production database (read-only)

set -e

# Load configuration
if [ -f "scripts/.render-config" ]; then
    source "scripts/.render-config"
else
    echo "❌ Render configuration not found. Run scripts/render-setup.sh first."
    exit 1
fi

if [ -f "scripts/.env.production-readonly" ]; then
    source "scripts/.env.production-readonly"
else
    echo "❌ Production database configuration not found."
    echo "Please update scripts/.env.production-readonly with actual credentials."
    exit 1
fi

echo "🔍 Connecting to production database (read-only)..."
echo "Service: $RENDER_SERVICE_ID"

if [ -z "$DATABASE_URL_READONLY" ] || [[ "$DATABASE_URL_READONLY" == *"password"* ]]; then
    echo "❌ DATABASE_URL_READONLY not configured properly."
    echo "Please update scripts/.env.production-readonly with actual credentials."
    exit 1
fi

# Use psql if available, otherwise provide connection string
if command -v psql &> /dev/null; then
    echo "Opening psql connection..."
    psql "$DATABASE_URL_READONLY" -c "\dt" # List tables
else
    echo "psql not found. Connection string:"
    echo "$DATABASE_URL_READONLY"
fi
EOF

    chmod +x "scripts/connect-production-db.sh"
    print_status "Created scripts/connect-production-db.sh"
    
    # Create production health check script
    cat > "scripts/check-production-health.sh" << 'EOF'
#!/bin/bash
# Production health check script

set -e

# Load configuration
if [ -f "scripts/.render-config" ]; then
    source "scripts/.render-config"
else
    echo "❌ Render configuration not found. Run scripts/render-setup.sh first."
    exit 1
fi

echo "🏥 Checking production health..."
echo "Service: $RENDER_SERVICE_ID"
echo "URL: $RENDER_SERVICE_URL"
echo

# Health check
echo "1. API Health Check:"
if curl -s --max-time 10 "$RENDER_SERVICE_URL/healthz" | jq -r '.status' 2>/dev/null; then
    echo "   ✅ API is healthy"
else
    echo "   ❌ API health check failed"
fi

# Scheduler check  
echo "2. Scheduler Status:"
if SCHEDULER=$(curl -s --max-time 10 "$RENDER_SERVICE_URL/scheduler/status"); then
    if echo "$SCHEDULER" | jq -r '.status' 2>/dev/null | grep -q "running"; then
        JOBS_COUNT=$(echo "$SCHEDULER" | jq -r '.jobs_count' 2>/dev/null)
        echo "   ✅ Scheduler running with $JOBS_COUNT jobs"
    else
        echo "   ❌ Scheduler not running"
    fi
else
    echo "   ❌ Scheduler status check failed"
fi

# Service metrics via Render CLI
echo "3. Service Metrics:"
if render services get "$RENDER_SERVICE_ID" --json 2>/dev/null | jq -r '.status' >/dev/null; then
    STATUS=$(render services get "$RENDER_SERVICE_ID" --json 2>/dev/null | jq -r '.status')
    echo "   ✅ Service status: $STATUS"
else
    echo "   ❌ Could not fetch service metrics"
fi

echo
echo "Health check complete!"
EOF

    chmod +x "scripts/check-production-health.sh"
    print_status "Created scripts/check-production-health.sh"
}

# Main setup process
main() {
    echo
    print_info "Starting Render CLI setup process..."
    echo
    
    # Step 1: Check prerequisites
    check_nodejs
    
    # Step 2: Install CLI
    install_render_cli
    
    # Step 3: Authenticate
    authenticate_render
    
    # Step 4: Discover service
    discover_service
    
    # Step 5: Verify connection
    verify_production_connection
    
    # Step 6: Set up read-only access
    setup_readonly_access
    
    # Step 7: Install helper tools
    install_helper_tools
    
    # Step 8: Create helper scripts
    create_helper_scripts
    
    echo
    print_status "Render CLI setup completed successfully!"
    echo
    echo "📝 Next steps:"
    echo "  1. Update scripts/.env.production-readonly with actual database credentials"
    echo "  2. Run scripts/check-production-health.sh to verify everything works"
    echo "  3. Use scripts/connect-production-db.sh for database access"
    echo
    echo "🔧 Available commands:"
    echo "  render services list                 - List all services"
    echo "  render services logs $RENDER_SERVICE_ID  - View production logs"
    echo "  render shell $RENDER_SERVICE_ID          - Connect to production shell"
    echo
    print_status "Setup complete! 🎉"
}

# Run main setup if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi