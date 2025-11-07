// demo_queries.cypher

// 1) Indexes / constraints
CREATE CONSTRAINT city_unique IF NOT EXISTS FOR (c:City) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT country_unique IF NOT EXISTS FOR (c:Country) REQUIRE c.name IS UNIQUE;

// 2) (Optional) LOAD CSV example if you hosted CSV on GitHub (replace URL)
// LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/<user>/<repo>/main/cities_capitals_europe_seasia.csv' AS row
// MERGE (co:Country {name: row.country})
// MERGE (ci:City {name: row.city})
// SET ci.latitude = toFloat(row.lat), ci.longitude = toFloat(row.lon), ci.region = row.region
// MERGE (co)-[:HAS_CITY]->(ci);

// 3) Create ROUTE relationships (if you didn't run import script)
WITH 1200 AS D
MATCH (a:City),(b:City)
WHERE a.name <> b.name AND id(a) < id(b)
AND exists(a.latitude) AND exists(b.latitude)
WITH a,b,
  2 * 6371 * asin( sqrt(
    sin(radians((a.latitude - b.latitude)/2))^2 +
    cos(radians(a.latitude)) * cos(radians(b.latitude)) *
    sin(radians((a.longitude - b.longitude)/2))^2
  )) AS km
WHERE km <= D
MERGE (a)-[r:ROUTE]->(b)
  SET r.distance = round(km,1), r.travel_time_hours = round(round(km,1)/80.0,2)
MERGE (b)-[r2:ROUTE]->(a)
  SET r2.distance = round(km,1), r2.travel_time_hours = round(round(km,1)/80.0,2);

// 4) Demo queries
// Unweighted shortest path (min hops)
MATCH (start:City {name:'Paris'}), (end:City {name:'Bangkok'})
MATCH p = shortestPath((start)-[:ROUTE*]-(end))
RETURN p, reduce(total = 0, r IN relationships(p) | total + r.distance) AS totalDistance;

// Weighted shortest path using GDS Dijkstra (if GDS available)
CALL gds.graph.project('routesGraph','City',{ROUTE:{properties:['distance']}});
MATCH (s:City {name:'Paris'}), (t:City {name:'Bangkok'})
CALL gds.shortestPath.dijkstra.stream('routesGraph', {
  sourceNode: id(s),
  targetNode: id(t),
  relationshipWeightProperty: 'distance'
})
YIELD nodeIds, cost
RETURN [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS path, cost;

// Reachable cities within cumulative distance
MATCH (start:City {name:'Paris'})
MATCH p = (start)-[:ROUTE*1..4]->(c:City)
WITH c, start, p, reduce(total=0, r IN relationships(p) | total + r.distance) AS dist
WHERE dist <= 1500
RETURN DISTINCT c.name AS city, dist ORDER BY dist ASC;

// Hubs (degree)
MATCH (c:City)
RETURN c.name, size((c)--()) AS degree
ORDER BY degree DESC LIMIT 10;

// Alternative routes sorted by distance (top 5)
MATCH (s:City {name:'Paris'}), (t:City {name:'Bangkok'})
MATCH p = (s)-[:ROUTE*1..6]-(t)
WITH p, reduce(total=0, r IN relationships(p) | total + r.distance) AS totalDist
RETURN [n IN nodes(p) | n.name] AS path, totalDist
ORDER BY totalDist ASC LIMIT 5;