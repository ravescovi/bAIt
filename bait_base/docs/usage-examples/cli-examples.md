# bAIt CLI Examples and Outputs

This document provides comprehensive examples of bAIt command-line interface usage with realistic outputs.

## Basic Commands

### System Status Check

```bash
$ bait-query 8id-bits "What is the current system status?"
```

**Output:**
```
bAIt System Status for 8-ID Beamline
═══════════════════════════════════

📊 Overall Health: 96/100 (Excellent)
🕒 Last Analysis: 2024-01-15 09:23:45 (18 minutes ago)

🔧 IOC Status:
   ✅ motor_ioc: Running (uptime: 3d 14h)
   ✅ detector_ioc_1: Running (uptime: 1d 8h)
   ✅ detector_ioc_2: Running (uptime: 1d 8h)
   ✅ scaler_ioc: Running (uptime: 5d 2h)
   ✅ temperature_ioc: Running (uptime: 2d 16h)
   ⚠️  beamline_ioc: Restarted 2h ago (monitoring)

🔍 Bluesky Environment:
   ✅ Queue Server: Active (3 plans pending)
   ✅ RunEngine: Ready
   ✅ Devices: 45/45 connected
   ✅ Catalog: Accessible

🖥️  MEDM Screens:
   ✅ Main screens: 8/8 operational
   ✅ Expert screens: 15/15 operational
   ⚠️  motor_expert.adl: 1 broken PV connection

⚠️  Current Warnings:
   • Motor controller temperature: 68°C (normal < 65°C)
   • Network latency elevated: 25ms (normal < 10ms)
   • Detector recalibration due in 5 days

🎯 Recommendations:
   • Monitor motor controller cooling
   • Check network performance during next maintenance
   • Schedule detector recalibration
```

### Deployment Analysis

```bash
$ bait-analyze 8id-bits --comprehensive
```

**Output:**
```
bAIt Comprehensive Analysis: 8-ID Beamline
═════════════════════════════════════════

🔍 Starting comprehensive analysis...
📊 Analysis Progress: [████████████████████████████████] 100%

━━━ IOC Analysis ━━━
✅ IOC Discovery: 12 IOCs found
✅ Configuration Validation: All IOCs properly configured
✅ Dependency Mapping: 47 dependencies identified
✅ PV Inventory: 234 PVs catalogued
⚠️  Issues: 2 warnings found

━━━ Bluesky Analysis ━━━
✅ Device Discovery: 45 devices found
✅ Device Validation: All devices properly mapped
✅ Plan Analysis: 23 plans available
✅ Callback Configuration: 8 callbacks configured
✅ Issues: None found

━━━ MEDM Analysis ━━━
✅ Screen Discovery: 23 screens found
✅ PV Connection Validation: 98.5% connections valid
✅ Navigation Structure: Properly organized
⚠️  Issues: 1 broken connection, 2 deprecated PVs

━━━ Network Analysis ━━━
✅ Host Discovery: 8 hosts found
✅ Service Validation: All services accessible
✅ Connectivity: Full mesh connectivity
⚠️  Issues: Elevated latency on subnet

━━━ Integrity Analysis ━━━
✅ Configuration Consistency: 95% consistent
✅ Cross-Component Validation: Passed
✅ Dependency Resolution: All dependencies resolved
⚠️  Issues: 3 minor inconsistencies

━━━ Performance Analysis ━━━
✅ Response Times: Within acceptable limits
✅ Resource Utilization: Normal levels
✅ Error Rates: <0.1% (excellent)
⚠️  Issues: Motor controller running warm

━━━ Summary ━━━
📊 Overall Score: 96/100 (Excellent)
✅ Critical Issues: 0
⚠️  Warnings: 8
📈 Recommendations: 12

🎯 Top Recommendations:
   1. Update motor_expert.adl PV references
   2. Replace deprecated PVs in temperature screens
   3. Investigate network latency during maintenance
   4. Install additional cooling for motor controller
   5. Schedule detector recalibration next week

📁 Detailed reports generated:
   • /reports/8id-bits-analysis-20240115.html
   • /reports/8id-bits-issues-20240115.json
   • /reports/8id-bits-recommendations-20240115.pdf

⏱️  Analysis completed in 2m 34s
```

### Troubleshooting Query

```bash
$ bait-query 8id-bits "The detector scan is taking too long, help me troubleshoot"
```

**Output:**
```
bAIt Troubleshooting Assistant
════════════════════════════

🔍 Issue: Detector scan performance degradation
🎯 Analysis: Investigating slow detector scans...

━━━ Detector Performance Analysis ━━━
🔍 Lambda Detector (DET1):
   • Current readout time: 8.2 seconds
   • Normal readout time: 2.8 seconds
   • Performance degradation: 193% slower
   • Temperature: 47°C (normal: 45°C)

🔍 Pilatus Detector (DET2):
   • Current readout time: 3.1 seconds
   • Normal readout time: 1.2 seconds
   • Performance degradation: 158% slower
   • Temperature: 52°C (normal: 48°C)

━━━ Root Cause Analysis ━━━
🎯 Primary Issue: Detector overheating
   Evidence:
   • Both detectors running 2-5°C above normal
   • Cooling system airflow reduced by 30%
   • Ambient temperature elevated (28°C vs 24°C)

🎯 Secondary Issue: Network congestion
   Evidence:
   • Network latency: 25ms (normal: 8ms)
   • Packet loss: 0.3% (normal: 0.01%)
   • Data transfer rate: 15% slower

━━━ Immediate Actions ━━━
🚨 Priority 1: Detector cooling
   1. Check cooling system air filters
   2. Verify cooling fans are operational
   3. Ensure proper airflow around detectors
   4. Consider temporary cooling assistance

🚨 Priority 2: Network optimization
   1. Check network switch status
   2. Verify cable connections
   3. Restart network services if needed
   4. Monitor network traffic patterns

━━━ Step-by-Step Resolution ━━━
1. 🔧 Check Cooling System (5 minutes):
   • Inspect air filters for blockage
   • Verify fan operation (should be audible)
   • Check temperature sensors readings

2. 🌐 Network Diagnostics (10 minutes):
   • ping detector hosts: ping det1, ping det2
   • Check switch status: ssh switch, show interfaces
   • Monitor traffic: iftop -i eth0

3. 🔄 Restart Services (5 minutes):
   • Restart detector IOCs if needed
   • Clear network buffers
   • Reset detector connections

4. 📊 Verify Resolution (10 minutes):
   • Run test acquisition
   • Monitor temperatures
   • Check network latency

━━━ Expected Results ━━━
✅ Detector readout time: Back to normal (2.8s, 1.2s)
✅ Temperature reduction: 2-3°C decrease
✅ Network performance: <10ms latency
✅ Scan time improvement: 60-70% faster

🔔 Escalation: If issue persists after 30 minutes:
   • Contact detector specialist: x1234
   • Contact network administrator: x5678
   • Consider alternative detector configuration

📊 Success probability: 85% (based on similar incidents)
⏱️  Estimated resolution time: 30 minutes
```

## Advanced Commands

### Impact Analysis

```bash
$ bait-analyze 8id-bits --impact-analysis motor_ioc
```

**Output:**
```
bAIt Impact Analysis: motor_ioc Update
════════════════════════════════════

🔍 Analyzing impact of motor_ioc changes...
📊 Dependencies discovered: 47 direct, 23 indirect

━━━ Direct Dependencies ━━━
🔧 Bluesky Devices (8 affected):
   • sample_x_motor → Grid scans, alignment procedures
   • sample_y_motor → Grid scans, alignment procedures
   • sample_z_motor → Sample positioning, focusing
   • detector_x_motor → Detector positioning
   • detector_y_motor → Detector positioning
   • monochromator_bragg → Energy scans
   • monochromator_roll → Beam conditioning
   • mirror_pitch → Beam steering

🖥️  MEDM Screens (12 affected):
   • motor_main.adl → Main motor control interface
   • motor_expert.adl → Advanced motor diagnostics
   • sample_positioning.adl → Sample positioning controls
   • detector_positioning.adl → Detector positioning
   • alignment_screen.adl → Alignment procedures
   • energy_control.adl → Energy change procedures
   • beam_conditioning.adl → Beam optimization
   • maintenance_screen.adl → Maintenance procedures

📋 Bluesky Plans (15 affected):
   • grid_scan → Sample grid measurements
   • alignment_scan → Beam alignment procedures
   • energy_scan → Energy-dependent measurements
   • detector_scan → Detector positioning optimization
   • sample_series → Multi-sample measurements
   • focus_optimization → Beam focus procedures
   • calibration_scan → System calibration
   • maintenance_scan → Maintenance procedures

━━━ Indirect Dependencies ━━━
🔄 Queue Server Operations:
   • Current queue: 3 plans (2 motor-dependent)
   • Scheduled experiments: 4 (all motor-dependent)
   • User procedures: 12 (8 motor-dependent)

🔗 System Integrations:
   • Temperature control → Motor-dependent positioning
   • Data collection → Motor-dependent geometry
   • Safety systems → Motor position monitoring
   • Automation scripts → Motor position validation

━━━ Risk Assessment ━━━
🚨 HIGH RISK - Components requiring immediate attention:
   • Running experiments: 2 active scans using motors
   • Critical positioning: Sample and detector motors
   • Safety systems: Position limit monitoring

⚠️  MEDIUM RISK - Components with potential issues:
   • MEDM screen connections: May need reconnection
   • Bluesky device initialization: May need restart
   • Historical data: Position logging continuity

✅ LOW RISK - Components with minimal impact:
   • Network services: Independent of motor IOC
   • Other IOCs: No direct dependencies
   • Documentation: Static content unaffected

━━━ Recommended Update Procedure ━━━
1. 🛑 Pre-Update Actions (10 minutes):
   • Pause queue server
   • Complete current scans
   • Park all motors at safe positions
   • Notify users of maintenance window

2. 🔄 Update Process (15 minutes):
   • Stop motor IOC gracefully
   • Backup current configuration
   • Install updated motor IOC
   • Verify IOC startup and PV connections

3. 🔍 Validation Process (10 minutes):
   • Test motor communication
   • Verify position readbacks
   • Check MEDM screen connections
   • Validate Bluesky device initialization

4. 🚀 Post-Update Actions (5 minutes):
   • Resume queue server
   • Notify users of completion
   • Monitor for any issues
   • Update documentation

━━━ Downtime Estimate ━━━
🕒 Planned Downtime: 40 minutes
   • Critical systems: 25 minutes
   • Full system: 40 minutes
   • Buffer time: 20 minutes (recommended)

🕒 Best Case: 30 minutes
🕒 Worst Case: 90 minutes (if complications arise)

━━━ Rollback Plan ━━━
📋 If Issues Occur:
1. Stop new motor IOC
2. Restore previous IOC version
3. Verify system restoration
4. Investigate issues offline
5. Reschedule update with fixes

📊 Rollback Time: 10 minutes
✅ Rollback Success Rate: 99%

━━━ Success Metrics ━━━
✅ Update Successful If:
   • All 8 motor devices responsive
   • All 12 MEDM screens functional
   • All 15 plans executable
   • Position accuracy maintained
   • No system errors in 30 minutes

📊 Historical Success Rate: 94% (based on 17 previous updates)
🎯 Confidence Level: High
```

### Visualization Generation

```bash
$ bait-visualize 8id-bits --type network --format interactive
```

**Output:**
```
bAIt Network Visualization Generator
══════════════════════════════════

🔍 Generating network topology for 8-ID beamline...
📊 Processing network data...

━━━ Network Discovery ━━━
✅ Hosts discovered: 8
✅ IOCs mapped: 12
✅ Services identified: 15
✅ Connections traced: 47

━━━ Topology Analysis ━━━
🌐 Network Structure:
   • Core switch: 8id-sw-main (24 ports)
   • IOC switch: 8id-sw-ioc (16 ports)
   • Workstation switch: 8id-sw-ws (8 ports)
   • Wireless access point: 8id-ap-lab

🖥️  Host Categories:
   • Workstations: 3 (8id-ws1, 8id-ws2, 8id-ws3)
   • IOC hosts: 3 (8id-ioc1, 8id-ioc2, 8id-ioc3)
   • Servers: 2 (8id-srv-data, 8id-srv-backup)

🔧 IOC Distribution:
   • 8id-ioc1: 5 IOCs (motors, scalers, temperature)
   • 8id-ioc2: 4 IOCs (detectors, beam monitoring)
   • 8id-ioc3: 3 IOCs (safety, utilities, backup)

━━━ Connection Analysis ━━━
🔗 Critical Connections:
   • CA Gateway: 8id-ws1:5064 → All IOCs
   • Queue Server: 8id-ws1:60615 → Bluesky clients
   • Data Server: 8id-srv-data:8080 → All systems
   • Backup Server: 8id-srv-backup:22 → All systems

📊 Traffic Patterns:
   • EPICS CA: 45% of network traffic
   • Data transfer: 30% of network traffic
   • SSH/Management: 15% of network traffic
   • Other protocols: 10% of network traffic

━━━ Visualization Generated ━━━
📁 Files created:
   • 8id-network-topology.html (Interactive visualization)
   • 8id-network-topology.svg (Static diagram)
   • 8id-network-data.json (Raw network data)
   • 8id-network-report.pdf (Detailed report)

🎯 Visualization Features:
   ✅ Interactive node selection
   ✅ Zoom and pan capabilities
   ✅ Layer filtering (hosts, IOCs, services)
   ✅ Connection highlighting
   ✅ Real-time status indicators
   ✅ Detailed tooltips
   ✅ Export capabilities

━━━ Visualization Statistics ━━━
📊 Network Metrics:
   • Total nodes: 23
   • Total connections: 47
   • Network diameter: 4 hops
   • Average path length: 2.3 hops
   • Clustering coefficient: 0.67
   • Network density: 0.43

🔧 Performance Indicators:
   • Average latency: 8.2ms
   • Bandwidth utilization: 52%
   • Error rate: 0.01%
   • Availability: 99.8%

━━━ Access Information ━━━
🌐 Interactive Visualization:
   URL: file:///tmp/8id-network-topology.html
   Browser: Chrome, Firefox, Safari supported
   Mobile: Responsive design included

📱 Mobile Access:
   • Touch-enabled interface
   • Gesture navigation
   • Optimized layouts
   • Offline viewing capability

💾 Data Export Options:
   • PNG: High-resolution static image
   • PDF: Printer-friendly report
   • JSON: Machine-readable data
   • CSV: Spreadsheet-compatible format

✅ Visualization generation completed in 45 seconds
🎯 Ready for viewing and sharing
```

### Report Generation

```bash
$ bait-report 8id-bits --format comprehensive --period weekly
```

**Output:**
```
bAIt Comprehensive Weekly Report
══════════════════════════════

📊 Report Period: January 8-15, 2024 (Week 2)
🏷️  Deployment: 8-ID Dynamic Scattering Beamline
📅 Generated: January 15, 2024, 14:23:45

━━━ Executive Summary ━━━
🎯 Overall Performance: 94/100 (Excellent)
✅ Uptime: 99.2% (target: 99.0%)
✅ Experiments: 23 completed (22 successful, 1 partial)
✅ Issues Resolved: 12 (avg resolution time: 18 minutes)
⚠️  Outstanding Issues: 3 (all low priority)

━━━ System Health Metrics ━━━
🔧 IOC Performance:
   • Average uptime: 99.4%
   • Response time: 12ms (excellent)
   • Error rate: 0.02% (excellent)
   • Restart events: 2 (scheduled maintenance)

🔍 Bluesky Operations:
   • Scan completion rate: 98.7%
   • Average scan time: 2.3 minutes
   • Queue server uptime: 99.8%
   • Device connectivity: 99.9%

🖥️  MEDM Interface:
   • Screen responsiveness: 95% (good)
   • Connection stability: 98.5%
   • User reported issues: 1 (resolved)

━━━ Experimental Activity ━━━
📊 Experiment Statistics:
   • Total experiments: 23
   • Successful: 22 (95.7%)
   • Partial success: 1 (4.3%)
   • Failed: 0 (0.0%)
   • User groups: 4 different groups

🔬 Experiment Types:
   • SAXS measurements: 12 experiments
   • Temperature series: 6 experiments
   • Pressure studies: 3 experiments
   • Calibration runs: 2 experiments

⏱️  Time Utilization:
   • Total beam time: 156 hours
   • Experiment time: 142 hours (91.0%)
   • Maintenance time: 8 hours (5.1%)
   • Setup time: 6 hours (3.9%)

━━━ Performance Trends ━━━
📈 Improvements This Week:
   • Scan completion rate: +2.3% vs last week
   • Average scan time: -8% vs last week
   • Network latency: -15% vs last week
   • Error rate: -45% vs last week

📉 Areas of Concern:
   • Motor controller temperature: +5°C vs last week
   • Detector recalibration overdue: +3 days
   • Network utilization: +12% vs last week

━━━ Issue Summary ━━━
🔴 Resolved Issues (12):
   1. Detector timeout errors (resolved in 15 min)
   2. Network connectivity glitch (resolved in 5 min)
   3. Motor positioning drift (resolved in 30 min)
   4. MEDM screen refresh issues (resolved in 10 min)
   5. Temperature controller overshoot (resolved in 45 min)
   6. Queue server restart needed (resolved in 5 min)
   7. Beam position drift (resolved in 20 min)
   8. Detector dark current high (resolved in 25 min)
   9. Sample changer malfunction (resolved in 60 min)
   10. Data transfer delays (resolved in 15 min)
   11. Scaler reading errors (resolved in 10 min)
   12. Alignment procedure issue (resolved in 20 min)

🟡 Outstanding Issues (3):
   1. Motor controller cooling upgrade needed (low priority)
   2. Detector recalibration scheduled (low priority)
   3. Network optimization pending (low priority)

━━━ Maintenance Summary ━━━
🔧 Completed Maintenance:
   • Scheduled IOC restart: 2 hours
   • Detector cleaning: 3 hours
   • Network cable replacement: 1 hour
   • Software updates: 2 hours

📅 Upcoming Maintenance:
   • Motor controller cooling upgrade: January 20
   • Detector recalibration: January 22
   • Network optimization: January 25
   • Quarterly system review: February 1

━━━ User Feedback ━━━
📝 User Satisfaction:
   • Overall satisfaction: 4.6/5.0
   • System reliability: 4.8/5.0
   • Performance: 4.4/5.0
   • Support responsiveness: 4.7/5.0

💬 User Comments:
   • "System performance excellent this week"
   • "Detector response much improved"
   • "Network issues resolved quickly"
   • "Appreciate proactive maintenance"

━━━ Recommendations ━━━
🎯 High Priority:
   1. Install motor controller cooling upgrade
   2. Complete detector recalibration
   3. Implement network optimization

🎯 Medium Priority:
   1. Review temperature controller PID settings
   2. Update MEDM screen PV connections
   3. Optimize queue server performance

🎯 Low Priority:
   1. Enhance monitoring capabilities
   2. Improve documentation
   3. Expand training programs

━━━ Comparative Analysis ━━━
📊 vs. Previous Week:
   • Overall performance: +2 points (92→94)
   • Uptime: +0.3% (98.9%→99.2%)
   • Experiment success: +1.2% (94.5%→95.7%)
   • Issue resolution time: -3 minutes (21→18 min)

📊 vs. Monthly Average:
   • Overall performance: +1 point (93→94)
   • Uptime: +0.1% (99.1%→99.2%)
   • Experiment success: +0.5% (95.2%→95.7%)
   • User satisfaction: +0.2 points (4.4→4.6)

━━━ Financial Impact ━━━
💰 Cost Savings:
   • Reduced downtime: $2,400 saved
   • Improved efficiency: $1,800 saved
   • Preventive maintenance: $1,200 saved
   • Total weekly savings: $5,400

💰 Cost Investments:
   • Maintenance activities: $800
   • Upgrade preparations: $400
   • Training time: $200
   • Total weekly investment: $1,400

💰 Net Benefit: $4,000 (ROI: 285%)

━━━ Appendices ━━━
📊 Detailed Metrics:
   • Appendix A: IOC Performance Data
   • Appendix B: Experiment Details
   • Appendix C: Network Statistics
   • Appendix D: User Survey Results

📁 Supporting Files:
   • 8id-weekly-metrics.csv
   • 8id-issue-details.json
   • 8id-maintenance-log.pdf
   • 8id-user-feedback.xlsx

━━━ Report Distribution ━━━
📧 Email Recipients:
   • Beamline Scientist: Dr. Sarah Chen
   • Controls Engineer: Mike Rodriguez
   • Facility Manager: Lisa Wang
   • User Group Leaders: 4 recipients

🔗 Online Access:
   • Report URL: https://reports.aps.anl.gov/8id/weekly/20240115
   • Archive: https://reports.aps.anl.gov/8id/archive/
   • Dashboard: https://dashboard.aps.anl.gov/8id/

━━━ Next Steps ━━━
✅ Immediate Actions:
   • Schedule motor controller upgrade
   • Coordinate detector recalibration
   • Plan network optimization

📅 Next Report: January 22, 2024
🎯 Focus Areas: Post-maintenance performance, user satisfaction

Report generation completed in 3m 15s
Total report size: 2.4 MB (including appendices)
```

This comprehensive CLI examples document demonstrates the power and versatility of bAIt's command-line interface, showing how it provides detailed, actionable insights for beamline operations.