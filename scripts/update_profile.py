import os
import json
import urllib.request
from datetime import datetime

USERNAME = "hans-cdm"
API_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=pushed"

LANG_BADGES = {
    "JavaScript": "🟨 JavaScript",
    "TypeScript": "🔷 TypeScript",
    "PHP": "🐘 PHP",
    "Python": "🐍 Python",
    "HTML": "🌐 HTML",
    "CSS": "🎨 CSS",
    "Java": "☕ Java",
    "Kotlin": "🟣 Kotlin",
    "C++": "🔵 C++",
    "C": "⚙️ C",
    "Dart": "🎯 Dart",
    "Go": "🐹 Go",
    "Rust": "🦀 Rust",
    "Tcl": "📜 Tcl",
    "Shell": "🐚 Shell",
}

def format_relative_time(iso_str):
    if not iso_str:
        return "—"
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    now = datetime.now(dt.tzinfo)
    diff = now - dt
    days = diff.days
    if days == 0:
        hours = diff.seconds // 3600
        return f"{hours}h ago" if hours > 0 else "just now"
    elif days < 30:
        return f"{days}d ago"
    elif days < 365:
        months = days // 30
        return f"{months}mo ago"
    else:
        years = days // 365
        return f"{years}y ago"

def fetch_repos():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    req = urllib.request.Request(API_URL)
    req.add_header("User-Agent", "Mozilla/5.0")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching repos via API: {e}")
        try:
            import subprocess
            out = subprocess.check_output(["gh", "api", f"users/{USERNAME}/repos?per_page=100&sort=pushed"], text=True)
            return json.loads(out)
        except Exception as e2:
            print(f"Error calling gh CLI: {e2}")
            return []

def analyze_profile(repos):
    languages = {}
    categories = {"bot": 0, "app": 0, "mod": 0, "web": 0, "tugas": 0, "tool": 0}
    public_repos = []

    for r in repos:
        if r["name"].lower() == USERNAME.lower():
            continue
        
        lang = r.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
        
        name_lower = r["name"].lower()
        desc_lower = (r.get("description") or "").lower()
        text = f"{name_lower} {desc_lower}"

        if "bot" in text:
            categories["bot"] += 1
        if "app" in text or "apk" in text or "aplikasi" in text:
            categories["app"] += 1
        if "mod" in text or "magisk" in text or "ksu" in text:
            categories["mod"] += 1
        if "web" in text or "html" in text or "css" in text or "php" in text:
            categories["web"] += 1
        if "tugas" in text:
            categories["tugas"] += 1
        
        public_repos.append(r)

    total_projects = len(public_repos)
    specialization = "Masa Eksplorasi / Belum Terspesialisasi"
    
    if total_projects >= 4:
        max_cat = max(categories, key=categories.get)
        count = categories[max_cat]
        if count / total_projects >= 0.4 and count >= 3:
            labels = {
                "bot": "Bot & Automation Development",
                "app": "Application & Mobile Engineering",
                "mod": "Modding & Reverse Engineering",
                "web": "Web & Backend Development",
                "tugas": "Academic & Project Studies"
            }
            specialization = labels.get(max_cat, "Masa Eksplorasi")

    return languages, categories, public_repos, specialization

def update_telemetry_svg(languages, public_repos, base_dir):
    total_repos = len(public_repos)
    total_langs = len(languages)
    total_stars = sum(r.get("stargazers_count", 0) for r in public_repos)

    # Hitung lebar spektrum (total 412 width)
    # Warna untuk bahasa
    colors = {
        "JavaScript": "#eab308",
        "PHP": "#6366f1",
        "TypeScript": "#0284c7",
        "Tcl": "#14b8a6",
        "Python": "#3b82f6",
        "HTML": "#f97316",
        "Java": "#ea580c"
    }

    svg_path = os.path.join(base_dir, "assets", "telemetry-card.svg")
    if not os.path.exists(svg_path):
        return

    # Hitung porsi masing-masing bahasa
    total_lang_repos = sum(languages.values()) or 1
    bar_segments = []
    current_x = 0
    total_width = 412
    
    legend_items = []
    legend_x = 0

    for lang, count in languages.items():
        pct = count / total_lang_repos
        w = max(int(pct * total_width), 8)
        color = colors.get(lang, "#10b981")
        bar_segments.append(f'<rect x="{current_x}" y="0" width="{w}" height="10" rx="3" fill="{color}" />')
        current_x += w

        legend_items.append(f'<circle cx="{legend_x + 4}" cy="0" r="3" fill="{color}" />')
        legend_items.append(f'<text x="{legend_x + 12}" y="3" fill="#cbd5e1">{lang}</text>')
        legend_x += 85

    bars_markup = "\n      ".join(bar_segments)
    legend_markup = "\n      ".join(legend_items)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 340" width="100%" height="340">
  <defs>
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080c14" />
      <stop offset="50%" stop-color="#0c111c" />
      <stop offset="100%" stop-color="#080c14" />
    </linearGradient>

    <linearGradient id="metricBoxBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0e1726" />
      <stop offset="100%" stop-color="#090f1a" />
    </linearGradient>

    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <style>
    .mono {{ font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace; }}
  </style>

  <!-- Outer Window Frame -->
  <rect x="2" y="2" width="456" height="336" rx="10" fill="url(#cardBg)" stroke="#1e293b" stroke-width="1.5" />

  <!-- Window Header -->
  <rect x="2" y="2" width="456" height="30" rx="10" fill="#0f172a" />
  <rect x="2" y="20" width="456" height="10" fill="#0f172a" />
  <line x1="2" y1="30" x2="458" y2="30" stroke="#1e293b" stroke-width="1" />

  <!-- Action Dots -->
  <circle cx="16" cy="16" r="4.5" fill="#ef4444" />
  <circle cx="30" cy="16" r="4.5" fill="#f59e0b" />
  <circle cx="44" cy="16" r="4.5" fill="#10b981" />

  <text x="230" y="20" text-anchor="middle" fill="#64748b" font-size="11" class="mono">
    hans-cdm@study-desk: ~ (stats)
  </text>

  <!-- Title & Subtitle -->
  <text x="24" y="58" fill="#10b981" font-size="12" font-weight="700" class="mono" letter-spacing="0.5">
    LIBRARY TELEMETRY &amp; METRICS
  </text>
  <text x="24" y="74" fill="#64748b" font-size="10.5" class="mono">
    Workstation &amp; GitHub workspace telemetry
  </text>

  <!-- 2x2 Metric Grid -->
  <g transform="translate(24, 88)">
    <g transform="translate(0, 0)">
      <rect x="0" y="0" width="198" height="54" rx="6" fill="url(#metricBoxBg)" stroke="#1e293b" />
      <text x="14" y="20" fill="#38bdf8" font-size="10" class="mono">📚 VOLUMES (REPOS)</text>
      <text x="14" y="42" fill="#f8fafc" font-size="16" font-weight="800" class="mono">{total_repos} <tspan fill="#64748b" font-size="11" font-weight="400">shelved</tspan></text>
    </g>

    <g transform="translate(214, 0)">
      <rect x="0" y="0" width="198" height="54" rx="6" fill="url(#metricBoxBg)" stroke="#1e293b" />
      <text x="14" y="20" fill="#10b981" font-size="10" class="mono">🌿 CONTRIBUTIONS</text>
      <text x="14" y="42" fill="#f8fafc" font-size="16" font-weight="800" class="mono">47+ <tspan fill="#64748b" font-size="11" font-weight="400">commits</tspan></text>
    </g>

    <g transform="translate(0, 64)">
      <rect x="0" y="0" width="198" height="54" rx="6" fill="url(#metricBoxBg)" stroke="#1e293b" />
      <text x="14" y="20" fill="#f59e0b" font-size="10" class="mono">⭐ TOTAL STARS</text>
      <text x="14" y="42" fill="#f8fafc" font-size="16" font-weight="800" class="mono">{total_stars} <tspan fill="#64748b" font-size="11" font-weight="400">stars</tspan></text>
    </g>

    <g transform="translate(214, 64)">
      <rect x="0" y="0" width="198" height="54" rx="6" fill="url(#metricBoxBg)" stroke="#1e293b" />
      <text x="14" y="20" fill="#a855f7" font-size="10" class="mono">⚡ UNLOCKED STACK</text>
      <text x="14" y="42" fill="#f8fafc" font-size="16" font-weight="800" class="mono">{total_langs} <tspan fill="#64748b" font-size="11" font-weight="400">languages</tspan></text>
    </g>
  </g>

  <!-- Stack Spectrum Progress Bar -->
  <g transform="translate(24, 222)">
    <text x="0" y="0" fill="#94a3b8" font-size="10" font-weight="600" class="mono" letter-spacing="0.5">
      STACK SPECTRUM (ACTIVE REPOS)
    </text>

    <g transform="translate(0, 10)">
      <rect x="0" y="0" width="412" height="10" rx="5" fill="#1e293b" />
      {bars_markup}
    </g>

    <g transform="translate(0, 36)" class="mono" font-size="9.5">
      {legend_markup}
    </g>
  </g>

  <!-- Footer Status Bar -->
  <g transform="translate(24, 288)">
    <rect x="0" y="0" width="412" height="26" rx="5" fill="#0a0f18" stroke="#1e293b" />
    <circle cx="14" cy="13" r="3.5" fill="#10b981" filter="url(#softGlow)" />
    <text x="24" y="17" fill="#64748b" font-size="9.5" class="mono">
      HOST: WINDOWS 11 <tspan fill="#334155">|</tspan> CPU: RYZEN 5 6600H <tspan fill="#334155">|</tspan> ONLINE // zen
    </text>
  </g>
</svg>"""

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("telemetry-card.svg berhasil di-update.")

def generate_readme(languages, public_repos, specialization):
    active_langs_str = " | ".join(languages.keys()) if languages else "Exploring"
    
    # Generate Repos Table
    repo_rows = []
    for r in public_repos:
        name = r["name"]
        url = r["html_url"]
        desc = r.get("description") or "*Belum ada deskripsi*"
        lang = r.get("language")
        badge = LANG_BADGES.get(lang, lang) if lang else "—"
        stars = f"★ {r['stargazers_count']}" if r["stargazers_count"] > 0 else "—"
        pushed = format_relative_time(r.get("pushed_at"))
        
        row = f"| **[`{USERNAME} / {name}`]({url})** | {desc} | {badge} | `{stars}` | `{pushed}` |"
        repo_rows.append(row)
    
    repos_table = "\n".join(repo_rows)

    # Generate Unlocked Tech Stack Tree
    lang_tree = []
    lang_descriptions = {
        "JavaScript": "Modern asynchronous services, bots, and web interactivity",
        "TypeScript": "Type-safe development and scalable architecture",
        "PHP": "Server-side web scripting and backend endpoints",
        "Python": "Automation scripting, data tools, and bots",
        "HTML": "Semantic web markup and portfolio interfaces",
        "CSS": "Responsive styling and modern dark-mode layouts",
        "Java": "Object-oriented software and Android foundation",
        "Kotlin": "Modern Android application engineering",
        "C++": "High-performance low-level systems & native libraries",
        "Tcl": "Scripting, tooling, and command execution"
    }

    total_langs = len(languages)
    for idx, (lang, count) in enumerate(languages.items()):
        is_last = (idx == total_langs - 1)
        prefix = "└──" if is_last else "├──"
        desc = lang_descriptions.get(lang, f"Used across {count} repository/projects")
        lang_tree.append(f"│   {prefix} {lang:<16} ── {desc} ({count} repo)")

    lang_tree_str = "\n".join(lang_tree) if lang_tree else "│   └── Belum ada bahasa yang terdaftar di repository"

    content = f"""<div align="center">

<img src="./assets/banner.svg" alt="hans-cdm Bookshelf Banner" width="100%" />

</div>

---

### 💻 System Specs & Environment

```text
████████   ████████      hans-cdm@workstation
████████   ████████     ----------------------
████████   ████████     OS: Windows 11 Home (64-bit)
████████   ████████     Host/CPU: AMD Ryzen 5 6600H (6C/12T)
                        Memory: 16 GB DDR5
████████   ████████     Shell: PowerShell 5.1 / Windows Terminal
████████   ████████     Active Stack: {active_langs_str}
████████   ████████     Specialization: [{specialization}]
████████   ████████     Growth Status: Continuous Evolution 🌱
```

---

### 📊 Activity & Telemetry

<div align="center">
<table border="0" width="100%">
  <tr>
    <td width="50%" align="center" valign="top">
      <img src="./assets/bookshelf-card.svg" width="100%" alt="Living Git Bookshelf" />
    </td>
    <td width="50%" align="center" valign="top">
      <img src="./assets/telemetry-card.svg" width="100%" alt="Library Telemetry" />
    </td>
  </tr>
</table>

<br/>

<img src="https://streak-stats.demolab.com/?user={USERNAME}&theme=dark&background=080C14&border=1E293B&stroke=10B981&ring=10B981&fire=F59E0B&currStreakNum=F59E0B&sideNums=E2E8F0&currStreakLabel=10B981&sideLabels=94A3B8&dates=34D399" width="100%" alt="hans-cdm Streak Stats" />

</div>

---

### 📈 Contribution Landscape

<div align="center">

<img src="https://github-readme-activity-graph.vercel.app/graph?username={USERNAME}&theme=tokyo-night&area=true&hide_border=true&bg_color=080c14&color=10b981&line=10b981&point=f59e0b" width="100%" alt="Contribution Activity Graph" />

</div>

---

### 📚 The Bookshelf (Active Repositories)

<!-- REPOS-LIST:START -->
| 📦 Project / Buku | 📝 Fokus / Deskripsi | ⚡ Bahasa Utama | ⭐ Stars | 🕒 Terakhir Push |
| :--- | :--- | :---: | :---: | :---: |
{repos_table}
<!-- REPOS-LIST:END -->

---

### 🛠️ Unlocked Stack & Tooling

> *Konsep Rak Buku: Hanya bahasa dan perkakas yang sudah pernah dibuatkan project nyata yang akan terbuka di rak ini.*

```
┌── [UNLOCKED LANGUAGES]
{lang_tree_str}
│
└── [SYSTEM & WORKSTATION]
    ├── Hardware       ── AMD Ryzen 5 6600H with Radeon Graphics • 16 GB RAM
    ├── Operating Sys  ── Microsoft Windows 11 Home (x64)
    ├── Terminal Shell ── PowerShell 5.1 / Windows Terminal
    └── Tooling Core   ── Git, GitHub CLI (gh), Node.js, Python
```

---

### 📬 Kontak & Koneksi

<div align="center">

[![Email Badge](https://img.shields.io/badge/EMAIL-hpra0097%40gmail.com-10B981?style=for-the-badge&logo=gmail&logoColor=white&labelColor=080C14)](mailto:hpra0097@gmail.com)
[![GitHub Badge](https://img.shields.io/badge/GITHUB-hans--cdm-F59E0B?style=for-the-badge&logo=github&logoColor=white&labelColor=080C14)](https://github.com/hans-cdm)

</div>
"""
    return content

def main():
    print("Mengambil data repository...")
    repos = fetch_repos()
    print(f"Total repos ditemukan: {len(repos)}")
    languages, categories, public_repos, specialization = analyze_profile(repos)
    print(f"Bahasa aktif: {list(languages.keys())}")
    print(f"Spesialisasi: {specialization}")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    update_telemetry_svg(languages, public_repos, base_dir)

    readme = generate_readme(languages, public_repos, specialization)
    readme_path = os.path.join(base_dir, "README.md")
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)
    
    print(f"README.md berhasil di-generate di: {readme_path}")

if __name__ == "__main__":
    main()
