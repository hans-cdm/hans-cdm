import os
import json
import urllib.request
from datetime import datetime

USERNAME = "hans-cdm"
API_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=pushed"

# Bahasa emoji/badge mapping
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
        # Coba baca dari gh CLI jika di lokal
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
        # Kecualikan repo profil sendiri
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

    # Deteksi spesialisasi jika dominan (minimal 40% dari total project dan >= 4 repo)
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

def generate_readme(languages, public_repos, specialization):
    # Urutkan bahasa berdasarkan frekuensi
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
        
        # Format baris
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

    # Template
    content = f"""<div align="center">

<img src="./assets/banner.svg" alt="hans-cdm Bookshelf Banner" width="100%" />

</div>

---

### 💻 System Specs & Environment

```text
       ._____________________________________.
       | [===] [===] [===]     |   |===|     |      hans-cdm@workstation
       |  JS   PHP    TS       |   |Git|     |     ----------------------
       |=======================+=============|     OS: Windows 11 Home 64-bit
       |  [=====]  [=====]     |    ---      |     CPU: AMD Ryzen 5 6600H (6C/12T)
       |   Apps     Bots       |   |o o|     |     RAM: 16 GB DDR5
       |=======================+=============|     Shell: PowerShell 5.1 / Windows Terminal
       |  [           Shelves of Code        |     Active Stack: {active_langs_str}
       |_____________________________________|     Specialization: [{specialization}]
                                                   Growth Status: Continuous Evolution 🌱
```

---

### 📊 Activity & Telemetry

<div align="center">
<table border="0" width="100%">
  <tr>
    <td width="50%" align="center" valign="top">
      <img src="https://github-readme-stats-sigma-five.vercel.app/api?username={USERNAME}&show_icons=true&theme=tokyonight&hide_border=true&bg_color=0d1117" width="100%" alt="GitHub Stats" />
    </td>
    <td width="50%" align="center" valign="top">
      <img src="https://streak-stats.demolab.com/?user={USERNAME}&theme=tokyonight&background=0D1117&border=1F2937&stroke=38BDF8&ring=38BDF8&fire=F59E0B&currStreakNum=F59E0B&sideNums=F8FAFC&currStreakLabel=38BDF8&sideLabels=94A3B8&dates=38BDF8" width="100%" alt="Streak Stats" />
    </td>
  </tr>
</table>
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

[![Email Badge](https://img.shields.io/badge/EMAIL-hpra0097%40gmail.com-38BDF8?style=for-the-badge&logo=gmail&logoColor=white&labelColor=0F172A)](mailto:hpra0097@gmail.com)
[![GitHub Badge](https://img.shields.io/badge/GITHUB-hans--cdm-F59E0B?style=for-the-badge&logo=github&logoColor=white&labelColor=0F172A)](https://github.com/hans-cdm)

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
    
    readme = generate_readme(languages, public_repos, specialization)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme_path = os.path.join(base_dir, "README.md")
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)
    
    print(f"README.md berhasil di-generate di: {readme_path}")

if __name__ == "__main__":
    main()
