from flask import Flask, jsonify, request, render_template_string
import time

app = Flask(__name__)

tasks = [
    {"id": 1, "title": "Write unit tests",      "done": False, "priority": "high",   "created": int(time.time()) - 7200},
    {"id": 2, "title": "Set up Docker pipeline", "done": True,  "priority": "high",   "created": int(time.time()) - 3600},
    {"id": 3, "title": "Review pull requests",   "done": False, "priority": "medium", "created": int(time.time()) - 1800},
    {"id": 4, "title": "Update documentation",   "done": False, "priority": "low",    "created": int(time.time()) - 900},
]
_next_id = 5

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Taskboard</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:        #0d0f14;
    --surface:   #14171f;
    --card:      #1a1e28;
    --border:    rgba(255,255,255,0.07);
    --border-h:  rgba(255,255,255,0.14);
    --txt:       #e8eaf0;
    --muted:     #5a5f72;
    --accent:    #6c63ff;
    --accent-g:  #8b85ff;
    --hi:        #ff6b6b;
    --med:       #ffd166;
    --lo:        #06d6a0;
    --done-op:   0.38;
    --radius:    12px;
  }

  body {
    font-family: 'DM Mono', monospace;
    background: var(--bg);
    color: var(--txt);
    min-height: 100vh;
    padding: 0 0 80px;
  }

  /* ── header ── */
  header {
    position: sticky; top: 0; z-index: 100;
    background: rgba(13,15,20,0.85);
    backdrop-filter: blur(18px);
    border-bottom: 1px solid var(--border);
    padding: 18px 40px;
    display: flex; align-items: center; justify-content: space-between;
  }

  .logo {
    font-family: 'Syne', sans-serif;
    font-size: 22px; font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #fff 30%, var(--accent-g));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }

  .stats {
    display: flex; gap: 24px;
  }
  .stat-pill {
    font-size: 11px; letter-spacing: 0.06em;
    color: var(--muted);
    display: flex; align-items: center; gap: 6px;
  }
  .stat-pill b { color: var(--txt); font-weight: 500; }

  /* ── main layout ── */
  .container { max-width: 780px; margin: 0 auto; padding: 40px 24px 0; }

  /* ── add form ── */
  .add-bar {
    display: flex; gap: 10px; margin-bottom: 36px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 10px 10px 10px 18px;
    transition: border-color .2s;
  }
  .add-bar:focus-within { border-color: var(--accent); }

  .add-bar input[type="text"] {
    flex: 1; background: none; border: none; outline: none;
    font-family: inherit; font-size: 14px; color: var(--txt);
    caret-color: var(--accent);
  }
  .add-bar input::placeholder { color: var(--muted); }

  .priority-select {
    background: var(--card); border: 1px solid var(--border);
    color: var(--muted); font-family: inherit; font-size: 11px;
    border-radius: 6px; padding: 4px 8px; cursor: pointer;
    outline: none; letter-spacing: .04em;
  }

  .btn-add {
    background: var(--accent); color: #fff;
    border: none; border-radius: 8px;
    padding: 8px 20px; font-family: inherit;
    font-size: 13px; font-weight: 500;
    cursor: pointer; letter-spacing: .03em;
    transition: background .2s, transform .1s;
  }
  .btn-add:hover { background: var(--accent-g); }
  .btn-add:active { transform: scale(0.97); }

  /* ── filter bar ── */
  .filters {
    display: flex; gap: 8px; margin-bottom: 22px; flex-wrap: wrap;
  }
  .filter-btn {
    font-family: inherit; font-size: 11px; letter-spacing: .05em;
    padding: 5px 14px; border-radius: 20px; cursor: pointer;
    border: 1px solid var(--border);
    background: transparent; color: var(--muted);
    transition: all .18s;
  }
  .filter-btn:hover, .filter-btn.active {
    background: var(--accent); color: #fff; border-color: var(--accent);
  }

  /* ── section label ── */
  .section-label {
    font-size: 10px; letter-spacing: .12em; color: var(--muted);
    text-transform: uppercase; margin-bottom: 10px;
    padding-left: 2px;
  }

  /* ── task list ── */
  #task-list { display: flex; flex-direction: column; gap: 8px; }

  .task-card {
    display: flex; align-items: center; gap: 14px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 16px;
    transition: border-color .2s, background .2s, opacity .3s;
    animation: slideIn .22s ease both;
  }
  .task-card:hover { border-color: var(--border-h); background: #1f2333; }
  .task-card.done  { opacity: var(--done-op); }

  @keyframes slideIn {
    from { opacity: 0; transform: translateY(-8px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  /* checkbox */
  .task-check {
    width: 20px; height: 20px; border-radius: 6px;
    border: 2px solid var(--border-h);
    background: none; cursor: pointer;
    appearance: none; flex-shrink: 0;
    transition: background .18s, border-color .18s;
    position: relative;
  }
  .task-check:checked {
    background: var(--accent); border-color: var(--accent);
  }
  .task-check:checked::after {
    content: '';
    position: absolute; top: 3px; left: 6px;
    width: 5px; height: 9px;
    border: 2px solid #fff; border-top: none; border-left: none;
    transform: rotate(45deg);
  }

  .task-title {
    flex: 1; font-size: 14px; line-height: 1.4;
    transition: color .2s;
    word-break: break-word;
  }
  .task-card.done .task-title {
    text-decoration: line-through; color: var(--muted);
  }

  .priority-dot {
    width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
  }
  .p-high   { background: var(--hi); }
  .p-medium { background: var(--med); }
  .p-low    { background: var(--lo); }

  .task-meta {
    font-size: 10px; color: var(--muted); white-space: nowrap;
  }

  .btn-del {
    background: none; border: none; cursor: pointer;
    color: var(--muted); font-size: 16px; line-height: 1;
    padding: 2px 4px; border-radius: 4px;
    transition: color .18s, background .18s;
    flex-shrink: 0;
  }
  .btn-del:hover { color: var(--hi); background: rgba(255,107,107,.1); }

  /* ── progress bar ── */
  .progress-wrap {
    margin-bottom: 28px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px; padding: 14px 18px;
  }
  .progress-header {
    display: flex; justify-content: space-between;
    font-size: 11px; letter-spacing: .05em; color: var(--muted); margin-bottom: 10px;
  }
  .progress-bar-bg {
    height: 6px; background: var(--border); border-radius: 10px; overflow: hidden;
  }
  .progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent), var(--accent-g));
    border-radius: 10px;
    transition: width .5s cubic-bezier(.4,0,.2,1);
  }

  /* ── empty state ── */
  .empty {
    text-align: center; color: var(--muted);
    padding: 60px 0; font-size: 13px;
  }
  .empty span { display: block; font-size: 32px; margin-bottom: 12px; }

  /* ── toast ── */
  #toast {
    position: fixed; bottom: 28px; left: 50%; transform: translateX(-50%) translateY(20px);
    background: var(--surface); border: 1px solid var(--border-h);
    color: var(--txt); font-family: 'DM Mono', monospace; font-size: 12px;
    padding: 10px 22px; border-radius: 20px;
    opacity: 0; transition: opacity .25s, transform .25s;
    pointer-events: none; white-space: nowrap;
  }
  #toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
</style>
</head>
<body>

<header>
  <div class="logo">taskboard_</div>
  <div class="stats">
    <div class="stat-pill">total <b id="s-total">0</b></div>
    <div class="stat-pill">done <b id="s-done">0</b></div>
    <div class="stat-pill">pending <b id="s-pending">0</b></div>
  </div>
</header>

<div class="container">

  <!-- Add form -->
  <div class="add-bar">
    <input type="text" id="new-title" placeholder="Add a new task…" maxlength="120"
           onkeydown="if(event.key==='Enter') addTask()">
    <select id="new-priority" class="priority-select">
      <option value="high">!! high</option>
      <option value="medium" selected>·· medium</option>
      <option value="low">__ low</option>
    </select>
    <button class="btn-add" onclick="addTask()">+ add</button>
  </div>

  <!-- Progress -->
  <div class="progress-wrap">
    <div class="progress-header">
      <span>completion</span>
      <span id="pct-label">0%</span>
    </div>
    <div class="progress-bar-bg">
      <div class="progress-bar-fill" id="prog-fill" style="width:0%"></div>
    </div>
  </div>

  <!-- Filters -->
  <div class="filters">
    <button class="filter-btn active" data-filter="all"     onclick="setFilter(this)">all</button>
    <button class="filter-btn"        data-filter="pending" onclick="setFilter(this)">pending</button>
    <button class="filter-btn"        data-filter="done"    onclick="setFilter(this)">done</button>
    <button class="filter-btn"        data-filter="high"    onclick="setFilter(this)">!! high</button>
    <button class="filter-btn"        data-filter="medium"  onclick="setFilter(this)">·· medium</button>
    <button class="filter-btn"        data-filter="low"     onclick="setFilter(this)">__ low</button>
  </div>

  <div class="section-label">tasks</div>
  <div id="task-list"></div>
</div>

<div id="toast"></div>

<script>
let tasks = [];
let currentFilter = 'all';

// ── API helpers ──────────────────────────────────────────────────
async function api(method, path, body) {
  const r = await fetch(path, {
    method,
    headers: body ? {'Content-Type':'application/json'} : {},
    body: body ? JSON.stringify(body) : undefined
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

// ── Load tasks ───────────────────────────────────────────────────
async function loadTasks() {
  tasks = await api('GET', '/api/tasks');
  render();
}

// ── Add task ─────────────────────────────────────────────────────
async function addTask() {
  const titleEl = document.getElementById('new-title');
  const title = titleEl.value.trim();
  if (!title) { titleEl.focus(); return; }
  const priority = document.getElementById('new-priority').value;
  const t = await api('POST', '/api/tasks', { title, priority });
  tasks.unshift(t);
  titleEl.value = '';
  render();
  toast('Task added');
}

// ── Toggle done ──────────────────────────────────────────────────
async function toggleTask(id, done) {
  const t = await api('PATCH', `/api/tasks/${id}`, { done });
  const idx = tasks.findIndex(x => x.id === id);
  if (idx !== -1) tasks[idx] = t;
  render();
  toast(done ? 'Marked complete ✓' : 'Marked pending');
}

// ── Delete task ──────────────────────────────────────────────────
async function deleteTask(id) {
  await api('DELETE', `/api/tasks/${id}`);
  tasks = tasks.filter(t => t.id !== id);
  render();
  toast('Task removed');
}

// ── Filter ───────────────────────────────────────────────────────
function setFilter(btn) {
  currentFilter = btn.dataset.filter;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  render();
}

function filteredTasks() {
  return tasks.filter(t => {
    if (currentFilter === 'all')    return true;
    if (currentFilter === 'pending') return !t.done;
    if (currentFilter === 'done')    return t.done;
    return t.priority === currentFilter;
  });
}

// ── Render ───────────────────────────────────────────────────────
function timeAgo(ts) {
  const s = Math.floor(Date.now()/1000 - ts);
  if (s < 60)   return 'just now';
  if (s < 3600) return Math.floor(s/60) + 'm ago';
  if (s < 86400)return Math.floor(s/3600) + 'h ago';
  return Math.floor(s/86400) + 'd ago';
}

function render() {
  const list = document.getElementById('task-list');
  const visible = filteredTasks();

  // stats
  const total   = tasks.length;
  const done    = tasks.filter(t => t.done).length;
  const pending = total - done;
  document.getElementById('s-total').textContent   = total;
  document.getElementById('s-done').textContent    = done;
  document.getElementById('s-pending').textContent = pending;

  // progress
  const pct = total ? Math.round(done/total*100) : 0;
  document.getElementById('prog-fill').style.width = pct + '%';
  document.getElementById('pct-label').textContent = pct + '%';

  if (!visible.length) {
    list.innerHTML = `<div class="empty"><span>○</span>no tasks here</div>`;
    return;
  }

  list.innerHTML = visible.map(t => `
    <div class="task-card ${t.done ? 'done' : ''}" id="card-${t.id}">
      <input type="checkbox" class="task-check" ${t.done ? 'checked' : ''}
             onchange="toggleTask(${t.id}, this.checked)">
      <div class="priority-dot p-${t.priority}"></div>
      <span class="task-title">${escHtml(t.title)}</span>
      <span class="task-meta">${timeAgo(t.created)}</span>
      <button class="btn-del" onclick="deleteTask(${t.id})" title="Delete">×</button>
    </div>
  `).join('');
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── Toast ────────────────────────────────────────────────────────
let _toastTimer;
function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => el.classList.remove('show'), 2200);
}

// ── Boot ─────────────────────────────────────────────────────────
loadTasks();
setInterval(render, 30000);   // refresh timestamps every 30 s
</script>
</body>
</html>
"""

# ── API routes ──────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)

@app.route("/api/tasks", methods=["POST"])
def add_task():
    global _next_id
    data = request.json or {}
    if not data.get("title", "").strip():
        return jsonify({"error": "title required"}), 400
    task = {
        "id":       _next_id,
        "title":    data["title"].strip(),
        "done":     False,
        "priority": data.get("priority", "medium"),
        "created":  int(time.time()),
    }
    _next_id += 1
    tasks.append(task)
    return jsonify(task), 201

@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "not found"}), 404
    data = request.json or {}
    if "done"     in data: task["done"]     = bool(data["done"])
    if "title"    in data: task["title"]    = data["title"].strip()
    if "priority" in data: task["priority"] = data["priority"]
    return jsonify(task)

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    before = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) == before:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": task_id})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)