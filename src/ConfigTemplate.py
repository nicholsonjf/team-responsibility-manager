body = """
{
    "enabled": "true",
    "timezone": "America/New_York",
    "slack": {
        "channels": {
            "my_channel": {
                "webhook": "https://hooks.slack.com/services/YYYY/XXXXX"
            }
        }
    },
    "people": {
        "jdoe": {
            "firstName": "Jane",
            "lastName": "Doe",
            "slackUID": "UXXXXXXX"
        }
    },
    "teams": {
        "my_team": {
            "people": [
                "jdoe"
            ]
        }
    },
    "responsibilities": {
        "meeting_facilitator": {
            "name": "Meeting Facilitator",
            "team": "my_team",
            "rotation": {
                "frequency": "weekly",
                "day": "monday",
                "hour": "8"
            },
            "slack_channel": "my_channel"
        }
    }
}
"""
