mail.send_mail(sender=sender_address,
                   to="Albert Johnson <Albert.Johnson@example.com>",
                   subject="Your account has been approved",
                   body="""Dear Albert:

Your example.com account has been approved.  You can now visit
http://www.example.com/ and sign in using your Google Account to
access new features.

Please let us know if you have any questions.

The example.com Team
""")
