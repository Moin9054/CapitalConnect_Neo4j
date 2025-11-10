# 🌍 CapitalConnect_Neo4j  

> **A Neo4j Graph Project** connecting and visualizing **capital cities** across  
> 🌍 *Europe*, 🌏 *Southeast Asia*, and 🌏 *South Asia*.  
>  
> This project builds a **city connection graph**, showing how capitals are linked geographically by distance based on `ROUTE` relationships ideal for showcasing data visualization skills.

---

## 🧩 Project Overview

CapitalConnect_Neo4j demonstrates how graph databases can represent **real world geographic networks**.  
It fetches live country data, builds a structured CSV, and imports it into **Neo4j AuraDB**.

---

## 📁 Folder Structure
```
CapitalConnect_Neo4j/
├── fetch_capitals.py 
├── import_into_neo4j.py 
├── demo_queries.cypher 
├── requirements.txt 
├── .env 
├── data/
│ └── cities_capitals.csv 
└── output/
└── graph_preview.png 
```

---

## ✨ Key Features

✅ Fetches **real capital data** using the RestCountries API  
✅ Automatically calculate **routes between cities within 1200 km**  
✅ PRE made **Cypher demo queries** for tables and graph visualization  
✅ Works on **Neo4j Aura** (cloud).
✅ Fully reproducible & customizable.

---

## ⚙️ Setup Instructions

### 1️⃣ Clone or open the project folder
```bash
cd CapitalConnect_Neo4j
```

### 2️⃣ Create & activate virtual environment
```
Windows
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1

macOS / Linux / WSL
python -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install dependencies
```
pip install -r requirements.txt
```

### 4️⃣ Add your Neo4j credentials to .env
```
NEO4J_URI=neo4j+s://<your-aura-id>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<your-password>
NEO4J_DATABASE=neo4j
```

### 🚀 Quick Run
```
python fetch_capitals.py
python import_into_neo4j.py
```

## 🎯 This will:

> Fetch capital data for Europe + Southeast Asia + South Asia

> Write it to data/cities_capitals_europe_seasia.csv

> Create nodes & routes in your Neo4j database