/**
 * RR AUCTION INTELLIGENCE 2027 — INTERACTIVE DASHBOARD ENGINE
 * Pure vanilla JavaScript with zero external CDN dependencies.
 * Renders SVG charts and dynamic tables completely offline.
 */

document.addEventListener('DOMContentLoaded', () => {
  const data = window.DASHBOARD_DATA;
  if (!data) {
    console.error("Dashboard data bundle not loaded!");
    return;
  }

  // ---------------------------------------------------------------------------
  // 1. TAB NAVIGATION
  // ---------------------------------------------------------------------------
  const tabs = document.querySelectorAll('.nav-tab');
  const panes = document.querySelectorAll('.tab-pane');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      panes.forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      const targetId = tab.getAttribute('data-target');
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add('active');
        // Render charts for the active pane if needed
        renderTabContent(targetId);
      }
    });
  });

  // State
  let selectedBatter = data.top_10_batters[0];
  let selectedBowler = data.top_10_bowlers[0];

  // ---------------------------------------------------------------------------
  // 2. PAGE 1: EXECUTIVE COMMAND CENTER
  // ---------------------------------------------------------------------------
  function renderExecutiveOverview() {
    renderBarChart('chart-top-batters', data.top_10_batters.slice(0, 5), 'cpri', 'cpri_ci_low', 'cpri_ci_high', '#E81B84');
    renderBarChart('chart-top-bowlers', data.top_10_bowlers.slice(0, 5), 'cpri', 'cpri_ci_low', 'cpri_ci_high', '#004BA0');
    renderScatterQuadrant('chart-bat-quadrant', data.cohort_batters.slice(0, 40), 'normal_sr', 'pressure_sr', 'delta_sr', 'Normal SR', 'Pressure SR', 133.6, '#E81B84');
    renderScatterQuadrant('chart-bowl-quadrant', data.cohort_bowlers.slice(0, 40), 'normal_econ', 'leverage_econ', 'delta_econ', 'Normal Econ', 'Leverage Econ', 8.15, '#004BA0', true);
  }

  // ---------------------------------------------------------------------------
  // 3. PAGE 2: BATTING INTELLIGENCE
  // ---------------------------------------------------------------------------
  function renderBattingIntelligence() {
    const tableBody = document.getElementById('batting-table-body');
    if (!tableBody) return;

    tableBody.innerHTML = '';
    data.top_10_batters.forEach((bat, idx) => {
      const tr = document.createElement('tr');
      if (bat.player_id === selectedBatter.player_id) tr.classList.add('selected');

      const tierClass = bat.overall_evidence_tier.includes('Tier 1') ? 'tier-1' :
                        bat.overall_evidence_tier.includes('Tier 2') ? 'tier-2' :
                        bat.overall_evidence_tier.includes('Tier 3') ? 'tier-3' : 'tier-4';

      tr.innerHTML = `
        <td><span class="rank-badge ${idx < 3 ? 'top3' : ''}">${bat.rank}</span></td>
        <td><strong>${bat.player_name}</strong></td>
        <td><strong style="color: #E81B84;">${bat.cpri.toFixed(2)}</strong></td>
        <td>${bat.pressure_sr.toFixed(2)}</td>
        <td class="delta-positive">+${bat.delta_sr.toFixed(2)}</td>
        <td>${bat.pressure_balls}</td>
        <td>${bat.bayes_sr.toFixed(2)}</td>
        <td><span style="font-size: 11px; color: #94A3B8;">[${bat.bayes_ci_low.toFixed(1)}, ${bat.bayes_ci_high.toFixed(1)}]</span></td>
        <td>${bat.match_cv ? bat.match_cv.toFixed(3) : 'N/A'}</td>
        <td><span class="tier-badge ${tierClass}">${bat.overall_evidence_tier.split(':')[0]}</span></td>
      `;

      tr.addEventListener('click', () => {
        document.querySelectorAll('#batting-table-body tr').forEach(r => r.classList.remove('selected'));
        tr.classList.add('selected');
        selectedBatter = bat;
        updateBatterDossier(bat);
      });

      tableBody.appendChild(tr);
    });

    updateBatterDossier(selectedBatter);
    renderErrorBarChart('chart-bat-uncertainty', data.top_10_batters, 'bayes_sr', 'bayes_ci_low', 'bayes_ci_high', 'Bayes Shrunk Strike Rate (95% CI)', '#E81B84');
  }

  function updateBatterDossier(bat) {
    const container = document.getElementById('batter-dossier-container');
    if (!container) return;

    const tierClass = bat.overall_evidence_tier.includes('Tier 1') ? 'tier-1' :
                      bat.overall_evidence_tier.includes('Tier 2') ? 'tier-2' :
                      bat.overall_evidence_tier.includes('Tier 3') ? 'tier-3' : 'tier-4';

    container.innerHTML = `
      <div class="player-dossier">
        <div class="dossier-header">
          <div>
            <div class="dossier-name">${bat.player_name}</div>
            <div class="dossier-meta">Rank #${bat.rank} Certified Finisher | ${bat.dim5_role}</div>
          </div>
          <span class="tier-badge ${tierClass}">${bat.overall_evidence_tier}</span>
        </div>

        <div class="dossier-stat-grid">
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Official CPRI</div>
            <div class="dossier-stat-val" style="color: #E81B84;">${bat.cpri.toFixed(2)}</div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Pressure Strike Rate</div>
            <div class="dossier-stat-val">${bat.pressure_sr.toFixed(2)}</div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Context Delta SR</div>
            <div class="dossier-stat-val delta-positive">+${bat.delta_sr.toFixed(2)}</div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Normal Baseline SR</div>
            <div class="dossier-stat-val">${bat.normal_sr.toFixed(2)}</div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Pressure Deliveries</div>
            <div class="dossier-stat-val">${bat.pressure_balls} <span style="font-size: 11px; color:#94A3B8;">(${bat.ipl_balls} IPL / ${bat.t20i_balls} T20I)</span></div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Match Consistency CV</div>
            <div class="dossier-stat-val">${bat.match_cv ? bat.match_cv.toFixed(3) : 'N/A'} <span style="font-size: 11px; color:#00C49F;">(${bat.match_success_rate.toFixed(0)}% Succ)</span></div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">95% Bayes Credible Interval</div>
            <div class="dossier-stat-val" style="font-size: 13px;">[${bat.bayes_ci_low.toFixed(1)} – ${bat.bayes_ci_high.toFixed(1)}]</div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Jackknife Worst-Case SR</div>
            <div class="dossier-stat-val">${bat.jackknife_worst_case.toFixed(2)} <span style="font-size: 11px; color:#94A3B8;">(Max Drop: ${bat.max_rank_drop} rank)</span></div>
          </div>
        </div>

        <div class="dossier-rationale">
          <strong>Scouting & Intelligence Rationale:</strong><br>
          ${bat.ranking_explanation}
        </div>
      </div>
    `;
  }

  // ---------------------------------------------------------------------------
  // 4. PAGE 3: BOWLING INTELLIGENCE
  // ---------------------------------------------------------------------------
  function renderBowlingIntelligence() {
    const tableBody = document.getElementById('bowling-table-body');
    if (!tableBody) return;

    tableBody.innerHTML = '';
    data.top_10_bowlers.forEach((bowl, idx) => {
      const tr = document.createElement('tr');
      if (bowl.player_id === selectedBowler.player_id) tr.classList.add('selected');

      const tierClass = bowl.overall_evidence_tier.includes('Tier 1') ? 'tier-1' :
                        bowl.overall_evidence_tier.includes('Tier 2') ? 'tier-2' :
                        bowl.overall_evidence_tier.includes('Tier 3') ? 'tier-3' : 'tier-4';

      tr.innerHTML = `
        <td><span class="rank-badge ${idx < 3 ? 'top3' : ''}">${bowl.rank}</span></td>
        <td><strong>${bowl.player_name}</strong></td>
        <td><strong style="color: #004BA0;">${bowl.cpri.toFixed(2)}</strong></td>
        <td>${bowl.leverage_econ.toFixed(2)}</td>
        <td class="delta-good-econ">${bowl.delta_econ.toFixed(2)}</td>
        <td>${bowl.pressure_balls}</td>
        <td>${bowl.bayes_econ.toFixed(2)}</td>
        <td><span style="font-size: 11px; color: #94A3B8;">[${bowl.bayes_ci_low.toFixed(1)}, ${bowl.bayes_ci_high.toFixed(1)}]</span></td>
        <td>${bowl.match_cv ? bowl.match_cv.toFixed(3) : 'N/A'}</td>
        <td><span class="tier-badge ${tierClass}">${bowl.overall_evidence_tier.split(':')[0]}</span></td>
      `;

      tr.addEventListener('click', () => {
        document.querySelectorAll('#bowling-table-body tr').forEach(r => r.classList.remove('selected'));
        tr.classList.add('selected');
        selectedBowler = bowl;
        updateBowlerDossier(bowl);
      });

      tableBody.appendChild(tr);
    });

    updateBowlerDossier(selectedBowler);
    renderErrorBarChart('chart-bowl-uncertainty', data.top_10_bowlers, 'bayes_econ', 'bayes_ci_low', 'bayes_ci_high', 'Bayes Shrunk Economy Rate (95% CI)', '#004BA0', true);
  }

  function updateBowlerDossier(bowl) {
    const container = document.getElementById('bowler-dossier-container');
    if (!container) return;

    const tierClass = bowl.overall_evidence_tier.includes('Tier 1') ? 'tier-1' :
                      bowl.overall_evidence_tier.includes('Tier 2') ? 'tier-2' :
                      bowl.overall_evidence_tier.includes('Tier 3') ? 'tier-3' : 'tier-4';

    container.innerHTML = `
      <div class="player-dossier">
        <div class="dossier-header">
          <div>
            <div class="dossier-name">${bowl.player_name}</div>
            <div class="dossier-meta">Rank #${bowl.rank} Certified Enforcer | ${bowl.dim5_role}</div>
          </div>
          <span class="tier-badge ${tierClass}">${bowl.overall_evidence_tier}</span>
        </div>

        <div class="dossier-stat-grid">
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Official CPRI</div>
            <div class="dossier-stat-val" style="color: #004BA0;">${bowl.cpri.toFixed(2)}</div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Leverage Economy</div>
            <div class="dossier-stat-val">${bowl.leverage_econ.toFixed(2)} rpo</div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Context Delta Econ</div>
            <div class="dossier-stat-val delta-good-econ">${bowl.delta_econ.toFixed(2)} rpo</div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Normal Baseline Econ</div>
            <div class="dossier-stat-val">${bowl.normal_econ.toFixed(2)} rpo</div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Leverage Deliveries</div>
            <div class="dossier-stat-val">${bowl.pressure_balls} <span style="font-size: 11px; color:#94A3B8;">(${bowl.ipl_balls} IPL / ${bowl.t20i_balls} T20I)</span></div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Match Consistency CV</div>
            <div class="dossier-stat-val">${bowl.match_cv ? bowl.match_cv.toFixed(3) : 'N/A'} <span style="font-size: 11px; color:#00C49F;">(${bowl.match_success_rate.toFixed(0)}% Succ)</span></div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">95% Bayes Credible Interval</div>
            <div class="dossier-stat-val" style="font-size: 13px;">[${bowl.bayes_ci_low.toFixed(2)} – ${bowl.bayes_ci_high.toFixed(2)}]</div>
          </div>
          <div class="dossier-stat-box">
            <div class="dossier-stat-label">Jackknife Worst-Case Econ</div>
            <div class="dossier-stat-val">${bowl.jackknife_worst_case.toFixed(2)} rpo <span style="font-size: 11px; color:#94A3B8;">(SE: ${bowl.jackknife_se.toFixed(2)})</span></div>
          </div>
        </div>

        <div class="dossier-rationale">
          <strong>Scouting & Intelligence Rationale:</strong><br>
          ${bowl.ranking_explanation}
        </div>
      </div>
    `;
  }

  // ---------------------------------------------------------------------------
  // 5. PAGE 4: PLAYER COMPARISON LAB
  // ---------------------------------------------------------------------------
  function renderPlayerComparisonLab() {
    const selDiscipline = document.getElementById('comp-discipline');
    const selP1 = document.getElementById('comp-player-1');
    const selP2 = document.getElementById('comp-player-2');

    if (!selDiscipline || !selP1 || !selP2) return;

    function populateSelectors() {
      const disc = selDiscipline.value;
      const list = disc === 'Batter' ? data.top_10_batters : data.top_10_bowlers;

      selP1.innerHTML = '';
      selP2.innerHTML = '';

      list.forEach((p, i) => {
        const opt1 = new Option(`${p.rank}. ${p.player_name} (CPRI: ${p.cpri.toFixed(1)})`, p.player_id);
        const opt2 = new Option(`${p.rank}. ${p.player_name} (CPRI: ${p.cpri.toFixed(1)})`, p.player_id);
        selP1.add(opt1);
        selP2.add(opt2);
      });

      selP1.selectedIndex = 0;
      selP2.selectedIndex = 1;
      updateComparison();
    }

    selDiscipline.addEventListener('change', populateSelectors);
    selP1.addEventListener('change', updateComparison);
    selP2.addEventListener('change', updateComparison);

    function updateComparison() {
      const disc = selDiscipline.value;
      const list = disc === 'Batter' ? data.top_10_batters : data.top_10_bowlers;
      const p1 = list.find(p => p.player_id == selP1.value) || list[0];
      const p2 = list.find(p => p.player_id == selP2.value) || list[1];

      const compContainer = document.getElementById('comparison-results-container');
      if (!compContainer) return;

      const isBat = disc === 'Batter';
      const p1Metric = isBat ? p1.pressure_sr.toFixed(2) : p1.leverage_econ.toFixed(2);
      const p2Metric = isBat ? p2.pressure_sr.toFixed(2) : p2.leverage_econ.toFixed(2);
      const metricLabel = isBat ? 'Pressure Strike Rate' : 'Leverage Economy';

      compContainer.innerHTML = `
        <div class="panel" style="margin-bottom: 20px;">
          <div class="panel-header">
            <span class="panel-title">Head-to-Head Reliability Comparison: ${p1.player_name} vs. ${p2.player_name}</span>
            <span class="panel-subtitle">${disc} Discipline Analysis</span>
          </div>
          <table class="data-table">
            <thead>
              <tr>
                <th>Evaluation Dimension</th>
                <th>${p1.player_name} (Rank #${p1.rank})</th>
                <th>${p2.player_name} (Rank #${p2.rank})</th>
                <th>Direct Variance & Advantage</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Official CPRI Score</strong></td>
                <td><strong style="color: #E81B84;">${p1.cpri.toFixed(2)}</strong></td>
                <td><strong style="color: #004BA0;">${p2.cpri.toFixed(2)}</strong></td>
                <td>${(p1.cpri - p2.cpri > 0 ? `+${(p1.cpri - p2.cpri).toFixed(2)} (Advantage ${p1.player_name})` : `${(p1.cpri - p2.cpri).toFixed(2)} (Advantage ${p2.player_name})`)}</td>
              </tr>
              <tr>
                <td><strong>${metricLabel}</strong></td>
                <td>${p1Metric}</td>
                <td>${p2Metric}</td>
                <td>${isBat ? (p1.pressure_sr > p2.pressure_sr ? `+${(p1.pressure_sr - p2.pressure_sr).toFixed(2)} SR` : `${(p1.pressure_sr - p2.pressure_sr).toFixed(2)} SR`) :
                              (p1.leverage_econ < p2.leverage_econ ? `${(p1.leverage_econ - p2.leverage_econ).toFixed(2)} Econ (Tighter)` : `+${(p1.leverage_econ - p2.leverage_econ).toFixed(2)} Econ`)}</td>
              </tr>
              <tr>
                <td><strong>Context-Adjusted Delta</strong></td>
                <td>${isBat ? `+${p1.delta_sr.toFixed(2)}` : p1.delta_econ.toFixed(2)}</td>
                <td>${isBat ? `+${p2.delta_sr.toFixed(2)}` : p2.delta_econ.toFixed(2)}</td>
                <td>${isBat ? `${(p1.delta_sr - p2.delta_sr > 0 ? `+${(p1.delta_sr - p2.delta_sr).toFixed(2)}` : (p1.delta_sr - p2.delta_sr).toFixed(2))}` :
                              `${(p1.delta_econ - p2.delta_econ).toFixed(2)}`}</td>
              </tr>
              <tr>
                <td><strong>Sample Volume (Deliveries)</strong></td>
                <td>${p1.pressure_balls} balls</td>
                <td>${p2.pressure_balls} balls</td>
                <td>${p1.pressure_balls - p2.pressure_balls > 0 ? `+${p1.pressure_balls - p2.pressure_balls} balls (${p1.player_name} higher)` : `${p1.pressure_balls - p2.pressure_balls} balls (${p2.player_name} higher)`}</td>
              </tr>
              <tr>
                <td><strong>IPL Battle-Testing Sample</strong></td>
                <td>${p1.ipl_balls} IPL balls</td>
                <td>${p2.ipl_balls} IPL balls</td>
                <td>${p1.ipl_balls - p2.ipl_balls > 0 ? `+${p1.ipl_balls - p2.ipl_balls} IPL balls (${p1.player_name})` : `${p1.ipl_balls - p2.ipl_balls} IPL balls (${p2.player_name})`}</td>
              </tr>
              <tr>
                <td><strong>95% Credible Interval Width</strong></td>
                <td>${p1.ci_width.toFixed(2)} (${p1.confidence_tier.split(' ')[0]})</td>
                <td>${p2.ci_width.toFixed(2)} (${p2.confidence_tier.split(' ')[0]})</td>
                <td>${p1.ci_width < p2.ci_width ? `Narrower CI by ${(p2.ci_width - p1.ci_width).toFixed(2)} (${p1.player_name} higher certainty)` : `Narrower CI by ${(p1.ci_width - p2.ci_width).toFixed(2)} (${p2.player_name} higher certainty)`}</td>
              </tr>
              <tr>
                <td><strong>Match Consistency CV</strong></td>
                <td>${p1.match_cv ? p1.match_cv.toFixed(3) : 'N/A'}</td>
                <td>${p2.match_cv ? p2.match_cv.toFixed(3) : 'N/A'}</td>
                <td>${p1.match_cv && p2.match_cv ? (p1.match_cv < p2.match_cv ? `${p1.player_name} more consistent night-to-night` : `${p2.player_name} more consistent night-to-night`) : 'N/A'}</td>
              </tr>
              <tr>
                <td><strong>Jackknife Sensitivity Drop</strong></td>
                <td>${p1.jackknife_verdict} (Max drop: ${p1.max_rank_drop} rank)</td>
                <td>${p2.jackknife_verdict} (Max drop: ${p2.max_rank_drop} rank)</td>
                <td>Both resilient against single-match distortion</td>
              </tr>
              <tr>
                <td><strong>Auction Evidence Classification</strong></td>
                <td>${p1.overall_evidence_tier}</td>
                <td>${p2.overall_evidence_tier}</td>
                <td>${p1.overall_evidence_tier === p2.overall_evidence_tier ? 'Same Evidence Tier' : 'Divergent Arena Experience'}</td>
              </tr>
            </tbody>
          </table>
        </div>
      `;
    }

    populateSelectors();
  }

  // ---------------------------------------------------------------------------
  // 6. PAGE 5: AUCTION INTELLIGENCE
  // ---------------------------------------------------------------------------
  function renderAuctionIntelligence() {
    const tableBody = document.getElementById('auction-table-body');
    if (!tableBody) return;

    tableBody.innerHTML = '';
    const allRanks = [...data.top_10_batters, ...data.top_10_bowlers];
    allRanks.sort((a, b) => b.cpri - a.cpri);

    allRanks.forEach(p => {
      const tr = document.createElement('tr');
      const tierClass = p.overall_evidence_tier.includes('Tier 1') ? 'tier-1' :
                        p.overall_evidence_tier.includes('Tier 2') ? 'tier-2' :
                        p.overall_evidence_tier.includes('Tier 3') ? 'tier-3' : 'tier-4';

      tr.innerHTML = `
        <td><strong>${p.player_name}</strong></td>
        <td>${p.discipline}</td>
        <td>Rank #${p.rank}</td>
        <td><strong>${p.cpri.toFixed(2)}</strong></td>
        <td>${p.ipl_balls} balls</td>
        <td>${p.t20i_balls} balls</td>
        <td>${p.confidence_tier.split(' ')[0]}</td>
        <td>${p.dim5_role}</td>
        <td><span class="tier-badge ${tierClass}">${p.overall_evidence_tier}</span></td>
      `;
      tableBody.appendChild(tr);
    });
  }

  // ---------------------------------------------------------------------------
  // 7. TAB CONTENT ROUTER
  // ---------------------------------------------------------------------------
  function renderTabContent(tabId) {
    if (tabId === 'tab-overview') renderExecutiveOverview();
    else if (tabId === 'tab-batting') renderBattingIntelligence();
    else if (tabId === 'tab-bowling') renderBowlingIntelligence();
    else if (tabId === 'tab-comparison') renderPlayerComparisonLab();
    else if (tabId === 'tab-auction') renderAuctionIntelligence();
  }

  // Initial render of Page 1
  renderExecutiveOverview();

  // ---------------------------------------------------------------------------
  // 8. PURE SVG CHART RENDERERS (ZERO DEPENDENCIES)
  // ---------------------------------------------------------------------------
  function renderBarChart(containerId, dataset, valKey, lowKey, highKey, barColor) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = container.clientWidth || 450;
    const height = 280;
    const padding = { top: 20, right: 30, bottom: 30, left: 110 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    const minX = 60;
    const maxX = 80;
    const barH = chartH / dataset.length;

    let svg = `<svg width="${width}" height="${height}" style="overflow: visible;">`;

    dataset.forEach((d, i) => {
      const y = padding.top + i * barH + barH * 0.15;
      const h = barH * 0.7;
      const val = d[valKey];
      const barW = Math.max(10, ((val - minX) / (maxX - minX)) * chartW);
      const lowX = padding.left + Math.max(0, ((d[lowKey] - minX) / (maxX - minX)) * chartW);
      const highX = padding.left + Math.min(chartW, ((d[highKey] - minX) / (maxX - minX)) * chartW);

      // Label
      svg += `<text x="${padding.left - 10}" y="${y + h / 2 + 4}" fill="#E2E8F0" font-size="11" font-weight="600" text-anchor="end">${d.player_name}</text>`;
      // Bar
      svg += `<rect x="${padding.left}" y="${y}" width="${barW}" height="${h}" rx="4" fill="${barColor}" fill-opacity="0.85"/>`;
      // Error Bar Line
      svg += `<line x1="${lowX}" y1="${y + h / 2}" x2="${highX}" y2="${y + h / 2}" stroke="#FFB81C" stroke-width="2"/>`;
      svg += `<line x1="${lowX}" y1="${y + h * 0.25}" x2="${lowX}" y2="${y + h * 0.75}" stroke="#FFB81C" stroke-width="2"/>`;
      svg += `<line x1="${highX}" y1="${y + h * 0.25}" x2="${highX}" y2="${y + h * 0.75}" stroke="#FFB81C" stroke-width="2"/>`;
      // Value text
      svg += `<text x="${padding.left + barW + 8}" y="${y + h / 2 + 4}" fill="#FFFFFF" font-size="11" font-weight="700">${val.toFixed(1)}</text>`;
    });

    svg += `</svg>`;
    container.innerHTML = svg;
  }

  function renderErrorBarChart(containerId, dataset, meanKey, lowKey, highKey, title, pointColor, isEcon = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = container.clientWidth || 550;
    const height = 300;
    const padding = { top: 25, right: 30, bottom: 40, left: 120 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    const allLows = dataset.map(d => d[lowKey]);
    const allHighs = dataset.map(d => d[highKey]);
    const minVal = Math.floor(Math.min(...allLows) * 0.95);
    const maxVal = Math.ceil(Math.max(...allHighs) * 1.05);

    const stepY = chartH / dataset.length;
    let svg = `<svg width="${width}" height="${height}">`;

    dataset.forEach((d, i) => {
      const y = padding.top + i * stepY + stepY / 2;
      const xMean = padding.left + ((d[meanKey] - minVal) / (maxVal - minVal)) * chartW;
      const xLow = padding.left + ((d[lowKey] - minVal) / (maxVal - minVal)) * chartW;
      const xHigh = padding.left + ((d[highKey] - minVal) / (maxVal - minVal)) * chartW;

      // Label
      svg += `<text x="${padding.left - 10}" y="${y + 4}" fill="#E2E8F0" font-size="11" font-weight="600" text-anchor="end">${d.player_name}</text>`;
      // Error Line
      svg += `<line x1="${xLow}" y1="${y}" x2="${xHigh}" y2="${y}" stroke="rgba(255, 255, 255, 0.4)" stroke-width="2"/>`;
      svg += `<line x1="${xLow}" y1="${y - 4}" x2="${xLow}" y2="${y + 4}" stroke="rgba(255, 255, 255, 0.6)" stroke-width="2"/>`;
      svg += `<line x1="${xHigh}" y1="${y - 4}" x2="${xHigh}" y2="${y + 4}" stroke="rgba(255, 255, 255, 0.6)" stroke-width="2"/>`;
      // Center Point
      svg += `<circle cx="${xMean}" cy="${y}" r="5" fill="${pointColor}" stroke="#FFFFFF" stroke-width="1.5"/>`;
      // Val
      svg += `<text x="${xHigh + 6}" y="${y + 4}" fill="#94A3B8" font-size="10">${d[meanKey].toFixed(1)}</text>`;
    });

    svg += `</svg>`;
    container.innerHTML = svg;
  }

  function renderScatterQuadrant(containerId, dataset, xKey, yKey, cKey, xLabel, yLabel, parVal, accentColor, isBowl = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = container.clientWidth || 450;
    const height = 280;
    const padding = { top: 20, right: 30, bottom: 40, left: 50 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    const xVals = dataset.map(d => d[xKey]).filter(v => !isNaN(v));
    const yVals = dataset.map(d => d[yKey]).filter(v => !isNaN(v));

    const minX = Math.min(...xVals);
    const maxX = Math.max(...xVals);
    const minY = Math.min(...yVals);
    const maxY = Math.max(...yVals);

    let svg = `<svg width="${width}" height="${height}">`;

    // Reference Line Par
    const parY = padding.top + chartH - ((parVal - minY) / (maxY - minY)) * chartH;
    svg += `<line x1="${padding.left}" y1="${parY}" x2="${padding.left + chartW}" y2="${parY}" stroke="rgba(255, 255, 255, 0.15)" stroke-dasharray="4,4"/>`;
    svg += `<text x="${padding.left + chartW - 5}" y="${parY - 5}" fill="rgba(255, 255, 255, 0.4)" font-size="10" text-anchor="end">Par (${parVal})</text>`;

    dataset.forEach(d => {
      if (isNaN(d[xKey]) || isNaN(d[yKey])) return;
      const cx = padding.left + ((d[xKey] - minX) / (maxX - minX)) * chartW;
      const cy = padding.top + chartH - ((d[yKey] - minY) / (maxY - minY)) * chartH;
      const isPositive = isBowl ? d[cKey] < 0 : d[cKey] > 0;
      const color = isPositive ? '#00C49F' : 'rgba(255, 255, 255, 0.3)';

      svg += `<circle cx="${cx}" cy="${cy}" r="4.5" fill="${color}" fill-opacity="0.8" stroke="rgba(255, 255, 255, 0.4)" stroke-width="1">
        <title>${d.player_name}: ${xLabel}=${d[xKey].toFixed(1)}, ${yLabel}=${d[yKey].toFixed(1)}</title>
      </circle>`;
    });

    // Axes
    svg += `<line x1="${padding.left}" y1="${padding.top + chartH}" x2="${padding.left + chartW}" y2="${padding.top + chartH}" stroke="rgba(255, 255, 255, 0.2)"/>`;
    svg += `<line x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${padding.top + chartH}" stroke="rgba(255, 255, 255, 0.2)"/>`;
    svg += `<text x="${padding.left + chartW / 2}" y="${height - 8}" fill="#94A3B8" font-size="11" text-anchor="middle">${xLabel}</text>`;
    svg += `<text x="15" y="${padding.top + chartH / 2}" fill="#94A3B8" font-size="11" text-anchor="middle" transform="rotate(-90 15 ${padding.top + chartH / 2})">${yLabel}</text>`;

    svg += `</svg>`;
    container.innerHTML = svg;
  }
});

