# export_all_perf_counters.ps1
# This script exports the full list of available performance counter sets to a text file
# in the current working directory.

$exportPath = Join-Path -Path (Get-Location) -ChildPath "CounterList.txt"
Get-Counter -ListSet * | Out-File -FilePath $exportPath -Encoding UTF8
Write-Output "Performance counter list exported to: $exportPath"
