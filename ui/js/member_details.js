
// ui/member-details.js
// Ensure ../config.js is loaded BEFORE this module so window.API exists.

const qs = new URLSearchParams(window.location.search);

function showAlert(type, message) {
  const el = document.getElementById('alert');
  el.className = `alert alert-${type}`;
  el.textContent = message;
  el.classList.remove('d-none');
}
function clearAlert() {
  const el = document.getElementById('alert');
  el.classList.add('d-none');
  el.textContent = '';
}
function formatNumber(n) {
  const num = Number(n ?? 0);
  return isNaN(num) ? '—' : num.toLocaleString(undefined);
}

async function fetchMember(memberId) {
  const api = window.API;
  if (!api || typeof api.join !== 'function') {
    throw new Error('API helper is not available. Ensure config.js is loaded.');
  }
  const url = api.join(`/members/${memberId}`);
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' } });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Failed to fetch member #${memberId}: ${res.status} ${res.statusText}${text ? ' - ' + text : ''}`);
  }
  const json = await res.json();
  return json?.data || json;
}

function renderMember(data) {
  // Title & subtitle
  const title = document.getElementById('title');
  title.textContent = data?.nickname ? `Member • ${data.nickname} (#${data.id})` : `Member #${data?.id ?? ''}`;

  const subtitle = document.getElementById('subtitle');
  subtitle.textContent = `Group #${data.groupId}`;

  // Badges & stats
  const groupBadge = document.getElementById('groupBadge');
  groupBadge.textContent = `Group #${data.groupId}`;
  groupBadge.classList.remove('d-none');

  document.getElementById('currentRefund').textContent = formatNumber(data.currentMonthRefund);
  document.getElementById('nextBill').textContent = formatNumber(data.estimatedBillNextMonth);
  document.getElementById('gender').textContent = data.gender ?? '—';
  document.getElementById('memberId').textContent = String(data.id ?? '—');

  const nicknameBadge = document.getElementById('nicknameBadge');
  nicknameBadge.textContent = `Nickname: ${data.nickname ?? '—'}`;

  // Raw JSON
//  document.getElementById('rawJson').textContent = JSON.stringify(data, null, 2);

  // Navigate to schedules (preserve api via API.link)
  const toSchedulesLink = document.getElementById('toSchedulesLink');
  toSchedulesLink.href = apiLink(`feeminton/ui/schedules.html?groupId=${encodeURIComponent(data.groupId)}&groupName=${encodeURIComponent(data.nickname || '')}`);

  // Back link — if we arrived from schedules, go back there; else default to index
  const backLink = document.getElementById('backLink');
  const cameFromSchedules = window.document.referrer?.includes('schedules.html');
  backLink.href = apiLink(cameFromSchedules
    ? 'schedules.html'
    : 'index.html'
  );
}

function apiLink(href) {
  const api = window.API;
  if (!api || typeof api.link !== 'function') return href;
  return api.link(href);
}

async function loadAndRender() {
  clearAlert();
  const loading = document.getElementById('loading');
  const content = document.getElementById('content');

  if (!qs.get('memberId')) {
    showAlert('warning', 'Missing memberId in URL. Example: member-details.html?memberId=1');
    return;
  }
  const memberId = qs.get('memberId');

  // Show spinner, hide content
  loading.style.display = '';
  content.style.display = 'none';

  try {
    const data = await fetchMember(memberId);
    renderMember(data);

    // Show content
    loading.style.display = 'none';
    content.style.display = '';
  } catch (err) {
    console.error(err);
    loading.style.display = 'none';
    content.style.display = 'none';
    showAlert('danger', err.message || 'Unexpected error while loading member details.');
  }
}

export function initMemberPage() {
  // Wire refresh
  const refreshBtn = document.getElementById('refreshBtn');
  refreshBtn.addEventListener('click', loadAndRender);

  // Initial load
  loadAndRender();
}
