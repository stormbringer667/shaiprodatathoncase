// Indexes and constraints
CREATE INDEX ip_index IF NOT EXISTS FOR (n:IP) ON (n.address);
CREATE INDEX asset_index IF NOT EXISTS FOR (n:Asset) ON (n.hostname);
CREATE INDEX user_index IF NOT EXISTS FOR (n:User) ON (n.username);
CREATE INDEX attack_index IF NOT EXISTS FOR (n:Attack) ON (n.technique_id);

CREATE CONSTRAINT ip_unique IF NOT EXISTS FOR (n:IP)     REQUIRE n.address  IS UNIQUE;
CREATE CONSTRAINT asset_unique IF NOT EXISTS FOR (n:Asset) REQUIRE n.asset_id IS UNIQUE;

// Demo topology (WARNING: this deletes all nodes/rels in the DB)
/*
MATCH (n) DETACH DELETE n;
CREATE (subnet1:Subnet {name: 'DMZ', cidr: '192.168.1.0/24'});
CREATE (subnet2:Subnet {name: 'Internal', cidr: '10.0.0.0/16'});
CREATE (fw:Firewall {name: 'PaloAlto-Main', model: 'PA-5220'});
CREATE (honeypot:Honeypot {name: 'Cowrie-01', type: 'SSH'});
CREATE (subnet1)-[:PROTECTED_BY]->(fw);
CREATE (subnet2)-[:PROTECTED_BY]->(fw);
CREATE (honeypot)-[:DEPLOYED_IN]->(subnet1);
*/
