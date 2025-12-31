
// ui/schedules.js
// Ensure ../config.js is loaded BEFORE this module so window.API exists.

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
  const target = 'feeminton/ui/index.html'; // adjust if needed
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
              <!-- 🔗 Make the member name clickable -->
              <a
                href="${apiLink(`feeminton/ui/member_details.html?memberId=${encodeURIComponent(a.memberId)}&groupId=${encodeURIComponent(s.groupId)}&groupName=${encodeURIComponent(state.groupName || '')}`)}"
                class="attendee-name text-decoration-none">${a.memberName}</a>
              <span class="badge bg-warning text-dark refund-badge">Refund: ${Number(a.refundAmount ?? 0)}</span>

            </div>
            <div class="d-flex align-items-center gap-3">
              <span class="badge ${a.joined ? 'bg-success' : 'bg-danger'} badge-status">${a.joined ? 'Joined' : 'Unjoined'}</span>
              <div class="form-check form-switch m-0">
                <input
                  class="form-check-input join-switch"
                  type="checkbox" role="switch"
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

// ---------------- Data fetch ----------------
async function fetchMonthSchedules() {
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
  return schedules;
}

async function fetchAndRender() {
  clearAlert();
  const loading = document.getElementById('loading');
  const grid = document.getElementById('grid');
  if (loading) loading.style.display = '';
  if (grid) grid.innerHTML = '';

  try {
    const schedules = await fetchMonthSchedules();
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

    // Render columns
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
    if (loading) loading.style.display = 'none';
    showAlert('danger', err.message || 'Unexpected error while loading schedules.');
  }
}

// -------- Single schedule refresh (preferred) --------
async function fetchScheduleById(scheduleId) {
  const api = window.API;
  if (!api || typeof api.join !== 'function') {
    throw new Error('API helper is not available. Ensure config.js is loaded before schedules.js.');
  }

  // Try GET /schedules/{id} first (recommended backend endpoint)
  const directUrl = api.join(`/schedules/${scheduleId}`);
  try {
    const res = await fetch(directUrl, { headers: { 'Content-Type': 'application/json' } });
    if (res.ok) {
      const json = await res.json();
      // Expect either {data: {..}} or a plain schedule object
      return json?.data || json;
    }
    // If 404 or not supported, fall back to month fetch below
  } catch (_) { /* ignore and fall back */ }

  // Fallback: re-fetch month and select the schedule by id
  const monthSchedules = await fetchMonthSchedules();
  const found = monthSchedules.find(s => String(s.id) === String(scheduleId));
  if (!found) throw new Error(`Schedule #${scheduleId} not found after refresh.`);
  return found;
}

async function refreshScheduleCard(scheduleId) {
  const card = document.querySelector(`.schedule-card[data-schedule-id="${scheduleId}"]`);
  const col = card ? card.closest('.col') : null;

  // If we can’t find the card (some edge case), just re-render the whole grid
  if (!card || !col) {
    await fetchAndRender();
    return;
  }

  // Show overlay spinner
  card.classList.add('updating');
  const spinner = document.createElement('div');
  spinner.className = 'update-spinner';
  spinner.innerHTML = `<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Updating…</span></div>`;
  card.appendChild(spinner);

  try {
    const freshSchedule = await fetchScheduleById(scheduleId);
    // Replace the entire card HTML with the fresh schedule (updates all refund amounts)
    col.innerHTML = renderScheduleCard(freshSchedule);
  } catch (err) {
    console.error(err);
    showAlert('danger', err.message || 'Failed to refresh schedule.');
    // Keep old card if refresh fails
    card.classList.remove('updating');
    spinner.remove();
  }
}

// ---------------- PATCH: use server envelope and refresh ----------------
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

  // Your backend returns { data: { attendanceId, joined, refundAmount, ... } }
  const json = await res.json();
  return json?.data || { attendanceId, joined };
}

// ---------------- Toggle handler ----------------
function bindToggleHandler() {
  const grid = document.getElementById('grid');
  if (!grid) return;

  grid.addEventListener('change', async (evt) => {
    const input = evt.target.closest('.join-switch');
    if (!input) return;

    const attendanceId = input.dataset.attendanceId;
    const li = input.closest('li.list-group-item');
    const card = input.closest('.schedule-card');
    const scheduleId = card?.dataset?.scheduleId;

    const optimisticJoined = input.checked;
    const icon = li.querySelector('.joined-icon');
    const statusBadge = li.querySelector('.badge-status');

    // Prevent double submits
    input.disabled = true;

    // Optimistic local toggle (optional)
    icon.classList.toggle('joined-true', optimisticJoined);
    icon.classList.toggle('joined-false', !optimisticJoined);
    icon.textContent = optimisticJoined ? '✓' : '✕';
    statusBadge.className = `badge ${optimisticJoined ? 'bg-success' : 'bg-danger'} badge-status`;
    statusBadge.textContent = optimisticJoined ? 'Joined' : 'Unjoined';

    try {
      // PATCH on server
      const updated = await patchAttendance(attendanceId, optimisticJoined);

      // Align the switch to server truth (in case server overrides)
      input.checked = !!updated.joined;

      // 🔁 REFRESH the entire schedule card to get new refund distribution
      if (scheduleId) {
        await refreshScheduleCard(scheduleId);
      } else {
        // Fallback if we didn't find a card
        await fetchAndRender();
      }
    } catch (err) {
      // Roll back UI on error
      input.checked = !optimisticJoined;
      icon.classList.toggle('joined-true', input.checked);
      icon.classList.toggle('joined-false', !input.checked);
      icon.textContent = input.checked ? '✓' : '✕';
      statusBadge.className = `badge ${input.checked ? 'bg-success' : 'bg-danger'} badge-status`;
      statusBadge.textContent = input.checked ? 'Joined' : 'Unjoined';

      console.error(err);
      showAlert('danger', err.message || 'Failed to update attendance.');
    } finally {
      input.disabled = false;
    }
  });
}


// Put this near your other helpers in ui/schedules.js
function apiLink(href) {
  const api = window.API;
  return (api && typeof api.link === 'function') ? api.link(href) : href;
}


//// ---- Helpers used below (you likely already have these) ----
//function pad2(n) { return String(n).padStart(2, '0'); }
//function toLocalDateParts(iso) {
//  const d = new Date(iso);
//  return {
//    year: d.getFullYear(),
//    month: d.getMonth() + 1,
//    day: d.getDate(),
//    weekday: d.toLocaleDateString(undefined, { weekday: 'short' }),
//    time: d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }),
//  };
//}
//function showAlert(type, message) {
//  const el = document.getElementById('alert');
//  el.className = `alert alert-${type}`;
//  el.textContent = message;
//  el.classList.remove('d-none');
//}
//function clearAlert() {
//  const el = document.getElementById('alert');
//  el.classList.add('d-none');
//  el.textContent = '';
//}

// ---- Add a Delete button to each card header ----
//function renderScheduleCard(s) {
//  const parts = toLocalDateParts(s.scheduleDate);
//  const attendees = Array.isArray(s.attendances) ? s.attendances.slice() : [];
//  attendees.sort((a, b) => a.memberName.localeCompare(b.memberName, undefined, { sensitivity: 'base' }));
//  const joinedCount = attendees.reduce((acc, a) => acc + (a.joined ? 1 : 0), 0);
//
//  return `
//    <div class="card schedule-card h-100 shadow-sm" data-schedule-id="${s.id}">
//      <div class="card-header d-flex justify-content-between align-items-center">
//        <div>
//          <div class="fw-bold">${parts.weekday}, ${parts.day}/${pad2(parts.month)}/${parts.year}</div>
//          <div class="small text-muted">${parts.time}</div>
//        </div>
//
//        <div class="d-flex align-items-center gap-2">
//          <span class="badge bg-secondary">ID: ${s.id}</span>
//          <button
//            class="btn btn-outline-danger btn-sm btn-delete-schedule"
//            title="Delete schedule"
//            data-schedule-id="${s.id}"
//            data-schedule-date="${parts.weekday}, ${parts.day}/${pad2(parts.month)}/${parts.year} ${parts.time}"
//          >Delete</button>
//        </div>
//      </div>
//
//      <ul class="list-group list-group-flush">
//        ${attendees.map(a => `
//          <li class="list-group-item d-flex justify-content-between align-items-center" data-attendance-id="${a.attendanceId}">
//            <div class="d-flex align-items-center gap-2">
//              <span class="joined-icon ${a.joined ? 'joined-true' : 'joined-false'}" title="${a.joined ? 'Joined' : 'Unjoined'}">${a.joined ? '✓' : '✕'}</span>
//
//              ${(window.API && window.API.link) ? window.API.link(`member-details.html?memberId=${encodeURIComponent(a.memberId)}`) : `member-details.html?memberId=${encodeURIComponent(a.memberId)}`}${a.memberName}</a>
//
//              <span class="text-muted small">#${a.memberId}</span>
//              <span class="badge bg-warning text-dark refund-badge">Refund: ${Number(a.refundAmount ?? 0)}</span>
//            </div>
//
//            <div class="d-flex align-items-center gap-3">
//              <span class="badge ${a.joined ? 'bg-success' : 'bg-danger'} badge-status">${a.joined ? 'Joined' : 'Unjoined'}</span>
//              <!-- Your toggle code can remain here -->
//            </div>
//          </li>
//        `).join('')}
//      </ul>
//
//      <div class="card-footer d-flex justify-content-between align-items-center">
//        <span class="small text-muted joined-count">${joinedCount}/${attendees.length} joined</span>
//        <span class="small text-muted">${parts.year}-${pad2(parts.month)}-${pad2(parts.day)}</span>
//      </div>
//    </div>
//  `;
//}

// ---- Delete flow: open modal -> confirm -> DELETE -> refresh ----
function bindDeleteHandlers(fetchAndRender) {
  const grid = document.getElementById('grid');
  if (!grid) return;

  grid.addEventListener('click', (evt) => {
    const btn = evt.target.closest('.btn-delete-schedule');
    if (!btn) return;

    const scheduleId = btn.dataset.scheduleId;
    const scheduleText = btn.dataset.scheduleDate;

    // Fill modal content
    const bodyEl = document.getElementById('confirmDeleteBody');
    bodyEl.textContent = `Are you sure you want to delete schedule #${scheduleId} on ${scheduleText}?`;

    const modalEl = document.getElementById('confirmDeleteModal');
    modalEl.dataset.scheduleId = scheduleId;

    // Show modal
    const modal = new bootstrap.Modal(modalEl);
    modal.show();

    // Bind confirm button for this schedule
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    const spinner = confirmBtn.querySelector('.spinner-border');

    const onConfirm = async () => {
      confirmBtn.disabled = true;
      spinner.classList.remove('d-none');

      try {
        await deleteSchedule(scheduleId);
        showAlert('success', `Schedule #${scheduleId} deleted successfully.`);

        // Hide modal
        modal.hide();

        // Refresh month list (safer) or remove just the card
        await fetchAndRender();
      } catch (err) {
        console.error(err);
        showAlert('danger', err.message || `Failed to delete schedule #${scheduleId}.`);
      } finally {
        confirmBtn.disabled = false;
        spinner.classList.add('d-none');
        // Clean listener to avoid duplications on future deletions
        confirmBtn.removeEventListener('click', onConfirm);
      }
    };

    // Attach one-shot listener
    confirmBtn.addEventListener('click', onConfirm, { once: true });
  });
}

async function deleteSchedule(scheduleId) {
  const api = window.API;
  if (!api || typeof api.join !== 'function') {
    throw new Error('API helper is not available. Ensure config.js is loaded.');
  }
  const url = api.join(`/schedules/${scheduleId}`);
  const res = await fetch(url, { method: 'DELETE', headers: { 'Content-Type': 'application/json' } });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Delete failed: ${res.status} ${res.statusText}${text ? ' - ' + text : ''}`);
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
  bindToggleHandler();  // enable PATCH handler (which refreshes schedule card)
  bindDeleteHandlers(fetchAndRender);
}
