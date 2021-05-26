
CREATE TABLE Sample (
    id INT PRIMARY KEY NOT NULL ,
    name VARCHAR NULL,
    FOREIGN KEY (team_id) 
        REFERENCES Team (team_id)
    
);
