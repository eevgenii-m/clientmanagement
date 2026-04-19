import smtplib

server = smtplib.SMTP("smtp.office365.com", 587, timeout=30)
server.ehlo()
server.starttls()
server.ehlo()

server.login("smtp@isstek.com", "scanner@110")
print("LOGIN OK")

server.quit()

from django.core.mail import send_mail

result = send_mail(
    subject="Django test",
    message="This is a test from Django.",
    from_email="smtp@isstek.com",
    recipient_list=["your-real-email@domain.com"],
    fail_silently=False,
)

print("send_mail result =", result)