from datetime import datetime
from typing import List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict, message_to_dict
from pymongo import MongoClient, ASCENDING
import json
import streamlit as st


class ChatDbMessages(BaseChatMessageHistory):
    def __init__(self):
        self.client = MongoClient(host='127.0.0.1', port=27017)
        self.session_id = st.session_state.session_id

        database = self.client['chat_history_test']
        self.collection = database['message_store_test']

    @property
    def messages(self) -> List[BaseMessage]:
        try:
            session = self.collection.find({'session_id': self.session_id})
            if session:
                results = [json.loads(data['history']) for data in session]
            else:
                results = []

        except Exception as e:
            raise e

        return messages_from_dict(results)

    def add_message(self, message:BaseMessage) -> None :
        try:
            self.collection.insert_one({
                'session_id': self.session_id,
                'history': json.dumps(message_to_dict(message)),
                'session_options': json.dumps(st.session_state.session_options),
                'timestamp': datetime.now()
            })

        except Exception as e:
            raise e

    def clear(self) -> None:
        self.collection.delete_many({'session_id': self.session_id})

    def get_previus_sessions(self):
        unique_sessions = {}

        for data in self.collection.find().sort('timestamp', ASCENDING):
            session_id = data['session_id']
            timestamp = data['timestamp']

            if session_id not in unique_sessions:
                unique_sessions[session_id] = timestamp

        # Retornar o session_id e timestamp únicos
        return [{'session_id': session_id, 'timestamp': timestamp} for session_id, timestamp in unique_sessions.items()]

    def get_previus_sessions_options(self, session_id:str) -> dict:
        return [json.loads(data['session_options']) for data in self.collection.find({"session_id":session_id}).limit(1)][0]

    def get_message_history(self, session_id:str=None) -> List[BaseMessage]:
        if session_id:
            result = [json.loads(data['history']) for data in self.collection.find({'session_id': session_id}).limit(1)]
        else:
            result = [json.loads(data['history']) for data in self.collection.find()]

        return messages_from_dict(result)

# if __name__=="__main__":
#     client = MongoClient(host='127.0.0.1', port=27017)

#     database = client['chat_history_test']
#     collection = database['message_store_test']

#     result = [data['session_options'] for data in collection.find({"session_id":'19ae2da5-af6b-43bc-8509-cafcab2fc437'}).limit(1)]

#     print(result)

    # result = [{data['session_id'] : data['timestamp']} for data in collection.find().sort('timestamp',-1)]

    # distinct_sessions = {}

    # for item in result:
    #     for session_id, timestamp in item.items():
    #         # Se o session_id já existir, comparar os timestamps
    #         if session_id in distinct_sessions:
    #             # Substitui o valor se o timestamp for mais recente
    #             if timestamp > distinct_sessions[session_id]:
    #                 distinct_sessions[session_id] = timestamp
    #         else:
    #             # Se não existe ainda, adiciona o session_id e o timestamp
    #             distinct_sessions[session_id] = timestamp

    # # Resultado final
    # print([distinct_sessions])
