// analytics.js - Enhanced Google Analytics tracking
console.log('📊 Enhanced Analytics module loaded');

// Your Vercel backend URL
const BACKEND_URL = 'https://n-six-rust-seven.vercel.app/api/track';

// Session tracking for engagement metrics
let sessionStartTime = Date.now();
let isActive = true;
let heartbeatInterval = null;

// Generate or get unique client ID
function getClientId() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['clientId'], (result) => {
      if (result.clientId) {
        resolve(result.clientId);
      } else {
        const newClientId = crypto.randomUUID();
        chrome.storage.local.set({ clientId: newClientId });
        resolve(newClientId);
      }
    });
  });
}

// Get user's country/location (approximate based on timezone)
function getUserLocation() {
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const locale = navigator.language || navigator.userLanguage;
  
  return {
    timezone,
    locale,
    // This will be enhanced by GA4's automatic geographic data
  };
}

// Get browser and system info
function getSystemInfo() {
  return {
    browser: navigator.userAgent.includes('Chrome') ? 'Chrome' : 
             navigator.userAgent.includes('Firefox') ? 'Firefox' : 
             navigator.userAgent.includes('Safari') ? 'Safari' : 'Other',
    os: navigator.platform,
    screen_resolution: `${screen.width}x${screen.height}`,
    language: navigator.language,
  };
}

// Send event to backend (which forwards to GA4)
async function trackEvent(eventName, params = {}) {
  try {
    const clientId = await getClientId();
    const location = getUserLocation();
    const systemInfo = getSystemInfo();

    const payload = {
      client_id: clientId,
      events: [
        {
          name: eventName,
          params: {
            ...params,
            ...location,
            ...systemInfo,
            engagement_time_msec: 100,
            session_id: sessionStartTime.toString(), // For session grouping
            timestamp: Date.now(),
          },
        },
      ],
    };

    console.log('📊 Tracking event:', eventName, params);

    const response = await fetch(BACKEND_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      console.log('✅ Event tracked successfully');
    } else {
      console.error('❌ Failed to track event', await response.text());
    }
  } catch (error) {
    console.error('❌ Analytics error:', error);
  }
}

// Track page view with enhanced data
async function trackPageView(pagePath, pageTitle) {
  try {
    const clientId = await getClientId();
    const location = getUserLocation();
    const systemInfo = getSystemInfo();

    const payload = {
      client_id: clientId,
      events: [
        {
          name: 'page_view',
          params: {
            page_location: `https://chrome-extension/${chrome.runtime.id}${pagePath}`,
            page_title: pageTitle,
            ...location,
            ...systemInfo,
            engagement_time_msec: 100,
            session_id: sessionStartTime.toString(),
          },
        },
      ],
    };

    const response = await fetch(BACKEND_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      console.log('✅ Page view tracked');
    }
  } catch (error) {
    console.error('❌ Page view tracking error:', error);
  }
}

// ============================================================================
// HEARTBEAT FOR REAL-TIME ACTIVE USERS
// ============================================================================

function startHeartbeat() {
  if (heartbeatInterval) return;
  
  // Send heartbeat every 30 seconds to track active users
  heartbeatInterval = setInterval(() => {
    if (isActive) {
      trackEvent('user_active', {
        active_duration: Math.floor((Date.now() - sessionStartTime) / 1000),
      });
    }
  }, 30000); // 30 seconds
  
  console.log('💓 Heartbeat started for real-time tracking');
}

function stopHeartbeat() {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
    heartbeatInterval = null;
    console.log('💓 Heartbeat stopped');
  }
}

// Detect user activity
let lastActivity = Date.now();
document.addEventListener('mousemove', () => {
  lastActivity = Date.now();
  isActive = true;
});
document.addEventListener('keydown', () => {
  lastActivity = Date.now();
  isActive = true;
});

// Check if user is inactive after 5 minutes
setInterval(() => {
  if (Date.now() - lastActivity > 300000) { // 5 minutes
    isActive = false;
  }
}, 60000); // Check every minute

// ============================================================================
// SPECIFIC EVENT TRACKING FUNCTIONS
// ============================================================================

/**
 * Track when user toggles auto-display
 * @param {boolean} enabled - Whether auto-display is enabled
 */
function trackAutoDisplayToggle(enabled) {
  trackEvent('setting_changed', {
    setting_name: 'auto_display',
    setting_value: enabled ? 'on' : 'off',
  });
}

/**
 * Track when user toggles dark/light mode
 * @param {boolean} isDarkMode - Whether dark mode is enabled
 */
function trackThemeToggle(isDarkMode) {
  trackEvent('setting_changed', {
    setting_name: 'theme',
    setting_value: isDarkMode ? 'dark' : 'light',
  });
}

/**
 * Track manual search queries (what users are searching for)
 * This helps identify videos that can't be loaded automatically
 * @param {string} query - The search query
 * @param {boolean} found - Whether lyrics were found
 */
function trackManualSearch(query, found = false) {
  trackEvent('manual_search', {
    search_query: query.substring(0, 100), // Limit to 100 chars for privacy
    search_result: found ? 'found' : 'not_found',
  });
}

/**
 * Track lyrics display
 * @param {string} artist - Artist name
 * @param {string} song - Song title
 * @param {string} source - Where lyrics came from (genius, musixmatch, etc)
 * @param {boolean} isSynced - Whether lyrics are time-synced
 */
function trackLyricsDisplayed(artist, song, source, isSynced = false) {
  trackEvent('lyrics_displayed', {
    artist: artist.substring(0, 50),
    song_title: song.substring(0, 50),
    lyrics_source: source,
    is_synced: isSynced,
  });
}

/**
 * Track when lyrics fail to load
 * @param {string} videoTitle - The YouTube video title
 * @param {string} reason - Why it failed
 */
function trackLyricsError(videoTitle, reason = 'not_found') {
  trackEvent('lyrics_error', {
    video_title: videoTitle.substring(0, 100),
    error_reason: reason,
  });
}

/**
 * Track auto-scroll toggle
 * @param {boolean} enabled - Whether auto-scroll is enabled
 */
function trackAutoScrollToggle(enabled) {
  trackEvent('setting_changed', {
    setting_name: 'auto_scroll',
    setting_value: enabled ? 'on' : 'off',
  });
}

/**
 * Track panel interactions
 * @param {string} action - minimize, maximize, close, etc.
 */
function trackPanelInteraction(action) {
  trackEvent('panel_interaction', {
    interaction_type: action,
  });
}

/**
 * Track video info
 * @param {string} videoId - YouTube video ID
 * @param {string} channelName - Channel name
 */
function trackVideoViewed(videoId, channelName = '') {
  trackEvent('video_viewed', {
    video_id: videoId,
    channel_name: channelName.substring(0, 50),
  });
}

/**
 * Track user engagement with synced lyrics
 * @param {number} duration - How long user watched with synced lyrics
 */
function trackSyncedLyricsEngagement(duration) {
  trackEvent('synced_lyrics_engagement', {
    duration_seconds: Math.floor(duration),
  });
}

// ============================================================================
// SESSION TRACKING
// ============================================================================

// Track session start
trackEvent('session_start', {
  session_id: sessionStartTime.toString(),
});

// Track session end when user closes tab/browser
window.addEventListener('beforeunload', () => {
  const sessionDuration = Math.floor((Date.now() - sessionStartTime) / 1000);
  trackEvent('session_end', {
    session_duration: sessionDuration,
  });
  stopHeartbeat();
});

// Start heartbeat for real-time tracking
startHeartbeat();

// ============================================================================
// EXPORT
// ============================================================================

// Export functions globally for content.js to use
window.analytics = {
  trackEvent,
  trackPageView,
  trackAutoDisplayToggle,
  trackThemeToggle,
  trackManualSearch,
  trackLyricsDisplayed,
  trackLyricsError,
  trackAutoScrollToggle,
  trackPanelInteraction,
  trackVideoViewed,
  trackSyncedLyricsEngagement,
};

console.log('✅ Enhanced Analytics ready');