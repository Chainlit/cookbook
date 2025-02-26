=== Animated Waiting Indicator ===

A Chainlit application demonstrating real-time animated status indicators.

✨ Features:
- Rotating emoji animation
- Dynamic progress bar
- Async task management
- Responds to "test animation" command

⚙️ Installation:
1. Install requirements:
   pip install chainlit asyncio
2. Save code as app.py
3. Run with:
   chainlit run app.py

🎮 Usage:
1. Open http://localhost:8000
2. Type "test animation"
3. Watch 30-second animation
4. Receive "Done!" confirmation

🔧 Customization:
- Change emojis in ["🌑", "🌒"...] list
- Modify duration in await asyncio.sleep(30)
- Adjust speed with interval=0.8 parameter

📝 Note:
Optimized for performance with minimal system resource usage.