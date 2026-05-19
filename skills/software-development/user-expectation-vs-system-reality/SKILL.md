---
name: user-expectation-vs-system-reality
title: User Expectation vs System Reality Gap
description: Diagnose and bridge the gap when users expect automatic functionality that requires explicit setup
tags:
  - diagnosis
  - user-education
  - system-state
  - expectation-management
trigger: |
  When a user asks "why doesn't X work?" or "why isn't Y happening?" implying they expect automatic functionality
---

# User Expectation vs System Reality Gap

## Problem Pattern
Users often expect systems to work automatically without understanding they need explicit configuration. Common examples:
- Cronjob reminders (expect automatic reminders, but need explicit cronjob creation)
- Multiple service instances (expect all instances to be running, but need explicit startup)
- Platform connections (expect automatic connectivity, but need explicit configuration)

## Diagnosis Flow

### 1. Check Actual System State First
Before explaining theory, check what actually exists:
```bash
# For cronjobs
cronjob list

# For running processes
ps aux | grep -i [relevant_keyword]

# For network services
ss -tlnp | grep -E ":[port_range]"

# For configuration files
ls -la ~/.hermes/profiles/
```

### 2. Identify the Expectation Gap
Ask clarifying questions to understand what the user expects:
- "Are you expecting automatic reminders at specific times?"
- "Is this service supposed to be always running?"
- "How were you accessing this before?"

### 3. Provide Concrete Evidence
Show the user what's actually configured vs what they expect:
```
✅ Current state: No cronjobs configured
❌ User expectation: Automatic reminders at 21:00
```

### 4. Create Demonstration Examples
Instead of just explaining, create a working example:
```bash
# Create a test cronjob to demonstrate
cronjob create --name "测试提醒" --prompt "测试提醒内容" --schedule "5m"
```

### 5. Offer Setup Options
Provide multiple paths forward:
- Option A: Quick fix (create the missing configuration)
- Option B: Proper setup (full configuration with verification)
- Option C: Automation (script to set up automatically)

## Common Scenarios

### Scenario 1: Missing Cronjobs
**User says**: "为什么时间到不提醒我"
**Diagnosis**: `cronjob list` shows empty
**Solution**: 
1. Explain cronjobs require explicit creation
2. Create a test cronjob to demonstrate
3. Guide user through creating their desired schedule

### Scenario 2: Service Not Running  
**User says**: "怎么登录XX助手"
**Diagnosis**: No process running on expected port
**Solution**:
1. Check for existing configurations (`ls ~/.hermes/profiles/`)
2. Check if service should be running (`ps aux | grep`)
3. Provide startup commands for each possible configuration

### Scenario 3: Missing Platform Connection
**User says**: "收不到消息"
**Diagnosis**: Platform not configured in config.yaml
**Solution**:
1. Check platform configuration
2. Guide through platform setup
3. Test connection

## Key Principles

1. **Show, don't just tell**: Create working examples
2. **Check before assuming**: Always verify actual system state
3. **Bridge the gap**: Connect user expectations to system requirements
4. **Empower, not just fix**: Teach users how to set things up themselves

## Verification Steps
After implementing a solution:
1. Confirm the system now works as expected
2. Ask user to verify functionality
3. Document the setup for future reference
4. Consider creating a skill if this is a recurring pattern