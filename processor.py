import re
import joblib
from sentence_transformers import SentenceTransformer

from groq import Groq
from dotenv import load_dotenv

# -----------------------------------------------------------------------------------------------------------------
# Regex Classification
# -----------------------------------------------------------------------------------------------------------------
def classify_with_regex(log_message):
    regex_patterns = {
        r"wsgi\.server"                     : "HTTP Status",
        r"nova\.compute"                    : "Resource Usage",
        r"User User"                        : "User Action",
        r"Account with ID"                  : "User Action",
        r"Backup (started|completed|ended)" : "System Notification",
        r"System updated to version"        : "System Notification",
        r"File data_"                       : "System Notification",
        r"Disk cleanup"                     : "System Notification",
        r"\bRAID\b"                         : "Critical Error",
        r"(?i)ssl certificat"               : "Error",
        r"(?i)module x"                     : "Error"
    }
    for pattern, label in regex_patterns.items():
        if re.search(pattern, log_message):
            return label
    return None

# -----------------------------------------------------------------------------------------------------------------
# ML Model Classification
# -----------------------------------------------------------------------------------------------------------------
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

classification_model = joblib.load("artifacts/classifier.joblib")

def classify_with_ml_model(log_message):
    embeddings = embedding_model.encode([log_message])
    label = classification_model.predict(embeddings)[0]
    return label

# -----------------------------------------------------------------------------------------------------------------
# LLM Classification
# -----------------------------------------------------------------------------------------------------------------
load_dotenv()
groq = Groq()

def classify_with_llm(log_message):
    """
    Classifies a log message into predefined categories using Groq's LLM API
    """

    prompt = f'''Classify the log message into one of these categories:
    (1) Workflow Error, (2) Deprecation Warning.
    If you can't figure out a category, use 'Unclassified'.
    Put the category inside <category> </category> tags. 
    Log message: {log_message}'''

    chat_completion = groq.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="openai/gpt-oss-120b",
        temperature=0
    )

    content = chat_completion.choices[0].message.content
    
    match = re.search(r'<category>(.*?)<\/category>', content, flags=re.DOTALL)      # re.DOTALL checks all lines, even after \n
    # r'<category>(.*)<\/category>' uses greedy matching. If LLM outputs multiple <category>...</category> ... </category>, it will capture everything in between
    
    label = 'Unclassified'
    if match:
        label = match.group(1).strip()      # match.group(1) gives the actual string between the tags

    return label

# -----------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    print(classify_with_regex("Backup completed successfully."))
    print(classify_with_ml_model("IP 192.168.133.114 blocked due to potential attack"))
    print(classify_with_llm("The 'BulkEmailSender' feature is no longer supported. Use 'EmailCampaignManager' for improved functionality."))