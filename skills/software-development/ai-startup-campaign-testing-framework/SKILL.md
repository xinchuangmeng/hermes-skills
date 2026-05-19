---
name: ai-startup-campaign-testing-framework
description: Comprehensive 7-step testing framework for validating AI-powered user outreach campaigns - from system integrity to emergency planning
tags: [testing, validation, email-campaign, startup, mvp, quality-assurance]
author: Hermes Agent
created: 2026-04-23
version: 1.0
---

# AI Startup Campaign Testing Framework

Complete testing methodology for validating AI-powered user outreach campaigns, particularly for B2B SaaS startups conducting user research validation.

## When to Use

Use this framework when:
- Testing email outreach campaigns for user research
- Validating AI-generated content quality
- Ensuring campaign system robustness
- Preparing for time-sensitive "golden hour" campaigns
- Creating standardized testing protocols for startup MVPs

## The 7-Step Testing Framework

### 1. System Integrity Test
**Goal**: Verify all dependencies and scripts are functional

```python
# Example: Check Python dependencies
import json, smtplib, time, os, sys, datetime
print("✅ All core dependencies available")

# Check file structure
required_files = [
    'target_users.json',
    'personalized_messages.json', 
    'campaign_config.json',
    'sender_system.py',
    'monitor_dashboard.py'
]
```

**Key Checks**:
- Python version and core modules
- File existence and permissions
- Script importability

### 2. Configuration Validation Test
**Goal**: Verify all configuration files are correctly structured

```python
def validate_config(config_file):
    import json
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    required_fields = [
        'smtp_server', 'smtp_port', 'sender_email',
        'send_interval', 'max_retries', 'test_mode'
    ]
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
```

**Key Checks**:
- JSON structure validity
- Required field presence
- Sensible value ranges (e.g., send_interval > 0)

### 3. Data Quality Test
**Goal**: Verify target user data and message content quality

```python
def validate_target_data(targets_file):
    with open(targets_file, 'r') as f:
        data = json.load(f)
    
    targets = data.get('targets', [])
    
    # Field completeness
    required_fields = ['id', 'name', 'email', 'conference', 'primary_pain', 'pain_intensity']
    field_stats = {field: 0 for field in required_fields}
    
    for target in targets:
        for field in required_fields:
            if field in target and target[field]:
                field_stats[field] += 1
    
    # Quality score calculation
    quality_score = sum(field_stats.values()) / (len(required_fields) * len(targets)) * 100
    return quality_score > 80
```

**Key Checks**:
- Field completeness (>80% threshold)
- Email format validity
- Pain intensity scoring (0-10 scale)
- Data consistency between targets and messages

### 4. Single Send Test
**Goal**: Test individual email sending with error handling

```python
def test_single_send(config, test_message):
    """Test sending one email with comprehensive error handling"""
    
    # 1. SMTP connection test
    try:
        smtp = smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=10)
        smtp.ehlo()
        if config['smtp_port'] == 587:
            smtp.starttls()
            smtp.ehlo()
        print("✅ SMTP connection successful")
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False
    
    # 2. Authentication test (with expected failure for dummy credentials)
    try:
        smtp.login(config['sender_email'], config['sender_password'])
        print("⚠️ Authentication succeeded (unexpected with test credentials)")
    except smtplib.SMTPAuthenticationError:
        print("✅ Authentication failed as expected with test credentials")
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    smtp.quit()
    return True
```

**Key Checks**:
- SMTP server reachability
- Port accessibility (587 for STARTTLS, 465 for SSL)
- Graceful handling of authentication failures
- Network timeout handling

### 5. Monitoring Dashboard Test
**Goal**: Verify real-time campaign monitoring functionality

```python
def test_monitoring_dashboard():
    # 1. File existence check
    dashboard_files = ['monitor_dashboard.py', 'cli_interface.py', 'test_data.json']
    
    # 2. Module import test
    import monitor_dashboard as dashboard
    
    # 3. Class and method verification
    assert hasattr(dashboard, 'CampaignDashboard')
    
    # 4. CLI interface test
    import subprocess
    result = subprocess.run(['python3', 'cli_interface.py', '--help'], 
                          capture_output=True, text=True)
    assert result.returncode == 0
```

**Key Checks**:
- Dashboard file integrity
- Python module functionality
- CLI interface usability
- Data loading and display

### 6. Full Campaign Simulation Test
**Goal**: Simulate complete campaign lifecycle

```python
class CampaignSimulator:
    def simulate_campaign(self, num_targets=5):
        """Simulate complete campaign with realistic success/failure rates"""
        
        results = {
            'targets_selected': num_targets,
            'messages_generated': num_targets,
            'emails_sent': 0,
            'send_successes': 0,
            'send_failures': 0,
            'replies_received': 0,
            'reply_rate': 0
        }
        
        # Simulate sending with 90% success rate
        for i in range(num_targets):
            success = random.random() < 0.9
            results['emails_sent'] += 1
            if success:
                results['send_successes'] += 1
            else:
                results['send_failures'] += 1
        
        # Simulate replies with 35-45% rate
        if results['send_successes'] > 0:
            reply_rate = random.uniform(0.35, 0.45)
            results['replies_received'] = int(results['send_successes'] * reply_rate)
            results['reply_rate'] = reply_rate * 100
        
        return results
```

**Key Checks**:
- End-to-end workflow simulation
- Realistic success/failure rates
- KPI calculation and tracking
- Report generation

### 7. Emergency Planning Test
**Goal**: Test system robustness and recovery procedures

```python
def test_emergency_scenarios():
    """Test system response to various failure scenarios"""
    
    scenarios = [
        {
            'name': 'Network outage',
            'test': lambda: _simulate_network_failure(),
            'recovery': ['pause_sending', 'log_outage', 'resume_on_recovery']
        },
        {
            'name': 'SMTP service failure', 
            'test': lambda: _simulate_smtp_failure(),
            'recovery': ['switch_to_backup_smtp', 'retry_failed_sends']
        },
        {
            'name': 'Data corruption',
            'test': lambda: _simulate_data_corruption(),
            'recovery': ['stop_all_operations', 'restore_from_backup', 'validate_data']
        }
    ]
    
    for scenario in scenarios:
        print(f"\nTesting: {scenario['name']}")
        try:
            scenario['test']()
            print(f"✅ Scenario handled: {scenario['recovery']}")
        except Exception as e:
            print(f"❌ Scenario failed: {e}")
```

**Key Checks**:
- Network failure handling
- Service outage recovery
- Data backup and restore
- Graceful degradation

## Implementation Template

Create a complete test suite with this structure:

```
project_testing/
├── test_system_integrity.py
├── test_config_validation.py
├── test_data_quality.py
├── test_single_send.py
├── test_monitoring_dashboard.py
├── test_full_campaign.py
├── test_emergency_planning.py
└── run_all_tests.py
```

## Common Pitfalls and Solutions

### Pitfall 1: Incorrect Field Expectations
**Problem**: Assuming data has specific field names that don't match actual structure
**Solution**: Always inspect actual data structure before writing validation

```python
# WRONG: Assuming specific field names
required_fields = ['paper_title', 'pain_points']

# RIGHT: Inspect first, then validate
sample = data['targets'][0]
actual_fields = list(sample.keys())
required_fields = ['id', 'email', 'conference']  # Based on actual data
```

### Pitfall 2: Network Timeout Issues
**Problem**: SMTP tests hanging indefinitely
**Solution**: Always use timeouts and handle TimeoutException

```python
import socket
socket.setdefaulttimeout(10)  # Global timeout

# Or per-connection
smtp = smtplib.SMTP(server, port, timeout=10)
```

### Pitfall 3: Overly Complex Simulations
**Problem**: Full simulations taking too long
**Solution**: Use simplified simulations for quick testing

```python
# Use small sample size for quick tests
test_targets = targets[:3]  # Test with first 3 targets only
```

### Pitfall 4: Missing Error Recovery
**Problem**: Tests crash on first error
**Solution**: Implement comprehensive error handling

```python
def safe_test(test_func, test_name):
    try:
        result = test_func()
        print(f"✅ {test_name}: Passed")
        return result
    except Exception as e:
        print(f"❌ {test_name}: Failed - {e}")
        return None
```

## Verification Steps

After running all tests, verify:

1. **All 7 test categories pass** (minimum 80% success rate)
2. **Data quality score > 80%**
3. **SMTP servers reachable** (connection successful)
4. **Monitoring dashboard functional** (real-time updates work)
5. **Emergency plan exists** (RTO/RPO defined)
6. **Test reports generated** (JSON format for analysis)

## Expected Outcomes

- **System readiness confidence**: >90%
- **Data quality score**: >80%
- **SMTP connectivity**: 100% for primary servers
- **Test coverage**: All critical paths tested
- **Emergency preparedness**: Complete contingency plans

## Related Skills

- `academic-researcher-user-validation` - For user research methodology
- `ai-startup-user-validation` - For startup validation workflows
- `qq-email-smtp-automation` - For email sending implementation
- `musk-ceo-user-validation-framework` - For CEO-level execution mindset