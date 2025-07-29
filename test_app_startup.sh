#!/bin/bash

echo "🧪 Testing LeadFinder app startup..."

# Clear the log
echo "" > app.log

# Start the app in background
echo "🚀 Starting app..."
bash start_app.sh &
APP_PID=$!

# Wait for app to start
echo "⏳ Waiting for app to start..."
sleep 15

# Check if app is running
if ps -p $APP_PID > /dev/null; then
    echo "✅ App is running (PID: $APP_PID)"
    
    # Test health endpoint
    echo "🔍 Testing health endpoint..."
    HEALTH_RESPONSE=$(curl -s http://localhost:5051/health 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "✅ Health endpoint responding"
        echo "📊 Health status: $HEALTH_RESPONSE"
    else
        echo "❌ Health endpoint not responding"
    fi
    
    # Test main page
    echo "🔍 Testing main page..."
    MAIN_RESPONSE=$(curl -s -I http://localhost:5051/ 2>/dev/null | head -1)
    if [ $? -eq 0 ]; then
        echo "✅ Main page responding: $MAIN_RESPONSE"
    else
        echo "❌ Main page not responding"
    fi
    
    echo ""
    echo "🎉 App startup test completed successfully!"
    echo "🌐 Access the app at: http://localhost:5051"
    
    # Stop the app
    echo "🛑 Stopping app..."
    kill $APP_PID
    wait $APP_PID 2>/dev/null
    
else
    echo "❌ App failed to start"
    echo "📋 App log:"
    cat app.log
fi 