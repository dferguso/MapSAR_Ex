@echo on

If DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles(x86)%
If Not DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles%

ECHO %_programs%

xcopy "c:\Mapsar_Ex\tools\addins\*.esriaddin" "%_programs%\ArcGIS\Desktop10.1\bin\Addins\"

xcopy "c:\Mapsar_Ex\tools\SAR_Toolbox100.tbx" "%_programs%\ArcGIS\Desktop10.1\ArcToolbox\Toolboxes\"

IF NOT EXIST %APPDATA%\ArcGIS4LocalGovernment\ConfigFiles (
   MKDIR %APPDATA%\ArcGIS4LocalGovernment\ConfigFiles"
)
copy c:\mapsar_ex\tools\aaloaded.config %APPDATA%\ArcGIS4LocalGovernment\ConfigFiles\loaded.config /y

cd %_programs%\Common Files\ArcGIS\bin

ESRIRegAsm /p:Desktop "C:\MapSAR_Ex\Tools\AddIns\MeasureAngle.dll"

cd \

c:\mapsar_ex\tools\geomag-0.9.win32.exe
