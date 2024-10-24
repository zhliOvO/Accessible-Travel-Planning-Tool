-- CREATE TABLE Users (
--     user_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     username VARCHAR(100) NOT NULL UNIQUE,
--     disability_type VARCHAR(100)
-- );

CREATE TABLE Hotels (
    hotel_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_name VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    country VARCHAR(100),
    phone_number VARCHAR(15)
);

CREATE TABLE AccessibilityFeatures (
    feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
    disability_type VARCHAR(100),
    feature_name VARCHAR(100) NOT NULL
);

CREATE TABLE HotelAccessibility (
    hotel_id INTEGER,
    feature_id INTEGER,
    FOREIGN KEY (hotel_id) REFERENCES Hotels(hotel_id) ON DELETE CASCADE,
    FOREIGN KEY (feature_id) REFERENCES AccessibilityFeatures(feature_id) ON DELETE CASCADE,
    PRIMARY KEY (hotel_id, feature_id)
);
