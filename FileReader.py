"""Módulo para leer distintos formatos de archivo en DataFrames de pandas."""

import pandas as pd
from pandas import DataFrame
import sqlite3
from pathlib import Path
import time


class ParseError(Exception):
    """Error personalizado para problemas al analizar archivos."""
    pass

class FormatError(Exception):
    """Error personalizado para formatos de archivo no soportados."""
    pass


class FileReader:
    """Analiza archivos y los convierte en DataFrames de pandas.
    
    Soporta archivos CSV, Excel y bases de datos SQLite.
    """

    def __init__(self):
        """Inicializa FileReader con las extensiones de archivo permitidas."""
        self._allowed_extensions = {'.csv', '.xlsx', '.xls', '.db', '.sqlite'}

    def _check_format(self, extension: str) -> None:
        """Valida si el formato de archivo es soportado.
        
        Args:
            extension: Extensión del archivo a validar.
            
        Raises:
            FormatError: Si la extensión no está permitida.
        """
        if extension not in self._allowed_extensions:
            raise FormatError

    def parse_file(self, file_name: str) -> DataFrame:
        """Analiza el archivo dado y lo convierte en un DataFrame de pandas.
        
        Args:
            file_name: Ruta del archivo a analizar.
            
        Returns:
            DataFrame con los datos analizados.
            
        Raises:
            Varias excepciones dependiendo de errores al leer el archivo.
        """
        extension = Path(file_name).suffix

        try:
            self._check_format(extension)

            if extension == '.csv':
                df = pd.read_csv(file_name)
            elif extension in {'.xls', '.xlsx'}:
                df = pd.read_excel(file_name)

            return df
        except:
            raise ParseError('ERROR: no se pudo analizar el archivo')
        
    def get_db_tables(self, file_name: str) -> list[str]:
        """Obtiene una lista de tablas de un archivo de base de datos SQLite.

        Args:
            file_name: Ruta del archivo SQLite.

        Returns:
            Lista con los nombres de las tablas.

        Raises:
            ParseError: Si no se puede acceder a la base de datos o es inválida.
        """
        extension = Path(file_name).suffix

        try:
            self._check_format(extension)

            if extension not in {'.db', '.sqlite'}:
                raise FormatError

            conn = sqlite3.connect(file_name)
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            result = pd.read_sql(query, conn)
            conn.close()

            return result['name'].tolist()

        except Exception:
            raise ParseError('ERROR: no se pudieron listar las tablas de la base de datos')


    def parse_sqlite_table(self, file_name: str, table_name: str) -> DataFrame:
        """Analiza una tabla específica de un archivo de base de datos SQLite.
        
        Args:
            file_name: Ruta del archivo SQLite.
            table_name: Nombre de la tabla a cargar.
            
        Returns:
            DataFrame con el contenido de la tabla.
        """
        try:
            conn = sqlite3.connect(file_name)
            df = pd.read_sql(f'SELECT * FROM "{table_name}";', conn)
            conn.close()
            return df
        except Exception:
            raise ParseError('ERROR: no se pudo leer la tabla especificada')


        except FormatError:
            raise ParseError('ERROR: formato de archivo no soportado')
        except pd.errors.EmptyDataError:
            raise ParseError('ERROR: el archivo puede estar vacío o dañado')
        except pd.errors.ParserError:
            raise ParseError('ERROR: el archivo no se pudo analizar')
        except sqlite3.DatabaseError:
            raise ParseError('ERROR: ocurrió un error con la base de datos')
        except sqlite3.OperationalError:
            raise ParseError('ERROR: no se pudo acceder a la base de datos')
        except FileNotFoundError:
            raise ParseError('ERROR: archivo no encontrado')
        except Exception as e:
            raise ParseError(f'ERROR: error desconocido, no se pudo leer el archivo')
