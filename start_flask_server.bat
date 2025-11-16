@echo off
REM انتقل إلى مجلد المشروع لكي يتمكن app.py من إيجاد ملفات الداتا
cd /d "D:\employee_form"

REM 1. تحديد المسار الكامل لنسخة Python التي تحتوي على 'openpyxl'
set PYTHON_EXE="C:\Users\acerl\AppData\Local\Programs\Python\Python310\python.exe"

REM 2. تشغيل سيرفر فلاسك باستخدام المسار الموثوق.
REM نستخدم 'start' لفتح نافذة CMD جديدة وتشغيل السيرفر فيها بشكل مستمر.
start "Flask Server" %PYTHON_EXE% app.py

exit
