import os
import sys
from database.connection import get_db_connection, create_tables, insert_menu_items
from parsers.menu_parser import parse_all_menu_files


def main():
    """Main function to orchestrate the database population."""
    conn = get_db_connection()
    if not conn:
        print("Failed to establish database connection. Exiting.")
        sys.exit(1)

    create_tables(conn)

    menu_dir = "BellaTerra"  # Path within the container
    all_items = parse_all_menu_files(menu_dir)

    if all_items:
        insert_menu_items(conn, all_items)
    else:
        print("No items found to insert.")

    conn.close()
    print("Database population completed successfully.")


if __name__ == "__main__":
    main()