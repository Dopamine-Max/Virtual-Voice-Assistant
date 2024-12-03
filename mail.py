import smtplib

def get_email_from_database(text, database_file):
    names = [name.strip() for name in text.split()]
    with open(database_file, 'r') as file:
        for line in file:
            for name in names:
                if name in line:
                    print(name)
                    return line.split('<')[1].strip('>').strip()

def send_email(recipient_email, subject, content):

    # Compose the email
    email_message = f"Subject: {subject}\n\n{content}"

    # SMTP configuration
    smtp_server = 'smtp.gmail.com'  # Update with your SMTP server
    smtp_port = 587  # Use 465 for SSL/TLS, or 587 for STARTTLS

    # Sender's email credentials
    sender_email = '2205153@kiit.ac.in'  # Update with your email
    sender_password = 'txwf oche kyju bssj'  # Update with your email password

    # Connect to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        # Start TLS for security
        server.starttls()

        # Login to the email account
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, email_message)

