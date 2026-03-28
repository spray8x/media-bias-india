# Indian Media Bias & Sentiment Dashboard

A real-time dashboard that tracks and analyzes sentiment and political bias across major Indian news outlets. Built as a capstone project for the Fundamentals in AI and ML course (CSA2001) at VIT Bhopal University.

---

## What it does

Fetches live headlines from 10 Indian news outlets spanning the full political spectrum — from far-right to far-left — runs sentiment analysis on each article using VADER, and visualizes the results across three interactive views:

- **Overview** — article volume and average sentiment broken down by political lean
- **Topic Explorer** — search any keyword and see how the left and right covered it differently, side by side
- **Outlet Profile** — deep dive into any single outlet's sentiment distribution and how it compares to its lean peers

## Outlets tracked

| Outlet | Political Lean |
|--------|---------------|
| OpIndia | Far Right |
| Swarajya | Far Right |
| Times of India | Moderate Right |
| Hindustan Times | Moderate Right |
| The Hindu | Centre |
| The Print | Centre |
| NDTV | Moderate Left |
| Indian Express | Moderate Left |
| Scroll.in | Far Left |
| AltNews | Far Left |

Bias classifications are based on MediaBias/FactCheck, AllSides, the Reuters Institute Digital News Report, and The Hoot, supplemented by the author's documented rationale where references did not adequately cover an outlet.

---

## Tech stack

- **Python** — core language
- **NewsAPI + feedparser** — live article fetching
- **VADER** — sentiment analysis
- **pandas** — data processing
- **Plotly** — charts and visualizations
- **Streamlit** — web dashboard

---

## Installation

### Prerequisites

- Python 3.10 or higher
- A free NewsAPI key from [newsapi.org](https://newsapi.org)

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/india-media-bias-dashboard.git
cd india-media-bias-dashboard
```

**2. Run the setup script**

This creates a virtual environment and installs all dependencies.
```bash
python setup.py
```

When prompted, enter your NewsAPI key. This will be saved to a `.env` file locally and is never committed to the repository.

**3. Launch the dashboard**

On Windows, double-click `Launch Dashboard.exe` in the project folder.

Alternatively, run directly with Python:
```bash
python launch.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## Notes

- Data is fetched live on first load and cached for 6 hours. Use the **Refresh Data** button in the sidebar to force a fresh fetch.
- The `.env` file containing your API key is gitignored and will never be uploaded to the repository.
- The `data/` directory is also gitignored. Article data is fetched fresh on each session.

---

## Project context

Built for the BYOP (Bring Your Own Project) capstone component of CSA2001 — Fundamentals in AI and ML at VIT Bhopal University (Batch 2029). The project applies NLP and sentiment analysis concepts from the course to a real-world problem in Indian media literacy.
