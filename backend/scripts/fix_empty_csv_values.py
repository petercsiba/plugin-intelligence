import pandas as pd

# Define the data types for the columns
dtype = {
    'id': 'string',
    'google_id': 'string',
    'name': 'string',
    'description': 'string',
    'pricing': 'string',
    'link': 'string',
    'developer_name': 'string',
    'developer_link': 'string',
    'with_drive': 'boolean',
    'with_docs': 'boolean',
    'with_sheets': 'boolean',
    'with_slides': 'boolean',
    'with_forms': 'boolean',
    'with_calendar': 'boolean',
    'with_gmail': 'boolean',
    'with_meet': 'boolean',
    'with_classroom': 'boolean',
    'with_chat': 'boolean',
    'permissions': 'string',
    'reviews': 'string',
    'overview': 'string',
    'logo_link': 'string',
    'featured_img_link': 'string',
    'source_url': 'string'
}

# List of columns to parse as dates
parse_dates = ['created_at', 'p_date', 'listing_updated', 'updated_at']

# Load your CSV with specified data types and parse dates
df = pd.read_csv('/Users/petercsiba/Downloads/google_workspace_export.csv', dtype=dtype, parse_dates=parse_dates, low_memory=False)

# Function to convert '82K+' style ratings to numeric values
def convert_to_numeric(value):
    if pd.isna(value):
        return None
    if isinstance(value, str):
        if 'K' in value:
            return float(value.replace('K', '').replace('+', '')) * 1000
        elif 'M' in value:
            return float(value.replace('M', '').replace('+', '')) * 1000000
        else:
            return float(value.replace('+', ''))
    return value

# Apply the conversion function to the 'user_count', 'rating', and 'rating_count' columns
df['user_count'] = df['user_count'].apply(convert_to_numeric).astype('Int64')
df['rating'] = df['rating'].apply(convert_to_numeric).astype('float')
df['rating_count'] = df['rating_count'].apply(convert_to_numeric).astype('Int64')

# Replace empty strings with NaN
df = df.replace('', pd.NA)

# Save the modified CSV
df.to_csv('/Users/petercsiba/Downloads/google_workspace_export-for-snowflake.csv', index=False)
