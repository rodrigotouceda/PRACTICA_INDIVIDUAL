import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

class DataManager:
    def __init__(self, dataframe: pd.DataFrame):
        """Inicializa el DataManager con un DataFrame de pandas, guardando una copia original y 
        creando variables auxiliares para el procesamiento."""
        self.original_data = dataframe
        self.data = dataframe.copy()
        self.columns = dataframe.columns.tolist()
        self.features = []
        self.target = []
        self.new_features = []
        self.missing_values_columns = []
        self.categoric_columns = []
        self.original_categoric_columns = []
        self.normalizable_columns = []
        self.original_normalizable_columns = []
        self.outlier_columns = []
        self.one_hot_features = []
    
    def mostrar_columnas(self):
        """Muestra los índices y nombres de las columnas del DataFrame."""
        for i, col in enumerate(self.columns, start = 0):
            print(f"\t [{i}]: {col}")

    def seleccionar_columnas(self, features: list[str], target: str):
        """
        Permite seleccionar columnas como características (features) y como variable objetivo (target) 
        mediante índices.

        Args:
            features (list[str]): Lista de índices como strings separados por coma.
            target (str): Índice de la columna objetivo como string.

        Returns:
            tuple: Tupla con lista de nombres de columnas features y nombre de columna target, 
            o (None, None) si hay error.
        """
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

        #Convertir a nombres de columnas
        X = [self.columns[i] for i in features]
        y = self.columns[target]

        self.features = X
        self.target = y

        return X, y
    
    def manejar_valores_faltantes(self, columns, method: int):
        """
        Maneja valores faltantes en columnas específicas del DataFrame.

        Args:
            columns (list): Nombres de columnas a procesar.
            method (int): 
                1 - Eliminar filas con NaN
                2 - Rellenar con la media
                3 - Rellenar con la mediana
                4 - Rellenar con la moda
                5 - Rellenar con un valor específico
                6 - Reiniciar menú

        Returns:
            DataFrame o None: DataFrame actualizado o None si hay error.
        """
        print(self.data.dtypes[columns])
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
        else:
            print("\n⚠️ Error: Opción no válida.")
            return None
        
        return self.data
    
    def tiene_valores_faltantes(self, column: str) -> bool:
        """
        Verifica si una columna tiene valores faltantes (NaN).

        Args:
            column (str): Nombre de la columna.

        Returns:
            bool: True si hay valores faltantes, False en caso contrario.
        """
        if self.data[column].isnull().sum() > 0:
            self.missing_values_columns.append(column)
            return True
        else:
            return False
    

    def es_categorica(self, column: str, og_df = False) -> bool:
        """
        Determina si una columna puede considerarse categórica.

        Args:
            column (str): Nombre de la columna.
            og_df (bool): Si se debe evaluar sobre el DataFrame original.

        Returns:
            bool: True si es categórica, False si no.
        """
        df = self.data if not og_df else self.original_data

        if (pd.api.types.is_categorical_dtype(df[column]) 
                or pd.api.types.is_object_dtype(df[column]) and df[column].nunique() < 7
                or pd.api.types.is_numeric_dtype(df[column]) and df[column].nunique() < 7
    ):      
            self.categoric_columns.append(column)
            return True
        else:
            return False
        
    def a_categorica(self, columns: list[str], opcion: int):
        """
        Convierte columnas categóricas a formato numérico.

        Args:
            columns (list[str]): Lista de columnas a transformar.
            opcion (int): 
                1 - One-Hot Encoding
                2 - Label Encoding

        Returns:
            DataFrame: DataFrame transformado.
        """
        if opcion == 1:
            self.data = self.a_one_hot(columns)
            print("Transformación completada con One-Hot Encoding.")
        elif opcion == 2:
            self.data = self.a_label(columns)
            print("Transformación completada con Label Encoding.")
        else:
            print("\nOpción no válida.")
            return None
        return self.data
        
    def es_normalizable(self, column: str, og_df = False) -> bool:
        """
        Verifica si una columna es adecuada para normalización.

        Args:
            column (str): Nombre de la columna.
            og_df (bool): Si se debe evaluar sobre el DataFrame original.

        Returns:
            bool: True si se puede normalizar, False en caso contrario.
        """
        df = self.data if not og_df else self.original_data
        norm_cols = self.normalizable_columns if not og_df else self.original_normalizable_columns

        if (pd.api.types.is_numeric_dtype(df[column])) and (df[column].nunique() > 0.05 * len(df[column])
                and df[column].nunique() < 0.95 * len(df[column])):
            norm_cols.append(column)
            return True
        else:
            return False
            
    def normalizar(self, columns: list[str], method: int):
        """
        Normaliza las columnas indicadas con el método elegido.

        Args:
            columns (list[str]): Lista de columnas numéricas.
            method (int): 
                1 - Min-Max Scaling
                2 - Z-Score Scaling

        Returns:
            DataFrame: DataFrame normalizado.
        """
        if method == 1:
            df_normalizado = self.normalizar_min_max(columns)
            print("Normalización Min-Max completada.")
        elif method == 2:
            df_normalizado = self.normalizar_z_score(columns)
            print("Normalización Z-score completada.")
        else:
            print("\nOpción no válida.")
            return None
        self.data = df_normalizado
        return self.data
    

    def tiene_outliers(self, column: str) -> bool:
        """
        Verifica si una columna contiene outliers utilizando el método IQR.

        Args:
            column (str): Nombre de la columna.

        Returns:
            bool: True si hay outliers, False si no.
        """
        if self.es_normalizable(column):
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

    def manejar_atipicos(self, columns: list[str], method: int):
        """
        Maneja valores atípicos (outliers) en columnas especificadas.

        Args:
            columns (list[str]): Lista de columnas a evaluar.
            method (int): 
                1 - Eliminar filas con outliers
                2 - Reemplazar con la mediana
                3 - No hacer nada

        Returns:
            DataFrame: DataFrame actualizado.
        """
        if method == 1:
            df_sin_atipicos = self.eliminar_atipicos(columns)
            print("Eliminación de outliers completada.")
        elif method == 2:
            df_sin_atipicos = self.reemplazar_atipicos_mediana(columns)
            print("Reemplazo de outliers con la mediana completado.")      

        elif method == 3:
            print("Manteniendo valores atípicos sin cambios.")
            df_sin_atipicos = self.data 

        else:
            print("\nOpción no válida.")
            return None
        
        self.data = df_sin_atipicos
        return self.data
 
    
    def eliminar_atipicos(self, columns: list[str]):
        """
        Elimina filas que contienen outliers en las columnas indicadas usando el método IQR.

        Args:
            columns (list[str]): Columnas a evaluar.

        Returns:
            DataFrame: DataFrame sin outliers.
        """
        for column in columns:

            Q1 = self.data[column].quantile(0.25)
            Q3 = self.data[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            # Conservar solo los valores dentro de los límites
            self.data = self.data[self.data[column] >= lower_bound]
            self.data = self.data[self.data[column] <= upper_bound]
        return self.data
    
    def reemplazar_atipicos_mediana(self, columns: list[str]):
        """
        Reemplaza valores atípicos en columnas especificadas con la mediana de esa columna.

        Args:
            columns (list[str]): Columnas a procesar.

        Returns:
            DataFrame: DataFrame con outliers reemplazados.
        """        
        for column in columns:
            print(column)
            if column not in self.outlier_columns:
                continue
            else:

                Q1 = self.data[column].quantile(0.25)
                Q3 = self.data[column].quantile(0.75)
                IQR = Q3 - Q1

                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                median_value = self.data[column].median()

                outliers_mask = (self.data[column] < lower_bound) | (self.data[column] > upper_bound)
                self.data.loc[outliers_mask, column] = median_value

        return self.data
    


    def a_one_hot(self, columns: list[str]):
        """
        Aplica One-Hot Encoding a columnas categóricas.

        Args:
            columns (list[str]): Lista de columnas a transformar.

        Returns:
            DataFrame: DataFrame actualizado con nuevas columnas codificadas.
        """
        original_features = self.features.copy()
        for col in columns:
            print(f"Valores únicos en {col}: {self.data[col].unique()}")

        self.data = pd.get_dummies(self.data, columns=columns)
        
        for col in columns:
            one_hot_cols = [c for c in self.data.columns if c.startswith(col + '_')]
            print(f"Columnas one-hot generadas para {col}: {one_hot_cols}")

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

    
    def a_label(self , columns: list[str]):
        """
        Aplica Label Encoding a columnas categóricas.

        Args:
            columns (list[str]): Lista de columnas a transformar.

        Returns:
            DataFrame: DataFrame con columnas codificadas.
        """
        for col in columns:
            self.data[col] = self.data[col].astype('category').cat.codes
        self.new_features = self.features
        return self.data
    
    def normalizar_min_max(self, columns: list[str]):
        """
        Aplica normalización Min-Max a las columnas especificadas.

        Args:
            columns (list[str]): Lista de columnas a normalizar.

        Returns:
            DataFrame: DataFrame con columnas normalizadas.
        """
        scaler = MinMaxScaler()
        self.data[columns] = scaler.fit_transform(self.data[columns])
        return self.data

    def normalizar_z_score(self, columns: list[str]):
        """
        Aplica normalización Z-Score a las columnas especificadas.

        Args:
            columns (list[str]): Lista de columnas a normalizar.

        Returns:
            DataFrame: DataFrame con columnas normalizadas.
        """
        scaler = StandardScaler()
        self.data[columns] = scaler.fit_transform(self.data[columns])
        return self.data
