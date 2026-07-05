import os
import re
import json
import urllib.request

GITHUB_USERNAME = "mayankpandey0"

def fetch_json(url, token=None):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    token = os.environ.get("GITHUB_TOKEN")
    
    # 1. Fetch public repositories
    repos_url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100"
    repos = fetch_json(repos_url, token)
    if not repos:
        print("Failed to fetch repositories.")
        return
        
    language_counts = {}
    
    # 2. Fetch language statistics per repository
    for repo in repos:
        if repo.get("fork"):
            continue
        repo_name = repo.get("name")
        lang_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/languages"
        langs = fetch_json(lang_url, token)
        if langs:
            for lang, bytes_count in langs.items():
                language_counts[lang] = language_counts.get(lang, 0) + bytes_count
                
    if not language_counts:
        print("No languages found.")
        return
        
    # Sort languages by byte size
    sorted_langs = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_langs[:3]
    total_bytes = sum(count for _, count in sorted_langs)
    
    # Language branding and icons (Devicons)
    lang_info = {
        "Python": {
            "name": "Python",
            "icon": "https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg"
        },
        "Java": {
            "name": "Java",
            "icon": "https://raw.githubusercontent.com/devicons/devicon/master/icons/java/java-original.svg"
        },
        "JavaScript": {
            "name": "JavaScript",
            "icon": "https://raw.githubusercontent.com/devicons/devicon/master/icons/javascript/javascript-original.svg"
        },
        "TypeScript": {
            "name": "TypeScript",
            "icon": "https://raw.githubusercontent.com/devicons/devicon/master/icons/typescript/typescript-original.svg"
        },
        "HTML": {
            "name": "HTML",
            "icon": "https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original.svg"
        },
        "CSS": {
            "name": "CSS",
            "icon": "https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original.svg"
        },
        "C++": {
            "name": "C++",
            "icon": "https://raw.githubusercontent.com/devicons/devicon/master/icons/cplusplus/cplusplus-original.svg"
        },
        "C": {
            "name": "C",
            "icon": "https://raw.githubusercontent.com/devicons/devicon/master/icons/c/c-original.svg"
        },
        "Shell": {
            "name": "Shell / Bash",
            "icon": "https://raw.githubusercontent.com/devicons/devicon/master/icons/bash/bash-original.svg"
        },
        "Go": {
            "name": "Go",
            "icon": "https://raw.githubusercontent.com/devicons/devicon/master/icons/go/go-original.svg"
        },
    }
    
    # Generate replacement Markdown block
    content_lines = ["<!-- START_LANGUAGES -->\n"]
    for lang, bytes_count in top_3:
        percent = (bytes_count / total_bytes) * 100
        info = lang_info.get(lang, {
            "name": lang,
            "icon": "https://raw.githubusercontent.com/devicons/devicon/master/icons/git/git-original.svg"
        })
        
        # HTML card layout matching GitHub's dark theme
        card = (
            f'  <div style="display: inline-block; background-color: #0D1117; '
            f'border: 1px solid #30363D; border-radius: 8px; padding: 16px 20px; '
            f'margin: 8px; width: 140px; text-align: center; vertical-align: middle; '
            f'box-shadow: 0 4px 6px rgba(0,0,0,0.1);">\n'
            f'    <img src="{info["icon"]}" alt="{info["name"]}" width="40" height="40" style="margin-bottom: 10px;" />\n'
            f'    <div style="font-size: 14px; font-weight: 600; color: #C9D1D9; font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;">{info["name"]}</div>\n'
            f'    <div style="font-size: 13px; font-weight: 500; color: #8B949E; margin-top: 6px; font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;">{percent:.1f}%</div>\n'
            f'  </div>\n'
        )
        content_lines.append(card)
        
    content_lines.append("  <!-- END_LANGUAGES -->")
    new_metrics = "".join(content_lines)
    
    # Update README.md
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
        
    pattern = r"<!-- START_LANGUAGES -->.*?<!-- END_LANGUAGES -->"
    if re.search(pattern, readme_content, re.DOTALL):
        updated_content = re.sub(pattern, new_metrics, readme_content, flags=re.DOTALL)
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print("README.md updated with 3 elegant language cards.")
    else:
        print("Markers not found in README.md.")

if __name__ == "__main__":
    main()
