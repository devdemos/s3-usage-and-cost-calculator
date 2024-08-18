# S3 Usage and Cost Calculator

This repository provides a Python script to calculate AWS S3 usage and estimate associated costs based on the configured storage class pricing. The tool aggregates data across all S3 buckets within a specified date range, generates a summary of storage usage, and calculates the cost based on hardcoded pricing tiers. Results are saved in an organized format within an output directory.

## Features

- Fetches all S3 bucket data using the AWS SDK (`boto3`).
- Calculates storage usage for all objects within the specified date range.
- Supports different storage classes with tiered pricing.
- Outputs detailed usage and cost reports as CSV files.
- Automatically creates an `output` directory for storing results.

## Requirements

- Python 3.x
- `boto3`
- `pandas`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/s3-usage-and-cost-calculator.git
   cd s3-usage-and-cost-calculator

2.	Create a virtual environment and install the required dependencies:

```
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```
3.	Make sure your AWS credentials are properly configured using the AWS CLI or environment variables.


## Usage

1. Run the script 

```
python s3_usage_and_cost_calculator.py
```

2.	You will be prompted to enter the following inputs:

	    • Start Date: The start of the date range for which you want to calculate S3 usage (format: YYYY-MM-DD).
	    • End Date: The end of the date range (format: YYYY-MM-DD).
	    • Output File Name: The base name of the output CSV files (without the .csv extension).

3.	The script will generate two CSV files in the output folder:

	    • usage_<output_file>.csv: A report of the storage usage in a human-readable format (e.g., GB, MB).
	    • cost_<output_file>.csv: A report of the estimated costs based on the usage and pricing tiers.

## Example 

```
Enter start date (YYYY-MM-DD): 2024-01-01
Enter end date (YYYY-MM-DD): 2024-07-01
Enter output file name (without extension): s3_report
```

After running, you’ll find the following files in the output directory:

	•	output/usage_s3_report.csv
	•	output/cost_s3_report.csv

Here's how you can display the `output/usage_s3_report.csv` and `output/cost_s3_report.csv` examples in Markdown code:

### Example of `usage_s3_report.csv`

The `usage_s3_report.csv` file contains the storage usage information for each S3 bucket, broken down by month and storage class. Here's an example of the content:

```csv
Month,Bucket_A.STANDARD,Bucket_B.STANDARD,Total
2024-01,15.25 GB,22.75 GB,38.00 GB
2024-02,10.50 GB,25.00 GB,35.50 GB
2024-03,12.00 GB,30.00 GB,42.00 GB
```

### Example of `cost_s3_report.csv`

The `cost_s3_report.csv` file contains the estimated cost for each bucket and storage class, based on the pricing tiers. Here's an example of the content:

```csv
Month,Bucket_A.STANDARD,Bucket_B.STANDARD,Total
2024-01,$0.38,$0.57,$0.95
2024-02,$0.26,$0.63,$0.89
2024-03,$0.30,$0.76,$1.06
```

### Visual Example of the Output

#### `output/usage_s3_report.csv`:
```
+-------+-------------------+-------------------+---------+
| Month | Bucket_A.STANDARD  | Bucket_B.STANDARD  | Total   |
+-------+-------------------+-------------------+---------+
| 2024-01 | 15.25 GB        | 22.75 GB           | 38.00 GB|
| 2024-02 | 10.50 GB        | 25.00 GB           | 35.50 GB|
| 2024-03 | 12.00 GB        | 30.00 GB           | 42.00 GB|
+-------+-------------------+-------------------+---------+
```

#### `output/cost_s3_report.csv`:
```
+-------+-------------------+-------------------+---------+
| Month | Bucket_A.STANDARD  | Bucket_B.STANDARD  | Total   |
+-------+-------------------+-------------------+---------+
| 2024-01 | $0.38           | $0.57             | $0.95   |
| 2024-02 | $0.26           | $0.63             | $0.89   |
| 2024-03 | $0.30           | $0.76             | $1.06   |
+-------+-------------------+-------------------+---------+
```



## Configuration

### S3 Pricing

The S3 pricing data is hardcoded in the script for simplicity. You can modify the pricing tiers inside the get_s3_pricing() function.

Example:

```
def get_s3_pricing():
    return {
        'STANDARD': {
            'price_tiers': [
                {'limit': 50, 'price': 0.025},
                {'limit': 500, 'price': 0.024},
                {'limit': float('inf'), 'price': 0.023}
            ]
        }
    }
```

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests for improvements and bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
