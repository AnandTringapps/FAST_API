from pymongo import MongoClient,client
conn = MongoClient()
client = "mongodb+srv://anandthravichandran:V4mWZltFTKKkQeRc@trl.uzbkhjf.mongodb.net/?retryWrites=true&w=majority&appName=TRL"

db= client.TRL

collection_name= db["Emp"]


