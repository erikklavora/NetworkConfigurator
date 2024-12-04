import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re
import ctypes
import sys
import json
import os
from typing import List, Dict

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class NetworkConfigurator(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Konstante
        self.VERSION = "1.0.1"
        self.COMPANY = "© 2024 ERKL Erik Klavora s.p."
        
        self.title(f"Konfigurator mrežne kartice v{self.VERSION}")
        self.geometry("400x550")  # Povečana višina za nogo
        
        # Centriranje okna
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 570) // 2
        self.geometry(f"400x570+{x}+{y}")
        
        # Nastavi ikono, če obstaja
        try:
            self.iconbitmap(resource_path("network_icon.ico"))
        except:
            pass
            
        # Nastavi pot do konfiguracijske datoteke
        self.config_file = os.path.join(
            os.path.expanduser("~"),
            "AppData",
            "Local",
            "NetworkConfigurator",
            "network_configs.json"
        )
        
        # Ustvari direktorij za konfiguracijo, če ne obstaja
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        self.interfaces = self.get_network_interfaces()
        self.saved_configs = self.load_saved_configs()
        
        self.create_widgets()
        self.load_current_config()

    def create_widgets(self):
        ttk.Label(self, text="Mrežna kartica:").grid(row=0, column=0, padx=5, pady=5)
        self.interface_var = tk.StringVar()
        self.interface_combo = ttk.Combobox(self, textvariable=self.interface_var, width=40)
        self.interface_combo['values'] = list(self.interfaces.keys())
        self.interface_combo.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        self.interface_combo.bind('<<ComboboxSelected>>', self.on_interface_select)

        ttk.Label(self, text="IP naslov:").grid(row=1, column=0, padx=5, pady=5)
        self.ip_var = tk.StringVar()
        self.ip_entry = ttk.Entry(self, textvariable=self.ip_var)
        self.ip_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Subnet maska:").grid(row=2, column=0, padx=5, pady=5)
        self.subnet_var = tk.StringVar()
        self.subnet_entry = ttk.Entry(self, textvariable=self.subnet_var)
        self.subnet_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self, text="Gateway:").grid(row=3, column=0, padx=5, pady=5)
        self.gateway_var = tk.StringVar()
        self.gateway_entry = ttk.Entry(self, textvariable=self.gateway_var)
        self.gateway_entry.grid(row=3, column=1, padx=5, pady=5)

        # DNS 1
        ttk.Label(self, text="DNS 1:").grid(row=4, column=0, padx=5, pady=5)
        self.dns1_var = tk.StringVar()
        self.dns1_entry = ttk.Entry(self, textvariable=self.dns1_var)
        self.dns1_entry.grid(row=4, column=1, padx=5, pady=5)

        # DNS 2
        ttk.Label(self, text="DNS 2:").grid(row=5, column=0, padx=5, pady=5)
        self.dns2_var = tk.StringVar()
        self.dns2_entry = ttk.Entry(self, textvariable=self.dns2_var)
        self.dns2_entry.grid(row=5, column=1, padx=5, pady=5)

        # DHCP / Static izbira
        self.ip_mode = tk.StringVar(value="static")
        ttk.Radiobutton(self, text="Statični IP", variable=self.ip_mode, 
                       value="static", command=self.toggle_entries).grid(row=6, column=0, padx=5, pady=5)
        ttk.Radiobutton(self, text="DHCP", variable=self.ip_mode, 
                       value="dhcp", command=self.toggle_entries).grid(row=6, column=1, padx=5, pady=5)

        # Gumbi
        ttk.Button(self, text="Nastavi", command=self.apply_config).grid(row=7, column=0, padx=5, pady=20)
        ttk.Button(self, text="Preberi trenutne", command=self.load_current_config).grid(row=7, column=1, padx=5, pady=20)
        ttk.Button(self, text="Shrani konfiguracijo", command=self.save_config).grid(row=8, column=0, padx=5, pady=5)

        self.config_listbox = tk.Listbox(self, height=10)
        self.config_listbox.grid(row=9, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        self.config_listbox.bind('<<ListboxSelect>>', self.load_selected_config)

        # Dodamo frame za gumbe pod listboxom
        button_frame = ttk.Frame(self)
        button_frame.grid(row=10, column=0, columnspan=3, padx=5, pady=5)

        ttk.Button(button_frame, text="Naloži izbrano", 
                  command=self.load_selected_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Izbriši izbrano", 
                  command=self.delete_config).pack(side=tk.LEFT, padx=5)

        self.update_config_listbox()

        # Dodaj nogo z informacijami o podjetju
        footer = ttk.Label(self, text=self.COMPANY, foreground="gray")
        footer.grid(row=11, column=0, columnspan=3, pady=10)

    def is_admin(self) -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def get_network_interfaces(self) -> Dict[str, str]:
        interfaces = {}
        output = subprocess.check_output("netsh interface show interface", shell=True).decode()
        for line in output.split('\n')[3:]:
            if line.strip():
                parts = line.split()
                if len(parts) >= 4:
                    name = ' '.join(parts[3:])
                    interfaces[name] = name
        return interfaces

    def on_interface_select(self, event=None):
        self.load_current_config()

    def toggle_entries(self):
        state = 'normal' if self.ip_mode.get() == "static" else 'disabled'
        for entry in [self.ip_entry, self.subnet_entry, self.gateway_entry, 
                     self.dns1_entry, self.dns2_entry]:
            entry['state'] = state

    def load_current_config(self):
        if not self.interface_var.get():
            return

        try:
            output = subprocess.check_output(
                f'netsh interface ip show config name="{self.interface_var.get()}"',
                shell=True).decode()

            ip_match = re.search(r'IP Address:\s+(\d+\.\d+\.\d+\.\d+)', output)
            subnet_match = re.search(r'Subnet Prefix:\s+.*?/(\d+)', output)
            gateway_match = re.search(r'Default Gateway:\s+(\d+\.\d+\.\d+\.\d+)', output)
            
            dns_output = subprocess.check_output(
                f'netsh interface ip show dns "{self.interface_var.get()}"',
                shell=True).decode()
            
            dns_servers = re.findall(r'(\d+\.\d+\.\d+\.\d+)', dns_output)

            self.ip_var.set(ip_match.group(1) if ip_match else '')
            self.subnet_var.set(self.cidr_to_netmask(int(subnet_match.group(1))) if subnet_match else '')
            self.gateway_var.set(gateway_match.group(1) if gateway_match else '')
            self.dns1_var.set(dns_servers[0] if len(dns_servers) > 0 else '')
            self.dns2_var.set(dns_servers[1] if len(dns_servers) > 1 else '')

        except Exception as e:
            messagebox.showerror("Napaka", f"Napaka pri branju konfiguracije: {str(e)}")

    def apply_config(self):
        if not self.interface_var.get():
            return

        try:
            interface = self.interface_var.get()
            
            if self.ip_mode.get() == "dhcp":
                # Nastavi DHCP
                subprocess.run(f'netsh interface ip set address "{interface}" dhcp', shell=True, check=True)
                subprocess.run(f'netsh interface ip set dns "{interface}" dhcp', shell=True, check=True)
                messagebox.showinfo("Uspeh", "DHCP nastavitve uspešno nastavljene!")
                return

            # Nastavi statični IP
            subprocess.run(
                f'netsh interface ip set address name="{interface}" '
                f'static {self.ip_var.get()} {self.subnet_var.get()} {self.gateway_var.get()}',
                shell=True, check=True)

            # Nastavi DNS
            if self.dns1_var.get():
                subprocess.run(
                    f'netsh interface ip set dns name="{interface}" '
                    f'static {self.dns1_var.get()}',
                    shell=True, check=True)
                
                if self.dns2_var.get():
                    subprocess.run(
                        f'netsh interface ip add dns name="{interface}" '
                        f'{self.dns2_var.get()} index=2',
                        shell=True, check=True)

            messagebox.showinfo("Uspeh", "Nastavitve uspešno spremenjene!")
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Napaka", f"Napaka pri nastavljanju: {str(e)}")

    def save_config(self):
        # Ustvari pogovorno okno za ime konfiguracije
        dialog = tk.Toplevel(self)
        dialog.title("Shrani konfiguracijo")
        dialog.geometry("300x120")
        dialog.transient(self)  # Naredi okno modalno
        dialog.grab_set()  # Prepreči interakcijo z glavnim oknom
        
        # Centriranje okna
        dialog.geometry("+%d+%d" % (self.winfo_x() + 50, self.winfo_y() + 50))
        
        # Dodaj oznako in vnosno polje
        ttk.Label(dialog, text="Ime konfiguracije:").pack(pady=10)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=40)
        name_entry.pack(pady=5)
        
        def save():
            config_name = name_var.get().strip()
            if not config_name:
                messagebox.showerror("Napaka", "Vnesite ime konfiguracije!", parent=dialog)
                return
            
            config = {
                "interface": self.interface_var.get(),
                "ip": self.ip_var.get(),
                "subnet": self.subnet_var.get(),
                "gateway": self.gateway_var.get(),
                "dns1": self.dns1_var.get(),
                "dns2": self.dns2_var.get(),
                "mode": self.ip_mode.get()
            }
            
            # Preveri, če ime že obstaja
            if config_name in self.saved_configs:
                if not messagebox.askyesno("Opozorilo", 
                    "Konfiguracija s tem imenom že obstaja. Jo želite prepisati?",
                    parent=dialog):
                    return
            
            self.saved_configs[config_name] = config
            self.save_configs_to_file()
            self.update_config_listbox()
            messagebox.showinfo("Uspeh", "Konfiguracija shranjena!", parent=dialog)
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        # Dodaj gumbe
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Shrani", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Prekliči", command=cancel).pack(side=tk.LEFT, padx=5)
        
        # Fokusiraj vnosno polje
        name_entry.focus_set()
        
        # Pritisk Enter shrani konfiguracijo
        dialog.bind('<Return>', lambda e: save())
        # Pritisk Escape zapre okno
        dialog.bind('<Escape>', lambda e: cancel())

    def load_selected_config(self, event=None):
        """Posodobljena funkcija za nalaganje konfiguracije brez pojavnih oken"""
        if isinstance(event, tk.Event):
            # Če je funkcija klicana preko dogodka dvojnega klika
            selection = self.config_listbox.curselection()
        else:
            # Če je funkcija klicana preko gumba
            selection = self.config_listbox.curselection()
            
        if not selection:
            return
            
        config_name = self.config_listbox.get(selection[0])
        config = self.saved_configs.get(config_name)
        
        if config:
            self.interface_var.set(config["interface"])
            self.ip_var.set(config["ip"])
            self.subnet_var.set(config["subnet"])
            self.gateway_var.set(config["gateway"])
            self.dns1_var.set(config["dns1"])
            self.dns2_var.set(config["dns2"])
            self.ip_mode.set(config["mode"])
            self.toggle_entries()
            messagebox.showinfo("Uspeh", f"Konfiguracija '{config_name}' naložena!")

    def delete_config(self):
        selection = self.config_listbox.curselection()
        if not selection:
            messagebox.showwarning("Opozorilo", "Izberite konfiguracijo za izbris!")
            return
            
        config_name = self.config_listbox.get(selection[0])
        
        if messagebox.askyesno("Potrdi izbris", 
                          f"Ali res želite izbrisati konfiguracijo '{config_name}'?"):
            del self.saved_configs[config_name]
            self.save_configs_to_file()
            self.update_config_listbox()
            messagebox.showinfo("Uspeh", "Konfiguracija izbrisana!")

    def load_saved_configs(self) -> Dict[str, Dict]:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_configs_to_file(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.saved_configs, f, indent=4)
        except Exception as e:
            messagebox.showerror("Napaka", f"Napaka pri shranjevanju konfiguracije: {str(e)}")

    def update_config_listbox(self):
        self.config_listbox.delete(0, tk.END)
        for config_name in self.saved_configs:
            self.config_listbox.insert(tk.END, config_name)

    @staticmethod
    def cidr_to_netmask(cidr: int) -> str:
        """Pretvori CIDR v subnet mask"""
        mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
        return '.'.join([str((mask >> (8 * i)) & 0xff) for i in range(3, -1, -1)])

if __name__ == "__main__":
    app = NetworkConfigurator()
    app.mainloop()