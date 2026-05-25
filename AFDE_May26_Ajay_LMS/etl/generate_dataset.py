"""Generate sample library dataset with 180 transactions, 50 books, 30 borrowers."""
import csv, random
from datetime import datetime, timedelta

CATEGORIES = ["Programming","Fiction","Non-Fiction","History","Science","AI/ML","Self-Help","Biography","Mathematics","Business"]
BOOKS = [
    ("Clean Code","Robert C. Martin","Programming"),("The Pragmatic Programmer","David Thomas","Programming"),
    ("Sapiens","Yuval Noah Harari","History"),("Atomic Habits","James Clear","Self-Help"),
    ("Deep Learning","Ian Goodfellow","AI/ML"),("The Lean Startup","Eric Ries","Business"),
    ("To Kill a Mockingbird","Harper Lee","Fiction"),("1984","George Orwell","Fiction"),
    ("Steve Jobs","Walter Isaacson","Biography"),("Cosmos","Carl Sagan","Science"),
    ("The Design of Everyday Things","Don Norman","Non-Fiction"),("Hands-On ML","Aurélien Géron","AI/ML"),
    ("Linear Algebra Done Right","Sheldon Axler","Mathematics"),("The Code Book","Simon Singh","Non-Fiction"),
    ("Refactoring","Martin Fowler","Programming"),("Pride and Prejudice","Jane Austen","Fiction"),
    ("The Innovators","Walter Isaacson","Biography"),("A Brief History of Time","Stephen Hawking","Science"),
    ("Designing Data-Intensive Apps","Martin Kleppmann","Programming"),("Calculus","James Stewart","Mathematics"),
    ("The Power of Habit","Charles Duhigg","Self-Help"),("Educated","Tara Westover","Biography"),
    ("Zero to One","Peter Thiel","Business"),("The Selfish Gene","Richard Dawkins","Science"),
    ("Effective Java","Joshua Bloch","Programming"),("Crime and Punishment","Fyodor Dostoevsky","Fiction"),
    ("Mindset","Carol Dweck","Self-Help"),("Outliers","Malcolm Gladwell","Non-Fiction"),
    ("Pattern Recognition","Christopher Bishop","AI/ML"),("Brave New World","Aldous Huxley","Fiction"),
]
BORROWERS = [(f"Borrower {i}", f"borrower{i}@example.com", f"98765{i:05d}") for i in range(1, 31)]

if __name__ == "__main__":
    random.seed(42)

    # Books CSV
    with open("datasets/books_raw.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["title","author","category","isbn","availability_status"])
        for i, (t, a, c) in enumerate(BOOKS):
            isbn = f"978-{random.randint(100000000, 999999999)}"
            if random.random() < 0.05: t = " " + t  # noise
            if random.random() < 0.05: c = c.upper()  # noise
            w.writerow([t, a, c, isbn, "Available"])

    # Borrowers CSV
    with open("datasets/borrowers_raw.csv","w",newline="",encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["borrower_name","email","phone"])
        for n, e, p in BORROWERS:
            if random.random() < 0.05: e = e.upper()
            w.writerow([n, e, p])

    # Transactions CSV - some with returns, some without (active), some overdue
    rows = []
    start = datetime(2024, 1, 1)
    for i in range(180):
        book_idx = random.randint(1, len(BOOKS))
        borrower_idx = random.randint(1, len(BORROWERS))
        bdate = start + timedelta(days=random.randint(0, 400))
        # 70% returned
        if random.random() < 0.7:
            rdate = bdate + timedelta(days=random.randint(1, 60))
            rdate_s = rdate.strftime("%Y-%m-%d %H:%M:%S")
        else:
            rdate_s = ""
        rows.append([book_idx, borrower_idx, bdate.strftime("%Y-%m-%d %H:%M:%S"), rdate_s])
    rows.extend(rows[:8])  # dupes

    with open("datasets/transactions_raw.csv","w",newline="",encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["book_id","borrower_id","borrow_date","return_date"]); w.writerows(rows)

    print(f"Generated {len(BOOKS)} books, {len(BORROWERS)} borrowers, {len(rows)} transactions")
