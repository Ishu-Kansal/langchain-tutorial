import os
import chromadb
from chromadb.utils import embedding_functions

from dotenv import find_dotenv, load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from dataclasses_presc import DrugInfoBasic, PatientHistoryDoc

print("initializing clinical RAG pipeline...")
load_dotenv(find_dotenv(), override=True)

patient_client = chromadb.EphemeralClient()
embedding_func = embedding_functions.DefaultEmbeddingFunction()

patient_collection = patient_client.get_or_create_collection(
    "patient_visits", 
    embedding_function=embedding_func
)

def reset_and_load_patient_history(patient_uuid: str, visit_files_dir: str):
    """
    Wipes the store and loads a patient's complete history.
    Each individual text file in the directory is treated as a single, complete doctor's visit.
    """
    global patient_collection
    try:
        patient_client.delete_collection("patient_visits")
    except ValueError:
        pass
    
    patient_collection = patient_client.create_collection(
        "patient_visits", 
        embedding_function=embedding_func,
    )
    
    if not os.path.exists(visit_files_dir):
        print(f"Error: Visit directory '{visit_files_dir}' not found.")
        return

    documents = []
    metadatas = []
    ids = []

    file_list = [f for f in os.listdir(visit_files_dir) if f.endswith(".txt")]
    
    for i, filename in enumerate(file_list):
        file_path = os.path.join(visit_files_dir, filename)
        
        with open(file_path, "r", encoding="utf-8") as f:
            visit_text = f.read().strip()
            
        if not visit_text:
            continue
        
        structured_content = f"CLINICAL ENCOUNTER FILE: {filename}\n\n{visit_text}"
        
        documents.append(structured_content)
        ids.append(f"pat_visit_{filename}")
        metadatas.append({
            "patient_id": str(patient_uuid),
            "visit_file": filename
        })

    if documents:
        patient_collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"Indexed {len(documents)} complete doctor visits for Patient UUID: {patient_uuid}")
    else:
        print("o valid text documents found in the specified directory.")



def process_history_standardize(patient_uuid: str, visit_files_dir: str):
    documents = []
    metadatas = []
    ids = []

    file_list = [f for f in os.listdir(visit_files_dir) if f.endswith(".txt")]
    for i, filename in enumerate(file_list):
        file_path = os.path.join(visit_files_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            visit_text = f.read().strip()
        if not visit_text:
            continue
        print('reading history ', filename)
        processor_prompt = SystemMessage(content=(
            "You are an intelligent pharmacy data processor. Your job is to take the given patient history "
            "and convert it into a standardized format. Include any drugs prescribed and patient's "
            "health conditions (ex. diabetes, heart problems, etc)"
        ))
        
        currPatientHistMsg = HumanMessage(content=(visit_text))
        messages = [processor_prompt, currPatientHistMsg]
        
        llm = ChatOpenAI(temperature=0.2, model='gpt-5.4')
        agent = create_agent(model=llm, response_format=PatientHistoryDoc)
        
        res = agent.invoke(input={"messages": messages})
        currHist: PatientHistoryDoc = res["structured_response"]
        print(currHist)
        processed = currHist.to_semantic_string()
        outfp = visit_files_dir + "/processed/" + filename
        with open(outfp, 'w') as fp:
            fp.write(processed)
        
        
  