# Proyecto-SO

# Simulador de Memoria Virtual

Este proyecto es un simulador de memoria virtual que implementa diferentes algoritmos de reemplazo de páginas, diseñado para ayudar a comprender los conceptos fundamentales de la gestión de memoria en sistemas operativos.
- **Alumno: Aaron Isaac Lopez**
- **Cuenta: 20211900269**

---

## ✨ Características principales

### 🔁 Algoritmos implementados

- **FIFO** (First-In, First-Out)  
- **LRU** (Least Recently Used)  
- **Óptimo** *(esqueleto para implementación futura)*

### 🖥️ Interfaz gráfica

- Visualización del estado de la memoria física  
- Tabla de páginas con estado de cada página  
- Gráficos estadísticos de accesos  
- Controles interactivos para la simulación

### ⚙️ Funcionalidades

- Creación de procesos con páginas aleatorias  
- Simulación de accesos aleatorios a memoria  
- Secuencia de prueba predefinida  
- Estadísticas en tiempo real (fallos de página, tasa de aciertos)

---

## 🧰 Requisitos del sistema

- Python **3.6** o superior

### Bibliotecas requeridas

- `tkinter` *(incluido en la instalación estándar de Python)*  
- `matplotlib`  
- `collections` *(incluido en la instalación estándar de Python)*

---

## 🛠️ Instalación

1. Clonar el repositorio o descargar el código fuente.
2. Instalar las dependencias con:

   ```bash
   pip install matplotlib

### Instrucciones de operación

-**1. Configurar el número de marcos físicos**  
2. Seleccionar el algoritmo de reemplazo deseado  
3. Crear un nuevo proceso (generará páginas aleatorias)  
4. Simular accesos a memoria con los botones correspondientes  
5. Ver resultados en tiempo real en la interfaz

## 🧩 Estructura del código

### Clase `VirtualMemorySimulator`

Contiene toda la lógica de simulación y la interfaz gráfica.

- `__init__`: Inicializa la simulación y la interfaz  
- **Métodos de simulación**: `access_page`, `handle_page_fault`  
- **Métodos de UI**: `setup_ui`, `update_display`, `setup_stats_chart`  
- **Métodos de control**: `create_process`, `simulate_access`, `reset_simulation`

---

## 📚 Algoritmos implementados

### FIFO (First-In, First-Out)

Mantiene una cola de páginas en memoria. Cuando ocurre un fallo de página, reemplaza la página que lleva más tiempo en memoria.

### LRU (Least Recently Used)

Mantiene un registro del uso de páginas. Reemplaza la página que no ha sido utilizada por más tiempo.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Algunas áreas para mejorar incluyen:

- Implementación completa del algoritmo Óptimo  
- Más secuencias de prueba  
- Visualizaciones adicionales  
- Soporte para múltiples procesos concurrentes

---

## 📄 Licencia

Este proyecto está bajo la licencia [MIT](https://opensource.org/licenses/MIT).