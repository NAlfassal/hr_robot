import subprocess
from datetime import date, datetime, time
import time as time_module 
from schedule_calculator import get_monthly_schedule 

# ==============================================================================
# CONFIGURATION
# ==============================================================================
PYTHON_EXECUTABLE = "D:/employee_form/venv/Scripts/python.exe" 
ROBOT_FILE_PATH = "D:/employee_form/f_send.robot"
FORM_URL = "http://localhost:5000/"

# --- Production Time Configuration ---
SEND_TIME = (8, 0)      # (Hour, Minute) -> 8:00 AM
REMINDER_TIME = (10, 0)   # -> 10:00 AM
REPORT_TIME = (9, 0)      # -> 9:00 AM

# ==============================================================================
# 🚦 TESTING CONFIGURATION
# ==============================================================================
TEST_MODE = "SEND" 
# Set the exact hour and minute for today's test.
TEST_TIME = (13, 27)  # <-- ✅ الآن يمكنك كتابة الساعة والدقيقة هنا (10:23 AM)
# ==============================================================================

def wait_until(target_hour, target_minute): # <-- تم تعديل الدالة لتقبل الدقائق
    """
    Pauses the script execution until the target time of the current day.
    """
    now = datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

    if now > target_time:
        print(f"Target time {target_hour}:{target_minute:02d} has already passed. Proceeding immediately.")
        return

    wait_seconds = (target_time - now).total_seconds()
    
    if wait_seconds > 0:
        print(f"Waiting for {wait_seconds / 3600:.2f} hours until the target time ({target_hour}:{target_minute:02d})...")
        time_module.sleep(wait_seconds)
        print(f"Woke up at {datetime.now()}. It's time to run the task.")

def run_robot_task(task_name):
    # ... (This function remains unchanged) ...
    print(f"[{datetime.now()}] Preparing to run Robot Framework task: '{task_name}'")
    command = ["robot", "--task", task_name, "--variable", f"FORM_URL:{FORM_URL}", ROBOT_FILE_PATH]
    print(f"Executing command: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"[{datetime.now()}] Successfully executed task: '{task_name}'")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR: The robot task '{task_name}' failed. Details: {e}")

if __name__ == "__main__":
    print(f"\n[{datetime.now()}] Smart Runner started.")

    if TEST_MODE:
        print("\n" + "="*50)
        print(f"!!! TESTING MODE IS ACTIVE: Simulating '{TEST_MODE}' task !!!")
        test_hour, test_minute = TEST_TIME
        print(f"Task is scheduled to run today at approximately {test_hour}:{test_minute:02d}.")
        print("="*50 + "\n")
        
        task_to_run = None
        if TEST_MODE == "SEND":
            task_to_run = "Send Form To All Employees"
        elif TEST_MODE == "REMIND":
            task_to_run = "Send Reminders To Non Responders"
        elif TEST_MODE == "REPORT":
            task_to_run = "Generate And Send Final Report"
        
        if task_to_run:
            wait_until(test_hour, test_minute)
            run_robot_task(task_to_run)
        else:
            print(f"Invalid TEST_MODE: '{TEST_MODE}'. No task will be run.")

    else: # Production Mode
        print("Running in PRODUCTION mode.")
        today = date.today()
        schedule = get_monthly_schedule(today.year, today.month)
        
        if today == schedule["send_day"]:
            print("\nACTION: Today is the Form Send Day.")
            hour, minute = SEND_TIME
            wait_until(hour, minute)
            run_robot_task("Send Form To All Employees")
        elif today == schedule["reminder_day"]:
            print("\nACTION: Today is the Reminder Day.")
            hour, minute = REMINDER_TIME
            wait_until(hour, minute)
            run_robot_task("Send Reminders To Non Responders")
        elif today == schedule["report_day"]:
            print("\nACTION: Today is the Report Day.")
            hour, minute = REPORT_TIME
            wait_until(hour, minute)
            run_robot_task("Generate And Send Final Report")
        else:
            print("\nACTION: No scheduled task for today. Exiting.")