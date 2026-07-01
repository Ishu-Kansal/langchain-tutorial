import uuid
import base64
from flask import Flask, request, jsonify
from dotenv import load_dotenv, find_dotenv

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver  
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import psycopg as pg


from dataclasses import PrescInfo
from psql import connect_str

load_dotenv(find_dotenv(), override=True)


def run_img_indexing(fp: str):
    with open('./data/proair_presc.png', 'rb') as imgfp:
        img_str = base64.b64encode(imgfp.read()).decode("utf-8")
    
    presc_processor_prompt = SystemMessage(content=("You are an expert prescription parser.\n" 
    "Your job is to parse the prescription into its components for further analysis."))

    presc_human_data = HumanMessage(content=[
        {"type": "text", "text": "Parse the following prescription into the output format"},
        {
            "type": "image_url",
            "image_url": {"url":f"data:image/jpeg;base64,{img_str}"}
        }
    ])

    messages = [
        presc_processor_prompt, presc_human_data
    ]
    
    llm = ChatOpenAI(temperature=0.2, model='gpt-5.4')
    threadID = f"presc-{uuid.uuid4().hex[:8]}"
    mem = InMemorySaver()
    mem.delete_thread(threadID)
    presc_agent = create_agent(
        model=llm, 
        response_format=PrescInfo,
        checkpointer=mem
    )
    
    res = presc_agent.invoke({"messages": messages}, config={"configurable": {"thread_id": threadID}})
    receipt_info: PrescInfo = res["structured_response"]
    print(receipt_info)
    
def search_patient_db(receipt_info: PrescInfo):
    with pg.connect(connect_str) as conn:
        with conn.cursor() as cur:
            fname = receipt_info.patient_first_name
            lname = receipt_info.patient_last_name
            dob = datetime.strptime(receipt_info.patient_DOB, '%m/%d/%Y').date()
            query = f"SELECT * FROM patients WHERE first_name = '{fname}' AND last_name = '{lname}' AND date_of_birth = %s"
            cur.execute(query, (dob,))
            existingRecords = cur.fetchall()
            for row in existingRecords:
                print(row)
            
            if len(existingRecords) == 0:
                newUUID = uuid.uuid4()
                updateQuery = f"INSERT INTO patients (first_name, last_name, date_of_birth) VALUES ('{fname}', '{lname}', %s)"
                cur.execute(updateQuery, (dob,))