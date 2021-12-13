# Team Responsibility Manager (TRM)

TRM keeps track of shared responsibilities and notifies teams when a responsibility rotates from one person to the next. The main concepts to understand in TRM are Responsibilities, Teams and People. 

When you configure TRM you define a Responsibility, the Team that is responsible for it, and the People that are members of that Team. You also define when that Responsibility rotates from one Person to the next. When a Responsibility rotates, the next Person is notified in the Team's Slack channel.

## Quickstart

This is a basic description of how to deploy the application. There's more detail on the deployment process further down in the readme.

**Step 1:**  
Login to the AWS console and switch to the "us-east-2" region.

**Step 2:**  
Go to the app's page on the AWS Serverless Application Repository:
https://serverlessrepo.aws.amazon.com/applications/us-east-2/825297539859/team-responsibility-manager

Add a bucket name, and click "Deploy".

**Step 3:**  
Setup your Slack app. See below for instructions.

**Step 4:**  
Fill in your config.json file. See below for instructions.

**Step 5:**  
That's it! Wait for your configured responsibilities to rotate and look out for notifications in Slack.

## Video Demos

Five minute summary video: https://youtu.be/kwhgHMHvxpc

Twenty minute in-depth discussion: https://youtu.be/aS-aM4hmNWg

## Example Use Case

Imagine a youth soccer team with 12 players. The parents and the coaches agreed at the beginning of the season that the parents would provide snacks and drinks for the kids after every practice. The team practices every weekday, and every practice the responsibility for bringing snacks will rotate from one player's parents to the next. They could use a shared spreadsheet that lists who is responsibile for what practice but this approach has some drawbacks. Every parent will need to be constantly checking the spreadsheet to see if it's their day to bring snacks. The parents could enter the dates into shared calendar. But what if a player leaves the team? Those parents' practices will need to be reassigned to the remaining parents. The parents can use TRM to solve both of these problems. Simply setup a Responsibility named "Soccer Snacks" to rotate every weekday at 9am. A Slack message will sent at 9am every weekday to the team's Slack channel letting them know which parent is responsible that day. If a player leaves the soccer team, all you need to do is remove their parents from the Team in the configuration file and TRM will seamlessly adjust.

## Deploy on Amazon Web Services

**Step 1:**    
Login to the AWS console and switch to the "us-east-2" region.  

(*Currently us-east-2 is the only region that's supported for this application's deployment. This is because container repositories on AWS ECR are only available from within a region. There may be a way around this but I'm not aware of how yet*)

**Step 2:**    
In the servies search box type in "Serverless Application Repository" and click on the first result.

**Step 3:**    
Click on "Available Applications"

**Step 4:**    
Under "Public Applications" type in "Team Responsibility Manager" and click on the first result.

**Step 5:**    
Scroll down to "Application Settings" and enter a name for the S3 bucket that will be created during deployment. It needs to be globally unique, so choose a name with attributes specific to you. Example: "harvard-trm-bucket-54321"

You can leave the other application settings as their defaults.

**Step 6:**    
Click "Deploy"

## Check The Deployment

Before setting up your config file, make sure the application deployed succesfully. Go to CloudWatch in your AWS console and click on the stack that was created. It should be named "serverlessrepo-team-responsibility-manager" or something similar. If it says "CREATE_COMPLETE" you're ready to setup your config file. If not, click on the "Events" tab to see what went wrong.

### Resources Created on AWS During Deployment

1 CloudFormation Stack

1 Lambda Function

1 S3 Bucket

1 CloudWatch Log Group

1 EventBridge Rule

1 Lambda Permission

1 IAM Role

To see the specific resources created go to CloudFormation and look at the stack that was created.


## Slack
In order for TRM to send notifications to the Slack channel you specify in your config.json you'll need to create a Slack app and setup incoming webhooks. If you want to create a new channel for TRM to use, do that from your Slack app before completing the below steps.

**Step 1:**  
Go to https://api.slack.com/apps and login to your Slack account. Once logged in, click the "Create New App" button.

**Step 2:**  
In the dialog that pops up, click on "From an app manifest". Select the workspace you want to receive notifications in.

**Step 3:**  
Paste in the below YAML as your app manifest.

```YAML
_metadata:
  major_version: 1
  minor_version: 1
display_information:
  name: Team Responsibility Manager
features:
  bot_user:
    display_name: Team Responsibility Manager
    always_online: false
oauth_config:
  scopes:
    bot:
      - incoming-webhook
settings:
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false
```

This creates a very basic Slack app that simply allows you to create incoming webhooks so TRM can send messages to Slack channels in your workspace.

**Step 4:**  
Once your app is created, click on its name under "Your Apps". This will take you to your app's configuration page. Once there, click on the "Incoming Webhooks" section in the left menu.

**Step 5:**  
If the "Activate Incoming Webhooks" switch isn't already enabled, enable it. Then, scroll down to the bottom of the page and click "Add New Webhook to Workspace". You should see a dropdown menu with options for channels in your workspace. Select the channel you want TRM to send messages to and click "Allow".

**Step 6:**  
You should be redirected back to the "Webhooks" page. Find the webhook you just created and copy the Webhook-URL. This is what you'll enter in the "webhook" property of a slack channel you setup in your config.json.

See the below Slack documentation if you need more help.

https://slack.com/help/articles/115005265063-Incoming-webhooks-for-Slack
https://api.slack.com/authentication/basics

## Configuration
When you deploy TRM in AWS a file named `config.json` will be created in the the S3 bucket you specified during deployment. Download that file
and open it in your preferred JSON document editor. When you're done making changes, upload it to the same location in S3.

Note: The config.json won't be created in your S3 bucket until the Lambda function runs for the first time. The Lambda function runs every 15 minutes on the quarter-hour. So if you deploy at 2:37pm your config file will be created at 2:45pm. If you want it created sooner you can manually run the Lambda function in AWS. 

### enabled
If set to `"true"` TRM will rotate Responsibilities and send notifications as configured in `config.json`. If set to `"false"` TRM will stop rotating responsibilities and won't send any notifications. When you're ready start rotating again just set it back to `"true"`.
### timezone
The config file requires the "hour" of day for certain properties. Enter the timezone that should be used when interpreting those times. Use a value from the "TZ database name" column in this list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

```json
{
  "timezone": "America/New_York"
}
```

### slack
Each responsibility in the config file requires the name of a Slack channel also  configured in the config file.

```json
"slack": {
    "channels": {
        "my_channel": {
            "webhook": "https://hooks.slack.com/services/YYYY/XXXXX"
        }
    }
}
```

In the above example `my_channel` is a unique id for the channel you'll reference in a responsibility. 

### People
Teams are made up of people. Enter a name for each person that will be sharing your responsibilities.

```json
"people": {
    "jdoe": {
        "firstName": "Jane",
        "lastName": "Doe",
        "slackUID": "UXXXXXXX"
    }
}
```

In the above example `jdoe` is a unique id you reference from a team. To find a person's `slackuid` you click on their avatar in Slack, click on "View Full Profile" then click the "More" button.

### Teams
Each responsibility requires a team. Teams are simply a list of people ids.

```json
"teams": {
    "my_team": {
        "people": [
            "jdoe"
        ]
    }
}
```

In the above example `my_team` is a unique id you reference from a responsibility.

### responsibilities

Responsibilities are what TRM keeps track of and notifies you about. The `frequency` property can be `weekly` or `weekdaily`. If you choose `weekdaily` you can omit the `day` property because it will rotate every weekday. The `hour` property is the hour of the day you want the responsibility to rotate in 24-hour time relative to your timezone. For example, if you want a responsibility to rotate at 2pm you'd enter `14`. 

```json
"responsibilities": {
    "garbage_collector": {
        "name": "Garbage Collector",
        "team": "my_team",
        "rotation": {
            "frequency": "weekly",
            "day": "monday",
            "hour": "8"
        },
        "slack_channel": "my_channel"
    }
}
```

## Example config.json


```json
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
```

# How This Serverless App Was Created

This project was built using Amazon's Serverless Application Model (SAM).

https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html

It is essentially a Python application running inside a Docker container that is deployed to an AWS Lambda function. During deployment, AWS references values specified in the Amazon SAM template to create the other resources needed by the application (see "Resources Created on AWS During Deployment" above).

I go into more detail about how the application was created and how it's used in the videos linked in the first section.