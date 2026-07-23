<#
.SYNOPSIS
    停止部署在deploy-server(121.41.238.92)上的慧笔Streamlit服务。

.DESCRIPTION
    本地运行，通过SSH远程操作。**只kill PID文件里记录的精确PID**，绝不用
    `pkill -f`之类的模式匹配——这台服务器是共用机器，同时跑着别人的生产容器
    (`ophthalmic-ai`，端口8501)和其他python3进程，本项目在另一台训练服务器上
    已经因为模式匹配误杀过一次别人的生产容器（见CLAUDE.md"不要重新踩的坑"），
    这里不能重犯。

.EXAMPLE
    powershell -File scripts/deploy_stop.ps1
#>

$ErrorActionPreference = "Stop"
$RemoteDir = "/root/sukai"
$PidFile = "$RemoteDir/streamlit.pid"

$checkCmd = "if [ -f $PidFile ]; then cat $PidFile; else echo NONE; fi"
$targetPid = (ssh deploy-server $checkCmd).Trim()

if ($targetPid -eq "NONE" -or [string]::IsNullOrWhiteSpace($targetPid)) {
    Write-Host "没有找到PID文件（$PidFile），可能本来就没在跑。"
    Write-Host "如果确认服务还在跑但PID文件丢了，手动登录服务器用 'ps aux | grep streamlit' 找到精确PID再kill，不要用模式匹配自动杀。"
    exit 0
}

$stopCmd = "if ps -p $targetPid > /dev/null 2>&1; then kill $targetPid && sleep 1 && echo STOPPED:$targetPid; else echo ALREADY_DEAD:$targetPid; fi; rm -f $PidFile"
$result = (ssh deploy-server $stopCmd).Trim()

if ($result.StartsWith("STOPPED:")) {
    Write-Host "已停止，PID=$($result.Substring(8))。"
} elseif ($result.StartsWith("ALREADY_DEAD:")) {
    Write-Host "进程已经不在了（PID=$($result.Substring(13))可能之前就退出了），PID文件已清理。"
} else {
    Write-Host "返回结果：$result"
}
