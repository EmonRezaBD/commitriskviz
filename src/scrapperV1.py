import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
from datetime import datetime, timedelta
import os

# Custom headers to avoid 406 error
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "application/vnd.github.v3+json"
}

# GitHub API Token (get from github.com/settings/tokens)
GITHUB_TOKEN = ""  # Replace with your token

# Popular C++ repos
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

# Keywords to filter relevant commits
KEYWORDS = ["fix", "bug", "crash", "overflow", "null", "memory", "leak", "security", "vuln"]

def get_commits_from_api(repo, days_back=30):
    """Fetch commit URLs from GitHub API"""
    commits = []
    
    # Calculate date range
    since = (datetime.now() - timedelta(days=days_back)).isoformat()
    
    # GitHub API endpoint
    url = f"https://api.github.com/repos/{repo}/commits"
    
    params = {
        "since": since,
        "per_page": 100,  # Max per page
        "page": 1
    }
    
    headers_with_auth = headers.copy()
    if GITHUB_TOKEN != "your_token_here":
        headers_with_auth["Authorization"] = f"token {GITHUB_TOKEN}"
    
    while True:
        try:
            response = requests.get(url, headers=headers_with_auth, params=params)
            
            if response.status_code == 403 and "rate limit" in response.text.lower():
                print("Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                continue
                
            if response.status_code != 200:
                print(f"API error: {response.status_code}")
                break
                
            data = response.json()
            if not data:
                break
                
            # Filter commits by keywords in message
            for commit in data:
                message = commit['commit']['message'].lower()
                if any(keyword in message for keyword in KEYWORDS):
                    commits.append(commit['html_url'])
            
            # Check if we have more pages
            if 'next' not in response.links:
                break
                
            params['page'] += 1
            time.sleep(0.5)  # Be nice to API
            
        except Exception as e:
            print(f"Error fetching commits: {e}")
            break
    
    return commits
def scrape_github_commit(url):
    """Updated scraper with proper GitHub headers"""
    
    # Critical: Add these headers to look like a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        # Add timeout to avoid hanging
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Updated selectors for GitHub's current HTML structure
        find_function_name = soup.find("td", class_="blob-code-hunk")
        if not find_function_name:
            # Try alternative selector
            find_function_name = soup.find("span", class_="pl-en")
        
        if not find_function_name:
            return None
            
        function_name = find_function_name.get_text(strip=True)

        if '(' in function_name and ')' in function_name:
            # Updated commit title selector
            commit_title_element = soup.find("a", class_="u-link")
            if not commit_title_element:
                commit_title_element = soup.find("div", class_="commit-title")
            commit_title = commit_title_element.get_text(strip=True) if commit_title_element else "No Title Found"

            # Rest of your code remains the same
            minus_version = []
            plus_version = []
            normal_version = []
            before_commit_list = []
            after_commit_list = []

            minusCode = soup.find_all("td", class_="blob-code-deletion")
            plusCode = soup.find_all("td", class_="blob-code-addition")
            normalCode = soup.find_all("td", class_="blob-code-context")
            before_commit_code = soup.find_all(["td"], class_=["blob-code-deletion", "blob-code-context"])
            after_commit_code = soup.find_all(["td"], class_=["blob-code-addition", "blob-code-context"])

            for line in minusCode:
                code_line = line.get_text(strip=True)
                minus_version.append(code_line)

            for line in plusCode:
                code_line = line.get_text(strip=True)
                plus_version.append(code_line)
            
            for line in normalCode:
                code_line = line.get_text(strip=True)
                normal_version.append(code_line)
            
            for line in before_commit_code:
                code_line = line.get_text(strip=True)
                before_commit_list.append(code_line)

            for line in after_commit_code:
                code_line = line.get_text(strip=True)
                after_commit_list.append(code_line)

            only_addition_codes = "\n".join(plus_version)
            only_deletion_codes = "\n".join(minus_version)
            normal_codes = "\n".join(normal_version)
            before_commit_codes = "\n".join(before_commit_list)
            after_commit_codes = "\n".join(after_commit_list)

            return {
                "commit_title": commit_title,
                "commit_url": url,
                "only_addition_codes": only_addition_codes,
                "only_deletion_codes": only_deletion_codes,
                "codes_without_addition_and_deletion": normal_codes,
                "before_commit_codebase": before_commit_codes,
                "after_commit_codebase": after_commit_codes
            }
            
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
    
    return None

# def scrape_github_commit(url):
    """Your original scraper function - unchanged"""
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Checking if Single function change
    find_function_name = soup.find("td", class_="blob-code-hunk")
    if not find_function_name:
        return None
        
    function_name = find_function_name.get_text(strip=True)

    if '(' in function_name and ')' in function_name:  # Checking function signature 
        commit_title_element = soup.find("div", class_="commit-title")
        commit_title = commit_title_element.get_text(strip=True) if commit_title_element else "No Title Found"

        minus_version = []
        plus_version = []
        normal_version = []
        before_commit_list = []
        after_commit_list = []

        minusCode = soup.find_all("td", class_="blob-code-deletion")
        plusCode = soup.find_all("td", class_="blob-code-addition")
        normalCode = soup.find_all("td", class_="blob-code-context")
        before_commit_code = soup.find_all(["td"], class_=["blob-code-deletion", "blob-code-context"])
        after_commit_code = soup.find_all(["td"], class_=["blob-code-addition", "blob-code-context"])

        for line in minusCode:
            code_line = line.get_text(strip=True)
            minus_version.append(code_line)

        for line in plusCode:
            code_line = line.get_text(strip=True)
            plus_version.append(code_line)
        
        for line in normalCode:
            code_line = line.get_text(strip=True)
            normal_version.append(code_line)
        
        for line in before_commit_code:
            code_line = line.get_text(strip=True)
            before_commit_list.append(code_line)

        for line in after_commit_code:
            code_line = line.get_text(strip=True)
            after_commit_list.append(code_line)

        only_addition_codes = "\n".join(plus_version)
        only_deletion_codes = "\n".join(minus_version)
        normal_codes = "\n".join(normal_version)
        before_commit_codes = "\n".join(before_commit_list)
        after_commit_codes = "\n".join(after_commit_list)

        return {
            "commit_title": commit_title,
            "commit_url": url,
            "only_addition_codes": only_addition_codes,
            "only_deletion_codes": only_deletion_codes,
            "codes_without_addition_and_deletion": normal_codes,
            "before_commit_codebase": before_commit_codes,
            "after_commit_codebase": after_commit_codes
        }
    return None

def write_to_jsonl(file_name, commit_data):
    """Your original write function - unchanged"""
    with open(file_name, 'a', encoding='utf-8') as f:
        formatted_data = {
            "Commit title": commit_data["commit_title"],
            "Commit url": commit_data["commit_url"],
            "Only_addition_codes": commit_data["only_addition_codes"],
            "Only_deletion_codes": commit_data["only_deletion_codes"],
            "Codes_without_addition_and_deletion": commit_data["codes_without_addition_and_deletion"],
            "Before_commit_codebase": commit_data["before_commit_codebase"],
            "After_commit_codebase": commit_data["after_commit_codebase"]
        }
        json_line = json.dumps(formatted_data, ensure_ascii=False)
        f.write(json_line + '\n')

def main():
    output_file = "data/Dataset_50_commits.jsonl"  # Change to Dataset_1000_commits.jsonl for final run
    
    # Remove existing file if you want fresh start
    if os.path.exists(output_file):
        print(f"Appending to existing {output_file}")
    
    total_collected = 0
    target = 50  # CHANGE THIS TO 1000 for final collection
    
    # Loop through repos
    for repo in REPOS:
        if total_collected >= target:
            break
            
        print(f"\n--- Fetching from {repo} ---")
        
        # Get commit URLs from API
        # CHANGE days_back=30 to days_back=365 for 1000 commits (more history)
        commit_urls = get_commits_from_api(repo, days_back=30)  # Change to 365 for 1000
        
        print(f"Found {len(commit_urls)} relevant commits in {repo}")
        
        # Process each commit
        for url in commit_urls:
            if total_collected >= target:
                break
                
            print(f"Processing ({total_collected+1}/{target}): {url}")
            
            try:
                commit_data = scrape_github_commit(url)
                
                if commit_data:
                    write_to_jsonl(output_file, commit_data)
                    total_collected += 1
                    print(f"✓ Collected. Total: {total_collected}")
                else:
                    print(f"✗ Not a single-function change")
                
                # Be nice to GitHub
                time.sleep(1)  # Can reduce to 0.5 for 1000 commits
                
            except Exception as e:
                print(f"Error: {e}")
                continue
    
    print(f"\n✅ Done! Collected {total_collected} commits in {output_file}")

if __name__ == "__main__":
    main()