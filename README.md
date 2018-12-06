# VirtueTron9000


VirtueTron9000: a Reddit moderation bot for r/TheBluePill (python 3 &amp; praw &amp; also peewee/sqlite now)

JAHR NULL (upcoming plans)

All currently banned users unbanned. Custom flair for ex-cons: Kenshiro/"ALREADY DEAD" (counts as vexatious)
All currently approved users, custom flair: "JUNIOR COMMISSAR". Approved users cleared, automod rule to modqueue new posts rescinded (or maybe just set to auto-approve after 4 hours of sitting in the queue)
Custom text flairs returned
    Changed flairs overwritten every couple of minutes by bot if redditor == shitty
Rethink of link flair system
Next gen shit tests
Mob justice
VirtueTron command interface

How should next gen scoring work?

    Naive scoring
        sum(comment.score * comment.subreddit.weight)

    Should I make more recent comments count more and older comments count less?
    
    Monster raving loony scoring:
        Average score per subreddit
            Scaled by number of comments in subreddit like +20% per comment (100% at 5, 200% at 10, etc.)
            Scaled by weight of subreddit
            Split into weight bands:
                200% for comments less than 48 hours old
                100% comments 2 weeks > x > 48 hours
                75% x > 2 weeks

    The beta marketplace:
        Sort userbase by average score, cut into negative/zero/positive bands:
            negative = 1 or 2 -- ceil(position in negative band / length of negative band)
            zero = 3
            positive = 4-10 -- ceil(position in postive band / length of positive band) + 3