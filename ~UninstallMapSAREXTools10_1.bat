@echo on

If DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles(x86)%
If Not DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles%

ECHO %_programs%

del "%_programs%\ArcGIS\Desktop10.1\bin\Addins\Search_Editor.esriAddIn"
del "%_programs%\ArcGIS\Desktop10.1\bin\Addins\MapSAREX_Config.esriAddIn"
del "%_programs%\ArcGIS\Desktop10.1\bin\Addins\GPX.esriAddIn"
del "%_programs%\ArcGIS\Desktop10.1\bin\Addins\Get_Map_Point_Addin_Tool.esriAddIn"
del "%_programs%\ArcGIS\Desktop10.1\bin\Addins\ConstructwithBuffer.esriAddIn"
del "%_programs%\ArcGIS\Desktop10.1\bin\Addins\AttributeAssistant.esriAddIn"

del "%_programs%\ArcGIS\Desktop10.1\ArcToolbox\Toolboxes\SAR_Toolbox100.tbx"

del "%APPDATA%\ArcGIS4LocalGovernment\ConfigFiles\loaded.config"

set _igtpath=%~dp0
set _regasmdir="%_programs%\Common Files\ArcGIS\bin\"
start "Unregister Measure Angle Addin" /D%_regasmdir% /W %_regasmdir%\ESRIRegAsm /p:Desktop /u "%_igtpath%Tools\AddIns\MeasureAngle.dll"
