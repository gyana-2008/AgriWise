/**
 * 🌾 AGRIWISE AI - Universal Navigation & Demo Journey Controller
 * Injects responsive top banner, sticky navbar, footer, role selector, and mobile drawer.
 */

const AgriNav = {
  init() {
    this.renderDemoBanner();
    this.renderHeader();
    this.renderMobileBottomNav();
    this.renderFooter();
    this.highlightActivePage();
  },

  getCurrentPath() {
    const path = window.location.pathname.replace(/^\/|\/$/g, '').toLowerCase();
    return path || 'index';
  },

  renderDemoBanner() {
    const currentPath = this.getCurrentPath();
    const steps = window.AgriState.demoJourneySteps;
    const currentStepIndex = steps.findIndex(s => s.route.includes(currentPath));
    const currentStepNum = currentStepIndex >= 0 ? currentStepIndex + 1 : 1;
    const nextStep = steps[currentStepIndex + 1] || steps[0];

    const bannerHtml = `
      <div class="demo-journey-banner">
        <div class="demo-banner-left">
          <span class="demo-badge-pulse">🚀 Demo Journey</span>
          <span class="banner-text-long">Hackathon Evaluator Guided Tour:</span>
          <span>Step ${currentStepNum} of ${steps.length}: <strong>${steps[currentStepIndex >= 0 ? currentStepIndex : 0].title}</strong></span>
        </div>
        <div class="demo-banner-actions">
          <a href="${nextStep.route}" class="btn-demo-action">
            <span>Next Step: ${nextStep.title.split('.')[1] || 'Next'}</span>
            <span>➔</span>
          </a>
          <button onclick="AgriNav.showJourneyModal()" class="btn-demo-action" style="background: rgba(0,0,0,0.25);">
            <span>📑 All Steps</span>
          </button>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('afterbegin', bannerHtml);
  },

  renderHeader() {
    const currentRole = window.AgriState.currentRole;

    // Role-specific navigation links
    let navLinksHtml = '';
    if (currentRole === 'DEALER') {
      navLinksHtml = `
        <a href="/dealer-dashboard" class="nav-link" data-route="dealer-dashboard">📊 Dealer Overview</a>
        <a href="/fertilizer-market" class="nav-link" data-route="fertilizer-market">🛒 Inventory</a>
        <a href="/crop-demand" class="nav-link" data-route="crop-demand">📈 Demand Radar</a>
        <a href="/payment" class="nav-link" data-route="payment">💳 Payments & POS</a>
        <a href="/farmer-orders" class="nav-link" data-route="farmer-orders">📦 Orders</a>
      `;
    } else if (currentRole === 'TRANSPORTER') {
      navLinksHtml = `
        <a href="/transport-dashboard" class="nav-link" data-route="transport-dashboard">🚛 Fleet Overview</a>
        <a href="/transport-marketplace" class="nav-link" data-route="transport-marketplace">📍 Available Trips</a>
        <a href="/payment" class="nav-link" data-route="payment">💳 Freight Ledger</a>
        <a href="/crop-shortage" class="nav-link" data-route="crop-shortage">🗺 Interstate Routes</a>
        <a href="/farmer-orders" class="nav-link" data-route="farmer-orders">📋 Bookings</a>
      `;
    } else if (currentRole === 'BUYER') {
      navLinksHtml = `
        <a href="/buyer-dashboard" class="nav-link" data-route="buyer-dashboard">🏢 Procurement Hub</a>
        <a href="/buyer-marketplace" class="nav-link" data-route="buyer-marketplace">🌾 Tenders</a>
        <a href="/payment" class="nav-link" data-route="payment">💳 Escrow Vault</a>
        <a href="/market-intelligence" class="nav-link" data-route="market-intelligence">💹 Mandi Prices</a>
        <a href="/crop-demand" class="nav-link" data-route="crop-demand">📊 Supply Pipeline</a>
      `;
    } else if (currentRole === 'ADMIN') {
      navLinksHtml = `
        <a href="/admin" class="nav-link" data-route="admin">⚙ System Admin</a>
        <a href="/payment" class="nav-link" data-route="payment">💳 Payments Engine</a>
        <a href="/dashboard" class="nav-link" data-route="dashboard">🌾 Farmer View</a>
        <a href="/market-intelligence" class="nav-link" data-route="market-intelligence">💹 Mandi Intelligence</a>
        <a href="/crop-shortage" class="nav-link" data-route="crop-shortage">🗺 Deficit Map</a>
      `;
    } else {
      // Default FARMER Links
      navLinksHtml = `
        <a href="/dashboard" class="nav-link" data-route="dashboard">🌾 Dashboard</a>
        <a href="/farm-analysis" class="nav-link" data-route="farm-analysis">🔬 Soil & Water</a>
        <a href="/crop-recommendation" class="nav-link" data-route="crop-recommendation">🌱 Crops</a>
        <a href="/fertilizer-market" class="nav-link" data-route="fertilizer-market">🛒 Inputs</a>
        <a href="/market-intelligence" class="nav-link" data-route="market-intelligence">💹 Markets</a>
        <a href="/crop-shortage" class="nav-link" data-route="crop-shortage">🗺 Shortages</a>
        <a href="/farm-to-market" class="nav-link" data-route="farm-to-market">🚜 Farm-to-Market</a>
        <a href="/payment" class="nav-link" data-route="payment">💳 Payments</a>
        <a href="/ai-assistant" class="nav-link" data-route="ai-assistant">🤖 AI Advisor</a>
      `;
    }

    const headerHtml = `
      <header class="main-header">
        <div class="container nav-container">
          <a href="/" class="brand-logo">
            <div class="brand-icon">🌾</div>
            <span>AGRIWISE<span class="ai-tag">AI</span></span>
          </a>

          <nav class="nav-links">
            ${navLinksHtml}
          </nav>

          <div class="header-actions">
            <!-- Role Switcher -->
            <div class="role-badge-selector" title="Switch User Role">
              <button class="role-pill ${currentRole === 'FARMER' ? 'active' : ''}" onclick="AgriState.setRole('FARMER')">Farmer</button>
              <button class="role-pill ${currentRole === 'DEALER' ? 'active' : ''}" onclick="AgriState.setRole('DEALER')">Dealer</button>
              <button class="role-pill ${currentRole === 'TRANSPORTER' ? 'active' : ''}" onclick="AgriState.setRole('TRANSPORTER')">Transport</button>
              <button class="role-pill ${currentRole === 'BUYER' ? 'active' : ''}" onclick="AgriState.setRole('BUYER')">Buyer</button>
              <button class="role-pill ${currentRole === 'ADMIN' ? 'active' : ''}" onclick="AgriState.setRole('ADMIN')">Admin</button>
            </div>

            <!-- Language Switcher -->
            <select id="langSelect" class="lang-select" onchange="AgriState.setLang(this.value)">
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
            </select>

            <!-- Notifications Button -->
            <a href="/notifications" class="notif-bell-btn" title="View Agricultural & Weather Notifications">
              🔔
              <span class="notif-badge-count">3</span>
            </a>
          </div>
        </div>
      </header>
    `;

    document.querySelector('.demo-journey-banner').insertAdjacentHTML('afterend', headerHtml);
  },

  renderMobileBottomNav() {
    const mobileNavHtml = `
      <div class="mobile-bottom-nav">
        <a href="/dashboard" class="mobile-nav-item" data-route="dashboard">
          <span class="mobile-nav-icon">🌾</span>
          <span>Home</span>
        </a>
        <a href="/crop-recommendation" class="mobile-nav-item" data-route="crop-recommendation">
          <span class="mobile-nav-icon">🌱</span>
          <span>Crops</span>
        </a>
        <a href="/weather" class="mobile-nav-item" data-route="weather">
          <span class="mobile-nav-icon">⛅</span>
          <span>Weather</span>
        </a>
        <a href="/market-intelligence" class="mobile-nav-item" data-route="market-intelligence">
          <span class="mobile-nav-icon">💹</span>
          <span>Mandi</span>
        </a>
        <a href="/ai-assistant" class="mobile-nav-item" data-route="ai-assistant">
          <span class="mobile-nav-icon">🤖</span>
          <span>AI Help</span>
        </a>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', mobileNavHtml);
  },

  renderFooter() {
    const footerHtml = `
      <footer class="main-footer">
        <div class="container">
          <div class="footer-grid">
            <div class="footer-col">
              <div class="brand-logo" style="color: #fff; margin-bottom: 1rem;">
                <div class="brand-icon">🌾</div>
                <span>AGRIWISE<span class="ai-tag">AI</span></span>
              </div>
              <p style="color: #94a3b8; font-size: 0.9rem; max-width: 380px;">
                Intelligent Crop, Seed, Input & Market Decision Platform designed for Indian agriculture. Empowering farmers with AI recommendations, live weather advisories, and direct mandi linkages.
              </p>
              <div style="display: flex; gap: 0.75rem; margin-top: 1.25rem;">
                <span class="badge badge-emerald">ICAR Agronomic Aligned</span>
                <span class="badge badge-blue">Open-Meteo Live</span>
              </div>
            </div>

            <div class="footer-col">
              <h5>Farmer Decision Suite</h5>
              <ul>
                <li><a href="/farm-profile">Farm Profile & GPS</a></li>
                <li><a href="/farm-analysis">Soil & Water Health Score</a></li>
                <li><a href="/crop-recommendation">Crop Recommendation Engine</a></li>
                <li><a href="/seed-recommendation">Certified Seed Comparison</a></li>
                <li><a href="/cultivation-plan">Day 0 to Harvest Timeline</a></li>
                <li><a href="/fertilizer-recommendation">N-P-K Fertilizer Plan</a></li>
              </ul>
            </div>

            <div class="footer-col">
              <h5>Market & Logistics</h5>
              <ul>
                <li><a href="/fertilizer-market">Nearby Input Dealers</a></li>
                <li><a href="/payment">Agri Payment Gateway & Escrow</a></li>
                <li><a href="/market-intelligence">Bloomberg Mandi Dashboard</a></li>
                <li><a href="/crop-shortage">National Deficit & Shortage Map</a></li>
                <li><a href="/buyer-marketplace">Verified Wholesale Millers</a></li>
                <li><a href="/transport-marketplace">Local Truck Transport Fleet</a></li>
                <li><a href="/profit-estimator">Multi-Scenario ROI Calculator</a></li>
              </ul>
            </div>

            <div class="footer-col">
              <h5>Platform & System</h5>
              <ul>
                <li><a href="/ai-assistant">Conversational AI Agronomist</a></li>
                <li><a href="/farm-calendar">Seasonal Task Calendar</a></li>
                <li><a href="/notifications">Severe Weather Alerts</a></li>
                <li><a href="/farm-report">Personalized Farm Dossier</a></li>
                <li><a href="/admin">Admin Weight Configuration</a></li>
                <li><a href="/login">Role Authentication</a></li>
              </ul>
            </div>
          </div>

          <div class="footer-bottom">
            <div>
              © 2026 AGRIWISE AI Technologies Pvt Ltd. All rights reserved. Made with ❤️ for Indian Farmers.
            </div>
            <div style="font-size: 0.8rem; color: #64748b;">
              ⚠️ Agronomic guidance based on ICAR guidelines. Local agricultural extension specialists and soil testing laboratories take precedence.
            </div>
          </div>
        </div>
      </footer>
    `;
    document.body.insertAdjacentHTML('beforeend', footerHtml);
  },

  highlightActivePage() {
    const current = this.getCurrentPath();
    document.querySelectorAll('.nav-link, .mobile-nav-item').forEach(el => {
      const route = el.getAttribute('data-route');
      if (route && (route === current || current.includes(route))) {
        el.classList.add('active');
      }
    });
  },

  showJourneyModal() {
    const steps = window.AgriState.demoJourneySteps;
    const currentPath = this.getCurrentPath();

    let itemsHtml = steps.map((s, idx) => {
      const isCurrent = s.route.includes(currentPath);
      return `
        <a href="${s.route}" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: ${isCurrent ? '#ecfdf5' : '#fff'}; border: 1px solid ${isCurrent ? '#10b981' : '#e2e8f0'}; border-radius: 8px; margin-bottom: 8px; text-decoration: none; color: inherit;">
          <div>
            <div style="font-weight: 700; font-size: 0.92rem; color: ${isCurrent ? '#047857' : '#0f172a'};">${s.title}</div>
            <div style="font-size: 0.8rem; color: #64748b;">${s.desc}</div>
          </div>
          <span style="color: #059669; font-weight: 700;">➔</span>
        </a>
      `;
    }).join('');

    const modalHtml = `
      <div id="journeyModal" style="position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 2000; display: flex; align-items: center; justify-content: center; padding: 1.5rem;" onclick="if(event.target.id === 'journeyModal') this.remove();">
        <div style="background: #fff; border-radius: 16px; max-width: 540px; width: 100%; max-height: 85vh; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.2);">
          <div style="padding: 1.25rem 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between; background: #064e3b; color: #fff;">
            <div>
              <h3 style="font-size: 1.2rem; color: #fff; margin-bottom: 2px;">🌾 AgriWise AI End-to-End Journey</h3>
              <p style="font-size: 0.82rem; color: #a7f3d0; margin-bottom: 0;">Complete 15-step Farm-to-Market Evaluation Workflow</p>
            </div>
            <button onclick="document.getElementById('journeyModal').remove()" style="background: transparent; border: none; color: #fff; font-size: 1.5rem; cursor: pointer;">&times;</button>
          </div>
          <div style="padding: 1.25rem; overflow-y: auto; flex: 1;">
            ${itemsHtml}
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
  }
};

window.AgriNav = AgriNav;
document.addEventListener('DOMContentLoaded', () => {
  AgriNav.init();
});
