import re
from urllib.parse import urlsplit

URL = re.compile(r"(?:https?://|www\.)[^\s<>]+|\b(?:bit\.ly|tinyurl\.com|t\.co)/[^\s<>]+", re.I)
SHORTENERS = {"short-demo.invalid", "bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "ow.ly"}
SECRET = r"(?:\botp\b|\bpin\b|\bcvv\b|password|ओटीपी|पिन|पासवर्ड|सीवीवी)"
REQUEST = r"(?:share|send|reply|enter|provide|tell|submit|give|bhej\w*|bata\w*|daal\w*|भेज\w*|बताएँ|बताएं|दर्ज|साझा)"
NEGATED = re.compile(
    rf"(?:never|do not|don't|dont)\s+(?:ever\s+)?{REQUEST}[^,;.!?]{{0,36}}{SECRET}"
    rf"|{SECRET}[^,;.!?]{{0,24}}(?:mat|नहीं|न)\s+{REQUEST}"
    rf"|(?:mat|नहीं|न)\s+{REQUEST}[^,;.!?]{{0,25}}{SECRET}"
    rf"|{SECRET}[^,;.!?]{{0,25}}{REQUEST}\s+(?:मत|न करें|na karein|mat karein)", re.I
)
RULES = [
    ("credential", 65, rf"{REQUEST}[^,;.!?]{{0,38}}{SECRET}|{SECRET}[^,;.!?]{{0,27}}{REQUEST}"),
    ("freeze", 35, r"account.{0,24}(?:frozen|suspended|blocked|band|freeze)|खाता.{0,24}(?:बंद|ब्लॉक)"),
    ("kyc", 25, r"kyc.{0,25}(?:urgent|immediate|today|abhi|turant|आज|तुरंत)|(?:urgent|immediate|abhi|तुरंत).{0,20}kyc"),
    ("reward", 45, r"(?:you (?:have )?won|lottery|inaam jeet|इनाम जीता|लॉटरी)"),
    ("remote", 65, r"(?:install|download|use|open|लगाएँ|करें|karo|karein).{0,35}(?:anydesk|teamviewer|remote access|screen sharing)|(?:anydesk|teamviewer|remote access).{0,28}(?:install|download|इंस्टॉल)"),
    ("app", 55, r"(?:install|download|इंस्टॉल|डाउनलोड).{0,30}(?:\.apk|apk|unknown app|अज्ञात ऐप)"),
    ("payment", 65, r"(?:pay|transfer|bhej\w*|भेजें|भुगतान).{0,50}(?:verify|verification|claim|unlock|satyaapan|सत्यापन|इनाम)"),
]
REASONS = {
    "credential": ("Requests confidential credentials", "गोपनीय जानकारी माँगता है", "Secret code ya password maang raha hai"),
    "freeze": ("Threatens to block the account", "खाता बंद करने की धमकी देता है", "Account block karne ki dhamki deta hai"),
    "kyc": ("Pressures you to complete KYC quickly", "तुरंत केवाईसी कराने का दबाव डालता है", "Jaldi KYC karne ka pressure deta hai"),
    "reward": ("Makes an unexpected reward claim", "अचानक इनाम मिलने का दावा करता है", "Achanak reward milne ka daava karta hai"),
    "remote": ("Requests remote access", "डिवाइस का दूर से नियंत्रण माँगता है", "Remote access maang raha hai"),
    "app": ("Requests installation of an unverified app", "असत्यापित ऐप इंस्टॉल करने को कहता है", "Unknown app install karne ko kehta hai"),
    "payment": ("Requests a verification or claim payment", "सत्यापन या इनाम के लिए पैसे माँगता है", "Verification ya claim ke liye paise maangta hai"),
    "link": ("Contains an unverified link", "इसमें एक असत्यापित लिंक है", "Ismein unverified link hai"),
    "shortener": ("Link hides the final destination", "लिंक असली वेबसाइट छिपाता है", "Link asli destination chhupa raha hai"),
}
WARNINGS = (
    "Verify through the official banking app or a verified number. Avoid links or contact details from this message and keep credentials private.",
    "बैंक के आधिकारिक ऐप या सत्यापित नंबर से जाँच करें। संदेश के लिंक और संपर्क विवरण से बचें और गोपनीय जानकारी साझा न करें।",
    "Official banking app ya verified number se check karein. Message ke links aur contact details use na karein aur secret codes share na karein.",
)


def assess(message, language="english"):
    index = ("english", "hindi", "hinglish").index(language)
    cleaned = NEGATED.sub(" ", message)
    matched = [(name, weight) for name, weight, pattern in RULES if re.search(pattern, cleaned, re.I)]
    links = URL.findall(message)
    if links:
        matched.append(("link", 30))
    for link in links:
        try:
            host = urlsplit(link if "://" in link else "https://" + link).hostname
        except ValueError:
            continue
        if host in SHORTENERS:
            matched.append(("shortener", 20))
            break
    score = min(100, sum(weight for _, weight in matched))
    return {
        "risk_level": "High" if score >= 65 else "Medium" if score >= 25 else "Low",
        "risk_score": score,
        "risk_reasons": [REASONS[name][index] for name, _ in matched],
        "risk_warning": WARNINGS[index] if matched else None,
    }
