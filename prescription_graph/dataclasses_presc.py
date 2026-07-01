from pydantic import BaseModel, Field
from typing import List


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