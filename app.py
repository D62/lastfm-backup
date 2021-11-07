import json
import os
import requests
import time
from IPython.core.display import clear_output

def lastfm_get(payload):

    # define headers and URL
    headers = {"user-agent": "test"}
    url = "https://ws.audioscrobbler.com/2.0/"

    response = requests.get(url, headers=headers, params=payload)
    return response

if __name__ == "__main__":

    # get API key and username from config file if exists
    if os.path.exists("config.json"):
        with open("config.json") as f:
            config = json.loads(f.read())
            api_key = config["api_key"]
            username = config["username"]

    # create config file if does not exist
    else:
        api_key = input("API Key: ")
        username = input("Username: ")
        config = {"api_key": api_key, "username": username}

        with open("config.json", "w") as f:
            json.dump(config, f)

    responses = []
    page = 1
    total_pages = 99999 # dummy number so the loop starts

    while page <= total_pages:

        # add API key and format to the payload
        payload = {
            "method": "user.getRecentTracks",
            "api_key": api_key,
            "user": username,
            "format": "json",
            "limit": 500,
            "page": page
        }

        # print some output so we can see the status
        print("Requesting page {}/{}".format(page, total_pages))

        # clear the output to make things neater
        clear_output(wait = True)

        # make the API call
        response = lastfm_get(payload)

        # if we get an error, print the response and halt the loop
        if response.status_code != 200:
            print(response.text)
            break

        # extract pagination info
        page = int(response.json()["recenttracks"]["@attr"]["page"])
        total_pages = int(response.json()["recenttracks"]["@attr"]["totalPages"])

        # append response
        responses.append(response)

        # if it is not a cached result, sleep
        if not getattr(response, "from_cache", False):
            time.sleep(0.25)

        # increment the page number
        page += 1

    df = [json.loads(r.content.decode("utf-8")) for r in responses]

    # write scrobble history in a json file
    with open("%s.json" % (username), "w", encoding="utf-8") as f:
        data = json.dumps(df, indent=4, sort_keys=True, ensure_ascii=False)
        f.write(data)