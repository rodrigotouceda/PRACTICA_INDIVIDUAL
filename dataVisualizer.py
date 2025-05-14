import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from DataManager import DataManager

class VisualizerCLI:
    def __init__(self, df_original: pd.DataFrame, df_procesado: pd.DataFrame, original_features: list[str], processed_features: list[str], data_manager: DataManager):
        
        self.df_original = df_original
        self.df_procesado = df_procesado
        self.visualizacion_completada = False
        self.original_features = original_features
        self.processed_features = processed_features
        self.data_manager = data_manager
        self.og_categorical_features = []
        self.new_categorical_features = []
        self.og_numerical_features = []
        self.one_hot_features = []
        self.new_numerical_features = []

        for feature in self.original_features:
            
            if self.data_manager.is_categorical(feature, True):
                self.og_categorical_features.append(feature)
            elif self.data_manager.is_normalizable(feature, True):
                self.og_numerical_features.append(feature)

        for feature in self.processed_features:
            if feature in self.data_manager.one_hot_features:
                self.one_hot_features.append(feature)
            elif feature in self.og_categorical_features:
                self.new_categorical_features.append(feature)
            elif feature in self.og_numerical_features:
                self.new_numerical_features.append(feature)
        

    def mostrar_menu(self):
        while True:
            print("\n=============================")
            print("Visualización de Datos")
            print("=============================")
            print("Seleccione qué tipo de visualización desea generar:")
            print("  [1] Resumen estadístico de las variables seleccionadas")
            print("  [2] Histogramas de variables numéricas")
            print("  [3] Gráficos de dispersión antes y después de la normalización")
            print("  [4] Heatmap de correlación de variables numéricas")
            print("  [5] Volver al menú principal")

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                self.mostrar_resumen_estadistico()
            elif opcion == "2":
                self.mostrar_histogramas_variables_numericas()
            elif opcion == "3":
                self.graficos_dispersion()
            elif opcion == "4":
                self.generar_heatmap()
            elif opcion == "5":
                self.visualizacion_completada = True
                print("\n[✓] Visualización completada.")
                break
            else:
                print("Opción no válida. Inténtelo de nuevo.")

    def mostrar_resumen_estadistico(self):
            
        print("\nResumen estadístico de las variables seleccionadas (antes del preprocesado):")
        print("\n================================================================")
        print("Resumen estadístico de variables categóricas (ANTES del preprocesado):")
        print("================================================================")

        resumen_categorico = []
        for feature in self.og_categorical_features:
            frecuencia = self.df_original[feature].value_counts()
            proporciones = self.df_original[feature].value_counts(normalize=True)
            moda = self.df_original[feature].mode()[0]
            num_unicas = self.df_original[feature].nunique()
            nulos = self.df_original[feature].isnull().sum()
            for categoria in frecuencia.index:
                resumen_categorico.append({
                    "Variable": feature,
                    "Categoría": categoria,
                    "Frecuencia": frecuencia[categoria],
                    "Proporción (%)": proporciones[categoria] * 100,
                    "Moda": moda,
                    "Número de categorías únicas": num_unicas,
                    "Número de valores nulos": nulos
                })

        resumen_df = pd.DataFrame(resumen_categorico)
        print(resumen_df.to_string(index=False))

        print("\n================================================================")
        print("Resumen estadístico de variables numéricas (ANTES del preprocesado):")
        print("================================================================")

        resumen_numerico = []
        for feature in self.og_numerical_features:
            media = self.df_original[feature].mean()
            mediana = self.df_original[feature].median()
            desviacion = self.df_original[feature].std()
            minimo = self.df_original[feature].min()
            maximo = self.df_original[feature].max()
            nulos = self.df_original[feature].isnull().sum()
            resumen_numerico.append({
                "Variable": feature,
                "Media": media,
                "Mediana": mediana,
                "Desviación estándar": desviacion,
                "Mínimo": minimo,
                "Máximo": maximo,
                "0.25 ": self.df_original[feature].quantile(0.25),
                "0.50": self.df_original[feature].quantile(0.50),
                "0.75": self.df_original[feature].quantile(0.75),
                "Número de valores nulos": nulos
            })
        resumen_df_numerico = pd.DataFrame(resumen_numerico)
        print(resumen_df_numerico.to_string(index=False))

        print("\n================================================================")
        print("Resumen estadístico de variables categóricas (DESPUÉS del preprocesado):")
        print("================================================================")
        
        resumen_categorico_procesado = []
        lista_columnas = []
        if len(self.one_hot_features) > 0:
            lista_columnas = self.one_hot_features
        else:
            lista_columnas = self.new_categorical_features

        for feature in lista_columnas:
            frecuencia = self.df_procesado[feature].value_counts()
            proporciones = self.df_procesado[feature].value_counts(normalize=True)
            moda_serie = self.df_procesado[feature].mode()
            moda = moda_serie[0] if not moda_serie.empty else None  # o "Sin moda"
            num_unicas = self.df_procesado[feature].nunique()
            nulos = self.df_procesado[feature].isnull().sum()
            for categoria in frecuencia.index:
                resumen_categorico_procesado.append({
                    "Variable": feature,
                    "Categoría": categoria,
                    "Frecuencia": frecuencia[categoria],
                    "Proporción (%)": proporciones[categoria] * 100,
                    "Moda": moda,
                    "Número de categorías únicas": num_unicas,
                    "Número de valores nulos": nulos
                })
        resumen_df_procesado = pd.DataFrame(resumen_categorico_procesado)
        print(resumen_df_procesado.to_string(index=False))

        print("\n================================================================")
        print("Resumen estadístico de variables numéricas (DESPUÉS del preprocesado):")
        print("================================================================")

        resumen_numerico_procesado = []
        for feature in self.new_numerical_features:
            media = self.df_procesado[feature].mean()
            mediana = self.df_procesado[feature].median()
            desviacion = self.df_procesado[feature].std()
            minimo = self.df_procesado[feature].min()
            maximo = self.df_procesado[feature].max()
            nulos = self.df_procesado[feature].isnull().sum()
            resumen_numerico_procesado.append({
                "Variable": feature,
                "Media": media,
                "Mediana": mediana,
                "Desviación estándar": desviacion,
                "Mínimo": minimo,
                "Máximo": maximo,
                "0.25 ": self.df_procesado[feature].quantile(0.25),
                "0.50": self.df_procesado[feature].quantile(0.50),
                "0.75": self.df_procesado[feature].quantile(0.75),
                "Número de valores nulos": nulos
            })
        
        resumen_df_numerico_procesado = pd.DataFrame(resumen_numerico_procesado)
        print(resumen_df_numerico_procesado.to_string(index=False))
        print("\n================================================================")



        
    def mostrar_histogramas_variables_numericas(self):
        print("\n=======================================")
        print("Histograma de variables numéricas (ANTES del preprocesado):")
        print("=======================================")
        for col in self.og_numerical_features:
            plt.figure(figsize=(6, 4))
            sns.histplot(self.df_original[col].dropna(), bins=30, kde=True, color='skyblue')
            plt.title(f'Histograma de {col} (Original)')
            plt.xlabel(col)
            plt.ylabel('Frecuencia')
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        print("\n=======================================")
        print("Histograma de variables numéricas (DESPUÉS del preprocesado):")
        print("=======================================")
        for col in self.new_numerical_features:
            plt.figure(figsize=(6, 4))
            sns.histplot(self.df_procesado[col].dropna(), bins=30, kde=True, color='lightgreen')
            plt.title(f'Histograma de {col} (Procesado)')
            plt.xlabel(col)
            plt.ylabel('Frecuencia')
            plt.grid(True)
            plt.tight_layout()
            plt.show()

    def graficos_dispersion(self):
        print("\nGenerando gráficos de dispersión (antes vs. después)...")
        num_cols = self.df_original.select_dtypes(include='number').columns.intersection(self.df_procesado.columns)

        for col in num_cols:
            plt.figure(figsize=(6, 6))
            plt.scatter(self.df_original[col], self.df_procesado[col], alpha=0.5)
            plt.xlabel(f"{col} (original)")
            plt.ylabel(f"{col} (normalizado)")
            plt.title(f"Dispersión: {col} antes vs. después")
            plt.grid(True)
            plt.show()

    def generar_heatmap(self):
        print("\nGenerando heatmap de correlación (post-preprocesado)...")
        corr = self.df_procesado.select_dtypes(include='number').corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title("Mapa de calor de correlación (post-preprocesado)")
        plt.tight_layout()
        plt.show()

    def visualizacion_completa(self):
        return self.visualizacion_completada
