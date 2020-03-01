import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd 
from datetime import datetime

def add_to_collection(collection_name, dic_list, fs_client):
    """Adds a list of dictionaries to a collection in firestore
    Considers that the firebase_admin app is already initialized and takes in argument the firestore client.
    
    collection_name: the collection name in Firestore
    dic_list: list of dicts
    fs_client: the firestore client object
    
    """
    
    doc_ref = fs_client.collection(collection_name)
    for d in dic_list:
        doc_ref.add(d)
    print("dic_list added to the collection", collection_name)


def agg_checks(event, context):
    PROJECT_ID = "ngt-technical-test"
    cred = credentials.ApplicationDefault()
    
    if (not len(firebase_admin._apps)):
        firebase_admin.initialize_app(cred, {'projectId': PROJECT_ID})
    db = firestore.client()
    
    doc_ref = db.collection("check_redeemed_subscribed")
    docs = doc_ref.stream()
    doc_list=[]
    
    for doc in docs:
        doc_list.append(doc.to_dict())
        
    df=pd.DataFrame(doc_list)

    df["Valuation_Date"]=df.apply(lambda row: datetime.strptime(row.Valuation_Date, "%d/%m/%Y"),
                                    axis=1)
    
    df["Valuation_Month"]=df.apply(lambda row: row.Valuation_Date.month,
                                    axis=1)
    
    df["Valuation_Year"]=df.apply(lambda row: row.Valuation_Date.year,
                                    axis=1)
    
    dic_list=df.groupby(["Valuation_Year", "Valuation_Month"], as_index=False)['NAV_Per_Share_Redeemed_Subscribed_Check'].min().to_dict("records")
    
    add_to_collection("check_redeemed_subscribed_aggregated", dic_list, db)
    return "Successful request"
    
