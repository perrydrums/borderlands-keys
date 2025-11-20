# Borderlands 4 Shift Codes Monitor 🎮

A free, automated solution to monitor [MentalMars](https://mentalmars.com/game-news/borderlands-4-shift-codes/) for new Borderlands 4 SHiFT codes and receive email notifications when new codes are available.

## Features

- ✅ **Free hosting** using GitHub Actions
- ✅ **Daily automated checks** (runs at 9:00 AM UTC by default)
- ✅ **Email notifications** when new codes are found
- ✅ **Multiple email providers** supported (SendGrid, Resend, SMTP)
- ✅ **No server required** - completely serverless

## How It Works

1. The scraper runs daily via GitHub Actions
2. It fetches the MentalMars page and extracts all shift codes
3. Compares with previously seen codes stored in `known_codes.json`
4. Sends an email notification if new codes are found
5. Updates the state file to track seen codes

## Setup Instructions

### 1. Fork/Clone This Repository

```bash
git clone https://github.com/yourusername/borderlands-keys.git
cd borderlands-keys
```

### 2. Set Up Mailjet (Free - 6,000 emails/month)

Mailjet offers a free tier with 6,000 emails per month (200 per day), perfect for this project!

1. Sign up at [Mailjet](https://www.mailjet.com/)
2. Go to [Account Settings → API Keys](https://app.mailjet.com/account/apikeys)
3. Copy your **API Key** and **Secret Key**
4. Verify your sender email address:
   - Go to [Senders & Domains](https://app.mailjet.com/account/sender)
   - Add and verify your email address (check your inbox for verification email)

### 3. Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions, and add:

**Required:**
- `RECIPIENT_EMAIL`: Your email address to receive notifications
- `MAILJET_API_KEY`: Your Mailjet API Key
- `MAILJET_API_SECRET`: Your Mailjet Secret Key
- `MAILJET_FROM_EMAIL`: Your verified sender email address
- `MAILJET_FROM_NAME`: (Optional) Sender name, defaults to "Borderlands Monitor"

### 4. Test Locally (Optional)

```bash
# Install dependencies
pip install -r requirements.txt

# Option 1: Use .env file (recommended)
cp .env.example .env
# Edit .env file with your actual credentials
python scraper.py

# Option 2: Set environment variables manually
export RECIPIENT_EMAIL="your-email@example.com"
export MAILJET_API_KEY="your-mailjet-api-key"
export MAILJET_API_SECRET="your-mailjet-api-secret"
export MAILJET_FROM_EMAIL="your-verified-email@example.com"
python scraper.py
```

**Using .env file:**
1. Copy `.env.example` to `.env`: `cp .env.example .env`
2. Edit `.env` and fill in your actual credentials
3. Run `python scraper.py` - it will automatically load variables from `.env`
4. The `.env` file is gitignored, so your secrets stay local

### 5. Enable GitHub Actions

1. Push your code to GitHub
2. Go to Actions tab in your repository
3. The workflow will run automatically on the schedule (daily at 9:00 AM UTC)
4. You can also trigger it manually via "Run workflow"

### 6. Customize Schedule (Optional)

Edit `.github/workflows/daily-check.yml` to change the schedule:

```yaml
schedule:
  - cron: '0 9 * * *'  # 9:00 AM UTC daily
```

Cron format: `minute hour day month weekday`
- `0 9 * * *` = 9:00 AM UTC daily
- `0 14 * * *` = 2:00 PM UTC daily (9:00 AM EST)
- `0 0 * * *` = Midnight UTC daily

## Project Structure

```
borderlands-keys/
├── .github/
│   └── workflows/
│       └── daily-check.yml    # GitHub Actions workflow
├── scraper.py                  # Main scraper script
├── requirements.txt            # Python dependencies
├── known_codes.json            # State file (auto-generated)
├── .gitignore
└── README.md
```

## How It Detects New Codes

The scraper:
1. Extracts all codes from the "Every Borderlands 4 SHiFT Code for Golden Keys" table
2. Compares each code with previously seen codes in `known_codes.json`
3. Only sends notifications for codes that haven't been seen before
4. Updates the state file after each run

## Troubleshooting

### No emails received

1. Check GitHub Actions logs: Repository → Actions → Latest run
2. Verify your secrets are set correctly
3. Check your spam folder
4. For SendGrid: Verify your sender email is verified
5. For Gmail SMTP: Make sure you're using an App Password, not your regular password

### Scraper not finding codes

1. The website structure may have changed - check the HTML structure
2. View the Actions logs to see error messages
3. Test locally with `python scraper.py`

### GitHub Actions not running

1. Make sure Actions are enabled: Repository → Settings → Actions
2. Check the workflow file syntax
3. Verify the schedule is correct (GitHub Actions may have delays)

## Cost Breakdown

- **GitHub Actions**: Free for public repositories (2,000 minutes/month)
- **Mailjet**: Free tier (6,000 emails/month, 200/day)

**Total Cost: $0/month** 🎉

## License

MIT License - feel free to use and modify as needed!

## Contributing

Found a bug or want to improve something? Feel free to open an issue or submit a pull request!

## Acknowledgments

- [MentalMars](https://mentalmars.com/) for maintaining the shift codes page
- GitHub Actions for free CI/CD
- Mailjet for free email services
