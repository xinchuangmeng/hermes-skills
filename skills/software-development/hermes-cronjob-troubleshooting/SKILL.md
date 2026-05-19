---
name: hermes-cronjob-troubleshooting
description: Troubleshoot Hermes cronjob scheduling and notification issues - why scheduled tasks don't run or don't notify users
tags: [hermes, cronjob, scheduling, notifications, troubleshooting]
version: 1.0
---

# Hermes Cronjob Troubleshooting

## When to Use This Skill
- User says "为什么时间到不提醒我" (Why don't I get notifications when time is up?)
- Scheduled tasks don't run at expected times
- Cron jobs are created but don't execute
- No notifications received for completed tasks

## Problem Diagnosis

Common reasons why cronjobs don't work:

### 1. No Cronjobs Exist
Check if any cronjobs are scheduled:
```bash
hermes cronjob list
```

If list is empty, no cronjobs are configured.

### 2. Cronjob Schedule Issues
- Incorrect cron syntax
- Timezone mismatch
- One-time jobs that have already run

### 3. Notification Delivery Issues
- Wrong delivery target
- Platform connection problems
- Message format issues

### 4. System Issues
- Hermes gateway not running
- System time incorrect
- Permission problems

## Step-by-Step Troubleshooting

### Step 1: Check Existing Cronjobs
```bash
hermes cronjob list
```

Expected output shows:
- Job ID
- Schedule
- Status (active/paused)
- Next run time

### Step 2: Verify Cronjob Details
For each job, check:
```bash
# Get detailed info about a specific job
hermes cronjob info <job_id>
```

Look for:
- Correct schedule expression
- Valid delivery target
- Skills loaded (if any)
- Last run time and status

### Step 3: Check Hermes Gateway Status
Cronjobs require the Hermes gateway to be running:
```bash
hermes gateway status
```

If gateway is not running:
```bash
hermes gateway start
```

### Step 4: Test Cronjob Manually
Run the cronjob immediately to test:
```bash
hermes cronjob run <job_id>
```

Check if:
1. Job executes successfully
2. Output is generated
3. Notification is sent

### Step 5: Check System Time
```bash
date
timedatectl status
```

Ensure system time matches your timezone.

## Common Issues & Solutions

### Issue 1: No Cronjobs Scheduled
**Solution**: Create a cronjob:
```bash
hermes cronjob create \
  --schedule "0 21 * * *" \
  --prompt "Reminder: It's 9 PM, time for your daily review" \
  --name "Daily 9 PM reminder"
```

### Issue 2: Incorrect Schedule Syntax
**Common mistakes**:
- `21:00` (wrong) vs `0 21 * * *` (correct)
- Missing timezone specification

**Correct formats**:
```bash
# Every day at 9 PM
--schedule "0 21 * * *"

# Every 2 hours
--schedule "every 2h"

# In 30 minutes
--schedule "30m"

# Specific ISO timestamp
--schedule "2024-12-31T23:59:00Z"
```

### Issue 3: Wrong Delivery Target
**Symptoms**: Job runs but no notification received

**Check delivery target**:
```bash
hermes cronjob info <job_id>
```

**Common targets**:
- `origin` (default, delivers to current chat)
- `telegram` (delivers to Telegram home channel)
- `telegram:chat_id:thread_id` (specific Telegram thread)
- `discord:#channel-name` (specific Discord channel)

**Solution**: Update delivery target:
```bash
hermes cronjob update <job_id> --deliver "origin"
```

### Issue 4: Gateway Not Running
**Symptoms**: Cronjobs don't execute at all

**Check gateway**:
```bash
systemctl status hermes-gateway
```

**Start gateway**:
```bash
sudo systemctl start hermes-gateway
sudo systemctl enable hermes-gateway  # Auto-start on boot
```

### Issue 5: Timezone Mismatch
**Symptoms**: Jobs run at wrong time

**Check system timezone**:
```bash
timedatectl
```

**Set timezone** (if needed):
```bash
sudo timedatectl set-timezone Asia/Shanghai
```

## Creating Reliable Reminders

### Example 1: Daily 9 PM Reminder
```bash
hermes cronjob create \
  --schedule "0 21 * * *" \
  --prompt "🕘 **晚上9点提醒**\n\n现在是黄金时间，请开始：\n1. 检查今日任务完成情况\n2. 规划明日工作\n3. 发送每日报告" \
  --name "Daily 9 PM reminder" \
  --deliver "origin"
```

### Example 2: Hourly Progress Check
```bash
hermes cronjob create \
  --schedule "0 * * * *" \
  --prompt "⏰ **每小时进度检查**\n\n请报告当前工作进展和遇到的障碍" \
  --name "Hourly check-in" \
  --deliver "origin"
```

### Example 3: Weekly Summary
```bash
hermes cronjob create \
  --schedule "0 20 * * 0" \
  --prompt "📊 **每周总结**\n\n请总结本周：\n1. 完成的主要工作\n2. 学到的关键知识\n3. 下周计划" \
  --name "Weekly summary" \
  --deliver "origin"
```

## Verification Checklist

- [ ] Cronjob exists (`hermes cronjob list`)
- [ ] Schedule syntax is correct
- [ ] Gateway is running (`hermes gateway status`)
- [ ] Delivery target is correct
- [ ] Timezone matches your location
- [ ] Job runs manually (`hermes cronjob run <job_id>`)
- [ ] Notification is received

## Debug Commands

```bash
# View cronjob logs
tail -f ~/.hermes/logs/cron.log

# Check system cron logs
sudo tail -f /var/log/syslog | grep cron

# List all system cron jobs
crontab -l

# Check Hermes service logs
sudo journalctl -u hermes-gateway -f
```

## User-Specific Considerations

Based on user profile:
- Prefers Chinese notifications with structured content
- Values 21:00 (9 PM) as "黄金窗口" (golden window)
- Likes step-by-step reminders
- Wants concise, actionable notifications

## Related Skills
- `cronjob` - Basic cronjob management tool
- `hermes-multi-agent-profiles` - Profile-specific cronjobs
- `project-specific-hermes-configuration` - Project reminder systems