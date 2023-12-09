import tkinter as tk
from tkinter import ttk
import speedtest
from PIL import Image, ImageTk 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from itertools import count
import threading
import time
from ping3 import ping, verbose_ping

class Measurement:
    def __init__(self, app):
        self.app = app

    def measure_ping(self):
        self.app.reset_labels()
        self.app.progress_label.config(text="Midiendo ping...", foreground='#333')

        try:
            target_url = self.app.url_entry.get()
            ping_result = ping(target_url, unit='ms')
            self.app.display_result(self.app.download_result_label, f"Ping: {ping_result:.2f} ms", '#4CAF50')
        except (OSError, ValueError) as e:
            self.app.display_result(self.app.download_result_label, f"Error: {str(e)}", 'red')
        except Exception as e:
            self.app.display_result(self.app.download_result_label, f"Error: {str(e)}", 'red')

    def measure_latency(self):
        self.app.reset_labels()
        self.app.progress_label.config(text="Midiendo latencia...", foreground='#333')

        try:
            target_url = self.app.url_entry.get()
            verbose_ping(target_url, count=4)  # Ping 4 veces para medir latencia
            latency_result = verbose_ping(target_url, count=4)['avg']
            self.app.display_result(self.app.upload_result_label, f"Latencia: {latency_result:.2f} ms", '#4CAF50')
        except OSError as os_error:
            self.app.display_result(self.app.upload_result_label, f"Error de sistema: {str(os_error)}", 'red')
        except ValueError as value_error:
            self.app.display_result(self.app.upload_result_label, f"Error de valor: {str(value_error)}", 'red')
        except Exception as e:
            self.app.display_result(self.app.upload_result_label, f"Error: {str(e)}", 'red')

    def measure_packet_loss(self):
        self.app.reset_labels()
        self.app.progress_label.config(text="Midiendo pérdida de paquetes...", foreground='#333')

        try:
            target_url = self.app.url_entry.get()
            packet_loss_result = verbose_ping(target_url, count=4)['packet_loss']
            self.app.display_result(self.app.progress_label, f"Pérdida de paquetes: {packet_loss_result}%", '#4CAF50')
        except OSError as os_error:
            self.app.display_result(self.app.progress_label, f"Error de sistema: {str(os_error)}", 'red')
        except ValueError as value_error:
            self.app.display_result(self.app.progress_label, f"Error de valor: {str(value_error)}", 'red')
        except Exception as e:
            self.app.display_result(self.app.progress_label, f"Error: {str(e)}", 'red')

    def measure_download(self):
        self.app.reset_labels()
        self.app.progress_label.config(text="Midiendo velocidad de descarga...", foreground='#333')

        try:
            st = speedtest.Speedtest()
            download_speed = st.download() / 1_000_000  # convertir a megabits
            self.app.display_result(self.app.download_result_label, f"Velocidad de descarga: {download_speed:.2f} Mbps", '#4CAF50')
        except Exception as e:
            self.app.display_result(self.app.download_result_label, f"Error: {str(e)}", 'red')

    def measure_upload(self):
        self.app.reset_labels()
        self.app.progress_label.config(text="Midiendo velocidad de subida...", foreground='#333')

        try:
            st = speedtest.Speedtest()
            upload_speed = st.upload() / 1_000_000  # convertir a megabits
            self.app.display_result(self.app.upload_result_label, f"Velocidad de subida: {upload_speed:.2f} Mbps", '#4CAF50')
        except Exception as e:
            self.app.display_result(self.app.upload_result_label, f"Error: {str(e)}", 'red')


class SpeedTestApp(tk.Tk):
    def __init__(self):
        super().__init__()
    
        self.title("Speed Test")
        self.geometry("600x400")

        # Cargar la imagen de fondo
        background_image = Image.open("fondo.jpg")
        background_image = background_image.resize((1080, 13000), Image.ANTIALIAS)
        self.background_photo = ImageTk.PhotoImage(background_image)

        background_label = ttk.Label(self, image=self.background_photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(padx=20, pady=20)

        ttk.Label(self.main_frame, text="URL:").grid(row=0, column=0, columnspan=2, pady=10)

        self.url_entry = ttk.Entry(self.main_frame, width=30)
        self.url_entry.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Label(self.main_frame, text="Medir Velocidad de Descarga y Subida", font=('DIN', 12)).grid(row=2, column=0, columnspan=2, pady=10)

        # Crear la instancia de Measurement
        self.measurement = Measurement(self)

        self.download_button = ttk.Button(self.main_frame, text="Medir Descarga", command=self.measurement.measure_download, style='TButton')
        self.download_button.grid(row=3, column=0, pady=10, sticky='e')
        self.upload_button = ttk.Button(self.main_frame, text="Medir Subida", command=self.measurement.measure_upload, style='TButton')
        self.upload_button.grid(row=3, column=1, pady=10, sticky='w')

        self.progress_label = ttk.Label(self.main_frame, text="", style='TLabel')
        self.progress_label.grid(row=4, column=0, columnspan=2, pady=10)

        self.download_result_label = ttk.Label(self.main_frame, text="", style='TLabel')
        self.download_result_label.grid(row=5, column=0, columnspan=2, pady=10)
        self.upload_result_label = ttk.Label(self.main_frame, text="", style='TLabel')
        self.upload_result_label.grid(row=6, column=0, columnspan=2, pady=10)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=7, column=0, columnspan=2, pady=10)

        self.plot_data_x = []
        self.plot_data_y_download = []
        self.plot_data_y_upload = []
        self.plot_data_count = count()

        self.plot_button = ttk.Button(self.main_frame, text="Mostrar Gráfico", command=self.show_plot, style='TButton')
        self.plot_button.grid(row=8, column=0, columnspan=2, pady=10)

        # Configuración para actualización en tiempo real
        self.update_interval = 5000  # 5000 milisegundos (5 segundos)

        # Inicia los hilos para las mediciones y la actualización del gráfico
        self.thread_measure = threading.Thread(target=self.update_measurements, daemon=True)
        self.thread_measure.start()

        self.thread_update = threading.Thread(target=self.update_plot, daemon=True)
        self.thread_update.start()

        # Crear la instancia de Measurement
        self.measurement = Measurement(self)

        ttk.Label(self.main_frame, text="Medir Ping, Latencia y Pérdida de Paquetes", font=('DIN', 12)).grid(row=9, column=0, columnspan=2, pady=10)

        self.ping_button = ttk.Button(self.main_frame, text="Medir Ping", command=self.measurement.measure_ping, style='TButton')
        self.ping_button.grid(row=10, column=0, pady=10, sticky='e')

        self.latency_button = ttk.Button(self.main_frame, text="Medir Latencia", command=self.measurement.measure_latency, style='TButton')
        self.latency_button.grid(row=10, column=1, pady=10, sticky='w')

        self.packet_loss_button = ttk.Button(self.main_frame, text="Medir Pérdida de Paquetes", command=self.measurement.measure_packet_loss, style='TButton')
        self.packet_loss_button.grid(row=11, column=0, columnspan=2, pady=10)

        # Mensaje de ayuda para el usuario
        ttk.Label(self.main_frame, text="Para medir la velocidad, introduzca una URL y haga clic en 'Medir Descarga' o 'Medir Subida'.",
                  font=('DIN', 10)).grid(row=12, column=0, columnspan=2, pady=10)

    def reset_labels(self):
        self.download_result_label.config(text="")
        self.upload_result_label.config(text="")

    def display_result(self, label, text, color):
        self.progress_label.config(text="")
        label.config(text=text, foreground=color)

    def update_measurements(self):
        while True:
            self.measurement.measure_download()
            self.measurement.measure_upload()
            time.sleep(self.update_interval / 1000)  # Convierte a segundos

    def update_plot(self):
        while True:
            # Agrega los datos al gráfico de líneas
            x = next(self.plot_data_count)
            y_download = float(self.download_result_label.cget("text").split(":")[-1].strip().split(" ")[0]) if self.download_result_label.cget("text") else 0
            y_upload = float(self.upload_result_label.cget("text").split(":")[-1].strip().split(" ")[0]) if self.upload_result_label.cget("text") else 0

            self.plot_data_x.append(x)
            self.plot_data_y_download.append(y_download)
            self.plot_data_y_upload.append(y_upload)

            # Limpia y actualiza el gráfico
            self.ax.clear()
            self.ax.plot(self.plot_data_x, self.plot_data_y_download, label="Descarga", color='blue')
            self.ax.plot(self.plot_data_x, self.plot_data_y_upload, label="Subida", color='orange')
            self.ax.legend()
            self.ax.set_xlabel('Intento')
            self.ax.set_ylabel('Velocidad (Mbps)')
            self.canvas.draw()

            time.sleep(self.update_interval / 1000)  # Convierte a segundos

    def show_plot(self):
        plt.show()


if __name__ == "__main__":
    app = SpeedTestApp()
    app.mainloop()
