# FB Digest

Receive a (mostly) noise-free email digest containing the most recent content posted to Facebook by your friends.

Back in the day, Facebook used to be a great place to keep up with friends and family. Unfortunately, it's now a firehose of garbage. Our feeds are clogged with ads and governed by an algoritm that controls which posts we see and which we miss.

Use this script to log in, scrape recent posts from your friends' profiles and send yourself (via your mailserver of choice) an email with just the good stuff. 

## Requirements

- [chromedriver](https://pypi.org/project/chromedriver/)
- [selenium](https://pypi.org/project/selenium/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)

## Configuration

You'll need to create two files for the script to reference.

A JSON file capturing a few settings:

```
{
    "facebookUsername" : "[VALUE]",
    "facebookPassword" : "[VALUE]",
    "senderEmailAddress" : "[VALUE]",
    "recipientEmailAddress" : "[VALUE]",
    "mailserverHost" : "[VALUE]",
    "mailserverPort" : "[VALUE]",
    "mailserverUsername" : "[VALUE]",
    "mailserverPassword" : "[VALUE]"
}
```

And a two-column CSV file identifying the profiles you'll be tracking (Friend Facebook ID, Friend Name):

```
emmett.fitz-hume,Emmett Fitz-Hume
amillbarge.3,Austin Millbarge
pierre.lemonjello.1,Pierre Lemonjello
...
```

Sure, it would be convenient to automatically pull in all of your friends from your profile, but do you really care about _all_ of them? 

#### Additional Notes

The script is configured with a number of personal preferences that should to tuned. It's written to be run weekly, and to examine only the last three posts on each friend's profile. It filters out posts that weren't created by the friend (ie. mentions don't count) and posts that includes a link without commentary (since those are often less meaningful). Filtering out posts that contain certain keywords could also be useful.

Parsing is configured to work with the Classic Facebook UI -- it does not yet support the new UI.

## Usage

```python3 suckerberg.py -config configuration.json -friends friends.csv```

Cron it up, then sit back and enjoy all the smugness of [#DeleteFacebook](https://knowyourmeme.com/memes/events/deletefacebook) without the [FOMO](https://www.urbandictionary.com/define.php?term=Fomo).

