# AI Employee Silver Tier - Launcher
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Employee Silver Tier Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$VaultPath = Get-Location

# Ensure directories exist
@("Needs_Action","Plans","Pending_Approval","Approved","Rejected","Done","Logs","Dropbox") | ForEach-Object {
    New-Item -ItemType Directory -Path $_ -Force | Out-Null
}

function Show-Menu {
    Write-Host "Select an option:" -ForegroundColor Yellow
    Write-Host "1. Start Orchestrator (watches Needs_Action, creates plans, processes approvals)"
    Write-Host "2. Start File System Watcher (monitors Dropbox folder)"
    Write-Host "3. Test Email MCP Server"
    Write-Host "4. Run Full Workflow Demo"
    Write-Host "5. Create Windows Scheduled Task"
    Write-Host "6. Show Dashboard"
    Write-Host "Q. Quit"
    Write-Host ""
}

function Start-Orchestrator {
    Write-Host "Starting Orchestrator... (Ctrl+C to stop)" -ForegroundColor Green
    python src/orchestrator.py
}

function Start-FileWatcher {
    Write-Host "Starting File System Watcher... (Ctrl+C to stop)" -ForegroundColor Green
    Write-Host "Drop files into: $VaultPath\Dropbox" -ForegroundColor Yellow
    python -c "import sys; sys.path.insert(0, 'src'); from simple_filesystem_watcher import SimpleFileSystemWatcher; SimpleFileSystemWatcher('.').run()"
}

function Test-MCPServer {
    Write-Host "Testing Email MCP Server..." -ForegroundColor Green
    Write-Output '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python email_mcp_server.py
}

function Test-FullWorkflow {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Full Workflow Demo" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # Step 1: Create a test file in Dropbox
    Write-Host "Step 1: Dropping a test file..." -ForegroundColor Yellow
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Set-Content -Path "Dropbox\demo_invoice_$timestamp.txt" -Value "Invoice for consulting services - $1,000"
    Write-Host "  -> File dropped: demo_invoice_$timestamp.txt" -ForegroundColor Gray
    Start-Sleep -Seconds 1

    # Step 2: Process with filesystem watcher
    Write-Host "Step 2: Filesystem watcher processing..." -ForegroundColor Yellow
    python -c "import sys; sys.path.insert(0, 'src'); from simple_filesystem_watcher import SimpleFileSystemWatcher; w = SimpleFileSystemWatcher('.'); w.check_interval = 1; [w.process_file(f) for f in w.scan_for_new_files()]"
    Start-Sleep -Seconds 1

    # Step 3: Orchestrator creates plan
    Write-Host "Step 3: Orchestrator creating plan..." -ForegroundColor Yellow
    python -c "import sys; sys.path.insert(0, 'src'); from orchestrator import Orchestrator; o = Orchestrator('.'); c = o.run_once(); print(f'  -> Processed {c} items')"

    # Step 4: Show plans
    Write-Host "Step 4: Plans created:" -ForegroundColor Yellow
    $plans = Get-ChildItem "Plans" -Filter "*.md" | Select-Object Name
    if ($plans) {
        $plans | ForEach-Object { Write-Host "  -> $($_.Name)" -ForegroundColor Gray }
    } else {
        Write-Host "  -> No plans yet" -ForegroundColor Red
    }

    # Step 5: Simulate approval
    Write-Host "Step 5: Simulating human approval..." -ForegroundColor Yellow
    $planFiles = Get-ChildItem "Plans" -Filter "PLAN_demo_*.md"
    foreach ($pf in $planFiles) {
        Copy-Item -Path $pf.FullName -Destination "Approved\APPROVED_$($pf.Name)"
        Write-Host "  -> Approved: $($pf.Name)" -ForegroundColor Gray
    }

    # Step 6: Process approvals
    Write-Host "Step 6: Processing approvals..." -ForegroundColor Yellow
    python -c "import sys; sys.path.insert(0, 'src'); from orchestrator import Orchestrator; o = Orchestrator('.'); a = o.process_approvals(); r = o.process_rejections(); o.update_dashboard(); print(f'  -> Approved: {a}, Rejected: {r}')"

    # Step 7: Show results
    Write-Host "Step 7: Results:" -ForegroundColor Yellow
    Write-Host "  -> Dashboard:" -ForegroundColor Gray
    Get-Content "Dashboard.md"

    Write-Host ""
    Write-Host "Demo complete!" -ForegroundColor Green
    Write-Host "Check the Done folder for completed items." -ForegroundColor Green
}

do {
    Show-Menu
    $choice = Read-Host "Enter choice (1-6, Q)"
    switch ($choice) {
        "1" { Start-Orchestrator }
        "2" { Start-FileWatcher }
        "3" { Test-MCPServer }
        "4" { Test-FullWorkflow }
        "5" {
            Write-Host "Creating Windows Scheduled Task..." -ForegroundColor Green
            python src/scheduler.py --create-task
        }
        "6" {
            if (Test-Path "Dashboard.md") {
                Get-Content "Dashboard.md"
            } else {
                Write-Host "Dashboard not found" -ForegroundColor Red
            }
        }
    }
    if ($choice -ne 'q' -and $choice -ne 'Q') {
        Write-Host ""
        Write-Host "Press any key to continue..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
} while ($choice -ne 'q' -and $choice -ne 'Q')
