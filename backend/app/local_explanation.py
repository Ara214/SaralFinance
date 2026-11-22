"""Template explanations for arbitrary messages when remote generation is unavailable."""
import re

from .risk_detector import URL
from .schemas import Explanation

AMOUNT = re.compile(r"(?:₹|\bINR\s*|\bRs\.?\s*)(\d[\d,]{0,11}(?:\.\d{1,2})?)(?![\d,])", re.I)
TOPICS = [
    (r"\bkyc\b|केवाईसी", ("a KYC or identity check", "केवाईसी या पहचान की जाँच", "KYC ya identity check")),
    (r"\bemi\b|instal+ment|\bloan\b|किस्त|ऋण", ("a loan or instalment", "ऋण या किस्त", "loan ya EMI")),
    (r"insurance|premium|बीमा|प्रीमियम", ("insurance or a premium", "बीमा या प्रीमियम", "insurance ya premium")),
    (r"\brefund\b|रिफंड", ("a refund", "रिफंड", "refund")),
    (r"reward|prize|lottery|voucher|इनाम|inaam", ("a reward or offer", "इनाम या ऑफ़र", "reward ya offer")),
    (r"\b(?:otp|pin|cvv|password)\b|ओटीपी|पासवर्ड", ("a security code or credential", "सुरक्षा कोड या गोपनीय जानकारी", "security code ya password")),
    (r"\bdebit(?:ed)?\b|deduct|कटे|कटा|कटने", ("money leaving an account", "खाते से पैसे कटने", "account se paise katne")),
    (r"\bcredit(?:ed)?\b|deposit|जमा", ("money coming into an account", "खाते में पैसे जमा होने", "account mein paise aane")),
    (r"\bupi\b|यूपीआई|payment|भुगतान", ("a UPI or payment update", "यूपीआई या भुगतान की जानकारी", "UPI ya payment update")),
]
COPY = {
    "english": ("The message appears to be about {}.", "The message mentions {}.",
                "The message alone does not confirm a transaction or identify the sender.",
                "Open the official app or website yourself and check the relevant activity or notice."),
    "hindi": ("यह संदेश {} के बारे में लगता है।", "संदेश में {} की राशि लिखी है।",
              "केवल इस संदेश से भेजने वाले या लेन-देन की पुष्टि नहीं होती।",
              "आधिकारिक ऐप या वेबसाइट सीधे खोलें और संबंधित गतिविधि या सूचना देखें।"),
    "hinglish": ("Message {} ke baare mein lagta hai.", "Message mein {} ki amount likhi hai.",
                 "Sirf is message se sender ya transaction verify nahi hota.",
                 "Official app ya website khud kholkar related activity ya notice check karein."),
}


def explain_locally(message, language, risk):
    text = URL.sub(" ", message)
    index = tuple(COPY).index(language)
    topic = next((translations[index] for pattern, translations in TOPICS
                  if re.search(pattern, text, re.I)), None)
    topic_text, amount_text, general, step = COPY[language]
    parts = [topic_text.format(topic)] if topic else []
    amounts = list(dict.fromkeys("₹" + item for item in AMOUNT.findall(text)))
    if amounts:
        parts.append(amount_text.format(", ".join(amounts[:3])))
    if not parts:
        parts.append(general)
    return Explanation(what_happened=" ".join(parts),
                       what_to_do_next=[risk["risk_warning"] or step])
