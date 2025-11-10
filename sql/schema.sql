-- Create database
CREATE DATABASE IF NOT EXISTS gpu_dashboard;
USE gpu_dashboard;

-- Create video_cards table
CREATE TABLE IF NOT EXISTS video_cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tpu_model_name VARCHAR(255) NOT NULL,
    vram VARCHAR(50),
    memory_type VARCHAR(50),
    bus_interface VARCHAR(50),
    passmark_g3d_score INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Add index for better query performance
CREATE INDEX idx_tpu_model_name ON video_cards(tpu_model_name);
CREATE INDEX idx_passmark_score ON video_cards(passmark_g3d_score);