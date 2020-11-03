CREATE TABLE uploads (
  id SERIAL,
  temp_name VARCHAR(32) UNIQUE,
  original_s3 VARCHAR(64) UNIQUE,
  result_s3 VARCHAR(64) UNIQUE,
  created_at TIMESTAMP DEFAULT now() NOT NULL
);
