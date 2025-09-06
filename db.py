from pymongo import MongoClient

MONGO_URI = "mongodb+srv://unizakhadpolkar:Uniza12345@cluster0.yqaaq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['submissions']  # Replace with your database name
collection = db['submissions']  # Replace with your collection name

# Test if connection is successful
print(collection.find_one())
