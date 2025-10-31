# NSO Health Check and Auto-Fix Tool

## Overview

This tool automatically detects and fixes common NSO issues that can cause hangs or unresponsiveness:
- Hung/unresponsive NSO (not responding to status or API calls)
- Device locks preventing transactions
- Stuck sessions holding locks
- NSO processes not responding to normal shutdown commands

## Quick Usage

### From Command Line

```bash
# Full health check with auto-fix (recommended)
cd /Users/gudeng/MCP_Server
./quick_nso_fix.sh

# Or run directly
python3 nso_health_check_auto_fix_20251031_153500.py

# Check only, don't fix
python3 nso_health_check_auto_fix_20251031_153500.py --no-fix
```

### From MCP Server (AI Tools)

Use the `nso_health_check` tool:
```
nso_health_check(auto_fix=True)  # Full check and auto-fix
nso_health_check(auto_fix=False) # Check only
```

## What It Does

### Detection Phase

1. **NSO Status Check**: Verifies NSO responds to `ncs --status`
2. **API Connection Test**: Tests if NSO API is responsive (can connect, start session, read config)
3. **Device Lock Detection**: Tests each device for locks by attempting write transactions
4. **Process Check**: Lists all NSO-related processes (main NCS, Java VMs, Python VMs)

### Auto-Fix Phase (when `auto_fix=True`)

1. **Clear Locks**: Attempts to clear locks via NSO CLI `clear locks` command
2. **Kill Hung Processes**: If NSO is hung, safely kills all NSO processes:
   - Python VMs (package processes) first
   - Java processes (webapp-runner, NcsJVMLauncher) second
   - Main NCS process last
3. **Restart NSO**: Automatically restarts NSO if killed or not running
4. **Verification**: Waits for NSO to start and verifies it's responsive

## Exit Codes

- `0`: Healthy - No issues detected
- `1`: Issues found but fixed - Health check found problems and successfully fixed them
- `2`: Issues found, not fixed - Health check found problems but couldn't fix them automatically

## Examples

### Normal Healthy NSO
```bash
$ ./quick_nso_fix.sh
======================================================================
NSO Health Check and Auto-Fix Tool
======================================================================

[15:46:14] ℹ️  Checking NSO status...
[15:46:14] ✅ NSO is running and responsive

[15:46:14] ℹ️  Checking NSO API connection...
[15:46:16] ✅ NSO API is responsive (1.91s)

[15:46:16] ✅ No device locks detected
[15:46:16] ℹ️  Found 7 NSO process(es)

======================================================================
Health Check Summary
======================================================================

✅ No issues detected
Total check time: 2.22 seconds
```

### Hung NSO Auto-Fixed
```bash
$ ./quick_nso_fix.sh
...
[15:32:10] ❌ NSO status check timed out - NSO appears hung
[15:32:10] ❌ NSO API hung (connection timeout)
...
[15:32:12] 🔧 Killing 7 NSO process(es)...
[15:32:15] ✅ Killed 7 process(es)
[15:32:15] 🔧 Restarting NSO...
[15:32:25] ✅ NSO restart successful!

======================================================================
Health Check Summary
======================================================================

✅ Applied 2 fix(es):
   - Killed 7 hung NSO processes
   - Restarted NSO
```

## When to Use

- **Before important operations**: Run health check before starting major configuration changes
- **When operations hang**: If `t.apply()` or other NSO operations hang, run this tool
- **Proactive monitoring**: Run periodically to catch issues early
- **After manual NSO restarts**: Verify NSO is healthy after manual intervention

## Integration

### Cron Job (Optional)

Add to crontab to run health check every hour:
```bash
0 * * * * /Users/gudeng/MCP_Server/quick_nso_fix.sh >> /tmp/nso_health.log 2>&1
```

### Before Critical Operations

Add to scripts before important NSO operations:
```python
from nso_health_check_auto_fix_20251031_153500 import NSOHealthChecker

checker = NSOHealthChecker()
if checker.run_full_check(auto_fix=True) > 1:
    # Critical issues found, abort or alert
    raise Exception("NSO health check failed")
```

## Files

- `nso_health_check_auto_fix_20251031_153500.py` - Main health check tool
- `quick_nso_fix.sh` - Quick wrapper script
- `nso_health_check()` - MCP tool wrapper (in fastmcp_nso_server_auto_generated.py)

## Troubleshooting

If the tool itself hangs:
1. The tool has a 60-second timeout
2. If it times out, NSO is severely hung
3. Manually kill NSO processes: `ps aux | grep ncs` then `kill -9 <PID>`
4. Restart NSO: `cd /Users/gudeng/ncs-run && /Users/gudeng/NCS-614/bin/ncs`

## Best Practices

1. **Run before critical operations**: Always check health before major config changes
2. **Monitor logs**: Check output for warnings about slow responses
3. **Don't ignore warnings**: Slow API responses may indicate future problems
4. **Keep NSO updated**: Ensure NSO packages are reloaded after changes

