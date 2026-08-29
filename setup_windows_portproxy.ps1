# Run in an elevated (Administrator) PowerShell on Windows:
#   powershell -ExecutionPolicy Bypass -File \\wsl.localhost\Ubuntu\home\naifa\rommfork\setup_windows_portproxy.ps1
# Forwards Windows LAN ports 3000/5000 to the WSL2 VM so phones on the LAN can reach RomM.
# Re-run after every Windows reboot: the WSL IP changes.

$ErrorActionPreference = "Stop"
$wslIp = (wsl.exe hostname -I).Trim().Split(" ")[0]
if (-not $wslIp) { throw "Could not read WSL IP (is WSL running?)" }
Write-Host "WSL IP: $wslIp"

foreach ($port in 3000, 5000) {
  netsh interface portproxy delete v4tov4 listenport=$port listenaddress=0.0.0.0 | Out-Null
  netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$wslIp | Out-Null
  $rule = "RomM dev $port"
  # Profile Any: the LAN is often classified as Public, where Private-only rules do nothing.
  Get-NetFirewallRule -DisplayName $rule -ErrorAction SilentlyContinue | Remove-NetFirewallRule
  New-NetFirewallRule -DisplayName $rule -Direction Inbound -Protocol TCP -LocalPort $port -Action Allow -Profile Any | Out-Null
}

# Windows 11 Hyper-V firewall can still block inbound traffic into WSL.
try {
  Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultInboundAction Allow
} catch { Write-Host "Hyper-V firewall setting skipped: $_" }

netsh interface portproxy show v4tov4
$lanIp = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'WSL|Loopback|vEthernet|Virtual' -and $_.IPAddress -notlike '169.*' } | Select-Object -First 1).IPAddress
Write-Host "Done. On your phone use: http://${lanIp}:3000"
