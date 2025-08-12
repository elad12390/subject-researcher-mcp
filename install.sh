#!/bin/bash
# Installation script for Subject Researcher MCP Server

set -e

echo "🚀 Installing Subject Researcher MCP Server..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install UV first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ UV found"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Test the installation
echo "🧪 Testing installation..."
if uv run python -c "import sys; sys.path.insert(0, 'src'); from subject_researcher_mcp.server import duckduckgo_search; print('✅ Import successful')"; then
    echo "✅ Installation successful!"
else
    echo "❌ Installation failed - import test failed"
    exit 1
fi

# Run the demo
echo "🎉 Running demo..."
uv run python demo.py

echo ""
echo "✨ Installation complete!"
echo ""
echo "Next steps:"
echo "1. (Optional) Get a Gemini API key from https://makersuite.google.com/app/apikey"
echo "2. Set environment variable: export GEMINI_API_KEY=\"your-key\""
echo "3. Add server to your MCP client configuration:"
echo ""
echo "   Claude Desktop config (~/.config/claude-desktop/config.json):"
echo "   {"
echo "     \"mcpServers\": {"
echo "       \"subject-researcher\": {"
echo "         \"command\": \"uv\","
echo "         \"args\": [\"run\", \"python\", \"$(pwd)/src/subject_researcher_mcp/server.py\"],"
echo "         \"env\": {"
echo "           \"GEMINI_API_KEY\": \"your-gemini-api-key-here\""
echo "         }"
echo "       }"
echo "     }"
echo "   }"
echo ""
echo "4. Restart Claude Desktop and use the research_subject tool!"