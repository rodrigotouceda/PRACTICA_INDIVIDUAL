from FileReader import FileReader
import pandas as pd
from pathlib import Path
from DataManager import DataManager
import sqlite3
from dataVisualizer import VisualizerCLI
from FileExporter import ExporterCLI

class MenuCLI:
    def __init__(self):
        """
        Inicializa la clase MenuCLI con los estados del flujo de preprocesamiento,
        variables para almacenar los datos cargados, su versión procesada, y otros
        indicadores de estado.
        """
        self.estado = {
            "archivo_cargado": False, 
            "seleccion_columnas": False,
            "valores_faltantes": False,
            "transformacion": False,
            "normalizacion": False,
            "outliers": False,
            "visualizacion": False,
            "exportacion": False
        }

        self.nombre_archivo = None
        self.df = None
        self.dataManager = None
        self.preprocesado_completo = False
        self.df_original = None
        self.df_procesado = None
        self.no_datos_numericos = False

    def _mostrar_subetapas(self, indent=""):
        """
        Muestra en consola las subetapas del preprocesamiento con su estado actual.
        
        Args:
            indent (str): Sangría opcional para formatear visualmente el texto mostrado.
        """
        etapas = [
            ("seleccion_columnas", "2.1 Selección de columnas"),
            ("valores_faltantes", "2.2 Manejo de valores faltantes"),
            ("transformacion", "2.3 Transformación de datos categóricos"),
            ("normalizacion", "2.4 Normalización y escalado"),
            ("outliers", "2.5 Detección y manejo de valores atípicos"),
        ]
        requisitos = [
            None,
            "seleccion_columnas",
            "valores_faltantes",
            "transformacion",
            "normalizacion"
        ]

        for (clave, texto), req in zip(etapas, requisitos):
            if req and not self.estado[req]:
                print(f"{indent}[✗] {texto} (requiere {self._nombre_etapa(req)})")
            else:
                status = "[✓]" if self.estado[clave] else "[-]"
                estado_texto = "(completado)" if self.estado[clave] else "(pendiente)"
                print(f"{indent}{status} {texto} {estado_texto}")

    

    def _nombre_etapa(self, clave):
        """
        Retorna el nombre descriptivo de una etapa a partir de su clave interna.

        Args:
            clave (str): Clave de etapa como 'transformacion', 'normalizacion', etc.

        Returns:
            str: Nombre legible de la etapa.
        """
        nombres = {
            "seleccion_columnas": "selección de columnas",
            "valores_faltantes": "manejo de valores faltantes",
            "transformacion": "transformación categórica",
            "normalizacion": "normalización",
            "outliers": "detección de outliers"
        }
        return nombres.get(clave, clave)


    def cargar_datos(self):
        """
        Permite al usuario cargar un archivo de datos (CSV, Excel o base de datos SQLite).
        Actualiza los estados y estructuras internas con los datos cargados.
        """
        print("\n" + "=" * 29)
        print("Cargar datos")
        print("=" * 29)
        
        opcion = input("Seleccione el tipo de archivo a cargar:\n1 - CSV\n2 - Excel\n3 - SQLite\n> ")

        diccionario = {
            "1": "del archivo CSV",
            "2": "sel archivo Excel",
            "3": "de la base de datos"
        }
 
        if opcion == "1"  or opcion == "2":
            ruta = input(f"Ingrese la ruta {diccionario[opcion]}: ")
            ruta = Path(ruta)
            extension = ruta.suffix.lower()
            if (opcion == "1" and extension == ".csv") or (opcion == "2" and extension == ".xlsx"):
            
                reader = FileReader()
                try:
                    df = reader.parse_file(ruta)
                    self.df = df
                    self.df_original = df
                    self.dataManager = DataManager(df)
                    print("Datos cargados correctamente")
                    print("Número de filas: ", df.shape[0])
                    print("Número de columnas: ", df.shape[1])
                    print("Primeras filas :")
                    print(df.head())
                    print("Datos cargados correctamente")
                    self.estado["archivo_cargado"] = True
                    self._nombre_archivo = ruta.name
                except: 
                    print("\nError al cargar el archivo. Asegúrese de que el formato sea correcto.")
            else:
                print(f"\nError: La ruta del archivo no es correcta o no es del tipo especificado.")
                return

        elif opcion == "3":
            ruta = input(f"Ingrese la ruta {diccionario[opcion]}: ")
            ruta = Path(ruta)
            extension = ruta.suffix.lower()
            if extension not in [".db", ".sqlite", ".sqlite3"]:
                print("\nError: La ruta del archivo no es correcta o no es del tipo especificado.")
                return
            
            reader = FileReader()
            tablas = reader.get_db_tables(ruta)

            print("Tablas disponibles en la base de datos :")
            for i, tabla in enumerate(tablas, start=1):
                print(f"[{i}] {tabla}")

            tabla_seleccionada = input("Seleccione una tabla:")
            if tabla_seleccionada not in [str(i) for i in range(1, len(tablas) + 1)]:
                print("\nError: Tabla no válida.")
                return
            
            
            try:
                df = reader.parse_sqlite_table(ruta, tablas[int(tabla_seleccionada) - 1])
                self.df = df
                self.df_original = df
                self.dataManager = DataManager(df)
                print("Datos cargados correctamente")
                print("Número de filas: ", df.shape[0])
                print("Número de columnas: ", df.shape[1])
                print("Primeras filas :")
                print(df.head())
                print("Datos cargados correctamente")
                self.estado["archivo_cargado"] = True
                self._nombre_archivo = ruta.name
            except: 
                print("\nError al cargar el archivo. Asegúrese de que el formato sea correcto.")

        else:
            print("\nOpción no válida.")
            return
        

       
    def seleccion_columnas(self):
        """
        Permite al usuario seleccionar las columnas de entrada (features) y salida (target).
        Almacena la selección en el DataManager y actualiza el estado del sistema.
        """
        while True:
            print("\n" + "=" * 29)
            print("Selección de Columnas")
            print("=" * 29)
    
            print("\n Columnas disponibles en los datos: ")
            self.dataManager.mostrar_columnas()

            try:
                features = input("\nIngrese los números de las columnas de entrada (features), separados por comas: ")
                target = input("\nIngrese el número de la columna de salida (target): ")

                X, y = self.dataManager.seleccionar_columnas(features, target)

                if X is None or y is None:
                    continue
                
                print("\nSelección guardada:")
                print(f"Features = {X}")
                print(f"Target = {y}")
    
                # Confirmar selección
                confirm = input("\n¿Desea confirmar esta selección? (s/n): ").lower()
                if confirm == 's':
                    self.estado["seleccion_columnas"] = True
                    self.estado["preprocesado_habilitado"] = True  # Habilitar el preprocesado
                    break  # Salir del while
                else:
                    print("\n🔄 Volviendo a seleccionar columnas...")
    
            except ValueError:
                print("\n⚠️ Error: Entrada inválida.")

        
    
    def valores_faltantes(self):
        """
        Detecta y permite manejar valores faltantes en las columnas seleccionadas.
        Ofrece varias estrategias de imputación o eliminación.
        """
        while True:
            print("\n" + "=" * 29)
            print("Manejo de Valores Faltantes")
            print("=" * 29)

            self.dataManager.missing_values_columns = []
            valores_faltantes = False
            for i in self.dataManager.features:
                if self.dataManager.tiene_valores_faltantes(i):
                    valores_faltantes = True

            if not valores_faltantes:
                print("\nNo se han detectado valores faltantes en las columnas seleccionadas.")
                print("\nNo es necesario manejar los valores faltantes.")
                self.estado["valores_faltantes"] = True
                break


            print("\n Se han detectado valores faltantes en las siguientes columnas:")

            for x in self.dataManager.missing_values_columns:
                print(f"\t - {x}: {self.dataManager.data[x].isnull().sum()} valores faltantes")

            print("\n Seleccione una estrategia para manejar los valores faltantes:")
            print("\t[1] Eliminar filas con valores faltantes")
            print("\t[2] Rellenar con la media de la columna")
            print("\t[3] Rellenar con la mediana de la columna")
            print("\t[4] Rellenar con la moda de la columna")
            print("\t[5] Rellenar con un valor constante")
            print("\t[6] Regresar al menú principal")

            try:
                opcion = int(input("Seleccione una opción: "))

                if opcion == 6:
                    print("\n🔁 Volviendo al menú principal")
                    break

                managed_df = self.dataManager.manejar_valores_faltantes(self.dataManager.missing_values_columns, opcion)
                if managed_df is not None:
                    self.df = managed_df
                    self.dataManager.data = managed_df  
                    self.estado["valores_faltantes"] = True
                    print("\n Manejo de valores faltantes completado.")
                    break
            except:
                print("\nOpción no válida.")
                continue


    def transformacion_datos_categoricos(self):
        """
        Detecta columnas categóricas y permite al usuario transformarlas utilizando 
        técnicas como One-Hot Encoding o Label Encoding.
        """
        while True:
            print("\n" + "=" * 29)
            print("Transformación de Datos Categóricos")
            print("=" * 29)

            datos_categoricos = False
            self.dataManager.categoric_columns = []
            for i in self.dataManager.features:
                if self.dataManager.es_categorica(i):  
                    datos_categoricos = True


            if not datos_categoricos:
                print("\n No se han detectado columnas categóricas en las variables de entrada seleccionadas.")
                print("\n No es necesario aplicar ninguna transformación.")
                self.estado["transformacion"] = True
                break

            print("Se han detectado columnas categóricas en las variables de entrada seleccionadas: ")
            for i in self.dataManager.categoric_columns:
                print(f"\t - {i}")

            print("Seleccione una estrategia de transformación:")
            print("\t[1] One-Hot Encoding (genera nuevas columnas binarias)")
            print("\t[2] Label Encoding(convierte categorías a números enteros)")
            print("\t[3] Regresar al menú principal")
            try:
                opcion = int(input("Seleccione una opción:"))

                if opcion == 3:
                    print("\n🔁 Volviendo al menú principal")
                    break

                df_transformado = self.dataManager.a_categorica(self.dataManager.categoric_columns, opcion)
                if df_transformado is not None:

                    self.df = df_transformado
                    self.estado["transformacion"] = True
                    break
                else:
                    print("Opción no válida.")
                    continue
            except:
                print("\nOpción no válida.")
                continue
                
        
    def normalizacion(self):
        """
        Permite aplicar técnicas de normalización o escalado a las columnas numéricas
        de entrada: Min-Max o Z-score.
        """
        while True:    
            print("\n" + "=" * 29)
            print("Normalización y Escalado")
            print("=" * 29)
            datos_normalizables = False
            self.dataManager.normalizable_columns = []
            for i in self.dataManager.new_features:
                if self.dataManager.es_normalizable(i):  
                    datos_normalizables = True

            if not datos_normalizables:
                print("\n No se han detectado columnas numericas en las variables de entrada seleccionadas.")
                print("\n No es necesario aplicar ninguna normalización.")
                self.estado["normalizacion"] = True
                self.no_datos_numericos = True
                return

            print("Se han detectado columnas numéricas en las variables de entrada seleccionadas: ")
            for i in self.dataManager.normalizable_columns:
                print(f"\t - {i}")

            print("Seleccione una estrategia de normalización:")
            print("\t[1] Min-Max Scaling (escala valores entre 0 y 1)")
            print("\t[2] Z-score Normalization  (media 0, desviación estándar 1)")
            print("\t[3] Regresar al menú principal")

            try:
                opcion = int(input("Seleccione una opción:"))

                if opcion == 3:
                    print("\n🔁 Volviendo al menú principal")
                    break

                df_transformado = self.dataManager.normalizar(self.dataManager.normalizable_columns, opcion)
                if df_transformado is not None:
                    self.df = df_transformado
                    self.estado["normalizacion"] = True
                    self.preprocesado_completo = True
                    break
                else:
                    print("Opción no válida.")
                    continue

            except:
                print("\nOpción no válida.")
                continue

        

    def valores_atipicos(self):
        """
        Detecta valores atípicos en las columnas seleccionadas y permite manejarlos
        con distintas estrategias: eliminación, reemplazo por la mediana o mantenerlos.
        """
        while True:
            print("\n" + "=" * 29)
            print("Detección y Manejo de Valores Atípicos")
            print("=" * 29)

            self.dataManager.outlier_columns = []
            valores_atipicos = False
            for i in self.dataManager.new_features:
                if self.dataManager.tiene_outliers(i):  
                    valores_atipicos = True

            if not valores_atipicos:
                print("\n No se han detectado valores atípicos en las columnas seleccionadas.")
                print("\n No es necesario aplicar ninguna transformación.")
                self.estado["outliers"] = True
                self.preprocesado_completo = True
                break

            print("Se han detectado valores atípicos en las variables de entrada seleccionadas: ")
            for i in self.dataManager.outlier_columns:
                print(f"\t - {i}")

            print("Seleccione una estrategia de manejo de outliers:")
            print("\t[1] Eliminar filas con valores atípicos")
            print("\t[2] Reemplazar valores atípicos con la mediana de la columna")
            print("\t[3] Mantener valores atípicos sin cambios")
            print("\t[4] Volver al menú principal")
            try:
                opcion = int(input("Seleccione una opción: "))

                
                if opcion == 4:
                    print("\n🔁 Volviendo al menú principal") 
                    break

                df_sin_atipicos = self.dataManager.manejar_atipicos(self.dataManager.outlier_columns, opcion)
                if df_sin_atipicos is not None:

                    self.estado["outliers"] = True
                    self.preprocesado_completo = True
                    self.df = df_sin_atipicos
                    self.df_procesado = self.df
                    break
        
            except:
                print("\nERROR.")
                continue


    def visualizar_datos(self):
        """
        Llama a la herramienta de visualización si hay datos numéricos disponibles. 
        En caso contrario, muestra un mensaje de advertencia.
        """
        if self.no_datos_numericos:
            print('No hay variables numéricas necesarias para visualizar los datos')
            self.estado['visualizacion'] = True
            return
        
        if self.preprocesado_completo:
            visualizador = VisualizerCLI(self.df_original, self.df_procesado, self.dataManager.features, self.dataManager.new_features, self.dataManager)
            visualizador.mostrar_menu()

            if visualizador.visualizacion_completa():
                self.estado['visualizacion'] = True
            else:
                print("No es posible visualizar los datos hasta que se complete el preprocesado.")


        



    def iniciar(self):
        """
        Inicia el bucle principal de la aplicación CLI.

        Muestra el menú principal de forma continua y responde a las entradas del usuario,
        ejecutando las acciones correspondientes como carga de datos, preprocesamiento,
        visualización, exportación o salida.

        El flujo está guiado por el estado actual de la aplicación, y se valida
        que cada etapa se complete antes de habilitar la siguiente.

        Controla la expansión del submenú de preprocesamiento y verifica
        que se sigan los pasos en orden secuencial.
        """
        expandir = False
        while True:
            self.mostrar_menu(expandir)  # por defecto sin subetapas
            opcion = input()

            if opcion == "1":
                self.cargar_datos()
            elif opcion == "2":
                if not self.estado["archivo_cargado"]:
                    print("\nPrimero debe cargar un archivo.")
                else:
                    expandir = True  # 👈 mostrá subetapas como parte del menú

            elif opcion == "2.1":
                if not expandir:
                    print("Opción no disponible. Seleccione '2' para expandir el menú.")
                else:
                    self.seleccion_columnas()

            elif opcion == "2.2":
                if not expandir:
                    print("Opción no disponible. Seleccione '2' para expandir el menú.")
                elif not self.estado["seleccion_columnas"]:
                    print("\nPrimero debe seleccionar las columnas.")
                else:
                    self.valores_faltantes()

            elif opcion == "2.3":
                if not expandir:
                    print("Opción no disponible. Seleccione '2' para expandir el menú.")
                elif not self.estado["valores_faltantes"]:
                    print("\nPrimero debe manejar los valores faltantes.")
                else:
                    self.transformacion_datos_categoricos()

            elif opcion == "2.4":
                if not expandir:
                    print("Opción no disponible. Seleccione '2' para expandir el menú.")
                elif not self.estado["transformacion"]:
                    print("\nPrimero debe transformar los datos categóricos.")
                else:
                    self.normalizacion()

            elif opcion == "2.5":
                if not expandir:
                    print("Opción no disponible. Seleccione '2' para expandir el menú.")
                elif not self.estado["normalizacion"]:
                    print("\nPrimero debe normalizar y escalar los datos.")
                else:
                    self.valores_atipicos()

                    
            elif opcion == "3":
                if all([self.estado[k] for k in ["seleccion_columnas", "valores_faltantes", "transformacion", "normalizacion", "outliers"]]):
                    
                    self.visualizar_datos()
                    self.estado["visualización"] = True
                    print("\nVisualización de datos completada.")
                else:
                    print("\nDebe completar todo el preprocesado antes de visualizar.")
            elif opcion == "4":
                if self.estado["visualizacion"]:
                    exportador = ExporterCLI(self.df_procesado, self.estado)
                    exportador.exportar_datos()
                    self.estado["exportacion"] = True
                    print("\nDatos exportados correctamente.")
                else:
                    print("\nDebe completar la visualización antes de exportar.")
            elif opcion == "5":
                if self._confirmar_salida():
                    print("\nCerrando la aplicación...")
                    break
                else:
                    print("\nRegresando al menú principal...")
            else:
                print("\nOpción no válida.")


    def mostrar_menu(self, expandir_subetapas=False):
        """
        Muestra el menú principal de la aplicación, reflejando el estado actual de cada etapa.

        Si `expandir_subetapas` es True, también se listan las subetapas del preprocesamiento
        con indentación visual.

        Indica con símbolos el estado de cada módulo:
            [✓] Completado
            [-] Disponible pero no completado
            [✗] No disponible (por dependencia no satisfecha)

        Parameters:
            expandir_subetapas (bool): Si es True, se muestran las subetapas del preprocesado.
        """
        print("\n" + "=" * 29)
        print("Menú Principal")
        print("=" * 29)

        
        # Opción 1: Cargar datos
        archivo_estado = f"(archivo: {self._nombre_archivo})" if self.estado["archivo_cargado"] else "(ningún archivo cargado)"
        check = "[✓]" if self.estado["archivo_cargado"] else "[-]"
        print(f"{check} 1. Cargar datos {archivo_estado}")
 
        # Opción 2: Preprocesado
        if not self.estado["archivo_cargado"] and not self.preprocesado_completo:
            print("[✗] 2. Preprocesado de datos (requiere carga de datos)")
        elif self.estado["archivo_cargado"] and not self.preprocesado_completo:
            print("[-] 2. Preprocesado de datos")
            if expandir_subetapas:
                self._mostrar_subetapas(indent="\t")  # Le pasamos una tabulación
        else:
            check = "[✓]"
            print(f"{check} 2. Preprocesado de datos (completado)")
            self._mostrar_subetapas(indent="\t")


        # Opción 3: Visualización
        if all([self.estado[k] for k in ["seleccion_columnas", "valores_faltantes", "transformacion", "normalizacion", "outliers"]]):
            check = "[✓]" if self.estado["visualizacion"] else "[-]"
            print(f"{check} 3. Visualización de datos")
        else:
            print("[✗] 3. Visualización de datos (requiere preprocesado completo)")

        # Opción 4: Exportación
        if self.estado["visualizacion"]:
            check = "[✓]" if self.estado["exportacion"] else "[-]"
            print(f"{check} 4. Exportar datos")
        else:
            print("[✗] 4. Exportar datos (requiere visualización de datos)")

        print("[✓] 5. Salir")
        print("Seleccione una opción: ", end='')


    def _confirmar_salida(self):
        """
        Solicita al usuario confirmación antes de cerrar la aplicación.
    
        Muestra un mensaje con opciones para confirmar o cancelar la salida.
        
        Returns:
            bool: True si el usuario confirma la salida, False en caso contrario.
        """
        print("\n" + "=" * 29)
        print("Salir de la Aplicación")
        print("=" * 29)
        print("¿Está seguro de que desea salir?")
        print("  [1] Sí")
        print("  [2] No")
        opcion = input("Seleccione una opción: ")
        return opcion == "1"
