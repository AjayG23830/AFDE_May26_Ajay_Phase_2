"""Generate sample helpdesk ticket dataset with 220 records (dirty for ETL practice)."""
import csv, random
from datetime import datetime, timedelta

CATEGORIES = ["VPN Issue","Password Reset","Software Installation","Laptop Issue",
              "Email Access","Network Connectivity","Hardware Request"]
DEPARTMENTS = ["Engineering","HR","Finance","Marketing","Sales","Operations","IT","Legal","Admin"]
PRIORITIES = ["Low","Medium","High","Critical"]
STATUSES   = ["Open","In Progress","Resolved","Closed"]
NAMES = ["Raj K","Priya S","Arun P","Sneha M","Vikram R","Anjali D","Karthik T","Pooja N",
        "Manoj G","Lakshmi V","Naveen B","Shruti J","Aditya R","Kavya I","Rohan P","Divya S",
        "Suresh K","Meera M","Rohit J","Tanvi A"]
DESCRIPTIONS = {
    "VPN Issue": "Cannot connect to VPN. Authentication keeps failing.",
    "Password Reset": "Forgot my email password, need a reset.",
    "Software Installation": "Need {sw} installed on my workstation.",
    "Laptop Issue": "Laptop is running very slow / overheating / not booting.",
    "Email Access": "Outlook not syncing with corporate server.",
    "Network Connectivity": "Office WiFi keeps dropping every few minutes.",
    "Hardware Request": "Requesting an external monitor / docking station / keyboard.",
}
SOFTWARES = ["MS Office 2021","Visual Studio Code","Slack","Zoom","Adobe Reader","Postman"]

if __name__ == "__main__":
    rows = []
    start = datetime(2024, 1, 1)
    random.seed(42)
    for i in range(220):
        cat = random.choice(CATEGORIES)
        prio = random.choices(PRIORITIES, weights=[20,40,30,10])[0]
        status = random.choices(STATUSES, weights=[25,25,30,20])[0]
        desc = DESCRIPTIONS[cat]
        if "{sw}" in desc: desc = desc.replace("{sw}", random.choice(SOFTWARES))
        name = random.choice(NAMES)
        if random.random() < 0.05: name = " " + name
        if random.random() < 0.04: cat = cat.upper()   # noise
        dept = random.choice(DEPARTMENTS)
        if random.random() < 0.03: dept = ""           # missing data
        created = start + timedelta(days=random.randint(0, 400), hours=random.randint(0,23))
        resolved_at = ""
        if status in ("Resolved","Closed"):
            resolved_at = (created + timedelta(hours=random.randint(2, 96))).strftime("%Y-%m-%d %H:%M:%S")
        rows.append([name, dept, cat, desc, prio, status, created.strftime("%Y-%m-%d %H:%M:%S"), resolved_at])
    rows.extend(rows[:8])  # duplicates

    with open("datasets/tickets_raw.csv","w",newline="",encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["employee_name","department","issue_category","description","priority","status","created_at","resolved_at"])
        w.writerows(rows)
    print(f"Generated {len(rows)} ticket records → datasets/tickets_raw.csv")
