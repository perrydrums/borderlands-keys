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

### 2. Choose an Email Provider

You have three options for sending emails:

#### Option A: SendGrid (Recommended - 100 emails/day free)

1. Sign up at [SendGrid](https://sendgrid.com/)
2. Create an API key in Settings → API Keys
3. Verify your sender email address

#### Option B: Resend (3,000 emails/month free)

1. Sign up at [Resend](https://resend.com/)
2. Create an API key
3. Verify your domain or use their test domain

#### Option C: SMTP (Gmail or other SMTP server)

1. For Gmail, create an [App Password](https://support.google.com/accounts/answer/185833)
2. Use your email and app password

### 3. Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions, and add:

**Required:**
- `RECIPIENT_EMAIL`: Your email address to receive notifications

**For SendGrid:**
- `EMAIL_PROVIDER`: `sendgrid`
- `SENDGRID_API_KEY`: Your SendGrid API key
- `SENDGRID_FROM_EMAIL`: Your verified sender email

**For Resend:**
- `EMAIL_PROVIDER`: `resend`
- `RESEND_API_KEY`: Your Resend API key
- `RESEND_FROM_EMAIL`: Your sender email (e.g., `notifications@resend.dev`)

**For SMTP:**
- `EMAIL_PROVIDER`: `smtp`
- `SMTP_SERVER`: `smtp.gmail.com` (or your SMTP server)
- `SMTP_PORT`: `587`
- `SMTP_USER`: Your email address
- `SMTP_PASSWORD`: Your app password or SMTP password

### 4. Test Locally (Optional)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export RECIPIENT_EMAIL="your-email@example.com"
export EMAIL_PROVIDER="sendgrid"  # or "resend" or "smtp"
export SENDGRID_API_KEY="your-api-key"  # if using SendGrid

# Run the scraper
python scraper.py
```

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
- **SendGrid**: Free tier (100 emails/day)
- **Resend**: Free tier (3,000 emails/month)
- **SMTP**: Free (Gmail, etc.)

**Total Cost: $0/month** 🎉

## License

MIT License - feel free to use and modify as needed!

## Contributing

Found a bug or want to improve something? Feel free to open an issue or submit a pull request!

## Acknowledgments

- [MentalMars](https://mentalmars.com/) for maintaining the shift codes page
- GitHub Actions for free CI/CD
- SendGrid/Resend for free email services
