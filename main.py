import random
from collections import deque, OrderedDict
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class VirtualMemorySimulator:
    """
    Simula el comportamiento de la memoria virtual con diferentes algoritmos
    de reemplazo de páginas: FIFO, LRU y Óptimo (no implementado).
    Incluye una interfaz gráfica para facilitar la interacción.
    """
    def __init__(self, root):
        """
        Inicializa el simulador de memoria virtual.
        
        Args:
            root (tk.Tk): Ventana principal de Tkinter.
        """
        self.root = root
        self.root.title("Simulador de Memoria Virtual")
        
        # Configuración inicial
        self.physical_frames = 4
        self.page_size = 1024  # 1KB
        self.processes = []
        self.current_process_id = 0
        self.page_faults = 0
        self.algorithm = "FIFO"
        self.simulation_speed = 1
        self.access_history = []
        
        # Estilo visual
        self.setup_styles()

        # Inicializar la memoria física
        self.reset_memory()
        
        # Configurar la interfaz
        self.setup_ui()

        # Gráficos
        self.setup_stats_chart()
    def setup_styles(self):
        """
        Configura estilos visuales para la interfaz
        """
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 9))
        style.configure('TButton', font=('Helvetica', 9), padding=5)
        style.configure('Title.TLabel', font=('Helvetica', 12, 'bold'))
        style.map('TButton', 
                 background=[('active', '#4CAF50'), ('pressed', '#45a049')],
                 foreground=[('pressed', 'white'), ('active', 'white')])
    def reset_memory(self):
        """
        Reinicia la memoria física y las estructuras necesarias para el manejo de páginas.
        """
        self.physical_memory = [None] * self.physical_frames
        self.page_table = {}  # {page_id: frame_id or None}
        self.fifo_queue = deque()
        self.lru_cache = OrderedDict()
        self.page_faults = 0
        self.hits = 0
        self.access_history = []
    
    def setup_ui(self):
        """
        Crea y organiza los elementos de la interfaz gráfica del simulador.
        """
        # Panel principal con pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)
        # Pestaña de Simulación
        sim_frame = ttk.Frame(notebook)
        notebook.add(sim_frame, text="Simulación")
        # Panel de control
        control_frame = ttk.LabelFrame(sim_frame, text="Controles", padding=10)
        control_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # Configuración de memoria
        ttk.Label(control_frame, text="Marcos físicos:").grid(row=0, column=0, sticky=tk.W)
        self.frames_entry = ttk.Entry(control_frame, width=5)
        self.frames_entry.insert(0, str(self.physical_frames))
        self.frames_entry.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(control_frame, text="Algoritmo:").grid(row=1, column=0, sticky=tk.W)
        self.algorithm_var = tk.StringVar(value=self.algorithm)
        algo_menu = ttk.OptionMenu(control_frame, self.algorithm_var, 
                                  "FIFO", "FIFO", "LRU", "Óptimo")
        algo_menu.grid(row=1, column=1, sticky=tk.W)
        

        # Botones de accion
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Nuevo Proceso", 
                  command=self.create_process).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Simular Acceso", 
                  command=self.simulate_access).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Secuencia Test", 
                  command=self.run_test_sequence).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reiniciar", 
                  command=self.reset_simulation).pack(side=tk.LEFT, padx=5)
        
        # Visualización de memoria
        mem_frame = ttk.LabelFrame(sim_frame, text="Estado de la Memoria", padding=10)
        mem_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.mem_canvas = tk.Canvas(mem_frame, bg="white", highlightthickness=0)
        self.mem_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de Estadísticas
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Estadísticas")
        
        self.stats_label = ttk.Label(stats_frame, 
                                   text="Fallos de página: 0 | Aciertos: 0 | Tasa aciertos: 0%",
                                   font=('Helvetica', 10, 'bold'))
        self.stats_label.pack(pady=10)
        
        self.chart_frame = ttk.Frame(stats_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
    
    def setup_stats_chart(self):
        """
        Configura el gráfico de estadísticas
        """
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.ax.set_title('Historial de Accesos')
        self.ax.set_xlabel('Accesos')
        self.ax.set_ylabel('Tipo')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    def update_stats_chart(self):
        """
        Actualiza el gráfico con el historial de accesos
        """
        self.ax.clear()
        
        if not self.access_history:
            return
            
        x = range(1, len(self.access_history)+1)
        y = [1 if access['type'] == 'hit' else 0 for access in self.access_history]
        
        self.ax.scatter(x, y, c=['green' if v == 1 else 'red' for v in y], s=50)
        self.ax.set_yticks([0, 1])
        self.ax.set_yticklabels(['Fallo', 'Acierto'])
        self.ax.set_title(f'Historial de Accesos (Aciertos: {self.hits}/{len(self.access_history)})')
        self.canvas.draw()    
    def create_process(self):
        """
        Crea un nuevo proceso con un número aleatorio de páginas y reinicia la simulación.
        """
        try:
            self.physical_frames = int(self.frames_entry.get())
            if self.physical_frames <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Número de marcos no válido")
            return
        
        self.reset_memory()
        self.algorithm = self.algorithm_var.get()
        self.current_process_id += 1
        
        # Crear un nuevo proceso con páginas aleatorias
        process_pages = random.randint(3, 10)
        self.page_table = {f"P{self.current_process_id}-{i}": None 
                          for i in range(process_pages)}
        self.update_display()
        messagebox.showinfo("Proceso creado", 
                          f"Proceso {self.current_process_id} creado con {process_pages} páginas")
        
    def simulate_access(self):
        """
        Simula un acceso aleatorio a una página del proceso actual.
        """
        if not self.page_table:
            messagebox.showwarning("Advertencia", "No hay proceso creado")
            return
        
        # Seleccionar una página al azar para acceder
        page_id = random.choice(list(self.page_table.keys()))
        self.access_page(page_id)
        self.update_display()

    def run_test_sequence(self):
        """
        Ejecuta una secuencia de prueba predefinida
        """
        if not self.page_table:
            messagebox.showwarning("Advertencia", "Crea un proceso primero")
            return
            
        test_sequence = ["P1-0", "P1-1", "P1-2", "P1-3", "P1-0", "P1-1", "P1-4"]
        
        for page in test_sequence:
            if page not in self.page_table:
                messagebox.showwarning("Error", f"La página {page} no existe en el proceso actual")
                return
                
        for page in test_sequence:
            self.access_page(page)
            self.update_display()
            self.root.update()
            time.sleep(1)
    
    def access_page(self, page_id):
        """
        Accede a una página. Si no está en memoria, se produce un fallo de página.
        
        Args:
            page_id (str): Identificador de la página.
        """
        # Verificar si la página está en memoria
        is_hit = self.page_table[page_id] is not None
        
        if is_hit:
            self.hits += 1
            if self.algorithm == "LRU":
                self.lru_cache.move_to_end(page_id)
            self.access_history.append({'page': page_id, 'type': 'hit'})
            return True
        else:
            self.page_faults += 1
            self.handle_page_fault(page_id)
            self.access_history.append({'page': page_id, 'type': 'fault'})
            return False
    
    def handle_page_fault(self, page_id):
        """
        Maneja el reemplazo de página en caso de fallo, según el algoritmo seleccionado.
        """
        # Buscar un marco libre
        for i, frame in enumerate(self.physical_memory):
            if frame is None:
                self.physical_memory[i] = page_id
                self.page_table[page_id] = i
                
                # Actualizar estructuras de algoritmos
                if self.algorithm == "FIFO":
                    self.fifo_queue.append(page_id)
                elif self.algorithm == "LRU":
                    self.lru_cache[page_id] = i
                return
        
        # No hay marcos libres, aplicar reemplazo
        if self.algorithm == "FIFO":
            # Implementación de FIFO
            victim_page = self.fifo_queue.popleft()
            victim_frame = self.page_table[victim_page]
            
            self.physical_memory[victim_frame] = page_id
            self.page_table[victim_page] = None
            self.page_table[page_id] = victim_frame
            
            self.fifo_queue.append(page_id)
        
        elif self.algorithm == "LRU":
            # Implementación de LRU
            victim_page, victim_frame = self.lru_cache.popitem(last=False)
            
            self.physical_memory[victim_frame] = page_id
            self.page_table[victim_page] = None
            self.page_table[page_id] = victim_frame
            
            self.lru_cache[page_id] = victim_frame
        
        elif self.algorithm == "Óptimo":
            # Implementación del algoritmo óptimo (no realista en práctica)
            # En una simulación real necesitarías conocer las referencias futuras
            pass
    
    def update_display(self):
        """
        Actualiza visualmente el estado de la memoria y la tabla de páginas.
        """
        self.mem_canvas.delete("all")
        
        # Dibujar marcos de memoria física
        frame_width = 120
        frame_height = 80
        margin = 20
        start_x = margin
        start_y = margin
        
        for i, page in enumerate(self.physical_memory):
            x0 = start_x
            y0 = start_y + i * (frame_height + margin)
            x1 = x0 + frame_width
            y1 = y0 + frame_height
            
            color = "#90CAF9" if page else "#E0E0E0"  # Azul si está ocupado, gris si está libre
            outline = "#2E7D32" if page else "#9E9E9E"

            self.mem_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=outline, width=2)
            self.mem_canvas.create_text((x0+x1)/2, y0+15, 
                                      text=f"Marco {i}", 
                                      font=('Helvetica', 9, 'bold'))
            self.mem_canvas.create_text((x0+x1)/2, (y0+y1)/2, 
                               text=f"Marco {i}\n{page if page else 'Libre'}",
                               font=("Helvetica", 10))
        
        # Dibujar tabla de páginas
        table_x = start_x + frame_width + 2*margin
        table_y = start_y
        
        self.mem_canvas.create_text(table_x, table_y-20, 
                                   text="Tabla de Páginas", anchor=tk.W)
        
        for i, (page, frame) in enumerate(self.page_table.items()):
            status = f"Marco {frame}" if frame is not None else "Disco"
            color = "#2E7D32" if frame is not None else "#F44336"
            
            self.mem_canvas.create_text(table_x, table_y + i*20, 
                                       text=f"{page}: {status}", 
                                       font=('Courier', 9),
                                       fill=color,
                                       anchor=tk.W)
        
        # Actualizar estadísticas
        total_accesses = len(self.access_history)
        hit_rate = (self.hits / total_accesses) * 100 if total_accesses > 0 else 0
        
        self.stats_label.config(
            text=f"Fallos de página: {self.page_faults} | Aciertos: {self.hits} | Tasa aciertos: {hit_rate:.1f}%"
        )
        
        self.update_stats_chart()
    
    def reset_simulation(self):
        """
        Reinicia por completo la simulación de memoria y la interfaz visual.
        """
        self.reset_memory()
        self.current_process_id = 0
        self.update_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualMemorySimulator(root)
    root.geometry("800x600")
    root.mainloop()