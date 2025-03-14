# CSV Obfuscation Tool

A Python tool for obfuscating CSV data while maintaining data patterns and context.

## Features

This tool performs two types of obfuscation on CSV files:

1. **Numeric Value Randomization**: Changes all numeric values to random values within a similar range (±20% by default)
2. **Unique Value Replacement**: Replaces unique values in each column with meaningful English words in a context-appropriate manner
3. **Smart Column Preservation**: Automatically preserves:
   - Date columns (detected by common date patterns)
   - Boolean/status columns with fewer than 3 unique values

## Installation

The CSV Obfuscator requires Python 3.6 or higher. No additional packages are required as it uses only standard library modules.

```bash
# Clone or download the repository
git clone https://github.com/yourusername/csv-obfuscator.git
cd csv-obfuscator

# Make the script executable
chmod +x csv_obfuscator.py
```

## Usage

```
python csv_obfuscator.py input.csv output.csv [--seed SEED]
```

### Arguments

- `input.csv`: Path to the input CSV file
- `output.csv`: Path to the output CSV file
- `--seed SEED`: (Optional) Random seed for reproducibility

### Examples

Basic usage:
```bash
python csv_obfuscator.py data.csv obfuscated_data.csv
```

Using a specific random seed for reproducible results:
```bash
python csv_obfuscator.py data.csv obfuscated_data.csv --seed 42
```

## How It Works

### Numeric Value Randomization

The tool identifies numeric values in the CSV and replaces them with random values within a similar range. By default, the variation is ±20% of the original value.

For example:
- Original: 100 → Possible range: 80-120
- Original: 1000 → Possible range: 800-1200
- Original: -50 → Possible range: -60 to -40

The tool preserves the type of the original value (integer or float) and maintains a similar number of decimal places for floating-point values.

### Unique Value Replacement

For non-numeric columns, the tool:

1. Identifies unique values in each column
2. Determines the most appropriate category for the column based on data patterns
3. Replaces each unique value with a word from the appropriate category

Available word categories include:
- Names
- Countries
- Cities
- Companies
- Products
- Colors
- Animals
- Fruits
- Vegetables
- Jobs

The tool intelligently selects the most appropriate category based on the data patterns in each column. For example, short text fields might be replaced with colors or names, while longer fields might be replaced with company names or job titles.

### Smart Column Preservation

The tool automatically detects and preserves certain types of columns:

#### Date Column Detection

Date columns are automatically detected using common date patterns:
- YYYY-MM-DD, DD-MM-YYYY, MM/DD/YYYY formats
- Month name formats (e.g., "Jan 15, 2023" or "15 January 2023")
- Various date separators (-, /, spaces)

When a column is identified as containing dates (more than 70% of values match date patterns), the original values are preserved without obfuscation.

#### Boolean/Status Column Detection

Boolean or status columns with fewer than 3 unique values are automatically preserved. The tool recognizes:
- Common boolean pairs like true/false, yes/no, y/n, 1/0, on/off
- Status indicators like active/inactive, enabled/disabled
- Any column with fewer than 3 unique values is considered a status/category column and preserved

## Example Transformation

### Original CSV:
```
ID,Name,Age,Country,City,Salary,Date Joined,Status,Active
1,John Smith,34,USA,New York,75000,2020-03-15,Active,Yes
2,Maria Garcia,29,Spain,Madrid,68000,2021-06-22,Active,Yes
3,Li Wei,42,China,Beijing,82000,2018-11-05,Inactive,No
```

### Obfuscated CSV:
```
ID,Name,Age,Country,City,Salary,Date Joined,Status,Active
1,Jennifer,36,James,Matthew,69773,2020-03-15,Active,Yes
2,Elizabeth,25,Robert,Donna,68094,2021-06-22,Active,Yes
3,Sophia,35,Matthew,Lisa,92576,2018-11-05,Inactive,No
```

Note how the "Date Joined" column is preserved because it contains date values, and the "Status" and "Active" columns are preserved because they contain fewer than 3 unique values (boolean/status columns).

## Limitations

- The tool preserves the CSV structure and header row
- It does not anonymize or encrypt the data; it only obfuscates it
- The obfuscation is not reversible
- The tool may not preserve relationships between columns (e.g., city-country relationships)
- Very large CSV files may require additional memory

## License

This project is licensed under the MIT License - see the LICENSE file for details.
