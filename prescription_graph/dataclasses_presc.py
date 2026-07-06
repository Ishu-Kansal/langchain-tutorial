from pydantic import BaseModel, Field
from typing import List, Optional, TypedDict

class DrugInfoBasic(BaseModel):
    drug_name: str = Field(description="Name of drug as given on prescription")
    active_ingredients: List[str] = Field(description="List of active ingredients in drug")

class PrescInfo(BaseModel):
    date: str = Field(description="Date formatted in MM-DD-YYYY")
    prescription_name: str = Field(description="Name of prescription given exactly.")
    active_ingrediants: List[str] = Field(description="list of active ingrediants in drug")
    patient_first_name: str = Field(description="First name of patient")
    patient_last_name: str = Field(description="Last name of patient")
    patient_DOB: str = Field(description="Date of birth of patient in MM/DD/YYYY")
    medication_details: str = Field(description="Details and instructions on usage")
    num_refills: float = Field(description="Maximum number of refills allowed")
    is_signed: bool = Field(description="True if the description is valid and signed, false otherwise")
    fulltext: str = Field(description="All text on prescription for analysis")
    
class PatientHistoryDoc(BaseModel):
    patient_uuid: str = Field(description="Patient's unique uuid identifier")
    prescription_names: Optional[List[DrugInfoBasic]] = Field(description="List of drugs prescribed during visit")
    conditions: Optional[List[str]] = Field(description="Patient's conditions which they are being treated for")
    
    def to_semantic_string(self) -> str:
        """Converts structured fields into natural medical prose for optimal RAG vector matching."""
        lines = [f"Patient Medical Record Summary."]
        
        if self.conditions:
            lines.append(f"The patient is currently diagnosed with and being treated for: {', '.join(self.conditions)}.")
            
        if self.prescription_names:
            drug_descriptions = []
            for drug in self.prescription_names:
                ingredients = f" (containing active ingredients: {', '.join(drug.active_ingredients)})" if drug.active_ingredients else ""
                drug_descriptions.append(f"{drug.drug_name}{ingredients}")
            lines.append(f"The patient is currently taking the following concurrent medications: {', '.join(drug_descriptions)}.")
            
        return " ".join(lines)

class ContIndFiles(TypedDict):
    filename: str
    text: str
    distance: float

class CriticalContradiction(BaseModel):
    prescription_names: Optional[List[(DrugInfoBasic, DrugInfoBasic)]] = Field(description=("List of "
        "contraindicting drugs represented as a tuple with first drug being the drug to-be-prescribed"))
    conditions: Optional[List[str]] = Field(description="Patient's conditions that contraindicate prescribed drug")
    significant_contra: bool = Field(description="True if contraindication is found and doctor callback required")

class CriticalContraWrapper(TypedDict):
    patient_id: str
    contras: List[(str, CriticalContradiction)] # tuple of patient history (filename, contra)
    
    