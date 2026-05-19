---
name: project-specific-feishu-configuration
description: Configure project-specific Feishu (Lark) webhooks for Hermes instances with isolated project configurations
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feishu, lark, webhook, configuration, project, isolation]
    related_skills: [hermes-multi-instance-guidelines, hermes-agent]
---

# Project-Specific Feishu Configuration

Configure isolated Feishu (Lark) webhooks for project-specific Hermes instances, keeping project notifications separate from system-level notifications.

## Use Case

When you need:
- Project-specific Hermes instances with dedicated Feishu notifications
- Clear separation between project-level and system-level communications
- Different notification channels for different projects
- Isolated configuration for each project's needs

## Core Concept

Create project-specific configuration files that define:
1. Project name and personality
2. Project-specific skills
3. Dedicated Feishu webhook for project notifications

## Implementation Steps

### Step 1: Create Project Directory and Configuration

```bash
# Create project directory
mkdir -p ~/project-name
cd ~/project-name

# Create project-specific configuration
cat > config.yaml << EOF
name: "project-name"
personality: "technical"  # Project-specific personality
skills: "skill1,skill2,skill3"  # Project-specific skills

feishu:
  webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_PROJECT_WEBHOOK"
  secret: "YOUR_PROJECT_SECRET"
EOF
```

### Step 2: Customize Configuration

Edit the configuration template with your specific values:

```yaml
# Example: E-commerce project configuration
name: "sea-ecommerce"
personality: "technical"
skills: "data-science,github,productivity"

feishu:
  webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/xxx2"
  secret: "secret2"
```

### Step 3: Start Project-Specific Hermes Instance

```bash
cd ~/project-name
hermes chat --config config.yaml
```

## Configuration Template

```yaml
# config.yaml template
name: "PROJECT_NAME"
personality: "technical|helpful|concise|creative"  # Choose one
skills: "COMMA_SEPARATED_SKILL_LIST"

feishu:
  webhook_url: "YOUR_FEISHU_WEBHOOK_URL"
  secret: "YOUR_FEISHU_SECRET"
```

## Complete Example: E-commerce Project

### Directory Structure
```
~/sea-ecommerce/
├── config.yaml          # Project configuration
├── src/                 # Project source code
└── docs/                # Project documentation
```

### Configuration File
```yaml
# ~/sea-ecommerce/config.yaml
name: "sea-ecommerce"
personality: "technical"
skills: "data-science,github,productivity"

feishu:
  webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/xxx2"
  secret: "secret2"
```

### Usage
```bash
# Navigate to project directory
cd ~/sea-ecommerce

# Start Hermes with project configuration
hermes chat --config config.yaml

# Or with additional options
hermes chat --config config.yaml --skills "data-science,github"
```

## Verification

After creating your configuration, verify it:

```bash
# Check configuration file exists
ls -la ~/project-name/config.yaml

# View configuration content
cat ~/project-name/config.yaml

# Test YAML syntax (optional)
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))" 2>/dev/null && echo "YAML syntax OK"
```

## Benefits

1. **Project Isolation**: Each project has its own notification channel
2. **Clear Context**: Notifications clearly indicate which project they relate to
3. **Customized Skills**: Each project loads only relevant skills
4. **Flexible Personalities**: Different projects can use different assistant personalities
5. **Easy Management**: Configuration stays with the project files

## Common Project Types and Configurations

### E-commerce Project
```yaml
name: "ecommerce-store"
personality: "technical"
skills: "data-science,github,productivity,linear"
feishu: {webhook_url: "...", secret: "..."}
```

### Research Project
```yaml
name: "research-paper"
personality: "teacher"
skills: "arxiv,research,obsidian,notion"
feishu: {webhook_url: "...", secret: "..."}
```

### Development Project
```yaml
name: "api-backend"
personality: "concise"
skills: "github,test-driven-development,systematic-debugging"
feishu: {webhook_url: "...", secret: "..."}
```

## Best Practices

1. **Descriptive Names**: Use clear project names in configuration
2. **Relevant Skills**: Only load skills needed for the project
3. **Secure Secrets**: Keep Feishu secrets secure
4. **Version Control**: Add config.yaml to .gitignore if it contains secrets
5. **Documentation**: Document the purpose of each project's Feishu channel

## Troubleshooting

### Issue: Configuration not loading
```bash
# Check file path
pwd
ls -la config.yaml

# Check YAML syntax
cat config.yaml
```

### Issue: Feishu notifications not working
```bash
# Test webhook directly
curl -X POST -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"Test from project"}}' \
  "YOUR_WEBHOOK_URL"
```

### Issue: Skills not loading
```bash
# Check skill names are correct
hermes chat --skills "skill-name"

# List available skills
hermes chat --skills-list
```

## Integration with Development Workflow

### Git Integration
```bash
# Add configuration template (without secrets) to repository
git add config.yaml.template

# Keep actual config with secrets in .gitignore
echo "config.yaml" >> .gitignore
```

### Environment-Specific Configurations
```bash
# Create different configs for different environments
cp config.yaml config.production.yaml
cp config.yaml config.development.yaml
```

## Summary

Project-specific Feishu configuration allows you to create isolated Hermes instances for different projects, each with its own notification channel and skill set. This approach keeps project communications organized and contextually relevant while maintaining the flexibility to customize each project's AI assistant behavior.