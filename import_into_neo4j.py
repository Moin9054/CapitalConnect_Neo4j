"""
import_into_neo4j.py
- Reads cities_capitals_europe_seasia.csv
- Upserts Country and City nodes and HAS_CITY relationships
- Creates ROUTE relationships between capitals within DISTANCE_THRESHOLD_KM using Haversine
- Attempts to create a GDS projection (safe/optional)

Usage:
  pip install neo4j
  Set env vars NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD or provide at prompt.
  python import_into_neo4j.py
"""

import os
import csv
from getpass import getpass
from neo4j import GraphDatabase
from dotenv import load_dotenv 

load_dotenv() 

CSV_PATH = "data/cities_capitals_europe_seasia.csv"  
DISTANCE_THRESHOLD_KM = 1200
BATCH_SIZE = 100


def upsert_batch(tx, batch):
    tx.run("""
    UNWIND $rows AS row
    MERGE (co:Country {name: row.country})
      ON CREATE SET co.created = timestamp()
    MERGE (ci:City {name: row.city})
      ON CREATE SET ci.latitude = row.lat, ci.longitude = row.lon, ci.region = row.region
      ON MATCH SET ci.latitude = coalesce(row.lat, ci.latitude), ci.longitude = coalesce(row.lon, ci.longitude), ci.region = coalesce(row.region, ci.region)
    MERGE (co)-[:HAS_CITY]->(ci)
    """, rows=batch)


def import_data_and_create_routes(uri, user, password, csv_path, distance_threshold_km):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        print("Creating constraints (if not exists)...")
        session.run("CREATE CONSTRAINT city_unique IF NOT EXISTS FOR (c:City) REQUIRE c.name IS UNIQUE")
        session.run("CREATE CONSTRAINT country_unique IF NOT EXISTS FOR (c:Country) REQUIRE c.name IS UNIQUE")

        print("Reading CSV and upserting nodes...")
        batch = []
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lat = None
                lon = None
                try:
                    lat = float(row['lat']) if row['lat'] not in (None, '', 'None') else None
                    lon = float(row['lon']) if row['lon'] not in (None, '', 'None') else None
                except:
                    lat = None; lon = None
                batch.append({
                    "country": row['country'],
                    "city": row['city'],
                    "lat": lat,
                    "lon": lon,
                    "region": row['region']
                })
                if len(batch) >= BATCH_SIZE:
                    # use execute_write for neo4j python driver v5+
                    session.execute_write(upsert_batch, batch)
                    batch = []
            if batch:
                session.execute_write(upsert_batch, batch)
        print("Nodes imported. Now creating ROUTE relationships...")

        create_routes_cypher = f"""
        WITH {distance_threshold_km} AS D
        MATCH (a:City),(b:City)
        WHERE a.name <> b.name AND id(a) < id(b)
        AND a.latitude IS NOT NULL AND b.latitude IS NOT NULL
        WITH a,b,
        2 * 6371 * asin( sqrt(
            sin(radians((a.latitude - b.latitude)/2))^2 +
            cos(radians(a.latitude)) * cos(radians(b.latitude)) *
            sin(radians((a.longitude - b.longitude)/2))^2
        )) AS km
        WHERE km <= D
        MERGE (a)-[r:ROUTE]->(b)
        SET r.distance = round(km,1),
            r.travel_time_hours = round(round(km,1)/80.0,2)
        MERGE (b)-[r2:ROUTE]->(a)
        SET r2.distance = round(km,1),
            r2.travel_time_hours = round(round(km,1)/80.0,2);
        """
        session.run(create_routes_cypher)
        print("ROUTE relationships created.")

        # Attempt to drop previous projection (safe)
        try:
            session.run("CALL gds.graph.drop('routesGraph') YIELD graphName")
        except Exception:
            pass

        # Try to create GDS projection — wrapped so script won't crash if GDS isn't available
        try:
            session.run("""
            CALL gds.graph.project(
              'routesGraph',
              'City',
              { ROUTE: {properties: ['distance']} }
            )
            """)
            print("GDS projection 'routesGraph' created (if GDS installed).")
        except Exception:
            print("GDS not available or projection failed. That's fine for the demo.")

    driver.close()


if __name__ == '__main__':
    uri = os.getenv("NEO4J_URI") or input("Neo4j URI (neo4j+s://...): ").strip()
    user = os.getenv("NEO4J_USERNAME") or input("Neo4j username: ").strip()
    password = os.getenv("NEO4J_PASSWORD") or getpass("Neo4j password: ")

    import_data_and_create_routes(uri, user, password, CSV_PATH, DISTANCE_THRESHOLD_KM)
    print('Done. Open demo_queries.cypher to run demo queries in your DB or open Aura Browser.')
