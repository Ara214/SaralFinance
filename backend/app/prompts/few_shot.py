import json
from .role_based import INSTRUCTIONS as ROLE

EXAMPLES = [
    ("english", "Card debit notice: ₹219 paid at Demo Kirana.", "The notice says ₹219 was spent using your card.", "Check the card activity in your official banking app."),
    ("hindi", "खाते में ₹740 जमा होने की सूचना।", "संदेश के अनुसार खाते में ₹740 जमा हुए हैं।", "बैंक के आधिकारिक ऐप में अपना बैलेंस देखें।"),
    ("hinglish", "Reply with your OTP for a refund.", "Message refund ke liye aapse OTP maang raha hai.", "OTP share mat karein. Official app mein refund status check karein."),
    ("english", "Send your PIN to finish KYC or your account will close.", "The message threatens account closure and asks for your PIN to complete identity verification.", "Keep your PIN private and check your KYC status directly in your bank’s app."),
    ("hindi", "₹1290 की ईएमआई अगले सोमवार को देय है।", "संदेश में कहा गया है कि ₹1290 की किस्त अगले सोमवार को देनी है।", "ऋणदाता के आधिकारिक ऐप पर तारीख और राशि जाँचें।"),
    ("hinglish", "You won a tablet. Pay ₹141 to claim it.", "Message tablet jeetne ka daava karta hai aur badle mein ₹141 maangta hai.", "Reward claim karne ke liye paise na bhejein."),
]
INSTRUCTIONS = ROLE + "\nReturn exactly one JSON object with what_happened, what_to_do_next (an array) and analogy (string or null).\nDemonstrations:\n" + "\n".join(
    json.dumps({"language": lang, "message": msg, "output": {
        "what_happened": summary, "what_to_do_next": [step], "analogy": None
    }}, ensure_ascii=False) for lang, msg, summary, step in EXAMPLES
)
