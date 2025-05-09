@echo off
echo Setting Firebase environment variables...
set GOOGLE_APPLICATION_CREDENTIALS=%~dp0firebase-key.json
echo Environment variable GOOGLE_APPLICATION_CREDENTIALS has been set to: %GOOGLE_APPLICATION_CREDENTIALS%

echo Starting application...
python main.py