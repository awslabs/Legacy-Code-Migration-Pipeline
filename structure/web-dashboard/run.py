#!/usr/bin/env python3
"""
Migration Dashboard Launcher

Simple launcher script for the migration dashboard.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Migration Dashboard")
    print("=" * 60)
    print(f"📁 Project Root: {project_root}")
    print(f"🌐 Dashboard URL: http://localhost:5001")
    print(f"📊 Monitoring: {project_root / 'output'}")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)