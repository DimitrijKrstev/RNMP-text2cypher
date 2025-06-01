Working branch that on startupt loads the dataset with in-container cypher queries (work in progress),
specific to the dataset(F1).

 Starts with the command
 docker build -t f1-neo4j .
 docker run -p 7474:7474 -p 7687:7687 --name f1-neo4j f1-neo4j

 In case of error remove the previous neo4j container, even if not running i.e. remove the imagecl