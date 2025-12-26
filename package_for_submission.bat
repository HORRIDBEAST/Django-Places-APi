@echo off
echo ============================================
echo Place Review API - Packaging for Submission
echo ============================================
echo.

:: Navigate to parent directory
cd ..

:: Create temp folder name
set FOLDER_NAME=place_review_api_submission

:: Remove old package if exists
if exist %FOLDER_NAME% rmdir /s /q %FOLDER_NAME%
if exist %FOLDER_NAME%.zip del %FOLDER_NAME%.zip

:: Create fresh folder
mkdir %FOLDER_NAME%

echo Copying files...

:: Copy necessary directories
xcopy "Review App APIS\config" "%FOLDER_NAME%\config\" /E /I /Y
xcopy "Review App APIS\reviews" "%FOLDER_NAME%\reviews\" /E /I /Y

:: Copy root files
copy "Review App APIS\manage.py" "%FOLDER_NAME%\"
copy "Review App APIS\requirements.txt" "%FOLDER_NAME%\"
copy "Review App APIS\populate_data.py" "%FOLDER_NAME%\"
copy "Review App APIS\README.md" "%FOLDER_NAME%\"
copy "Review App APIS\place_review_api.postman_collection.json" "%FOLDER_NAME%\"

:: Clean __pycache__ from copied files
echo Cleaning __pycache__ folders...
for /d /r "%FOLDER_NAME%" %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

:: Clean .pyc files
echo Cleaning .pyc files...
del /s /q "%FOLDER_NAME%\*.pyc" 2>nul

:: Create zip file using PowerShell
echo Creating zip file...
powershell -command "Compress-Archive -Path '%FOLDER_NAME%' -DestinationPath '%FOLDER_NAME%.zip' -Force"

:: Check file size
echo.
echo Checking file size...
for %%A in ("%FOLDER_NAME%.zip") do (
    set size=%%~zA
    set /a size_kb=%%~zA/1024
)
echo File size: %size_kb% KB

if %size_kb% GTR 1024 (
    echo.
    echo WARNING: File size is over 1MB limit! Current size: %size_kb% KB
    echo.
) else (
    echo.
    echo SUCCESS: File size is within 1MB limit ✓
    echo.
)

:: Clean up temporary folder
rmdir /s /q "%FOLDER_NAME%"

echo.
echo Package created: %FOLDER_NAME%.zip
echo Location: %CD%\%FOLDER_NAME%.zip
echo.
echo ============================================
echo Next steps:
echo 1. Reply to the assignment email
echo 2. Attach: %FOLDER_NAME%.zip
echo ============================================
pause
