# ig_post_bot
# 🤖 TechNews-AutoBot: Daily Instagram Automation

A fully automated, serverless bot that fetches the latest technical news and publishes it to Instagram every 24 hours. Powered by **GitHub Actions** for zero-cost hosting.

![GitHub Actions Status](https://img.shields.io/badge/Workflow-Active-success?style=flat-square&logo=github-actions)
![Python](https://img.shields.io/badge/Language-Python-3776AB?style=flat-square&logo=python)
![Automation](https://img.shields.io/badge/Automation-Cron--Job-orange?style=flat-square)

---

## How It Works

This project eliminates the manual effort of staying consistent on social media. The bot follows a three-step automated pipeline:

1.  **Scrape:** A Python script fetches the top trending stories from tech news APIs and RSS feeds.
2.  **Process:** The content is formatted into an Instagram-ready caption and image layout.
3.  **Deploy:** Using the **Meta Graph API**, the bot pushes the post directly to Instagram.
4.  **Schedule:** **GitHub Actions** triggers the entire workflow daily using a `cron` schedule.

## Tech Stack

* **Language:** Python 3.x
* **Automation:** GitHub Actions (CI/CD)
* **API Integration:** Meta Graph API (Instagram Business)
* **Secrets Management:** GitHub Actions Secrets (to keep API tokens safe)

## Project Structure

```text
├── .github/workflows/
│   └── daily_post.yml  # The Cron job & CI/CD config
├── src/
│   ├── scraper.py      # Logic for fetching news
│   └── instagram.py    # Meta API integration logic
├── requirements.txt    # Required Python libraries
└── README.md           # Documentation

