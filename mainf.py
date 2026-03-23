import os
import re
# tldextract is a Python library used to extract the subdomain, domain, and top-level domain (TLD) from a URL accurately
import tldextract
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


# Load environment variables
load_dotenv()


# Extract Links from SMS
def extract_links(text):
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)


# Analyze Domains
def analyze_links(links):
    domains = []
    
    for link in links:
        ext = tldextract.extract(link)
        domain = f"{ext.domain}.{ext.suffix}"
        domains.append(domain)
        
    return domains


# Prompt Template
prompt = PromptTemplate.from_template("""
You are an AI assistant specialized in detecting SMS fraud.

Analyze the following SMS message and determine if it is:

1. Fraud / Scam
2. Legitimate / Real

Check for:
- Suspicious links
- Fake bank domains
- Requests for OTP, password, PIN
- Urgent messages
- Prize or lottery scams
- Account suspension threats

SMS Message:
{sms}

Links Found:
{links}

Return the result in this format:

Fraud Status: Fraud or Real

Confidence: Low / Medium / High
""")


# Gemini Model
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2
)

parser = StrOutputParser()

# Chain
chain = prompt | model | parser


#Example SMS
# sms = """
# Dear customer, your Kotak KYC is pending. Update immediately at https://bit.ly/kyc-update to avoid account block.
# """

sms = """Thank you for using Axis Bank net banking services."""

# Extract and analyze links
links = extract_links(sms)
domains = analyze_links(links)


# Run the chain
result = chain.invoke({
    "sms": sms,
    "links": domains
})

print("\nSMS Fraud Detection Result:\n")
print(result)