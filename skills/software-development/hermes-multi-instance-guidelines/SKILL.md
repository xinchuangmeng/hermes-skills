---
name: hermes-multi-instance-guidelines
description: Conceptual guidelines for running multiple Hermes Agent instances on the same server. Focuses on isolation strategies and common pitfalls without specific dangerous commands.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, deployment, multi-instance, isolation]
    related_skills: [hermes-agent]
---

# Hermes Multi-Instance Guidelines

This document provides conceptual guidance for running multiple Hermes Agent instances on a single server, based on practical experience with existing installations.

## Core Principles

### 1. Discovery Before Installation
Always investigate existing Hermes installations before attempting to add another instance. Common findings:
- Instances often run under non-root users (e.g., `agentuser`)
- Configuration resides in `~/.hermes/` directory
- Default port is 3000

### 2. Isolation Levels
Choose the appropriate isolation level based on your needs:

| Level | Method | Use Case |
|-------|--------|----------|
| **Skill Isolation** | `--skills` flag | Different projects using same instance |
| **File Isolation** | `--worktree` flag | Projects that edit different files |
| **Profile Isolation** | `--profile` option | Different configurations, same binary |
| **Directory Isolation** | Custom `HERMES_HOME` | Separate data, shared binary |
| **Container Isolation** | Docker | Maximum separation, production |

### 3. Port Management
- First instance: typically port 3000
- Additional instances: 3001, 3002, etc.
- Always verify ports are not conflicting

## Common Scenarios & Solutions

### Scenario 1: Adding a Second Project
**Situation**: You have "小小书童" running and want to add "research-audit" project.

**Recommended approach**:
```bash
# Use skill isolation within existing Hermes
hermes chat --skills "ai-startup-user-validation"
```

**Why this works**:
- No additional installation needed
- Uses existing API keys and configuration
- Skills provide logical separation
- `--worktree` optional for file isolation

### Scenario 2: Complete Process Separation
**Situation**: Need independent processes for different teams/clients.

**Options**:
1. **Docker containers** (best isolation)
2. **Different system users** with separate home directories
3. **Profile system** with separate config directories

### Scenario 4: Multiple Messaging Platform Integration
**Situation**: Different projects need separate bot notifications (Feishu, Telegram, etc.)

**Configuration Strategy**:
1. **Port-based separation**: Run each Hermes instance on different ports
2. **Project-specific config**: Create separate configuration files for each project
3. **Platform-specific webhooks**: Each project gets its own webhook URL
4. **Simplified approach**: Start with basic webhook functionality before configuring full event systems

**Critical Discovery**: Multiple Hermes instances **cannot share the same Feishu App ID**. Each instance requires its own Feishu application with unique App ID and App Secret.

**Practical Experience**:
- Feishu bots often show "待上线" status - this usually means the app needs to be published or permissions configured
- Event subscription requires server to be accessible from internet (public IP or tunnel)
- Webhook-only mode works for sending notifications but not receiving @mentions
- Different Verification Tokens are needed for each bot instance

**Conflict Diagnosis Flow**:
1. **Check for existing instances**: `ps aux | grep -i hermes | grep -v grep`
2. **Verify port usage**: `ss -tlnp | grep -E ":(3000|3001|8000|8001|8002)"`
3. **Examine error logs**: Look for "Another local Hermes gateway is already using this Feishu app_id"
4. **Check configuration inheritance**: Verify if instances share the same platform configuration

**Solutions for Feishu App ID Conflicts**:
1. **Option A - CLI Mode**: Use `HERMES_HOME=/path/to/project/.hermes hermes chat` for direct CLI access
2. **Option B - Separate Feishu Apps**: Create new Feishu application for each Hermes instance
3. **Option C - Alternate Platforms**: Configure different platforms (Telegram, Discord) for different instances
4. **Option D - Sequential Usage**: Stop one instance before starting another

## Key Lessons Learned

### Lesson 1: User Context Matters
Existing Hermes installations often use dedicated users (not root). Attempting to install as root can cause permission issues and configuration conflicts.

### Lesson 2: Configuration Inheritance
When creating new instances, they may inherit or require configuration from existing installations. The `HERMES_HOME` environment variable controls which configuration directory is used.

### Lesson 3: Network Realities
Chinese cloud providers often have network restrictions that affect:
- Docker image pulls
- GitHub binary downloads
- External API access

### Lesson 4: Skill-Based Separation Often Suffices
For many use cases, running separate projects within the same Hermes instance using different skills is sufficient and simpler than full process isolation.

## Decision Framework

### Questions to Ask:
1. **Do projects need different API keys?** → Separate instances
2. **Do projects edit the same files?** → `--worktree` or separate instances
3. **Is there a security boundary?** → Separate users/containers
4. **Are network restrictions present?** → Plan for mirror sources

### Flowchart:
```
Existing Hermes? → Yes → Check user/port/config
                    ↓
           Need process isolation?
                    ↓
           Yes → Docker/separate user
           No  → Skill isolation (+worktree if needed)
```

## Best Practices

1. **Start with skill isolation** - Try simplest approach first
2. **Check before installing** - Investigate existing setup
3. **Document port assignments** - Avoid conflicts
4. **Test network access** - Before attempting downloads
5. **Use profiles for config variants** - Rather than multiple binaries

## Troubleshooting Concepts

### "Not configured" errors
- Usually means empty or missing configuration directory
- Solution: Ensure `HERMES_HOME` points to valid config or copy from existing

### Port conflicts
- Check with network monitoring tools
- Modify configuration to use different ports

### Permission issues
- Match user context of existing installation
- Avoid mixing root and non-root installations

### Platform Configuration Conflicts
**Symptoms**:
- "Another local Hermes gateway is already using this Feishu app_id"
- Gateway fails to start with platform connection errors
- Only one instance can connect to messaging platform at a time

**Diagnostic Steps**:
1. **Identify conflicting instances**: `ps aux | grep "hermes.*gateway" | grep -v grep`
2. **Check platform configurations**: Look for shared platform credentials
3. **Review error logs**: Check gateway startup logs for specific conflict messages
4. **Verify isolation level**: Ensure instances have truly separate configurations

**Resolution Strategies**:
1. **Immediate Workaround**: Use CLI mode (`hermes chat`) with `HERMES_HOME` pointing to project directory
2. **Platform Separation**: Create unique platform applications for each instance
3. **Sequential Operation**: Stop one instance before starting another
4. **Configuration Audit**: Ensure each instance has its own `platforms/` directory with unique credentials

**Quick CLI Access Pattern**:
```bash
# Access project-specific Hermes instance via CLI
cd /path/to/project
HERMES_HOME=/path/to/project/.hermes hermes chat
```

This allows direct interaction with the project's Hermes instance without gateway conflicts.

## Summary

Running multiple Hermes instances on one server is achievable through various isolation strategies. For most project separation needs, skill-based isolation within a single Hermes instance is sufficient and simplest. For strict security boundaries or resource isolation, consider Docker containers or separate system users.

The key is to understand your specific requirements and choose the appropriate level of isolation rather than defaulting to the most complex solution.