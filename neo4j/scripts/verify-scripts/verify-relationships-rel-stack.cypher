// 1. Summary
MATCH (n) RETURN labels(n)[0] AS node, count(*) AS cnt ORDER BY node;
MATCH ()-[r]->() RETURN type(r) AS rel, count(*) AS cnt ORDER BY rel;

// 2. Orphaned nodes
MATCH (n) WHERE NOT (n)--()
RETURN labels(n)[0] AS orphanType, count(*) AS cnt;

// 3. Referential integrity violations (each should be 0)
RETURN
  count { MATCH (c:comments)
          WHERE NOT EXISTS { MATCH (p:posts {Id:c.PostId}) } }      AS comments_without_post,
  count { MATCH (c:comments)
          WHERE NOT EXISTS { MATCH (u:users {Id:c.UserId}) } }      AS comments_without_user,
  count { MATCH (v:votes)
          WHERE NOT EXISTS { MATCH (p:posts {Id:v.PostId}) } }      AS votes_without_post,
  count { MATCH (v:votes)
          WHERE NOT EXISTS { MATCH (u:users {Id:v.UserId}) } }      AS votes_without_user,
  count { MATCH (b:badges)
          WHERE NOT EXISTS { MATCH (u:users {Id:b.UserId}) } }      AS badges_without_user,
  count { MATCH (ph:postHistory)
          WHERE NOT EXISTS { MATCH (p:posts {Id:ph.PostId}) } }     AS postHistory_without_post,
  count { MATCH (pl:postLinks)
          WHERE NOT EXISTS { MATCH (p:posts {Id:pl.PostId}) } }     AS postLinks_without_post;

// 4. Relationship density
MATCH (u:users)-[:OWNS]->(p:posts)
WITH count(p) AS totalPosts, count(DISTINCT u) AS totalUsers
RETURN totalUsers,
       totalPosts,
       round(1.0*totalPosts/totalUsers,1) AS avgPostsPerUser;