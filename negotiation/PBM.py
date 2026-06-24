import uuid
from flask import Flask, request, jsonify
from dotenv import load_dotenv, find_dotenv

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import InMemorySaver  
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List



load_dotenv(find_dotenv(), override=True)
app = Flask(__name__)

class DrugInfo(BaseModel):
    prescriptionName: str = Field(description="Official branded prescription name or 'generic'")
    activeIngredient: str = Field(description="active ingredient in the drug")
    dosage: float = Field(description="dosage in milligrams of drug")
    price: float = Field(description="full cost of one dose of drug")
    

drugMap = {
    "ProAir_XCell": DrugInfo(
        prescriptionName="ProAir HFA",
        activeIngredient="Albuterol Sulfate",
        dosage=0.09,
        price=100.00
    ),
    "ProAir_GEN": DrugInfo(
        prescriptionName="generic",
        activeIngredient="Albuterol Sulfate",
        dosage=0.09,
        price=85.00
    ),
    "ProAir_LITE": DrugInfo(
        prescriptionName="generic",
        activeIngredient="Albuterol Sulfate",
        dosage=0.05,
        price=70.00
    ),
    "FloVent_HFA": DrugInfo(
        prescriptionName="Flovent HFA",
        activeIngredient="Fluticasone Propionate",
        dosage=0.11,
        price=110.00
    ),
    "FloVent_Gen": DrugInfo(
        prescriptionName="generic",
        activeIngredient="Fluticasone Propionate",
        dosage=0.11,
        price=88.00
    )
}

@tool
def getDrugsInfo() -> List[DrugInfo]:
    """
    You are a database tool. You return all drugs offered by the pharmacy
    Input: none
    Output:
        All drugs offered by the pharmacy in a list
    """
    
    return list(drugMap.values())

initPrompt = SystemMessage(
    content= (
        "You are a Pharmacy Benefits Negotiator negotiating with an insurance provider. "
        "Your goal is to maximize revenue by protecting your margins on both brand and generic options, only conceding price in small increments if the buyer is highly persistent."
        "\n\nCRITICAL RULES:\n"
        "1. Opening Offer: You MUST pitch the exact 'Brand Name Option' provided in your data window. Calculate your opening quote by multiplying its specific 'Price' by exactly 1.10 (a strict 10% markup).\n"
        "2. Brand Concession Scale: If the buyer is persistent and repeatedly rejects your brand price, concede ground slowly on the brand-name item in steps:\n"
        "   - Next Brand Counter: Drop to a 5% markup on the brand item (Brand Price * 1.05).\n"
        "   - Final Brand Counter: Drop to the exact baseline 'Brand Price' (0% markup).\n"
        "3. Value Capturing: If the buyer states a specific maximum budget, attempt to match your counter-offer directly to or just below their stated budget using whichever product tier yields higher revenue, provided it stays above your absolute floors.\n"
        "4. Generic Pivot: If the buyer explicitly rejects the baseline brand price, or if their stated budget is strictly below the brand price, pivot to the 'Generic Option'. \n"
        "5. Generic Concession Scale: Do not give away the generic floor immediately. Just like the brand, apply a markup and step-down strategy to the generic tier:\n"
        "   - Initial Generic Offer: Quote the generic 'Price' multiplied by exactly 1.10 (a 10% markup on the generic).\n"
        "   - Persistent Generic Counter: If they push back further, drop to a 5% markup on the generic item (Generic Price * 1.05).\n"
        "   - Absolute Baseline Floor: Your final concession is the exact baseline 'Generic Option' price (0% markup). Never under any circumstance quote a price lower than this baseline floor.\n"
        "6. Agreement: If they accept an offer, reply exactly with: 'AGREED: [Medication Name] at $[Price]'.\n\n"
        "Keep your replies highly professional, firm, and brief (1-2 sentences)."
        "Be intelligent and negotiate as a human would. Do not give any more information to the client than is necessary"
    )
)
llm = ChatOpenAI(temperature=0.5, model='gpt-5.4')
threadID = f"pbm-{uuid.uuid4().hex[:8]}"
mem = InMemorySaver()
mem.delete_thread(threadID)
Pbm = create_agent(
    model=llm, 
    tools=[getDrugsInfo],
    system_prompt=initPrompt,
    checkpointer=mem
)

@app.route("/negotiate", methods=["POST"])
def negotiate():
    print(f"\033[31m[Thread ID]: {threadID}\033[31m")
    data = request.get_json()
    providerMsg = data.get("message", "")
    drug = data.get("drug")
    
    print(f"\033[34m[Buyer]: {providerMsg}\033[0m")
    agentInput = (
        f"TARGET TRANSACTION DRUG KEY: {drug}\n"
        f"Buyer Message: {providerMsg}"
    )
    response = Pbm.invoke(
        {"messages": [{"role": "user", "content": agentInput}]},
        config={"configurable": {"thread_id": threadID}}
    )
    
    seller_reply = response["messages"][-1].content
    print(f"\033[32m[Seller]: {seller_reply}\033[0m")
    
    return jsonify({"reply": seller_reply})

if __name__ == "__main__":
    print("Running PBM Server...")
    app.run(host="127.0.0.1", port=8002, debug=True)



