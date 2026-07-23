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

Write-Host "启动中（首次启动如果依赖还没装好，请先看 Docs/08-前端与部署操作手册.md）..."
$startCmd = "cd $RemoteDir && source .venv/bin/activate && nohup streamlit run app.py --server.port $Port --server.address 0.0.0.0 > streamlit.log 2>&1 & echo `$! > $PidFile ; disown"
ssh deploy-server $startCmd

Write-Host "等待服务起来..."
Start-Sleep -Seconds 8

$httpCode = (ssh deploy-server "curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://localhost:$Port").Trim()
if ($httpCode -eq "200") {
    Write-Host "启动成功，HTTP $httpCode。"
    # 上面`echo $!`拿到的其实是"cd && source && nohup ..."这条复合命令被
    # 整体丢进后台之后、bash为它开的那层shell包装器的PID，不是真正exec出来的
    # streamlit进程PID（bash在这种写法下不一定做尾调用exec优化）。实测过：
    # 按这个PID跑deploy_stop.ps1报告"已停止"，但真正吃内存的streamlit进程
    # 其实还活着、还占着端口，见Docs/Progress.md第三十二轮。这里改成按
    # "谁在监听这个端口"反查一次真实PID，覆盖掉PID文件，保证以后
    # deploy_stop.ps1杀的是真正的进程。
    $realPidCmd = "ss -tlnp 2>/dev/null | grep ':$Port ' | grep -oP 'pid=\K[0-9]+' | head -1"
    $realPid = (ssh deploy-server $realPidCmd).Trim()
    if ($realPid -match '^\d+$') {
        ssh deploy-server "echo $realPid > $PidFile"
        Write-Host "已用真实进程PID=$realPid覆盖PID文件（不是shell包装器PID）。"
    } else {
        Write-Host "警告：没能从端口反查到真实PID，PID文件里可能仍是包装器PID，建议手动登录服务器用 `"ps aux | grep streamlit`" 核对。"
    }
    Write-Host "访问地址：http://121.41.238.92:$Port"
} else {
    Write-Host "启动可能失败（HTTP返回 '$httpCode'，不是200），检查日志："
    Write-Host "  ssh deploy-server `"tail -60 $RemoteDir/streamlit.log`""
}
