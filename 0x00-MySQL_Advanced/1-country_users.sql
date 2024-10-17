-- 3 first students in the Batch ID=3
-- because Batch 3 is the besti!
CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    country enum('US', 'CO', 'TN') NOT NULL DEFAULT 'US',
);

