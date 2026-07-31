# spamscoring.py
# Script for scoring email based on spam probability metrics with pretrained Tensorflow model
import string
import pickle
import nltk
import tensorflow as tf
from nltk.corpus import stopwords
from tensorflow.keras.preprocessing.sequence import pad_sequences

nltk.download("stopwords", quiet=True)

# Preprocessing to remove punctuation and stopwords
punctuation = string.punctuation

def rm_punctuation(text):
    translator = str.maketrans("", "", punctuation)
    return text.translate(translator)

def rm_stopwords(text):
    stwords = set(stopwords.words("english"))

    words = []
    for word in str(text).split():
        word = word.lower()
        if word not in stwords:
            words.append(word)

    return " ".join(words)

# Function for scoring email which returns a float value representing probability that the email is spam
# 	email_path: path to email (plaintext file)
#	model: tf.keras.Model (exported from initial training)
#	tokenizer: keras.preprocessing.text.Tokenizer (exported from initial training)
#	max_length: sequence length used during training (integer)

def spamscoring(email_path, model, tokenizer, max_length=200):
    with open(email_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    subject = ""
    body = ""

    if lines:
        first_line = lines[0].strip()

        if first_line.lower().startswith("subject:"):
            subject = first_line[len("Subject:"):].strip()
            body = "".join(lines[1:])
        else:
            body = "".join(lines)

    # Concatenate subject and body
    text = f"{subject} {body}"

    # Preprocess
    text = rm_punctuation(text)
    text = rm_stopwords(text)

    # Convert to sequence
    sequence = tokenizer.texts_to_sequences([text])

    padded = pad_sequences(sequence, maxlen=max_length, padding="post",truncating="post")

    # Predict
    probability = model.predict(padded, verbose=0)[0][0]

    return float(probability)