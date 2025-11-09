// Professional Proctoring AI Dashboard JavaScript

let updateInterval = null;
let sessionStartTime = null;
let isMonitoring = false;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    startStatusUpdates();
    updateTime();
    setInterval(updateTime, 1000);
});

// Start monitoring
function startMonitoring() {
    fetch('/api/start_monitoring')
        .then(response => response.json())
        .then(data => {
            if (data.monitoring) {
                isMonitoring = true;
                sessionStartTime = new Date();
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('stopBtn').style.display = 'inline-block';
                showNotification('Monitoring started', 'success');
            }
        })
        .catch(error => {
            console.error('Error starting monitoring:', error);
            showNotification('Failed to start monitoring', 'danger');
        });
}

// Stop monitoring
function stopMonitoring() {
    fetch('/api/stop_monitoring')
        .then(response => response.json())
        .then(data => {
            isMonitoring = false;
            sessionStartTime = null;
            document.getElementById('startBtn').style.display = 'inline-block';
            document.getElementById('stopBtn').style.display = 'none';
            showNotification('Monitoring stopped', 'warning');
        })
        .catch(error => {
            console.error('Error stopping monitoring:', error);
        });
}

// Capture screenshot
function captureScreenshot() {
    const canvas = document.createElement('canvas');
    const video = document.getElementById('videoFeed');
    canvas.width = video.naturalWidth;
    canvas.height = video.naturalHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    canvas.toBlob(function(blob) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `proctoring_${new Date().getTime()}.jpg`;
        a.click();
        URL.revokeObjectURL(url);
        showNotification('Screenshot captured', 'success');
    }, 'image/jpeg');
}

// Start status updates
function startStatusUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    
    updateInterval = setInterval(() => {
        updateStatus();
        updateViolations();
        updateActivityLog();  // Add activity log updates
    }, 500); // Update every 500ms for smooth UI
}

// Update status from API
function updateStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            // Update alert status
            updateAlertStatus(data.alert_level);
            
            // Update face detection
            updateIndicator('faceIndicator', 'faceStatus', 
                data.face_detected, 
                data.face_detected ? 'Face Detected' : 'No Face');
            
            // Update eye tracking
            const eyeNormal = data.eye_status === 'Center' || data.eye_status === 'Not Detected';
            updateIndicator('eyeIndicator', 'eyeStatus', 
                eyeNormal, 
                data.eye_status);
            
            // Update head pose
            const headNormal = data.head_status === 'Head Straight' || data.head_status === 'Not Detected';
            updateIndicator('headIndicator', 'headStatus', 
                headNormal, 
                data.head_status);
            
            // Update person count
            const personNormal = data.person_count === 1;
            updateIndicator('personIndicator', 'personStatus', 
                personNormal, 
                `${data.person_count} Person${data.person_count !== 1 ? 's' : ''}`);
            
            // Update phone detection
            updateIndicator('phoneIndicator', 'phoneStatus', 
                !data.phone_detected, 
                data.phone_detected ? 'Phone Detected!' : 'No Phone');
            
            // Update statistics
            document.getElementById('totalViolations').textContent = data.total_violations;
            document.getElementById('framesProcessed').textContent = data.frames_processed;
            document.getElementById('timestamp').textContent = data.timestamp;
            
            // Update active alerts
            updateActiveAlerts(data.alerts);
            
            // Calculate FPS
            if (data.frames_processed > 0) {
                const fps = Math.round(data.frames_processed / ((new Date() - sessionStartTime) / 1000));
                document.getElementById('fps').textContent = `FPS: ${fps || '--'}`;
            }
        })
        .catch(error => {
            console.error('Error updating status:', error);
        });
}

// Update alert status card
function updateAlertStatus(level) {
    const alertCard = document.getElementById('alertCard');
    const alertStatus = document.getElementById('alertStatus');
    const alertBadge = document.getElementById('alertBadge');
    const alertBanner = document.getElementById('alertBanner');
    
    // Remove all alert classes
    alertCard.classList.remove('alert-normal', 'alert-warning', 'alert-danger');
    alertBanner.classList.remove('warning', 'danger');
    
    // Update based on level
    if (level === 'NORMAL') {
        alertCard.classList.add('alert-normal');
        alertStatus.textContent = 'NORMAL';
        alertBadge.innerHTML = '<i class="fas fa-check-circle"></i> All Good';
        alertBanner.innerHTML = '<i class="fas fa-shield-alt"></i> Monitoring Active';
    } else if (level === 'WARNING') {
        alertCard.classList.add('alert-warning');
        alertStatus.textContent = 'WARNING';
        alertBadge.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Attention Needed';
        alertBanner.classList.add('warning');
        alertBanner.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Warning Detected';
    } else if (level === 'ALERT') {
        alertCard.classList.add('alert-danger');
        alertStatus.textContent = 'ALERT';
        alertBadge.innerHTML = '<i class="fas fa-times-circle"></i> Violation Detected';
        alertBanner.classList.add('danger');
        alertBanner.innerHTML = '<i class="fas fa-ban"></i> ALERT: Violation!';
    }
}

// Update indicator
function updateIndicator(indicatorId, statusId, isNormal, text) {
    const indicator = document.getElementById(indicatorId);
    const status = document.getElementById(statusId);
    
    indicator.classList.remove('active', 'warning', 'danger', 'inactive');
    
    if (text === 'Not Detected' || text === 'No Face') {
        indicator.classList.add('inactive');
    } else if (isNormal) {
        indicator.classList.add('active');
    } else if (text.includes('Phone')) {
        indicator.classList.add('danger');
    } else {
        indicator.classList.add('warning');
    }
    
    status.textContent = text;
}

// Update active alerts
function updateActiveAlerts(alerts) {
    const alertsList = document.getElementById('activeAlerts');
    
    if (!alerts || alerts.length === 0) {
        alertsList.innerHTML = `
            <div class="text-center text-muted p-3">
                <i class="fas fa-check-circle fa-2x mb-2"></i>
                <p>No active alerts</p>
            </div>
        `;
        return;
    }
    
    const alertLabels = {
        'NO_FACE': '<i class="fas fa-user-slash"></i> No Face Detected',
        'NO_PERSON': '<i class="fas fa-user-times"></i> No Person Detected',
        'MULTIPLE_PEOPLE': '<i class="fas fa-users"></i> Multiple People',
        'PHONE_DETECTED': '<i class="fas fa-mobile-alt"></i> Phone Detected',
        'EYE_MOVEMENT': '<i class="fas fa-eye"></i> Suspicious Eye Movement',
        'HEAD_MOVEMENT': '<i class="fas fa-head-side"></i> Head Movement Detected'
    };
    
    let html = '';
    alerts.forEach(alert => {
        const severity = alert.includes('PHONE') || alert.includes('MULTIPLE') ? 'danger' : 'warning';
        html += `
            <div class="alert-item ${severity}">
                ${alertLabels[alert] || alert}
            </div>
        `;
    });
    
    alertsList.innerHTML = html;
}

// Update violations log
function updateViolations() {
    fetch('/api/violations')
        .then(response => response.json())
        .then(data => {
            const violationsList = document.getElementById('violationsList');
            
            if (!data.violations || data.violations.length === 0) {
                violationsList.innerHTML = `
                    <div class="text-center text-muted p-3">
                        <i class="fas fa-clipboard-list fa-2x mb-2"></i>
                        <p>No violations detected</p>
                    </div>
                `;
                return;
            }
            
            let html = '';
            data.violations.reverse().forEach(violation => {
                const severityClass = violation.severity.toLowerCase();
                html += `
                    <div class="violation-item">
                        <span class="violation-time">${violation.timestamp}</span>
                        <span class="violation-type">${violation.type}</span>
                        <span class="violation-severity ${severityClass}">${violation.severity}</span>
                    </div>
                `;
            });
            
            violationsList.innerHTML = html;
        })
        .catch(error => {
            console.error('Error updating violations:', error);
        });
}

// Update time display
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    
    if (sessionStartTime) {
        const elapsed = Math.floor((now - sessionStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        document.getElementById('sessionDuration').textContent = 
            `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        
        const sessionTime = document.getElementById('sessionTime');
        const sessionElapsed = Math.floor(elapsed / 60);
        sessionTime.textContent = `Session: ${sessionElapsed}m ${seconds}s`;
    }
}

// Show notification
function showNotification(message, type) {
    const notificationHTML = `
        <div class="alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3" 
             style="z-index: 9999;" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.createElement('div');
    container.innerHTML = notificationHTML;
    document.body.appendChild(container.firstElementChild);
    
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, 3000);
}

// Toggle fullscreen
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.key === 'F11') {
        e.preventDefault();
        toggleFullscreen();
    } else if (e.key === 's' || e.key === 'S') {
        if (e.ctrlKey) {
            e.preventDefault();
            captureScreenshot();
        }
    }
});

// Handle page visibility changes and fullscreen exits
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        console.log('⚠️ Page hidden - user switched tab or minimized window');
        
        // Log the event to backend
        fetch('/api/log_event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: 'PAGE_HIDDEN'
            })
        });
        
        // Show alert to user when they return
        setTimeout(() => {
            if (!document.hidden) {
                showNotification('⚠️ Warning: Tab switching detected and logged!', 'danger');
            }
        }, 1000);
    } else {
        console.log('✓ Page visible - user returned to exam');
        
        // Log the return event
        fetch('/api/log_event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: 'PAGE_VISIBLE'
            })
        });
        
        updateStatus();
    }
});

// Handle fullscreen changes
document.addEventListener('fullscreenchange', function() {
    if (!document.fullscreenElement) {
        console.log('⚠️ User exited fullscreen mode');
        
        // Log the fullscreen exit
        fetch('/api/log_event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: 'FULLSCREEN_EXIT'
            })
        });
        
        showNotification('⚠️ Warning: Exiting fullscreen is not allowed during exam!', 'danger');
    } else {
        console.log('✓ Entered fullscreen mode');
        
        // Log fullscreen entry
        fetch('/api/log_event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: 'FULLSCREEN_ENTER'
            })
        });
    }
});

// Prevent right-click context menu (industry best practice for exams)
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    showNotification('Right-click is disabled during the exam', 'warning');
});

// Prevent common keyboard shortcuts for cheating
document.addEventListener('keydown', function(e) {
    // Prevent opening developer tools
    if (e.key === 'F12' || 
        (e.ctrlKey && e.shiftKey && e.key === 'I') ||
        (e.ctrlKey && e.shiftKey && e.key === 'J') ||
        (e.ctrlKey && e.key === 'U')) {
        e.preventDefault();
        showNotification('⚠️ This action is not allowed during the exam', 'danger');
        return false;
    }
    
    // Allow F11 for fullscreen
    if (e.key === 'F11') {
        e.preventDefault();
        toggleFullscreen();
    }
    
    // Allow Ctrl+S for screenshot
    if (e.key === 's' || e.key === 'S') {
        if (e.ctrlKey) {
            e.preventDefault();
            captureScreenshot();
        }
    }
});

// Warn user before leaving page
window.addEventListener('beforeunload', function(e) {
    if (isMonitoring) {
        e.preventDefault();
        e.returnValue = 'Are you sure you want to leave? Your exam session will be terminated.';
        return e.returnValue;
    }
});

// Update activity log
function updateActivityLog() {
    fetch('/api/activity')
        .then(response => response.json())
        .then(data => {
            const activityLog = document.getElementById('activityLog');
            
            if (!data.activities || data.activities.length === 0) {
                activityLog.innerHTML = `
                    <div class="text-center text-muted p-3">
                        <i class="fas fa-history fa-2x mb-2"></i>
                        <p>No activity yet</p>
                    </div>
                `;
                return;
            }
            
            let html = '';
            data.activities.reverse().forEach(activity => {
                const levelClass = activity.level.toLowerCase();
                const iconMap = {
                    'INFO': 'fa-info-circle',
                    'WARNING': 'fa-exclamation-triangle',
                    'CRITICAL': 'fa-times-circle'
                };
                const icon = iconMap[activity.level] || 'fa-circle';
                
                html += `
                    <div class="activity-item ${levelClass}">
                        <span class="activity-time">${activity.timestamp}</span>
                        <span class="activity-message">
                            <i class="fas ${icon}"></i> ${activity.message}
                        </span>
                    </div>
                `;
            });
            
            activityLog.innerHTML = html;
        })
        .catch(error => {
            console.error('Error updating activity log:', error);
        });
}
