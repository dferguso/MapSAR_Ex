@echo on

If DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles(x86)%
If Not DEFINED ProgramFiles(x86) Set _programs=%ProgramFiles%

ECHO %_programs%

del "%_programs%\ArcGIS\Desktop10.2\bin\Addins\Search_Editor.esriAddIn"
del "%_programs%\ArcGIS\Desktop10.2\bin\Addins\MapSAREX_Config.esriAddIn"
del "%_programs%\ArcGIS\Desktop10.2\bin\Addins\GPX.esriAddIn"
del "%_programs%\ArcGIS\Desktop10.2\bin\Addins\Get_Map_Point_Addin_Tool.esriAddIn"
del "%_programs%\ArcGIS\Desktop10.2\bin\Addins\ConstructwithBuffer.esriAddIn"
del "%_programs%\ArcGIS\Desktop10.2\bin\Addins\AttributeAssistant.esriAddIn"

del "%_programs%\ArcGIS\Desktop10.2\ArcToolbox\Toolboxes\SAR_Toolbox100.tbx"

del "%APPDATA%\ArcGIS4LocalGovernment\ConfigFiles\loaded.config"

cd %_programs%\Common Files\ArcGIS\bin

ESRIRegAsm /p:Desktop /u "C:\MapSAR_Ex\Tools\AddIns\MeasureAngle.dll"

