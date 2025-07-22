# Troubleshooting Scenarios with bAIt

This document provides real-world troubleshooting scenarios showing how bAIt helps diagnose and resolve common beamline issues.

## Scenario 1: Detector Not Responding

### Initial Problem Report
**User**: "The detector screen is black, and I can't collect any data."

### bAIt Diagnostic Process

#### Step 1: Initial Assessment
```bash
$ bait-query 8id-bits "The detector is not responding, help me diagnose the issue"

Detector Diagnostic Analysis:
═══════════════════════════

🔍 Detector Status Check:
• Detector IOC (detector_ioc_1): ❌ Not responding
• Last communication: 23 minutes ago
• IOC process status: ❌ Not running
• Power supply status: ✅ Normal (24V)

🔗 System Dependencies:
• MEDM screens affected: 3 (detector_main.adl, detector_expert.adl, detector_config.adl)
• Bluesky devices affected: 2 (lambda_detector, pilatus_detector)
• Current experiments: 1 scan paused, 3 scans queued

🚨 Immediate Actions Required:
1. Restart detector IOC on host 8id-ioc2
2. Verify detector hardware connections
3. Check network connectivity
4. Resume paused experiments once resolved
```

#### Step 2: Detailed Analysis
```bash
$ bait-analyze 8id-bits --focus detector --verbose

Detailed Detector Analysis:
═════════════════════════

🖥️  IOC Host Status (8id-ioc2):
• Host responsive: ✅ Yes
• CPU usage: 15% (normal)
• Memory: 2.3GB used / 8GB total
• Disk space: 78% used (normal)

🔌 Hardware Connections:
• Detector power: ✅ 24V stable
• Network cable: ✅ Link detected
• Cooling system: ✅ 42°C (normal)
• Trigger cable: ⚠️ May be loose

📝 Error Log Analysis:
• Last error: "Communication timeout at 14:23:45"
• Frequency: 3 timeouts in last hour
• Pattern: Intermittent connection issues

🔧 Root Cause Analysis:
Most likely cause: Loose network connection
Secondary cause: IOC software hang
Evidence: Intermittent timeouts, hardware OK
```

#### Step 3: Resolution Steps
```bash
$ bait-query 8id-bits "Provide step-by-step resolution for detector communication timeout"

Resolution Steps: Detector Communication Timeout
══════════════════════════════════════════════

🔧 Immediate Actions:
1. Check network cable at detector:
   • Visually inspect for damage
   • Ensure secure connection
   • Check LED indicators (should be green)

2. Restart detector IOC:
   • SSH to 8id-ioc2: ssh controls@8id-ioc2
   • Check process: ps aux | grep detector
   • Kill if running: pkill detector_ioc
   • Restart: /home/controls/iocs/detector_ioc/st.cmd

3. Verify communication:
   • Test PV connection: caget DET1:CAM:Status
   • Check MEDM screen: detector_main.adl
   • Verify detector response: detector self-test

⏱️  Expected Resolution Time: 5-10 minutes

🔄 Verification Steps:
• IOC status: Should show "Running"
• PV values: Should update normally
• MEDM screen: Should show live data
• Test acquisition: Take test image

📊 Success Criteria:
• All detector PVs responding
• MEDM screens updating
• Test image acquired successfully
• No timeout errors in logs
```

### Resolution Outcome
```bash
$ bait-query 8id-bits "Verify detector issue resolution"

Resolution Verification:
═════════════════════

✅ Issue Resolved Successfully:
• Detector IOC restarted and running
• Network connection stabilized
• All PVs responding normally
• MEDM screens operational

📊 Post-Resolution Status:
• Detector temperature: 42°C (normal)
• Communication latency: 15ms (excellent)
• Error rate: 0% (last 30 minutes)
• Experiments resumed: 4 scans completed

🔧 Actions Taken:
• Tightened network cable connection
• Restarted detector IOC
• Verified all dependent systems
• Updated maintenance log

📈 Prevention Measures:
• Schedule cable inspection monthly
• Add network monitoring alerts
• Update IOC watchdog settings
• Train operators on quick diagnostics
```

## Scenario 2: Motor Moving Slowly

### Initial Problem Report
**User**: "The sample positioning is taking forever. The motor is moving much slower than usual."

### bAIt Diagnostic Process

#### Step 1: Motor Performance Analysis
```bash
$ bait-query 8id-bits "The sample motor is moving slowly, analyze performance"

Motor Performance Analysis:
═════════════════════════

🔍 Sample X Motor (8idimot1:m1):
• Current velocity: 0.3 mm/s
• Configured velocity: 2.0 mm/s
• Actual performance: 15% of expected
• Motor controller: ESP301 #1

⚡ Power and Control:
• Supply voltage: 22.1V (normal: 24V)
• Current draw: 0.8A (normal: 0.6A)
• Temperature: 71°C (normal: <60°C)
• Controller status: Active warnings

🔧 Potential Issues Identified:
1. Low power supply voltage (9% below normal)
2. High operating temperature (18% above normal)
3. Increased current draw (33% above normal)
4. Controller reporting internal warnings

🚨 Immediate Concerns:
• Risk of motor damage if overheating continues
• Experiment timeline will be significantly delayed
• Other motors may be affected by power supply issue
```

#### Step 2: Root Cause Investigation
```bash
$ bait-analyze 8id-bits --focus motor_system --root-cause-analysis

Root Cause Analysis: Motor Performance
════════════════════════════════════

🔍 Power Supply Analysis:
• Main supply: 22.1V (should be 24V ±0.5V)
• Supply current: 4.2A (normal: 3.5A)
• Ripple: 0.3V (normal: <0.1V)
• Temperature: 68°C (normal: <50°C)

🔗 Dependency Chain:
Power Supply → Motor Controller → Motor → Positioning System

🔧 Fault Tree Analysis:
Primary Cause: Power supply degradation
├── Aging capacitors (likely)
├── Ventilation blockage (check)
├── Overload condition (check)
└── Component failure (possible)

📊 Historical Data:
• Voltage trend: Declining over past 2 weeks
• Temperature trend: Rising over past month
• Performance degradation: 15% over past week

🎯 Recommended Actions:
1. IMMEDIATE: Reduce motor speeds to prevent damage
2. SHORT-TERM: Replace power supply
3. LONG-TERM: Implement power monitoring
4. PREVENTIVE: Schedule regular power supply maintenance
```

#### Step 3: Mitigation Strategy
```bash
$ bait-query 8id-bits "Provide immediate mitigation for motor power supply issues"

Mitigation Strategy: Motor Power Supply Issues
════════════════════════════════════════════

🚨 Immediate Actions (Next 30 minutes):
1. Reduce motor velocities to 50% of normal:
   • Access motor_control_expert.adl
   • Update velocity settings for all motors
   • Test with short moves first

2. Improve ventilation:
   • Check power supply air filters
   • Ensure cooling fans operating
   • Clear any obstructions

3. Monitor temperatures:
   • Set up continuous monitoring
   • Alert threshold: 75°C
   • Automatic shutdown at 80°C

⏱️  Short-term Actions (Next 24 hours):
1. Order replacement power supply:
   • Model: Acopian 24V/5A regulated
   • Delivery: Next day if ordered by 2 PM
   • Cost: ~$200

2. Prepare for replacement:
   • Schedule maintenance window
   • Notify users of brief downtime
   • Prepare backup procedures

📊 Experiment Impact:
• Current scans: 2.5x longer than normal
• Recommended: Pause complex positioning
• Alternative: Use manual positioning for critical samples
• Timeline: Full resolution in 24-48 hours
```

### Resolution and Follow-up
```bash
$ bait-report 8id-bits --incident-report motor_power_supply --resolution-summary

Incident Report: Motor Power Supply Issue
═══════════════════════════════════════

📋 Incident Summary:
• Date: 2024-01-15
• Issue: Motor performance degradation due to power supply failure
• Impact: 85% reduction in positioning speed
• Resolution time: 18 hours
• Experiments affected: 3 (temporarily paused)

🔧 Actions Taken:
• Immediate: Reduced motor speeds to prevent damage
• Short-term: Replaced power supply unit
• Long-term: Installed power monitoring system
• Preventive: Updated maintenance schedule

📊 Results:
• Motor performance: Restored to 100%
• Power supply voltage: Stable at 24.0V ±0.1V
• Temperature: Reduced to 45°C
• No equipment damage occurred

💡 Lessons Learned:
• Early warning system needed for power supplies
• Regular voltage monitoring prevents failures
• Spare power supplies should be kept on-site
• Staff training on power supply diagnostics improved
```

## Scenario 3: Scan Plan Execution Failures

### Initial Problem Report
**User**: "My scan keeps failing after the first few points. The queue server shows errors."

### bAIt Diagnostic Process

#### Step 1: Scan Analysis
```bash
$ bait-query 8id-bits "My scan plan keeps failing, help me debug this"

Scan Plan Debug Analysis:
═══════════════════════

🔍 Recent Scan Failures:
• Failed scans: 7 out of last 10 attempts
• Failure pattern: Typically fails at point 3-5
• Error type: Device timeout
• Affected plan: grid_scan_temperature

📊 Error Pattern Analysis:
• Failure point: During detector readout
• Timeout: 30 seconds (default)
• Success rate: 30% (normally 98%+)
• Failure timing: Random, not systematic

🔗 Involved Components:
• Primary: Lambda detector (detector_ioc_1)
• Secondary: Sample temperature controller (temp_ioc)
• Tertiary: Sample positioning motors (motor_ioc)

🚨 Potential Issues:
1. Detector readout timeout (most likely)
2. Temperature controller instability
3. Network communication issues
4. Insufficient wait times in plan
```

#### Step 2: Component Analysis
```bash
$ bait-analyze 8id-bits --focus scan_execution --error-analysis

Scan Execution Error Analysis:
════════════════════════════

🔍 Detector Performance:
• Readout time: 8.5 seconds (normal: 3.2 seconds)
• Timeout setting: 30 seconds
• Success rate: 65% (should be >95%)
• Error type: "Acquisition timeout"

🌡️  Temperature Controller:
• Stability: ±0.5°C (normal: ±0.1°C)
• Response time: 45 seconds (normal: 15 seconds)
• Overshoot: 2.3°C (normal: <0.5°C)
• PID tuning: Appears suboptimal

🔧 Scan Plan Analysis:
• Wait time after temp change: 30 seconds
• Required stabilization time: 60 seconds (estimated)
• Detector exposure: 5 seconds
• Total point time: 43.5 seconds (should be ~25 seconds)

💡 Root Cause Identified:
Temperature controller instability causing:
1. Longer stabilization times needed
2. Detector performance degradation at unstable temperatures
3. Scan plan timing assumptions invalid
```

#### Step 3: Solution Implementation
```bash
$ bait-query 8id-bits "Provide solution for scan plan failures due to temperature instability"

Solution: Scan Plan Temperature Issues
════════════════════════════════════

🔧 Immediate Fixes:
1. Adjust scan plan timing:
   • Increase wait time: 30s → 90s
   • Add temperature stability check
   • Implement adaptive waiting

2. Optimize temperature controller:
   • Retune PID parameters
   • Reduce overshoot settings
   • Implement gradual temperature changes

3. Modify detector settings:
   • Increase timeout: 30s → 60s
   • Pre-warm detector before scan
   • Add temperature compensation

📝 Updated Scan Plan:
```python
# Original problematic plan
def grid_scan_temperature(temps):
    for temp in temps:
        yield from bps.mv(temp_controller, temp)
        yield from bps.sleep(30)  # Too short!
        yield from bp.count([detector], num=1)

# Improved plan
def grid_scan_temperature_stable(temps):
    for temp in temps:
        yield from bps.mv(temp_controller, temp)
        yield from bps.sleep(60)  # Longer wait
        # Wait for stability
        yield from wait_for_temperature_stability(temp, tolerance=0.1)
        yield from bp.count([detector], num=1)
```

🎯 Expected Results:
• Scan success rate: >95%
• Point completion time: 85 seconds
• Temperature stability: ±0.1°C
• Detector timeouts: Eliminated
```

### Verification and Optimization
```bash
$ bait-query 8id-bits "Verify scan plan fixes and suggest optimizations"

Scan Plan Verification Results:
═════════════════════════════

✅ Test Results:
• Test scans completed: 15/15 (100% success)
• Average point time: 78 seconds (improved from 43.5s)
• Temperature stability: ±0.08°C (excellent)
• Detector timeouts: 0 (eliminated)

📊 Performance Metrics:
• Scan completion rate: 100%
• Data quality: Excellent (no temperature artifacts)
• Total scan time: 32 minutes (vs. 18 minutes original)
• Reliability: Significantly improved

🚀 Further Optimizations:
1. Implement predictive temperature control:
   • Pre-calculate temperature trajectory
   • Start temperature changes earlier
   • Reduce total wait times

2. Add intelligent waiting:
   • Monitor temperature derivative
   • Adaptive wait times based on stability
   • Parallel detector preparation

3. Optimize PID parameters:
   • Run auto-tuning procedure
   • Optimize for scan application
   • Reduce overshoot to <0.2°C

💡 Expected Improvements:
• Scan time reduction: 15-20%
• Further reliability improvement
• Better data quality consistency
• Reduced operator intervention
```

## Scenario 4: Network Connectivity Issues

### Initial Problem Report
**User**: "MEDM screens are updating very slowly, and some PVs show disconnected."

### bAIt Diagnostic Process

#### Step 1: Network Analysis
```bash
$ bait-query 8id-bits "MEDM screens are slow and PVs are disconnected"

Network Connectivity Analysis:
════════════════════════════

🌐 Network Status:
• Subnet: 164.54.xxx.xxx/24
• Active hosts: 15/18 (3 not responding)
• Average latency: 45ms (normal: <5ms)
• Packet loss: 3.2% (normal: <0.1%)

🔗 EPICS Network Status:
• CA Gateway: ⚠️ Intermittent timeouts
• PV Access: ⚠️ High latency
• Channel connections: 234/267 (87% connected)
• Disconnected PVs: 33 (mostly on IOC host 8id-ioc2)

📊 Problem Areas:
• IOC host 8id-ioc2: High latency (95ms)
• Switch connection: Intermittent errors
• Network utilization: 78% (high)
• DNS resolution: Slow (2.3s average)

🚨 Impact Assessment:
• MEDM screen updates: 5-10 second delays
• Bluesky device communication: Intermittent failures
• Data collection: 15% slower than normal
• User experience: Significantly degraded
```

#### Step 2: Infrastructure Investigation
```bash
$ bait-analyze 8id-bits --network-diagnostics --infrastructure-check

Network Infrastructure Analysis:
══════════════════════════════

🔍 Physical Layer:
• Switch status: 2 ports showing errors
• Cable integrity: 1 cable with high error rate
• Port utilization: 3 ports >90% usage
• Power supply: All switches normal

📈 Traffic Analysis:
• Broadcast storms: None detected
• Bandwidth usage: 78% on main trunk
• Protocol distribution: 45% EPICS, 30% SSH, 25% other
• Error rate: 0.3% (elevated)

🖥️  Host Performance:
• 8id-ioc2: CPU 85%, Memory 92% (overloaded)
• 8id-ws1: Normal performance
• 8id-gateway: Normal performance
• Network stack: TCP retransmissions elevated

🔧 Root Cause Analysis:
Primary: IOC host 8id-ioc2 overloaded
Secondary: Network cable degradation
Tertiary: High network utilization

⚡ Immediate Actions Needed:
1. Reduce load on 8id-ioc2
2. Replace degraded network cable
3. Implement traffic prioritization
4. Add network monitoring
```

#### Step 3: Resolution Strategy
```bash
$ bait-query 8id-bits "Provide network issue resolution strategy"

Network Issue Resolution Strategy:
════════════════════════════════

🚨 Immediate Actions (Next 2 hours):
1. Redistribute IOC load:
   • Move 2 IOCs from 8id-ioc2 to 8id-ioc3
   • Restart overloaded IOCs
   • Verify PV connections restored

2. Replace network cable:
   • Identify degraded cable (port 12)
   • Replace with Cat6 cable
   • Test connection integrity

3. Network optimization:
   • Implement EPICS traffic prioritization
   • Reduce broadcast frequency
   • Optimize CA Gateway settings

📊 Expected Results:
• Latency reduction: 45ms → <10ms
• PV connection rate: 87% → >98%
• MEDM responsiveness: Normal
• Network utilization: 78% → <60%

🔧 Long-term Improvements:
1. Add network monitoring:
   • Real-time latency monitoring
   • Automated alerts for high usage
   • Traffic analysis dashboard

2. Infrastructure upgrades:
   • Dedicated EPICS network segment
   • Redundant switch configuration
   • Improved cable management

3. Load balancing:
   • Distribute IOCs across multiple hosts
   • Implement failover mechanisms
   • Regular load assessment

⏱️  Timeline:
• Immediate fixes: 2 hours
• Full resolution: 24 hours
• Long-term improvements: 2 weeks
```

### Resolution Verification
```bash
$ bait-report 8id-bits --network-resolution-report

Network Resolution Report:
════════════════════════

✅ Resolution Summary:
• Issue: Network connectivity and performance problems
• Duration: 6 hours (detection to full resolution)
• Impact: Temporary degradation of MEDM and PV access
• Resolution: Successful, all systems normal

📊 Post-Resolution Metrics:
• Network latency: 3.2ms (excellent)
• PV connection rate: 99.2% (excellent)
• MEDM responsiveness: Normal
• Network utilization: 52% (normal)

🔧 Actions Completed:
• Redistributed IOC load across hosts
• Replaced degraded network cable
• Implemented EPICS traffic prioritization
• Added network monitoring system

📈 Improvements Achieved:
• 92% reduction in network latency
• 14% improvement in PV connection rate
• 100% improvement in MEDM responsiveness
• 33% reduction in network utilization

💡 Preventive Measures:
• Monthly network health checks
• Automated monitoring alerts
• Regular cable inspection
• Load balancing review quarterly
```

## Common Troubleshooting Patterns

### Pattern 1: Intermittent Issues
```bash
$ bait-query 8id-bits "Help me troubleshoot intermittent system issues"

Intermittent Issue Troubleshooting:
═════════════════════════════════

🔍 Diagnostic Approach:
1. Pattern Recognition:
   • Time-based patterns (hourly, daily, weekly)
   • Load-based patterns (high usage periods)
   • Environment-based patterns (temperature, humidity)

2. Data Collection:
   • Enable detailed logging
   • Monitor system metrics
   • Track error frequencies

3. Correlation Analysis:
   • Match errors with system events
   • Identify common factors
   • Establish cause-effect relationships

🔧 Common Causes:
• Thermal cycling effects
• Network congestion periods
• Memory leaks in long-running processes
• Timing-sensitive race conditions
• Environmental factors
```

### Pattern 2: Performance Degradation
```bash
$ bait-query 8id-bits "System performance is gradually getting worse"

Performance Degradation Analysis:
═══════════════════════════════

📊 Trending Analysis:
• CPU usage: Monitor for increasing baseline
• Memory usage: Check for memory leaks
• Network performance: Track latency trends
• Disk I/O: Monitor for fragmentation

🔍 Root Cause Categories:
1. Resource exhaustion (most common)
2. Software aging effects
3. Hardware degradation
4. Configuration drift
5. Environmental changes

🛠️  Diagnostic Tools:
• Historical performance data
• Resource utilization trends
• Error rate analysis
• Comparative benchmarking
```

This comprehensive troubleshooting guide demonstrates how bAIt provides systematic, intelligent assistance for resolving complex beamline issues efficiently and effectively.