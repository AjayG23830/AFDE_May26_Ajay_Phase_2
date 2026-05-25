"""Generate sample article dataset with 120 records + search log."""
import csv, random
from datetime import datetime, timedelta

CATEGORIES = ["HR Policies","IT Support","Infrastructure","Training Materials","Finance","Operations"]
TAGS_POOL  = ["python","fastapi","react","devops","security","onboarding","policy","aws",
              "docker","kubernetes","ml","data","sql","linux","networking"]
AUTHORS    = [f"Author_{c}" for c in "ABCDEFGHIJ"]
STATUSES   = ["Draft","Pending Approval","Approved","Rejected","Archived"]

ARTICLE_TITLES = [
    "Setting up VPN for remote work","Guide to password manager rollout","Quarterly tax filing checklist",
    "Employee onboarding handbook","Docker container best practices","Disaster recovery procedures",
    "Code review guidelines","CI/CD pipeline architecture","HR leave policy 2024",
    "AWS cost optimization tips","Network firewall configuration","Annual performance review process",
    "Python coding standards","Kubernetes deployment patterns","Database backup strategy",
    "Vendor management workflow","React component library guide","Health insurance enrollment",
    "Office expense reimbursement","Security incident response plan",
]

SEARCH_KEYWORDS = ["python","vpn","leave","docker","react","backup","security","onboarding",
                   "tax","aws","sql","policy","review","insurance","kubernetes","linux"]

if __name__ == "__main__":
    random.seed(42)

    # Articles
    rows = []
    start = datetime(2024, 1, 1)
    for i in range(120):
        title = random.choice(ARTICLE_TITLES) + (f" — v{random.randint(1,5)}" if random.random() < 0.5 else "")
        cat = random.choice(CATEGORIES)
        if random.random() < 0.04: cat = cat.upper()
        n_tags = random.randint(1, 4)
        tags = "|".join(random.sample(TAGS_POOL, n_tags))
        author = random.choice(AUTHORS)
        status = random.choices(STATUSES, weights=[15,15,55,10,5])[0]
        views = random.choices([0, random.randint(1,5), random.randint(5,30), random.randint(30,150)], weights=[10,30,40,20])[0]
        created = start + timedelta(days=random.randint(0, 400), hours=random.randint(0,23))
        if random.random() < 0.05: title = " " + title  # whitespace noise
        rows.append([title, cat, tags, author, status, views, created.strftime("%Y-%m-%d %H:%M:%S")])
    rows.extend(rows[:5])  # dupes

    with open("datasets/articles_raw.csv","w",newline="",encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["title","category","tags","author","status","view_count","created_at"])
        w.writerows(rows)

    # Search log (separate file - simulates user searches)
    log_rows = []
    for _ in range(400):
        kw = random.choice(SEARCH_KEYWORDS)
        ts = start + timedelta(days=random.randint(0, 400), hours=random.randint(0,23))
        log_rows.append([kw, ts.strftime("%Y-%m-%d %H:%M:%S")])
    with open("datasets/search_log_raw.csv","w",newline="",encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["keyword","searched_at"]); w.writerows(log_rows)

    print(f"Generated {len(rows)} articles + {len(log_rows)} search log entries")
