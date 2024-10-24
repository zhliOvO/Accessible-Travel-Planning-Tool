-- INSERT INTO Users (username, disability_type) VALUES
-- ('john', 'Wheelchair user'),
-- ('daniel', 'Visual impairment'),
-- ('daisy', 'Hearing impairment');

INSERT INTO Hotels (hotel_name, postal_code, country, phone_number) VALUES
('Sunset Resort', '12345', 'USA', '123-456-7890'),
('Mountain Inn', '54321', 'Canada', '234-567-8901'),
('Ocean Breeze Hotel', '23456', 'USA', '345-678-9012'),
('City Comfort Hotel', '65432', 'UK', '456-789-0123'),
('Desert Escape Lodge', '34567', 'Australia', '567-890-1234');

INSERT INTO AccessibilityFeatures (disability_type, feature_name) VALUES
('Wheelchair user', 'Wheelchair ramp'),
('Wheelchair user', 'Accessible bathroom'),
('Visual impairment', 'Braille signage'),
('Hearing impairment', 'Hearing loops'),
('Visual impairment', 'Tactile flooring');

INSERT INTO HotelAccessibility (hotel_id, feature_id) VALUES
(1, 1),
(1, 2),
(2, 3),
(3, 4),
(4, 5),
(5, 1),
(5, 3);
