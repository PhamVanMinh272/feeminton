

(function (global) {
const qs = new URLSearchParams(window.location.search);
function detectApiBase() {
  const host = window.location.hostname;

  if (host === 'localhost' || host === '127.0.0.1') {
    return 'http://127.0.0.1:5000/api'; // local backend
  }
  if (host.includes('feeminton-website')) {
    return 'https://gvtvwamhvf.execute-api.us-west-2.amazonaws.com/dev/api';
  }
  return 'https://gvtvwamhvf.execute-api.us-west-2.amazonaws.com/prod/api';
}

const DEFAULT_API_BASE = detectApiBase();
//const DEFAULT_API_BASE = 'http://127.0.0.1:5000/api';
//const DEFAULT_API_BASE = 'https://gvtvwamhvf.execute-api.us-west-2.amazonaws.com/dev/api';
const apiFromQuery = qs.get('api');

// Normalize base to avoid double/missing slashes
function normalize(base) {
  return base.endsWith('/') ? base : base + '/';
}
const API_BASE = normalize(apiFromQuery || DEFAULT_API_BASE);

function join(path) {
  const left = API_BASE.replace(/\/$/, '');
  const right = String(path || '').replace(/^\//, '');
  return `${left}/${right}`;
}

// Build links for navigation while preserving the api base across pages
//function link(href) {
//  // Keep same server path; only add/merge the 'api' query arg
//  const url = new URL(href, window.location.origin);
//  const currentPath = url.pathname; // ensures relative path stays
//  const merged = new URL(window.location.origin + currentPath);
//  const existingQs = new URLSearchParams(url.search);
//  existingQs.set('api', API_BASE.replace(/\/$/, '')); // store without trailing slash in param
//  merged.search = existingQs.toString();
//  return merged.pathname + (merged.search ? merged.search : '');
//}

function link(href) {
  const url = new URL(href, window.location.href); // resolve relative to current page
  const qs = new URLSearchParams(url.search);
  qs.set('api', API_BASE.replace(/\/$/, ''));
  url.search = qs.toString();
  return url.pathname + (url.search ? url.search : '');
}

global.API = {
  base: API_BASE,
  join, // API.join('/groups') => http://127.0.0.1:5000/api/groups
  link, // API.link('schedules.html?...') ensures api=... is carried over
};
})(window);

