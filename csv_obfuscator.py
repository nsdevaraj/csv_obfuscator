#!/usr/bin/env python3
"""
CSV Obfuscation Tool

This tool performs two types of obfuscation on CSV files:
1. Changes all numeric values to random values within a similar range
2. Replaces unique values in each column with meaningful English words in the same context

Usage:
    python csv_obfuscator.py input.csv output.csv [--seed SEED]

Arguments:
    input.csv   - Path to the input CSV file
    output.csv  - Path to the output CSV file
    --seed SEED - Optional random seed for reproducibility

"""

import argparse
import csv
import random
import sys
import math
import re
from collections import defaultdict

# Will be used to generate contextually relevant words for replacement
WORD_CATEGORIES = {
    'names': [
        'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 
        'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica', 
        'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa', 
        'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley', 
        'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle', 
        'Kenneth', 'Dorothy', 'Kevin', 'Carol', 'Brian', 'Amanda', 'George', 'Melissa',
        'Emma', 'Noah', 'Olivia', 'Liam', 'Ava', 'Ethan', 'Sophia', 'Lucas', 'Isabella', 'Mason'
    ],
    'countries': [
        'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Argentina', 'Armenia', 'Australia',
        'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium',
        'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria',
        'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Chad', 'Chile', 'China', 'Colombia',
        'Congo', 'Croatia', 'Cuba', 'Cyprus', 'Czechia', 'Denmark', 'Ecuador', 'Egypt', 'Estonia', 'Ethiopia',
        'Finland', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Guatemala', 'Haiti',
        'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy',
        'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kuwait', 'Laos', 'Latvia', 'Lebanon', 'Liberia',
        'Libya', 'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta',
        'Mexico', 'Moldova', 'Monaco', 'Mongolia', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nepal',
        'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Panama',
        'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda',
        'Saudi Arabia', 'Senegal', 'Serbia', 'Singapore', 'Slovakia', 'Slovenia', 'Somalia', 'South Africa',
        'South Korea', 'Spain', 'Sri Lanka', 'Sudan', 'Sweden', 'Switzerland', 'Syria', 'Taiwan', 'Tanzania',
        'Thailand', 'Togo', 'Tunisia', 'Turkey', 'Uganda', 'Ukraine', 'UAE', 'UK', 'USA', 'Uruguay',
        'Uzbekistan', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe'
    ],
    'cities': [
        'Tokyo', 'Delhi', 'Shanghai', 'São Paulo', 'Mexico City', 'Cairo', 'Mumbai', 'Beijing', 'Dhaka',
        'Osaka', 'New York', 'Karachi', 'Buenos Aires', 'Chongqing', 'Istanbul', 'Kolkata', 'Manila',
        'Lagos', 'Rio de Janeiro', 'Tianjin', 'Kinshasa', 'Guangzhou', 'Los Angeles', 'Moscow', 'Shenzhen',
        'Lahore', 'Bangalore', 'Paris', 'Bogotá', 'Jakarta', 'Chennai', 'Lima', 'Bangkok', 'Seoul',
        'Nagoya', 'Hyderabad', 'London', 'Tehran', 'Chicago', 'Chengdu', 'Nanjing', 'Wuhan', 'Ho Chi Minh City',
        'Luanda', 'Ahmedabad', 'Kuala Lumpur', 'Xian', 'Hong Kong', 'Dongguan', 'Hangzhou', 'Foshan',
        'Shenyang', 'Riyadh', 'Baghdad', 'Santiago', 'Surat', 'Madrid', 'Suzhou', 'Pune', 'Harbin',
        'Houston', 'Dallas', 'Toronto', 'Dar es Salaam', 'Miami', 'Belo Horizonte', 'Singapore', 'Philadelphia',
        'Atlanta', 'Fukuoka', 'Khartoum', 'Barcelona', 'Johannesburg', 'Saint Petersburg', 'Qingdao',
        'Dalian', 'Washington', 'Yangon', 'Alexandria', 'Jinan', 'Guadalajara'
    ],
    'companies': [
        'Acme', 'Globex', 'Umbrella', 'Cyberdyne', 'Wayne Enterprises', 'Stark Industries', 'Oscorp',
        'Aperture Science', 'Weyland-Yutani', 'Soylent', 'Massive Dynamic', 'Wonka Industries', 'Hooli',
        'Pied Piper', 'Dunder Mifflin', 'Sterling Cooper', 'Initech', 'Bluth Company', 'Gekko & Co',
        'Prestige Worldwide', 'Oceanic Airlines', 'Cyberdyne Systems', 'Tyrell Corporation', 'Nakatomi Trading',
        'Gringotts', 'Olivia Pope & Associates', 'Cheers', 'Krusty Krab', 'Los Pollos Hermanos', 'Waystar Royco',
        'Apple', 'Microsoft', 'Google', 'Amazon', 'Facebook', 'Tesla', 'Netflix', 'IBM', 'Intel', 'Oracle',
        'Samsung', 'Sony', 'Toyota', 'Honda', 'Ford', 'BMW', 'Volkswagen', 'Coca-Cola', 'Pepsi', 'Nike',
        'Adidas', 'Visa', 'Mastercard', 'JPMorgan', 'Goldman Sachs', 'Walmart', 'Target', 'Costco', 'Starbucks',
        'McDonalds', 'Subway', 'Disney', 'Warner Bros', 'Universal', 'Paramount', 'Spotify', 'Airbnb', 'Uber',
        'Lyft', 'Twitter', 'LinkedIn', 'Pinterest', 'Snapchat', 'Reddit', 'TikTok', 'Zoom', 'Slack', 'Dropbox',
        'Adobe', 'Salesforce', 'Cisco', 'Siemens', 'Shell', 'BP', 'ExxonMobil', 'Chevron', 'AT&T', 'Verizon',
        'T-Mobile', 'Comcast', 'FedEx', 'UPS', 'DHL', 'Pfizer', 'Johnson & Johnson', 'Novartis', 'Roche',
        'Nestle', 'Unilever', 'P&G', 'LOreal', 'LVMH', 'Nike', 'H&M', 'Zara', 'IKEA', 'Lego'
    ],
    'products': [
        'Smartphone', 'Laptop', 'Tablet', 'Desktop', 'Monitor', 'Keyboard', 'Mouse', 'Headphones',
        'Speaker', 'Microphone', 'Camera', 'Printer', 'Scanner', 'Router', 'Modem', 'Server', 'Storage',
        'Watch', 'Fitness Tracker', 'VR Headset', 'TV', 'Projector', 'Gaming Console', 'Drone', 'Robot',
        'Refrigerator', 'Freezer', 'Dishwasher', 'Washing Machine', 'Dryer', 'Microwave', 'Oven', 'Stove',
        'Blender', 'Mixer', 'Coffee Maker', 'Toaster', 'Air Conditioner', 'Fan', 'Heater', 'Air Purifier',
        'Vacuum', 'Iron', 'Hair Dryer', 'Electric Shaver', 'Electric Toothbrush', 'Massage Chair',
        'Treadmill', 'Exercise Bike', 'Rowing Machine', 'Weights', 'Yoga Mat', 'Basketball', 'Football',
        'Soccer Ball', 'Tennis Racket', 'Golf Club', 'Bicycle', 'Skateboard', 'Scooter', 'Kayak', 'Surfboard',
        'Tent', 'Sleeping Bag', 'Backpack', 'Suitcase', 'Wallet', 'Purse', 'Watch', 'Sunglasses', 'Umbrella',
        'Book', 'Magazine', 'Newspaper', 'Journal', 'Calendar', 'Pen', 'Pencil', 'Marker', 'Notebook',
        'Stapler', 'Scissors', 'Glue', 'Tape', 'Paper', 'Envelope', 'Folder', 'Binder', 'Chair', 'Table',
        'Desk', 'Bed', 'Sofa', 'Dresser', 'Bookshelf', 'Cabinet', 'Lamp', 'Clock', 'Mirror', 'Rug', 'Curtain'
    ],
    'colors': [
        'Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple', 'Pink', 'Brown', 'Black', 'White', 'Gray',
        'Cyan', 'Magenta', 'Lime', 'Olive', 'Navy', 'Teal', 'Maroon', 'Indigo', 'Turquoise', 'Violet',
        'Coral', 'Crimson', 'Gold', 'Silver', 'Bronze', 'Copper', 'Platinum', 'Ruby', 'Emerald', 'Sapphire',
        'Amber', 'Ivory', 'Lavender', 'Mint', 'Peach', 'Periwinkle', 'Salmon', 'Tan', 'Aqua', 'Beige',
        'Burgundy', 'Charcoal', 'Khaki', 'Mauve', 'Ochre', 'Rust', 'Slate', 'Umber', 'Vermilion'
    ],
    'animals': [
        'Dog', 'Cat', 'Bird', 'Fish', 'Horse', 'Cow', 'Pig', 'Sheep', 'Goat', 'Chicken', 'Duck', 'Rabbit',
        'Hamster', 'Guinea Pig', 'Mouse', 'Rat', 'Ferret', 'Hedgehog', 'Turtle', 'Snake', 'Lizard', 'Frog',
        'Toad', 'Salamander', 'Newt', 'Goldfish', 'Guppy', 'Betta', 'Angelfish', 'Parrot', 'Canary', 'Finch',
        'Budgie', 'Cockatiel', 'Cockatoo', 'Macaw', 'Lovebird', 'Dove', 'Pigeon', 'Sparrow', 'Robin', 'Eagle',
        'Hawk', 'Falcon', 'Owl', 'Penguin', 'Ostrich', 'Emu', 'Flamingo', 'Swan', 'Goose', 'Peacock', 'Turkey',
        'Lion', 'Tiger', 'Leopard', 'Jaguar', 'Cheetah', 'Cougar', 'Lynx', 'Wolf', 'Fox', 'Coyote', 'Hyena',
        'Bear', 'Panda', 'Koala', 'Kangaroo', 'Wallaby', 'Wombat', 'Platypus', 'Echidna', 'Opossum', 'Raccoon',
        'Skunk', 'Badger', 'Otter', 'Beaver', 'Squirrel', 'Chipmunk', 'Mole', 'Shrew', 'Bat', 'Monkey', 'Gorilla',
        'Chimpanzee', 'Orangutan', 'Baboon', 'Lemur', 'Elephant', 'Rhinoceros', 'Hippopotamus', 'Giraffe', 'Zebra',
        'Deer', 'Elk', 'Moose', 'Bison', 'Buffalo', 'Camel', 'Llama', 'Alpaca', 'Dolphin', 'Whale', 'Shark', 'Seal',
        'Walrus', 'Sea Lion', 'Manatee', 'Octopus', 'Squid', 'Crab', 'Lobster', 'Shrimp', 'Crayfish', 'Butterfly',
        'Moth', 'Dragonfly', 'Beetle', 'Ant', 'Bee', 'Wasp', 'Fly', 'Mosquito', 'Spider', 'Scorpion', 'Tick', 'Mite'
    ],
    'fruits': [
        'Apple', 'Banana', 'Orange', 'Grape', 'Strawberry', 'Blueberry', 'Raspberry', 'Blackberry', 'Cherry',
        'Peach', 'Pear', 'Plum', 'Apricot', 'Nectarine', 'Mango', 'Pineapple', 'Watermelon', 'Cantaloupe',
        'Honeydew', 'Kiwi', 'Papaya', 'Guava', 'Lychee', 'Passion Fruit', 'Dragon Fruit', 'Pomegranate',
        'Fig', 'Date', 'Coconut', 'Avocado', 'Lemon', 'Lime', 'Grapefruit', 'Tangerine', 'Clementine',
        'Mandarin', 'Persimmon', 'Quince', 'Cranberry', 'Gooseberry', 'Currant', 'Elderberry', 'Boysenberry',
        'Mulberry', 'Loganberry', 'Kiwano', 'Kumquat', 'Durian', 'Jackfruit', 'Breadfruit', 'Starfruit',
        'Rambutan', 'Mangosteen', 'Longan', 'Tamarind', 'Soursop', 'Cherimoya', 'Feijoa', 'Plantain'
    ],
    'vegetables': [
        'Carrot', 'Potato', 'Tomato', 'Onion', 'Garlic', 'Lettuce', 'Spinach', 'Kale', 'Cabbage', 'Broccoli',
        'Cauliflower', 'Asparagus', 'Celery', 'Cucumber', 'Zucchini', 'Eggplant', 'Pepper', 'Mushroom',
        'Corn', 'Pea', 'Bean', 'Lentil', 'Chickpea', 'Soybean', 'Pumpkin', 'Squash', 'Sweet Potato', 'Yam',
        'Turnip', 'Radish', 'Beet', 'Rutabaga', 'Parsnip', 'Artichoke', 'Brussels Sprout', 'Leek', 'Scallion',
        'Shallot', 'Bok Choy', 'Arugula', 'Endive', 'Radicchio', 'Watercress', 'Okra', 'Kohlrabi', 'Fennel',
        'Ginger', 'Turmeric', 'Horseradish', 'Jicama', 'Taro', 'Cassava', 'Plantain', 'Bamboo Shoot', 'Seaweed',
        'Chayote', 'Fiddlehead', 'Lotus Root', 'Water Chestnut', 'Rhubarb', 'Nopales', 'Salsify', 'Celeriac'
    ],
    'jobs': [
        'Doctor', 'Nurse', 'Teacher', 'Professor', 'Engineer', 'Architect', 'Lawyer', 'Judge', 'Accountant',
        'Banker', 'Financial Analyst', 'Manager', 'CEO', 'CFO', 'CTO', 'Director', 'Supervisor', 'Coordinator',
        'Administrator', 'Secretary', 'Receptionist', 'Clerk', 'Cashier', 'Salesperson', 'Marketer', 'PR Specialist',
        'Advertiser', 'Designer', 'Artist', 'Musician', 'Actor', 'Dancer', 'Singer', 'Writer', 'Editor', 'Journalist',
        'Reporter', 'Photographer', 'Videographer', 'Filmmaker', 'Producer', 'Director', 'Programmer', 'Developer',
        'System Administrator', 'Network Engineer', 'Database Administrator', 'Security Analyst', 'Data Scientist',
        'Researcher', 'Scientist', 'Biologist', 'Chemist', 'Physicist', 'Mathematician', 'Astronomer', 'Geologist',
        'Archaeologist', 'Anthropologist', 'Psychologist', 'Sociologist', 'Historian', 'Philosopher', 'Economist',
        'Political Scientist', 'Linguist', 'Translator', 'Interpreter', 'Pilot', 'Flight Attendant', 'Air Traffic Controller',
        'Sailor', 'Captain', 'Driver', 'Truck Driver', 'Taxi Driver', 'Bus Driver', 'Train Conductor', 'Mechanic',
        'Electrician', 'Plumber', 'Carpenter', 'Construction Worker', 'Miner', 'Farmer', 'Rancher', 'Fisherman',
        'Gardner', 'Landscaper', 'Florist', 'Chef', 'Cook', 'Baker', 'Butcher', 'Waiter', 'Bartender', 'Barista',
        'Housekeeper', 'Janitor', 'Cleaner', 'Tailor', 'Seamstress', 'Cobbler', 'Jeweler', 'Hairdresser', 'Barber',
        'Makeup Artist', 'Esthetician', 'Massage Therapist', 'Personal Trainer', 'Coach', 'Athlete', 'Referee',
        'Firefighter', 'Police Officer', 'Detective', 'Security Guard', 'Soldier', 'Military Officer', 'Paramedic',
        'EMT', 'Pharmacist', 'Dentist', 'Veterinarian', 'Zoologist', 'Botanist', 'Ecologist', 'Environmental Scientist',
        'Meteorologist', 'Oceanographer', 'Astronaut', 'Librarian', 'Archivist', 'Curator', 'Tour Guide', 'Travel Agent',
        'Real Estate Agent', 'Insurance Agent', 'Consultant', 'Social Worker', 'Counselor', 'Therapist', 'Clergy'
    ]
}

def detect_column_type(values):
    """
    Attempt to determine the semantic type of a column based on its values.
    Returns a category from WORD_CATEGORIES that best matches the column.
    """
    # Convert all values to strings for analysis
    str_values = [str(v).strip() for v in values if v]
    
    if not str_values:
        return 'names'  # Default if no values
    
    # Check if values are mostly numeric
    numeric_count = sum(1 for v in str_values if re.match(r'^-?\d+(\.\d+)?$', v))
    if numeric_count / len(str_values) > 0.7:
        return 'products'  # Use products for numeric columns
    
    # Look for patterns in the data
    # Names are typically shorter
    if all(len(v.split()) <= 2 for v in str_values) and max(len(v) for v in str_values) < 20:
        return 'names'
    
    # Countries are typically single words or few words
    if all(len(v.split()) <= 3 for v in str_values):
        return 'countries'
    
    # Check for email patterns
    if any('@' in v for v in str_values):
        return 'names'  # Use names for email prefixes
    
    # Check for date-like patterns
    date_pattern = re.compile(r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}')
    if any(date_pattern.search(v) for v in str_values):
        return 'fruits'  # Use fruits for dates
    
    # Check for currency-like patterns
    currency_pattern = re.compile(r'[$€£¥]')
    if any(currency_pattern.search(v) for v in str_values):
        return 'products'  # Use products for currency
    
    # Check for address-like patterns
    if any(re.search(r'\b(street|st|avenue|ave|road|rd|boulevard|blvd)\b', v, re.I) for v in str_values):
        return 'cities'
    
    # Default categories based on average length
    avg_len = sum(len(v) for v in str_values) / len(str_values)
    if avg_len < 10:
        return 'colors'
    elif avg_len < 15:
        return 'animals'
    elif avg_len < 20:
        return 'fruits'
    elif avg_len < 30:
        return 'companies'
    else:
        return 'jobs'

def is_numeric(value):
    """Check if a value is numeric."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def randomize_numeric_value(value, variation_percent=20):
    """
    Randomize a numeric value within a specified percentage range.
    
    Args:
        value: The original numeric value
        variation_percent: The percentage range for variation (default 20%)
        
    Returns:
        A randomized value within the specified range
    """
    try:
        num_value = float(value)
        # Determine if the original value is an integer
        is_int = isinstance(value, int) or (isinstance(value, str) and value.isdigit())
        
        # Calculate the variation range
        variation = abs(num_value) * (variation_percent / 100)
        
        # Special handling for small numbers
        if abs(num_value) < 0.1:
            variation = max(variation, 0.01)
        
        # Generate a random value within the range
        min_val = num_value - variation
        max_val = num_value + variation
        
        # Ensure we don't flip signs unless the original value is close to zero
        if num_value > 0 and min_val < 0 and num_value > 0.1:
            min_val = 0
        elif num_value < 0 and max_val > 0 and num_value < -0.1:
            max_val = 0
            
        randomized = random.uniform(min_val, max_val)
        
        # Return as integer if the original was an integer
        if is_int:
            return int(round(randomized))
        else:
            # Preserve original precision
            original_str = str(value)
            if '.' in original_str:
                decimal_places = len(original_str.split('.')[1])
                return round(randomized, decimal_places)
            return randomized
    except (ValueError, TypeError):
        # Return the original value if it's not numeric
        return value

def is_date_column(values):
    """
    Check if a column appears to contain date values.
    
    Args:
        values: List of values to check
        
    Returns:
        True if the column appears to contain dates, False otherwise
    """
    # Common date patterns
    date_patterns = [
        r'\d{1,4}[-/\.]\d{1,2}[-/\.]\d{1,4}',  # YYYY-MM-DD, DD-MM-YYYY, etc.
        r'\d{1,2}[-/\s][A-Za-z]{3,9}[-/\s]\d{2,4}',  # DD Month YYYY
        r'[A-Za-z]{3,9}[-/\s]\d{1,2}[-/\s]\d{2,4}'   # Month DD YYYY
    ]
    
    # Count matches for date patterns
    date_count = 0
    non_empty_values = [str(v).strip() for v in values if v is not None and v != '']
    
    if not non_empty_values:
        return False
    
    for value in non_empty_values:
        for pattern in date_patterns:
            if re.search(pattern, value):
                date_count += 1
                break
    
    # If more than 70% of non-empty values match date patterns, consider it a date column
    return date_count / max(1, len(non_empty_values)) > 0.7

def is_boolean_column(values):
    """
    Check if a column appears to contain boolean values (with fewer than 3 unique values).
    
    Args:
        values: List of values to check
        
    Returns:
        True if the column appears to be boolean, False otherwise
    """
    # Get unique non-empty values
    non_empty_values = [str(v).strip().lower() for v in values if v is not None and v != '']
    
    if not non_empty_values:
        return False
    
    # Check if there are fewer than 3 unique values
    unique_values = set(non_empty_values)
    
    if len(unique_values) < 3:
        # Common boolean-like values
        boolean_pairs = [
            {'true', 'false'},
            {'yes', 'no'},
            {'y', 'n'},
            {'1', '0'},
            {'on', 'off'},
            {'active', 'inactive'},
            {'enabled', 'disabled'},
            {'t', 'f'}
        ]
        
        # Check if unique values match common boolean patterns
        lowercase_unique = {v.lower() for v in unique_values}
        for pair in boolean_pairs:
            if lowercase_unique.issubset(pair):
                return True
        
        # If not matching common patterns but still fewer than 3 values, consider it boolean-like
        return True
    
    return False

def replace_unique_values(data):
    """
    Replace unique values in each column with meaningful English words.
    Preserves date columns and boolean columns with fewer than 3 unique values.
    
    Args:
        data: A list of lists representing the CSV data
        
    Returns:
        The data with unique values replaced
    """
    if not data:
        return data
    
    # Transpose the data to work with columns
    columns = list(zip(*data))
    replaced_columns = []
    
    for col_idx, column in enumerate(columns):
        # Find unique values in this column
        non_empty_values = [v for v in column if v is not None and v != '']
        
        # Skip replacement if the column is mostly numeric
        numeric_count = sum(1 for v in non_empty_values if is_numeric(v))
        if numeric_count / max(1, len(non_empty_values)) > 0.7:
            replaced_columns.append(column)
            continue
        
        # Skip replacement if the column contains dates
        if is_date_column(column):
            replaced_columns.append(column)
            continue
        
        # Skip replacement if the column is boolean-like with fewer than 3 unique values
        if is_boolean_column(column):
            replaced_columns.append(column)
            continue
            
        # Determine the best category for this column
        category = detect_column_type(non_empty_values)
        word_list = WORD_CATEGORIES[category]
        
        # Create mapping for unique values
        unique_non_empty = set(non_empty_values)
        if len(unique_non_empty) > len(word_list):
            # If we have more unique values than words, we'll cycle through the word list
            word_mapping = {}
            for i, value in enumerate(unique_non_empty):
                word_mapping[value] = word_list[i % len(word_list)]
        else:
            # Otherwise, we'll use a random sample of words
            replacement_words = random.sample(word_list, len(unique_non_empty))
            word_mapping = dict(zip(unique_non_empty, replacement_words))
        
        # Replace values in the column
        new_column = []
        for value in column:
            if value is not None and value != '' and not is_numeric(value):
                new_column.append(word_mapping.get(value, value))
            else:
                new_column.append(value)
                
        replaced_columns.append(new_column)
    
    # Transpose back to rows
    return list(zip(*replaced_columns))

def obfuscate_csv(input_file, output_file, seed=None):
    """
    Obfuscate a CSV file by randomizing numeric values and replacing unique values.
    
    Args:
        input_file: Path to the input CSV file
        output_file: Path to the output CSV file
        seed: Optional random seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)
    
    try:
        # Read the input CSV file
        with open(input_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            data = list(reader)
        
        # Step 1: Randomize numeric values
        for i in range(len(data)):
            for j in range(len(data[i])):
                if is_numeric(data[i][j]):
                    data[i][j] = randomize_numeric_value(data[i][j])
        
        # Step 2: Replace unique values with meaningful English words
        data = replace_unique_values(data)
        
        # Write the obfuscated data to the output file
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)
            
        print(f"CSV obfuscation complete. Output saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error obfuscating CSV: {e}")
        return False

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description='Obfuscate CSV files.')
    parser.add_argument('input', help='Input CSV file')
    parser.add_argument('output', help='Output CSV file')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    return obfuscate_csv(args.input, args.output, args.seed)

if __name__ == '__main__':
    main()
