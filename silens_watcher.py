import requests
from datetime import datetime, timedelta
from dateutil import parser
from datetime import timezone

now = datetime.now(timezone.utc)
# Конфигурация
ALERTMANAGER_URL = "http://127.0.0.1:9093"  
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/xxxxxx" 
DAYS_TO_CHECK = 2  # Количество дней для фильтрации

def get_silences():
    """Получить список silence из Alertmanager."""
    url = f"{ALERTMANAGER_URL}/api/v2/silences"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении silence: {response.status_code}")
        return []

def filter_recent_silences(silences, days):
    now = datetime.now(timezone.utc)
    return [
        silence for silence in silences
        if now - parser.isoparse(silence["updatedAt"]) <= timedelta(days=days)
    ]

def filter_expiring_silences(silences, days):
    now = datetime.now(timezone.utc)
    return [
        silence for silence in silences
        if now <= parser.isoparse(silence["endsAt"]) <= now + timedelta(days=days)
    ]

def format_silences_block(silences, title):
    """Формируем текстовый блок для Slack."""
    if not silences:
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{title}:*\nНет записей."
            }
        }

    silence_lines = []
    for silence in silences:
        matchers = ", ".join([f"{m['name']}={m['value']}" for m in silence["matchers"]])
        starts_at = parser.isoparse(silence["startsAt"]).strftime("%Y-%m-%d %H:%M:%S")
        ends_at = parser.isoparse(silence["endsAt"]).strftime("%Y-%m-%d %H:%M:%S")
        comment = silence.get("comment", "нет комментария")
        silence_url = f"{ALERTMANAGER_URL}/silences/{silence['id']}"
        silence_lines.append(f"- *Matchers:* {matchers}\n  *Start:* {starts_at}\n  *End:* {ends_at}\n  *Comment:* {comment}\n  <{silence_url}|Перейти к silence>")

    block_text = f"*{title}:*\n" + "\n\n".join(silence_lines)
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": block_text
        }
    }

def send_summary_to_slack(recent_silences, expiring_silences):
    """Отправить общее сообщение в Slack."""
    blocks = []

    blocks.append(format_silences_block(recent_silences, "Сайленсы, созданные за последние 2 дня"))
    blocks.append({"type": "divider"})
    blocks.append(format_silences_block(expiring_silences, "Сайленсы, истекающие в ближайшие 2 дня"))

    message = {
        "text": "Отчет по сайленсам Alertmanager",
        "blocks": blocks
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=message)
    if response.status_code != 200:
        print(f"Ошибка при отправке в Slack: {response.status_code}")

def main():
    silences = get_silences()
    recent_silences = filter_recent_silences(silences, DAYS_TO_CHECK)
    expiring_silences = filter_expiring_silences(silences, DAYS_TO_CHECK)

    send_summary_to_slack(recent_silences, expiring_silences)

if __name__ == "__main__":
    main()
