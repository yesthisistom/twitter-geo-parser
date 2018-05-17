
import os
import sys
import json
import tweepy
import argparse
import threading

import db_wrapper
import twitter_stream


def create_twitter_api(twitter_config):
    # twitter auth
    auth = tweepy.OAuthHandler(twitter_config["consumer_key"], twitter_config["consumer_secret"])
    auth.set_access_token(twitter_config["access_token"], twitter_config["access_token_secret"])
    api = tweepy.API(auth)
    return api


def run_locations(twitter_dict, mongo_dict, areas_list):

    twitter_api = create_twitter_api(twitter_dict)

    ts = []
    for area_dict in areas_list:

        collector = twitter_stream.TwitterCollector(area_dict, twitter_api, mongo_dict)
        t = threading.Thread(target=collector.run, args=())
        t.start()
        ts.append(t)

    for t in ts:
        t.join()


def validate_config(config_dict, locations):

    return True


def main(args):

    # Create parser, ensure inputs exist
    parser = argparse.ArgumentParser(description='Geospatial Twitter Parser for multiple Locations')

    required = parser.add_argument_group('required arguments')
    required.add_argument("-c", "--config", help="configuration file", default=None)
    required.add_argument("-l", "--locations", nargs="*", help="location strings", default=None)

    args = parser.parse_args()
    config = args.config
    locations = args.locations

    if config is None:
        print("No config file specified")
        parser.print_help()
        return

    if locations is None:
        print("No location strings specified")
        parser.print_help()
        return

    # Read and validate config
    if not os.path.exists(config):
        print("Unable to find configuration file")
        return

    with open(config) as file_hdl:
        config_dict = json.load(file_hdl)

    if not validate_config(config_dict, locations):
        print("Configuration not valid. Exiting")
        return

    # Start all twitter feeds
    mongo_dict = config_dict["connectors"]["mongodb"]
    twitter_dict = config_dict["connectors"]["twitter"]

    areas_list = [loc_dict for loc, loc_dict in config_dict["regions"].items() if loc in locations]
    run_locations(twitter_dict, mongo_dict, areas_list)

    print("Run complete: Exiting")


if __name__ == '__main__':
    main(sys.argv[1:])
