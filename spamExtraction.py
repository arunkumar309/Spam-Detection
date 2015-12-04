#Remove '_sample' from the frist two from import statements to run on the complete dataset
from polluters_tweets_sample import content as pollutersTweets
from legit_tweets_sample import content as legitTweets
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
import nltk
import unicodedata
import string
import re
from collections import Counter
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

def getSpamFreq(tweetsUniqueString):
	global numOfWords, numOfSpam, spamFrequency, spamFrequencyDict
	tweetTokens = tweetsUniqueString.lower().split()
	tweetTokens = [word for word in tweetTokens if word not in stopwords]
	tweetsString = ' '.join(word for word in tweetTokens)
	tweetTokens = tt.tokenize(tweetsString)
	tweetTokens = [toString(word) for word in tweetTokens]
	wordFreq = nltk.FreqDist(tweetTokens)
	numOfWords = len(wordFreq)
	numOfSpam = int(numOfWords*0.10)
	spamFrequency = wordFreq.most_common(numOfSpam)
	spamFrequencyDict = dict(spamFrequency)
	#spamFrequencyDict['prop'] = {}
	#spamFrequencyDict['prop']['numOfWords'] = numOfWords
	#spamFrequencyDict['prop']['numOfSpam'] = numOfSpam

def matchSpam(tweetsDict):
	global matchedSpamFreq, matchedSpam
	for userId in tweetsDict:
		matchedSpam = []
		matchedSpamCount= 0
		matchedSpamFreq[userId] = {}
		tweets = tweetsDict[userId]
		tweets = getUniqueWords(tweets)
		tweets = tweets.split()
		tweets = [word for word in tweets if word not in stopwords]
		tweets = dict(Counter(tweets))
		totalWords = len(tweets)
		for word in tweets:
			if word in spamFrequencyDict:
				matchedSpam.append((word, tweets[word]))
				matchedSpamCount += tweets[word]
		matchedSpamFreq[userId]['matchedWords'] = matchedSpam
		matchedSpamFreq[userId]['frequency'] = (matchedSpamCount, totalWords)

def write_to_file(dictionary, dictname):
	print 'Inside write_to_file for' , dictname
	with open(dictname + '.py', 'w') as f:
		f.write('content = ' + str(dictionary))

punctuations = string.punctuation
tt = TweetTokenizer()
urlRegex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
replyRegex = '(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)'
hashtagRegex = '(?<=^|(?<=[^a-zA-Z0-9-_\.]))#([A-Za-z]+[A-Za-z0-9]+)'
stopwords = stopwords.words('english')
stopwords = [toString(word).lower() for word in stopwords]
tweetTokens = []
tweetsUniqueString = ''
matchedSpamFreq = {}
if __name__ == '__main__':
	for userId in pollutersTweets:
		tweets = pollutersTweets[userId]
		tweetsUniqueString += getUniqueWords(tweets)
		tweetsUniqueString += ' '
	getSpamFreq(tweetsUniqueString)
	print 'NumOfUniqueWordsInPollutersTweets:' , numOfWords,\
	'\nnumOfSpamWordsUnderConsideration: ', numOfSpam, '\n'
	matchSpam(legitTweets)
	for userId in matchedSpamFreq:
		print 'userId:', userId, '\nNumOfMatchedSpamWords:',\
		matchedSpamFreq[userId]['frequency'][0],\
		'\nNumOfUniqueWordsInAllTweets:',\
		matchedSpamFreq[userId]['frequency'][1], '\n'
	write_to_file(spamFrequencyDict, 'spamFrequency')
	write_to_file(matchedSpamFreq, 'matchedSpam')