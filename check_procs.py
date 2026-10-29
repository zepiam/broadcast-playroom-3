import subprocess
import json

ps = subprocess.run([
    "powershell", "-NoProfile", "-Command",
    "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*8801*' -or $_.CommandLine -like '*BroadcastPlayroom*' } | Select-Object ProcessId, ParentProcessId, Name, CommandLine | ConvertTo-Json"
], capture_output=True, text=True)

print(ps.stdout)
