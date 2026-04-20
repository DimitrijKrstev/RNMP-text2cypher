CREATE OR REPLACE TABLE users (
    Id BIGINT PRIMARY KEY,
    AccountId DOUBLE,
    DisplayName VARCHAR,
    Location VARCHAR,
    ProfileImageUrl DOUBLE,
    WebsiteUrl VARCHAR,
    AboutMe VARCHAR,
    CreationDate TIMESTAMP
);

CREATE OR REPLACE TABLE badges (
    Id BIGINT PRIMARY KEY,
    UserId BIGINT,
    Class BIGINT,
    Name VARCHAR,
    TagBased BOOLEAN,
    Date TIMESTAMP,
    FOREIGN KEY (UserId) REFERENCES users(Id)
);

CREATE OR REPLACE TABLE posts (
    Id BIGINT PRIMARY KEY,
    OwnerUserId BIGINT,
    PostTypeId BIGINT,
    AcceptedAnswerId BIGINT,
    ParentId BIGINT,
    OwnerDisplayName VARCHAR,
    Title VARCHAR,
    Tags VARCHAR,
    ContentLicense VARCHAR,
    Body VARCHAR,
    CreationDate TIMESTAMP,
    FOREIGN KEY (OwnerUserId) REFERENCES users(Id)
);

CREATE OR REPLACE TABLE comments (
    Id BIGINT PRIMARY KEY,
    PostId BIGINT,
    UserId BIGINT,
    ContentLicense VARCHAR,
    UserDisplayName VARCHAR,
    Text VARCHAR,
    CreationDate TIMESTAMP,
    FOREIGN KEY (UserId) REFERENCES users(Id),
    FOREIGN KEY (PostId) REFERENCES posts(Id)
);

CREATE OR REPLACE TABLE postHistory (
    Id BIGINT PRIMARY KEY,
    PostId BIGINT,
    UserId BIGINT,
    PostHistoryTypeId BIGINT,
    UserDisplayName VARCHAR,
    ContentLicense VARCHAR,
    RevisionGUID VARCHAR,
    Text VARCHAR,
    Comment VARCHAR,
    CreationDate TIMESTAMP,
    FOREIGN KEY (PostId) REFERENCES posts(Id),
    FOREIGN KEY (UserId) REFERENCES users(Id)
);

CREATE OR REPLACE TABLE postLinks (
    Id BIGINT PRIMARY KEY,
    RelatedPostId BIGINT,
    PostId BIGINT,
    LinkTypeId BIGINT,
    CreationDate TIMESTAMP,
    FOREIGN KEY (RelatedPostId) REFERENCES posts(Id),
    FOREIGN KEY (PostId) REFERENCES posts(Id)
);

CREATE OR REPLACE TABLE votes (
    Id BIGINT PRIMARY KEY,
    UserId BIGINT,
    PostId BIGINT,
    VoteTypeId BIGINT,
    CreationDate TIMESTAMP,
    FOREIGN KEY (PostId) REFERENCES posts(Id),
    FOREIGN KEY (UserId) REFERENCES users(Id)
);