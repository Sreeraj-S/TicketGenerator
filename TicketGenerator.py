from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import os
import urllib.request
import SheetAccess
import Utiles
import datetime

class TicketGenerator:
    def __init__(self, master, base_image_path, overlay_image_folder, output_folder, num_loops):
        self.master = master
        self.base_image_path = base_image_path
        self.overlay_image_folder = overlay_image_folder
        self.output_folder = output_folder
        self.num_loops = num_loops
        
        self.size = 256

        self.tickType = "none"

        self.sheet = SheetAccess.Sheets()
        self.utils = Utiles.Utiles()

        self.overlay_image_path = None
        self.overlay_image = None
        self.overlay_position = (50, 50)

        self.generate_tickets()
    def reset(self):
        self.size = 256

        self.tickType = "none"

        self.overlay_image_path = None
        self.overlay_image = None
        self.overlay_position = (50, 50)
        self.qrcodes=[]

    def create_widgets(self):
        self.clear_frame()


        qr_frame = tk.Frame(self.master)
        qr_frame.pack()
        self.canvas = tk.Canvas(self.master)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.load_base_image()
        f0=tk.Frame(self.master)
        f1 = tk.Frame(f0)
        self.sizeE = tk.Entry(f1)
        self.sizeE.pack(side=tk.LEFT,padx=5)
        self.chge_btn = tk.Button(f1, text="Change Size", command=lambda: self.change_size(self.sizeE))
        self.chge_btn.pack(side=tk.LEFT,padx=5)
        f1.pack(padx=5,side=tk.LEFT)
        f4=tk.Frame(f0)
        self.transpQRcode = tk.BooleanVar()
        transpQRcodeCheckbox = tk.Checkbutton(f4, text="Transparent Baground:", variable=self.transpQRcode)
        transpQRcodeCheckbox.pack(padx=5)
        f4.pack(padx=5,side=tk.LEFT)
        f0.pack(pady=5)
        f2 = tk.Frame(self.master)
        self.noOfTickL = tk.Label(f2,text="No of Tickets")
        self.noOfTickL.pack(side=tk.LEFT,padx=5)
        self.noOfTick = tk.Entry(f2)
        self.noOfTick.pack(padx=5,side=tk.LEFT)
        f2.pack(pady=5)
        f3 = tk.Frame(self.master)
        self.tickType = tk.Entry(f3)
        self.tickType.pack(side=tk.LEFT,padx=5)
        self.tickType_btn = tk.Button(f3, text="Change Type", command=lambda: self.tick_type(self.tickType))
        self.tickType_btn.pack(side=tk.LEFT,padx=5)
        f3.pack(pady=5)
        self.load_overlay_button = tk.Button(self.master, text="Load Overlay Image", command=self.load_overlay_image)
        self.load_overlay_button.pack(pady=5)
        self.load_no_button = tk.Button(self.master, text="Load Number", command=self.load_number)
        self.load_ono_button.pack(pady=5)

        self.save_button = tk.Button(self.master, text="Save Images", command=self.save_images)
        self.save_button.pack(pady=5)

        self.back_button = tk.Button(self.master, text="Back", command=self.generate_tickets)
        self.back_button.pack(pady=5)

        self.master.bind("<B1-Motion>", self.on_drag)
    
    def tick_type(self,entry):
        self.tickType = str(entry.get())

    def change_size(self,entry):
        self.size = int(entry.get())
        self.load_overlay_image()

    def load_base_image(self):
        file_path = filedialog.askopenfilename(title="Select Base Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.base_image = Image.open(file_path)
            self.tk_base_image = ImageTk.PhotoImage(self.base_image)
            self.canvas.config(width=self.tk_base_image.width(), height=self.tk_base_image.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_base_image)

    def load_overlay_image(self):
        qrcodes=self.sheet.qrCodeAvilable(self.tickType,int(self.noOfTick.get())if(self.noOfTick.get()!="")else None)
        dumy,self.qrcodes = qrcodes[0],qrcodes[1:]
        urllib.request.urlretrieve(dumy,"qr.png")
        self.overlay_image_path = "qr.png"
        if self.overlay_image_path:
            if(self.transpQRcode.get()):self.overlay_image = self.utils.transparentImg(Image.open(self.overlay_image_path).convert("RGBA"))
            else:self.overlay_image = Image.open(self.overlay_image_path).convert("RGBA")
            self.overlay_image = self.overlay_image.resize((self.size, self.size))
            self.tk_overlay_image = ImageTk.PhotoImage(self.overlay_image)
            self.canvas.create_image(self.overlay_position, anchor=tk.NW, image=self.tk_overlay_image)

    def on_drag(self, event):
        try:
            self.overlay_position = (event.x, event.y)
            self.canvas.delete("overlay")
            self.canvas.create_image(self.overlay_position, anchor=tk.NW, image=self.tk_overlay_image, tags="overlay")
        except:
            pass

    

    def save_images(self):
        for idx_,qrcode in enumerate(self.qrcodes):
            urllib.request.urlretrieve(qrcode,"qr.png")
            self.overlay_image_path = "qr.png"
            if self.overlay_image_path:
                self.overlay_image = self.utils.transparentImg(Image.open(self.overlay_image_path).convert("RGBA"))
                self.overlay_image = self.overlay_image.resize((256, 256))  # Change this to the desired overlay image size
                self.tk_overlay_image = ImageTk.PhotoImage(self.overlay_image)
                base_image_copy = self.base_image.copy()
                base_image_copy.paste(self.overlay_image, self.overlay_position, self.overlay_image)

                output_path = os.path.join(self.output_folder, f"{self.tickType}_{idx_}.png")
                base_image_copy.save(output_path)
                self.sheet.generatedTicket(qrcode)
                self.generate_tickets()
                self.reset()

    def generate_tickets(self):
        self.clear_frame()

        frame = tk.Frame(self.master)
        frame.pack()

        # sheet = tk.Entry(frame)
        # sheet.pack(pady=10)
        # chge_btn = tk.Button(frame, text="Change Sheet ID", command=lambda: self.sheet_key(sheet))
        # chge_btn.pack(pady=10)

        btn_generate_qr = tk.Button(frame, text="Generate QR Codes", command=self.generate_qr_codes_frame)
        btn_generate_qr.pack(pady=10)

        btn_generate_tickets = tk.Button(frame, text="Generate Tickets", command=self.create_widgets)
        btn_generate_tickets.pack(pady=10)

        btn_exit = tk.Button(frame, text="Exit", command=self.master.destroy)
        btn_exit.pack(pady=10)

    def sheet_key(self,sheet):
        self.sheet = SheetAccess.Sheets(sheet)


    def generate_qr_codes_frame(self):
        self.clear_frame()

        qr_frame = tk.Frame(self.master)
        qr_frame.pack()

        lbl_num_qr = tk.Label(qr_frame, text="Number of QR Codes:")
        lbl_num_qr.pack(pady=10)

        entry_num_qr = tk.Entry(qr_frame)
        entry_num_qr.pack(pady=10)

        lbl_type = tk.Label(qr_frame, text="Ticket Type:")
        lbl_type.pack(pady=10)

        entry_type = tk.Entry(qr_frame)
        entry_type.pack(pady=10)

        lbl_success = tk.Label(qr_frame, text="")
        lbl_success.pack(pady=10)

        self.back_button = tk.Button(self.master, text="Back", command=self.generate_tickets)
        self.back_button.pack(pady=10)

        btn_generate = tk.Button(qr_frame, text="Generate", command=lambda: self.generate_qr(entry_num_qr, lbl_success, entry_type))
        btn_generate.pack(pady=10)

    def generate_qr(self, entry, lbl_success, entry_type):
        try:
            num_qr = int(entry.get())
            _success = self.sheet.generateQrcode(num_qr,str(entry_type.get()))
            if _success:
                lbl_success.config(text="Successful")
            else:
                lbl_success.config(text="An Error Occured and failed to Generate")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def exit_application(self):
        self.master.destroy()

    def clear_frame(self):
        for widget in self.master.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    base_image_path = "img/ticket.jpg"
    overlay_image_folder = ['https://chart.googleapis.com/chart?cht=qr&chs=512x512&chl=d89fa039-93c4-4374-8cf2-4ee603080ee5']
    output_folder = "output"
    num_loops = 1
    root = tk.Tk()
    app = TicketGenerator(root, base_image_path, overlay_image_folder, output_folder, num_loops)
    root.mainloop()
