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

    def mostrar_menu(self):
        print("\n" + "=" * 29)
        print("Menú Principal")
        print("=" * 29)

        # Opción 1: Cargar datos
        archivo_estado = "(archivo: datos.csv)" if self.estado["archivo_cargado"] else "(ningún archivo cargado)"
        check = "[✓]" if self.estado["archivo_cargado"] else "[-]"
        print(f"{check} 1. Cargar datos {archivo_estado}")

        # Opción 2: Preprocesado
        if not self.estado["archivo_cargado"]:
            print("[✗] 2. Preprocesado de datos (requiere carga de datos)")
        else:
            print("[-] 2. Preprocesado de datos")
            self._mostrar_subetapas()

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

    def _mostrar_subetapas(self):
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
                print(f"[✗] {texto} (requiere {self._nombre_etapa(req)})")
            else:
                status = "[✓]" if self.estado[clave] else "[-]"
                estado_texto = "(completado)" if self.estado[clave] else "(pendiente)"
                print(f"{status} {texto} {estado_texto}")

    def _nombre_etapa(self, clave):
        nombres = {
            "seleccion_columnas": "selección de columnas",
            "valores_faltantes": "manejo de valores faltantes",
            "transformacion": "transformación categórica",
            "normalizacion": "normalización",
            "outliers": "detección de outliers"
        }
        return nombres.get(clave, clave)

    def iniciar(self):
        while True:
            self.mostrar_menu()
            opcion = input()

            if opcion == "1":
                self.estado["archivo_cargado"] = True
                print("\nDatos cargados correctamente.")
            elif opcion == "2":
                if not self.estado["archivo_cargado"]:
                    print("\nPrimero debe cargar un archivo.")
                else:
                    self._navegar_preprocesado()
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

    def _navegar_preprocesado(self):
        print("\n-- Preprocesado --")
        print("Seleccione subetapa:")
        print("  1. Selección de columnas")
        print("  2. Manejo de valores faltantes")
        print("  3. Transformación categórica")
        print("  4. Normalización y escalado")
        print("  5. Manejo de outliers")
        subop = input("Opción: ")
        mapeo = {
            "1": "seleccion_columnas",
            "2": "valores_faltantes",
            "3": "transformacion",
            "4": "normalizacion",
            "5": "outliers"
        }
        etapa = mapeo.get(subop)
        if etapa:
            requisitos = {
                "valores_faltantes": "seleccion_columnas",
                "transformacion": "valores_faltantes",
                "normalizacion": "transformacion",
                "outliers": "normalizacion"
            }
            req = requisitos.get(etapa)
            if req and not self.estado[req]:
                print(f"\nPrimero debe completar: {self._nombre_etapa(req)}.")
            else:
                self.estado[etapa] = True
                print(f"\nEtapa '{self._nombre_etapa(etapa)}' completada.")
        else:
            print("\nSubopción no válida.")

    def _confirmar_salida(self):
        print("\n" + "=" * 29)
        print("Salir de la Aplicación")
        print("=" * 29)
        print("¿Está seguro de que desea salir?")
        print("  [1] Sí")
        print("  [2] No")
        opcion = input("Seleccione una opción: ")
        return opcion == "1"
