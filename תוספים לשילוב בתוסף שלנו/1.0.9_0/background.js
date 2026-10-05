
console.log('🚀 YouTube Lyrics - Background Service');

// Your Vercel backend URL
const BACKEND_URL = 'https://n-six-rust.vercel.app/api/track';

chrome.runtime.onInstalled.addListener((details) => {
  console.log('✅ Lyrics Extension Installed!');

  // Set new default settings for smart auto-show
  chrome.storage.sync.get(['autoShowLyrics', 'smartAutoShow'], (result) => {
    const updates = {};
    if (result.autoShowLyrics === undefined) {
      updates.autoShowLyrics = false;  // ✅ Already correct - OFF by default
    }
    if (result.smartAutoShow === undefined) {
      updates.smartAutoShow = true;    // ✅ Already correct - ON by default
    }
    if (Object.keys(updates).length > 0) {
      chrome.storage.sync.set(updates);
    }
  });
  
  chrome.storage.sync.set({ 
    autoShowLyrics: false,    // ✅ OFF by default
    smartAutoShow: true,       // ✅ ON by default
    darkMode: true
  });

  // Track installation or update
  if (details.reason === 'install') {
    console.log('📊 Tracking: New installation');
    trackBackgroundEvent('extension_installed', {
      version: chrome.runtime.getManifest().version
    });
  } else if (details.reason === 'update') {
    console.log('📊 Tracking: Extension updated');
    trackBackgroundEvent('extension_updated', {
      version: chrome.runtime.getManifest().version,
      previous_version: details.previousVersion
    });
  }
});

// Analytics function for background script
async function trackBackgroundEvent(eventName, params = {}) {
  try {
    const result = await chrome.storage.local.get(['clientId']);
    let clientId = result.clientId;
    
    if (!clientId) {
      clientId = crypto.randomUUID();
      await chrome.storage.local.set({ clientId });
      console.log('🆔 Generated new client ID:', clientId);
    }

    const payload = {
      client_id: clientId,
      events: [
        {
          name: eventName,
          params: {
            ...params,
            engagement_time_msec: 100,
          },
        },
      ],
    };

    console.log('📊 Tracking background event:', eventName, params);

    const response = await fetch(BACKEND_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      console.log('✅ Background event tracked successfully');
    } else {
      console.error('❌ Failed to track background event');
    }
  } catch (error) {
    console.error('❌ Background analytics error:', error);
  }
}

// Keep message listener for future features if needed
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background received message:', request.action);
  
  // Track certain actions from content script if needed
  if (request.action === 'trackEvent' && request.eventName) {
    trackBackgroundEvent(request.eventName, request.params || {});
  }
  
  sendResponse({ success: true });
  return true;
});
