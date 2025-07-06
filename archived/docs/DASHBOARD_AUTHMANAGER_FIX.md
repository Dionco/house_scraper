# Dashboard AuthManager Fix

## Issue
The dashboard iframe was experiencing authentication issues with the following problems:
1. **Duplicate AuthManager declaration**: The dashboard was trying to create a new `authManager` instance while `auth.js` already creates a global one
2. **Syntax error**: `Uncaught SyntaxError: Identifier 'authManager' has already been declared`
3. **Infinite retry loop**: The dashboard kept trying to initialize AuthManager but failed due to the duplicate declaration
4. **Profile selection not working**: Because AuthManager wasn't properly initialized, users couldn't select search profiles

## Root Cause
The `auth.js` file creates a global `authManager` instance and exports it to `window.authManager`, but the dashboard was trying to create its own instance, causing a conflict.

## Solution
Modified the dashboard to use the existing global `authManager` instance instead of creating a new one:

### 1. Updated Authentication Initialization
**Before:**
```javascript
// Global auth manager instance
let authManager = null;

// Wait for auth.js to load and initialize AuthManager
function initializeAuth() {
    if (typeof AuthManager === 'undefined') {
        console.log('AuthManager class not loaded yet, retrying...');
        setTimeout(initializeAuth, 100);
        return;
    }
    
    authManager = new AuthManager();
    // ...
}
```

**After:**
```javascript
// Wait for auth.js to load and use the global authManager
function initializeAuth() {
    if (typeof window.authManager === 'undefined') {
        console.log('Global authManager not loaded yet, retrying...');
        setTimeout(initializeAuth, 100);
        return;
    }
    
    console.log('Using global authManager instance');
    // No need to create new instance - use existing one
    // ...
}
```

### 2. Updated Token Handling
**Before:**
```javascript
// Store the token
localStorage.setItem('token', event.data.token);

// Reinitialize AuthManager with the new token
authManager = new AuthManager();
```

**After:**
```javascript
// Store the token in localStorage
localStorage.setItem('accessToken', event.data.token);
if (event.data.user) {
    localStorage.setItem('currentUser', JSON.stringify(event.data.user));
}

// Reload the authManager state from localStorage
window.authManager.loadFromStorage();
```

### 3. Updated All AuthManager References
Changed all references from `authManager` to `window.authManager` throughout the dashboard:
- Authentication checks: `window.authManager.isAuthenticated()`
- API requests: `window.authManager.apiRequest()`
- User data: `window.authManager.getCurrentUser()`
- Event listeners: `window.authManager.addListener()`

### 4. Fixed Function Names
Updated `loadUserData()` to call the correct existing functions:
- `loadProfiles()` → `fetchProfiles()`
- `loadListings()` → `fetchListings(null, false)`

## Files Modified
- `/backend/listings.html` - Updated authentication initialization and all AuthManager references

## Result
- ✅ No more duplicate AuthManager declaration errors
- ✅ No more infinite retry loops  
- ✅ Proper authentication flow in iframe mode
- ✅ Profile selection dropdown now works correctly
- ✅ User-specific data loads properly after login
- ✅ Clean console logs without authentication errors

## Testing
1. Navigate to `http://localhost:8000`
2. Login with valid credentials
3. Dashboard should load in iframe without errors
4. Profile selection dropdown should populate and work
5. User-specific listings should display
6. No more "AuthManager class not loaded yet" errors in console

The authentication flow now works seamlessly between the parent landing page and the dashboard iframe, allowing users to properly select search profiles and view their listings.
