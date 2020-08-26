import argparse
import os
import time
import json
import csv
import emails
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as parser

# Pull in configuration details (see README.md for format)
with open('../secrets/fb-digest-secrets.json') as file:
    data = json.load(file)
    FACEBOOK_USERNAME = data["secrets"]["facebookUsername"]
    FACEBOOK_PASSWORD = data["secrets"]["facebookPassword"]
    EMAIL_FROM_ADDRESS = data["secrets"]["senderEmailAddress"]
    EMAIL_TO_ADDRESS = data["secrets"]["recipientEmailAddress"]
    EMAIL_HOST = data["secrets"]["mailserverHost"]
    EMAIL_PORT = data["secrets"]["mailserverPort"]
    EMAIL_USERNAME = data["secrets"]["mailserverUsername"]
    EMAIL_PASSWORD = data["secrets"]["mailserverPassword"]


def _extract_post_text(item):
    actualPosts = item.find_all(attrs = {"data-testid": "post_message"})
    text = ""
    if actualPosts:
        for posts in actualPosts:
            paragraphs = posts.find_all('p')
            text = ""
            for index in range(0, len(paragraphs)):
                text += paragraphs[index].text
    return text


def _extract_poster(item):
    poster = None
    postTitle = item.find("h5")
    if postTitle is None:
        postTitle = item.find("h6")
    if not postTitle is None:
        posterLink = postTitle.find("a")
        if not posterLink is None:
            poster = posterLink.get("title")
            if poster is None:
                poster = posterLink.getText()
    return poster


def _extract_date(item):
    postIds = item.find_all(class_ = "_5pcq")
    timestamp = postIds[0].find('abbr').get('data-utime')
    return timestamp


# Original Poster (for items that were re-shared)
def _extract_op(item):
    attribution = item.find_all(class_ = "_5pcm")
    op = ""
    for link in attribution:
        op = link.find('a').getText()
    return op


def _extract_link(item):
    postLinks = item.find_all(class_ = "_6ks")
    link = ""
    for postLink in postLinks:
        link = postLink.find('a').get('href')
    return link


def _extract_post_id(item):
    postIds = item.find_all(class_="_5pcq")
    post_id = ""
    for postId in postIds:
        if ("http" in postId.get('href')):
            post_id = postId.get('href')
        else:
            post_id = f"https://www.facebook.com{postId.get('href')}"
        break
    return post_id


def _extract_image(item):
    postPictures = item.find_all(class_ = "scaledImageFitWidth img")
    if len(postPictures) <= 0:
        postPictures = item.find_all(class_ = "_46-i img")
    image = ""
    for postPicture in postPictures:
        image = postPicture.get('src')
    return image


def _extract_html(raw_data):

    with open('./raw.html',"w", encoding = "utf-8") as file:
        file.write(str(raw_data.prettify()))

    k = raw_data.find_all(class_ = "_5pcr userContentWrapper")
    posts = list()

    for item in k:
        post = dict()
        post['Poster'] = _extract_poster(item)
        post['OriginalPoster'] = _extract_op(item)
        post['Post'] = _extract_post_text(item)
        post['Date'] = _extract_date(item)
        post['Link'] = _extract_link(item)
        post['PostId'] = _extract_post_id(item)
        post['Image'] = _extract_image(item)

        posts.append(post)
        with open('./posts.json','w', encoding = 'utf-8') as file:
            file.write(json.dumps(posts, ensure_ascii = False).encode('utf-8').decode())

    return posts


def _login(browser, email, password):
    browser.get("http://facebook.com")
    browser.maximize_window()
    browser.find_element_by_name("email").send_keys(email)
    browser.find_element_by_name("pass").send_keys(password)
    browser.find_element_by_name('login').click()
    time.sleep(5)


def _count_needed_scrolls(browser, infiniteScroll, numOfPost):
    if infiniteScroll:
        lenOfPage = browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;"
        )
    else:
        # Roughly 8 post per scroll
        lenOfPage = int(numOfPost / 8)
    return lenOfPage


def _scroll(browser, infiniteScroll, lenOfPage):
    lastCount = -1
    match = False

    while not match:
        if infiniteScroll:
            lastCount = lenOfPage
        else:
            lastCount += 1

        # Wait for the browser to load
        time.sleep(5)

        if infiniteScroll:
            lenOfPage = browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")
        else:
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")

        if lastCount == lenOfPage:
            match = True


def writeJSON(posts, outputFile):
    with open(outputFile, 'w') as file:
        for post in posts:
            file.write(json.dumps(post))


def extract(browser, page, numOfPost):

    browser.get(page)

    lenOfPage = _count_needed_scrolls(browser, False, numOfPost)
    _scroll(browser, False, lenOfPage)

    # Now that the page is fully scrolled, grab the source code
    source_data = browser.page_source

    # Throw source into BeautifulSoup and start parsing
    raw_data = parser(source_data, 'html.parser')
    posts = _extract_html(raw_data)

    return posts


if __name__ == "__main__":

    print("--------------------------------------------")
    print("Pulling recent friend activity from Facebook")
    print("--------------------------------------------")

    option = Options()
    option.add_argument('headless')
    option.add_argument("start-maximized")
    option.add_argument("--disable-infobars")
    option.add_argument("--disable-extensions")
    option.add_argument("--disable-gpu")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    browser = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", options = option)

    print("Logging In...")

    _login(browser, FACEBOOK_USERNAME, FACEBOOK_PASSWORD)

    print("Scraping...")

    content = "<h1>Posts from Friends</h1>"

    with open('../secrets/fb-digest/friends.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter = ',')
        for row in readCSV:

            friendId = row[0]
            friendName = row[1]

            posts = extract(browser, page="https://www.facebook.com/" + friendId, numOfPost = 3)
            if not os.path.exists("output"):
                os.makedirs("output")

            for i in range(len(posts)):
                poster = posts[i]['Poster']
                originalPoster = posts[i]['OriginalPoster']
                post = posts[i]['Post']
                linkURL = posts[i]['Link']
                postURL = posts[i]['PostId']
                imageURL = posts[i]['Image']
                date = posts[i]['Date']

                # We only want content they've:
                # 1. posted themself
                # 2. posted this week
                # 3. posted with a comment or without a shared link

                postTime = float(date)
                currentTime = time.time()
                prettyTime = time.ctime(postTime)
                secondsInAWeek = 604800
                isRecent = (currentTime - postTime <= secondsInAWeek)

                isSelfPosted = (friendName == poster)
                hasOP = ((not originalPoster is None) & (originalPoster != ''))
                hasPostContent = ((not post is None) & (post != ''))
                hasLink = ((not linkURL is None) & (linkURL != ''))
                hasImage = ((not imageURL is None) & (imageURL != ''))
                hasElligiblePost = False

                if (isSelfPosted & isRecent & (hasPostContent | ((not hasLink) & (not hasOP)))):

                    content += "<p>"
                    content += "<h3>" + friendName + "</h3 style='margin-bottom: 0;'> (" + prettyTime + ")<br>"
                    if hasPostContent:
                        content += post + "<br>"
                    if hasImage:
                        content += "<img src='" + imageURL + "' style='width: 100%; max-width: 480px; margin-top: 10px;'><br>"
                    content += "<a href='" + postURL + "'>View Post</a>"
                    if hasLink:
                        content += " | <a href='" + linkURL + "'>Shared Link</a>"
                    content += "</p>"

                    print("- Recent post from: " + friendName + " - " + prettyTime + " - " + post)
                    hasElligiblePost = True
                    break

            if not hasElligiblePost:
                print("- No recent posts from: " + friendName)

            # Keep a copy for reference
            writeJSON(posts, "output/posts-" + friendId + ".json")

            # Keep them guessing...
            time.sleep(random.randint(5,30))

    content += "<p>That's all, folks!</p>"

    browser.close()

    print("Sending Email...")

    message = emails.html(
        html = content,
        subject = "Facebook Updates",
        mail_from = ("Suckerberg", EMAIL_FROM_ADDRESS),
    )

    message.send(
        to = EMAIL_TO_ADDRESS,
        smtp = {
            "host": EMAIL_HOST,
            "port": EMAIL_PORT,
            "timeout": 5,
            "user": EMAIL_USERNAME,
            "password": EMAIL_PASSWORD,
            "tls": True,
        },
    )

    print("Finished!")