#!/bin/bash

# PlayCricket Frontend File Generator
# This script creates all necessary Angular files for the application

set -e

echo "🚀 Generating PlayCricket Frontend Files..."

# Base directories
APP_DIR="src/app"
CORE_DIR="$APP_DIR/core"
SHARED_DIR="$APP_DIR/shared"
FEATURES_DIR="$APP_DIR/features"

# Create directory structure
echo "📁 Creating directory structure..."

mkdir -p $CORE_DIR/{services,interceptors,guards,models}
mkdir -p $SHARED_DIR/{components/{header,footer,loading-spinner,pagination,table,card,form,not-found},pipes}
mkdir -p $FEATURES_DIR/{dashboard,teams,players,venues,tournaments,matches,live-scoring,statistics}

echo "✅ Directory structure created!"

# Note: Individual component and service files will be created separately
# This script establishes the folder structure

echo "🎉 File structure generation complete!"
echo ""
echo "Next steps:"
echo "1. Run: npm install"
echo "2. Run: npm start"
echo "3. Open: http://localhost:4200"
