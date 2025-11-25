
import requests
from config import JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN, PROJECT_KEY

auth = (JIRA_EMAIL, JIRA_API_TOKEN)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def adf(text: str):
    if not text:
        text = ""
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": text}]
            }
        ]
    }

# Convert "1h 30m" → "1h 30m" (Jira accepts this directly)
def to_jira_time(estimate: str | None):
    if not estimate:
        return None
    return estimate

def create_epic(summary: str, description: str, assignee_id: str | None, estimate: str | None = None):
    url = f"{JIRA_DOMAIN}/rest/api/3/issue"

    fields = {
        "project": {"key": PROJECT_KEY},
        "summary": summary,
        "description": adf(description),
        "issuetype": {"name": "Epic"},
        "customfield_10011": summary,
    }

    if assignee_id:
        fields["assignee"] = {"accountId": assignee_id}

    jira_time = to_jira_time(estimate)
    if jira_time:
        fields["timetracking"] = {"originalEstimate": jira_time}

    return requests.post(url, json={"fields": fields}, headers=headers, auth=auth).json()

def add_comment(issue_key: str, comment: str):
    url = f"{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}/comment"
    payload = {
        "body": adf(comment)  # используем твою функцию adf для ADF текста
    }
    return requests.post(url, json=payload, headers=headers, auth=auth).json()

def create_story(summary: str, description: str, epic_key: str, assignee_id: str | None, estimate: str | None = None):
    url = f"{JIRA_DOMAIN}/rest/api/3/issue"

    fields = {
        "project": {"key": PROJECT_KEY},
        "summary": summary,
        "description": adf(description),
        "issuetype": {"name": "Story"},
        "customfield_10014": epic_key,
    }

    if assignee_id:
        fields["assignee"] = {"accountId": assignee_id}

    jira_time = to_jira_time(estimate)
    if jira_time:
        fields["timetracking"] = {"originalEstimate": jira_time}

    return requests.post(url, json={"fields": fields}, headers=headers, auth=auth).json()

def create_task(summary: str, description: str, assignee_id: str | None, estimate: str | None = None):
    url = f"{JIRA_DOMAIN}/rest/api/3/issue"

    fields = {
        "project": {"key": PROJECT_KEY},
        "summary": summary,
        "description": adf(description),
        "issuetype": {"name": "Task"},
    }

    if assignee_id:
        fields["assignee"] = {"accountId": assignee_id}

    jira_time = to_jira_time(estimate)
    if jira_time:
        fields["timetracking"] = {"originalEstimate": jira_time}

    return requests.post(url, json={"fields": fields}, headers=headers, auth=auth).json()

def create_subtask(summary: str, description: str, parent_id: str, assignee_id: str | None, estimate: str | None = None):
    url = f"{JIRA_DOMAIN}/rest/api/3/issue"

    fields = {
        "project": {"key": PROJECT_KEY},
        "summary": summary,
        "description": adf(description),
        "issuetype": {"name": "Sub-task"},
        "parent": {"id": parent_id},
    }

    if assignee_id:
        fields["assignee"] = {"accountId": assignee_id}

    jira_time = to_jira_time(estimate)
    if jira_time:
        fields["timetracking"] = {"originalEstimate": jira_time}

    return requests.post(url, json={"fields": fields}, headers=headers, auth=auth).json()
