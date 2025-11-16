*** Settings ***
Documentation     A collection of atomic tasks for the employee_form
 automation.
...               This robot is designed to be controlled by an external scheduler
...               (e.g., smart_runner.py) which handles all timing and logic.
Library           OperatingSystem
Library           DateTime              # Used for creating timestamped filenames.
Library           RPA.Email.ImapSmtp
Library           RPA.Tables
Library           Collections

*** Variables ***
# --- Core File Paths and Scripts ---
${PYTHON_EXE}          D:${/}employee_form${/}venv${/}Scripts${/}python.exe
${PROCESSOR_SCRIPT}    ${CURDIR}${/}report_processor.py  
${CLEANER_SCRIPT}      ${CURDIR}${/}excel_cleaner.py  
${REMINDER_SCRIPT}     ${CURDIR}${/}reminder_checker.py
${RESPONSES_FILE}      D:${/}employee_form${/}data${/}responses.xlsx
${MASTER_LIST_FILE}    D:${/}employee_form${/}data${/}Employees_emails_list.xlsx

# --- Email Configuration ---
${GMAIL_USER}     nadaalfassal@gmail.com
${GMAIL_PASS}     qdoarilqytgttkmg
${SMTP_SERVER}    smtp.gmail.com
${SMTP_PORT}      587
${HR_EMAIL}       nadaalfassal@gmail.com
@{EMPLOYEES}      nadaalfassal@gmail.com

#  ${FORM_URL} is passed as an argument from the smart_runner script.

*** Tasks ***
# These tasks are designed to be called individually by the smart_runner.py script.

Send Form To All Employees
    [Documentation]    Task to send the initial form link to all employees.
    Send Form Link To Employees

Send Reminders To Non Responders
    [Documentation]    Task to send a reminder email to non-responding employees.
    Send Reminders To Non-Responders

Generate And Send Final Report
    [Documentation]    Task to process data, send the final report, and reset the file.
    Copy Send And Reset Monthly Data

*** Keywords ***
Authorize Gmail
    [Documentation]    Authorizes the connection to the Gmail SMTP server.
    Authorize    account=${GMAIL_USER}    password=${GMAIL_PASS}    smtp_server=${SMTP_SERVER}    smtp_port=${SMTP_PORT}
    Log To Console    Successfully logged into Gmail ✅

Send Form Link To Employees
    [Documentation]    Constructs and sends the form email to the master employee list.
    Authorize Gmail 
    Log To Console    Sending form link to employees. URL received: ${FORM_URL}
    FOR    ${email}    IN    @{EMPLOYEES}
        Send Message
        ...    sender=${GMAIL_USER}
        ...    recipients=${email}
        ...    subject=📋 حصر الأنشطة المعرفية في الهيئة العامة للغذاء والدواء
        ...    body=مرحبًا، الرجاء تعبئة النموذج عبر الرابط التالي:\n${FORM_URL}
    END
    Log To Console    ✅ Link sent successfully.

Send Reminders To Non-Responders
    [Documentation]    Executes the external Python script for checking non-responders.
    Log To Console    Starting reminder check for non-responders...
    ${REMINDER_COMMAND}=    Catenate    SEPARATOR=    "${PYTHON_EXE}" -X utf8 "${REMINDER_SCRIPT}" "${RESPONSES_FILE}" "${MASTER_LIST_FILE}" "${GMAIL_USER}" "${GMAIL_PASS}" "${FORM_URL}" 2>&1
    ${REMINDER_RESULT}=    OperatingSystem.Run    ${REMINDER_COMMAND}
    Log To Console    Reminder Script Output: ${REMINDER_RESULT}
    ${error_found}=    Run Keyword And Return Status    Should Contain    ${REMINDER_RESULT}    error    ignore_case=True
    IF    ${error_found}
        Log To Console    An error occurred in the reminder script, but continuing execution. Error: ${REMINDER_RESULT}    level=WARN
    END

Copy Send And Reset Monthly Data
    [Documentation]    Manages the end-of-month process: process, copy, send, and clean.
    Log To Console    Starting Data Processing (Clean & Highlight Duplicates)...
    ${PROCESS_COMMAND}=    Catenate    SEPARATOR=    "${PYTHON_EXE}" "${PROCESSOR_SCRIPT}" "${RESPONSES_FILE}" 2>&1
    ${PROCESSOR_RESULT}=    OperatingSystem.Run    ${PROCESS_COMMAND}
    Log To Console    Processor Script Output: ${PROCESSOR_RESULT}
    ${error_found_in_processor}=    Run Keyword And Return Status    Should Contain    ${PROCESSOR_RESULT}    ERROR    ignore_case=True
    IF    ${error_found_in_processor}
        FAIL    Data Processor Failed: ${PROCESSOR_RESULT}
    END

    ${CURRENT_DATE}=    Get Current Date    result_format=%Y-%m-%d_%H%M%S
    ${TEMP_FILENAME}=    Set Variable    temp_responses_${CURRENT_DATE}.xlsx
    ${TEMP_COPY_PATH}=    Set Variable    ${CURDIR}${/}${TEMP_FILENAME} 
    
    Log To Console    Creating temporary copy of the PROCESSED file...
    OperatingSystem.Copy File    ${RESPONSES_FILE}    ${TEMP_COPY_PATH}
    
    Send Report To HR    ${TEMP_COPY_PATH}
    
    OperatingSystem.Remove File    ${TEMP_COPY_PATH}
    Log To Console    ✅ Temporary copy deleted.
    
    Log To Console    Starting final file reset (clearing content)...
    ${CLEAN_COMMAND}=     Catenate    SEPARATOR=    "${PYTHON_EXE}" "${CLEANER_SCRIPT}" "${RESPONSES_FILE}" 2>&1
    ${CLEANER_RESULT}=    OperatingSystem.Run    ${CLEAN_COMMAND}
    Log To Console    Cleaner Script Output: ${CLEANER_RESULT}
    ${error_found_in_cleaner}=    Run Keyword And Return Status    Should Contain    ${CLEANER_RESULT}    ERROR    ignore_case=True
    IF    ${error_found_in_cleaner}
        FAIL    Excel Cleaner Failed: ${CLEANER_RESULT}
    END
    Log To Console    ✅ Original responses file reset successfully.

Send Report To HR
    [Arguments]    ${attachment_path}
    [Documentation]    Sends the processed Excel file as an attachment to HR.
    Authorize Gmail 
    Log To Console    Sending monthly report to HR...
    Send Message
    ...    sender=${GMAIL_USER}
    ...    recipients=${HR_EMAIL}
    ...    subject=📊 التقرير الشهري للأنشطة المعرفية 
    ...    body=مرفق ملف الردود المجمعة والمُعالجة، مع تظليل الصفوف المكررة باللون الأحمر للمراجعة.
    ...    attachments=${attachment_path}
    Log To Console    Report sent successfully to HR.