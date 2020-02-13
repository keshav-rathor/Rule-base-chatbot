import json
import os
import traceback
import random
# import spacy
from bidaf.models import BidirectionalAttentionFlow

from bson.objectid import ObjectId
from flask import Flask
from flask import request, make_response
from pymongo import MongoClient
import sentiment_analysis
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
from sentiment_analysis import lemmatize_sentence
from sentiment_analysis import remove_noise
from sentiment_analysis import get_all_words
from sentiment_analysis import get_tweets_for_model
from sentiment_analysis import remove_noise
import nltk

from nltk.corpus import twitter_samples
from nltk.tag import pos_tag
from nltk.corpus import twitter_samples
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
import re, string
from nltk.corpus import stopwords
import random
from nltk import FreqDist
from nltk import classify
from nltk import NaiveBayesClassifier
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
from nltk.tokenize import word_tokenize

import re, string, random


nltk.download('stopwords')
nltk.download('twitter_samples')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

positive_tweets = twitter_samples.strings('positive_tweets.json')
negative_tweets = twitter_samples.strings('negative_tweets.json')
text = twitter_samples.strings('tweets.20150430-223406.json')
tweet_tokens = twitter_samples.tokenized('positive_tweets.json')[0]
tweet_tokens = twitter_samples.tokenized('positive_tweets.json')

positive_cleaned_tokens_list = []
negative_cleaned_tokens_list = []

stop_words = stopwords.words('english')
print(remove_noise(tweet_tokens[0], stop_words))

positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')

for tokens in positive_tweet_tokens:
    positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

for tokens in negative_tweet_tokens:
    negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

print(positive_tweet_tokens[500])
print(positive_cleaned_tokens_list[500])

all_pos_words = get_all_words(positive_cleaned_tokens_list)
freq_dist_pos = FreqDist(all_pos_words)
print(freq_dist_pos.most_common(10))
positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)
positive_dataset = [(tweet_dict, "Positive") for tweet_dict in positive_tokens_for_model]
negative_dataset = [(tweet_dict, "Negative") for tweet_dict in negative_tokens_for_model]
dataset = positive_dataset + negative_dataset
random.shuffle(dataset)
train_data = dataset[:7000]
test_data = dataset[7000:]
classifier = NaiveBayesClassifier.train(train_data)



#printing the version of python
import sys
print('Python %s on %s' % (sys.version, sys.platform))

#Check the file in saved_items if it's there then pass else download from drive
import os.path
if os.path.isfile('bidaf/saved_items/bidaf_50.h5'):
    pass
else:
    from google_drive_downloader import GoogleDriveDownloader as gdd
    gdd.download_file_from_google_drive(file_id='10C56f1DSkWbkBBhokJ9szXM44P9T-KfW',
                                        dest_path='bidaf\\saved_items\\bidaf_50.h5',
                                        unzip=False)                                 #download the .h5 file from google drive

#from utils import ButtonList
MONGODB_URI = "mongodb+srv://kamlesh:techmatters123@aflatoun-quiz-pflgi.mongodb.net/test?retryWrites=true&w=majority"
client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
db = client.hrchatbot
candidates = db.Chatbots_Candidates
job = db.Hiring_PublicJobPosition


flag = 0

job_detail={}
name={}
candidates_detail={}

# Flask app should start in global layout
app = Flask(__name__)

#function displaying the text on facebook
def make_text_response(message, platform="FACEBOOK"):
    return {
        "text": {
            "text": [
                message
            ]
        },
        "platform": platform
    }



# Defining a function which inputs a text and outputs the formatted object to return in facebook response
def make_text_response(message, platform="FACEBOOK"):
    return {
        "text": {
            "text": [
                message
            ]
        },
        "platform": platform
    }


information=["experiance","skills","CTC","Location"]
information_previous=[]
def show(information,information_previous):
    if len(information) != 0:
        information_sample = random.choice(information)
        information_previous.append(information_sample)
        information.remove(information_sample)
    return information_sample


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = process_request(req)
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def process_request(req):
    global job_detail,candidates_detail
    global flag

    try:
        action = req.get("queryResult").get("action")

        if action == "input.welcome":
            # CLear the previous question list if start over

            return {
                "source": "webhook"
            }

#Asking for name from user and updating the candidates details
        elif action == "name":
            result = req.get("queryResult")
            parameter = result.get("parameters")
            candidates_detail.update(parameter)
            #candidates.insert(candidates_detail)

#Taking the details of user in community and update the database
        elif action == "Community":
            result = req.get("queryResult")
            parameter = result.get("parameters")
            candidates_detail.update(parameter)
        #candidates.insert(candidates_detail)
            if len(candidates_detail) >= 11:
                candidates.insert(candidates_detail)
                candidates_detail = {}
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        make_text_response(
                            "Excellent! i'll keep you updated."

                        )
                    ] + [
                        make_text_response("Meanwhile you can have a look on these things"),
                        {
                            "quickReplies": {
                                "title": "These are your options",
                                "quickReplies": [
                                    "About us",
                                    "Be You!",
                                    "Jobs",
                                    "Help us to improve"
                                ]
                            },
                            "platform": "FACEBOOK"
                        }

                    ]
                }

#Accept the Resume URL from user and update candidates detail
        elif action == "resume":
            result = req.get("originalDetectIntentRequest").get("payload").get("data").get("message").get("attachments")[0].get("payload")
            #resume_url = result.get("url")
            candidates_detail.update(result)


        # elif action == "skill":
        #     skills_details=[]
        #     result = req.get("queryResult")
        #     parameter = result.get("parameters")
        #     skills_text=parameter["skills"]
        #     nlp = spacy.load("en_core_web_sm")
        #     doc_skills = nlp(skills_text)
        #     for ent in doc_skills.ents:
        #         print(ent.text,ent.label_)
        #         skills_details.append(ent.text)

#Searching the jobs
        elif action == "search_jobs":
            result = req.get("queryResult")
            parameter = result.get("parameters")
            job_detail.update(parameter)
            # print("Job details", job_detail)
            # print("Name", name)

            # print("Got all job details")
            #candidates.insert(job_detail)
            filter_query = {"statusVisible": "enum.Hiring_JobPositionStatusVisible.Public"}
            filter_query.update(parameter)

            show_jobs = job.find(filter_query).limit(5)
            print("show jobs",show_jobs)

            if show_jobs.count()!=0:
                job_detail = {}
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "card": {
                                "title": i["jobTitle"],
                                "subtitle": i["companyName"] + " | " + i["locality"] + " | " + i["region"],
                                "imageUri": "https://akm-img-a-in.tosshub.com/sites/btmt/images/stories/jobs660_090518050232_103118054303_022119084317.jpg",
                                "buttons": [
                                    {
                                        "text": "View Job Detail",
                                        "postback": i["jobDetailsUrl"]
                                    }
                                ]
                            },

                            "platform": "FACEBOOK"
                        } for i in show_jobs
                    ] + [
                        make_text_response("You can apply for the job or you can view something else."),
                        {
                            "quickReplies": {
                                "title": "These are your options",
                                "quickReplies": [
                                    "About us",
                                    "Be You!",
                                    "Jobs"
                                ]
                            },
                            "platform": "FACEBOOK"
                        }

                    ]


                }

            else:
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        make_text_response(
                            " We are really sorry but we don't have any job opening for your profile for now ."
                            "We have your contact details and will contact you if there is any opening in future ."
                            "Thanks for visiting our site")
                    ]+[
                        {
                            "quickReplies": {
                                "title": "These are your options",
                                "quickReplies": [
                                    "About us",
                                    "Be You!",
                                    "Jobs"
                                ]
                            },
                            "platform": "FACEBOOK"
                        }

                    ]
                }

        elif action == "IT":
            print("IT")
            result = req.get("queryResult")
            parameter = result.get("parameters")
            job_detail.update(parameter)
            # print("Job details", job_detail)
            # print("Name", name)

            print("Got all job details")
            print(job_detail)
            #candidates.insert(job_detail)
            show_jobs = job.find({"jobTitle": job_detail["jobTitle"],
                                  "statusVisible": "enum.Hiring_JobPositionStatusVisible.Public"}).limit(3)
            print(show_jobs)

            if show_jobs:
                print("IT - Show_jobs")
                job_detail = {}
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "card": {
                                "title": i["jobTitle"],
                                "subtitle": i["companyName"] + " | " + i["locality"] + " | " + i["region"],
                                "imageUri": "https://akm-img-a-in.tosshub.com/sites/btmt/images/stories/jobs660_090518050232_103118054303_022119084317.jpg",
                                "buttons": [
                                    {
                                        "text": "View Job Detail",
                                        "postback": i["jobDetailsUrl"]
                                    }
                                ]
                            },
                            "platform": "FACEBOOK"
                        } for i in show_jobs]
                }

            else:
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        make_text_response(
                            " We are really sorry but we don't have any job opening for your profile for now ."
                            "We have your contact details and will contact you if there is any opening in future ."
                            "Thanks for visiting our site")
                    ]
                }


        elif action == "Jobs":
            print("jobs")
            result = req.get("queryResult")
            parameter=result.get("parameters")
            job_detail.update(parameter)
            # print("Job details", job_detail)
            # print("Name", name)
            if len(job_detail)>=6:
               # print("Got all job details")
               candidates.insert(job_detail)
               show_jobs = job.find({ "locality": job_detail["locality"],
                                        "statusVisible" : "enum.Hiring_JobPositionStatusVisible.Public"}).limit(3)
               # print(show_jobs)

               if show_jobs:
                   job_detail={}
                   return {
                       "source": "webhook",
                       "fulfillmentMessages":   [
                            {
                                   "card": {
                                       "title": i["jobTitle"],
                                       "subtitle": i["companyName"] + " | " + i["locality"] + " | " + i["region"],
                                       "imageUri": "https://akm-img-a-in.tosshub.com/sites/btmt/images/stories/jobs660_090518050232_103118054303_022119084317.jpg",
                                       "buttons": [
                                           {
                                               "text": "View Job Detail",
                                               "postback": i["jobDetailsUrl"]
                                           }
                                       ]
                                   },
                                   "platform": "FACEBOOK"
                               } for i in show_jobs ]
                   }

               else:
                   return {
                       "source": "webhook",
                       "fulfillmentMessages": [
                           make_text_response(" We are really sorry but we don't have any job opening for your profile for now ."
                                              "We have your contact details and will contact you if there is any opening in future ."
                                              "Thanks for visiting our site")
                       ]
                   }

#Default fallback if flag==2 means 2 known input so show the message
        elif action == "input.unknown":
            flag += 1
            if flag >= 2:
                flag = 0
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "text": {
                                "text": [
                                    "It's look like I unable to understand what you are saying but  "
                                    "I can help you these following things:\n1. About Qrata 📝\n2. Jobs 👨🏼‍🏫\n3. "
                                    "Be You",
                                ]
                            }
                        },
                        {
                            "text": {
                                "text": [
                                    "I am not fully aware of what you are asking .",
                                ]
                            },
                            "platform": "FACEBOOK"
                        },
                        {
                            "quickReplies": {
                                "title": "But I can help you these following things",
                                "quickReplies": [
                                    "About Qrata",
                                    "Jobs",
                                    "Be You",

                                ]
                            },
                            "platform": "FACEBOOK"
                        }
                    ]
                }

        elif action == "faq":
            result = req.get("queryResult")
            parameter = result.get("parameters")
            custom_tokens = remove_noise(word_tokenize(parameter))
            classifier = NaiveBayesClassifier.train(train_data)
            print(classifier.classify(dict([token, True] for token in custom_tokens)))
            return {
                "source": "webhook",
                "fulfillmentMessages": [
                    classifier.classify(dict([token, True] for token in custom_tokens))

                ]
            }




# #Document reading from FAQ intent
#         elif action == "faq":
#             result = req.get("queryResult")
#             parameter = result.get("parameters")
#             bidaf_model = BidirectionalAttentionFlow(400)
#             bidaf_model.load_bidaf("bidaf/saved_items/bidaf_50.h5")
#             bidaf_model.predict_ans('this is a very beautiful flower but girls used to think they are more beautiful.',parameter)
#             return {
#                 "source": "webhook",
#                 "fulfillmentMessages": [
#                     make_text_response(bidaf_model.predict_ans('this is a very beautiful flower but girls used to think they are more beautiful.',parameter).get('answer'))
#                 ]
#             }

#if some error occure then display this message
    except Exception as e:
        print("Error:", e)
        traceback.print_exc()
        return {
            "fulfillmentText": "Oops... 😮 I am not able to help you at the moment, please try again..",
            "source": "webhook"
        }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port {}".format(port))
    app.run(debug=False, port=port, host='0.0.0.0')
