#!/usr/bin/env python3
"""
Web UI launcher for Summazier
Run this to start the web interface
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Summazier Web UI...")
    print("📱 Open your browser to: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop")
    
    uvicorn.run(
        "summazier.web:app", 
        host="0.0.0.0", 
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
