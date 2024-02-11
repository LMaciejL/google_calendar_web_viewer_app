from flask import Flask, render_template, jsonify
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = 'auth/credentials.json'
TOKEN_FILE = 'auth/token.json'

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds
    
def datetime_to_hour(datetime_str):
    dt_object = datetime.fromisoformat(datetime_str)
    return dt_object.strftime('%H:%M')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/today_meetings')
def api_today_meetings():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.utcnow().isoformat() + 'Z'
    today_end = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=today_end,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        return jsonify({'meetings': []})
    for event in events:
        print(event['end'])
        startTime_datetime = event['start'].get('dateTime', event['start'].get('date'))
        startTime_hourMinute = datetime_to_hour(startTime_datetime)
        event['start'] = startTime_hourMinute
        endTime_datetime = event['end'].get('dateTime', event['end'].get('date'))
        endTime_hourMinute = datetime_to_hour(endTime_datetime)
        event['end'] = endTime_hourMinute
        
    meetings = [{'title': event['summary'], 'timeStart': event['start'], 'timeEnd': event['end']}
                for event in events]
                
    return jsonify({'meetings': meetings})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
