import os
import json
import pandas as pd
import tempfile
from supabase import create_client, Client
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

import RAGer as rag

class UserData:
    def __init__(self):
        self.Data = None
        self.important_fields = [
            'F_Name', 'L_Name', "Gender", 'Mobile_No', "Income", 'Bureau_score',
            "Loan_amount", "Loan_type", "Interest_Rate", 'Interest', 'Loan_Processing_Fee', "Current_balance",
            "Installment_Amount",
            'Disbursal_Date', "Repayment_Start_Date", "Repayment_tenure", "Date_of_last_payment", 'Repayment_mode',
            "No_of_late_payments"
        ]
        self.account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.container_name = os.getenv("AZURE_CONTAINER_NAME")
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.blob_name = "borrower.csv"

    def read_file(self, file_name="borrower.csv"):
        try:
            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            container_client = blob_service_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(file_name)  # use file_name instead of self.blob_name

            print(f"Downloading {file_name} from Azure Blob Storage...")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                blob_data = blob_client.download_blob()
                tmp_file.write(blob_data.readall())
                temp_file_path = tmp_file.name  # Save path before closing

            print(f"Downloaded to temporary file: {temp_file_path}")
            
            # Read CSV from temp file
            self.Data = pd.read_csv(temp_file_path)

            # Clean up
            os.remove(temp_file_path)

        except Exception as e:
            print(f"Error downloading or reading CSV from Azure Blob Storage: {e}")
            self.Data = None

    def fetch_user(self,phone_no):
        try:
            phone_no = int(phone_no)
            if phone_no in self.Data['Mobile_No'].values:
                user_data = self.Data.loc[self.Data['Mobile_No'] == phone_no]
                user_info = {
                    "first_name": user_data['F_Name'].item(),
                    "last_name": user_data['L_Name'].item(),
                    "phone_no": user_data['Mobile_No'].item(),
                    "gender": user_data['Gender'].item(),
                    "income_in_inr": user_data['Income'].item(),
                    "credit_score": user_data['Bureau_score'].item(),
                    "loan_type": user_data['Loan_type'].item(),
                    "loan_amount": user_data['Loan_amount'].item(),
                    "interest_rate": user_data['Interest_Rate'].item(),
                    "process_fee": user_data['Loan_Processing_Fee'].item(),
                    "installment": user_data['Installment_Amount'].item(),
                    "start_date": user_data['Repayment_Start_Date'].item(),
                    "tenure": user_data['Repayment_tenure'].item(),
                    "balance_to_pay": user_data['Current_balance'].item(),
                    "payment_mode": user_data['Repayment_mode'].item(),
                    "late_payment": user_data['No_of_late_payments'].item(),
                    "last_date": user_data['Date_of_last_payment'].item(),
                    "due_date": user_data['Next_due_date'].item(),
                    "pending_days": user_data['Pending_days'].item(),
                    "minimum_due_amount": user_data['Minimum_amount_due'].item(),
                    "late_fees": user_data["Late_Fees"].item(),
                    "emi_eligible": user_data["Eligible_for_EMI"].item()
                }
                return user_info
            else:
                print('User does not exist.')
                return {"Error": "User does not exist."}
        except (TypeError) as e:
            print(f'Such a Phone Number does not exist in {self.file_path}')
            return {}

    def fetch_info(self,query):
        result = rag.fetch_query(query)
        return result

# class Database:
#     def __init__(self):
#         self.cred = credentials.Certificate("./conversational-ai-ab55c-firebase-adminsdk-fbsvc-e19783f081.json")
#         try:
#             firebase_admin.initialize_app(self.cred)
#         except ValueError as e:
#             print('Firebase App already Initialized')
#         self.db = firestore.client()

#     def init_user(self,phone: str, wa_id=None, chat_id=None, name=None):
#         doc_ref = self.db.collection("testing").document(phone)
#         if not doc_ref.get().exists:
#             data = {
#                 "whatsapp_id": wa_id,
#                 "id": chat_id,
#                 "phone": phone,
#                 "name": name,
#                 "whatsapp_messages": [],
#                 "call_transcripts": []
#             }
#             self.db.collection("testing").document(phone).set(data)

#         return self.db.collection("testing").document(phone)

#     def payload(self, name, text, time):
#         msg = {
#             f"{name}": str(text),
#             "timestamp": time
#         }
#         return msg

#     def add_convo(self, ref, agent, msg):
#         if agent == 'voice':
#             ref.update({"call_transcripts": firestore.ArrayUnion(msg)})
#         elif agent == 'whatsapp':
#             ref.update({"whatsapp_messages": firestore.ArrayUnion(msg)})
#         else:
#             raise Exception('Invalid Agent')

#     def get_convo(self, ref, agent):
#         if agent == 'voice':
#             conversation = ref.get().to_dict()['call_transcripts']
#         elif agent == 'whatsapp':
#             conversation = ref.get().to_dict()['whatsapp_messages']
#         else:
#             raise Exception('Invalid Agent')

#         for msg in conversation:
#             if 'timestamp' in msg:
#                 del msg['timestamp']

#         latest_conversation = conversation[-10:]  # Slicing the list
#         return latest_conversation


class Database:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    def init_user(self, phone: str, wa_id=None, chat_id=None, name=None):
        response = self.supabase.table("users").select("*").eq("phone", phone).execute()
        
        if not response.data: 
            data = {
                "phone": phone,
                "whatsapp_id": wa_id,
                "chat_id": chat_id,
                "name": name,
                "whatsapp_messages": [],
                "call_transcripts": []
            }
            self.supabase.table("users").insert(data).execute()
        
        return phone 

    def payload(self, name, text, time):
        msg = {
            name: str(text),
            "timestamp": time.isoformat() if isinstance(time, datetime) else time
        }
        return msg

    # def add_convo(self, ref, agent, msg):
    #     response = self.supabase.table("users").select("*").eq("phone", ref).execute()
    #     if not response.data:
    #         raise Exception("User does not exist")

    #     user_data = response.data[0]
        
    #     if agent == "voice":
    #         user_data["call_transcripts"].append(msg)
    #         self.supabase.table("users").update({
    #             "call_transcripts": user_data["call_transcripts"]
    #         }).eq("phone", ref).execute()
    #     elif agent == "whatsapp":
    #         user_data["whatsapp_messages"].append(msg)
    #         self.supabase.table("users").update({
    #             "whatsapp_messages": user_data["whatsapp_messages"]
    #         }).eq("phone", ref).execute()
    #     else:
    #         raise Exception("Invalid Agent")
    def add_convo(self, ref, agent, msg):
        response = self.supabase.table("users").select("*").eq("phone", ref).execute()
        if not response.data:
            raise Exception("User does not exist")

        user_data = response.data[0]

        if isinstance(msg, list):
            try:
                msg = json.dumps(msg) 
            except Exception as e:
                raise Exception(f"Message not serializable: {e}")

        if agent == "voice":
            user_data["call_transcripts"].append(msg)
            self.supabase.table("users").update({
                "call_transcripts": user_data["call_transcripts"]
            }).eq("phone", ref).execute()
        elif agent == "whatsapp":
            user_data["whatsapp_messages"].append(msg)
            self.supabase.table("users").update({
                "whatsapp_messages": user_data["whatsapp_messages"]
            }).eq("phone", ref).execute()
        else:
            raise Exception("Invalid Agent")


    def get_convo(self, ref, agent):
        response = self.supabase.table("users").select("*").eq("phone", ref).execute()
        if not response.data:
            raise Exception("User does not exist")

        user_data = response.data[0]
        
        if agent == "voice":
            conversation = user_data["call_transcripts"]
        elif agent == "whatsapp":
            conversation = user_data["whatsapp_messages"]
        else:
            raise Exception("Invalid Agent")

        for msg in conversation:
            if "timestamp" in msg:
                del msg["timestamp"]

        latest_conversation = conversation[-10:]
        return latest_conversation
    