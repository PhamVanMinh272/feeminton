
// ---------- Helpers ----------
const qs = new URLSearchParams(window.location.search);
const groupId   = qs.get('groupId') || '';
const groupName = qs.get('groupName') || '';
const yearQS    = qs.get('year') || String(new Date().getFullYear());
const monthQS   = qs.get('month') || String(new Date().getMonth() + 1);

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
function isoFromDateTimeLocal(value) {
  // value like "2025-12-20T14:48"
  // Create ISO string without timezone offset (server can treat as local or UTC)
  const d = new Date(value);
  // Ensure seconds and milliseconds trimmed
  const yyyy = d.getFullYear();
  const mm   = String(d.getMonth() + 1).padStart(2, '0');
  const dd   = String(d.getDate()).padStart(2, '0');
  const hh   = String(d.getHours()).padStart(2, '0');
  const mi   = String(d.getMinutes()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}T${hh}:${mi}:00`;
}
function buildISO(year, month, day, timeHHMM) {
  const [hh, mi] = timeHHMM.split(':').map(Number);
  const d = new Date(year, month - 1, day, hh, mi, 0);
  const yyyy = d.getFullYear();
  const mm   = String(d.getMonth() + 1).padStart(2, '0');
  const dd   = String(d.getDate()).padStart(2, '0');
  const hh2  = String(d.getHours()).padStart(2, '0');
  const mi2  = String(d.getMinutes()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}T${hh2}:${mi2}:00`;
}
function daysInMonth(year, month) {
  return new Date(year, month, 0).getDate();
}

// ---------- Init UI ----------
document.getElementById('title').textContent = groupName ? `Create Schedule • ${groupName} (#${groupId})` : 'Create Schedule';
document.getElementById('subtitle').textContent = `Target month: ${yearQS}-${String(monthQS).padStart(2, '0')}`;
document.getElementById('backLink').href = API.link(`feeminton/ui/schedules.html?groupId=${encodeURIComponent(groupId)}&groupName=${encodeURIComponent(groupName)}&year=${encodeURIComponent(yearQS)}&month=${encodeURIComponent(monthQS)}`);

// Prefill groupId
document.getElementById('singleGroupId').value = groupId || '';
document.getElementById('recurringGroupId').value = groupId || '';

// Default recurring month selector to query month
const recurringMonthInput = document.getElementById('recurringMonth');
recurringMonthInput.value = `${yearQS}-${String(monthQS).padStart(2, '0')}`;

// ---------- POST helpers ----------
async function postSchedule(scheduleDateISO, groupIdNum) {
  const url = API.join('/schedules');
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scheduleDate: scheduleDateISO, groupId: Number(groupIdNum) }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Failed to create schedule: ${res.status} ${res.statusText}${text ? ' - ' + text : ''}`);
  }
  return res.json(); // assuming { data: {...} } or created resource
}

// ---------- Single submission ----------
document.getElementById('singleForm').addEventListener('submit', async (evt) => {
  evt.preventDefault();
  clearAlert();

  const dtValue = document.getElementById('singleDateTime').value;
  const groupIdVal = document.getElementById('singleGroupId').value;
  if (!dtValue || !groupIdVal) {
    showAlert('warning', 'Please fill Date & Time and Group ID.');
    return;
  }

  const scheduleISO = isoFromDateTimeLocal(dtValue);
  try {
    await postSchedule(scheduleISO, groupIdVal);
    // Success → go back to schedules for the same group/month
    window.location.href = API.link(`feeminton/ui/schedules.html?groupId=${encodeURIComponent(groupId)}&groupName=${encodeURIComponent(groupName)}&year=${encodeURIComponent(yearQS)}&month=${encodeURIComponent(monthQS)}`);
  } catch (err) {
    console.error(err);
    showAlert('danger', err.message || 'Error creating schedule.');
  }
});

// ---------- Recurring submission ----------
document.getElementById('recurringForm').addEventListener('submit', async (evt) => {
  evt.preventDefault();
  clearAlert();

  const ymVal = recurringMonthInput.value; // "YYYY-MM"
  const timeVal = document.getElementById('recurringTime').value; // "HH:MM"
  const groupIdVal = document.getElementById('recurringGroupId').value;

  if (!ymVal || !timeVal || !groupIdVal) {
    showAlert('warning', 'Please fill Month, Time and Group ID.');
    return;
  }

  // Collect selected DOWs (0=Sun .. 6=Sat)
  const dowInputs = Array.from(document.querySelectorAll('.weekday-list .form-check-input'));
  const selectedDOW = dowInputs.filter(i => i.checked).map(i => Number(i.value));
  if (selectedDOW.length === 0) {
    showAlert('warning', 'Please choose at least one day of the week.');
    return;
  }

  const [yStr, mStr] = ymVal.split('-');
  const year = Number(yStr);
  const month = Number(mStr);
  const days = daysInMonth(year, month);

  // Build all ISO timestamps for selected DOWs in the month
  const toCreate = [];
  for (let day = 1; day <= days; day++) {
    const d = new Date(year, month - 1, day);
    const dow = d.getDay(); // 0=Sun..6=Sat
    if (selectedDOW.includes(dow)) {
      toCreate.push(buildISO(year, month, day, timeVal));
    }
  }

  if (toCreate.length === 0) {
    showAlert('info', 'No matching days in the selected month.');
    return;
  }

  // Submit all (sequentially to keep server happy; switch to Promise.all if backend tolerates parallel)
  try {
    for (const iso of toCreate) {
      await postSchedule(iso, groupIdVal);
    }
    // Success → back to schedules page
    window.location.href = API.link(`feeminton/ui/schedules.html?groupId=${encodeURIComponent(groupId)}&groupName=${encodeURIComponent(groupName)}&year=${encodeURIComponent(year)}&month=${encodeURIComponent(month)}`);
  } catch (err) {
    console.error(err);
    showAlert('danger', err.message || 'Error creating one or more schedules.');
  }
});