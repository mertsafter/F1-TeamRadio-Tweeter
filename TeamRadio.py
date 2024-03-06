import json
import requests
import whisper
import sqlite3
import logging

# Define logging format
logging.basicConfig(format='[%(asctime)s] - %(levelname)s:\t%(message)s', level=logging.INFO)

# Initialise needed Database table
def initDatabase():
    con = sqlite3.connect("f1radio.db")
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS TeamRadio (id INTEGER PRIMARY KEY AUTOINCREMENT,racing_number INTEGER,timestamp DATETIME, path char)')

# Save racing number, timestamp and path into the db to check which team radio has to be tweeted next
def saveLatestEntry(racing_number, timestamp, path):
    con = sqlite3.connect("f1radio.db")
    cur = con.cursor()
    cur.execute('INSERT INTO TeamRadio(racing_number, timestamp, path) VALUES (?, ?, ?)',
                (racing_number, timestamp, path))
    con.commit()


def getLatestEntry():
    con = sqlite3.connect("f1radio.db")
    cur = con.cursor()
    return cur.execute('SELECT * FROM TeamRadio order by id desc limit 1').fetchone()


# Gets the current session info and checks the team radio for a new entry and tweets it
def tweetNextTeamRadio(model):
    logging.info("Starting Team radio check and transcription...")
    
    # Get the latest Session Info of the F1 Session (Race, Quali, Training)
    
    response = requests.get('https://livetiming.formula1.com/static/SessionInfo.json')
    if response.status_code == 200:
        source = response.content
        sessionInfo = json.loads(source)
        
        logging.info("Session Info successfully retrieved! " + sessionInfo['Meeting']['OfficialName'])

        teamRadiosUrl = "https://livetiming.formula1.com/static/" + \
            sessionInfo['Path'] + "TeamRadio.json"
        
        teamRadioResponse = requests.get(teamRadiosUrl)
        teamRadioResponse.encoding = 'utf-8-sig'

        teamRadioContent = json.loads(teamRadioResponse.text)
        
        # Get the latest saved entry to check where to continue
        latest_entry = getLatestEntry()

        # Set the lastTweet to the latest entry if any otherwise to None
        if latest_entry is not None and len(latest_entry) >= 4:
            lastPath = latest_entry[3]
        else:
            lastPath = None
            
        # Helper variable to determine when to tweet the next entry of the TeamRadioContent
        next = False
        
        for currentTeamRadio in teamRadioContent['Captures']:
            if lastPath is None or next:
                # Prepare whipser model only if tweet will be posted
                model = whisper.load_model(model)
                
                # Get the url to the mp3 of the current team radio entry by the data path
                currentTeamRadioUrl = "https://livetiming.formula1.com/static/" + sessionInfo['Path'] + currentTeamRadio['Path']
                
                # Start the transcription using whisper's model
                result = model.transcribe(currentTeamRadioUrl, fp16=False)
                
                # Tweet
                # TODO: Include the https://www.tweepy.org/ library for doing the real tweet on X previously twitter
                logging.info("Tweet: " + currentTeamRadio['RacingNumber'] + ": " + result["text"])
                saveLatestEntry(currentTeamRadio['RacingNumber'], currentTeamRadio['Utc'], currentTeamRadio['Path'])
                break

            # Check if the lastPath has the same Path as the current entry to determine that the next entry should tweet the transcribtion 
            if lastPath == currentTeamRadio['Path']:
                next = True
                continue
    else:
        logging.error('Error occurred retrieving Session Info!', response.status_code)


initDatabase()
# Supported models see https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages
tweetNextTeamRadio("medium.en")
