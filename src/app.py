import boto3
import json
import requests
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict
import logging
import pprint
import ConfigTemplate

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
DEFAULT_TIMEZONE = 'America/New_York'
SLACK_HEADERS = {'Content-type': 'application/json'}
BUCKET_NAME = os.getenv('BUCKET_NAME')
BUCKET_CONFIG_FILENAME = 'config.json'
BUCKET_STATE_FILENAME = 'state.json'

# Globals
s3 = boto3.resource("s3")
trmb = s3.Bucket(BUCKET_NAME)

def log_obj(label, obj):
    logger.info(f"{label}:\n{pprint.pformat(obj, indent=4)}\n")

def file_exists(filename):
    file_objs = trmb.objects.filter(Prefix=filename)
    filenames = [obj.key for obj in file_objs]
    return filename in filenames

def get_or_create_file(filename, default_data):
    if not file_exists(filename):
        upload_file(default_data, filename)
        return default_data
    s3_file_obj = s3.Object(BUCKET_NAME, filename)
    file_contents = s3_file_obj.get()['Body'].read().decode('utf-8')
    return file_contents

def upload_file(data, filename):
    local_path = '/tmp/' + filename
    with open(local_path, 'w+') as f_empty:
        f_empty.write(data)
    with open(local_path, 'rb') as f_binary:
        f_s3 = trmb.Object(filename)
        f_s3.upload_fileobj(f_binary)

def response_factory(code, message):
    response = {
        "statusCode": code,
        "body": json.dumps(
            {
                "message": message,
            }
        ),
    }
    return response

def handle_responsibilities(state, config):
    update_state = False
    for resp_key,resp in config['responsibilities'].items():
        log_obj('Checking responsibility:', resp)
        timezone = config.get('timezone', DEFAULT_TIMEZONE)
        if should_rotate(state, config, resp_key, timezone):
            next_person = rotate(resp_key, state, config, timezone)
            logger.info(f"Rotating {resp['name'].lower()} to {next_person}")
            notify(next_person, resp, config)
            update_state = True
    return update_state

def should_rotate(state, config, resp_key, timezone):
    resp = config['responsibilities'][resp_key]
    last_rotation_str = state['responsibilities'][resp_key].get('last_rotation', None)
    if not last_rotation_str:
        return True
    current_time = datetime.now(tz=ZoneInfo(timezone))
    last_rotation = datetime.fromisoformat(last_rotation_str)
    log_obj('Execution time:', current_time)
    log_obj('Rotation frequency:', resp['rotation']['frequency'])
    if resp['rotation']['frequency'] == 'weekdaily':
        if current_time - last_rotation > timedelta(days=1):
            log_obj('Weekday number:', current_time.weekday())
            if current_time.weekday() < 5:
                log_obj('Current day is a weekday:', 'True')
                log_obj('Rotation hour', resp['rotation'].get('hour', '9'))
                log_obj('Current hour', current_time.hour)
                if str(current_time.hour) == resp['rotation'].get('hour', '9'):
                    log_obj('Current hour equals rotation hour:', 'True')
                    return True
    elif resp['rotation']['frequency'] == 'weekly':
        if current_time - last_rotation > timedelta(days=1):
            if current_time.strftime('%A').lower() == resp['rotation'].get('day', 'monday').lower():
                if str(current_time.hour) == resp['rotation'].get('hour', '9'):
                    return True
    else:
        return False

def rotate(resp_key, state, config, timezone):
    resp = config['responsibilities'][resp_key]
    team_name = resp['team']
    team_people = config['teams'][team_name]['people']
    team_order = {person:order for person,order in zip(team_people, range(len(team_people)))}
    current_person = state['responsibilities'][resp_key].get('person', None)
    current_person_i = team_order.get(current_person, None)
    log_obj('Current person index', current_person_i)
    next_person_i = current_person_i + 1 if current_person_i and current_person_i < len(team_people) - 1 else 0
    log_obj('Next person index', next_person_i)
    next_person = team_people[next_person_i]
    state['responsibilities'][resp_key]['person'] = next_person
    current_time = datetime.now(tz=ZoneInfo(timezone))
    state['responsibilities'][resp_key]['last_rotation'] = current_time.isoformat()
    return next_person

def notify(person, resp, config):
    slack_channel = resp['slack_channel']
    slack_webhook = config['slack']['channels'][slack_channel]['webhook']
    person = config['people'][person]
    if resp['rotation']['frequency'] == 'weekdaily':
        time_period = 'today'
    elif resp['rotation']['frequency'] == 'weekly':
        time_period = 'this week'
    requests.post(
        slack_webhook,
        headers=SLACK_HEADERS,
        json={
            'text': f"Hey <@{person['slackUID']}>! You're the {resp['name'].lower()} {time_period}."}
    )

def nested_default_dict(existing=None, **kwargs):
    if existing is None:
        existing = defaultdict()
    if isinstance(existing, list):
        existing = [nested_default_dict(val) for val in existing]
    if not isinstance(existing, dict):
        return existing
    existing = {key: nested_default_dict(val) for key, val in existing.items()}
    return defaultdict(nested_default_dict, existing, **kwargs)

def lambda_handler(event, context):
    # Get the config
    config_file = get_or_create_file(BUCKET_CONFIG_FILENAME, ConfigTemplate.body)
    config = nested_default_dict(json.loads(config_file))
    if config.get('enabled', 'false') != 'true':
        msg = (
            'Team Responsibility Manager is disabled. '
            'To enable, set the "enabled" property to '
            '"true" in your config.json file.'
            )
        log_obj('Application disabled', msg)
        return response_factory(200, msg)
    # Get the state
    state_file = get_or_create_file(BUCKET_STATE_FILENAME, json.dumps({}))
    state = nested_default_dict(json.loads(state_file))
    log_obj('Pre-execution state:', state)
    update_state = handle_responsibilities(state, config)
    if update_state:
        upload_file(json.dumps(state), BUCKET_STATE_FILENAME)
    log_obj('Post-execution state:', state)
    return response_factory(200, 'success')
