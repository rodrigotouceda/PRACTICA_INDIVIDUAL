import pandas as pd

class DataManager:
    def __init__(self, dataframe: pd.DataFrame):
        """Initialize DataManager with a pandas DataFrame."""
        self.data = dataframe
        self.columns = dataframe.columns.tolist()
        self.features = None
        self.target = None
        self.categoric_columns = []
        self.numeric_columns = []

    def get_columns(self):
        """Get the list of columns in the DataFrame."""
        return self.columns
    
    def display_columns(self):
        """Display the columns in the DataFrame."""
        for i, col in enumerate(self.columns, start = 0):
            print(f"\t [{i}]: {col}")

    def select_columns(self, features: list[str], target: str):
        features = [int(i.strip()) for i in features.split(",") if i.strip() != ""]
        target = int(target.strip())
        if not features:
            print("\n⚠️ Error: Debe seleccionar al menos una columna como feature.")
            return None, None

        if target in features:
            print("\n⚠️ Error: La columna target no puede ser una de las features.")
            return None, None
        
        if len(features) != len(set(features)):
            print("\n⚠️ Error: No se permiten columnas repetidas en las features.")
            return None, None

        if any(i < 0 or i >= len(self.columns) for i in features + [target]):
            print("\n⚠️ Error: Has ingresado un número de columna que no existe.")
            return None, None

        # Convertir a nombres de columnas
        X = [self.columns[i] for i in features]
        y = self.columns[target]

        self.features = X
        self.target = y

        return X, y
    
    def manage_missing_values(self, columns, method: int):
        """
        Manage missing values in specific columns of the DataFrame.

        Args:
            columns (list): Column names to apply the method on.
            method (int): 
                1 - Drop rows with NaN
                2 - Fill with mean
                3 - Fill with median
                4 - Fill with mode
                5 - Fill with a specific value
                6 - Restart menu

        Returns:
            None or DataFrame: Returns the updated DataFrame or None if cancelled.
        """
        if method == 1:
            self.data = self.data.dropna(subset=columns)

        elif method == 2:
            for col in columns:
                if pd.api.types.is_numeric_dtype(self.data[col]):
                    self.data[col] = self.data[col].fillna(self.data[col].mean())

        elif method == 3:
            for col in columns:
                if pd.api.types.is_numeric_dtype(self.data[col]):
                    self.data[col] = self.data[col].fillna(self.data[col].median())

        elif method == 4:
            for col in columns:
                self.data[col] = self.data[col].fillna(self.data[col].mode().iloc[0])

        elif method == 5:
            value = input("Ingrese el valor con el que desea llenar los NaN: ")
            for col in columns:
                self.data[col] = self.data[col].fillna(value)

        elif method == 6:
            print("\n🔁 Reiniciando menú de manejo de valores faltantes...")
            return None

        else:
            print("\n⚠️ Error: Opción no válida.")
            return None

        return self.data
    

    def is_categorical(self, column: str) -> bool:
        """Check if a column is categorical."""
        
        if (pd.api.types.is_categorical_dtype(self.data[column]) 
                or pd.api.types.is_object_dtype(self.data[column]) 
                and self.data[column].nunique() < 0.05 * len(self.data[column]) 
                or pd.api.types.is_numeric_dtype(self.data[column]) 
                and self.data[column].nunique() < 0.05 * len(self.data[column])
    ):      
            self.categoric_columns.append(column)
            return True
        
        else:
            return False

    def to_one_hot(self, columns: list[str]):
        """Convert specified columns to one-hot encoding."""
        df_encoded = pd.get_dummies(self.data, columns = columns)
        return df_encoded
    
    def to_label(self , columns: list[str]):
        """Convert specified columns to label encoding."""
        for col in columns:
            self.data[col] = self.data[col].astype('category').cat.codes
        return self.data
    
    

        

        

    def get_data(self, key):
        if key not in self.data:
            raise KeyError(f"Key {key} not found.")
        return self.data[key]

    def remove_data(self, key):
        if key not in self.data:
            raise KeyError(f"Key {key} not found.")
        del self.data[key]