/* ===== StageLink API helper =====
 * Talks to the existing Django backend at /api/v1/.
 *
 * If you open these HTML files directly (file://) or from a different host
 * than the Django server, set API_BASE to the server origin, e.g.
 *   const API_BASE = "http://127.0.0.1:8000";
 * If you serve the frontend from the same origin as Django, leave it "".
 */
// Empty = call the same origin this page is served from.
// When you run serve.py, that origin proxies /api/ to Django, so this just works.
// (If you ever serve the API on a different origin WITH CORS enabled, put its URL here.)
const API_BASE = "";
const API = API_BASE + "/api/v1";

/* Read a cookie (used for Django CSRF token on protected endpoints). */
function getCookie(name) {
  const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
  return m ? decodeURIComponent(m.pop()) : "";
}

/* Build a urlencoded body from a plain object.
 * Array values are appended as repeated keys (Django getlist()). */
function toBody(data) {
  const p = new URLSearchParams();
  Object.entries(data || {}).forEach(([k, v]) => {
    if (Array.isArray(v)) v.forEach((item) => p.append(k, item));
    else if (v !== undefined && v !== null) p.append(k, v);
  });
  return p;
}

async function request(method, path, data) {
  const opts = {
    method,
    credentials: "include",
    headers: {},
  };

  if (method !== "GET") {
    opts.headers["Content-Type"] = "application/x-www-form-urlencoded";
    const csrf = getCookie("csrftoken");
    if (csrf) opts.headers["X-CSRFToken"] = csrf;
    opts.body = toBody(data).toString();
  }

  let res, json;
  try {
    res = await fetch(API + path, opts);
  } catch (e) {
    throw { status: 0, message: "Cannot reach the server. Is Django running at " + API_BASE + "?" };
  }

  try {
    json = await res.json();
  } catch (e) {
    json = {};
  }

  if (!res.ok) {
    throw {
      status: res.status,
      message: json.error || json.message || ("Request failed (" + res.status + ")"),
      data: json
    };
  }

  return json;
}

const api = {
  get: (path) => request("GET", path),
  post: (path, data) => request("POST", path, data),

  // Auth
  register: (d) => api.post("/register/", d),
  verify: (d) => api.post("/verify/", d),
  login: (d) => api.post("/login/", d),
  logout: () => api.post("/logout/", {}),
  me: () => api.get("/me/"),
  resetPassword: (d) => api.post("/reset-password/", d),
  updatePassword: (d) => api.post("/update-password/", d),

  // Groups / Teams
  groups: () => api.get("/groups/"),
  teams: () => api.get("/teams/"),
  createGroup: (d) => api.post("/groups/create/", d),
  createTeam: (d) => api.post("/teams/create/", d),

  // Events
  createEvent: (d) => api.post("/events/create/", d),
  editEvent: (id, d) => api.post("/events/" + id + "/edit/", d),
  removeEvent: (id) => api.post("/events/" + id + "/remove/", {}),
  events: () => api.get("/events/"),
};

/* ---------- small UI utilities ---------- */
function showAlert(el, type, msg) {
  if (!el) return;
  el.className = "alert " + type + " show";
  el.textContent = msg;
}
function hideAlert(el) {
  if (el) el.className = "alert";
}

/* Lightweight local cache of the signed-in user (UI hints only). */
const Session = {
  set(u) { try { sessionStorage.setItem("sl_user", JSON.stringify(u)); } catch (e) {} },
  get() { try { return JSON.parse(sessionStorage.getItem("sl_user") || "null"); } catch (e) { return null; } },
  clear() { try { sessionStorage.removeItem("sl_user"); } catch (e) {} },
};

/* Guard a protected page: load /me, redirect to login on 401. */
async function requireAuth() {
  try {
    const me = await api.me();
    Session.set(me);
    return me;
  } catch (e) {
    if (e.status === 401 || e.status === 403) {
      window.location.href = "login.html";
      return null;
    }
    throw e;
  }
}

/* Render the shared sidebar into an element with id="sidebar". */
function renderSidebar(me, active) {
  const el = document.getElementById("sidebar");
  if (!el) return;
  const link = (href, ic, label, key) =>
    `<a href="${href}" class="${active === key ? "active" : ""}"><span class="ic">${ic}</span>${label}</a>`;
  el.innerHTML = `
    <div class="brand">Stage<span>Link</span></div>
    <nav class="nav">
      ${link("profile.html", "👤", "Profile", "profile")}
      ${link("planning.html", "🗓️", "Planning", "planning")}
      ${link("create-event.html", "➕", "Create Event", "create")}
      ${link("groups-teams.html", "👥", "Groups / Teams", "groups")}
    </nav>
    <div class="me">
      <div class="name">${me ? esc(me.first_name + " " + me.last_name) : ""}</div>
      <div class="role">${me ? esc(me.role) : ""}</div>
      <button class="btn secondary sm" style="margin-top:12px;width:100%" id="logoutBtn">Log out</button>
    </div>`;
  const lb = document.getElementById("logoutBtn");
  if (lb) lb.addEventListener("click", async () => {
    try { await api.logout(); } catch (e) {}
    Session.clear();
    window.location.href = "login.html";
  });
}

/* Escape text for safe HTML insertion. */
function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

/* Pretty-print a backend datetime if present. */
function fmtDate(s) {
  if (!s) return "";
  const d = new Date(s);
  if (isNaN(d)) return s;
  return d.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}