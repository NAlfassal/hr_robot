from flask import Flask, render_template, request
import pandas as pd
import os
from datetime import date, datetime 
import mimetypes 
# Import the shared, dynamic scheduler
from schedule_calculator import get_monthly_schedule 

# --- App Initialization ---
mimetypes.add_type('application/javascript', '.js')
app = Flask(__name__, static_folder='static', template_folder='.')
DATA_PATH = os.path.join("data", "responses.xlsx")

# --- Route for Displaying the Page (GET) ---
@app.route("/", methods=["GET"])
def home():
    """
    Serves the main page, deciding which template to show based on the
    dynamically calculated schedule.
    """
    today = date.today()
    # Get the schedule from the single source of truth
    schedule = get_monthly_schedule(today.year, today.month)
    last_valid_day = schedule["last_submission_day"]

    # Check if today is past the last allowed submission day.
    if today > last_valid_day:
        return render_template("closed.html")
    else:
        return render_template("index.html")

# --- Route for Handling Form Submissions (POST) ---
@app.route("/form", methods=["POST"])
def handle_form_submission():
    """
    Handles form submissions with a dynamic server-side security check
    using the same logic as the home route.
    """
    # --- DYNAMIC SECURITY CHECK ---
    today = date.today()
    # Get the schedule from the single source of truth again
    schedule = get_monthly_schedule(today.year, today.month)
    last_valid_day = schedule["last_submission_day"]
    
    # If someone tries to submit data after the deadline, reject it.
    if today > last_valid_day:
        return "The submission period has ended. Data cannot be saved.", 403

    # --- Data Processing (The rest of the code is for handling the form data) ---
    try:
        column_order = [
            "البريد الإلكتروني", "اسم القطاع", "الإدارة التنفيذية", "الإدارة", "القسم",
            "هل توجد أنشطة؟", "موضوع النشاط", "نوع النشاط", "هدف استراتيجي 1", 
            "هدف استراتيجي 2", "تصنيف المقدم", "تاريخ بداية النشاط", "تاريخ نهاية النشاط",
            "اسم المقدم", "مسؤول الحضور", "الفئة المستهدفة (النوع)", "الفئة المستهدفة (تفاصيل)",
            "عدد الحضور", "مدة النشاط (ساعة)", "مكان الحفظ", "تاريخ الإرسال"
        ]
        form_data = request.form
        has_activities = form_data.get('hasActivities') == 'yes'
        new_entry = {
            "البريد الإلكتروني": form_data.get("employeeEmail"), "اسم القطاع": form_data.get('sector'),
            "الإدارة التنفيذية": form_data.get('department'), "الإدارة": form_data.get('division'),
            "القسم": form_data.get('section'), "هل توجد أنشطة؟": "نعم" if has_activities else "لا يوجد",
            "تاريخ الإرسال": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "موضوع النشاط": form_data.get("activityTopic") if has_activities else "لا يوجد",
            "نوع النشاط": form_data.get("activityType") if has_activities else "لا يوجد",
            "هدف استراتيجي 1": form_data.get("strategicGoalLevel1") if has_activities else "لا يوجد",
            "هدف استراتيجي 2": form_data.get("strategicGoalLevel2") if has_activities else "لا يوجد",
            "تصنيف المقدم": form_data.get("presenterCategory") if has_activities else "لا يوجد",
            "تاريخ بداية النشاط": form_data.get("activityStartDate") if has_activities else "لا يوجد",
            "تاريخ نهاية النشاط": form_data.get("activityEndDate") if has_activities else "لا يوجد",
            "اسم المقدم": form_data.get("presenterName") if has_activities else "لا يوجد",
            "مسؤول الحضور": form_data.get("attendanceResponsible") if has_activities else "لا يوجد",
            "الفئة المستهدفة (النوع)": form_data.get("targetAudienceType") if has_activities else "لا يوجد",
            "الفئة المستهدفة (تفاصيل)": form_data.get("targetAudienceDetails") if has_activities else "لا يوجد",
            "عدد الحضور": form_data.get("attendeeCount") if has_activities else 0,
            "مدة النشاط (ساعة)": form_data.get("activityDuration") if has_activities else 0,
            "مكان الحفظ": form_data.get("contentLocation") if has_activities else "لا يوجد",
        }
        df = pd.DataFrame([new_entry])
        df = df.reindex(columns=column_order)
        if os.path.exists(DATA_PATH):
            try:
                old_df = pd.read_excel(DATA_PATH)
                df = pd.concat([old_df, df], ignore_index=True)  
            except Exception as e:
                print(f"Error reading existing Excel file: {e}")
                return "Failed to read existing data file. Please contact support.", 500
        with pd.ExcelWriter(DATA_PATH, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='الردود', index=False)
            worksheet = writer.sheets['الردود']
            worksheet.right_to_left()
        return "Your response has been received successfully. Thank you!", 200
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "An error occurred while saving the data. Please contact technical support.", 500

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    app.run(debug=True)