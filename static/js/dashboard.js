// Professional Proctoring AI Dashboard JavaScript

let updateInterval = null;
let sessionStartTime = null;
let isMonitoring = false;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    startStatusUpdates();
    updateTime();
    setInterval(updateTime, 5000);
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
    }, 5000); // Update every 5 seconds as requested
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
            
            // Update audio detection
            const audioNormal = !data.speech_detected && !data.suspicious_audio;
            let audioStatusText = 'No Audio';
            if (data.suspicious_audio) {
                audioStatusText = 'Suspicious Audio!';
            } else if (data.speech_detected) {
                audioStatusText = 'Speech Detected';
            } else if (data.audio_detected) {
                audioStatusText = 'Audio Detected';
            }
            updateIndicator('audioIndicator', 'audioStatus', 
                audioNormal, 
                audioStatusText);
            document.getElementById('volumeLevel').textContent = `Volume: ${data.volume_level}%`;
            
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
        'SPEECH_DETECTED': '<i class="fas fa-microphone"></i> Speech Detected',
        'SUSPICIOUS_AUDIO': '<i class="fas fa-volume-up"></i> Suspicious Audio',
        'EYE_MOVEMENT': '<i class="fas fa-eye"></i> Suspicious Eye Movement',
        'HEAD_MOVEMENT': '<i class="fas fa-head-side"></i> Head Movement Detected',
        'HEAD_DOWN': '<i class="fas fa-arrow-down"></i> Head Looking Down',
        'HEAD_UP': '<i class="fas fa-arrow-up"></i> Head Looking Up'
    };
    
    let html = '';
    alerts.forEach(alert => {
        const severity = (alert.includes('PHONE') || alert.includes('MULTIPLE') || alert.includes('SUSPICIOUS')) ? 'danger' : 'warning';
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
        const elapsed = Math.floor((now - sessionStartTime) / 5000);
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

// Screenshot Detection - Multiple Methods
let screenshotAttempts = 0;

// Function to show screenshot warning
function showScreenshotWarning() {
    const overlay = document.getElementById('screenshotWarning');
    overlay.classList.add('active');
    
    // Log to backend
    fetch('/api/log_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            type: 'SCREENSHOT_ATTEMPT',
            attempts: ++screenshotAttempts
        })
    });
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        overlay.classList.remove('active');
    }, 3000);
}

// Hide screenshot warning
function hideScreenshotWarning() {
    document.getElementById('screenshotWarning').classList.remove('active');
}

// Method 1: Detect PrintScreen key
document.addEventListener('keyup', function(e) {
    if (e.key === 'PrintScreen' || e.keyCode === 44) {
        console.log('⚠️ PrintScreen key detected!');
        showScreenshotWarning();
        showNotification('🚨 Screenshot attempt detected and logged!', 'danger');
        
        // Clear clipboard to prevent screenshot
        try {
            navigator.clipboard.writeText('SCREENSHOT PROHIBITED - This action has been logged');
        } catch (err) {
            console.log('Could not clear clipboard:', err);
        }
    }
});

// Method 1b: Prevent PrintScreen in keydown
document.addEventListener('keydown', function(e) {
    if (e.key === 'PrintScreen' || e.keyCode === 44) {
        e.preventDefault();
        e.stopPropagation();
        showScreenshotWarning();
        showNotification('🚨 Screenshot BLOCKED!', 'danger');
        return false;
    }
});

// Method 1c: Disable context menu (right-click) during monitoring
document.addEventListener('contextmenu', function(e) {
    if (isMonitoring) {
        e.preventDefault();
        showNotification('⛔ Right-click disabled during monitoring', 'warning');
        return false;
    }
});

// Method 2: Detect common screenshot keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Windows: Win+Shift+S, Win+PrintScreen
    // Mac: Cmd+Shift+3, Cmd+Shift+4, Cmd+Shift+5
    if ((e.metaKey || e.key === 'Meta') && e.shiftKey && 
        (e.key === '3' || e.key === '4' || e.key === '5' || e.key === 's' || e.key === 'S')) {
        e.preventDefault();
        console.log('⚠️ Screenshot keyboard shortcut detected!');
        showScreenshotWarning();
        showNotification('🚨 Screenshot shortcut blocked and logged!', 'danger');
        return false;
    }
    
    // Windows Snipping Tool shortcuts
    if (e.key === 'PrintScreen' || e.keyCode === 44) {
        e.preventDefault();
        console.log('⚠️ PrintScreen detected!');
        showScreenshotWarning();
        showNotification('🚨 Screenshot blocked and logged!', 'danger');
        return false;
    }
});

// Method 3: Detect window blur (might indicate screenshot tool opened)
let blurCount = 0;
let lastBlurTime = 0;

window.addEventListener('blur', function() {
    const currentTime = Date.now();
    
    // If window loses focus multiple times in short period (suspicious)
    if (currentTime - lastBlurTime < 2000) {
        blurCount++;
        if (blurCount >= 2) {
            console.log('⚠️ Suspicious window focus pattern detected!');
            showNotification('⚠️ Suspicious activity detected', 'warning');
            blurCount = 0;
        }
    } else {
        blurCount = 1;
    }
    
    lastBlurTime = currentTime;
});

// Method 4: Detect browser DevTools (could be used for screenshots)
const devtoolsDetector = () => {
    const threshold = 160;
    const widthThreshold = window.outerWidth - window.innerWidth > threshold;
    const heightThreshold = window.outerHeight - window.innerHeight > threshold;
    
    if (widthThreshold || heightThreshold) {
        console.log('⚠️ Developer tools might be open!');
        // Don't show warning for devtools, but log it
        fetch('/api/log_event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: 'DEVTOOLS_DETECTED'
            })
        });
    }
};

// Check for devtools every 1 second
setInterval(devtoolsDetector, 1000);

// Method 5: Detect copy attempts on video
document.getElementById('videoFeed')?.addEventListener('copy', function(e) {
    e.preventDefault();
    showScreenshotWarning();
    showNotification('🚨 Copy attempt blocked!', 'danger');
    return false;
});

// Method 6: Disable drag and drop on video
document.getElementById('videoFeed')?.addEventListener('dragstart', function(e) {
    e.preventDefault();
    return false;
});

// Method 7: Monitor visibility API for screenshot tools
document.addEventListener('visibilitychange', function() {
    if (document.hidden && isMonitoring) {
        // Page hidden during monitoring - could be screenshot tool
        console.log('⚠️ Page visibility changed during monitoring');
    }
});

// Prevent selection of content (makes screenshots less useful)
document.body.style.userSelect = 'none';
document.body.style.webkitUserSelect = 'none';
document.body.style.mozUserSelect = 'none';
document.body.style.msUserSelect = 'none';

// Continuously monitor clipboard for screenshot attempts
setInterval(() => {
    if (isMonitoring) {
        try {
            navigator.clipboard.readText().then(text => {
                // If clipboard contains image data or is recently changed, it might be a screenshot
                if (text && text.length > 0) {
                    // Clear it
                    navigator.clipboard.writeText('SCREENSHOT PROHIBITED');
                }
            }).catch(err => {
                // Permission denied or no clipboard access
            });
        } catch (err) {
            // Browser doesn't support clipboard API
        }
    }
}, 500);

// Add CSS to make entire page harder to screenshot
const style = document.createElement('style');
style.textContent = `
    * {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }
    img, video {
        pointer-events: none !important;
        -webkit-user-drag: none !important;
    }
`;
document.head.appendChild(style);

console.log('✓ Screenshot prevention systems activated');
console.log('✓ Audio detection UI ready');

