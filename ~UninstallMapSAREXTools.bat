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

IF EXIST "%_programs%\ArcGIS\Desktop10.0\License" CALL :remove "%_programs%\ArcGIS\Desktop10.0"
IF EXIST "%_programs%\ArcGIS\Desktop10.1\License" CALL :remove "%_programs%\ArcGIS\Desktop10.1"
IF EXIST "%_programs%\ArcGIS\Desktop10.2\License" CALL :remove "%_programs%\ArcGIS\Desktop10.2"
IF EXIST "%_programs%\ArcGIS\Desktop10.3\License" CALL :remove "%_programs%\ArcGIS\Desktop10.3"
IF EXIST "%_programs%\ArcGIS\Desktop10.4\License" CALL :remove "%_programs%\ArcGIS\Desktop10.4"
IF EXIST "%_programs%\ArcGIS\Desktop10.5\License" CALL :remove "%_programs%\ArcGIS\Desktop10.5"
IF EXIST "%_programs%\ArcGIS\Desktop10.6\License" CALL :remove "%_programs%\ArcGIS\Desktop10.6"

del "%APPDATA%\ArcGIS4LocalGovernment\ConfigFiles\loaded.config"

set _igtpath=%~dp0
set _regasmdir="%_programs%\Common Files\ArcGIS\bin\"
start "Unregister Measure Angle Addin" /D%_regasmdir% /W %_regasmdir%\ESRIRegAsm /p:Desktop /u "%_igtpath%Tools\AddIns\MeasureAngle.dll"

goto :eof


:remove

	del "%~1\bin\Addins\Search_Editor.esriAddIn"
	del "%~1\bin\Addins\MapSAREX_Config.esriAddIn"
	del "%~1\bin\Addins\GPX.esriAddIn"
	del "%~1\bin\Addins\Get_Map_Point_Addin_Tool.esriAddIn"
	del "%~1\bin\Addins\ConstructwithBuffer.esriAddIn"
	del "%~1\bin\Addins\AttributeAssistant.esriAddIn"

	del "%~1\ArcToolbox\Toolboxes\SAR_Toolbox100.tbx"

ENDLOCAL
