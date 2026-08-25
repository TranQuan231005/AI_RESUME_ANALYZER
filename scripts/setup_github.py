import requests
import json
import re
import os
import time

import yaml
import sys

# Đảm bảo in tiếng Việt không bị lỗi trên Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# CONFIGURATION
# ==========================================
# THAY THẾ CÁC GIÁ TRỊ NÀY BẰNG THÔNG TIN CỦA BẠN
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER", "TranQuan231005")
REPO_NAME = os.getenv("REPO_NAME", "AI_RESUME_ANALYZER")

# Đọc token từ file config.yml (nếu có)
if not GITHUB_TOKEN:
    config_path = os.path.join(os.path.dirname(__file__), "config.yml")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            if config_data and "github_token" in config_data:
                GITHUB_TOKEN = config_data["github_token"]

if not GITHUB_TOKEN or GITHUB_TOKEN == "YOUR_GITHUB_TOKEN_HERE":
    print("❌ Lỗi: Không tìm thấy GITHUB_TOKEN hợp lệ trong biến môi trường hoặc scripts/config.yml!")
    sys.exit(1)


MARKDOWN_FILE = "../KE_HOACH_LAM_LAI_DU_AN_3_TUAN.md"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

# ==========================================
# 1. SETUP BRANCH PROTECTION
# ==========================================
def protect_main_branch():
    print("-> Setting up branch protection for 'main'...")
    url = f"{BASE_URL}/branches/main/protection"
    data = {
        "required_status_checks": None,
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "required_approving_review_count": 1
        },
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print("   ✅ Branch 'main' is protected.")
    else:
        print(f"   ❌ Failed to protect branch: {response.status_code} - {response.text}")


# ==========================================
# 2. CREATE MILESTONES
# ==========================================
MILESTONES = [
    {"title": "M0 – Contract Freeze", "description": "Scope, Auth contract, DB V1, API Contracts, Fixtures"},
    {"title": "M1 – Walking Skeleton", "description": "App Shell, Basic PDF Validation, Auth basics"},
    {"title": "M2 – Feature Freeze", "description": "All pipelines implemented"},
    {"title": "M3 – Clean-machine Demo", "description": "Integration and Compose orchestration"},
    {"title": "M4 – Final Release", "description": "End-to-end evaluation and polish"}
]
milestone_map = {}

def create_milestones():
    print("-> Creating Milestones...")
    url = f"{BASE_URL}/milestones"
    # Lấy danh sách hiện tại
    exist_res = requests.get(url, headers=headers)
    if exist_res.status_code == 200:
        for m in exist_res.json():
            milestone_map[m['title'][:2]] = m['number']

    for m in MILESTONES:
        key = m['title'][:2]
        if key in milestone_map:
            print(f"   ✅ Milestone {key} already exists.")
            continue
        
        response = requests.post(url, headers=headers, json=m)
        if response.status_code == 201:
            data = response.json()
            milestone_map[key] = data['number']
            print(f"   ✅ Created Milestone: {m['title']}")
        else:
            print(f"   ❌ Failed to create milestone {m['title']}: {response.text}")


# ==========================================
# 3. PARSE MARKDOWN AND CREATE ISSUES
# ==========================================
def parse_and_create_issues():
    print("-> Parsing Markdown and creating issues...")
    # Check if the file is run from scripts/ or from root
    md_path = MARKDOWN_FILE
    if not os.path.exists(md_path):
        md_path = "KE_HOACH_LAM_LAI_DU_AN_3_TUAN.md"
        if not os.path.exists(md_path):
            print(f"   ❌ File not found!")
            return

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match các dòng trong bảng task: | T1.1 | TV1 | TV2 | 3 | D2 | Repo layout...
    pattern = r"\|\s*(T[1-5]\.[1-9])\s*\|\s*(TV[1-5])\s*\|\s*(TV[1-5])\s*\|\s*(\d+)\s*\|\s*(D\d+)\s*\|\s*([^\|]+)\|\s*([^\|]+)\|\s*([^\|]+)\|\s*([^\|]+)\|"
    matches = re.findall(pattern, content)

    url = f"{BASE_URL}/issues"
    
    for m in matches:
        task_id = m[0].strip()
        owner = m[1].strip()
        reviewer = m[2].strip()
        sp = m[3].strip()
        deadline = m[4].strip()
        inp = m[5].strip()
        outp = m[6].strip()
        acc = m[7].strip()
        tests = m[8].strip()

        title = f"{task_id} - {inp[:40]}..." if len(inp) > 40 else f"{task_id} - {inp}"
        
        # Tách fixture và test command nếu có dấu chấm phẩy
        if ";" in tests:
            fixture_part, test_part = tests.split(";", 1)
        else:
            fixture_part = tests
            test_part = tests

        body = f"""**Task ID:** {task_id}
**Owner:** {owner}
**Reviewer:** {reviewer}
**Story points:** {sp}
**Deadline:** {deadline}
**Input:** {inp}
**Output:** {outp}
**Acceptance criteria:** {acc}
**Fixtures:** {fixture_part.strip()}
**Test command:** `{test_part.strip()}`
**Dependencies:** N/A (Xem trong file Markdown)
"""
        
        m_num = None
        d_val = int(deadline.replace('D', ''))
        if d_val <= 3: m_num = milestone_map.get('M0')
        elif d_val <= 7: m_num = milestone_map.get('M1')
        elif d_val <= 10: m_num = milestone_map.get('M2')
        elif d_val <= 13: m_num = milestone_map.get('M3')
        else: m_num = milestone_map.get('M4')

        data = {
            "title": title,
            "body": body,
            "labels": [f"member-{owner.lower()}", f"priority-p1"]
        }
        if m_num:
            data["milestone"] = m_num

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print(f"   ✅ Created Issue {task_id}")
        else:
            print(f"   ❌ Failed to create Issue {task_id}: {response.text}")
        
        time.sleep(1) # Tránh rate limit

# ==========================================
# 4. CREATE PROJECT BOARD (Classic)
# ==========================================
def create_project_board():
    print("-> Creating Project Board...")
    url = f"{BASE_URL}/projects"
    data = {
        "name": "AI Resume Analyzer - 3 Weeks",
        "body": "Bảng theo dõi tiến độ dự án 3 tuần"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        proj_id = response.json()['id']
        print("   ✅ Created Project Board.")
        
        # Tạo Columns
        columns = ["Backlog", "Ready", "In Progress", "Review", "Blocked", "Done"]
        col_url = f"https://api.github.com/projects/{proj_id}/columns"
        # Accept header đặc biệt cho project columns
        col_headers = headers.copy()
        col_headers["Accept"] = "application/vnd.github.inertia-preview+json"

        for col in columns:
            c_res = requests.post(col_url, headers=col_headers, json={"name": col})
            if c_res.status_code == 201:
                print(f"      ✅ Created column '{col}'")
            else:
                print(f"      ❌ Failed to create column '{col}': {c_res.text}")
    else:
        print(f"   ❌ Failed to create Project Board: {response.status_code} - {response.text}")


if __name__ == "__main__":
    print("Bắt đầu setup GitHub...")
    protect_main_branch()
    create_milestones()
    create_project_board()
    parse_and_create_issues()
    print("Hoàn tất!")
