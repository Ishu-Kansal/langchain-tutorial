import dataloader
from dataloader import drugInfos

dataloader._initialize_and_load_data()

drug_name = "ProAir HFA"
drug_results = drugInfos.query(
        query_texts=[f"warnings and interactions, not recommended, other drugs, contraindications for {drug_name}"],
        n_results=10,
        where={"drug_name": drug_name.lower()}
    )

print("\n--- Retrieved Drug Context ---")
print(drug_results["documents"][0])
print(len(drug_results["documents"][0]))