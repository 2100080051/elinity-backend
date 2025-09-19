"""
Test script to verify Celery configuration and task execution
"""
import sys
import os
import time

# Add parent directory to path so we can import modules from it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import from the parent directory
from core.celery import celery, my_scheduled_task

if __name__ == "__main__":
    print("Testing Celery task execution...")
    print(f"Celery app: {celery}")
    print(f"Broker URL: {celery.conf.broker_url}")
    print(f"Result backend: {celery.conf.result_backend}")
    print(f"Current working directory: {os.getcwd()}")
    
    # The path where we expect the file to be created
    expected_file_path = os.path.join(os.getcwd(), "celery_task_log.txt")
    print(f"Expected file path: {expected_file_path}")
    
    # Check if file already exists
    if os.path.exists(expected_file_path):
        print(f"File already exists at {expected_file_path}")
        with open(expected_file_path, 'r') as f:
            print(f"Current file content:\n{f.read()}")
    else:
        print(f"File does not exist at {expected_file_path} yet")
    
    # Execute the task
    print("\nSubmitting task...")
    task = my_scheduled_task.delay()
    print(f"Task ID: {task.id}")
    
    # Wait for task to complete
    print("\nWaiting for task to complete...")
    for i in range(10):  # Check status for up to 10 seconds
        time.sleep(1)
        print(f"Checking task status ({i+1}/10)...")
        
        if task.ready():
            if task.successful():
                print(f"Task succeeded with result: {task.result}")
                break
            else:
                print(f"Task failed with error: {task.traceback}")
                break
    else:
        print("Task is still running after 10 seconds")
    
    # Check if file exists after task execution
    print("\nChecking if file was created...")
    if os.path.exists(expected_file_path):
        print(f"✅ File exists at {expected_file_path}")
        with open(expected_file_path, 'r') as f:
            print(f"File content:\n{f.read()}")
    else:
        print(f"❌ File still does not exist at {expected_file_path}")
        
    print("\nPossible reasons if file wasn't created:")
    print("1. Celery worker is running with a different working directory")
    print("2. Celery worker doesn't have write permissions")
    print("3. Task failed before writing to file")
    print("4. File is being created in a different location")
    
    print("\nTest complete!")

