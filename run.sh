#!/bin/bash

echo "=================================="
echo "NIP-90 DVM Scanner Setup & Launch"
echo "=================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated"
echo ""

# Install/upgrade dependencies
echo "📥 Installing dependencies from requirements.txt..."
pip install --upgrade pip -q
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Make scanner executable
chmod +x scanner.py

echo "=================================="
echo "🚀 Starting NIP-90 DVM Scanner"
echo "=================================="
echo ""
echo "📝 Output will be saved to:"
echo "   - dvm_vendors.json (structured data)"
echo "   - dvm_scan_master.log (verbose log)"
echo ""
echo "⏳ Scanning may take 30-60 seconds..."
echo ""

# Run the scanner
python scanner.py

SCAN_EXIT_CODE=$?

echo ""
echo "=================================="
if [ $SCAN_EXIT_CODE -eq 0 ]; then
    echo "✅ Scan completed successfully!"
    echo ""
    echo "📊 Results available:"
    if [ -f "dvm_vendors.json" ]; then
        VENDOR_COUNT=$(grep -o "\"pubkey\"" dvm_vendors.json | wc -l)
        echo "   📦 Found $VENDOR_COUNT vendors in dvm_vendors.json"
    fi
    if [ -f "dvm_scan_master.log" ]; then
        LOG_LINES=$(wc -l < dvm_scan_master.log)
        echo "   📝 Master log has $LOG_LINES lines"
    fi
else
    echo "⚠️  Scan completed with errors (exit code: $SCAN_EXIT_CODE)"
    echo "   Check dvm_scan_master.log for details"
fi
echo "=================================="
echo ""
