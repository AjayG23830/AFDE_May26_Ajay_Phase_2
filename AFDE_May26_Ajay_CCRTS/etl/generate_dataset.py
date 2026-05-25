"""Generate sample complaint dataset with 250 records."""
import csv, random
from datetime import datetime, timedelta

CATEGORIES = ["Billing Issues","Service Disruption","Product Defects","Technical Problems",
              "Delivery Delays","Account Issues","Customer Service"]
PRIORITIES = ["Low","Medium","High","Critical"]
STATUSES   = ["Open","Assigned","In Progress","Pending Customer Response","Escalated","Resolved","Closed"]
SLA_HOURS  = {"Low":72,"Medium":48,"High":24,"Critical":4}
AGENTS     = [f"Agent_{c}" for c in "ABCDEFGH"]
TITLES = {
    "Billing Issues": "Incorrect charge of ₹{amt} on my invoice",
    "Service Disruption": "Service outage in my area since {date}",
    "Product Defects": "Defective {item} received in last order",
    "Technical Problems": "App keeps crashing when I try to {action}",
    "Delivery Delays": "Order #{oid} delayed by {days} days",
    "Account Issues": "Cannot login to my account",
    "Customer Service": "Poor response from support team",
}
ITEMS = ["laptop","headphones","router","monitor","keyboard"]
ACTIONS = ["pay","login","upload","share","download"]

if __name__ == "__main__":
    rows = []
    start = datetime(2024, 1, 1)
    random.seed(42)
    for i in range(250):
        cat = random.choice(CATEGORIES)
        prio = random.choices(PRIORITIES, weights=[20,40,30,10])[0]
        status = random.choices(STATUSES, weights=[15,15,20,5,10,25,10])[0]
        agent = random.choice(AGENTS) if status != "Open" else ""
        created = start + timedelta(days=random.randint(0, 400), hours=random.randint(0,23))
        sla_deadline = created + timedelta(hours=SLA_HOURS[prio])

        resolved_at = ""
        if status in ("Resolved","Closed"):
            # Some on time, some breach
            if random.random() < 0.65:
                resolved_at = created + timedelta(hours=random.randint(1, SLA_HOURS[prio]))
            else:
                resolved_at = created + timedelta(hours=SLA_HOURS[prio] + random.randint(1, 100))
            resolved_at = resolved_at.strftime("%Y-%m-%d %H:%M:%S")

        title = TITLES[cat].format(amt=random.randint(500,9999), date="last week",
                                   item=random.choice(ITEMS), action=random.choice(ACTIONS),
                                   oid=random.randint(10000,99999), days=random.randint(2,15))

        # Inject noise
        if random.random() < 0.04: cat = cat.upper()
        if random.random() < 0.03: prio = ""
        if random.random() < 0.03: status = ""

        rows.append([f"CMP-{i+1:05d}", title, cat, prio, status, agent,
                     created.strftime("%Y-%m-%d %H:%M:%S"),
                     sla_deadline.strftime("%Y-%m-%d %H:%M:%S"),
                     resolved_at])
    rows.extend(rows[:10])

    with open("datasets/complaints_raw.csv","w",newline="",encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["complaint_number","title","category","priority","status","agent_name",
                    "created_at","sla_deadline","resolved_at"])
        w.writerows(rows)
    print(f"Generated {len(rows)} complaint records")
