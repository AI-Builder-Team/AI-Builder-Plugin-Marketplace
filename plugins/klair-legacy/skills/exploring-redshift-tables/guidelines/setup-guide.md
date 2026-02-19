# Setup Guide

## AWS Secrets Manager

The utilities use the existing secret: `klair/redshift-creds`

Expected secret structure:
```json
{
  "host": "your-cluster.region.redshift.amazonaws.com",
  "port": 5439,
  "database": "your_database",
  "user": "your_username",
  "password": "your_password"
}
```

## Python Dependencies

Install required packages from requirements.txt:

```bash
# Using pip
pip install -r requirements.txt

# Or using pip3
pip3 install -r requirements.txt
```

Or with uv (from klair-api/):

```bash
uv add boto3 redshift-connector
```

## Testing Connection

After setup, verify everything works:

```bash
python3 utils/test_connection.py
```

This will test:
- ✓ AWS credentials are valid
- ✓ Secret 'klair/redshift-creds' is accessible
- ✓ Connection to Redshift works
- ✓ Ready to explore tables
