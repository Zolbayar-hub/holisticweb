// auth.js: Handles login, logout, and register API calls

async function register(username, email, password) {
    const response = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    });
    return response.json();
}

async function login(email, password) {
    const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    return response.json();
}

async function logout() {
    const response = await fetch('/api/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
}

async function checkAuthStatus() {
    const response = await fetch('/api/user/status', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
}

const authModalHtml = `
<div id="auth-modal" style="display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.4);z-index:1000;justify-content:center;align-items:center;">
  <div style="background:#fff;padding:32px 24px;border-radius:8px;min-width:360px;box-shadow:0 2px 16px rgba(0,0,0,0.2);position:relative;">
    <button id="close-auth-modal" style="position:absolute;top:8px;right:8px;background:none;border:none;font-size:1.2rem;cursor:pointer;">&times;</button>
    
    <div style="display:flex;margin-bottom:20px;border-bottom:1px solid #e1e5e9;">
      <button id="login-tab" class="auth-tab" style="flex:1;padding:12px;background:none;border:none;border-bottom:2px solid #0066ff;color:#0066ff;font-weight:600;cursor:pointer;">Login</button>
      <button id="register-tab" class="auth-tab" style="flex:1;padding:12px;background:none;border:none;border-bottom:2px solid transparent;color:#666;font-weight:600;cursor:pointer;">Register</button>
    </div>

    <div id="login-section">
      <h2 style="margin-bottom:16px;color:#333;">Welcome Back</h2>
      <form id="login-form">
        <input type="text" id="login-username" placeholder="Email" required style="width:100%;margin-bottom:12px;padding:12px;border:1px solid #ddd;border-radius:4px;font-size:14px;" />
        <input type="password" id="login-password" placeholder="Password" required style="width:100%;margin-bottom:16px;padding:12px;border:1px solid #ddd;border-radius:4px;font-size:14px;" />
        <button type="submit" style="width:100%;background:#0066ff;color:#fff;padding:12px 0;border:none;border-radius:4px;font-size:1rem;cursor:pointer;font-weight:600;">Sign In</button>
      </form>
      <div id="login-message" style="margin-top:12px;color:#e63946;font-size:14px;"></div>
    </div>

    <div id="register-section" style="display:none;">
      <h2 style="margin-bottom:16px;color:#333;">Create Account</h2>
      <form id="register-form">
        <input type="text" id="register-username" placeholder="Choose Username" required style="width:100%;margin-bottom:12px;padding:12px;border:1px solid #ddd;border-radius:4px;font-size:14px;" />
        <input type="email" id="register-email" placeholder="Email Address" required style="width:100%;margin-bottom:12px;padding:12px;border:1px solid #ddd;border-radius:4px;font-size:14px;" />
        <input type="password" id="register-password" placeholder="Create Password" required style="width:100%;margin-bottom:12px;padding:12px;border:1px solid #ddd;border-radius:4px;font-size:14px;" />
        <input type="password" id="register-confirm-password" placeholder="Confirm Password" required style="width:100%;margin-bottom:16px;padding:12px;border:1px solid #ddd;border-radius:4px;font-size:14px;" />
        <button type="submit" style="width:100%;background:#28a745;color:#fff;padding:12px 0;border:none;border-radius:4px;font-size:1rem;cursor:pointer;font-weight:600;">Create Account</button>
      </form>
      <div id="register-message" style="margin-top:12px;color:#e63946;font-size:14px;"></div>
    </div>
  </div>
</div>
`;

// Initialize auth button - can be called externally
function initializeAuthButton() {
  // Remove existing button if present to avoid duplicates
  const existingBtn = document.getElementById('auth-btn');
  if (existingBtn) {
    existingBtn.remove();
  }
  
  // Try to find either container (base.html, tutorial.html, or content header)
  console.log('Looking for auth button containers...');
  let containerHeader = document.getElementById('login-btn-container');
  let containerSidebar = document.getElementById('login-btn-sidebar');
  let containerContent = document.getElementById('content-login-btn-container');
  console.log('Header container:', containerHeader);
  console.log('Sidebar container:', containerSidebar);
  console.log('Content container:', containerContent);
  
  // Prefer content container, then header, then sidebar
  let sidebarBtnContainer = containerContent || containerHeader || containerSidebar;
  
  if (sidebarBtnContainer) {
    console.log('Using container:', sidebarBtnContainer.id);
    let btn = document.createElement('button');
    btn.id = 'auth-btn';
    btn.textContent = 'Login'; // Default state
      // Style differently based on container location
    if (sidebarBtnContainer.id === 'content-login-btn-container') {
      // Content header styling - matches share button with responsive design
      btn.style.cssText = 'background:#0066ff;color:#fff;padding:10px 20px;border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.2s;box-shadow:0 2px 4px rgba(0,102,255,0.2);width:100%;display:block;text-align:center;';
    } else if (sidebarBtnContainer.id === 'login-btn-container') {
      // Header bar styling - more compact
      btn.style.cssText = 'display:inline-block;background:#0066ff;color:#fff;padding:8px 16px;border:none;border-radius:4px;font-size:0.9rem;cursor:pointer;font-weight:500;box-shadow:0 2px 4px rgba(0,102,255,0.2);';
    } else {
      // Sidebar styling - full width
      btn.style.cssText = 'display:block;width:100%;margin:0 0 18px 0;background:#0066ff;color:#fff;padding:8px 18px;border:none;border-radius:4px;font-size:1rem;cursor:pointer;';
    }
    
    btn.onclick = showLoginModal; // Default action
    sidebarBtnContainer.appendChild(btn);
    console.log('Button created and added to container');
    
    // Initialize button based on auth status (async)
    updateAuthButton().catch(error => {
      console.error('Failed to update auth button:', error);
      // Button already has default state, so no need to do anything
    });
  } else {
    console.warn('Login button container not found (tried content-login-btn-container, login-btn-container and login-btn-sidebar)');
  }
  
  // Also initialize mobile auth button if it exists
  initializeMobileAuthButton();
}

// Initialize mobile auth button (for hamburger menu)
function initializeMobileAuthButton() {
  const mobileAuthBtn = document.getElementById('mobile-auth-btn');
  if (mobileAuthBtn) {
    updateMobileAuthButton().catch(error => {
      console.error('Failed to update mobile auth button:', error);
    });
  }
}

async function updateMobileAuthButton() {
  const mobileAuthBtn = document.getElementById('mobile-auth-btn');
  if (!mobileAuthBtn) return;
  
  try {
    const status = await checkAuthStatus();
    if (status.logged_in) {
      mobileAuthBtn.textContent = 'Logout';
      mobileAuthBtn.classList.add('logout-btn');
      mobileAuthBtn.onclick = async () => {
        try {
          const res = await logout();
          if (res.message) {
            location.reload();
          }
        } catch (error) {
          console.error('Logout error:', error);
        }
      };
    } else {
      mobileAuthBtn.textContent = 'Login';
      mobileAuthBtn.classList.remove('logout-btn');
      mobileAuthBtn.onclick = showLoginModal;
    }
  } catch (error) {
    console.error('Error checking auth status:', error);
    mobileAuthBtn.textContent = 'Login';
    mobileAuthBtn.classList.remove('logout-btn');
    mobileAuthBtn.onclick = showLoginModal;
  }
}

async function updateAuthButton() {
  const btn = document.getElementById('auth-btn');
  if (!btn) {
    console.warn('Auth button not found when trying to update');
    return;
  }

  const container = btn.parentElement;
  const isHeaderButton = container && container.id === 'login-btn-container';
  const isContentButton = container && container.id === 'content-login-btn-container';

  try {
    const status = await checkAuthStatus();
    if (status.logged_in) {
      btn.textContent = 'Logout';
      btn.classList.add('logout-btn');
        if (isContentButton) {
        // Content header styling - matches share button with responsive design
        btn.style.cssText = 'background:#dc3545;color:#fff;padding:10px 20px;border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.2s;box-shadow:0 2px 4px rgba(220,53,69,0.2);width:100%;display:block;text-align:center;';
      } else if (isHeaderButton) {
        btn.style.cssText = 'display:inline-block;background:#dc3545;color:#fff;padding:8px 16px;border:none;border-radius:4px;font-size:0.9rem;cursor:pointer;font-weight:500;box-shadow:0 2px 4px rgba(220,53,69,0.2);';
      } else {
        btn.style.background = '#dc3545';
      }
      btn.onclick = handleLogout;
      
      console.log('Button updated to Logout state');
    } else {
      btn.textContent = 'Login';
      btn.classList.remove('logout-btn');
      
      if (isContentButton) {
        // Content header styling - matches share button
        btn.style.cssText = 'background:#0066ff;color:#fff;padding:10px 20px;border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.2s;box-shadow:0 2px 4px rgba(0,102,255,0.2);';
      } else if (isHeaderButton) {
        btn.style.cssText = 'display:inline-block;background:#0066ff;color:#fff;padding:8px 16px;border:none;border-radius:4px;font-size:0.9rem;cursor:pointer;font-weight:500;box-shadow:0 2px 4px rgba(0,102,255,0.2);';
      } else {
        btn.style.background = '#0066ff';
      }
      btn.onclick = showLoginModal;
      console.log('Button updated to Login state');
    }
  } catch (error) {
    console.error('Error checking auth status:', error);
    // Ensure button is in default login state if there's an error
    btn.textContent = 'Login';
    if (isHeaderButton) {
      btn.style.cssText = 'display:inline-block;background:#0066ff;color:#fff;padding:8px 16px;border:none;border-radius:4px;font-size:0.9rem;cursor:pointer;font-weight:500;box-shadow:0 2px 4px rgba(0,102,255,0.2);';
    } else {
      btn.style.background = '#0066ff';
    }
    btn.onclick = showLoginModal;
  }
  
  // Also update mobile button if it exists
  updateMobileAuthButton();
}

async function handleLogout() {
  try {
    const res = await logout();
    if (res.message) {
      location.reload();
    }
  } catch (error) {
    console.error('Logout error:', error);
  }
}

function showLoginModal() {
  const authModal = document.getElementById('auth-modal');
  const loginMessage = document.getElementById('login-message');
  const registerMessage = document.getElementById('register-message');
  
  authModal.style.display = 'flex';
  loginMessage.textContent = '';
  registerMessage.textContent = '';
  showLoginTab();
}

function hideLoginModal() {
  const authModal = document.getElementById('auth-modal');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const loginMessage = document.getElementById('login-message');
  const registerMessage = document.getElementById('register-message');
  
  authModal.style.display = 'none';
  loginForm.reset();
  registerForm.reset();
  loginMessage.textContent = '';
  registerMessage.textContent = '';
}

function showLoginTab() {
  const loginTab = document.getElementById('login-tab');
  const registerTab = document.getElementById('register-tab');
  const loginSection = document.getElementById('login-section');
  const registerSection = document.getElementById('register-section');
  
  loginTab.style.borderBottomColor = '#0066ff';
  loginTab.style.color = '#0066ff';
  registerTab.style.borderBottomColor = 'transparent';
  registerTab.style.color = '#666';
  loginSection.style.display = 'block';
  registerSection.style.display = 'none';
}

function showRegisterTab() {
  const loginTab = document.getElementById('login-tab');
  const registerTab = document.getElementById('register-tab');
  const loginSection = document.getElementById('login-section');
  const registerSection = document.getElementById('register-section');
  
  registerTab.style.borderBottomColor = '#0066ff';
  registerTab.style.color = '#0066ff';
  loginTab.style.borderBottomColor = 'transparent';
  loginTab.style.color = '#666';
  loginSection.style.display = 'none';
  registerSection.style.display = 'block';
}

function setupModalEventListeners() {
  const authModal = document.getElementById('auth-modal');
  const closeAuthModal = document.getElementById('close-auth-modal');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const loginMessage = document.getElementById('login-message');
  const registerMessage = document.getElementById('register-message');
  const loginTab = document.getElementById('login-tab');
  const registerTab = document.getElementById('register-tab');

  closeAuthModal.onclick = hideLoginModal;
  authModal.onclick = function(e) { if (e.target === authModal) hideLoginModal(); };
  loginTab.onclick = showLoginTab;
  registerTab.onclick = showRegisterTab;
  
  loginForm.onsubmit = async function(e) {
    e.preventDefault();
    const email = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
      const res = await login(email, password);
      if (res.message) {
        hideLoginModal();
        await updateAuthButton(); // Update button after successful login
        await updateMobileAuthButton(); // Also update mobile button
        // After login success
        window.location.reload();
      } else {
        loginMessage.textContent = res.error || 'Login failed';
      }
    } catch (error) {
      loginMessage.textContent = 'Network error. Please try again.';
    }
  };

  registerForm.onsubmit = async function(e) {
    e.preventDefault();
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;

    if (password !== confirmPassword) {
      registerMessage.textContent = 'Passwords do not match';
      return;
    }

    if (password.length < 6) {
      registerMessage.textContent = 'Password must be at least 6 characters long';
      return;
    }

    try {
      const res = await register(username, email, password);
      if (res.message) {
        registerMessage.style.color = '#28a745';
        registerMessage.textContent = 'Account created successfully! You can now login.';
        setTimeout(() => {
          showLoginTab();
          document.getElementById('login-username').value = email;
        }, 1500);
      } else {
        registerMessage.style.color = '#e63946';
        registerMessage.textContent = res.error || 'Registration failed';
      }
    } catch (error) {
      registerMessage.style.color = '#e63946';
      registerMessage.textContent = 'Network error. Please try again.';
    }
  };
}

// Make functions available globally
window.initializeAuthButton = initializeAuthButton;
window.initializeMobileAuthButton = initializeMobileAuthButton;
window.updateMobileAuthButton = updateMobileAuthButton;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize modal HTML
  if (!document.getElementById('auth-modal')) {
    document.body.insertAdjacentHTML('beforeend', authModalHtml);
    setupModalEventListeners();
  }

  // Hamburger menu dropdown logic
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobile-menu');
  hamburger.addEventListener('click', function(e) {
    e.stopPropagation();
    mobileMenu.classList.toggle('active');
  });
  // Close dropdown if clicking outside
  document.addEventListener('click', function(e) {
    if (mobileMenu.classList.contains('active')) {
      if (!mobileMenu.contains(e.target) && e.target !== hamburger) {
        mobileMenu.classList.remove('active');
      }
    }
  });

  // Initialize auth button
  initializeAuthButton();
});
