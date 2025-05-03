import pandas as pd

class DataManager:
    def __init__(self, dataframe: pd.DataFrame):
        """Initialize DataManager with a pandas DataFrame."""
        self.data = dataframe
        self.columns = dataframe.columns.tolist()
        self.features = None
        self.target = None

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
    
    

        

    def get_data(self, key):
        if key not in self.data:
            raise KeyError(f"Key {key} not found.")
        return self.data[key]

    def remove_data(self, key):
        if key not in self.data:
            raise KeyError(f"Key {key} not found.")
        del self.data[key]