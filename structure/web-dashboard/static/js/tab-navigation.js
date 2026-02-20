/**
 * Tab Navigation Component
 * Handles tab-based navigation between Overview and Phase Details views
 * Requirements: 16.1, 16.2, 16.3, 16.4, 16.5
 */

class TabNavigation {
    constructor() {
        this.currentTab = 'overview';
        this.tabs = {};
        this.tabContents = {};
    }

    /**
     * Initialize tab navigation system
     * Sets up event listeners and restores saved tab state
     */
    initializeTabs() {
        console.log('Initializing tab navigation...');
        
        // Get all tab buttons and content containers
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');
        
        // Store references
        tabButtons.forEach(button => {
            const tabId = button.getAttribute('data-tab');
            this.tabs[tabId] = button;
            
            // Add click event listener
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(tabId);
            });
            
            // Add keyboard navigation support
            button.addEventListener('keydown', (e) => {
                this.handleKeyboardNavigation(e, tabId);
            });
        });
        
        tabContents.forEach(content => {
            const tabId = content.getAttribute('data-tab-content');
            this.tabContents[tabId] = content;
        });
        
        // Restore saved tab state or default to overview
        this.restoreTabState();
        
        console.log('Tab navigation initialized');
    }

    /**
     * Switch to a specific tab
     * @param {string} tabId - The ID of the tab to switch to
     */
    switchTab(tabId) {
        console.log(`Switching to tab: ${tabId}`);
        
        // Validate tab exists
        if (!this.tabs[tabId] || !this.tabContents[tabId]) {
            console.error(`Tab ${tabId} not found`);
            return;
        }
        
        // Remove active state from all tabs
        Object.values(this.tabs).forEach(tab => {
            tab.classList.remove('active');
            tab.setAttribute('aria-selected', 'false');
        });
        
        // Hide all tab contents
        Object.values(this.tabContents).forEach(content => {
            content.classList.remove('active');
            content.style.display = 'none';
        });
        
        // Activate selected tab
        this.tabs[tabId].classList.add('active');
        this.tabs[tabId].setAttribute('aria-selected', 'true');
        
        // Show selected content
        this.tabContents[tabId].classList.add('active');
        this.tabContents[tabId].style.display = 'block';
        
        // Update current tab
        this.currentTab = tabId;
        
        // Save tab state
        this.saveTabState();
        
        // Trigger custom event for other components to react
        const event = new CustomEvent('tabChanged', { 
            detail: { tabId: tabId } 
        });
        document.dispatchEvent(event);
    }

    /**
     * Save current tab state to sessionStorage
     * Persists tab selection across page interactions
     */
    saveTabState() {
        try {
            sessionStorage.setItem('activeTab', this.currentTab);
            console.log(`Tab state saved: ${this.currentTab}`);
        } catch (e) {
            console.warn('Failed to save tab state:', e);
        }
    }

    /**
     * Restore tab state from sessionStorage
     * Falls back to 'overview' if no saved state exists
     */
    restoreTabState() {
        try {
            const savedTab = sessionStorage.getItem('activeTab');
            const tabToActivate = savedTab && this.tabs[savedTab] ? savedTab : 'overview';
            
            console.log(`Restoring tab state: ${tabToActivate}`);
            this.switchTab(tabToActivate);
        } catch (e) {
            console.warn('Failed to restore tab state:', e);
            this.switchTab('overview');
        }
    }

    /**
     * Handle keyboard navigation for accessibility
     * Supports Arrow keys and Home/End keys
     * @param {KeyboardEvent} event - The keyboard event
     * @param {string} currentTabId - The ID of the currently focused tab
     */
    handleKeyboardNavigation(event, currentTabId) {
        const tabIds = Object.keys(this.tabs);
        const currentIndex = tabIds.indexOf(currentTabId);
        
        let targetIndex = currentIndex;
        
        switch (event.key) {
            case 'ArrowLeft':
                // Move to previous tab
                targetIndex = currentIndex > 0 ? currentIndex - 1 : tabIds.length - 1;
                event.preventDefault();
                break;
                
            case 'ArrowRight':
                // Move to next tab
                targetIndex = currentIndex < tabIds.length - 1 ? currentIndex + 1 : 0;
                event.preventDefault();
                break;
                
            case 'Home':
                // Move to first tab
                targetIndex = 0;
                event.preventDefault();
                break;
                
            case 'End':
                // Move to last tab
                targetIndex = tabIds.length - 1;
                event.preventDefault();
                break;
                
            case 'Enter':
            case ' ':
                // Activate current tab
                this.switchTab(currentTabId);
                event.preventDefault();
                break;
                
            default:
                return;
        }
        
        // Focus and switch to target tab
        if (targetIndex !== currentIndex) {
            const targetTabId = tabIds[targetIndex];
            this.tabs[targetTabId].focus();
            this.switchTab(targetTabId);
        }
    }

    /**
     * Get the currently active tab ID
     * @returns {string} The ID of the active tab
     */
    getCurrentTab() {
        return this.currentTab;
    }
}

// Export for use in other modules
window.TabNavigation = TabNavigation;
