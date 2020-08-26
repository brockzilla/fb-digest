# FB Digest

Receive an email digest containing content posted by friends to Facebook.

Back in the day, Facebook used to be a great place to keep up with friends and family. Unfortunately, it's now a firehose of garbage. Our feeds are clogged with ads and governed by an algoritm that controls which posts we see and which we miss.

Use this script to log in, scrape recent posts from your friends' profiles and send you (via your mailserver of choice) an email with just the good stuff.

## Requirements

You'll need to install:

- chrome
- chromedriver
- selenium
- beautifulsoup4

## Configuration

You'll need to create and tweak the script to reference your configuration secrets via a JSON file: `fb-digest-secrets.json`:

```
{
    "secrets" : {
        "facebookUsername" : "[VALUE]",
        "facebookPassword" : "[VALUE]",
        "senderEmailAddress" : "[VALUE]",
        "recipientEmailAddress" : "[VALUE]",
        "mailserverHost" : "[VALUE]",
        "mailserverPort" : "[VALUE]",
        "mailserverUsername" : "[VALUE]",
        "mailserverPassword" : "[VALUE]"
    }
}
```

Then, you'll need to create and reference a two-column CSV file identifying the profiles you'll be tracking: `friends.csv`

```
emmett.fitz-hume,Emmett Fitz-Hume
amillbarge.3,Austin Millbarge
pierre.lemonjello.1,Pierre Lemonjello
...
```

#### Additional Notes

The script is configured with a number of personal preferences that should to tuned. It's written to be run weekly, and to examine only the last three posts on each friend's profile. It filters out:

- Content that wasn't posted by the friend (ie. mentions don't count)
- Content that includes a link without commentary


## Usage

```python3 suckerberg.py```