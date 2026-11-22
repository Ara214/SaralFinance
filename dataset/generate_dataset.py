"""Build a fixed-size multilingual dataset, holding out entire scenario families."""
import csv
import random
from pathlib import Path

# category -> (count, scenarios). Each scenario has independent reference labels and three authored realizations.
CATALOG = {
    "bank_alert": (60, [
        ("Low", "", "Check posted debits in the official app.", "The alert reports a debit.", ["Card purchase at Demo Market: INR {amount} debited.", "डेमो मार्केट में कार्ड से ₹{amount} कटने की सूचना।", "Demo Market mein card se ₹{amount} debit ka alert hai."]),
        ("Low", "", "Verify the deposit in your statement.", "The alert reports a credit.", ["Savings account update: salary credit INR {amount}.", "बचत खाते में ₹{amount} वेतन जमा होने की सूचना।", "Savings account mein salary credit ₹{amount} ka alert."]),
        ("Medium", "unverified link", "Check the statement through your bank.", "The sender offers a link to review a debit.", ["Debit alert ₹{amount}. Review at https://statement-demo.invalid.", "₹{amount} कटने की सूचना। विवरण https://statement-demo.invalid पर देखें।", "₹{amount} katne ka alert. Details https://statement-demo.invalid par."]),
        ("High", "credential request", "Keep your PIN private and check the transaction directly.", "The sender asks for a PIN to reverse a debit.", ["Send your card PIN to reverse an INR {amount} debit.", "₹{amount} की कटौती वापस पाने के लिए पिन भेजें।", "₹{amount} ka debit reverse karne ke liye PIN bhejo."]),
        ("Low", "", "Review the refund in the official app.", "The notice claims a refund was initiated.", ["The merchant initiated a refund of INR {amount}. The balance may take time to update.", "व्यापारी ने ₹{amount} का रिफंड शुरू किया है। बैलेंस अपडेट होने में समय लग सकता है।", "Merchant ne ₹{amount} ka refund initiate kiya hai. Balance update hone mein time lag sakta hai."]),
    ]),
    "upi": (50, [
        ("Low", "", "Check the official UPI app.", "The alert reports a UPI payment.", ["UPI payment of INR {amount} to Demo Transit completed.", "डेमो ट्रांजिट को ₹{amount} का यूपीआई भुगतान होने की सूचना।", "Demo Transit ko ₹{amount} ka UPI payment complete hone ka alert."]),
        ("Low", "", "Check payment history before retrying.", "The sender reports a failed payment.", ["Your UPI payment of INR {amount} failed. Check history before retrying.", "₹{amount} का यूपीआई भुगतान विफल। दोबारा भुगतान से पहले हिस्ट्री देखें।", "₹{amount} ka UPI payment fail hua. Retry se pehle history check karein."]),
        ("High", "verification payment", "Decline the request and check your app.", "The sender wants a payment for verification.", ["Pay INR {amount} to verify your UPI profile.", "यूपीआई सत्यापन के लिए ₹{amount} का भुगतान करें।", "UPI verification ke liye ₹{amount} pay karo."]),
        ("Medium", "unknown collect request", "Check who sent the collect request before approving.", "The message claims a pending collect request.", ["Unfamiliar merchant requests INR {amount} via UPI collect.", "अज्ञात व्यापारी ने ₹{amount} की यूपीआई भुगतान रिक्वेस्ट भेजी है।", "Unknown merchant ki ₹{amount} ki UPI collect request pending hai."]),
        ("Low", "", "Verify the reversal in the official UPI app.", "The message reports a reversal.", ["UPI reversal for INR {amount} posted to your linked account.", "₹{amount} का यूपीआई रिवर्सल लिंक किए गए खाते में जमा होने की सूचना।", "Linked account mein ₹{amount} ka UPI reversal post hone ka alert."]),
    ]),
    "kyc": (40, [
        ("Low", "", "Open the bank app yourself to check the reminder.", "The message reminds the reader to review KYC.", ["Your KYC review is due on day {day}. Use the official app.", "केवाईसी की समीक्षा {day} तारीख को है। बैंक का आधिकारिक ऐप खोलें।", "KYC review {day} tareekh ko due hai. Official app kholo."]),
        ("Medium", "urgent KYC", "Check KYC status through the bank app.", "The sender pressures the reader to update KYC today.", ["KYC due today. Update it immediately before {day} pm.", "KYC आज देय है। इसे तुरंत अपडेट करें। समय सीमा {day} बजे।", "KYC aaj due hai. Abhi update karein, {day} baje tak."]),
        ("High", "threat, unverified link", "Avoid the link and check with the bank.", "The sender threatens a freeze and provides a link.", ["Account frozen after day {day} unless updated: https://identity-demo.invalid.", "अपडेट न करने पर {day} तारीख से खाता बंद होगा। https://identity-demo.invalid", "Update nahi kiya toh account band on day {day}. https://identity-demo.invalid"]),
        ("Low", "", "Check directly with your bank if needed.", "The notice claims KYC was completed.", ["Your KYC review finished on day {day}. No action required.", "{day} तारीख को केवाईसी समीक्षा पूरी होने की सूचना। कोई कार्रवाई नहीं करनी है।", "KYC review {day} tareekh ko complete bataya gaya hai. Kuch karna nahi hai."]),
        ("High", "credential request", "Keep the password private.", "The sender requests a password for identity checks.", ["For your KYC appointment on day {day}, reply with your password.", "{day} तारीख की केवाईसी जाँच के लिए पासवर्ड भेजें।", "Day {day} ki KYC appointment ke liye password bhejo."]),
    ]),
    "credentials": (40, [
        ("Low", "", "Keep codes private and verify unexpected activity.", "The notice advises against sharing an OTP.", ["A login was attempted on day {day}. Never share your OTP.", "{day} तारीख को लॉगिन का प्रयास हुआ। ओटीपी साझा न करें।", "Day {day} ko login attempt hua. OTP share mat karein."]),
        ("High", "credential request", "Keep the OTP private and contact official support.", "The sender asks for a secret code.", ["To confirm refund INR {amount}, reply with your OTP.", "₹{amount} की वापसी के लिए ओटीपी भेजें।", "₹{amount} refund ke liye OTP bhejo."]),
        ("High", "credential request", "Keep card security details private.", "The message asks for a CVV to release a payment.", ["Give your CVV to release a transfer of INR {amount}.", "₹{amount} का ट्रांसफर जारी करने के लिए सीवीवी बताएं।", "₹{amount} ka transfer release karne ke liye CVV batao."]),
        ("Low", "", "Review the change through your official app.", "The message claims a PIN changed.", ["A card PIN change was recorded on day {day}. If unexpected, open your official app.", "{day} तारीख को कार्ड पिन बदलने की सूचना। अनजान बदलाव हो तो बैंक का ऐप खोलें।", "Day {day} ko PIN change ka alert. Aapne nahi kiya toh official app kholo."]),
        ("High", "credential request, deceptive wording", "Verify the sender independently and never share the code.", "The sender disguises an OTP request.", ["Read out the digits from your login text to release INR {amount}.", "₹{amount} पाने के लिए लॉगिन संदेश में आए अंक बोलें।", "₹{amount} paane ke liye login SMS ki digits bol do."]),
    ]),
    "loan": (30, [
        ("Low", "", "Verify the amount with the lender.", "The notice claims a loan instalment is due.", ["Your monthly instalment of INR {amount} is due on day {day}.", "₹{amount} की मासिक किस्त {day} तारीख को देय है।", "₹{amount} ki monthly EMI {day} tareekh ko due hai."]),
        ("Low", "", "Check repayment history in the lender app.", "The notice claims an instalment was received.", ["We received your EMI payment of INR {amount}.", "₹{amount} की किस्त मिलने की सूचना।", "₹{amount} ki EMI receive hone ka message."]),
        ("High", "verification payment", "Do not pay a verification fee.", "The sender wants a fee to verify a loan.", ["Transfer INR {amount} to verify your loan before disbursal.", "ऋण सत्यापन के लिए ₹{amount} का भुगतान करें।", "Loan verification ke liye ₹{amount} transfer karo."]),
        ("Medium", "unverified link", "Check the lender app directly.", "The sender provides a link to an EMI notice.", ["See your INR {amount} repayment schedule at https://emi-review.invalid.", "₹{amount} की किस्त का शेड्यूल https://emi-review.invalid पर देखें।", "₹{amount} ki EMI schedule https://emi-review.invalid par dekho."]),
    ]),
    "insurance": (30, [
        ("Low", "", "Check the policy details through the insurer.", "The notice claims a premium is due.", ["A premium of INR {amount} is due on day {day}.", "₹{amount} का बीमा प्रीमियम {day} तारीख को देय है।", "₹{amount} ka insurance premium day {day} ko due hai."]),
        ("Low", "", "Confirm claim status directly with the insurer.", "The notice reports a claim acknowledgement.", ["Your claim for INR {amount} was received for review.", "₹{amount} का बीमा दावा समीक्षा के लिए प्राप्त होने की सूचना।", "₹{amount} ka claim review ke liye receive hone ka alert."]),
        ("High", "credential request", "Keep secret information private.", "The sender asks for a password to release a claim.", ["Provide your password to release your INR {amount} insurance claim.", "₹{amount} के बीमा दावे के लिए पासवर्ड भेजें।", "₹{amount} ke insurance claim ke liye password bhejo."]),
        ("Medium", "unverified link", "Verify renewal details in the official portal.", "The sender provides a renewal link.", ["Renewal quote INR {amount}: https://policy-renewal.invalid.", "₹{amount} का नवीनीकरण प्रस्ताव: https://policy-renewal.invalid।", "₹{amount} ka renewal quote https://policy-renewal.invalid par."]),
    ]),
    "reward_phishing": (30, [
        ("High", "reward, payment", "Avoid sending money for the reward.", "The message claims a prize and asks for a fee.", ["You won a lottery. Pay INR {amount} to claim it.", "लॉटरी में इनाम जीता। इनाम पाने के लिए ₹{amount} का भुगतान करें।", "Lottery mein inaam jeeta. Claim karne ke liye ₹{amount} pay karo."]),
        ("Medium", "unexpected reward", "Verify the offer independently.", "The sender claims the reader won a reward.", ["You won a voucher worth INR {amount}. A representative will contact you.", "आपने ₹{amount} का इनाम जीता। प्रतिनिधि आपसे संपर्क करेगा।", "Aapne ₹{amount} ka inaam jeeta. Representative call karega."]),
        ("High", "remote access", "Do not install remote access tools.", "The sender asks the reader to install remote access software.", ["Install AnyDesk for support with payment INR {amount}.", "₹{amount} के भुगतान में सहायता के लिए AnyDesk इंस्टॉल करें।", "₹{amount} payment help ke liye AnyDesk install karo."]),
        ("Low", "", "Verify any benefit in the official rewards activity.", "The alert reports earned cashback.", ["Demo card cashback of INR {amount} was credited to your rewards balance.", "डेमो कार्ड के रिवॉर्ड बैलेंस में ₹{amount} कैशबैक जमा होने की सूचना।", "Demo card ke rewards balance mein ₹{amount} cashback credit ka alert."]),
        ("High", "unknown app, unverified link", "Avoid the link and do not install APKs from messages.", "The sender directs the reader to download an APK.", ["Download the bonus APK for INR {amount} at https://demo-app.invalid.", "₹{amount} के बोनस के लिए APK डाउनलोड करें: https://demo-app.invalid।", "₹{amount} bonus ki APK download karo: https://demo-app.invalid."]),
    ]),
    "misc": (20, [
        ("Low", "", "Review the official app notice if needed.", "The message announces planned maintenance.", ["Mobile banking maintenance scheduled for day {day}.", "मोबाइल बैंकिंग में {day} तारीख को रखरखाव होगा।", "Day {day} ko mobile banking maintenance scheduled hai."]),
        ("Medium", "shortened link", "Use your official app to read statements.", "The sender links to a statement through a short URL.", ["New statement on day {day}. See https://short-demo.invalid/statement.", "{day} तारीख का नया स्टेटमेंट: https://short-demo.invalid/statement", "Day {day} ka new statement: https://short-demo.invalid/statement"]),
        ("High", "verification payment", "Avoid the payment and verify directly.", "The notice asks for a payment to unlock an account.", ["Pay INR {amount} to unlock your online account.", "ऑनलाइन खाते के सत्यापन के लिए ₹{amount} का भुगतान करें।", "Account unlock karne ke liye ₹{amount} pay karo."]),
        ("Low", "", "Check the balance independently.", "The message reports a balance update.", ["Available balance at end of day: INR {amount}.", "दिन के अंत में उपलब्ध बैलेंस ₹{amount} होने की सूचना।", "End of day available balance ₹{amount} ka alert."]),
    ]),
}
LANGUAGES = ("english", "hindi", "hinglish")


def build():
    rng = random.Random(4701)
    rows = []
    for category, (count, scenarios) in CATALOG.items():
        # Hold out family number 2 and the final family, including all translations and amount variants.
        held_out = {1, len(scenarios) - 1}
        for i in range(count):
            family = i % len(scenarios)
            level, indicators, action, explanation, templates = scenarios[family]
            locale = (i // len(scenarios) + family) % len(LANGUAGES)
            day = 1 + i // len(scenarios)
            amount = rng.randrange(175, 19000, 5) + i / 100
            msg = templates[locale].format(day=day, amount=f"{amount:.2f}")
            rows.append({
                "message_id": f"SF{len(rows) + 1:03}", "message_text": msg,
                "category": category, "language": LANGUAGES[locale],
                "ground_truth_risk": level, "risk_indicators": indicators,
                "expected_action": action, "reference_explanation": explanation,
                "scenario": f"{category}-{family + 1}", "split": "evaluation" if family in held_out else "development",
            })
    assert len(rows) == len({row["message_text"] for row in rows}) == 300
    rng.shuffle(rows)
    return rows


if __name__ == "__main__":
    data = build()
    with Path(__file__).with_name("synthetic_messages.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)
