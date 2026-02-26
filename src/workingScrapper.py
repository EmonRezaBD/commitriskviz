import requests
import csv
import time

# Your GitHub token
GITHUB_TOKEN = ""

# Just 3 repos for testing (from your original list)
REPOS = [
    "FFmpeg/FFmpeg",
    "opencv/opencv",
    "nlohmann/json",
    "google/leveldb",
    "google/re2",
    "facebook/folly",
    "apache/arrow",
    "libjpeg-turbo/libjpeg-turbo",
    "cmu-sei/pharos",
    "boostorg/algorithm"
]

def find_candidate_commits():
    """Find 10 commits that might be single-function changes"""
    
    all_candidates = []
    target = 220 #change the target
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    
    for repo in REPOS:
        if len(all_candidates) >= target:
            break
            
        print(f"Searching {repo}...")
        
        # Simple search for bug fixes
        url = "https://api.github.com/search/commits"
        params = {
            "q": f"repo:{repo} fix bug",
            "per_page": 5  # Get 5 per repo
        }
        
        # Special header for commit search
        search_headers = headers.copy()
        search_headers["Accept"] = "application/vnd.github.cloak-preview"
        
        try:
            response = requests.get(url, headers=search_headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    all_candidates.append({
                        'repo': repo,
                        'commit_url': item['html_url'],
                        'message': item['commit']['message'][:100],  # First 100 chars
                        'date': item['commit']['committer']['date']
                    })
                    
                    if len(all_candidates) >= target:
                        break
                        
            time.sleep(1)  # Be nice
            
        except Exception as e:
            print(f"Error: {e}")
    
    return all_candidates

def save_to_csv(candidates, filename="data\candidate_commits.csv"):
    """Save candidates to CSV file"""
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['repo', 'commit_url', 'message', 'date'])
        writer.writeheader()
        writer.writerows(candidates)
    
    print(f"Saved {len(candidates)} commits to {filename}")

def main():
    print("Finding 10 candidate commits...")
    candidates = find_candidate_commits()
    
    if candidates:
        save_to_csv(candidates)
        print("\nFirst 3 commits:")
        for c in candidates[:3]:
            print(f"- {c['commit_url']}")
    else:
        print("No commits found")

if __name__ == "__main__":
    main()