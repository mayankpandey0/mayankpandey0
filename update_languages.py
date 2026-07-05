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
    
    # Language branding information
    lang_styles = {
        "Python": {"color": "3776AB", "logo": "python"},
        "Java": {"color": "ED8B00", "logo": "openjdk"},
        "JavaScript": {"color": "F7DF1E", "logo": "javascript"},
        "TypeScript": {"color": "3178C6", "logo": "typescript"},
        "HTML": {"color": "E34F26", "logo": "html5"},
        "CSS": {"color": "1572B6", "logo": "css3"},
        "C++": {"color": "00599C", "logo": "cplusplus"},
        "C": {"color": "A8B9CC", "logo": "c"},
        "Shell": {"color": "89E051", "logo": "gnubash"},
        "Go": {"color": "00ADD8", "logo": "go"},
    }
    
    # Generate replacement Markdown block
    content_lines = ["<!-- START_LANGUAGES -->\n"]
    for lang, bytes_count in top_3:
        percent = (bytes_count / total_bytes) * 100
        style = lang_styles.get(lang, {"color": "555555", "logo": "github"})
        logo_part = f"&logo={style['logo']}&logoColor=white" if style['logo'] else ""
        badge_url = f"https://img.shields.io/badge/{lang}-{percent:.1f}%25-{style['color']}?style=for-the-badge{logo_part}"
        content_lines.append(f'  <img src="{badge_url}" alt="{lang}" />\n')
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
        print("README.md updated with top 3 languages.")
    else:
        print("Markers not found in README.md.")

if __name__ == "__main__":
    main()
