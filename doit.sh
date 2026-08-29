Set-Location D:\Projects\SIH\SIH26095
$ErrorActionPreference = 'Stop'
function Run($cmd) {
  $out = cmd /c $cmd 2>&1
  $out | ForEach-Object { Write-Host $_ }
  $LASTEXITCODE
}
"--- pre-commit ---"
Run 'git status --short'
Run 'git add -A'
Run 'git status --short'
"--- commit ---"
Run 'git commit -m docs: add planv5 and DEMO_GUIDE'
"--- log ---"
Run 'git log --oneline -3'