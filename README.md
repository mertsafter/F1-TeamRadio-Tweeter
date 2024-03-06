# F1 Team Radio Transcriber
This Python script gets the latest team radio of the current Formula 1 Session, transcribes it and than tweets it (feature later included).

# Use Case
The transcription is only done against the latest new entry, which was not already been transcribed. The use case is to run this script every x minute to check for a new entry and tweet the result. 

# How to run
Install the needed requirements using:
````
pip3 install -r requirements.txt
`````

Run the script:
````
python3 TeamRadio.py
`````
Info: If the script is run first time, the whisper library will download the model, which takes some time.

# Troubleshoot
If you have issues running whisper, check (https://github.com/openai/whisper?tab=readme-ov-file#setup) for the setup