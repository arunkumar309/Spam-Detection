from tweetsSample import content
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
import nltk
import unicodedata
import string
import re
punctuations = string.punctuation
tt = TweetTokenizer()
def toString(unicodeData):
	stringOut = unicodedata.normalize('NFKD',unicodeData).encode('ascii','ignore')
	return stringOut

def getUniqueWords(tweets):
	tweetsUniqueString = ''
	for tweet in tweets:
		urls = re.findall(urlRegex,tweet)
		hashtags = re.findall(hashtagRegex, tweet)
		replies = re.findall(replyRegex, tweet)
		retweets = re.search(r'(RT|retweet|from|via)(?:\b\W*@(\w+))+', tweet)
		if isinstance(retweets, tuple):
			retweets = retweets.groups()
		else:
			retweets = []
		tweetWords = []
		tweetSplit = tweet.split()
		tweetWords = list(set(tweetSplit))
		temp = ' '.join(word.lower() for word in tweetWords if word not in urls and word not in hashtags and word not in replies and word not in retweets)
		temp = ''.join(ch for ch in temp if ch not in punctuations)
		tweetsUniqueString += temp
		tweetsUniqueString += ' '
	return tweetsUniqueString

urlRegex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
replyRegex = '(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)'
hashtagRegex = '(?<=^|(?<=[^a-zA-Z0-9-_\.]))#([A-Za-z]+[A-Za-z0-9]+)'
stopwords = stopwords.words('english')
stopwords = [toString(word).lower() for word in stopwords]
spamCount ={}

tweetTokens = []
tweetsUniqueString = ''
for userId in content:
	tweets = content[userId]
	tweetsUniqueString += getUniqueWords(tweets)
	tweetsUniqueString += ' '
tweetTokens = tweetsUniqueString.split()
tweetTokens = [word for word in tweetTokens if word not in stopwords]
tweetsString = ' '.join(word for word in tweetTokens)
tweetTokens = tt.tokenize(tweetsString)
tweetTokens = [toString(word) for word in tweetTokens]
wordFreq = nltk.FreqDist(tweetTokens)
numOfWords = len(wordFreq)
numOfSpam = int(numOfWords*0.10)
spamFrequency = wordFreq.most_common(numOfSpam)
print 'numOfWords:' , numOfWords, 'numOfSpam: ', numOfSpam
print spamFrequency