import json

import dataloader

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
        n_results=8,
    )
    
    # 3. Extract the complete matching doctor visits
    matching_visits = query_results["documents"][0] if query_results["documents"] else []
    with open("data.txt", 'w') as fp:   
        print(json.dump(query_results, fp, indent=1))
    print(f"Retrieved {len(matching_visits)} clinical encounters matching the risk profile.")
    
    # Clean join to feed right into your LLM safety validation prompt
    combined_patient_context = "\n\n========================================\n\n".join(matching_visits)
    
    return extracted_contraindications, combined_patient_context, matching_visits


contra, context, rel_visits = cross_reference_patient_history('./data/drugs/proair_hfa.txt', 'first')
print(context, type(context))

for visit in rel_visits:
    pass


# dataloader.process_history_standardize('first', './data/patient_history')

