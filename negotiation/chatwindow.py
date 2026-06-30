from flask import Flask, request, jsonify
import requests
SELLER_URL = "http://127.0.0.1:8002/negotiate"

while True:
    user_input = input("Enter something (type 'exit' to quit): ").strip().lower()

    if user_input == "exit":
        print("Goodbye!")
        break
    
    res = requests.post(SELLER_URL, json={"message": user_input, "drug": "ProAir"})
    print(res.json()["reply"])
        
    