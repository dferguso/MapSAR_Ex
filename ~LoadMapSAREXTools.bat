@echo on

If DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles(x86)%
If Not DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles%

ECHO %_programs%

set _igtpath=%~dp0

IF EXIST "%_programs%\ArcGIS\Desktop10.0" CALL :install "%_programs%\ArcGIS\Desktop10.0"
IF EXIST "%_programs%\ArcGIS\Desktop10.1" CALL :install "%_programs%\ArcGIS\Desktop10.1"
IF EXIST "%_programs%\ArcGIS\Desktop10.2" CALL :install "%_programs%\ArcGIS\Desktop10.2"
IF EXIST "%_programs%\ArcGIS\Desktop10.3" CALL :install "%_programs%\ArcGIS\Desktop10.3"

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
