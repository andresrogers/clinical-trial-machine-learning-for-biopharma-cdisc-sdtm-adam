@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT_DIR=%~1"
if "%ROOT_DIR%"=="" set "ROOT_DIR=clinical-trial-portfolio"

set "ARCHIVE_DIR=%ROOT_DIR%\data\external\archives"
set "CDISC_RAW_DIR=%ROOT_DIR%\data\external\cdisc_pilot\raw_xpt"
set "CDISC_META_DIR=%ROOT_DIR%\data\external\cdisc_pilot\metadata"
set "CDISC_CSR_DIR=%ROOT_DIR%\data\external\cdisc_pilot\csr"
set "CLINTRIALDATA_DIR=%ROOT_DIR%\data\external\clintrialdata"
set "SAFETYDATA_DIR=%ROOT_DIR%\data\external\safetydata"
set "PHARMAVERSE_REF_DIR=%ROOT_DIR%\docs\reference\pharmaverse"
set "REG_REF_DIR=%ROOT_DIR%\docs\reference\regulatory"

for %%D in (
  "%ARCHIVE_DIR%"
  "%CDISC_RAW_DIR%"
  "%CDISC_META_DIR%"
  "%CDISC_CSR_DIR%"
  "%CLINTRIALDATA_DIR%"
  "%SAFETYDATA_DIR%"
  "%ROOT_DIR%\data\interim"
  "%ROOT_DIR%\data\derived"
  "%ROOT_DIR%\data\generated"
  "%ROOT_DIR%\metadata"
  "%ROOT_DIR%\qc"
  "%ROOT_DIR%\config"
  "%ROOT_DIR%\src\ingest"
  "%ROOT_DIR%\src\transform"
  "%ROOT_DIR%\src\modeling"
  "%ROOT_DIR%\src\reporting"
  "%PHARMAVERSE_REF_DIR%"
  "%REG_REF_DIR%"
) do if not exist %%~D mkdir %%~D

echo Downloading archives with PowerShell...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ProgressPreference='SilentlyContinue';" ^
  "Invoke-WebRequest -Uri 'https://codeload.github.com/cdisc-org/sdtm-adam-pilot-project/zip/refs/heads/master' -OutFile '%ARCHIVE_DIR%\cdisc-pilot-master.zip';" ^
  "Invoke-WebRequest -Uri 'https://cran.r-project.org/src/contrib/clinTrialData_0.1.3.tar.gz' -OutFile '%CLINTRIALDATA_DIR%\clinTrialData_0.1.3.tar.gz';" ^
  "Invoke-WebRequest -Uri 'https://codeload.github.com/SafetyGraphics/safetyData/zip/refs/heads/main' -OutFile '%ARCHIVE_DIR%\safetyData-main.zip';"
if errorlevel 1 exit /b 1

echo Extracting required files with PowerShell...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$root='%ROOT_DIR%';" ^
  "$tmp=Join-Path $env:TEMP ('ctdl_' + [guid]::NewGuid().ToString()); New-Item -ItemType Directory -Force -Path $tmp | Out-Null;" ^
  "$cdisc=Join-Path $tmp 'cdisc'; Expand-Archive -Path '%ARCHIVE_DIR%\cdisc-pilot-master.zip' -DestinationPath $cdisc -Force;" ^
  "$needed=@('dm.xpt','ae.xpt','lb.xpt','vs.xpt','ex.xpt','ds.xpt','adsl.xpt','adae.xpt','adlbc.xpt','adlbh.xpt','adtte.xpt','advs.xpt');" ^
  "Get-ChildItem -Path $cdisc -Recurse -File | ForEach-Object { $p=$_.FullName.ToLower(); if($p -like '*updated-pilot-submission-package\900172\m5\datasets\*' -and $needed -contains $_.Name.ToLower()){ Copy-Item $_.FullName -Destination '%CDISC_RAW_DIR%' -Force }; if($_.Name.ToLower() -like '*define*.xml' -or $_.Name.ToLower() -like '*define*.pdf'){ Copy-Item $_.FullName -Destination '%CDISC_META_DIR%' -Force }; if($_.Name.ToLower() -like 'cdiscpilot01*.pdf' -or $p -like '*\53-clin-stud-rep\*'){ Copy-Item $_.FullName -Destination '%CDISC_CSR_DIR%' -Force } };" ^
  "$safety=Join-Path $tmp 'safety'; Expand-Archive -Path '%ARCHIVE_DIR%\safetyData-main.zip' -DestinationPath $safety -Force;" ^
  "Get-ChildItem -Path $safety -Recurse -File | ForEach-Object { $p=$_.FullName.ToLower(); $n=$_.Name.ToLower(); if($p -like '*\data\*' -or $n -like 'readme*' -or $n -eq 'description'){ Copy-Item $_.FullName -Destination '%SAFETYDATA_DIR%' -Force } };" ^
  "Set-Content -Path '%PHARMAVERSE_REF_DIR%\links.txt' -Value @('https://pharmaverse.github.io/examples','https://pharmaverse.github.io/examples/sdtm','https://pharmaverse.github.io/examples/adam','https://pharmaverse.github.io/examples/tlg','https://github.com/pharmaverse/admiral');" ^
  "Set-Content -Path '%REG_REF_DIR%\links.txt' -Value @('https://www.cdisc.org/standards/foundational/sdtmig/sdtmig-v3-3/html','https://www.cdisc.org/standards/foundational/adam','https://www.fda.gov/media/133252/download','https://www.ema.europa.eu/');" ^
  "Remove-Item -Recurse -Force $tmp;"
if errorlevel 1 exit /b 1

echo Done.
endlocal
