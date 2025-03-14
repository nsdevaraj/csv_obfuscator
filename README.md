# CSV Obfuscation Tool

A Python tool for obfuscating CSV data while maintaining data patterns and context.

## Features

This tool performs two types of obfuscation on CSV files:

1. **Numeric Value Randomization**: Changes all numeric values to random values within a similar range (±20% by default)
2. **Unique Value Replacement**: Replaces unique values in each column with meaningful English words in a context-appropriate manner

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

## Example Transformation

### Original CSV:
```
ID,Name,Age,Country,City,Salary
1,John Smith,34,USA,New York,75000
2,Maria Garcia,29,Spain,Madrid,68000
3,Li Wei,42,China,Beijing,82000
```

### Obfuscated CSV:
```
ID,Name,Age,Country,City,Salary
1,Jennifer,36,James,Matthew,69773
2,Elizabeth,25,Robert,Donna,68094
3,Sophia,35,Matthew,Lisa,92576
```

## Limitations

- The tool preserves the CSV structure and header row
- It does not anonymize or encrypt the data; it only obfuscates it
- The obfuscation is not reversible
- The tool may not preserve relationships between columns (e.g., city-country relationships)
- Very large CSV files may require additional memory

## License

This project is licensed under the MIT License - see the LICENSE file for details.
