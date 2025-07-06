/**
 * Authentication components for the House Scraper frontend
 * Handles user registration, login, and session management
 */

class AuthManager {
    constructor() {
        this.currentUser = null;
        this.accessToken = null;
        this.refreshToken = null;
        this.listeners = [];
        
        // Initialize from localStorage
        this.loadFromStorage();
        
        // Set up automatic token refresh
        this.setupTokenRefresh();
    }
    
    /**
     * Load authentication state from localStorage
     */
    loadFromStorage() {
        const storedUser = localStorage.getItem('currentUser');
        const storedAccessToken = localStorage.getItem('accessToken');
        const storedRefreshToken = localStorage.getItem('refreshToken');
        
        if (storedUser && storedAccessToken && storedRefreshToken) {
            this.currentUser = JSON.parse(storedUser);
            this.accessToken = storedAccessToken;
            this.refreshToken = storedRefreshToken;
        }
    }
    
    /**
     * Save authentication state to localStorage
     */
    saveToStorage() {
        if (this.currentUser && this.accessToken && this.refreshToken) {
            localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
            localStorage.setItem('accessToken', this.accessToken);
            localStorage.setItem('refreshToken', this.refreshToken);
        } else {
            localStorage.removeItem('currentUser');
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
        }
    }
    
    /**
     * Set up automatic token refresh
     */
    setupTokenRefresh() {
        // Check token expiry every 5 minutes
        setInterval(() => {
            if (this.accessToken && this.refreshToken) {
                const tokenData = this.parseJWT(this.accessToken);
                if (tokenData) {
                    const now = Math.floor(Date.now() / 1000);
                    const expiry = tokenData.exp;
                    
                    // Refresh token if it expires in next 5 minutes
                    if (expiry - now < 300) {
                        this.refreshAccessToken();
                    }
                }
            }
        }, 5 * 60 * 1000); // 5 minutes
    }
    
    /**
     * Parse JWT token
     */
    parseJWT(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            
            return JSON.parse(jsonPayload);
        } catch (e) {
            return null;
        }
    }
    
    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!(this.currentUser && this.accessToken);
    }
    
    /**
     * Get current user
     */
    getCurrentUser() {
        return this.currentUser;
    }
    
    /**
     * Get access token
     */
    getToken() {
        return this.accessToken;
    }
    
    /**
     * Get authorization header
     */
    getAuthHeader() {
        return this.accessToken ? { 'Authorization': `Bearer ${this.accessToken}` } : {};
    }
    
    /**
     * Register a new user
     */
    async register(userData) {
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                const errorMessage = errorData.detail || errorData.message || 'Registration failed';
                throw new Error(errorMessage);
            }
            
            const data = await response.json();
            this.setAuthData(data);
            return data;
        } catch (error) {
            console.error('Registration error:', error);
            if (error.message) {
                throw error;
            } else {
                throw new Error('Registration failed. Please try again.');
            }
        }
    }
    
    /**
     * Login user
     */
    async login(credentials) {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                const errorMessage = errorData.detail || errorData.message || 'Login failed';
                throw new Error(errorMessage);
            }
            
            const data = await response.json();
            this.setAuthData(data);
            return data;
        } catch (error) {
            console.error('Login error:', error);
            if (error.message) {
                throw error;
            } else {
                throw new Error('Login failed. Please check your credentials.');
            }
        }
    }
    
    /**
     * Logout user
     */
    async logout() {
        try {
            if (this.accessToken) {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: this.getAuthHeader()
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.clearAuthData();
        }
    }
    
    /**
     * Refresh access token
     */
    async refreshAccessToken() {
        try {
            const response = await fetch('/api/auth/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    refresh_token: this.refreshToken
                })
            });
            
            if (!response.ok) {
                throw new Error('Token refresh failed');
            }
            
            const data = await response.json();
            this.setAuthData(data);
            return data;
        } catch (error) {
            console.error('Token refresh error:', error);
            this.clearAuthData();
            throw error;
        }
    }
    
    /**
     * Set authentication data
     */
    setAuthData(data) {
        this.currentUser = data.user;
        this.accessToken = data.access_token;
        this.refreshToken = data.refresh_token;
        this.saveToStorage();
        this.notifyListeners();
    }
    
    /**
     * Clear authentication data
     */
    clearAuthData() {
        this.currentUser = null;
        this.accessToken = null;
        this.refreshToken = null;
        this.saveToStorage();
        this.notifyListeners();
    }
    
    /**
     * Add authentication state listener
     */
    addListener(callback) {
        this.listeners.push(callback);
    }
    
    /**
     * Remove authentication state listener
     */
    removeListener(callback) {
        this.listeners = this.listeners.filter(listener => listener !== callback);
    }
    
    /**
     * Notify all listeners of authentication state change
     */
    notifyListeners() {
        this.listeners.forEach(callback => callback(this.currentUser));
    }
    
    /**
     * Update user profile
     */
    async updateProfile(profileData) {
        try {
            const response = await this.apiRequest('/api/auth/profile', {
                method: 'PUT',
                body: JSON.stringify(profileData)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Profile update failed');
            }
            
            const data = await response.json();
            this.currentUser = { ...this.currentUser, ...data };
            this.saveToStorage();
            this.notifyListeners();
            
            return data;
        } catch (error) {
            console.error('Profile update error:', error);
            throw error;
        }
    }
    
    /**
     * Make authenticated API request
     */
    async apiRequest(url, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...this.getAuthHeader(),
            ...options.headers
        };
        
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        // Handle token expiry
        if (response.status === 401 && this.refreshToken) {
            try {
                await this.refreshAccessToken();
                // Retry the original request
                return fetch(url, {
                    ...options,
                    headers: {
                        ...headers,
                        ...this.getAuthHeader()
                    }
                });
            } catch (error) {
                // Refresh failed, redirect to login
                this.clearAuthData();
                throw error;
            }
        }
        
        return response;
    }
}

// Create global auth manager instance
const authManager = new AuthManager();

/**
 * Authentication UI Component
 */
class AuthUI {
    constructor() {
        this.isOpen = false;
        this.mode = 'login'; // 'login' or 'register'
        this.createModal();
        this.setupEventListeners();
    }
    
    /**
     * Create authentication modal
     */
    createModal() {
        const modalHTML = `
            <div id="auth-modal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 hidden">
                <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                    <div class="mt-3">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-medium text-gray-900" id="auth-modal-title">Login</h3>
                            <button id="auth-modal-close" class="text-gray-400 hover:text-gray-600">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>
                        
                        <div id="auth-error" class="hidden mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                            <div class="flex">
                                <div class="flex-shrink-0">
                                    <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                                    </svg>
                                </div>
                                <div class="ml-3">
                                    <p class="text-sm text-red-800" id="auth-error-message"></p>
                                </div>
                            </div>
                        </div>
                        
                        <form id="auth-form" class="space-y-4">
                            <div id="register-fields" class="hidden">
                                <div>
                                    <label for="auth-email" class="block text-sm font-medium text-gray-700">Email</label>
                                    <input type="email" id="auth-email" name="email" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary">
                                </div>
                            </div>
                            
                            <div>
                                <label for="auth-username" class="block text-sm font-medium text-gray-700">Username</label>
                                <input type="text" id="auth-username" name="username" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary">
                            </div>
                            
                            <div>
                                <label for="auth-password" class="block text-sm font-medium text-gray-700">Password</label>
                                <input type="password" id="auth-password" name="password" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary">
                            </div>
                            
                            <div id="password-requirements" class="hidden text-sm text-gray-500">
                                <p>Password must be at least 8 characters long and contain:</p>
                                <ul class="list-disc list-inside ml-2">
                                    <li>At least one letter</li>
                                    <li>At least one number</li>
                                </ul>
                            </div>
                            
                            <div class="flex items-center justify-between">
                                <button type="submit" id="auth-submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
                                    Login
                                </button>
                            </div>
                        </form>
                        
                        <div class="mt-6 text-center">
                            <button id="auth-toggle" class="text-primary hover:text-primary-600 text-sm">
                                Don't have an account? Register
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('auth-modal');
        this.form = document.getElementById('auth-form');
        this.errorDiv = document.getElementById('auth-error');
        this.errorMessage = document.getElementById('auth-error-message');
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Close modal
        document.getElementById('auth-modal-close').addEventListener('click', () => {
            this.close();
        });
        
        // Close modal on outside click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
        
        // Toggle between login and register
        document.getElementById('auth-toggle').addEventListener('click', () => {
            this.toggleMode();
        });
        
        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
        
        // Show password requirements when in register mode
        document.getElementById('auth-password').addEventListener('focus', () => {
            if (this.mode === 'register') {
                document.getElementById('password-requirements').classList.remove('hidden');
            }
        });
    }
    
    /**
     * Show login modal
     */
    showLogin() {
        this.mode = 'login';
        this.updateUI();
        this.show();
    }
    
    /**
     * Show register modal
     */
    showRegister() {
        this.mode = 'register';
        this.updateUI();
        this.show();
    }
    
    /**
     * Show modal
     */
    show() {
        this.modal.classList.remove('hidden');
        this.isOpen = true;
        this.clearError();
        this.form.reset();
    }
    
    /**
     * Close modal
     */
    close() {
        this.modal.classList.add('hidden');
        this.isOpen = false;
    }
    
    /**
     * Toggle between login and register modes
     */
    toggleMode() {
        this.mode = this.mode === 'login' ? 'register' : 'login';
        this.updateUI();
        this.clearError();
    }
    
    /**
     * Update UI based on current mode
     */
    updateUI() {
        const title = document.getElementById('auth-modal-title');
        const submitBtn = document.getElementById('auth-submit');
        const toggleBtn = document.getElementById('auth-toggle');
        const registerFields = document.getElementById('register-fields');
        const passwordReqs = document.getElementById('password-requirements');
        
        if (this.mode === 'login') {
            title.textContent = 'Login';
            submitBtn.textContent = 'Login';
            toggleBtn.textContent = "Don't have an account? Register";
            registerFields.classList.add('hidden');
            passwordReqs.classList.add('hidden');
        } else {
            title.textContent = 'Register';
            submitBtn.textContent = 'Register';
            toggleBtn.textContent = "Already have an account? Login";
            registerFields.classList.remove('hidden');
        }
    }
    
    /**
     * Handle form submission
     */
    async handleSubmit() {
        const formData = new FormData(this.form);
        const data = Object.fromEntries(formData);
        
        try {
            this.showLoading();
            
            if (this.mode === 'login') {
                await authManager.login({
                    username: data.username,
                    password: data.password
                });
            } else {
                await authManager.register({
                    username: data.username,
                    email: data.email,
                    password: data.password
                });
            }
            
            this.close();
            showNotification(`${this.mode === 'login' ? 'Login' : 'Registration'} successful!`, 'success');
            
            // Reload page to refresh user context
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        const submitBtn = document.getElementById('auth-submit');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Loading...';
    }
    
    /**
     * Hide loading state
     */
    hideLoading() {
        const submitBtn = document.getElementById('auth-submit');
        submitBtn.disabled = false;
        submitBtn.textContent = this.mode === 'login' ? 'Login' : 'Register';
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorDiv.classList.remove('hidden');
    }
    
    /**
     * Clear error message
     */
    clearError() {
        this.errorDiv.classList.add('hidden');
        this.errorMessage.textContent = '';
    }
}

// Create global auth UI instance
const authUI = new AuthUI();

// Export for global use
window.AuthManager = AuthManager;
window.authManager = authManager;
window.authUI = authUI;
