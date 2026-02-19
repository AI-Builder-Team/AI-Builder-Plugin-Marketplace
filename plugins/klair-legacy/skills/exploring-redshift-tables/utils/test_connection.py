#!/usr/bin/env python3
"""Test Redshift connection and verify setup."""

import sys
import json
import boto3
from db_connector import get_credentials, get_connection


def test_aws_credentials():
    """Test if AWS credentials are valid."""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print("✓ AWS credentials valid")
        print(f"  Account: {identity['Account']}")
        print(f"  User ARN: {identity['Arn']}")
        return True
    except Exception as e:
        print(f"✗ AWS credentials invalid: {e}")
        return False


def test_secret_access():
    """Test if the Redshift credentials secret exists and is accessible."""
    try:
        creds = get_credentials()
        required_keys = ['host', 'database', 'user', 'password']
        missing_keys = [key for key in required_keys if key not in creds]

        if missing_keys:
            print(f"✗ Secret missing required keys: {', '.join(missing_keys)}")
            return False

        print("✓ Secret 'klair/redshift-creds' found")
        print(f"  Host: {creds['host']}")
        print(f"  Database: {creds['database']}")
        print(f"  User: {creds['user']}")
        return True
    except SystemExit:
        # get_credentials already printed the error
        return False
    except Exception as e:
        print(f"✗ Failed to access secret: {e}")
        return False


def test_redshift_connection():
    """Test if we can connect to Redshift."""
    try:
        conn = get_connection()

        # Try a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result and result[0] == 1:
            print("✓ Connected to Redshift successfully")
            return True
        else:
            print("✗ Connected but test query failed")
            return False
    except SystemExit:
        # get_connection already printed the error
        return False
    except Exception as e:
        print(f"✗ Failed to connect to Redshift: {e}")
        return False


def main():
    """Run all connection tests."""
    print("Testing Redshift connection setup...\n")

    tests_passed = 0
    total_tests = 3

    # Test 1: AWS Credentials
    if test_aws_credentials():
        tests_passed += 1
    print()

    # Test 2: Secret Access
    if test_secret_access():
        tests_passed += 1
    print()

    # Test 3: Redshift Connection
    if test_redshift_connection():
        tests_passed += 1
    print()

    # Summary
    if tests_passed == total_tests:
        print("=" * 50)
        print("✓ All tests passed! Ready to explore Redshift tables")
        print("=" * 50)
        sys.exit(0)
    else:
        print("=" * 50)
        print(f"✗ {total_tests - tests_passed} test(s) failed")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()
