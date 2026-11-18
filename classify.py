from processor import classify_with_regex, classify_with_ml_model, classify_with_llm

def classify_record(source, log_message):
    if source=='LegacyCRM':
        label = classify_with_llm(log_message)
    else:
        label = classify_with_regex(log_message)
        if not label:
            label = classify_with_ml_model(log_message)
    return label

def classify_logs(logs_collection):
    """
    Input  : List of Tuples (source, log_message)
    Output : List of Classification Labels
    Calls classify_record function internally for classifying individual records
    """
    labels = []
    for source, log_message in logs_collection:
        label = classify_record(source, log_message)
        labels.append(label)

    return labels

#---------------------------------------------------------------------------------------------------------------
# import pandas as pd
# def classify_logs_csv(filepath):
#     try:
#         df = pd.read_csv(filepath)
#         df['target_label'] = classify_logs(list(zip(df['source'], df['log_message'])))
#         df.to_csv('resources/output.csv', index=False)
#         print('Output CSV file with target_labels created')
#     except FileNotFoundError:
#         print('The expected input CSV file is missing.')
#---------------------------------------------------------------------------------------------------------------



if __name__ == '__main__':

    logs = [
        ("ModernCRM", "IP 192.168.133.114 blocked due to potential attack"),
        ("BillingSystem", "User User12345 logged in."),
        ("AnalyticsEngine", "File data_6957.csv uploaded successfully by user User265."),
        ("AnalyticsEngine", "Backup completed successfully."),
        ("ModernHR", "GET /v2/54fadb412c4e40cdbaed9335e4c35a9e/servers/detail HTTP/1.1 RCODE  200 len: 1583 time: 0.1878400"),
        ("ModernHR", "Admin access escalation detected for user 9429"),
        ("LegacyCRM", "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active."),
        ("LegacyCRM", "Invoice generation process aborted for order ID 8910 due to invalid tax calculation module."),
        ("LegacyCRM", "The 'BulkEmailSender' feature is no longer supported. Use 'EmailCampaignManager' for improved functionality."),
        ("LegacyCRM", " The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025")
    ]
    print(classify_logs(logs))
#    classify_logs_csv('resources/input.csv')