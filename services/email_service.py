import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading

def send_overbudget_email_async(category: str, limit: float, spent: float, user_email: str):
    """Sends email asynchronously to avoid blocking the API request."""
    if not user_email:
        return
    
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    if not app_password:
        print("Email not sent: GMAIL_APP_PASSWORD not set in .env")
        return

    def _send():
        msg = MIMEMultipart()
        msg['From'] = user_email
        msg['To'] = user_email
        msg['Subject'] = f"Budget Alert: Exceeded limit for {category}!"

        body = f"""
        Hello,
        
        You have exceeded your monthly budget for {category}.
        
        Limit: ₹{limit:.2f}
        Currently Spent: ₹{spent:.2f}
        
        Consider reviewing your recent transactions!
        
        - FinanceAI
        """
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(user_email, app_password)
            text = msg.as_string()
            server.sendmail(user_email, user_email, text)
            server.quit()
            print(f"Alert email sent to {user_email} for {category}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    threading.Thread(target=_send).start()
