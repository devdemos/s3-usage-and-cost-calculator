import boto3
import pandas as pd
from datetime import datetime, timezone
import json
import os

def get_s3_pricing():
    # Hardcoded pricing data based on provided rates
    return {
        'STANDARD': {
            'price_tiers': [
                {'limit': 50, 'price': 0.025},
                {'limit': 500, 'price': 0.024},
                {'limit': float('inf'), 'price': 0.023}
            ]
        }
    }

def get_all_buckets():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    return [bucket['Name'] for bucket in response['Buckets']]

def get_s3_usage(bucket_name, start_date, end_date):
    client = boto3.client('s3')
    paginator = client.get_paginator('list_objects_v2')
    
    usage_data = []
    
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get('Contents', []):
            obj_date = obj['LastModified']
            if start_date <= obj_date <= end_date:
                storage_class = obj.get('StorageClass', 'STANDARD')  # Default to 'STANDARD' if not specified
                usage_data.append((obj_date, obj['Size'], storage_class))
    
    return usage_data

def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

def calculate_cost(size_in_bytes, storage_class, pricing_data):
    size_in_gb = size_in_bytes / (1024 ** 3)
    price_tiers = pricing_data.get(storage_class, {}).get('price_tiers', [])
    
    if not price_tiers:
        print(f"No pricing tiers found for storage class: {storage_class}")
        return 0

    cost = 0
    remaining_gb = size_in_gb
    for tier in price_tiers:
        if remaining_gb > tier['limit']:
            cost += tier['limit'] * tier['price']
            remaining_gb -= tier['limit']
        else:
            cost += remaining_gb * tier['price']
            break
    
    return cost

def create_output_folder():
    output_folder = 'output'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return output_folder

def main(start_date, end_date, output_file):
    start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    
    pricing_data = get_s3_pricing()
    buckets = get_all_buckets()
    
    all_usage_data = []
    
    for bucket in buckets:
        usage_data = get_s3_usage(bucket, start_date, end_date)
        for date, size, storage_class in usage_data:
            all_usage_data.append({'Bucket': bucket, 'Date': date, 'Size': size, 'StorageClass': storage_class})
    
    if not all_usage_data:
        print("No data found in the specified date range.")
        return
    
    df = pd.DataFrame(all_usage_data)
    df['Month'] = df['Date'].dt.to_period('M')
    summary = df.groupby(['Bucket', 'Month', 'StorageClass'])['Size'].sum().reset_index()
    
    summary_pivot = summary.pivot(index='Month', columns=['Bucket', 'StorageClass'], values='Size').fillna(0)
    
    summary_pivot['Total'] = summary_pivot.sum(axis=1)
    bucket_totals = summary_pivot.sum(axis=0)
    bucket_totals.name = 'Total'
    
    summary_pivot = pd.concat([summary_pivot, pd.DataFrame(bucket_totals).T])
    
    # Calculate costs
    cost_summary = summary_pivot.copy()
    for column in cost_summary.columns:
        if column != 'Total':
            bucket, storage_class = column
            if storage_class in pricing_data:
                cost_summary[column] = cost_summary[column].apply(lambda x: calculate_cost(x, storage_class, pricing_data))
            else:
                cost_summary[column] = cost_summary[column].apply(lambda x: 0)  # Set cost to 0 if unknown storage class
    
    summary_pivot = summary_pivot.applymap(format_size)
    cost_summary = cost_summary.applymap('${:,.2f}'.format)
    
    output_folder = create_output_folder()
    
    if not output_file.endswith('.csv'):
        output_file += '.csv'
    
    usage_output_path = os.path.join(output_folder, f"usage_{output_file}")
    cost_output_path = os.path.join(output_folder, f"cost_{output_file}")
    
    summary_pivot.to_csv(usage_output_path)
    cost_summary.to_csv(cost_output_path)
    
    print(f"Usage output written to {usage_output_path}")
    print(f"Cost output written to {cost_output_path}")

if __name__ == '__main__':
    start_date = input('Enter start date (YYYY-MM-DD): ')
    end_date = input('Enter end date (YYYY-MM-DD): ')
    output_file = input('Enter output file name (without extension): ')
    
    main(start_date, end_date, output_file)