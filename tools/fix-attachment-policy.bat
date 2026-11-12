@echo off
title Fix "Open File - Security Warning"
setlocal

echo ============================================================
echo  Current Attachment Manager setting
echo ============================================================
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Attachments" /v ScanWithAntiVirus
echo.
echo   0 = do not check
echo   1 = check files from Internet only   ^<-- target
echo   2 = check Internet + Intranet
echo   3 = check all files                  ^<-- current problem
echo.
echo Changing it to 1 so local exe files stop asking for confirmation.
echo.
pause

reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Attachments" /v ScanWithAntiVirus /t REG_DWORD /d 1 /f
if errorlevel 1 goto failed

echo.
echo ============================================================
echo  OK - setting is now 1.
echo  Double-click CppVideoLearner.exe again; it should not ask.
echo ============================================================
goto done

:failed
echo.
echo ============================================================
echo  FAILED
echo  Right-click this .bat file and choose "Run as administrator".
echo ============================================================

:done
echo.
pause
endlocal
