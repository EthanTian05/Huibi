<#
.SYNOPSIS
    启动部署在deploy-server(121.41.238.92)上的慧笔Streamlit服务。

.DESCRIPTION
    本地运行，通过SSH远程操作。会先检查是否已经在跑（读PID文件），避免重复启动。
    只用PID文件里记录的精确PID做状态判断，不用"streamlit run app.py"这类字符串
    模式匹配（这台服务器是共用机器，模式匹配可能误伤同名进程，见CLAUDE.md
    "不要重新踩的坑"）。

.EXAMPLE
    powershell -File scripts/deploy_start.ps1
#>

$ErrorActionPreference = "Stop"
$RemoteDir = "/root/sukai"
$Port = 8503
$PidFile = "$RemoteDir/streamlit.pid"

Write-Host "检查deploy-server上是否已经在运行..."
$checkCmd = "if [ -f $PidFile ]; then P=`$(cat $PidFile); if ps -p `$P > /dev/null 2>&1; then echo RUNNING:`$P; else echo STALE; fi; else echo NOTRUNNING; fi"
$status = (ssh deploy-server $checkCmd).Trim()

if ($status.StartsWith("RUNNING:")) {
    $existingPid = $status.Substring(8)
    Write-Host "已经在运行，PID=$existingPid，端口$Port。如需重启，先跑 deploy_stop.ps1 再跑本脚本。"
    Write-Host "访问地址：http://121.41.238.92:$Port"
    exit 0
}

if ($status -eq "STALE") {
    Write-Host "PID文件存在但进程已经不在了，清理旧文件后重新启动。"
    ssh deploy-server "rm -f $PidFile"
}

Write-Host "启动中（首次启动如果依赖还没装好，请先看 Docs/08-部署操作手册.md）..."
$startCmd = "cd $RemoteDir && source .venv/bin/activate && nohup streamlit run app.py --server.port $Port --server.address 0.0.0.0 > streamlit.log 2>&1 & echo `$! > $PidFile ; disown"
ssh deploy-server $startCmd

Write-Host "等待服务起来..."
Start-Sleep -Seconds 8

$httpCode = (ssh deploy-server "curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://localhost:$Port").Trim()
if ($httpCode -eq "200") {
    Write-Host "启动成功，HTTP $httpCode。"
    Write-Host "访问地址：http://121.41.238.92:$Port"
} else {
    Write-Host "启动可能失败（HTTP返回 '$httpCode'，不是200），检查日志："
    Write-Host "  ssh deploy-server `"tail -60 $RemoteDir/streamlit.log`""
}
