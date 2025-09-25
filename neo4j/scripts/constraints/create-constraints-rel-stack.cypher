// Pimrary key Constraints

CREATE CONSTRAINT postLinks_pk IF NOT EXISTS FOR (n:postLinks) REQUIRE n.Id IS UNIQUE;
CREATE CONSTRAINT posts_pk IF NOT EXISTS FOR (n:posts) REQUIRE n.Id IS UNIQUE;
CREATE CONSTRAINT users_pk IF NOT EXISTS FOR (n:users) REQUIRE n.Id IS UNIQUE;
CREATE CONSTRAINT comments_pk IF NOT EXISTS FOR (n:comments) REQUIRE n.Id IS UNIQUE;
CREATE CONSTRAINT postHistory_pk IF NOT EXISTS FOR (n:postHistory) REQUIRE n.Id IS UNIQUE;
CREATE CONSTRAINT votes_pk IF NOT EXISTS FOR (n:votes) REQUIRE n.Id IS UNIQUE;
CREATE CONSTRAINT badges_pk IF NOT EXISTS FOR (n:badges) REQUIRE n.Id IS UNIQUE;

// Foreign key Constraints

CREATE INDEX post_link_post_fk      IF NOT EXISTS  FOR (n:postLinks)               ON (n.PostId);
CREATE INDEX related_post_link_post_fk      IF NOT EXISTS  FOR (n:postLinks)               ON (n.RelatedPostId);

CREATE INDEX comments_post_fk      IF NOT EXISTS  FOR (n:comments)               ON (n.PostId);
CREATE INDEX comments_user_fk      IF NOT EXISTS  FOR (n:comments)               ON (n.UserId);

CREATE INDEX post_history_post_fk      IF NOT EXISTS  FOR (n:postHistory)               ON (n.PostId);
CREATE INDEX post_history_user_fk      IF NOT EXISTS  FOR (n:postHistory)               ON (n.UserId);

CREATE INDEX badges_user_fk      IF NOT EXISTS  FOR (n:badges)               ON (n.UserId);

CREATE INDEX votes_posts_fk      IF NOT EXISTS  FOR (n:votes)               ON (n.PostId);
CREATE INDEX votes_users_fk      IF NOT EXISTS  FOR (n:votes)               ON (n.UserId);

CREATE INDEX posts_owner_userId_fk      IF NOT EXISTS  FOR (n:posts)               ON (n.OwnerUserId);
CREATE INDEX posts_parentId_fk      IF NOT EXISTS  FOR (n:posts)               ON (n.ParentId);
CREATE INDEX posts_accepted_answers_fk      IF NOT EXISTS  FOR (n:posts)               ON (n.AcceptedAnswerId);
