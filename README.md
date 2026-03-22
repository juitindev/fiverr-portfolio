# 🐍 Python Portfolio — juitindev

Freelance Python developer specializing in automation, data, bots, and web scraping.  
Available on **[Fiverr @jt_code](https://www.fiverr.com/jt_code)**

---

## 📁 Projects

### 🧹 [Data Cleaning](./data-cleaning/data_cleaner.py)
Clean, process, and transform messy CSV data into structured output.

**Features:**
- Multi-format date parsing (handles 6+ date formats automatically)
- Currency symbol stripping (`$`, `NT$`, `¥`, etc.)
- Duplicate row detection and removal
- Country name standardization
- Auto-generated cleaning report

```bash
python data_cleaner.py
# Output: cleaned_orders.csv + cleaning_report.txt
```

---

### 🕷️ [Web Scraping](./web-scraping/scraper.py)
Scrape product data from any e-commerce site and detect price changes.

**Features:**
- Multi-page scraping with polite delay
- Price change detection between runs
- Structured CSV output
- Summary stats (avg price, cheapest, most expensive)

```bash
python scraper.py
# Output: products.csv + price_history.csv
```

---

### ⚙️ [File Automation](./automation/automation.py)
Auto-sort a messy folder of files into organized subfolders by type.

**Features:**
- Sorts 7 file categories (images, docs, data, video, code, audio, other)
- Timestamp prefix to prevent filename collisions
- Daily log file
- Full summary report

```bash
python automation.py
# Output: sorted/ folder + logs/YYYY-MM-DD.log
```

---

### 🤖 [Telegram Bot](./bots/telegram_bot.py)
A customer service bot for an online store.

**Features:**
- `/order <ID>` — real-time order tracking
- `/deals` — daily promotions
- Graceful handling of unknown messages
- Easy to extend with more commands

```bash
BOT_TOKEN=your_token python telegram_bot.py
```

---

## 🛠️ Tech Stack

`Python 3.10+` · `Pandas` · `BeautifulSoup4` · `Requests` · `python-telegram-bot`

---

## 📬 Hire Me

| Platform | Link |
|----------|------|
| Fiverr   | [@jt_code](https://www.fiverr.com/jt_code) |
| GitHub   | [@juitindev](https://github.com/juitindev) |

> 💬 Have a project in mind? Feel free to reach out!
