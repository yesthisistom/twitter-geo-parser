import db_wrapper

import datetime

from collections import defaultdict
from flask import Flask, render_template


app = Flask(__name__)


def get_center(coords):
    lats, lons = map(list, zip(*coords))
    return [(min(lats) + max(lats))/2, (min(lons) + max(lons))/2]


@app.route('/location/<location_str>')
def location(location_str):

    location = db_wrapper.get_location(location_str)
    dbwrapper = db_wrapper.SocialMediaMongoWrapper('localhost', location)

    tweets = dbwrapper.get_data()
    tweet_dict = defaultdict(list)
    coords = []
    for tweet in tweets:
        del tweet['_id']
        del tweet['source']
        coord_tuple = tuple(tweet["geo"]["coordinates"])

        coords.append(coord_tuple)
        tweet["dt"] = str(datetime.datetime.fromtimestamp(int(tweet["timestamp_ms"])/1000))
        tweet_dict[coord_tuple].append(tweet)

    dbwrapper.shutdown()
    return render_template('location.html', tweets=tweet_dict, center=get_center(coords), request_box=location)


@app.route('/')
def index():
    locations = db_wrapper.get_mongodb_list()

    locations_map = {}
    for loc in locations:
        loc_dict = db_wrapper.get_location(loc)
        dbwrapper = db_wrapper.SocialMediaMongoWrapper('localhost', loc_dict)

        tweets = dbwrapper.get_data()
        locations_map[loc] = len(list(tweets))

    return render_template('index.html', locations=locations_map)


if __name__ == '__main__':
    app.run(debug=True)
