MATCH (p:posts)
WHERE p.score IS NOT NULL 
  AND (toInteger(p.score) < -100 OR toInteger(p.score) > 5000)
RETURN 'invalid_post_score' AS issue, count(*) AS cnt;

MATCH (u:users)
WHERE u.reputation IS NOT NULL
  AND (toInteger(u.reputation) < 1 OR toInteger(u.reputation) > 1000000)
RETURN 'invalid_reputation' AS issue, count(*) AS cnt;

MATCH (p:posts)
WHERE toInteger(substring(p.CreationDate, 0, 4)) < 2008 OR toInteger(substring(p.CreationDate, 0, 4)) > 2024
RETURN 'implausible_year' AS issue,
       count(*) AS cnt,
       min(toInteger(substring(p.CreationDate, 0, 4))) AS minYear,
       max(toInteger(substring(p.CreationDate, 0, 4))) AS maxYear;

MATCH (n:users)
WITH n.Id AS id, count(*) AS c WHERE c>1
RETURN 'dup_userId' AS issue, sum(c) AS cnt;

MATCH (n:posts)
WITH n.Id AS id, count(*) AS c WHERE c>1
RETURN 'dup_postId' AS issue, sum(c) AS cnt;

MATCH (n:comments)
WITH n.Id AS id, count(*) AS c WHERE c>1
RETURN 'dup_commentId' AS issue, sum(c) AS cnt;

MATCH (n:votes)
WITH n.Id AS id, count(*) AS c WHERE c>1
RETURN 'dup_voteId' AS issue, sum(c) AS cnt;

MATCH (n:badges)
WITH n.Id AS id, count(*) AS c WHERE c>1
RETURN 'dup_badgeId' AS issue, sum(c) AS cnt;

MATCH (n:postHistory)
WITH n.Id AS id, count(*) AS c WHERE c>1
RETURN 'dup_postHistoryId' AS issue, sum(c) AS cnt;

MATCH (n:postLinks)
WITH n.Id AS id, count(*) AS c WHERE c>1
RETURN 'dup_postLinkId' AS issue, sum(c) AS cnt;

MATCH (p:posts)
WHERE p.Title IS NULL
RETURN 'posts_missing_title' AS issue, count(*) AS cnt;

MATCH (p:posts)
WHERE p.CreationDate IS NULL
RETURN 'posts_missing_creation_date' AS issue, count(*) AS cnt;

MATCH (p:posts)
WHERE p.Id = p.ParentId
RETURN 'self_referencing_posts' AS issue, count(*) AS cnt;

MATCH (p:posts)
WHERE p.Id = p.AcceptedAnswerId
RETURN 'self_accepted_answer' AS issue, count(*) AS cnt;