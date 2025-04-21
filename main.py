import requests
import time
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


# ====== CONFIG FROM ENV ======
DOMAIN = "innerspacegroup.com"
GODADDY_API_KEY = os.getenv("GODADDY_API_KEY")
GODADDY_API_SECRET = os.getenv("GODADDY_API_SECRET")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
CHECK_INTERVAL_SECONDS = 600  # 10 minutes

headers = {
    "Authorization": f"sso-key {GODADDY_API_KEY}:{GODADDY_API_SECRET}"
}

def is_domain_available(domain):
    url = f"https://api.godaddy.com/v1/domains/available?domain={domain}&checkType=FAST"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("available", False)
    else:
        print(f"⚠️ GoDaddy API error: {response.status_code} - {response.text}")
        return False

def send_email(domain):
    subject = f"Hi! Looks like {domain} is finally available 🔓"

    plain_body = f"""
Hey,

Quick heads-up — the domain {domain} is now available!

If you've been waiting for it, now’s a great time to grab it before someone else does.

You can check it here:
https://www.godaddy.com/domainsearch/find?checkAvail=1&domainToCheck={domain}

Let me know if you'd like to stop these notifications.

Cheers,  
– Your Domain Watcher Bot
"""

    html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; font-size: 15px; color: #333;">
    <p>Hey,</p>
    <p>Just a quick heads-up — the domain <strong>{domain}</strong> is now available!</p>
    <p>
      <a href="https://www.godaddy.com/domainsearch/find?checkAvail=1&domainToCheck={domain}" style="color: #1a73e8;">
        👉 Click here to view or register it on GoDaddy
      </a>
    </p>
    <p style="margin-top: 20px;">Let me know if you want to stop getting these alerts.</p>
    <p style="margin-top: 10px;">– Your Domain Watcher Bot</p>
  </body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg['From'] = f"Domain Watcher <{EMAIL_SENDER}>"
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject

    msg.attach(MIMEText(plain_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

    print(f"📩 Email sent to {EMAIL_RECEIVER}")


# ====== MAIN LOOP ======
print(f"🔁 Watching domain: {DOMAIN}")
while True:
    try:
        if is_domain_available(DOMAIN):

            print(f"✅ Domain available: {DOMAIN}")
            send_email(DOMAIN)
            break
        else:
            print(f"❌ Still taken: {DOMAIN} — retrying in {CHECK_INTERVAL_SECONDS // 60} mins...")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    time.sleep(CHECK_INTERVAL_SECONDS)
