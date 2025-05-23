# Database Migrations Guide

This document explains how to use database migrations in the Tidal Weather App.

## Setup

The application uses Flask-Migrate (based on Alembic) to handle database migrations. This allows for:

- Tracking database schema changes
- Upgrading the database schema to newer versions
- Downgrading to previous versions if needed
- Generating migration scripts automatically based on model changes

## Initial Setup

If you're setting up the project for the first time:

1. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Initialize the database:

   ```bash
   flask db init
   ```

3. Create the first migration:

   ```bash
   flask db migrate -m "Initial migration"
   ```

4. Apply the migration:

   ```bash
   flask db upgrade
   ```

## ## Managing Migrations

1. To upgrade to the latest version:

    ```bash
    flask db upgrade
    ```

2. To downgrade to a previous version:

    ```bash
    flask db downgrade
    ```

3. To see the current migration version:

    ```bash
    flask db current
    ```

4. To see the history of migrations:

    ```bash
    flask db history
    ```

5. To generate a new migration based on model changes:

    ```bash
    flask db migrate -m "dd description to Location model"
    ```

6. To apply a specific migration:

    ```bash
    flask db upgrade
    ```
