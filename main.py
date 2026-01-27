#!/usr/bin/env python3
import multiprocessing
import time
import sys

# Import the logic from your other files
from app import app
from worker import lcd_worker

def run_flask():
    """Function to run the Flask Web Server."""
    print("Starting Web Interface on port 5000...")
    # debug=False is important when running in a multiprocess environment
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def run_worker():
    """Function to run the LCD Hardware Logic."""
    print("Starting LCD Worker...")
    try:
        lcd_worker()
    except Exception as e:
        print(f"Worker crashed: {e}")

if __name__ == "__main__":
    # Define the processes
    flask_process = multiprocessing.Process(target=run_flask, name="Flask_Server")
    worker_process = multiprocessing.Process(target=run_worker, name="LCD_Worker")

    # Start them
    flask_process.start()
    worker_process.start()

    try:
        # Keep the main script alive while processes are running
        flask_process.join()
        worker_process.join()
    except KeyboardInterrupt:
        print("\nShutting down Zeus LCD System...")
        flask_process.terminate()
        worker_process.terminate()
        sys.exit(0)