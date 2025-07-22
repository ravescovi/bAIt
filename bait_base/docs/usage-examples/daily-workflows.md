# Daily Workflows with bAIt

This document provides practical examples of how different beamline staff use bAIt in their daily workflows.

## Beamline Scientist Workflows

### Morning Routine: System Check

**Dr. Sarah Chen, Beamline Scientist at 8-ID**

```bash
# Quick system overview
$ bait-query 8id-bits "What's the current system status?"

System Status for 8-ID Beamline:
✅ 12 IOCs running normally
✅ Bluesky environment active
✅ All detectors responding
⚠️  Warning: Motor controller temperature elevated (68°C)
📊 Last successful scan: 2 hours ago
🔄 Queue server: 3 plans pending

Recommendations:
- Monitor motor controller temperature
- Check cooling system if temperature exceeds 70°C
```

### Experiment Planning

```bash
# Planning a new experiment
$ bait-query 8id-bits "What's the best detector configuration for small-angle scattering?"

Detector Configuration Recommendations:
🎯 Primary: Lambda detector (detector_ioc_1)
   - Optimal for SAXS measurements
   - Current configuration: 2048x2048 pixels
   - Exposure time: 0.1-10 seconds recommended

🎯 Secondary: Pilatus detector (detector_ioc_2)  
   - Better for wide-angle measurements
   - Current configuration: 1024x1024 pixels
   - Exposure time: 0.01-1 second recommended

📋 Suggested scan parameters:
   - Sample-detector distance: 2-5 meters
   - Beam size: 100-500 μm
   - Energy range: 8-12 keV optimal
```

### Troubleshooting During Experiments

```bash
# During experiment: "Sample motor is moving too slowly"
$ bait-query 8id-bits "Why is the sample motor moving slowly?"

Motor Performance Analysis:
🔍 Sample X Motor (8idimot1:m1):
   - Current velocity: 0.5 mm/s (normal: 2.0 mm/s)
   - Controller status: OK
   - Power supply: 23.8V (normal: 24V)
   
🔍 Potential causes:
   1. Low power supply voltage (most likely)
   2. Increased mechanical load
   3. Controller parameter drift
   
🛠️  Recommended actions:
   1. Check power supply connections
   2. Verify mechanical clearance
   3. Review controller parameters in MEDM screen: motor_control_expert.adl
```

## Controls Engineer Workflows

### System Maintenance Planning

**Mike Rodriguez, Controls Engineer**

```bash
# Planning IOC updates
$ bait-analyze 8id-bits --impact-analysis motor_ioc

Impact Analysis: motor_ioc Update
════════════════════════════════

📊 Affected Components:
• 8 Bluesky devices dependent on motor_ioc
• 4 MEDM screens with motor controls
• 2 scan plans using motor positioning
• 1 alignment procedure affected

🔗 Dependency Chain:
motor_ioc → sample_x_motor → grid_scan_plan → experiment_queue

📋 Update Procedure:
1. Stop queue server
2. Park all motors at safe positions
3. Update motor_ioc
4. Restart and verify positions
5. Resume queue server

⏱️  Estimated downtime: 15 minutes
```

### Configuration Validation

```bash
# After making changes
$ bait-analyze 8id-bits --validate-configuration

Configuration Validation Results:
═══════════════════════════════

✅ IOC Configuration:
   - 12 IOCs found and validated
   - All startup scripts syntactically correct
   - Database files properly linked

✅ Bluesky Configuration:
   - 45 devices properly configured
   - All device prefixes match IOC PVs
   - No circular dependencies detected

⚠️  MEDM Configuration:
   - 23 screens validated
   - 2 screens have broken PV connections:
     • detector_expert.adl: PV 'DET1:CAM:Status' not found
     • motor_diagnostics.adl: PV 'MOT1:Status' deprecated

🔧 Recommended fixes:
   - Update detector_expert.adl PV reference
   - Replace deprecated MOT1:Status with MOT1:State
```

## Operator Workflows

### Shift Change Briefing

**Jennifer Kim, Beamline Operator**

```bash
# Start of shift
$ bait-query 8id-bits "What should I monitor during my shift?"

Shift Monitoring Checklist:
═════════════════════════

🎯 Critical Systems:
• Detector cooling: Monitor temperature < 50°C
• Beam position: Check every 2 hours
• Sample environment: Verify temperature stability

⚠️  Current Warnings:
• Motor controller running warm (68°C)
• Detector IOC restarted 3 times today
• Network latency elevated on subnet

📊 Ongoing Experiments:
• User group: Johnson Lab (Stanford)
• Experiment: In-situ crystallization study
• Status: 65% complete, 8 hours remaining
• Next milestone: Temperature ramp at 14:00

🔔 Alerts to watch for:
• Beam dump (auto-recovery enabled)
• Detector temperature alarm
• Sample temperature deviation > 2°C
```

### Emergency Response

```bash
# Emergency: "Detector not responding"
$ bait-query 8id-bits "The detector is not responding, what should I do?"

Emergency Response: Detector Not Responding
══════════════════════════════════════════

🚨 Immediate Actions:
1. Check detector IOC status: ssh 8id-ioc2, check process
2. Verify detector power supply: Green LED should be on
3. Check network connectivity: ping detector IP
4. Review detector cooling: Temperature should be < 50°C

🔍 Diagnostic Steps:
1. Check IOC logs: tail -f /var/log/detector_ioc.log
2. Verify EPICS connections: caget DET1:CAM:Status
3. Check MEDM screen: detector_main.adl
4. Test detector communication: detector self-test

📞 Escalation:
• If detector hardware issue: Call detector specialist (x1234)
• If IOC software issue: Call controls engineer (x5678)
• If network issue: Call IT support (x9999)

⏱️  Expected resolution time: 5-15 minutes
```

## Quality Assurance Workflows

### Pre-Experiment Validation

**Dr. Lisa Wang, Quality Assurance**

```bash
# Before starting new experiment
$ bait-report 8id-bits --format pre-experiment-check

Pre-Experiment Validation Report
════════════════════════════════

📋 System Readiness:
✅ All IOCs operational
✅ Detector calibration current (updated yesterday)
✅ Beam alignment verified
✅ Sample environment stable

🔍 Recent Changes:
• Motor IOC updated 2 days ago - validated
• New scan plan added - tested
• MEDM screen modified - validated

📊 Performance Metrics:
• Average scan time: 2.3 minutes (within tolerance)
• Detector efficiency: 97.2% (excellent)
• Data quality score: 9.1/10 (excellent)

🎯 Recommendations:
✅ System ready for experiment
• Consider beam optimization for better flux
• Monitor detector temperature during long scans
```

### Post-Experiment Analysis

```bash
# After experiment completion
$ bait-query 8id-bits "Analyze the performance of today's experiment"

Experiment Performance Analysis:
═══════════════════════════════

📊 Experiment Summary:
• Duration: 8.5 hours
• Scans completed: 127/130 (97.7% success rate)
• Data quality: Excellent (9.2/10)
• No significant issues detected

🔍 System Performance:
• Detector uptime: 99.8%
• Motor positioning accuracy: ±0.5 μm
• Temperature stability: ±0.2°C
• Network latency: Normal ranges

⚠️  Minor Issues:
• 3 scans failed due to beam trips (normal)
• Motor controller temperature peaked at 71°C
• Brief network timeout at 16:23 (recovered)

📈 Recommendations for future:
• Install additional cooling for motor controller
• Consider beam stability improvements
• Monitor network during peak hours
```

## System Administrator Workflows

### Weekly System Health Check

**Bob Thompson, System Administrator**

```bash
# Weekly comprehensive analysis
$ bait-analyze 8id-bits --comprehensive --weekly-report

Weekly System Health Report
═══════════════════════════

📊 Overall System Health: 94/100 (Excellent)

🖥️  Hardware Status:
• CPU utilization: 23% average (normal)
• Memory usage: 67% average (normal)
• Disk space: 78% used (monitor)
• Network performance: 95% efficiency

🔧 Software Status:
• IOC uptime: 99.2% average
• Bluesky availability: 99.8%
• MEDM responsiveness: Good
• Database integrity: Verified

📈 Performance Trends:
• Scan completion rate: Stable at 98%
• Error rate: Decreased 15% from last week
• Response time: Improved 8% from last week

⚠️  Action Items:
• Plan disk cleanup (>75% usage)
• Update detector IOC firmware
• Review network configuration
• Schedule motor controller maintenance
```

### Security and Compliance

```bash
# Monthly security review
$ bait-analyze 8id-bits --security-audit

Security Audit Results:
═════════════════════

🔒 Access Control:
✅ All user accounts reviewed
✅ SSH keys rotated on schedule
✅ Network segmentation proper
⚠️  2 IOCs have default passwords

🔍 Vulnerability Assessment:
✅ No critical vulnerabilities found
✅ All systems patched current
⚠️  1 medium-risk issue in detector software

📊 Compliance Status:
✅ APS security policy: Compliant
✅ Data protection: Compliant
✅ Audit logging: Enabled
⚠️  Password policy: 2 exceptions

🛠️  Recommended Actions:
• Update IOC passwords immediately
• Patch detector software next maintenance window
• Review password policy exceptions
• Update firewall rules for new equipment
```

## User Support Workflows

### Training New Users

**Maria Santos, User Support Specialist**

```bash
# Creating training materials for new users
$ bait-visualize 8id-bits --type training-overview --interactive

Generating Interactive Training Overview...
✅ System architecture diagram created
✅ Component relationship map generated
✅ Control flow visualization ready
✅ Emergency procedures guide prepared

Training Materials Created:
• 8id-overview.html - Interactive system tour
• controls-guide.pdf - Basic controls overview
• safety-procedures.pdf - Emergency procedures
• troubleshooting-guide.html - Common issues

Recommended Training Sequence:
1. System overview (30 minutes)
2. Basic controls (45 minutes)
3. Safety procedures (20 minutes)
4. Hands-on practice (60 minutes)
```

### User Issue Resolution

```bash
# User reports: "I can't get the detector to trigger"
$ bait-query 8id-bits "Help a user who can't get the detector to trigger"

User Support: Detector Triggering Issues
════════════════════════════════════════

🎯 Common Causes & Solutions:

1. **Trigger Mode Configuration**
   • Check: Detector set to external trigger mode
   • Solution: Use detector_main.adl → Mode → External

2. **Trigger Signal Issues**
   • Check: Trigger cable connected properly
   • Solution: Verify cable from trigger IOC to detector

3. **Timing Configuration**
   • Check: Trigger pulse width (should be >1ms)
   • Solution: Adjust in trigger_control.adl

4. **Software Configuration**
   • Check: Bluesky detector configuration
   • Solution: Verify trigger_mode in startup.py

🔧 Step-by-Step Troubleshooting:
1. Open detector_main.adl
2. Check Status → Should show "Ready"
3. Verify Mode → Should show "External"
4. Test trigger manually → Press "Test Trigger"
5. Check timing → Verify pulse width >1ms

📞 If issue persists:
• Call detector specialist (x1234)
• Check recent system changes
• Review detector logs
```

## Performance Monitoring

### Real-time System Monitoring

```bash
# Continuous monitoring during critical experiments
$ bait-query 8id-bits "Monitor system performance in real-time"

Real-time Performance Monitor:
═══════════════════════════

🔄 Live Status (Updated every 30 seconds):
• Detector status: ✅ Online, temp: 45°C
• Motor positions: ✅ All within limits
• Beam current: ✅ 102 mA (stable)
• Sample temp: ✅ 295.2K (±0.1K)

📊 Performance Metrics:
• Scan rate: 2.1 scans/min (target: 2.0)
• Success rate: 98.3% (last 100 scans)
• Average scan time: 28.5 sec
• Data throughput: 1.2 MB/s

⚠️  Alerts:
• No current alerts
• Next maintenance: Motor controller (in 3 days)
• Detector recalibration: Due in 2 weeks

🔔 Monitoring Schedule:
• Critical parameters: Every 30 seconds
• Performance metrics: Every 5 minutes
• Full system check: Every hour
• Weekly trend analysis: Sundays at 06:00
```

## Integration with Experimental Workflows

### Automated Experiment Validation

```bash
# Before starting automated experiment sequence
$ bait-analyze 8id-bits --experiment-validation temperature_series

Experiment Validation: Temperature Series
════════════════════════════════════════

📋 Experiment Parameters:
• Type: Temperature-dependent measurement
• Temperature range: 77K - 400K
• Number of steps: 25
• Estimated duration: 6 hours

🔍 System Readiness Check:
✅ Sample environment: Ready for temperature range
✅ Detector: Calibrated and ready
✅ Motors: Positioned and ready
✅ Data collection: Disk space sufficient (89 GB free)

⚠️  Potential Issues:
• Temperature controller: Last calibration 6 months ago
• Detector: May require recalibration above 350K
• Cryostat: Service due in 2 weeks

🎯 Recommendations:
✅ Proceed with experiment
• Monitor temperature stability carefully
• Check detector calibration at T>350K
• Schedule cryostat service after experiment

📊 Expected Results:
• Data quality: Excellent (based on similar experiments)
• Completion probability: 95%
• Recommended monitoring: Every 30 minutes
```

This comprehensive set of workflows shows how bAIt integrates seamlessly into daily beamline operations, providing intelligence and insights that enhance efficiency, safety, and experimental success.