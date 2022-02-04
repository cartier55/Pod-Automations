import pickle

def load_cookies(file):
    with open(file, 'rb') as f:
        cookies = pickle.load(f)
    return cookies
    ...