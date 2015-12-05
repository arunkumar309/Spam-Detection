#install fuzzywuzzy
# add 'import datetime' to both legit_features.py and polluters_features.py
from legit_features import content as features
from legit_tweets import content as tweets
from fuzzywuzzy import fuzz
import nltk
from nltk.stem.snowball import SnowballStemmer
import datetime
import unicodedata

mostTweeted = {}
tweetsCreatedAt = {}
tweetsToCheck = {}
tweetsToStem = {}
tweetSimilarity = {}
stemmer = SnowballStemmer('english')

def toString(unicodeData):
	stringOut = unicodedata.normalize('NFKD',unicodeData).encode('ascii','ignore')
	return stringOut.lower()

stopwords = nltk.corpus.stopwords.words('english')
stopwords = [toString(word) for word in stopwords]

def write_to_file(dictionary, dictname):
	print 'Inside write_to_file for' , dictname
	with open(dictname + '.py', 'w') as f:
		f.write('content = ' + str(dictionary))

def getMostTweetedDate(feature):
	global mostTweeted
	for userId in feature:
		mostTweeted[userId] = {}
		mostCommon = nltk.FreqDist(feature[userId]['tweetFrequency'])\
		.most_common(1)
		mcYear, mcMonth, mcDay = mostCommon[0][0][0], mostCommon[0][0][1],mostCommon[0][0]\
		[2]
		mostTweeted[userId]['YMD'] = (mcYear,mcMonth,mcDay)
		mostTweeted[userId]['count'] = mostCommon[0][1]

def getToStemTweets():
	global tweetsToStem, tweetsCreatedAt
	for userId in tweetsCreatedAt:
		tweetsToStem[userId] = []
		tweetIndices = []
		timeObjs = tweetsCreatedAt[userId]
		for timeObj in timeObjs:
			date = (timeObj.year, timeObj.month, timeObj.day)
			if date == mostTweeted[userId]['YMD']:
				tweetIndices.append(timeObjs.index(timeObj))
		for index in tweetIndices:
			tweetsToStem[userId].append(tweets[userId][index])

def stemming():
	global tweetsToCheck
	for userId in tweetsToStem:
		tweets = tweetsToStem[userId]
		tweetsToCheck[userId] = []
		for tweet in tweets:
			tweet = tweet.lower().split()
			tweet = [word for word in tweet if word not in stopwords]
			tweet = ' '.join(word for word in tweet)
			tweet = stemmer.stem(tweet)
			tweet = toString(tweet)
			tweetsToCheck[userId].append(tweet)

def similarity(feature, dictname):
	global tweetSimilarity
	c = 1
	for userId in feature:
		tweetsCreatedAt[userId] = feature[userId]['tweetsCreatedAt']
	getMostTweetedDate(feature)
	getToStemTweets()
	stemming()
	for userId in tweetsToCheck:
		tweetSimilarity[userId] = {}
		tweetSim  = []
		print c, len(tweetsToCheck[userId])
		for tweet in tweetsToCheck[userId]:
			index = tweetsToCheck[userId].index(tweet)
			#print 'Comparing tweet ', index, 'with other tweets'
			for tweetNext in tweetsToCheck[userId][index+1:]:
				similarity = fuzz.token_set_ratio(tweet, tweetNext)
				tweetSim.append(similarity)
		numOfTweets = len(tweetsToCheck[userId])
		if numOfTweets > 1:
				tweetSimilarity[userId]= sum(tweetSim)/(100*float(numOfTweets*(numOfTweets-1)/2))
	write_to_file(tweetSimilarity, dictname)

if __name__ == '__main__':
	similarity(features, 'legitimateTweetSimilarities')
	mostTweeted = {}
	tweetsCreatedAt = {}
	tweetsToCheck = {}
	tweetsToStem = {}
	tweetSimilarity = {}
	from polluters_features import content as features
	from polluters_tweets import content as tweets
	similarity(features, 'pollutersTweetSimilarities')