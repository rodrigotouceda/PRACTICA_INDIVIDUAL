import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

class DataManager:
    def __init__(self, dataframe: pd.DataFrame):
        """Initialize DataManager with a pandas DataFrame."""
        self.original_data = dataframe
        self.data = dataframe.copy()
        self.columns = dataframe.columns.tolist()
        self.features = []
        self.target = []
        self.new_features = []
        self.categoric_columns = []
        self.original_categoric_columns = []
        self.normalizable_columns = []
        self.original_normalizable_columns = []
        self.outlier_columns = []
        self.one_hot_features = []

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
    

    def is_categorical(self, column: str, og_df = False) -> bool:
        """Check if a column is categorical."""
        if not og_df:
            if (pd.api.types.is_categorical_dtype(self.data[column]) 
                    or pd.api.types.is_object_dtype(self.data[column]) and self.data[column].nunique() < 0.05 * len(self.data[column]) 
                    or pd.api.types.is_numeric_dtype(self.data[column]) and self.data[column].nunique() < 0.05 * len(self.data[column])
        ):      
                self.categoric_columns.append(column)
                return True

            else:
                return False
        else:
            if (pd.api.types.is_categorical_dtype(self.original_data[column]) 
                    or pd.api.types.is_object_dtype(self.original_data[column]) and self.original_data[column].nunique() < 0.05 * len(self.original_data[column]) 
                    or pd.api.types.is_numeric_dtype(self.original_data[column]) and self.original_data[column].nunique() < 0.05 * len(self.original_data[column])
        ):      
                self.original_categoric_columns.append(column)
                return True

            else:
                return False

        
    def to_categorical(self, columns: list[str], opcion: int):
        """Convert specified columns to categorical."""
        if opcion == 1:
            self.data = self.to_one_hot(columns)
            print("Transformación completada con One-Hot Encoding.")
        elif opcion == 2:
            self.data = self.to_label(columns)
            print("Transformación completada con Label Encoding.")
        elif opcion == 3:
            print("\n🔁 Reiniciando menú de manejo de valores faltantes...")
            return
        else:
            print("\nOpción no válida.")
            return
        return self.data
        
    def is_normalizable(self, column: str, og_df = False) -> bool:
        """Check if a column is normalizable."""
        if not og_df:
            if (pd.api.types.is_numeric_dtype(self.data[column])) and (self.data[column].nunique() > 0.05 * len(self.data[column])
                    and self.data[column].nunique() < 0.95 * len(self.data[column])):
                self.normalizable_columns.append(column)
                return True

            else:
                return False
        else:
            if (pd.api.types.is_numeric_dtype(self.original_data[column])) and (self.original_data[column].nunique() > 0.05 * len(self.original_data[column])
                    and self.original_data[column].nunique() < 0.95 * len(self.original_data[column])):
                self.original_normalizable_columns.append(column)
                return True

            else:
                return False
        
    def has_outliers(self, column: str) -> bool:
        if self.is_normalizable(column):
            """Check if a column has outliers using the IQR method."""
            Q1 = self.data[column].quantile(0.25)
            Q3 = self.data[column].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = (self.data[column] < lower_bound) | (self.data[column] > upper_bound)
            self.outlier_columns.append(column)
            return outliers.any()  # Devuelve True si algún valor es un outlier
        else:
            return False

  
    
    def remove_outliers(self, columns: list[str]):
        """Elimina las filas que contienen outliers en la columna especificada usando el método IQR."""
        print(self.data)
        for column in columns:
            if column not in self.normalizable_columns:
                continue
            else:

                Q1 = self.data[column].quantile(0.25)
                Q3 = self.data[column].quantile(0.75)
                IQR = Q3 - Q1

                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                # Conserva solo los valores dentro de los límites
                self.data = self.data[self.data[column] >= lower_bound]
                self.data = self.data[self.data[column] <= upper_bound]
        print(self.data)
        return self.data
    
    def replace_outliers_with_median(self, column: str):
        """Reemplaza los outliers en la columna especificada con la mediana de esa columna."""
        if pd.api.types.is_numeric_dtype(self.data[column]):
            Q1 = self.data[column].quantile(0.25)
            Q3 = self.data[column].quantile(0.75)
            IQR = Q3 - Q1
    
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
    
            # Calcula la mediana
            median_value = self.data[column].median()
    
            # Reemplaza los outliers con la mediana
            mask_outliers = (self.data[column] < lower_bound) | (self.data[column] > upper_bound)
            self.data.loc[mask_outliers, column] = median_value
    
        return self.data
    


    def to_one_hot(self, columns: list[str]):
        """One-hot encode columns and update only selected features."""
        original_features = self.features.copy()

        self.data = pd.get_dummies(self.data, columns=columns)

        # Actualizar solo las columnas derivadas de las seleccionadas
        updated_features = []
        for col in original_features:
            if col in columns:
                # Añadir todas las nuevas columnas one-hot que provienen de esta
                updated_features.extend([c for c in self.data.columns if c.startswith(col + '_')])
                self.one_hot_features.extend([c for c in self.data.columns if c.startswith(col + '_')])
            elif col in self.data.columns:
                updated_features.append(col)  # Si sigue existiendo, mantenerla

        self.new_features = updated_features
        return self.data

    
    def to_label(self , columns: list[str]):
        """Convert specified columns to label encoding."""
        for col in columns:
            self.data[col] = self.data[col].astype('category').cat.codes
        self.new_features = self.features
        return self.data
    
    def min_max_scaler(self, columns: list[str]):
        """Apply Min-Max scaling to specified columns."""
        scaler = MinMaxScaler()
        self.data[columns] = scaler.fit_transform(self.data[columns])
        return self.data

    def z_score_scaler(self, columns: list[str]):
        """Apply Z-Score scaling to specified columns."""
        scaler = StandardScaler()
        self.data[columns] = scaler.fit_transform(self.data[columns])
        return self.data
        

    def get_data(self, key):
        if key not in self.data:
            raise KeyError(f"Key {key} not found.")
        return self.data[key]

    def remove_data(self, key):
        if key not in self.data:
            raise KeyError(f"Key {key} not found.")
        del self.data[key]