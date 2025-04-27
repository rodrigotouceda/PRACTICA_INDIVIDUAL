from FileReader import FileReader
import pandas as pd
from pathlib import Path
import sqlite3

class MenuCLI:
    def __init__(self):
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

        self._nombre_archivo = None
        self._df = None
        self._columns = None
        self._features = None
        self._target = None


    def _mostrar_subetapas(self, indent=""):
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
        nombres = {
            "seleccion_columnas": "selección de columnas",
            "valores_faltantes": "manejo de valores faltantes",
            "transformacion": "transformación categórica",
            "normalizacion": "normalización",
            "outliers": "detección de outliers"
        }
        return nombres.get(clave, clave)


    def cargar_datos(self):
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
                    self._df = df
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
                self._df = df
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
        


       
    def _seleccion_columnas(self):
        while True:
            print("\n" + "=" * 29)
            print("Selección de Columnas")
            print("=" * 29)
            self._columns = self._df.columns.tolist()
    
            print("\n Columnas disponibles en los datos: ")
            for i, col in enumerate(self._columns, start=0):
                print("\t [{}] {}".format(i, col))
    
            try:
                features_input = input("\nIngrese los números de las columnas de entrada (features), separados por comas: ")
                target_input = input("\nIngrese el número de la columna de salida (target): ")
    
                # Validaciones básicas
                features_indices = [int(i.strip()) for i in features_input.split(",") if i.strip() != ""]
                target_index = int(target_input.strip())
    
                if not features_indices:
                    print("\n⚠️ Error: Debe seleccionar al menos una columna como feature.")
                    continue
                
                if target_index in features_indices:
                    print("\n⚠️ Error: La columna target no puede ser una de las features.")
                    continue
                
                if any(i < 0 or i >= len(self._columns) for i in features_indices + [target_index]):
                    print("\n⚠️ Error: Has ingresado un número de columna que no existe.")
                    continue
                
                # Convertir a nombres de columnas
                features = [self._columns[i] for i in features_indices]
                target = self._columns[target_index]
    
                print("\nSelección guardada:")
                print(f"Features = {features}")
                print(f"Target = {target}")
    
                # Confirmar selección
                confirm = input("\n¿Desea confirmar esta selección? (s/n): ").lower()
                if confirm == 's':
                    self.estado["seleccion_columnas"] = True
                    self.estado["preprocesado_habilitado"] = True  # Habilitar el preprocesado
                    self._features = features
                    self._target = target
                    break  # Salir del while
                else:
                    print("\n🔄 Volviendo a seleccionar columnas...")
    
            except ValueError:
                print("\n⚠️ Error: Entrada inválida.")

        
        



    def iniciar(self):
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
                self._seleccion_columnas()

                    
            elif opcion == "3":
                if all([self.estado[k] for k in ["seleccion_columnas", "valores_faltantes", "transformacion", "normalizacion", "outliers"]]):
                    self.estado["visualizacion"] = True
                    print("\nVisualización completada.")
                else:
                    print("\nDebe completar todo el preprocesado antes de visualizar.")
            elif opcion == "4":
                if self.estado["visualizacion"]:
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
        print("\n" + "=" * 29)
        print("Menú Principal")
        print("=" * 29)

        # Opción 1: Cargar datos
        archivo_estado = f"(archivo: {self._nombre_archivo})" if self.estado["archivo_cargado"] else "(ningún archivo cargado)"
        check = "[✓]" if self.estado["archivo_cargado"] else "[-]"
        print(f"{check} 1. Cargar datos {archivo_estado}")

        # Opción 2: Preprocesado
        if not self.estado["archivo_cargado"]:
            print("[✗] 2. Preprocesado de datos (requiere carga de datos)")
        else:
            print("[-] 2. Preprocesado de datos")
            if expandir_subetapas:
                self._mostrar_subetapas(indent="\t")  # Le pasamos una tabulación


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



    def _navegar_preprocesado(self):
           
            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                self._seleccion_columnas()
            elif opcion == "2":
                if not self.estado["seleccion_columnas"]:
                    print("\nPrimero debe seleccionar las columnas.")
                else:
                    self.estado["valores_faltantes"] = True
                    print("\nManejo de valores faltantes completado.")
            elif opcion == "3":
                if not self.estado["valores_faltantes"]:
                    print("\nPrimero debe manejar los valores faltantes.")
                else:
                    self.estado["transformacion"] = True
                    print("\nTransformación de datos categóricos completada.")
            elif opcion == "4":
                if not self.estado["transformacion"]:
                    print("\nPrimero debe transformar los datos categóricos.")
                else:
                    self.estado["normalizacion"] = True
                    print("\nNormalización y escalado completados.")
            elif opcion == "5":
                if not self.estado["normalizacion"]:
                    print("\nPrimero debe normalizar y escalar los datos.")
                else:
                    self.estado["outliers"] = True
                    print("\nDetección y manejo de valores atípicos completados.")
            else:
                print("\nOpción no válida.")



    def _confirmar_salida(self):
        print("\n" + "=" * 29)
        print("Salir de la Aplicación")
        print("=" * 29)
        print("¿Está seguro de que desea salir?")
        print("  [1] Sí")
        print("  [2] No")
        opcion = input("Seleccione una opción: ")
        return opcion == "1"
