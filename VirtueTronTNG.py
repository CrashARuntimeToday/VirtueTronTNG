#!/usr/bin/env python3
LICENSE = "WTFPL", "http://www.wtfpl.net/about"
VERSION = "TNG.test5"
DATABASE = "VirtueBrain.sqlite"
LOGFILE = "VirtueLog.txt"

import logging
import pickle
import praw
import prawcore
import sys

from datetime import datetime, timedelta
from math import ceil
from peewee import SqliteDatabase, Model, BooleanField, CharField, FloatField, ForeignKeyField, IntegerField, TextField, TimestampField
from time import sleep

CREDENTIALS = pickle.load(open("credentials.pickle", "rb")) # { client_id: "VirtueTron9000",
                                                            #   client_secret: "🤖🤡🍆💯™", 
                                                            #   username: "SignalAVirtueToday",
                                                            #   password: "https://youtu.be/RCVJ7bujnSc" }
CREDENTIALS["user_agent"] = f"VirtueTron 9000 {VERSION}"

# Set up logging
log = logging.getLogger("VirtueTron")
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y/%m/%d %I:%M:%S%p")
file_log = logging.FileHandler(filename=LOGFILE, mode="a")
file_log.setLevel(logging.INFO)
file_log.setFormatter(formatter)
log.addHandler(file_log)
console_log = logging.StreamHandler(stream=sys.stdout)
console_log.setLevel(logging.DEBUG)
console_log.setFormatter(formatter)
log.addHandler(console_log)
log.info(f"VirtueTron® 9000™ {VERSION} © CrashARuntimeToday@outlook.com")

# Set up database
db = SqliteDatabase(DATABASE)
class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    name = CharField(unique=True)
    last_seen = TimestampField(null=True)
    next_probe = TimestampField(null=True)
    ignore = BooleanField(default=False)

class Subreddit(BaseModel):
    name = CharField(unique=True)
    flair = CharField(default="")
    weight = FloatField(default=0)

class Submission(BaseModel):
    rid = CharField(unique=True)
    redditor  = ForeignKeyField(User, backref="submissions", null=True)
    score = IntegerField()
    subreddit = ForeignKeyField(Subreddit, backref="submissions")
    timestamp = TimestampField()

class Comment(BaseModel):
    rid = CharField(unique=True)
    sub_rid = ForeignKeyField(Submission, backref="comments")
    redditor = ForeignKeyField(User, backref="comments", null=True)
    score = IntegerField()                              
    subreddit = ForeignKeyField(Subreddit, backref="comments")
    timestamp = TimestampField()


class _VirtueTron:
    QUICKSCAN_INTERVAL = timedelta(minutes=15)
    QUICKSCAN_DEPTH = timedelta(hours=2)
    MEDSCAN_INTERVAL = timedelta(minutes=60)
    MEDSCAN_DEPTH = timedelta(hours=4)
    LONGSCAN_INTERVAL = timedelta(days=1)
    LONGSCAN_DEPTH = timedelta(days=2)
    DEEPSCAN_INTERVAL = timedelta(days=3)
    DEEPSCAN_DEPTH = timedelta(days=7)
    PROBE_INTERVAL = timedelta(days=7)
    PROBE_DEPTH = 250
    
    def __init__(self, credentials):
        self._reddit = praw.Reddit(**credentials)
        self._tbp = self._reddit.subreddit("TheBluePill")
        self.next_deepscan = datetime.now() + self.DEEPSCAN_INTERVAL
        self.next_longscan = datetime.now() + self.LONGSCAN_INTERVAL
        self.next_medscan = datetime.now() + self.MEDSCAN_INTERVAL
        self.next_quickscan = datetime.now() + self.QUICKSCAN_INTERVAL
    
    def archive_shitpost(self, shitpost):
        if Comment.get_or_none(rid=shitpost.id):
            log.debug(f"Not archiving comment '{shitpost.id}' -- already archived.'")
            return False

        if shitpost.author:
            user, created = User.get_or_create(name=shitpost.author.name)
            if created:
                log.info(f"New user: '{shitpost.author.name}'")
        else:
            log.debug(f"Comment (id: {shitpost.id} on submission '{shitpost.submission.title}' is orphaned.")
            user = None

        subreddit, created = Subreddit.get_or_create(name=shitpost.subreddit.display_name)
        if created:
            log.debug(f"New subreddit: '{shitpost.subreddit.display_name}'")
    
        if shitpost.submission.author:
            op, created = User.get_or_create(name=shitpost.submission.author)
            if created:
                log.info(f"New OP: '{shitpost.submission.author}'")
        else:
            log.debug(f"Submission '{shitpost.submission.title}' (id: {shitpost.submission.id}) is orphaned.")
            op = None

        submission = Submission.get_or_none(rid=shitpost.submission.id)
        if submission is None:
            submission = Submission.create(rid=shitpost.submission.id, redditor=op, subreddit=subreddit, score=shitpost.submission.score - 1, timestamp=shitpost.submission.created_utc)
            log.debug(f"New submission: '{shitpost.submission.title}' by '{shitpost.submission.author}' in '{shitpost.submission.subreddit.display_name}' (id: '{shitpost.submission.id}')")            
 
        Comment.create(rid=shitpost.id, sub_rid=submission, redditor=user, subreddit=subreddit, score=shitpost.score - 1, timestamp=shitpost.created_utc)
        log.debug(f"New comment by '{shitpost.author}' (id: {shitpost.id}) on submission '{shitpost.submission.title}' in subreddit '{shitpost.subreddit.display_name}' (id: '{shitpost.submission.id}')")
        return True
    
    def refresh_score(self):
        mark = datetime.now()
        if datetime.now() > self.next_deepscan:
            depth = self.DEEPSCAN_DEPTH
            self.next_deepscan = datetime.now() + self.DEEPSCAN_INTERVAL
            self.next_longscan = datetime.now() + self.LONGSCAN_INTERVAL
            self.next_medscan = datetime.now() + self.MEDSCAN_INTERVAL
            self.next_quickscan = datetime.now() + self.QUICKSCAN_INTERVAL
        elif datetime.now() > self.next_longscan:
            depth = self.LONGSCAN_DEPTH
            self.next_longscan = datetime.now() + self.LONGSCAN_INTERVAL
            self.next_medscan = datetime.now() + self.MEDSCAN_INTERVAL
            self.next_quickscan = datetime.now() + self.QUICKSCAN_INTERVAL
        elif datetime.now() > self.next_medscan:
            depth = self.MEDSCAN_DEPTH
            self.next_medscan = datetime.now() + self.MEDSCAN_INTERVAL
            self.next_quickscan = datetime.now() + self.QUICKSCAN_INTERVAL
        else:
            depth = self.QUICKSCAN_DEPTH
            self.next_quickscan = datetime.now() + self.QUICKSCAN_INTERVAL

        log.info(f"Refreshing comment scores (maximum depth is: {depth}).")
        shitheap = Comment.select().where(Comment.timestamp > (datetime.now() - depth)).join(User)
        for shitpost in shitheap:
            new_score = self._reddit.comment(id=shitpost.rid).score - 1
            if new_score == shitpost.score:
                log.debug(f"Comment by '{shitpost.redditor.name}' (id: {shitpost.rid}) hasn't changed, still {shitpost.score}.")
            else:
                log.debug(f"Comment by '{shitpost.redditor.name}' (id: {shitpost.rid}) changed from {shitpost.score} to {new_score}.")
                shitpost.score = new_score
                shitpost.save()
        log.info(f"{len(shitheap)} comments refreshed in {datetime.now() - mark}.")
    
    def probe_redditor(self, redditor):
        mark = datetime.now()
        archived = 0
        for comment in self._reddit.redditor(redditor.name).comments.new(limit=self.PROBE_DEPTH):
            if self.archive_shitpost(comment):
                archived += 1
        try:
            log.info(f"Archived {archived}/{self.PROBE_DEPTH} comments from '{redditor.name}' in {datetime.now() - mark}, next probe due on {(redditor.last_seen + self.PROBE_INTERVAL):%Y/%m/%d %I:%M:%S%p}.")
        except TypeError:
            log.info(f"Archived {archived}/{self.PROBE_DEPTH} comments from '{redditor.name}' in {datetime.now() - mark}, next probe due on {(datetime.now() + self.PROBE_INTERVAL):%Y/%m/%d %I:%M:%S%p}.")

    def masstag_redditor(self, redditor):
        shitheap = list(redditor.comments.select().join(Subreddit).where(Subreddit.flair != "", Subreddit.flair != None))
        shitheap += list(redditor.submissions.select().join(Subreddit).where(Subreddit.flair != "", Subreddit.flair != None))
        tally = {}
        for shitpost in shitheap:
            assert shitpost.subreddit.weight != 0
            try:
                tally[shitpost.subreddit.flair] += 1
            except KeyError:
                tally[shitpost.subreddit.flair] = 1

        log.debug(f"Results from {len(shitheap)} posts by '{redditor.name}':")
        for flair in tally.keys():
            log.debug(f"{flair} -- count: {tally[flair]}")
    
    def subscore_redditor(self, redditor, subreddit):
        FRESH_THRESHOLD = timedelta(days=2)
        FRESH_WEIGHT = 2.0
        OKAY_THRESHOLD = timedelta(days=7)
        OKAY_WEIGHT = 1.0
        STALE_THRESHOLD = timedelta(days=14)
        STALE_WEIGHT = 0.75
        SUBMISSION_WEIGHT = 1.25
        score = 0
        shitheap = redditor.comments.select().join(Subreddit).where(Subreddit == subreddit, Comment.score != 0, Comment.timestamp > datetime.now() + FRESH_THRESHOLD)
        for shitpost in shitheap:
            score += shitpost.score * FRESH_WEIGHT
        fresh_posts = len(shitheap)
        shitheap = redditor.comments.select().join(Subreddit).where(Subreddit == subreddit, Comment.score != 0, Comment.timestamp > datetime.now() + FRESH_THRESHOLD)
    
        log.debug(f"Tallied {len(shitheap)} comments by '{redditor.name}', score is {score}.")

    def loop(self):
        try:
            for shitpost in self._tbp.stream.comments():
                if datetime.now() > self.next_quickscan:
                    self.refresh_score()
                #if Comment.get_or_none(rid=shitpost.id) is None: # Skip over already seen comments
                self.archive_shitpost(shitpost)
                if shitpost.author: # Skip orphaned comments
                    redditor = User.get_or_none(name=shitpost.author)
                    if redditor is not None:
                        if redditor.name == "SnapshillBot":
                            redditor.ignore = True
                        else:
                            redditor.ignore = False
                            
                        if redditor.next_probe is None or datetime.now() > redditor.next_probe + self.PROBE_INTERVAL:
                            log.info(f"Probing '{shitpost.author}'")
                            self.probe_redditor(redditor)
                            redditor.next_probe = datetime.now() + self.PROBE_INTERVAL
                        self.masstag_redditor(redditor)
                        redditor.last_seen = datetime.now()
                        redditor.save()

 #               else:
 #                   log.debug(f"Skipping comment: {shitpost.id} by '{shitpost.author}' -- already seen'")

        except prawcore.PrawcoreException:
            log.warn(":( Something Went Wrong™")
            return False

VirtueTron = _VirtueTron(CREDENTIALS)

while True:
    try:
        if not VirtueTron.loop():
            sleep(5)
    except KeyboardInterrupt:
        break
    finally:
        log.info("Shutting down.")
