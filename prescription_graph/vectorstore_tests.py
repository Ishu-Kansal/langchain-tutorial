import json
from typing import List, TypedDict
from dotenv import find_dotenv, load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

import dataloader
from dataclasses_presc import ContIndFiles

load_dotenv(find_dotenv(), override=True)
dataloader.reset_and_load_patient_history("first", './data/patient_history/processed')

def cross_reference_patient_history(contraindications_file_path: str, patient_uuid: str, top_n_visits: int = 3):
    # 1. Read your manually extracted contraindications document in full
    with open(contraindications_file_path, "r", encoding="utf-8") as f:
        extracted_contraindications = f.read().strip()
        
    print(f"\nScanning history for Patient {patient_uuid} using extracted drug warnings...")
    
    # 2. Query the patient records using the full list of warnings as the semantic prompt
    # High-efficiency deterministic filter restricts the search space to *only* this patient's records
    query_results = dataloader.patient_collection.query(
        query_texts=[extracted_contraindications],
        n_results=top_n_visits,
        where={"patient_id": patient_uuid}
    )
    
    # 3. Extract the complete matching doctor visits
    matching_visits = query_results["documents"][0] if query_results["documents"] else []
    with open("data.txt", 'w') as fp:   
        print(json.dump(query_results, fp, indent=1))
    print(f"Retrieved {len(matching_visits)} clinical encounters matching the risk profile.")
    
    # Clean join to feed right into your LLM safety validation prompt
    combined_patient_context = "\n\n========================================\n\n".join(matching_visits)
    
    return extracted_contraindications, combined_patient_context, matching_visits, query_results

def getErrFiles(threshold: float, drug_filepath: str, patient_id: str, top_n: int) -> List[ContIndFiles]:
    contra, context, rel_visits, res = cross_reference_patient_history(drug_filepath, patient_id, top_n)
    distances = res['distances'][0] if res['distances'] else []

    criticalFiles = []
    for i in range(len(distances)):
        if(distances[i] < threshold):
            text = rel_visits[i].split('\n\n')
            err_filename = text[0]
            err_text = text[1]
            criticalFiles.append({"filename": err_filename, "text": err_text, "distance": distances[i]})
    
    return criticalFiles

def processErrors(errF: List[ContIndFiles]):
    if len(errF) == 0:
        # go to Intake Prep cycle
        pass
    else:
        contraIndCheck = SystemMessage(content=(
            "You are an intelligent pharmacist technician.\n"
            "Attached is the prescribed drugs's information and the patient's potentially conflicting history. "
            "Check to see if the patient history will have any adverse effects if the drug is prescribed."
        ))
        docs = HumanMessage(content={})
        # check if any files are actual errors
        

errF = getErrFiles(1.5, './data/drugs/proair_hfa.txt', 'first', 8)



for err in errF:
    print('\n' + err['filename'] + '\n' + err['text'] + '\n' + str(err['distance']) + '\n')

# dataloader.process_history_standardize('first', './data/patient_history')

