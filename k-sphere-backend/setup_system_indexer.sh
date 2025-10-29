#!/bin/bash
# System-Wide Indexing Setup Script for K-Sphere

echo "🚀 K-Sphere System-Wide Indexing Setup"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the k-sphere-backend directory"
    exit 1
fi

echo "📦 Installing required dependencies..."
pip install watchdog

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🔍 Checking system requirements..."

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Warning: Ollama doesn't seem to be running"
    echo "   Please start Ollama before using K-Sphere"
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

echo ""
echo "📝 Creating default configuration..."

# Ensure data directories exist
mkdir -p data/uploads
mkdir -p data/vectordb
mkdir -p logs

echo "✅ Data directories created"

echo ""
echo "✨ Setup Complete!"
echo ""
echo "🎯 Next Steps:"
echo "   1. Start the backend:"
echo "      python main.py"
echo ""
echo "   2. Start the frontend (in another terminal):"
echo "      cd ../k-sphere-frontend"
echo "      npm run dev"
echo ""
echo "   3. Open your browser to:"
echo "      http://localhost:3000/system-indexer"
echo ""
echo "📖 Documentation:"
echo "   Read SYSTEM_INDEXER_GUIDE.md for detailed usage instructions"
echo ""
echo "🔐 Privacy & Security:"
echo "   - All processing happens locally on your machine"
echo "   - No data is sent to external servers"
echo "   - You have full control over which paths are indexed"
echo "   - Original files are never modified"
echo ""
