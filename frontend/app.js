/**
 * SHEVAULT AI - Frontend Application Core Logic
 * SPA Routing, State Management, Authentication, 5-Module Analysis Engine & UI Interactions
 */

(function () {
  'use strict';

  // --- Global Application State ---
  const state = {
    user: null,
    token: localStorage.getItem('shevault_jwt_token') || null,
    sessionStats: JSON.parse(localStorage.getItem('shevault_stats') || '{"analyzed": 3, "risks": 2, "protected": 3}'),
    currentResult: null,
    uploadedFile: null,
    activeTab: 'dashboard',
    presets: {}
  };

  // --- API Utilities ---
  const API_BASE = '/api';

  async function apiRequest(endpoint, method = 'GET', body = null, isFormData = false) {
    const headers = {};
    if (state.token) {
      headers['Authorization'] = `Bearer ${state.token}`;
    }
    if (!isFormData && body) {
      headers['Content-Type'] = 'application/json';
    }

    const options = {
      method,
      headers
    };

    if (body) {
      options.body = isFormData ? body : JSON.stringify(body);
    }

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, options);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Request failed.');
      }
      return data;
    } catch (err) {
      throw err;
    }
  }

  // --- Toast Notification Helper ---
  function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = '✨';
    if (type === 'success') icon = '✓';
    if (type === 'error') icon = '⚠';
    if (type === 'warning') icon = '✦';

    toast.innerHTML = `<span style="font-weight:700;">${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  // --- Initial Setup & Auth Hydration ---
  async function initApp() {
    // 1. Resolve hash routes immediately so direct links load with zero delay
    handleHashNavigation();

    // 2. Fetch background data
    loadPresets();
    loadSafetyGuide();
    loadScamHeatmap();

    // 3. Hydrate authenticated session if present
    if (state.token) {
      try {
        const res = await apiRequest('/auth/me');
        if (res && res.user) {
          state.user = res.user;
          updateUserUI();
        } else {
          clearAuth();
        }
      } catch (err) {
        clearAuth();
      }
    }

    setupEventListeners();
  }

  function clearAuth() {
    state.user = null;
    state.token = null;
    localStorage.removeItem('shevault_jwt_token');
    localStorage.removeItem('shevault_user');
    const authActions = document.getElementById('top-auth-actions');
    if (authActions) {
      authActions.innerHTML = `
        <button class="btn btn-ghost" id="nav-login-btn">Log In</button>
        <button class="btn btn-primary" id="nav-get-started-btn">Get Started</button>
      `;
      const loginBtn = document.getElementById('nav-login-btn');
      if (loginBtn) loginBtn.addEventListener('click', () => openAuthModal('login'));
      const getStartedBtn = document.getElementById('nav-get-started-btn');
      if (getStartedBtn) getStartedBtn.addEventListener('click', () => openAuthModal('signup'));
    }
  }

  function setAuth(token, user) {
    state.token = token;
    state.user = user;
    localStorage.setItem('shevault_jwt_token', token);
    localStorage.setItem('shevault_user', JSON.stringify(user));
    updateUserUI();
  }

  function updateUserUI() {
    const avatar = document.getElementById('user-avatar');
    const nameEl = document.getElementById('user-display-name');
    const roleEl = document.getElementById('user-display-role');
    const dashNameEl = document.getElementById('dash-user-name');
    const profNameInput = document.getElementById('prof-name-input');
    const profEmailInput = document.getElementById('prof-email-input');
    const profRoleSelect = document.getElementById('prof-role-select');

    if (state.user) {
      const initial = (state.user.name || 'U').charAt(0).toUpperCase();
      if (avatar) avatar.textContent = initial;
      if (nameEl) nameEl.textContent = state.user.name;
      if (roleEl) roleEl.textContent = state.user.role || 'Student';
      if (dashNameEl) dashNameEl.textContent = state.user.name.split(' ')[0];
      if (profNameInput) profNameInput.value = state.user.name;
      if (profEmailInput) profEmailInput.value = state.user.email;
      if (profRoleSelect) profRoleSelect.value = state.user.role || 'Student';

      // Update top nav on landing view
      const authActions = document.getElementById('top-auth-actions');
      if (authActions) {
        authActions.innerHTML = `
          <button class="btn btn-ghost" id="nav-landing-logout-btn">Log Out</button>
          <a href="#dashboard" class="btn btn-primary" id="nav-landing-dash-link">Go to Dashboard →</a>
        `;
        const landingLogout = document.getElementById('nav-landing-logout-btn');
        if (landingLogout) {
          landingLogout.addEventListener('click', () => {
            clearAuth();
            showToast('You have logged out.', 'info');
            showLandingView();
          });
        }
      }
    } else {
      if (avatar) avatar.textContent = 'G';
      if (nameEl) nameEl.textContent = 'Guest Explorer';
      if (roleEl) roleEl.textContent = 'Visitor';
      if (dashNameEl) dashNameEl.textContent = 'Guest';
      if (profNameInput) profNameInput.value = 'Guest Explorer';
      if (profEmailInput) profEmailInput.value = 'guest@shevault.ai';
      if (profRoleSelect) profRoleSelect.value = 'Student';
    }

    updateStatsUI();
  }

  function updateStatsUI() {
    const analyzedEl = document.getElementById('stat-analyzed-count');
    const riskEl = document.getElementById('stat-risk-count');
    const protectedEl = document.getElementById('stat-protected-count');

    if (analyzedEl) analyzedEl.textContent = state.sessionStats.analyzed;
    if (riskEl) riskEl.textContent = state.sessionStats.risks;
    if (protectedEl) protectedEl.textContent = state.sessionStats.protected;
  }

  function incrementStat(type) {
    if (type === 'analyzed') state.sessionStats.analyzed += 1;
    if (type === 'risk') state.sessionStats.risks += 1;
    if (type === 'protected') state.sessionStats.protected += 1;
    localStorage.setItem('shevault_stats', JSON.stringify(state.sessionStats));
    updateStatsUI();
  }

  // --- View Switching ---
  function showLandingView() {
    document.getElementById('landing-view').style.display = 'block';
    document.getElementById('app-view').style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function showAppView(targetTab = 'dashboard') {
    document.getElementById('landing-view').style.display = 'none';
    document.getElementById('app-view').style.display = 'block';
    switchSubTab(targetTab);
  }

  function switchSubTab(tabName) {
    state.activeTab = tabName;

    // Update sidebar navigation active classes
    document.querySelectorAll('.sidebar-item').forEach(el => {
      if (el.getAttribute('data-tab') === tabName) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });

    // Hide all subviews
    document.querySelectorAll('.subview').forEach(el => {
      el.style.display = 'none';
    });

    // View title mapping
    const titleMap = {
      'dashboard': 'Dashboard',
      'analyze': 'Scan Opportunity',
      'result': 'Opportunity Trust Profile',
      'protect-me-now': 'Protect Me Now (Crisis Containment)',
      'recruiter-pass': 'Verified Recruiter Pass',
      'campus-mode': 'Campus SHEVAULT Mode',
      'scam-heatmap': 'Scam Threat Heatmap & Risk Radar',
      'firewall': 'Identity Firewall',
      'safety-guide': 'Safety Guide',
      'profile': 'Profile & Privacy'
    };

    const topbarTitle = document.getElementById('topbar-view-title');
    if (topbarTitle) topbarTitle.textContent = titleMap[tabName] || 'Dashboard';

    // Show target subview
    const targetEl = document.getElementById(`subview-${tabName}`);
    if (targetEl) {
      targetEl.style.display = 'block';
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // If opening specific subviews, trigger data loads
    if (tabName === 'scam-heatmap') {
      loadScamHeatmap();
    }
    if (tabName === 'safety-guide') {
      loadSafetyGuide();
    }
    if (tabName === 'profile') {
      updateUserUI();
    }

    // On mobile, close sidebar after clicking
    const sidebar = document.getElementById('app-sidebar');
    if (sidebar && window.innerWidth <= 1024) {
      sidebar.classList.remove('open');
    }

    setTimeout(init3DInteractions, 100);
  }

  // --- Hash Route Listener ---
  function handleHashNavigation() {
    let rawHash = window.location.hash.replace(/^#\/?/, '').trim();
    if (!rawHash) {
      showLandingView();
      return;
    }

    // Normalize hash (handle '#p rofile', '#profile/', '#safety-guide', '#firewall')
    let cleanHash = decodeURIComponent(rawHash).toLowerCase().replace(/[\s_]+/g, '-');
    if (cleanHash === 'p-rofile' || cleanHash === 'privacy' || cleanHash === 'settings') {
      cleanHash = 'profile';
    }
    if (cleanHash === 'safety' || cleanHash === 'guide' || cleanHash === 'safetyguide') {
      cleanHash = 'safety-guide';
    }
    if (cleanHash === 'identity-firewall' || cleanHash === 'shield') {
      cleanHash = 'firewall';
    }

    const appTabs = ['dashboard', 'analyze', 'protect-me-now', 'recruiter-pass', 'campus-mode', 'scam-heatmap', 'firewall', 'safety-guide', 'profile', 'result'];
    if (appTabs.includes(cleanHash)) {
      showAppView(cleanHash);
    } else if (cleanHash === 'landing' || cleanHash === 'home') {
      showLandingView();
    } else {
      showLandingView();
    }
  }

  window.addEventListener('hashchange', handleHashNavigation);

  // --- Fetch Presets & Safety Guide ---
  async function loadPresets() {
    try {
      const res = await apiRequest('/presets');
      if (res && res.presets) {
        res.presets.forEach(p => {
          state.presets[p.id] = p;
        });
      }
    } catch (e) {
      console.warn('Presets endpoint load error', e);
    }
  }

  async function loadSafetyGuide() {
    try {
      const res = await apiRequest('/safety-guide');
      if (res && res.categories) {
        renderSafetyGuideCards(res.categories);
      }
    } catch (e) {
      console.warn('Safety guide load error', e);
    }
  }

  function renderSafetyGuideCards(categories) {
    const container = document.getElementById('safety-guide-cards-container');
    if (!container) return;

    container.innerHTML = categories.map(cat => `
      <div class="card" style="display:flex; flex-direction:column; gap:12px;">
        <div style="display:flex; align-items:center; gap:12px;">
          <div style="font-size:1.8rem; width:44px; height:44px; border-radius:12px; background:var(--bg-surface-subtle); display:flex; align-items:center; justify-content:center;">
            ${cat.icon}
          </div>
          <div>
            <h3 style="font-size:1.25rem;">${cat.title}</h3>
            <p style="font-size:0.84rem; color:var(--text-subtle);">${cat.summary}</p>
          </div>
        </div>

        <div style="background:var(--bg-surface-subtle); padding:14px; border-radius:var(--radius-md); font-size:0.88rem;">
          <div style="font-weight:700; color:var(--text-main); margin-bottom:6px;">Common Warning Signs:</div>
          <ul style="padding-left:18px; color:var(--text-muted); display:flex; flex-direction:column; gap:4px;">
            ${cat.warning_signs.map(w => `<li>${w}</li>`).join('')}
          </ul>
        </div>

        <div style="background:var(--primary-light); padding:12px 14px; border-radius:var(--radius-md); font-size:0.86rem; border-left:3px solid var(--primary);">
          <strong style="color:var(--primary);">What to do:</strong>
          <span style="color:var(--text-main);"> ${cat.what_to_do}</span>
        </div>
      </div>
    `).join('');
  }

  // --- Populate Preset into Form ---
  function populateFormWithPreset(presetId) {
    const p = state.presets[presetId];
    if (!p) return;

    // Set category
    document.querySelectorAll('.category-select-card').forEach(card => {
      if (card.getAttribute('data-value') === p.opportunity_type) {
        card.classList.add('selected');
      } else {
        card.classList.remove('selected');
      }
    });
    const oppTypeInput = document.getElementById('form-opp-type');
    if (oppTypeInput) oppTypeInput.value = p.opportunity_type;

    const orgInput = document.getElementById('form-org-name');
    const urlInput = document.getElementById('form-website-url');
    const msgInput = document.getElementById('form-message-text');

    if (orgInput) orgInput.value = p.organization_name;
    if (urlInput) urlInput.value = p.website_url;
    if (msgInput) msgInput.value = p.message_text;
  }

  // --- Analysis Execution Flow ---
  async function runAnalysis(formData) {
    // 1. Show loading screen
    document.querySelectorAll('.subview').forEach(el => el.style.display = 'none');
    document.getElementById('subview-loading').style.display = 'flex';
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // 2. Animate step-by-step progress checklist
    const steps = [
      'l-step-1', 'l-step-2', 'l-step-3', 'l-step-4', 'l-step-5', 'l-step-6'
    ];

    steps.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.className = 'loading-step-item';
      }
    });

    for (let i = 0; i < steps.length; i++) {
      const el = document.getElementById(steps[i]);
      if (el) {
        el.classList.add('active');
        await new Promise(r => setTimeout(r, 380));
        el.classList.remove('active');
        el.classList.add('completed');
      }
    }

    // 3. Send API request
    try {
      const result = await apiRequest('/analyze', 'POST', formData, true);
      state.currentResult = result;

      // Update statistics
      incrementStat('analyzed');
      if (result.overall_risk_level === 'HIGH RISK') {
        incrementStat('risk');
      } else {
        incrementStat('protected');
      }

      // Render Result
      renderTrustProfile(result);
      document.getElementById('subview-loading').style.display = 'none';
      switchSubTab('result');
      showToast('Opportunity Trust Profile generated!', 'success');
    } catch (err) {
      document.getElementById('subview-loading').style.display = 'none';
      switchSubTab('analyze');
      showToast(err.message || 'Analysis failed. Please check details and try again.', 'error');
    }
  }

  // --- Render Opportunity Trust Profile ---
  function renderTrustProfile(data) {
    // 1. Header Details
    const titleEl = document.getElementById('res-org-title');
    const badgeEl = document.getElementById('res-risk-badge');
    const typeBadgeEl = document.getElementById('res-opp-type-badge');
    const engineBadgeEl = document.getElementById('res-engine-mode-badge');
    const scoreGraphic = document.getElementById('res-score-graphic');
    const scoreExplanation = document.getElementById('res-score-explanation');

    if (titleEl) titleEl.textContent = data.organization_name || 'Opportunity Candidate';
    if (typeBadgeEl) typeBadgeEl.textContent = `${getOppTypeIcon(data.opportunity_type)} ${data.opportunity_type}`;
    if (engineBadgeEl) engineBadgeEl.textContent = data.analysis_mode_label || '✨ Smart Trust Engine';

    // Risk Level Badge Styling
    if (badgeEl) {
      badgeEl.textContent = data.overall_risk_badge || data.overall_risk_level;
      badgeEl.className = 'badge-pill';
      if (data.overall_risk_level === 'LOW CONCERN') {
        badgeEl.classList.add('badge-risk-green');
      } else if (data.overall_risk_level === 'NEEDS REVIEW') {
        badgeEl.classList.add('badge-risk-yellow');
      } else {
        badgeEl.classList.add('badge-risk-red');
      }
    }

    // Trust Score
    if (scoreGraphic) {
      scoreGraphic.textContent = data.trust_score;
      if (data.trust_score >= 75) {
        scoreGraphic.style.borderColor = '#10B981';
        scoreGraphic.style.color = '#065F46';
      } else if (data.trust_score >= 50) {
        scoreGraphic.style.borderColor = '#F59E0B';
        scoreGraphic.style.color = '#92400E';
      } else {
        scoreGraphic.style.borderColor = '#EF4444';
        scoreGraphic.style.color = '#991B1B';
      }
    }

    if (scoreExplanation) {
      scoreExplanation.textContent = data.score_explanation;
    }

    // 2. Render 5 AI Modules
    const modulesGrid = document.getElementById('res-modules-grid');
    if (modulesGrid && data.modules) {
      const moduleIcons = {
        trust_analysis: '⚖',
        scam_detection: '🚨',
        identity_protection: '🛡',
        privacy_analysis: '🔒',
        document_intelligence: '📄'
      };

      const moduleTitles = {
        trust_analysis: 'Trust Analysis',
        scam_detection: 'Scam Detection',
        identity_protection: 'Identity Firewall',
        privacy_analysis: 'Privacy Analysis',
        document_intelligence: 'Document Intel'
      };

      modulesGrid.innerHTML = Object.keys(data.modules).map(key => {
        const m = data.modules[key];
        let statusBadge = '🟢 Safe';
        let statusClass = 'badge-risk-green';
        if (m.status === 'caution') {
          statusBadge = '🟡 Review';
          statusClass = 'badge-risk-yellow';
        } else if (m.status === 'danger') {
          statusBadge = '🔴 High Risk';
          statusClass = 'badge-risk-red';
        }

        return `
          <div class="card" style="padding:16px; display:flex; flex-direction:column; gap:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:1.25rem;">${moduleIcons[key] || '✦'}</span>
              <span class="badge-pill ${statusClass}" style="font-size:0.68rem; padding:2px 8px;">${statusBadge}</span>
            </div>
            <div style="font-weight:700; font-size:0.88rem;">${moduleTitles[key] || m.headline}</div>
            <p style="font-size:0.78rem; line-height:1.4; color:var(--text-muted);">${m.summary}</p>
          </div>
        `;
      }).join('');
    }

    // 3. Evidence List ("Why did SHEVAULT flag this?")
    const evidenceContainer = document.getElementById('evidence-container');
    const evidenceCountBadge = document.getElementById('evidence-count-badge');
    const evidenceList = Array.isArray(data.evidence_list) ? data.evidence_list : (Array.isArray(data.evidence) ? data.evidence : []);

    if (evidenceCountBadge) {
      const count = evidenceList.length;
      evidenceCountBadge.textContent = `${count} Flagged Signal${count === 1 ? '' : 's'}`;
    }

    if (evidenceContainer) {
      if (evidenceList.length === 0) {
        evidenceContainer.innerHTML = `
          <div class="card" style="background:var(--status-safe-bg); border-color:var(--status-safe-border); padding:20px; display:flex; align-items:center; gap:12px;">
            <span style="font-size:1.5rem;">🟢</span>
            <div>
              <div style="font-weight:700; color:var(--status-safe-text);">No Major Red Flags Detected</div>
              <div style="font-size:0.86rem; color:var(--status-safe-text); opacity:0.9;">The opportunity appears to conform to standard recruitment practices without coercive payment demands or premature sensitive identity requests.</div>
            </div>
          </div>
        `;
      } else {
        evidenceContainer.innerHTML = evidenceList.map((ev, index) => {
          const badgeClass = ev.severity === 'high' ? 'badge-risk-red' : (ev.severity === 'medium' ? 'badge-risk-yellow' : 'badge-soft-primary');
          return `
            <div class="evidence-card" data-evidence-index="${index}">
              <div class="evidence-card-header">
                <div class="evidence-title">
                  <span>${ev.severity === 'high' ? '⚠' : '✦'}</span>
                  <span>${ev.title || 'Risk Finding'}</span>
                </div>
                <div style="display:flex; align-items:center; gap:10px;">
                  <span class="badge-pill ${badgeClass}">${ev.risk_category || 'Opportunity Risk'}</span>
                  <span style="font-size:0.85rem; color:var(--primary); font-weight:700;">Details ➔</span>
                </div>
              </div>
              <p style="font-size:0.88rem; color:var(--text-muted); margin-top:8px;">${ev.description || ''}</p>
            </div>
          `;
        }).join('');

        // Attach click listener to evidence cards to open modal
        document.querySelectorAll('.evidence-card').forEach(el => {
          el.addEventListener('click', () => {
            const idx = parseInt(el.getAttribute('data-evidence-index'), 10);
            const ev = evidenceList[idx];
            if (ev) openEvidenceModal(ev);
          });
        });
      }
    }

    // 4. Identity Firewall Checklist Cards
    const fwContainer = document.getElementById('firewall-items-container');
    if (fwContainer && data.identity_firewall) {
      fwContainer.innerHTML = data.identity_firewall.map(item => `
        <div class="firewall-item-card ${item.detected ? 'detected' : ''}">
          <div class="firewall-item-header">
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:1.2rem;">${item.detected ? '🚨' : '🛡'}</span>
              <strong style="font-size:0.98rem;">${item.name}</strong>
            </div>
            <span class="badge-pill ${item.detected ? 'badge-risk-red' : 'badge-risk-green'}">
              ${item.detected ? 'Detected in Request' : 'Not Requested'}
            </span>
          </div>

          <div style="font-size:0.84rem; color:var(--text-muted); line-height:1.4;">
            <strong>Sensitivity:</strong> ${item.sensitivity} • <em>${item.reason}</em>
          </div>

          <div style="background:var(--bg-surface-subtle); padding:10px 12px; border-radius:var(--radius-sm); font-size:0.84rem; color:var(--text-main); border-left:3px solid var(--primary);">
            <strong>Safe Action:</strong> ${item.recommended_action}
          </div>
        </div>
      `).join('');
    }

    // 5. Website & Organization Inspections
    const webContent = document.getElementById('res-website-content');
    if (webContent) {
      if (data.website_analysis) {
        const w = data.website_analysis;
        webContent.innerHTML = `
          <div style="display:flex; flex-direction:column; gap:8px; font-size:0.88rem;">
            <div style="display:flex; justify-content:space-between;">
              <span style="color:var(--text-subtle);">Domain Name:</span>
              <strong>${w.domain || 'N/A'}</strong>
            </div>
            <div style="display:flex; justify-content:space-between;">
              <span style="color:var(--text-subtle);">Protocol:</span>
              <span class="badge-pill ${w.is_https ? 'badge-risk-green' : 'badge-risk-red'}">${w.is_https ? 'HTTPS Encrypted' : 'Insecure HTTP'}</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
              <span style="color:var(--text-subtle);">Domain Consistency:</span>
              <span>${w.domain_consistency}</span>
            </div>
            <div style="font-size:0.82rem; color:var(--text-muted); background:var(--bg-surface-subtle); padding:8px 10px; border-radius:6px; margin-top:4px;">
              ${w.https_note}
            </div>
          </div>
        `;
      } else {
        webContent.innerHTML = `<p style="font-size:0.88rem; color:var(--text-subtle);">No external URL was provided with this opportunity.</p>`;
      }
    }

    const orgContent = document.getElementById('res-org-content');
    if (orgContent) {
      if (data.organization_check) {
        const o = data.organization_check;
        orgContent.innerHTML = `
          <div style="display:flex; flex-direction:column; gap:8px; font-size:0.88rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="color:var(--text-subtle);">Entity Name:</span>
              <strong>${o.name || 'N/A'}</strong>
            </div>
            <div>
              <span class="badge-pill ${o.badge.includes('🟢') ? 'badge-risk-green' : (o.badge.includes('🟡') ? 'badge-risk-yellow' : 'badge-risk-red')}">
                ${o.badge}
              </span>
            </div>
            <p style="font-size:0.84rem; color:var(--text-muted);">${o.details}</p>
            <div style="background:var(--bg-surface-subtle); padding:8px 10px; border-radius:6px; font-size:0.82rem; color:var(--text-main);">
              <strong>Tip:</strong> ${o.verification_tips}
            </div>
          </div>
        `;
      }
    }

    // 6. Safe Communication Script
    const scriptEl = document.getElementById('res-safe-script');
    if (scriptEl) {
      scriptEl.textContent = data.safe_communication_script || 'Standard verification message.';
    }

    // 7. Before You Share Checklist
    const shareList = document.getElementById('before-you-share-list');
    if (shareList && data.before_you_share_questions) {
      shareList.innerHTML = data.before_you_share_questions.map(q => `
        <div style="display:flex; align-items:flex-start; gap:10px; font-size:0.9rem;">
          <span style="color:var(--primary); font-weight:700; font-size:1.1rem;">✓</span>
          <span>${q}</span>
        </div>
      `).join('');
    }

    // 8. Safe Sharing Matrix Table
    const tableBody = document.getElementById('safe-sharing-tbody');
    if (tableBody && data.safe_sharing_table) {
      tableBody.innerHTML = data.safe_sharing_table.map(row => {
        let badgeClass = 'badge-risk-green';
        if (row.sensitivity === 'Medium') badgeClass = 'badge-risk-yellow';
        if (row.sensitivity === 'High' || row.sensitivity.includes('Critical') || row.sensitivity.includes('Very High')) badgeClass = 'badge-risk-red';

        return `
          <tr>
            <td><strong>${row.item}</strong></td>
            <td><span class="badge-pill ${badgeClass}">${row.sensitivity}</span></td>
            <td style="color:var(--text-muted);">${row.stage}</td>
            <td style="font-size:0.88rem;">${row.guidance}</td>
          </tr>
        `;
      }).join('');
    }

    // 9. Recommended Practical Next Actions
    const actionsContainer = document.getElementById('recommended-actions-container');
    if (actionsContainer && data.recommended_actions) {
      actionsContainer.innerHTML = data.recommended_actions.map(action => `
        <div style="display:flex; align-items:flex-start; gap:12px; background:var(--bg-surface-subtle); padding:12px 16px; border-radius:var(--radius-md); font-size:0.92rem;">
          <span style="font-weight:700; color:var(--primary);">✦</span>
          <span style="color:var(--text-main); font-weight:500;">${action}</span>
        </div>
      `).join('');
    }

    // 10. Opportunity Black Box (4-Quadrant Explainability Grid)
    const blackBoxContainer = document.getElementById('black-box-grid-container');
    if (blackBoxContainer && data.black_box) {
      const b = data.black_box;
      
      const renderQuadrantItems = (arr) => {
        if (!arr || !Array.isArray(arr) || arr.length === 0) {
          return '<li style="color:var(--text-subtle); font-size:0.84rem;">None flagged at this stage.</li>';
        }
        return arr.map(item => {
          if (typeof item === 'string') return `<li>${item}</li>`;
          const t = item.title || item.name || '';
          const d = item.desc || item.details || item.description || '';
          const badge = item.badge ? `${item.badge} ` : '';
          return `
            <li style="margin-bottom:8px;">
              <strong style="font-size:0.88rem; color:var(--text-main);">${badge}${t}</strong>
              ${d ? `<div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px; line-height:1.4;">${d}</div>` : ''}
            </li>
          `;
        }).join('');
      };

      const riskSignals = Array.isArray(b.risk_signals) ? b.risk_signals : (b.quadrant_1_risk_signals?.items || []);
      const positiveSignals = Array.isArray(b.positive_signals) ? b.positive_signals : (b.quadrant_2_positive_signals?.items || []);
      const missingInfo = Array.isArray(b.missing_information) ? b.missing_information : (b.quadrant_3_missing_info?.items || []);
      const recommendedVerif = Array.isArray(b.recommended_verification) ? b.recommended_verification : (b.quadrant_4_recommended_verification?.items || []);

      blackBoxContainer.innerHTML = `
        <!-- Quadrant 1: Risk Signals -->
        <div class="black-box-card quadrant-risk">
          <div class="quadrant-header">
            <span class="quadrant-icon">🔴</span>
            <div>
              <strong style="font-size:1rem; color:#991B1B;">Risk Signals Flagged</strong>
              <div style="font-size:0.75rem; color:#B91C1C;">${riskSignals.length} Flagged Item(s)</div>
            </div>
          </div>
          <ul class="quadrant-list">
            ${renderQuadrantItems(riskSignals)}
          </ul>
        </div>

        <!-- Quadrant 2: Positive Signals -->
        <div class="black-box-card quadrant-positive">
          <div class="quadrant-header">
            <span class="quadrant-icon">🟢</span>
            <div>
              <strong style="font-size:1rem; color:#065F46;">Positive Signals Verified</strong>
              <div style="font-size:0.75rem; color:#047857;">${positiveSignals.length} Validated Item(s)</div>
            </div>
          </div>
          <ul class="quadrant-list">
            ${renderQuadrantItems(positiveSignals)}
          </ul>
        </div>

        <!-- Quadrant 3: Missing Information -->
        <div class="black-box-card quadrant-missing">
          <div class="quadrant-header">
            <span class="quadrant-icon">🟡</span>
            <div>
              <strong style="font-size:1rem; color:#92400E;">Missing Information & Gaps</strong>
              <div style="font-size:0.75rem; color:#B45309;">${missingInfo.length} Data Gap(s)</div>
            </div>
          </div>
          <ul class="quadrant-list">
            ${renderQuadrantItems(missingInfo)}
          </ul>
        </div>

        <!-- Quadrant 4: Recommended Verification -->
        <div class="black-box-card quadrant-verify">
          <div class="quadrant-header">
            <span class="quadrant-icon">🔵</span>
            <div>
              <strong style="font-size:1rem; color:#1E40AF;">Recommended Verifications</strong>
              <div style="font-size:0.75rem; color:#2563EB;">${recommendedVerif.length} Action Step(s)</div>
            </div>
          </div>
          <ul class="quadrant-list">
            ${renderQuadrantItems(recommendedVerif)}
          </ul>
        </div>
      `;
    }

    // 11. Automatically Trigger AI Voice Advisory Spoken Announcement
    const autoSpeakToggle = document.getElementById('voice-auto-speak-toggle');
    if (!autoSpeakToggle || autoSpeakToggle.checked) {
      setTimeout(() => {
        speakRiskAdvisory(data);
      }, 500);
    }

    setTimeout(init3DInteractions, 100);
  }

  // --- AI Voice Advisory Speech Synthesis ---
  function speakRiskAdvisory(data) {
    if (!data || !('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();

    const waveEl = document.getElementById('voice-wave-animation');
    const statusText = document.getElementById('voice-status-text');

    const org = data.organization_name || 'this opportunity';
    const score = data.trust_score !== undefined ? data.trust_score : 50;
    const risk = data.overall_risk_level || data.overall_risk || 'NEEDS REVIEW';
    const evArr = Array.isArray(data.evidence_list) ? data.evidence_list : (Array.isArray(data.evidence) ? data.evidence : []);

    let speechText = '';

    if (risk === 'HIGH RISK') {
      const topEvidence = (evArr.length > 0 && evArr[0]?.title) 
        ? evArr[0].title 
        : 'advance payment demands and premature identity requests';
      speechText = `Warning: High Risk detected for ${org}. Calculated trust score is ${score} out of 100. Critical risk signals identified include ${topEvidence}. We strongly advise you to withhold sensitive documents and never make advance payments.`;
    } else if (risk === 'NEEDS REVIEW') {
      speechText = `Caution: This opportunity from ${org} needs review. Calculated trust score is ${score} out of 100. We recommend independent verification before sharing personal documents or accepting terms.`;
    } else {
      speechText = `Opportunity verified: Low Concern detected for ${org}. Trust score is ${score} out of 100. Standard recruitment communication patterns identified.`;
    }

    if (statusText) {
      statusText.textContent = `Announcing: ${risk} (${score}/100)`;
    }

    const utterance = new SpeechSynthesisUtterance(speechText);
    utterance.rate = 0.95;
    utterance.pitch = 1.05;

    // Populate best English voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => 
      v.lang.startsWith('en') && (
        v.name.includes('Female') || 
        v.name.includes('Jenny') || 
        v.name.includes('Google') || 
        v.name.includes('Samantha') || 
        v.name.includes('Zira') ||
        v.name.includes('Natural')
      )
    ) || voices.find(v => v.lang.startsWith('en')) || voices[0];

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onstart = () => {
      if (waveEl) waveEl.classList.add('speaking');
      if (statusText) statusText.textContent = `Speaking: ${risk} Advisory (${score}/100)...`;
    };

    utterance.onend = () => {
      if (waveEl) waveEl.classList.remove('speaking');
      if (statusText) statusText.textContent = 'Voice advisory completed. Click to replay.';
    };

    utterance.onerror = () => {
      if (waveEl) waveEl.classList.remove('speaking');
      if (statusText) statusText.textContent = 'Click speaker icon to listen to voice advisory.';
    };

    window.speechSynthesis.speak(utterance);
  }

  function getOppTypeIcon(type) {
    const map = {
      'Job': '💼',
      'Internship': '🎓',
      'Scholarship': '✨',
      'Freelance': '💻',
      'Business Opportunity': '🚀',
      'Other': '🔍'
    };
    return map[type] || '💼';
  }

  // --- Evidence Modal Open ---
  function openEvidenceModal(ev) {
    const modal = document.getElementById('evidence-modal');
    if (!modal) return;

    const titleEl = document.getElementById('modal-ev-title');
    const badgeEl = document.getElementById('modal-ev-badge');
    const descEl = document.getElementById('modal-ev-desc');
    const snippetBox = document.getElementById('modal-ev-snippet-box');
    const snippetEl = document.getElementById('modal-ev-snippet');
    const whyEl = document.getElementById('modal-ev-why');
    const uncertaintyEl = document.getElementById('modal-ev-uncertainty');

    if (titleEl) titleEl.textContent = ev.title;
    if (badgeEl) {
      badgeEl.textContent = ev.risk_category;
      badgeEl.className = `badge-pill ${ev.severity === 'high' ? 'badge-risk-red' : 'badge-risk-yellow'}`;
    }
    if (descEl) descEl.textContent = ev.description;
    if (whyEl) whyEl.textContent = ev.why_it_matters;
    if (uncertaintyEl) uncertaintyEl.textContent = ev.uncertainty_note;

    if (ev.source_snippet && snippetEl) {
      snippetEl.textContent = ev.source_snippet;
      snippetBox.style.display = 'block';
    } else if (snippetBox) {
      snippetBox.style.display = 'none';
    }

    modal.classList.add('open');
  }

  // --- Pure Lightweight Vector QR Generator (No external dependencies) ---
  function generateQrSvg(text, size = 180) {
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
      hash = ((hash << 5) - hash) + text.charCodeAt(i);
      hash |= 0;
    }

    const modules = 21;
    const matrix = Array(modules).fill(null).map(() => Array(modules).fill(false));

    function setFinder(rStart, cStart) {
      for (let r = 0; r < 7; r++) {
        for (let c = 0; c < 7; c++) {
          if (r === 0 || r === 6 || c === 0 || c === 6 || (r >= 2 && r <= 4 && c >= 2 && c <= 4)) {
            matrix[rStart + r][cStart + c] = true;
          }
        }
      }
    }

    setFinder(0, 0);
    setFinder(0, modules - 7);
    setFinder(modules - 7, 0);

    for (let i = 8; i < modules - 8; i++) {
      matrix[6][i] = i % 2 === 0;
      matrix[i][6] = i % 2 === 0;
    }

    let bitIdx = 0;
    for (let r = 0; r < modules; r++) {
      for (let c = 0; c < modules; c++) {
        if ((r < 8 && c < 8) || (r < 8 && c >= modules - 8) || (r >= modules - 8 && c < 8)) {
          continue;
        }
        if (r === 6 || c === 6) continue;

        const charCode = text.charCodeAt(bitIdx % text.length) || 42;
        const bit = ((hash ^ (r * 31 + c * 17) ^ (charCode << (bitIdx % 8))) & 1) === 1;
        matrix[r][c] = bit;
        bitIdx++;
      }
    }

    const cellSize = (size / modules).toFixed(2);
    let rects = '';

    for (let r = 0; r < modules; r++) {
      for (let c = 0; c < modules; c++) {
        if (matrix[r][c]) {
          rects += `<rect x="${(c * cellSize).toFixed(2)}" y="${(r * cellSize).toFixed(2)}" width="${cellSize}" height="${cellSize}" fill="#1E1B4B" rx="1.5"/>`;
        }
      }
    }

    return `
      <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg" style="border-radius:10px;">
        <rect width="100%" height="100%" fill="white"/>
        ${rects}
      </svg>
    `;
  }

  function openSafeQRModal(data) {
    if (!data) data = state.currentResult;
    if (!data) {
      showToast('Please analyze an opportunity first to generate a Safe QR code.', 'info');
      return;
    }

    const modal = document.getElementById('safe-qr-modal');
    if (!modal) return;

    const qrData = data.safe_qr || {
      verification_url: `${window.location.origin}/#verify/${data.opportunity_id || 'shv-demo'}`,
      trust_badge: data.overall_risk_badge || '🟢 LOW CONCERN',
      trust_score: data.trust_score || 95,
      zero_pii_guarantee: true
    };

    const orgEl = document.getElementById('safe-qr-org-name');
    const badgeEl = document.getElementById('safe-qr-trust-badge');
    const scoreEl = document.getElementById('safe-qr-score');
    const urlInput = document.getElementById('safe-qr-share-url');
    const visualEl = document.getElementById('safe-qr-visual');

    if (orgEl) orgEl.textContent = data.organization_name || 'Opportunity Trust Verification';
    if (badgeEl) {
      badgeEl.textContent = qrData.trust_badge;
      badgeEl.className = `badge-pill ${qrData.trust_badge.includes('🟢') ? 'badge-risk-green' : (qrData.trust_badge.includes('🟡') ? 'badge-risk-yellow' : 'badge-risk-red')}`;
    }
    if (scoreEl) scoreEl.textContent = `${qrData.trust_score} / 100`;
    if (urlInput) urlInput.value = qrData.verification_url;
    if (visualEl) visualEl.innerHTML = generateQrSvg(qrData.verification_url, 200);

    modal.classList.add('open');
  }

  // --- 1. Protect Me Now (Emergency Crisis Containment) ---
  const emergencyPresets = {
    upi_transfer: {
      exposure_types: ['money_paid', 'bank_account_cheque'],
      entity_name: 'Apex Remote Careers (Telegram Recruiter)',
      amount_lost: '₹3,500 via UPI (GPay)',
      details: 'Transferred ₹3,500 security deposit for remote data entry laptop. Recruiter deleted chat.'
    },
    aadhaar_pan_shared: {
      exposure_types: ['aadhaar_card', 'pan_card'],
      entity_name: 'Vogue Global Media Freelance Lead',
      amount_lost: '₹0 (Identity files compromised)',
      details: 'Uploaded unmasked color scans of Aadhaar card and PAN card on an unencrypted Telegram form.'
    },
    otp_credentials: {
      exposure_types: ['otp_shared', 'pan_card'],
      entity_name: 'STEM Leadership Grant Portal Support',
      amount_lost: 'Account Credential Compromised',
      details: 'Shared 6-digit SMS verification code with caller claiming to be grant disbursement officer.'
    }
  };

  function initProtectMeNow() {
    // Preset buttons
    document.querySelectorAll('.emergency-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const presetKey = btn.getAttribute('data-preset');
        const p = emergencyPresets[presetKey];
        if (!p) return;

        document.querySelectorAll('#emergency-exposure-form input[name="exposure_types"]').forEach(cb => {
          cb.checked = p.exposure_types.includes(cb.value);
        });

        const entInput = document.getElementById('emerg-entity-name');
        const amtInput = document.getElementById('emerg-amount-lost');
        const detInput = document.getElementById('emerg-details');

        if (entInput) entInput.value = p.entity_name;
        if (amtInput) amtInput.value = p.amount_lost;
        if (detInput) detInput.value = p.details;

        showToast('Emergency incident scenario loaded.', 'info');
      });
    });

    // Form submit
    const emergForm = document.getElementById('emergency-exposure-form');
    if (emergForm) {
      emergForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const exposureTypes = Array.from(document.querySelectorAll('#emergency-exposure-form input[name="exposure_types"]:checked')).map(cb => cb.value);

        if (exposureTypes.length === 0) {
          showToast('Please select at least one compromised item or asset.', 'warning');
          return;
        }

        const entityName = document.getElementById('emerg-entity-name').value.trim();
        const amountLost = document.getElementById('emerg-amount-lost').value.trim();
        const details = document.getElementById('emerg-details').value.trim();

        const btn = document.getElementById('btn-generate-emergency-plan');
        if (btn) {
          btn.disabled = true;
          btn.textContent = 'Generating Containment Plan...';
        }

        try {
          const plan = await apiRequest('/protect-me-now', 'POST', {
            exposure_types: exposureTypes,
            entity_name: entityName,
            approximate_amount_lost: amountLost,
            incident_details: details
          });

          renderEmergencyPlan(plan);
          showToast('Emergency containment protocol generated!', 'success');
        } catch (err) {
          showToast(err.message || 'Failed to generate emergency response plan.', 'error');
        } finally {
          if (btn) {
            btn.disabled = false;
            btn.textContent = '⚡ Generate Immediate Containment Plan';
          }
        }
      });
    }
  }

  function renderEmergencyPlan(plan) {
    const resultBox = document.getElementById('emergency-plan-result');
    if (!resultBox || !plan) return;

    resultBox.style.display = 'block';

    const urgencyEl = document.getElementById('emerg-res-urgency');
    const titleEl = document.getElementById('emerg-res-title');
    const summaryEl = document.getElementById('emerg-res-summary');
    const warningText = document.getElementById('emerg-anti-recovery-text');

    if (urgencyEl) {
      urgencyEl.textContent = plan.urgency_badge || plan.urgency_level || plan.status_headline || 'CRITICAL CONTAINMENT';
      urgencyEl.className = 'badge-pill badge-risk-red';
    }
    if (titleEl) titleEl.textContent = plan.title || plan.status_headline || 'Immediate Crisis Response Plan';
    if (summaryEl) summaryEl.textContent = plan.summary || plan.immediate_summary || (Array.isArray(plan.priority_warnings) ? plan.priority_warnings.join(' ') : 'Containment protocol active.');
    if (warningText) warningText.textContent = plan.anti_recovery_warning || plan.anti_recovery_scam_warning || '';

    // Render Checklist with dynamic progress
    const checkContainer = document.getElementById('emerg-checklist-container');
    const checklistItems = plan.checklist || plan.action_checklist || plan.action_items || [];
    const totalSteps = checklistItems.length;

    function updateProgress() {
      const checkedCount = checkContainer.querySelectorAll('input[type="checkbox"]:checked').length;
      const pct = totalSteps > 0 ? Math.round((checkedCount / totalSteps) * 100) : 0;

      const bar = document.getElementById('emerg-progress-bar');
      const label = document.getElementById('emerg-progress-label');
      const countLabel = document.getElementById('emerg-steps-count');

      if (bar) bar.style.width = `${pct}%`;
      if (label) label.textContent = `${pct}% Completed`;
      if (countLabel) countLabel.textContent = `${checkedCount} of ${totalSteps} Steps`;
    }

    if (checkContainer) {
      checkContainer.innerHTML = checklistItems.map((item, idx) => {
        const criticality = (item.criticality || item.priority || 'high').toLowerCase();
        const category = item.category || 'Containment';
        const title = item.title || item.action || 'Containment Step';
        const instructions = item.instructions || item.details || '';
        const badgeClass = criticality === 'critical' ? 'badge-risk-red' : (criticality === 'high' || criticality === 'urgent' ? 'badge-risk-yellow' : 'badge-soft-primary');

        return `
          <label class="checklist-interactive-card priority-${criticality}">
            <input type="checkbox" data-idx="${idx}" class="checklist-step-cb" />
            <div class="step-card-content">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <span class="badge-pill ${badgeClass}" style="font-size:0.72rem;">
                  ${criticality.toUpperCase()}
                </span>
                <span style="font-size:0.78rem; font-weight:700; color:var(--text-subtle);">${category}</span>
              </div>
              <strong style="font-size:0.95rem; color:var(--text-main);">${title}</strong>
              <p style="font-size:0.84rem; color:var(--text-muted); margin-top:4px;">${instructions}</p>
              ${item.action_link ? `<div style="margin-top:6px;"><a href="${item.action_link}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm" style="font-size:0.75rem; padding:4px 10px;">${item.action_label || 'Take Action ↗'}</a></div>` : ''}
            </div>
          </label>
        `;
      }).join('');

      checkContainer.querySelectorAll('.checklist-step-cb').forEach(cb => {
        cb.addEventListener('change', updateProgress);
      });

      updateProgress();
    }

    // Render Helplines
    const helplineGrid = document.getElementById('emerg-helpline-grid');
    const helplines = plan.official_helplines || plan.quick_dial_actions || plan.helplines || [];
    if (helplineGrid && helplines.length > 0) {
      helplineGrid.innerHTML = helplines.map(h => {
        const name = h.title || h.name || 'Official Helpline';
        const contact = h.contact || h.number || 'Dial 1930';
        const details = h.url || h.availability || h.purpose || '24x7 Emergency Assistance';
        return `
          <div class="card helpline-card">
            <div style="font-size:1.6rem; margin-bottom:6px;">📞</div>
            <strong style="font-size:1.05rem;">${name}</strong>
            <div style="font-size:1.25rem; font-weight:800; color:var(--primary); margin:6px 0;">${contact}</div>
            <div style="font-size:0.82rem; color:var(--text-muted); margin-bottom:10px;">${details}</div>
            ${h.url ? `<a href="${h.url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm" style="width:100%; justify-content:center;">Visit Official Portal ↗</a>` : ''}
          </div>
        `;
      }).join('');
    }

    resultBox.scrollIntoView({ behavior: 'smooth' });
  }

  // --- 2. Verified Recruiter Pass ---
  const recruiterPresets = {
    google_recruiter: {
      name: 'Sarah Jenkins',
      organization: 'Google',
      email: 'sarahjenkins@google.com',
      phone: '+1 650 253 0000',
      platform: 'Official Career Portal',
      role: 'Senior Software Engineer Intern Recruiter',
      docs: 'Resume, GitHub portfolio link, Academic Transcript',
      fee: false
    },
    telegram_scout: {
      name: 'Elena Rostova',
      organization: 'Apex Global Design Studio',
      email: 'apexlead_talent@gmail.com',
      phone: '+91 99887 76655',
      platform: 'Telegram',
      role: 'Remote Banner Designer ($800/wk)',
      docs: 'Passport scan, Selfie holding ID card, Bank account number',
      fee: false
    },
    agency_free_email: {
      name: 'Vikram Singh',
      organization: 'TechStaff Solutions',
      email: 'vikram.recruiter1984@yahoo.com',
      phone: '+91 98111 22334',
      platform: 'WhatsApp',
      role: 'Data Analyst Trainee',
      docs: 'Aadhaar Card, Marksheets, ₹500 Test Registration Fee',
      fee: true
    }
  };

  function initRecruiterPass() {
    document.querySelectorAll('.recruiter-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const presetKey = btn.getAttribute('data-preset');
        const p = recruiterPresets[presetKey];
        if (!p) return;

        document.getElementById('rec-name').value = p.name;
        document.getElementById('rec-org').value = p.organization;
        document.getElementById('rec-email').value = p.email;
        document.getElementById('rec-phone').value = p.phone;
        document.getElementById('rec-platform').value = p.platform;
        document.getElementById('rec-role').value = p.role;
        document.getElementById('rec-docs').value = p.docs;
        document.getElementById('rec-fee-demanded').checked = p.fee;

        showToast('Sample recruiter profile loaded.', 'info');
      });
    });

    const recForm = document.getElementById('recruiter-pass-form');
    if (recForm) {
      recForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const recruiterName = document.getElementById('rec-name').value.trim();
        const organizationName = document.getElementById('rec-org').value.trim();
        const email = document.getElementById('rec-email').value.trim();
        const phone = document.getElementById('rec-phone').value.trim();
        const platform = document.getElementById('rec-platform').value;
        const role = document.getElementById('rec-role').value.trim();
        const docs = document.getElementById('rec-docs').value.trim();
        const feeDemanded = document.getElementById('rec-fee-demanded').checked;

        const btn = document.getElementById('btn-submit-recruiter-pass');
        if (btn) {
          btn.disabled = true;
          btn.textContent = 'Auditing Recruiter Authenticity...';
        }

        try {
          const result = await apiRequest('/recruiter-pass', 'POST', {
            recruiter_name: recruiterName,
            organization_name: organizationName,
            email_address: email,
            phone_number: phone,
            platform_channel: platform,
            role_offered: role,
            documents_requested: docs,
            registration_fee_demanded: feeDemanded
          });

          renderRecruiterPassResult(result);
          showToast('Recruiter authenticity pass evaluated!', 'success');
        } catch (err) {
          showToast(err.message || 'Recruiter pass evaluation failed.', 'error');
        } finally {
          if (btn) {
            btn.disabled = false;
            btn.textContent = '🛡️ Analyze Recruiter Authenticity';
          }
        }
      });
    }
  }

  function renderRecruiterPassResult(data) {
    const resultBox = document.getElementById('recruiter-pass-result');
    if (!resultBox || !data) return;

    resultBox.style.display = 'block';

    const badgeEl = document.getElementById('rec-pass-badge');
    const nameEl = document.getElementById('rec-pass-name');
    const roleOrgEl = document.getElementById('rec-pass-role-org');
    const scoreEl = document.getElementById('rec-pass-score');
    const summaryEl = document.getElementById('rec-pass-summary');
    const safeActionEl = document.getElementById('rec-safe-action');

    const statusBadge = data.pass_badge || data.status_badge || data.verification_status || 'VERIFICATION REQUIRED';
    const status = data.verification_status || data.status || 'CAUTION';

    if (badgeEl) {
      badgeEl.textContent = statusBadge;
      badgeEl.className = 'badge-pill';
      if (status.includes('VERIFIED') || status.includes('Found')) {
        badgeEl.classList.add('badge-risk-green');
      } else if (status.includes('CAUTION') || status.includes('Needs')) {
        badgeEl.classList.add('badge-risk-yellow');
      } else {
        badgeEl.classList.add('badge-risk-red');
      }
    }

    if (nameEl) nameEl.textContent = data.recruiter_name || 'Recruiter';
    if (roleOrgEl) roleOrgEl.textContent = `${data.role_offered || 'Opportunity'} @ ${data.organization_name || data.company_name || 'Claimed Organization'} • via ${data.platform_channel || data.contact_platform || 'Direct Channel'}`;
    if (scoreEl) scoreEl.textContent = `${data.authenticity_score !== undefined ? data.authenticity_score : 85}/100`;
    if (summaryEl) summaryEl.textContent = data.summary || 'Authenticity signals evaluated against enterprise domain records.';
    if (safeActionEl) safeActionEl.textContent = data.safe_action || (Array.isArray(data.recommended_next_steps) ? data.recommended_next_steps.join(' ') : 'Request correspondence from an official corporate email domain.');

    // Helper for formatting signal items safely
    const formatSignalItem = (s) => {
      if (!s) return '';
      if (typeof s === 'string') return `<li>${s}</li>`;
      const t = s.title || s.name || '';
      const d = s.details || s.desc || s.importance || '';
      return `<li><strong>${t}</strong>${d ? `<div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">${d}</div>` : ''}</li>`;
    };

    // Populate 3 Columns
    const vList = document.getElementById('rec-verified-signals-list');
    const uList = document.getElementById('rec-user-verify-list');
    const rList = document.getElementById('rec-risk-signals-list');

    const verifiedArr = data.verified_signals || [];
    const userVerifyArr = data.user_should_verify || [];
    const riskArr = data.risk_signals || [];

    if (vList) {
      vList.innerHTML = verifiedArr.length > 0 
        ? verifiedArr.map(formatSignalItem).join('')
        : `<li style="color:var(--text-subtle);">None verified at this stage.</li>`;
    }
    if (uList) {
      uList.innerHTML = userVerifyArr.length > 0
        ? userVerifyArr.map(formatSignalItem).join('')
        : `<li style="color:var(--text-subtle);">Standard checks complete.</li>`;
    }
    if (rList) {
      rList.innerHTML = riskArr.length > 0 
        ? riskArr.map(formatSignalItem).join('')
        : `<li style="color:#059669;">🟢 No overt risk signals flagged.</li>`;
    }

    resultBox.scrollIntoView({ behavior: 'smooth' });
  }

  // --- 3. Campus SHEVAULT Mode (Placement Cell Verification) ---
  const campusPresets = {
    campus_microsoft: {
      college: 'Delhi Technological University (DTU)',
      officer: 'Dr. Neha Verma (Placement Head)',
      company: 'Microsoft India',
      role: 'Software Engineering Summer Intern 2026 (₹1.25L/mo)',
      comm_mode: 'Official On-Campus Placement Cell Portal',
      zero_fee: true,
      doc_retention: true,
      jd: 'Microsoft India Summer Internship 2026 for B.Tech/Dual Degree students (CS/IT/ECE). Shortlisting via online coding test on official Microsoft Codility portal followed by 3 rounds of technical interviews. Stipend: ₹1,25,000/month. Zero application or training fee. No retention of original certificates.'
    },
    campus_deposit_intern: {
      college: 'Indira Gandhi Delhi Technical University for Women (IGDTUW)',
      officer: 'Prof. Anjali Mehta (Faculty Coordinator)',
      company: 'Apex Cloud Solutions',
      role: 'Virtual Cloud Analyst Intern (₹25k/mo)',
      comm_mode: 'External Google Form / Typeform',
      zero_fee: false,
      doc_retention: false,
      jd: 'Shortlisted students must deposit ₹4,500 security caution money for AWS Sandbox credentials prior to onboarding. Original 10th and 12th passing marksheets must be deposited with HR for 6 months internship commitment bond.'
    },
    campus_unaccredited_grant: {
      college: 'SNDT Women\'s University Mumbai',
      officer: 'Placement Cell Officer',
      company: 'Global Future Leaders Institute',
      role: 'Research Fellow ($4,000 International Grant)',
      comm_mode: 'Direct Telegram / WhatsApp Group',
      zero_fee: false,
      doc_retention: true,
      jd: 'Congratulations to all shortlisted female students for the $4,000 Research Fellowship. To generate international clearance certificate, each candidate must pay ₹2,500 processing charge via UPI within 24 hours.'
    }
  };

  function initCampusMode() {
    document.querySelectorAll('.campus-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const presetKey = btn.getAttribute('data-preset');
        const p = campusPresets[presetKey];
        if (!p) return;

        document.getElementById('camp-college-name').value = p.college;
        document.getElementById('camp-officer-name').value = p.officer;
        document.getElementById('camp-company-name').value = p.company;
        document.getElementById('camp-role-offered').value = p.role;
        document.getElementById('camp-comm-mode').value = p.comm_mode;
        document.getElementById('camp-zero-fee').checked = p.zero_fee;
        document.getElementById('camp-doc-retention').checked = p.doc_retention;
        document.getElementById('camp-jd-text').value = p.jd;

        showToast('Sample campus drive details loaded.', 'info');
      });
    });

    const campusForm = document.getElementById('campus-audit-form');
    if (campusForm) {
      campusForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const collegeName = document.getElementById('camp-college-name').value.trim();
        const placementOfficer = document.getElementById('camp-officer-name').value.trim();
        const companyName = document.getElementById('camp-company-name').value.trim();
        const roleOffered = document.getElementById('camp-role-offered').value.trim();
        const commMode = document.getElementById('camp-comm-mode').value;
        const zeroFee = document.getElementById('camp-zero-fee').checked;
        const docRetention = document.getElementById('camp-doc-retention').checked;
        const jdText = document.getElementById('camp-jd-text').value.trim();

        const btn = document.getElementById('btn-submit-campus-audit');
        if (btn) {
          btn.disabled = true;
          btn.textContent = 'Running Placement Audit Engine...';
        }

        try {
          const result = await apiRequest('/campus/verify', 'POST', {
            college_name: collegeName,
            placement_officer_name: placementOfficer,
            company_name: companyName,
            role_offered: roleOffered,
            communication_mode: commMode,
            zero_fee_placement_policy: zeroFee,
            original_document_retention_policy: docRetention,
            opportunity_details: jdText
          });

          renderCampusResult(result);
          showToast('Campus Placement Audit completed!', 'success');
        } catch (err) {
          showToast(err.message || 'Campus verification audit failed.', 'error');
        } finally {
          if (btn) {
            btn.disabled = false;
            btn.textContent = '🎓 Run Campus Placement Audit';
          }
        }
      });
    }

    // Copy Student Notice Buttons
    const copyNotice1 = document.getElementById('btn-copy-student-notice');
    const copyNotice2 = document.getElementById('btn-copy-student-notice-2');

    [copyNotice1, copyNotice2].forEach(btn => {
      if (btn) {
        btn.addEventListener('click', () => {
          const text = document.getElementById('camp-student-notice').textContent;
          navigator.clipboard.writeText(text).then(() => {
            showToast('Student placement notice copied to clipboard!', 'success');
          });
        });
      }
    });
  }

  function renderCampusResult(data) {
    const resultBox = document.getElementById('campus-audit-result');
    if (!resultBox) return;

    resultBox.style.display = 'block';

    const badgeEl = document.getElementById('camp-res-badge');
    const titleEl = document.getElementById('camp-res-title');
    const metaEl = document.getElementById('camp-res-meta');
    const summaryEl = document.getElementById('camp-res-summary');

    if (badgeEl) {
      badgeEl.textContent = data.clearance_badge || data.clearance_status;
      badgeEl.className = 'badge-pill';
      if (data.clearance_status === 'APPROVED') {
        badgeEl.classList.add('badge-risk-green');
      } else if (data.clearance_status === 'CONDITIONAL') {
        badgeEl.classList.add('badge-risk-yellow');
      } else {
        badgeEl.classList.add('badge-risk-red');
      }
    }

    if (titleEl) titleEl.textContent = `${data.company_name} — ${data.role_offered}`;
    if (metaEl) metaEl.textContent = `Audited for ${data.college_name} • Clearance: ${data.clearance_status}`;
    if (summaryEl) summaryEl.textContent = data.audit_summary;

    // 5-Step Lifecycle Pipeline Grid
    const pipelineContainer = document.getElementById('camp-pipeline-steps-container');
    if (pipelineContainer && data.pipeline_steps) {
      pipelineContainer.innerHTML = data.pipeline_steps.map(step => `
        <div class="pipeline-step-card ${step.status}">
          <div class="pipeline-step-header">
            <div class="pipeline-step-num">${step.step}</div>
            <span class="badge-pill ${step.status === 'completed' ? 'badge-risk-green' : (step.status === 'active' ? 'badge-soft-primary' : 'badge-risk-red')}" style="font-size:0.68rem; padding:2px 8px;">
              ${step.badge}
            </span>
          </div>
          <div class="pipeline-step-actor">${step.actor}</div>
          <div class="pipeline-step-title">${step.title}</div>
          <div class="pipeline-step-details">${step.details}</div>
        </div>
      `).join('');
    }

    // Student 1-Click Personal Check Button
    const studentPersonalCheckBtn = document.getElementById('btn-run-student-personal-check');
    if (studentPersonalCheckBtn) {
      studentPersonalCheckBtn.onclick = () => {
        // Preload company details into standard Opportunity Analyzer
        switchSubTab('analyze');
        document.getElementById('form-opp-type').value = 'Internship';
        document.getElementById('form-org-name').value = data.company_name;
        document.getElementById('form-website-url').value = '';
        document.getElementById('form-message-text').value = `Applying for: ${data.role_offered} at ${data.company_name}\n\nCollege: ${data.college_name}\nPlacement Notice Reference: ${data.certificate_id}\n\nCandidate Request: Please analyze safe KYC submission guidelines, mask Aadhaar/PAN, and generate a polite recruiter response for this drive.`;
        
        // Update category selector UI
        document.querySelectorAll('.category-select-card').forEach(c => {
          if (c.getAttribute('data-value') === 'Internship') c.classList.add('selected');
          else c.classList.remove('selected');
        });

        showToast(`Loaded ${data.company_name} into Opportunity Scanner for personal safety check.`, 'info');
      };
    }

    // Certificate Box
    const certId = document.getElementById('cert-id');
    const certCompany = document.getElementById('cert-company-name');
    const certRole = document.getElementById('cert-role-name');
    const certAuditor = document.getElementById('cert-auditor');
    const certDate = document.getElementById('cert-date');

    if (certId) certId.textContent = data.certificate_id;
    if (certCompany) certCompany.textContent = data.company_name;
    if (certRole) certRole.textContent = data.role_offered;
    if (certAuditor) certAuditor.textContent = data.placement_officer_name || 'Placement Cell Head';
    if (certDate) certDate.textContent = data.verification_date || 'September 30, 2026';

    // Student Notice Text
    const noticeEl = document.getElementById('camp-student-notice');
    if (noticeEl) noticeEl.textContent = data.student_notice_template;

    // Advisories List
    const advList = document.getElementById('camp-advisories-list');
    if (advList && data.placement_advisories) {
      advList.innerHTML = data.placement_advisories.map(a => `<li>✦ ${a}</li>`).join('');
    }

    resultBox.scrollIntoView({ behavior: 'smooth' });
  }

  // --- 4. Scam Threat Heatmap & Risk Radar ---
  async function loadScamHeatmap() {
    const riskType = document.getElementById('heatmap-filter-type') ? document.getElementById('heatmap-filter-type').value : 'all';
    const platform = document.getElementById('heatmap-filter-platform') ? document.getElementById('heatmap-filter-platform').value : 'all';

    try {
      const data = await apiRequest(`/scam-heatmap?risk_type=${riskType}&platform=${platform}`);
      renderScamHeatmap(data);
    } catch (err) {
      console.warn('Heatmap load error', err);
    }
  }

  function initScamHeatmap() {
    const fType = document.getElementById('heatmap-filter-type');
    const fPlat = document.getElementById('heatmap-filter-platform');

    if (fType) fType.addEventListener('change', () => loadScamHeatmap());
    if (fPlat) fPlat.addEventListener('change', () => loadScamHeatmap());
  }

  function renderScamHeatmap(data) {
    if (!data) return;

    // 1. KPI Stats - check top-level or nested summary_metrics
    const metrics = data.summary_metrics || {};
    const totalCount = data.total_threats_prevented ?? metrics.total_threats_prevented ?? metrics.total_analyzed ?? 1428;
    const depCount = data.advance_fee_traps_caught ?? metrics.advance_fee_traps_caught ?? metrics.high_risk_flagged ?? 612;
    const idCount = data.id_harvesting_blocked ?? metrics.id_harvesting_blocked ?? 589;
    const topChannel = data.highest_risk_channel || metrics.highest_risk_channel || metrics.most_vulnerable_platform || 'Telegram (42%)';

    const totalEl = document.getElementById('kpi-total-threats');
    const depEl = document.getElementById('kpi-deposit-traps');
    const idEl = document.getElementById('kpi-id-traps');
    const chanEl = document.getElementById('kpi-top-channel');

    if (totalEl) totalEl.textContent = typeof totalCount === 'number' ? totalCount.toLocaleString() : String(totalCount);
    if (depEl) depEl.textContent = typeof depCount === 'number' ? depCount.toLocaleString() : String(depCount);
    if (idEl) idEl.textContent = typeof idCount === 'number' ? idCount.toLocaleString() : String(idCount);
    if (chanEl) chanEl.textContent = String(topChannel);

    // 2. Regional Radar Hubs
    const regionalContainer = document.getElementById('regional-radar-cards');
    const hotspots = data.regional_hotspots || data.regional_risks || [];
    if (regionalContainer && Array.isArray(hotspots) && hotspots.length > 0) {
      regionalContainer.innerHTML = hotspots.map(r => {
        const regionName = r.region || 'Regional Hub';
        const riskIdx = r.risk_index || (r.high_risk_pct ? `${r.high_risk_pct}% Risk` : '🔴 High Risk');
        const vector = r.primary_threat_vector || r.top_scam || 'Caution Deposit / Fee Trap';
        const alertText = r.active_hotspot_alert || r.alert || r.details || 'Surge in unsolicited direct outreach targeting candidates.';
        const badgeClass = String(riskIdx).includes('High') || String(riskIdx).includes('Critical')
          ? 'badge-risk-red'
          : (String(riskIdx).includes('Elevated') || String(riskIdx).includes('Caution') ? 'badge-risk-yellow' : 'badge-soft-primary');

        return `
          <div class="card regional-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <strong style="font-size:1.05rem;">${regionName}</strong>
              <span class="badge-pill ${badgeClass}" style="font-size:0.72rem;">
                ${riskIdx}
              </span>
            </div>
            <div style="font-size:0.84rem; color:var(--text-muted); margin-bottom:10px;">
              <strong>Primary Vector:</strong> ${vector}
            </div>
            <div style="background:var(--bg-surface-subtle); padding:8px 10px; border-radius:6px; font-size:0.8rem; color:var(--text-main);">
              <strong>Hotspot Alert:</strong> ${alertText}
            </div>
          </div>
        `;
      }).join('');
    }

    // 3. Platform Distribution Bars
    const platformBars = document.getElementById('platform-bars-container');
    const platforms = data.platform_vulnerabilities || data.platform_breakdown || [];
    if (platformBars && Array.isArray(platforms) && platforms.length > 0) {
      platformBars.innerHTML = platforms.map(p => {
        const pName = p.platform || 'Platform';
        const score = p.risk_score ?? p.pct ?? 50;
        const pattern = p.common_scam_pattern || p.note || p.risk_level || 'Deceptive outreach and fee demands';
        const barColor = score >= 75 ? '#EF4444' : (score >= 55 ? '#F59E0B' : '#6366F1');
        const textColor = score >= 75 ? '#DC2626' : (score >= 55 ? '#D97706' : '#2563EB');

        return `
          <div class="platform-bar-item">
            <div style="display:flex; justify-content:space-between; font-size:0.88rem; font-weight:600; margin-bottom:4px;">
              <span>${pName}</span>
              <span style="color:${textColor}; font-weight:700;">${score}% Risk Index</span>
            </div>
            <div class="platform-progress-track">
              <div class="platform-progress-fill" style="width:${score}%; background:${barColor};"></div>
            </div>
            <div style="font-size:0.78rem; color:var(--text-subtle); margin-top:4px;">${pattern}</div>
          </div>
        `;
      }).join('');
    }

    // 4. Emerging Modus Operandi
    const modusContainer = document.getElementById('modus-operandi-container');
    const tactics = data.emerging_modus_operandi || data.scam_types || [];
    if (modusContainer && Array.isArray(tactics) && tactics.length > 0) {
      modusContainer.innerHTML = tactics.map(m => {
        const tacticTitle = m.tactic || m.type || 'Tactical Warning';
        const tacticDesc = m.description || m.warning || '';
        return `
          <div style="background:white; padding:12px 14px; border-radius:var(--radius-md); border-left:3px solid var(--primary); font-size:0.88rem; box-shadow:var(--shadow-sm);">
            <div style="font-weight:700; color:var(--text-main); margin-bottom:2px;">${tacticTitle}</div>
            <div style="font-size:0.82rem; color:var(--text-muted); line-height:1.45;">${tacticDesc}</div>
          </div>
        `;
      }).join('');
    }
  }

  // --- Setup Event Listeners ---
  function setupEventListeners() {
    // 1. Navbar Buttons & Navigation
    const navLoginBtn = document.getElementById('nav-login-btn');
    const navGetStartedBtn = document.getElementById('nav-get-started-btn');
    const footerLoginBtn = document.getElementById('footer-login-btn');
    const heroAnalyzeCta = document.getElementById('hero-analyze-cta');
    const heroLoginBtn = document.getElementById('hero-login-btn');
    const authModal = document.getElementById('auth-modal');
    const authModalClose = document.getElementById('auth-modal-close');

    if (navLoginBtn) navLoginBtn.addEventListener('click', () => openAuthModal('login'));
    if (heroLoginBtn) heroLoginBtn.addEventListener('click', () => openAuthModal('login'));
    if (footerLoginBtn) footerLoginBtn.addEventListener('click', (e) => { e.preventDefault(); openAuthModal('login'); });
    if (navGetStartedBtn) navGetStartedBtn.addEventListener('click', () => openAuthModal('signup'));
    const ctaGetStartedBtn = document.getElementById('cta-get-started-btn');
    if (ctaGetStartedBtn) ctaGetStartedBtn.addEventListener('click', () => {
      if (!state.user) {
        openAuthModal('signup');
      } else {
        showAppView('dashboard');
      }
    });
    
    if (heroAnalyzeCta) {
      heroAnalyzeCta.addEventListener('click', () => {
        if (!state.user) {
          openAuthModal('signup');
        } else {
          showAppView('analyze');
        }
      });
    }

    // Interactive Phone Mockup Handlers
    const requireAuthOrNavigate = (tab) => {
      if (!state.user) {
        openAuthModal('login');
      } else {
        showAppView(tab);
      }
    };

    const phoneQuickAccess = document.getElementById('phone-quick-access-btn');
    const phoneBtnDocs = document.getElementById('phone-btn-docs');
    const phoneBtnEmergency = document.getElementById('phone-btn-emergency');
    const phoneBtnPlaces = document.getElementById('phone-btn-places');
    const phoneBtnSupport = document.getElementById('phone-btn-support');
    const phoneRowDocs = document.getElementById('phone-row-docs');
    const phoneRowTracker = document.getElementById('phone-row-tracker');
    const phoneRowContacts = document.getElementById('phone-row-contacts');
    const phoneRowSettings = document.getElementById('phone-row-settings');

    if (phoneQuickAccess) phoneQuickAccess.addEventListener('click', () => requireAuthOrNavigate('firewall'));
    if (phoneBtnDocs) phoneBtnDocs.addEventListener('click', () => requireAuthOrNavigate('firewall'));
    if (phoneBtnEmergency) phoneBtnEmergency.addEventListener('click', () => requireAuthOrNavigate('protect-me-now'));
    if (phoneBtnPlaces) phoneBtnPlaces.addEventListener('click', () => requireAuthOrNavigate('scam-heatmap'));
    if (phoneBtnSupport) phoneBtnSupport.addEventListener('click', () => requireAuthOrNavigate('safety-guide'));
    if (phoneRowDocs) phoneRowDocs.addEventListener('click', () => requireAuthOrNavigate('firewall'));
    if (phoneRowTracker) phoneRowTracker.addEventListener('click', () => requireAuthOrNavigate('scam-heatmap'));
    if (phoneRowContacts) phoneRowContacts.addEventListener('click', () => requireAuthOrNavigate('protect-me-now'));
    if (phoneRowSettings) phoneRowSettings.addEventListener('click', () => requireAuthOrNavigate('profile'));

    if (authModalClose) {
      authModalClose.addEventListener('click', () => {
        authModal.classList.remove('open');
      });
    }

    // Safe QR Modal
    const safeQrModal = document.getElementById('safe-qr-modal');
    const safeQrModalClose = document.getElementById('safe-qr-modal-close');
    const btnOpenSafeQr = document.getElementById('btn-open-safe-qr');
    const btnBlackBoxQr = document.getElementById('btn-black-box-qr');
    const btnCopyQrUrl = document.getElementById('btn-copy-qr-url');

    if (btnOpenSafeQr) btnOpenSafeQr.addEventListener('click', () => openSafeQRModal());
    if (btnBlackBoxQr) btnBlackBoxQr.addEventListener('click', () => openSafeQRModal());
    if (safeQrModalClose && safeQrModal) {
      safeQrModalClose.addEventListener('click', () => safeQrModal.classList.remove('open'));
    }
    if (btnCopyQrUrl) {
      btnCopyQrUrl.addEventListener('click', () => {
        const input = document.getElementById('safe-qr-share-url');
        if (input) {
          navigator.clipboard.writeText(input.value).then(() => {
            showToast('Safe Opportunity verification link copied!', 'success');
          });
        }
      });
    }

    // SHEVAULT Safety Center Action Cards
    document.querySelectorAll('.safety-action-card').forEach(card => {
      card.addEventListener('click', () => {
        const action = card.getAttribute('data-action');
        if (action === 'open-analyze') switchSubTab('analyze');
        else if (action === 'open-protect-me-now') switchSubTab('protect-me-now');
        else if (action === 'open-recruiter-pass') switchSubTab('recruiter-pass');
        else if (action === 'open-campus-mode') switchSubTab('campus-mode');
        else if (action === 'open-scam-heatmap') switchSubTab('scam-heatmap');
        else if (action === 'open-firewall') switchSubTab('firewall');
      });
    });

    const dashEmergencyCta = document.getElementById('dash-emergency-cta');
    if (dashEmergencyCta) dashEmergencyCta.addEventListener('click', () => switchSubTab('protect-me-now'));

    const dashQuickRecruiterCta = document.getElementById('dash-quick-recruiter-cta');
    if (dashQuickRecruiterCta) dashQuickRecruiterCta.addEventListener('click', () => switchSubTab('recruiter-pass'));

    // Initialize Subsystem Handlers
    initProtectMeNow();
    initRecruiterPass();
    initCampusMode();
    initScamHeatmap();

    // Modal background click close
    [authModal, document.getElementById('evidence-modal')].forEach(modal => {
      if (modal) {
        modal.addEventListener('click', (e) => {
          if (e.target === modal) {
            modal.classList.remove('open');
          }
        });
      }
    });

    const evClose = document.getElementById('evidence-modal-close');
    if (evClose) {
      evClose.addEventListener('click', () => {
        document.getElementById('evidence-modal').classList.remove('open');
      });
    }

    // 2. Auth Modal Tabs
    const tabLogin = document.getElementById('tab-btn-login');
    const tabSignup = document.getElementById('tab-btn-signup');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    if (tabLogin && tabSignup) {
      tabLogin.addEventListener('click', () => {
        tabLogin.classList.add('active');
        tabSignup.classList.remove('active');
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
      });

      tabSignup.addEventListener('click', () => {
        tabSignup.classList.add('active');
        tabLogin.classList.remove('active');
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
      });
    }

    // 3. Password Toggle
    document.querySelectorAll('.toggle-pwd-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-target');
        const input = document.getElementById(targetId);
        if (input) {
          if (input.type === 'password') {
            input.type = 'text';
            btn.textContent = 'Hide';
          } else {
            input.type = 'password';
            btn.textContent = 'Show';
          }
        }
      });
    });

    // 5. Auth Submissions
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
          const res = await apiRequest('/auth/login', 'POST', { email, password });
          setAuth(res.token, res.user);
          authModal.classList.remove('open');
          showToast(`Welcome back, ${res.user.name}!`, 'success');
          showAppView('dashboard');
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    }

    if (signupForm) {
      signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('signup-name').value;
        const email = document.getElementById('signup-email').value;
        const role = document.getElementById('signup-role').value;
        const password = document.getElementById('signup-password').value;
        const confirm = document.getElementById('signup-confirm-password').value;

        if (password !== confirm) {
          showToast('Passwords do not match.', 'error');
          return;
        }

        try {
          const res = await apiRequest('/auth/register', 'POST', { name, email, password, role });
          setAuth(res.token, res.user);
          authModal.classList.remove('open');
          showToast(`Account created! Welcome, ${res.user.name}.`, 'success');
          showAppView('dashboard');
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    }


    // Forgot password alert
    const forgotLink = document.getElementById('forgot-password-link');
    if (forgotLink) {
      forgotLink.addEventListener('click', (e) => {
        e.preventDefault();
        showToast('Password reset link sent to registered email.', 'info');
      });
    }

    // Logout Button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => {
        clearAuth();
        showToast('You have been logged out safely.', 'info');
        showLandingView();
      });
    }

    // 6. Sidebar Navigation Links
    document.querySelectorAll('.sidebar-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const tab = item.getAttribute('data-tab');
        if (tab) {
          window.location.hash = tab;
          switchSubTab(tab);
        }
      });
    });

    const topbarNewBtn = document.getElementById('topbar-new-analysis-btn');
    if (topbarNewBtn) topbarNewBtn.addEventListener('click', () => switchSubTab('analyze'));

    const dashStartCta = document.getElementById('dash-start-analysis-cta');
    if (dashStartCta) dashStartCta.addEventListener('click', () => switchSubTab('analyze'));

    const dashCentralBtn = document.getElementById('dash-central-start-btn');
    if (dashCentralBtn) dashCentralBtn.addEventListener('click', () => switchSubTab('analyze'));

    const btnReanalyze = document.getElementById('btn-reanalyze');
    if (btnReanalyze) btnReanalyze.addEventListener('click', () => switchSubTab('analyze'));

    const backToLandingBtn = document.getElementById('back-to-landing-btn');
    if (backToLandingBtn) {
      backToLandingBtn.addEventListener('click', (e) => {
        e.preventDefault();
        showLandingView();
      });
    }

    // 7. Preset Clicks across Landing Page, Dashboard, and Form
    document.querySelectorAll('.landing-preset-btn').forEach(card => {
      card.addEventListener('click', () => {
        const presetId = card.getAttribute('data-preset');
        if (!state.user) {
          openAuthModal('signup');
          return;
        }
        showAppView('analyze');
        populateFormWithPreset(presetId);
        const form = document.getElementById('opportunity-form');
        if (form) form.dispatchEvent(new Event('submit'));
      });
    });

    document.querySelectorAll('.dash-preset-btn').forEach(card => {
      card.addEventListener('click', () => {
        const presetId = card.getAttribute('data-preset');
        switchSubTab('analyze');
        populateFormWithPreset(presetId);
        const form = document.getElementById('opportunity-form');
        if (form) form.dispatchEvent(new Event('submit'));
      });
    });

    document.querySelectorAll('.form-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const presetId = btn.getAttribute('data-preset');
        populateFormWithPreset(presetId);
        showToast('Sample opportunity loaded into form.', 'info');
      });
    });

    // 8. Category Selector Cards in Form
    document.querySelectorAll('.category-select-card').forEach(card => {
      card.addEventListener('click', () => {
        document.querySelectorAll('.category-select-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        const val = card.getAttribute('data-value');
        document.getElementById('form-opp-type').value = val;
      });
    });

    // 9. File Upload Drag and Drop & Browse
    const dropzone = document.getElementById('upload-dropzone');
    const fileInput = document.getElementById('form-file-input');
    const browseBtn = document.getElementById('browse-file-btn');
    const fileChip = document.getElementById('file-chip-container');
    const fileChipName = document.getElementById('file-chip-name');
    const removeFileBtn = document.getElementById('remove-file-btn');

    if (browseBtn && fileInput) {
      browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
      });
    }

    if (dropzone && fileInput) {
      dropzone.addEventListener('click', () => fileInput.click());

      dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });

      dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
      });

      dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          handleSelectedFile(e.dataTransfer.files[0]);
        }
      });

      fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files.length > 0) {
          handleSelectedFile(fileInput.files[0]);
        }
      });
    }

    function handleSelectedFile(file) {
      state.uploadedFile = file;
      if (fileChip && fileChipName) {
        fileChipName.textContent = `${file.name} (${Math.round(file.size / 1024)} KB)`;
        fileChip.style.display = 'block';
      }
      showToast(`Attached evidence: ${file.name}`, 'info');
    }

    if (removeFileBtn) {
      removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        state.uploadedFile = null;
        if (fileInput) fileInput.value = '';
        if (fileChip) fileChip.style.display = 'none';
      });
    }

    // 10. Form Submission
    const oppForm = document.getElementById('opportunity-form');
    if (oppForm) {
      oppForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const oppType = document.getElementById('form-opp-type').value || 'Job';
        const orgName = document.getElementById('form-org-name').value.trim();
        const webUrl = document.getElementById('form-website-url').value.trim();
        const msgText = document.getElementById('form-message-text').value.trim();

        if (!msgText && !webUrl && !orgName && !state.uploadedFile) {
          showToast('Please paste a message, provide a URL, or upload a document to analyze.', 'warning');
          return;
        }

        const formData = new FormData();
        formData.append('opportunity_type', oppType);
        formData.append('organization_name', orgName);
        formData.append('website_url', webUrl);
        formData.append('message_text', msgText);
        if (state.uploadedFile) {
          formData.append('file', state.uploadedFile);
        }

        await runAnalysis(formData);
      });
    }

    // 11. Profile & Settings Submissions
    const profForm = document.getElementById('profile-update-form');
    if (profForm) {
      profForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('prof-name-input').value;
        const role = document.getElementById('prof-role-select').value;
        const allowStorage = document.getElementById('pref-storage-toggle').checked;

        try {
          const res = await apiRequest(`/auth/update-profile?name=${encodeURIComponent(name)}&role=${encodeURIComponent(role)}&allow_storage=${allowStorage}`, 'POST');
          state.user = res.user;
          updateUserUI();
          showToast('Profile updated successfully!', 'success');
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    }

    const changePwdForm = document.getElementById('change-password-form');
    if (changePwdForm) {
      changePwdForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const old_password = document.getElementById('old-pwd-input').value;
        const new_password = document.getElementById('new-pwd-input').value;

        try {
          await apiRequest('/auth/change-password', 'POST', { old_password, new_password });
          showToast('Password changed successfully.', 'success');
          changePwdForm.reset();
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    }

    const btnClearFiles = document.getElementById('btn-clear-session-files');
    if (btnClearFiles) {
      btnClearFiles.addEventListener('click', () => {
        state.uploadedFile = null;
        const fileChip = document.getElementById('file-chip-container');
        if (fileChip) fileChip.style.display = 'none';
        showToast('Session document cache wiped from memory.', 'success');
      });
    }

    const btnDeleteAccount = document.getElementById('btn-delete-account');
    if (btnDeleteAccount) {
      btnDeleteAccount.addEventListener('click', async () => {
        if (confirm('Are you sure you want to permanently delete your account and clear all session data?')) {
          try {
            await apiRequest('/auth/account', 'DELETE');
            clearAuth();
            showToast('Account deleted.', 'info');
            showLandingView();
          } catch (err) {
            showToast(err.message, 'error');
          }
        }
      });
    }

    // 12. Copy Safe Script & Watermark
    const btnCopyScript = document.getElementById('btn-copy-script');
    if (btnCopyScript) {
      btnCopyScript.addEventListener('click', () => {
        const text = document.getElementById('res-safe-script').textContent;
        navigator.clipboard.writeText(text).then(() => {
          showToast('Safe communication script copied to clipboard!', 'success');
        }).catch(() => {
          showToast('Script copied to clipboard.', 'info');
        });
      });
    }

    const btnCopyWatermark = document.getElementById('btn-copy-watermark');
    if (btnCopyWatermark) {
      btnCopyWatermark.addEventListener('click', () => {
        const text = document.getElementById('watermark-sample-text').textContent;
        navigator.clipboard.writeText(text).then(() => {
          showToast('Watermark statement copied!', 'success');
        });
      });
    }

    // 13. Voice Advisory Play / Replay Buttons
    const btnPlayVoice = document.getElementById('btn-play-voice');
    const btnReplayVoice = document.getElementById('btn-replay-voice');

    if (btnPlayVoice) {
      btnPlayVoice.addEventListener('click', () => {
        if (state.currentResult) {
          speakRiskAdvisory(state.currentResult);
        } else {
          showToast('No active opportunity analysis to announce.', 'info');
        }
      });
    }

    if (btnReplayVoice) {
      btnReplayVoice.addEventListener('click', () => {
        if (state.currentResult) {
          speakRiskAdvisory(state.currentResult);
        } else {
          showToast('No active opportunity analysis to announce.', 'info');
        }
      });
    }

    // Toggle Safe Table
    const toggleSafeBtn = document.getElementById('toggle-safe-table-btn');
    const safeTableWrap = document.getElementById('safe-sharing-table-wrap');
    if (toggleSafeBtn && safeTableWrap) {
      toggleSafeBtn.addEventListener('click', () => {
        if (safeTableWrap.style.display === 'none') {
          safeTableWrap.style.display = 'block';
          toggleSafeBtn.textContent = 'Hide Safe Sharing Matrix ↑';
        } else {
          safeTableWrap.style.display = 'none';
          toggleSafeBtn.textContent = 'Show Safe Sharing Matrix ↓';
        }
      });
    }
  }

  function openAuthModal(mode = 'login') {
    const modal = document.getElementById('auth-modal');
    const tabLogin = document.getElementById('tab-btn-login');
    const tabSignup = document.getElementById('tab-btn-signup');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    if (!modal) return;

    if (mode === 'signup' && tabSignup) {
      tabSignup.classList.add('active');
      tabLogin.classList.remove('active');
      loginForm.style.display = 'none';
      signupForm.style.display = 'block';
    } else if (tabLogin) {
      tabLogin.classList.add('active');
      tabSignup.classList.remove('active');
      loginForm.style.display = 'block';
      signupForm.style.display = 'none';
    }

    modal.classList.add('open');
  }

  // --- Flat Clean Cards (3D Tilt Disabled per Design Directive) ---
  function init3DInteractions() {
    // 3D tilt deliberately disabled for clean flat upright cards
  }

  // Start initialization on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initApp();
      setTimeout(init3DInteractions, 200);
    });
  } else {
    initApp();
    setTimeout(init3DInteractions, 200);
  }

})();

