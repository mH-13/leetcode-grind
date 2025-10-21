# leetcode-grind

Beautiful LeetCode problem tracker with **auto-fetch from URL**, interactive dashboard, and one-command workflow!

## ✨ Key Features

🤖 **Auto-fetch** - Paste LeetCode URL, get title/tags/difficulty/code automatically
🧙 **Interactive wizard** - One command does everything
📊 **Beautiful dashboard** - Heatmap, charts, and stats
🎨 **Cream aesthetic** - Easy on the eyes
🚀 **Full automation** - File creation, sync, git commit & push

## 🚀 Quick Start

```bash
# 1. Fetch problem from LeetCode URL
python scripts/fetch_leetcode.py https://leetcode.com/problems/two-sum/

# 2. Run wizard (auto-loads fetched data!)
./daily.sh

# 3. Select track → Done!
```

## 📊 Progress

<!-- PROGRESS:lc75:start -->Leetcode 75: 5/76 (7%)<!-- PROGRESS:lc75:end -->
<!-- PROGRESS:ti150:start -->Top Interview 150: 0/5 (0%)<!-- PROGRESS:ti150:end -->
<!-- PROGRESS:sql50:start -->Sql 50: 1/4 (25%)<!-- PROGRESS:sql50:end -->

## 🌐 Dashboard

Live at: `https://mh-13.github.io/leetcode-grind/`

- Progress cards with animated counters
- GitHub-style activity heatmap (365 days)
- Difficulty distribution charts
- Tag cloud visualization
- Recent activity feed
- Filterable problem list

## 📖 Full Documentation

See **[GUIDE.md](./GUIDE.md)** for complete guide including:
- Detailed workflow
- Pro tips and aliases
- Customization
- Troubleshooting

## 🛠️ Setup (One-Time)

```bash
git clone https://github.com/mh-13/leetcode-grind.git
cd leetcode-grind
pip install requests
chmod +x daily.sh
```

Enable GitHub Pages: Settings → Pages → Source: `docs/`

## 💡 Pro Tip

```bash
# Add to ~/.bashrc or ~/.zshrc
alias lcf='python ~/Codes/leetcode-grind/scripts/fetch_leetcode.py'
alias lc='cd ~/Codes/leetcode-grind && ./daily.sh'
```

Then:
```bash
lcf <paste-leetcode-url>  # Auto-fetch
lc                         # Run wizard
```

## 📁 Structure

```
python/leetcode-75/0001_two_sum.py
       └─ track ─┘ └id┘└── slug ──┘
```

Always 4-digit ID, underscore slug

---

**Made with ☕ and automation** • See [GUIDE.md](./GUIDE.md) for details
