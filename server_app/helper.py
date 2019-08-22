from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import glob
import speech_recognition as sr
import os


def filter_sentence(sentence=None):
    """
    this fxn takes a sentence and remove stop words from it and return it as a list
    Parameters: sentence - string sentence to be filtered
    Return: a list of string after removing the stopwords
    """
    # empty string
    result = []
    # get all the words in sentence
    words = word_tokenize(sentence)
    # get all the stop words
    stop_words = set(stopwords.words("english"))
    for w in words:
        if w not in stop_words:
            result.append(w)
            print(result)
    return result

fileName = ""
files = ""
data = []
fdata = ""
fnamelist = []
speech_to_text = {}
UPLOAD_FOLDER = '/tmp/uploadFolder/'  # os.path.join("F:", "uploadFolder")

def print_it(filterfile=""):
    global fdata
    global strdata
    strdata = ""
    fdata = ""
    text = ""
    global speech_to_text
    # threading.Timer(10.0, printit).start()
    filenames = glob.glob(UPLOAD_FOLDER + "*.wav")
    # print(filenames)
    if (len(filenames) > 0):
        for index in range(len(filenames)):
            fileName = filenames[index]
            fpathlist = fileName.split("/")
            files = fpathlist[len(fpathlist) - 1]
            fnamelist = files.split("_")
            if (filterfile in files):
                fdata = fdata + files + ":"
                r = sr.Recognizer()
                audio =  UPLOAD_FOLDER+files
                with sr.AudioFile(audio) as source:
                    audio = r.record(source)
                try:
                    text = r.recognize_google(audio)
                    speech_to_text[files] = text
                except Exception as e:
                    print(e)
                data.append(text + ":")
                strdata = strdata + text + ":"
        f = open(UPLOAD_FOLDER + filterfile + ".txt", "w")
        f.writelines(data)
        f.close()
        # return data
        return strdata + "@" + fdata
        # print(speech_to_text)
        # print(strdata + "@" + fdata)
    else:
        print("file not uploaded")

def make_a_dir(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            print("not need to create the dir, dir already present")
    except Exception as e:
        print("Error: "+e)
    