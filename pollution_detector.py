import customtkinter as ctk
from tkinter import filedialog
import os

def parse_file_data(content):
    data_points = []
    lines = content.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if not line[0].isdigit():
            continue
        
        parts = line.split('|')
        if len(parts) >= 3:
            try:
                p_str = parts[1].strip().replace('%', '')
                h_str = parts[2].strip().replace('%', '')
                
                if not p_str or not h_str:
                    continue

                pollution = float(p_str)
                humidity = float(h_str)
                data_points.append((pollution, humidity))
            except ValueError:
                continue
                
    return data_points

def analyze_air_quality(data_points):
    if not data_points:
        return 0, 0, "UNKNOWN", "gray"
    
    count = len(data_points)
    total_pol = sum(p for p, h in data_points)
    total_hum = sum(h for p, h in data_points)
    
    avg_pol = total_pol / count
    avg_hum = total_hum / count
    
    # Determine Pollution Level
    # Low: < 40, Medium: 40-60, High: > 60
    if avg_pol < 40:
        pol_level = "LOW"
    elif 40 <= avg_pol <= 60:
        pol_level = "MEDIUM"
    else:
        pol_level = "HIGH"
        
    # Determine Humidity Level
    # Low: < 40, High: >= 40
    if avg_hum < 40:
        hum_level = "LOW"
    else:
        hum_level = "HIGH"
        
    # Decision Rules
    # GREEN: Low Pol + Low Hum
    if pol_level == "LOW" and hum_level == "LOW":
        status = "سبز"
        color = "green"
    
    # YELLOW: (Low Pol + High Hum) OR (Medium Pol + Low Hum)
    elif (pol_level == "LOW" and hum_level == "HIGH") or \
         (pol_level == "MEDIUM" and hum_level == "LOW"):
        status = "زرد"
        color = "#FFD700" # Gold/Yellow
        
    # RED: (Medium Pol + High Hum) OR (High Pol)
    elif (pol_level == "MEDIUM" and hum_level == "HIGH") or \
         (pol_level == "HIGH"):
        status = "قرمز"
        color = "red"
    else:
        # Fallback
        status = "نامشخص"
        color = "gray"
        
    return avg_pol, avg_hum, status, color

class AirStatusApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("سیستم تشخیص وضعیت هوا")
        self.geometry("550x600")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.label_title = ctk.CTkLabel(
            self, 
            text="سیستم تشخیص وضعیت هوا", 
            font=("Vazirmatn", 26, "bold")
        )
        self.label_title.grid(row=0, column=0, pady=(30, 10), sticky="ew")
        
        self.btn_file = ctk.CTkButton(
            self, 
            text="انتخاب فایل", 
            command=self.select_file,
            font=("Vazirmatn", 14)
        )
        self.btn_file.grid(row=1, column=0, pady=10)
        
        self.textbox = ctk.CTkTextbox(
            self, 
            width=500, 
            height=300, 
            font=("Vazirmatn", 12)
        )
        self.textbox.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.textbox.bind("<KeyRelease>", self.update_status)

        self.label_analysis = ctk.CTkLabel(
            self, 
            text="لطفاً یک فایل انتخاب کنید...", 
            font=("Vazirmatn", 16),
            justify="center"
        )
        self.label_analysis.grid(row=3, column=0, pady=20)
        
        self.status_indicator = ctk.CTkFrame(
            self, 
            width=100, 
            height=100, 
            corner_radius=10
        )
        self.status_indicator.grid(row=4, column=0, pady=(0, 30))
        self.status_indicator.grid_propagate(False) 
        
        self.load_initial_file()
        
    def load_initial_file(self):
        default_file = "status.txt"
        if os.path.exists(default_file):
            self.load_file(default_file)
            
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", content)
            
            self.update_status()
            
        except Exception as e:
            self.label_analysis.configure(text=f"خطا در خواندن فایل:\n{str(e)}")
            self.status_indicator.configure(fg_color="gray")

    def update_status(self, event=None):
        content = self.textbox.get("0.0", "end")
        data_points = parse_file_data(content)
        
        if not data_points:
            self.label_analysis.configure(text="داده معتبری یافت نشد.")
            self.status_indicator.configure(fg_color="gray")
            return
            
        avg_pol, avg_hum, status, color = analyze_air_quality(data_points)
        
        result_text = (
            f"میانگین آلودگی: {avg_pol:.1f}%\n"
            f"میانگین رطوبت: {avg_hum:.1f}%\n"
            f"وضعیت نهایی: {status}"
        )
        self.label_analysis.configure(text=result_text)
        self.status_indicator.configure(fg_color=color)

if __name__ == "__main__":
    app = AirStatusApp()
    app.mainloop()