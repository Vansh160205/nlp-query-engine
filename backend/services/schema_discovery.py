from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.exc import SQLAlchemyError

class SchemaDiscovery:
    """
    Connects to a database and discovers its schema, including tables,
    columns, data types, and relationships (foreign keys).
    """

    def analyze_database(self, connection_string: str) -> dict:
        """
        Analyzes the database schema and returns it as a dictionary.

        Args:
            connection_string: The SQLAlchemy connection string for the database.

        Returns:
            A dictionary representing the database schema.
            Returns an error dictionary if the connection fails.
        """
        try:
            engine = create_engine(connection_string)
            inspector = inspect(engine)
            metadata = MetaData()
            metadata.reflect(bind=engine)

            schema = {"tables": []}

            table_names = inspector.get_table_names()

            for table_name in table_names:
                table_info = {
                    "name": table_name,
                    "columns": [],
                    "foreign_keys": []
                }

                # Get column information
                columns = inspector.get_columns(table_name)
                for column in columns:
                    table_info["columns"].append({
                        "name": column['name'],
                        "type": str(column['type']),
                        "nullable": column['nullable'],
                        "default": column.get('default'),
                    })

                # Get foreign key information
                foreign_keys = inspector.get_foreign_keys(table_name)
                for fk in foreign_keys:
                    table_info["foreign_keys"].append({
                        "constrained_columns": fk['constrained_columns'],
                        "referred_table": fk['referred_table'],
                        "referred_columns": fk['referred_columns'],
                    })
                
                schema["tables"].append(table_info)
            
            return schema

        except SQLAlchemyError as e:
            print(f"Error connecting to the database or analyzing schema: {e}")
            return {"error": f"Failed to analyze database. Details: {e}"}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"error": f"An unexpected error occurred: {e}"}
