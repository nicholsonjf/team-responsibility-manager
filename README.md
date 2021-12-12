# Team Responsibility Manager (TRM)

TRM keeps track of shared responsibilities and notifies teams when a responsibility rotates from one person to the next. The main concepts to understand in TRM are Responsibilities, Teams and People. 

When you configure TRM you define a Responsibility, the Team that is responsible for it, and the People that are members of that Team. You also define when that Responsibility rotates from one Person to the next. When a Responsibility rotates, the next Person is notified in the Team's Slack channel.

## Example Use Case

Imagine a youth soccer team with 12 players. The parents and the coaches agreed at the beginning of the season that the parents would provide snacks and drinks for the kids after every practice. The team practices every weekday, and every practice the responsibility for bringing snacks will rotate from one player's parents to the next. They could use a shared spreadsheet that lists who is responsibile for what practice but this approach has some drawbacks. Every parent will need to be constantly checking the spreadsheet to see if it's their day to bring snacks. The parents could enter the dates into shared calendar. But what if a player leaves the team? Those parents' practices will need to be reassigned to the remaining parents. The parents can use TRM to solve both of these problems. Simply setup a Responsibility named "Soccer Snacks" to rotate every weekday at 9am. A Slack message will sent at 9am every weekday to the team's Slack channel letting them know which parent is responsible that day. If a player leaves the soccer team, all you need to do is remove their parents from the Team in the configuration file and TRM will seamlessly adjust.

## Deploy on Amazon Web Services

Step 1.

### Resources Created on AWS During Deployment

CloudFormation Stacks
Lambda Function
S3 Buckets
ECR Repository
CloudWatch Log Group


## Slack
Sends messages to #trp-test.

## Configuration
When you deploy TRM in AWS a file named `config.json` will be created in the the S3 bucket you specified during deployment. Download that file
and open it in your preferred JSON document editor. When you're done making changes, upload it to the same location in S3.

### enabled
If set to `"true"` TRM will rotate Responsibilities and send notifications as configured in `config.json`. If set to `"false"` TRM will stop rotating responsibilities and won't send any notifications. When you're ready start rotating again just set it back to `"true"`.
### timezone
The config file requires the "hour" of day for certain properties. Enter the timezone that should be used when interpreting those times. Use a value from the "TZ database name" column in this list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

```json
{
  "timezone": "America/New_York"
}
```

## Example config.json


```json
{
    "enabled": "false",
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
        "garbage_collector": {
            "name": "Garbage Collector",
            "team": "my_team",
            "rotation": {
                "frequency": "weekdaily",
                "hour": "8"
            },
            "slack_channel": "my_channel"
        }
    }
}
```