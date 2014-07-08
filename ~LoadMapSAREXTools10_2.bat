@echo on

If DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles(x86)%
If Not DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles%

ECHO %_programs%

set _igtpath=%~dp0

xcopy "%_igtpath%tools\addins\*.esriaddin" "%_programs%\ArcGIS\Desktop10.2\bin\Addins\"

xcopy "%_igtpath%tools\SAR_Toolbox100.tbx" "%_programs%\ArcGIS\Desktop10.2\ArcToolbox\Toolboxes\"

set _config="%APPDATA%\ArcGIS4LocalGovernment\ConfigFiles"
IF NOT EXIST %_config% (
   MKDIR %_config%
)
copy "%_igtpath%tools\aaloaded.config" %_config%\loaded.config /y

set _regasmdir="%_programs%\Common Files\ArcGIS\bin\"
start "Register Measure Angle Addin" /D%_regasmdir% /W %_regasmdir%\ESRIRegAsm /p:Desktop "%_igtpath%Tools\AddIns\MeasureAngle.dll"

"%_igtpath%tools\geomag-0.9.win32.exe"
