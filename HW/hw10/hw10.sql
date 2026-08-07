CREATE TABLE parents AS
  SELECT "ace" AS parent, "bella" AS child UNION
  SELECT "ace"          , "charlie"        UNION
  SELECT "daisy"        , "hank"           UNION
  SELECT "finn"         , "ace"            UNION
  SELECT "finn"         , "daisy"          UNION
  SELECT "finn"         , "ginger"         UNION
  SELECT "ellie"        , "finn";

CREATE TABLE dogs AS
  SELECT "ace" AS name, "long" AS fur, 26 AS height UNION
  SELECT "bella"      , "short"      , 52           UNION
  SELECT "charlie"    , "long"       , 47           UNION
  SELECT "daisy"      , "long"       , 46           UNION
  SELECT "ellie"      , "short"      , 35           UNION
  SELECT "finn"       , "curly"      , 32           UNION
  SELECT "ginger"     , "short"      , 28           UNION
  SELECT "hank"       , "curly"      , 31;

CREATE TABLE sizes AS
  SELECT "toy" AS size, 24 AS min, 28 AS max UNION
  SELECT "mini"       , 28       , 35        UNION
  SELECT "medium"     , 35       , 45        UNION
  SELECT "standard"   , 45       , 60;


-- All dogs with parents ordered by decreasing height of their parent
CREATE TABLE by_parent_height AS
  SELECT a.name AS chil from dogs AS a, parents AS b, dogs AS c WHERE a.name = b.child AND b.parent = c.name ORDER BY c.height DESC;


-- The size of each dog
CREATE TABLE size_of_dogs AS
  SELECT name, size from dogs, sizes WHERE height > min AND height <= max ORDER BY name;


-- [Optional] Filling out this helper table is recommended
CREATE TABLE siblings AS
  SELECT a.name AS one, c.child AS two FROM dogs AS a, parents AS b, parents AS c WHERE a.name = b.child AND b.parent = c.parent AND c.child > a.name;

-- Sentences about siblings that are the same size
CREATE TABLE sentences AS
  SELECT "The two siblings, " || a.one || " and " || a.two || ", have the same size: " || b.size FROM siblings AS a, size_of_dogs AS b, size_of_dogs AS c
    WHERE a.one = b.name AND a.two = c.name AND b.size = c.size;


-- Height range for each fur type where all of the heights differ by no more than 30% from the average height
CREATE TABLE low_variance AS
  SELECT fur, MAX(height) - MIN(height) as height_range FROM dogs
    GROUP BY fur HAVING MAX(height) <= 1.3 * AVG(height) AND MIN(height) >= 0.7 * AVG(height);

