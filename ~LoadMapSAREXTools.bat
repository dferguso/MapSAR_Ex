@echo off

REM Get admin privileges
REM from https://sites.google.com/site/eneerge/scripts/batchgotadmin

REM  --> Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )

@echo on

If DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles(x86)%
If Not DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles%

ECHO %_programs%

set _igtpath=%~dp0

IF EXIST "%_programs%\ArcGIS\Desktop10.0\License" CALL :install "%_programs%\ArcGIS\Desktop10.0"
IF EXIST "%_programs%\ArcGIS\Desktop10.1\License" CALL :install "%_programs%\ArcGIS\Desktop10.1"
IF EXIST "%_programs%\ArcGIS\Desktop10.2\License" CALL :install "%_programs%\ArcGIS\Desktop10.2"
IF EXIST "%_programs%\ArcGIS\Desktop10.3\License" CALL :install "%_programs%\ArcGIS\Desktop10.3"
IF EXIST "%_programs%\ArcGIS\Desktop10.4\License" CALL :install "%_programs%\ArcGIS\Desktop10.4"
IF EXIST "%_programs%\ArcGIS\Desktop10.5\License" CALL :install "%_programs%\ArcGIS\Desktop10.5"
IF EXIST "%_programs%\ArcGIS\Desktop10.6\License" CALL :install "%_programs%\ArcGIS\Desktop10.6"

set _config="%APPDATA%\ArcGIS4LocalGovernment\ConfigFiles"
IF NOT EXIST %_config% (
   MKDIR %_config%
)
copy "%_igtpath%tools\aaloaded.config" %_config%\loaded.config /y

set _regasmdir="%_programs%\Common Files\ArcGIS\bin\"
start "Register Measure Angle Addin" /D%_regasmdir% /W %_regasmdir%\ESRIRegAsm /p:Desktop "%_igtpath%Tools\AddIns\MeasureAngle.dll"

GOTO :eof


:install

	xcopy "%_igtpath%tools\addins\*.esriaddin" "%~1\bin\Addins\"
	xcopy "%_igtpath%tools\SAR_Toolbox100.tbx" "%~1\ArcToolbox\Toolboxes\"

ENDLOCAL
