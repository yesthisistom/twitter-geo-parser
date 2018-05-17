__author__ = 'tv'

import tweepy
import db_wrapper


class TwitterStream(tweepy.StreamListener):

    def __init__(self, api, dbwrapper, strict=True):
        self.api = api
        super(tweepy.StreamListener, self).__init__()

        self.dbwrapper = dbwrapper
        self.strict_boundary = self.dbwrapper.get_location() if strict else None

    def _coord_in_box(self, coord):
        if self.strict_boundary:
            if coord[0] < self.strict_boundary["latmin"] or coord[0] > self.strict_boundary["latmax"]:
                return False
            if coord[1] < self.strict_boundary["lonmin"] or coord[1] > self.strict_boundary["lonmax"]:
                return False

        return True

    def on_status(self, status):
        tweet_json = status if type(status) == dict else status._json

        # If the tweet has a coordinate and the coordinate is inside our bounding box (if strict)
        if tweet_json['coordinates'] and self._coord_in_box(tweet_json["geo"]["coordinates"]):
            tweet_json["tweet_url"] = "https://twitter.com/" + str(tweet_json["user"]["id"]) \
                                      + "/status/" + str(tweet_json["id"])
            self.dbwrapper.add_data(tweet_json)


    def on_error(self, status_code):
        print('Encountered error with status code:', status_code)
        return True  # Don't kill the stream

    def on_timeout(self):
        print("Timeout...")
        return True  # Don't kill the stream


class TwitterCollector:

    def __init__(self, location_dict, twitter_api, mongo_params):
        self.exporter = db_wrapper.SocialMediaMongoWrapper(mongo_params["host"],
                                                           location_dict, port=mongo_params["port"])

        self.location_dict = location_dict

        self.location_box = []
        self.location_box.extend([location_dict["lonmin"], location_dict["latmin"]])
        self.location_box.extend([location_dict["lonmax"], location_dict["latmax"]])

        self.twitter_api = twitter_api

    def run(self):
        print("Starting run for area", self.location_dict["name"])

        try:
            stream_listener = TwitterStream(self.twitter_api, self.exporter)
            sapi = tweepy.Stream(auth=self.twitter_api.auth, listener=stream_listener)
            sapi.filter(locations=self.location_box, async=False)
        except Exception as e:
            print("Exception caught in TwitterCollector's run function. ")
            print(e)

        print("Ending run for area", self.location_dict["name"])


