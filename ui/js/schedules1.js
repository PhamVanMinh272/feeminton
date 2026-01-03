
// ui/schedules.js
// Make sure ../config.js is loaded BEFORE this module so window.API exists.

const qs = new URLSearchParams(window.location.search);

const state = {
  groupId: qs.get('groupId') || null,
  groupName: qs.get('groupName') || null,
  year: parseInt(qs.get('year') || new Date().getFullYear(), 10),
  month: parseInt(qs.get('month') || (new Date().getMonth() + 1), 10),
  schedules: [],
};

// ---------------- Utilities ----------------
function showAlert(type, message) {
  const alertEl = document.getElementById('alert');
  alertEl.className = `alert alert-${type}`;
  alertEl.textContent = message;
  alertEl.classList.remove('d-none');
}
function clearAlert() {
  const alertEl = document.getElementById('alert');
  alertEl.classList.add('d-none');
  alertEl.textContent = '';
}
function pad2(n) { return String(n).padStart(2, '0'); }
function monthKey(y, m) { return `${y}-${pad2(m)}`; }
function formatMonthLabel(y, m) {
  const date = new Date(y, m - 1, 1);
  return date.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
}
function toLocalDateParts(iso) {
  const d = new Date(iso);
  return {
    year: d.getFullYear(),
    month: d.getMonth() + 1,
    day: d.getDate(),
    weekday: d.toLocaleDateString(undefined, { weekday: 'short' }),
    time: d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }),
  };
}

// ---------------- DOM bindings ----------------
function setTitle() {
  const titleEl = document.getElementById('title');
  if (!titleEl) return;
  titleEl.textContent = state.groupName ? state.groupName : 'Schedules';
}
function setBackLink() {
  const backLink = document.getElementById('backLink');
  if (!backLink) return;
  const target = 'index.html'; // adjust path if needed
  backLink.href = (window.API && typeof window.API.link === 'function')
    ? window.API.link(target)
    : target;
}
function initGroupBadge() {
  const groupBadge = document.getElementById('groupBadge');
  if (!groupBadge) return;
  if (state.groupId) {
    groupBadge.textContent = `Group #${state.groupId}`;
    groupBadge.classList.remove('d-none');
  }
}
function initMonthControls() {
  const monthPicker = document.getElementById('monthPicker');
  const prevBtn = document.getElementById('prevMonthBtn');
  const nextBtn = document.getElementById('nextMonthBtn');

  if (monthPicker) {
    monthPicker.value = monthKey(state.year, state.month);
    monthPicker.addEventListener('change', () => {
      const [y, m] = monthPicker.value.split('-').map(Number);
      state.year = y; state.month = m;
      updateSubtitle();
      fetchAndRender();
      updateUrl();
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      const d = new Date(state.year, state.month - 1, 1);
      d.setMonth(d.getMonth() - 1);
      state.year = d.getFullYear();
      state.month = d.getMonth() + 1;
      if (monthPicker) monthPicker.value = monthKey(state.year, state.month);
      updateSubtitle();
      fetchAndRender();
      updateUrl();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      const d = new Date(state.year, state.month - 1, 1);
      d.setMonth(d.getMonth() + 1);
      state.year = d.getFullYear();
      state.month = d.getMonth() + 1;
      if (monthPicker) monthPicker.value = monthKey(state.year, state.month);
      updateSubtitle();
      fetchAndRender();
      updateUrl();
    });
  }
}

function updateSubtitle() {
  const el = document.getElementById('subtitle');
  if (!el) return;
  const suffix = state.groupId ? ` • Group #${state.groupId}` : '';
  el.textContent = `Showing ${formatMonthLabel(state.year, state.month)}${suffix}`;
}
function updateUrl() {
  const params = new URLSearchParams(window.location.search);
  if (state.groupId) params.set('groupId', state.groupId); else params.delete('groupId');
  params.set('year', String(state.year));
  params.set('month', String(state.month));
  const newUrl = window.location.pathname + '?' + params.toString();
  window.history.replaceState({}, '', newUrl);
}

// ---------------- Rendering ----------------
function renderScheduleCard(s) {
  const parts = toLocalDateParts(s.scheduleDate);
  const attendees = Array.isArray(s.attendances) ? s.attendances.slice() : [];
  attendees.sort((a, b) => a.memberName.localeCompare(b.memberName, undefined, { sensitivity: 'base' }));
  const joinedCount = attendees.reduce((acc, a) => acc + (a.joined ? 1 : 0), 0);

  return `
    <div class="card schedule-card h-100 shadow-sm" data-schedule-id="${s.id}">
      <div class="card-header d-flex justify-content-between align-items-center">
        <div>
          <div class="fw-bold">${parts.weekday}, ${parts.day}/${pad2(parts.month)}/${parts.year}</div>
          <div class="small text-muted">${parts.time}</div>
        </div>
        <span class="badge bg-secondary">ID: ${s.id}</span>
      </div>
      <ul class="list-group list-group-flush">
        ${attendees.map(a => `
          <li class="list-group-item d-flex justify-content-between align-items-center" data-attendance-id="${a.attendanceId}">
            <div class="d-flex align-items-center gap-2">
              <span class="joined-icon ${a.joined ? 'joined-true' : 'joined-false'}" title="${a.joined ? 'Joined' : 'Unjoined'}">${a.joined ? '✓' : '✕'}</span>
              <span class="attendee-name">${a.memberName}</span>
              <span class="text-muted small">#${a.memberId}</span>

              <!-- Refund shown always -->
              <span class="badge bg-warning text-dark refund-badge">Refund: ${Number(a.refundAmount ?? 0)}</span>
            </div>

            <div class="d-flex align-items-center gap-3">
              <!-- Joined/Unjoined text badge -->
              <span class="badge ${a.joined ? 'bg-success' : 'bg-danger'} badge-status">
                ${a.joined ? 'Joined' : 'Unjoined'}
              </span>

              <!-- Toggle switch -->
              <div class="form-check form-switch m-0">
                <input
                  class="form-check-input join-switch"
                  type="checkbox"
                  role="switch"
                  ${a.joined ? 'checked' : ''}
                  aria-label="Toggle joined for ${a.memberName}"
                  data-attendance-id="${a.attendanceId}"
                />
              </div>
            </div>
          </li>
        `).join('')}
      </ul>
      <div class="card-footer d-flex justify-content-between align-items-center">
        <span class="small text-muted joined-count">${joinedCount}/${attendees.length} joined</span>
        <span class="small text-muted">${parts.year}-${pad2(parts.month)}-${pad2(parts.day)}</span>
      </div>
    </div>
  `;
}

// ---------------- PATCH helper ----------------

async function patchAttendance(attendanceId, joined) {
  const api = window.API;
  if (!api || typeof api.join !== 'function') {
    throw new Error('API helper is not available. Ensure config.js is loaded before schedules.js.');
  }
  const url = api.join(`/attendances/${attendanceId}`);

  const res = await fetch(url, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ joined }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Failed to update attendance #${attendanceId}: ${res.status} ${res.statusText}${text ? ' - ' + text : ''}`);
  }

  // IMPORTANT: backend wraps result in { data: { ... } }
  const json = await res.json();
  if (!json || typeof json !== 'object' || !json.data) {
    // fallback if nothing returned
    return { attendanceId, joined };
  }
  return json.data; // { attendanceId, joined, memberId, memberName, refundAmount }
}


// ---------------- Event delegation for toggles ----------------

function bindToggleHandler() {
  const grid = document.getElementById('grid');
  if (!grid) return;

  grid.addEventListener('change', async (evt) => {
    const input = evt.target.closest('.join-switch');
    if (!input) return;

    const attendanceId = input.dataset.attendanceId;
    const optimisticJoined = input.checked;

    // DOM references
    const li = input.closest('li.list-group-item');
    const icon = li.querySelector('.joined-icon');
    const statusBadge = li.querySelector('.badge-status');
    const refundBadge = li.querySelector('.refund-badge');
    const card = input.closest('.card');
    const joinedCountEl = card.querySelector('.joined-count');

    // Disable to prevent double submits
    input.disabled = true;

    // Optimistic UI update first
    icon.classList.toggle('joined-true', optimisticJoined);
    icon.classList.toggle('joined-false', !optimisticJoined);
    icon.textContent = optimisticJoined ? '✓' : '✕';
    statusBadge.className = `badge ${optimisticJoined ? 'bg-success' : 'bg-danger'} badge-status`;
    statusBadge.textContent = optimisticJoined ? 'Joined' : 'Unjoined';

    try {
      const updated = await patchAttendance(attendanceId, optimisticJoined);
      const finalJoined = !!updated.joined;

      // Align UI with server response (in case backend overrides)
      input.checked = finalJoined;
      icon.classList.toggle('joined-true', finalJoined);
      icon.classList.toggle('joined-false', !finalJoined);
      icon.textContent = finalJoined ? '✓' : '✕';
      statusBadge.className = `badge ${finalJoined ? 'bg-success' : 'bg-danger'} badge-status`;
      statusBadge.textContent = finalJoined ? 'Joined' : 'Unjoined';

      // ✅ Reflect refund amount immediately
      if (refundBadge) {
        const amount = Number(updated.refundAmount ?? 0);
        refundBadge.textContent = `Refund: ${amount}`;

        // Optional: highlight the change briefly
        refundBadge.classList.add('refund-updated');
        setTimeout(() => refundBadge.classList.remove('refund-updated'), 900);
      }

      // Recompute joined count in this card
      const switches = card.querySelectorAll('.join-switch');
      let count = 0;
      switches.forEach(sw => { if (sw.checked) count++; });
      joinedCountEl.textContent = `${count}/${switches.length} joined`;
    } catch (err) {
      // Roll back UI if patch fails
      input.checked = !optimisticJoined;
      const rolledBack = input.checked;

      icon.classList.toggle('joined-true', rolledBack);
      icon.classList.toggle('joined-false', !rolledBack);
      icon.textContent = rolledBack ? '✓' : '✕';
      statusBadge.className = `badge ${rolledBack ? 'bg-success' : 'bg-danger'} badge-status`;
      statusBadge.textContent = rolledBack ? 'Joined' : 'Unjoined';

      console.error(err);
      showAlert('danger', err.message || 'Failed to update attendance.');
    } finally {
      input.disabled = false;
    }
  });
}


// ---------------- Data fetch ----------------
async function fetchAndRender() {
  clearAlert();
  const loading = document.getElementById('loading');
  const grid = document.getElementById('grid');
  if (loading) loading.style.display = '';
  if (grid) grid.innerHTML = '';

  try {
    const api = window.API;
    if (!api || typeof api.join !== 'function') {
      throw new Error('API helper is not available. Ensure config.js is loaded before schedules.js.');
    }
    const url = new URL(api.join('/schedules'), window.location.origin);
    url.searchParams.set('year', String(state.year));
    url.searchParams.set('month', String(state.month));
    if (state.groupId) url.searchParams.set('groupId', String(state.groupId));

    const res = await fetch(url.toString(), { headers: { 'Content-Type': 'application/json' } });
    if (!res.ok) throw new Error(`Failed to fetch schedules: ${res.status} ${res.statusText}`);

    const payload = await res.json();
    let schedules = Array.isArray(payload?.data) ? payload.data : [];

    // Client-side filter fallback
    schedules = schedules.filter(s => {
      const d = new Date(s.scheduleDate);
      return d.getFullYear() === state.year && (d.getMonth() + 1) === state.month;
    });

    // Sort by date ascending
    schedules.sort((a, b) => new Date(a.scheduleDate) - new Date(b.scheduleDate));

    state.schedules = schedules;

    if (loading) loading.style.display = 'none';
    if (!grid) return;

    if (schedules.length === 0) {
      grid.innerHTML = `
        <div class="col">
          <div class="alert alert-info">No schedules found for ${formatMonthLabel(state.year, state.month)}.</div>
        </div>`;
      return;
    }

    // Render schedule columns
    const frag = document.createDocumentFragment();
    schedules.forEach(s => {
      const col = document.createElement('div');
      col.className = 'col';
      col.innerHTML = renderScheduleCard(s);
      frag.appendChild(col);
    });
    grid.appendChild(frag);
  } catch (err) {
    console.error(err);
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'none';
    showAlert('danger', err.message || 'Unexpected error while loading schedules.');
  }
}

// ---------------- Public init ----------------
export function initSchedulesPage() {
  setTitle();
  setBackLink();
  initGroupBadge();
  initMonthControls();
  updateSubtitle();
  updateUrl();
  fetchAndRender();
  bindToggleHandler(); // enable PATCH toggle handler
}
