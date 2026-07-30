import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import io
import glob
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image

class PDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("pdf页面增删程序 - 作者：Y NA")
        self.root.geometry("784x665")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f5f5")
        
        self.input_pdf = tk.StringVar()
        self.output_pdf = tk.StringVar()
        self.pages_input = tk.StringVar()
        self.image_path = tk.StringVar()
        self.image_page = tk.StringVar(value="1")
        self.folder_var = tk.StringVar()
        self.batch_pages = tk.StringVar()
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_text = tk.StringVar(value="就绪")
        
        self.setup_ui()
    
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#f5f5f5')
        style.configure('TNotebook.Tab', padding=[20, 8], font=("微软雅黑", 10))
        style.configure('TFrame', background='#f5f5f5')
        style.configure('Horizontal.TProgressbar', troughcolor='#e0e0e0', background='#4a90d9', thickness=18)
        
        title_frame = tk.Frame(self.root, bg="#f5f5f5")
        title_frame.pack(pady=(15, 5))
        
        title_label = tk.Label(
            title_frame,
            text="pdf页面增删程序",
            font=("微软雅黑", 16, "bold"),
            fg="#333333",
            bg="#f5f5f5"
        )
        title_label.pack()
        
        author_label = tk.Label(
            title_frame,
            text="作者：Y NA",
            font=("微软雅黑", 9),
            fg="#888888",
            bg="#f5f5f5"
        )
        author_label.pack()
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=5, padx=15, fill="both", expand=True)
        
        delete_frame = ttk.Frame(notebook)
        notebook.add(delete_frame, text="  删除页面 ")
        self.setup_delete_tab(delete_frame)
        
        image_frame = ttk.Frame(notebook)
        notebook.add(image_frame, text="  插入图片 ")
        self.setup_image_tab(image_frame)
        
        batch_frame = ttk.Frame(notebook)
        notebook.add(batch_frame, text="  批量处理 ")
        self.setup_batch_tab(batch_frame)
        
        progress_frame = tk.Frame(self.root, bg="#f5f5f5")
        progress_frame.pack(pady=5, padx=20, fill="x")
        
        tk.Label(progress_frame, text="处理进度", font=("微软雅黑", 10, "bold"), fg="#333333", bg="#f5f5f5").pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, style='Horizontal.TProgressbar')
        self.progress_bar.pack(fill="x", pady=(5, 2))
        
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_text, font=("微软雅黑", 9), fg="#666666", bg="#f5f5f5")
        self.progress_label.pack()
    
    def create_section(self, parent, number, title):
        section_frame = tk.Frame(parent, bg="#f5f5f5")
        section_frame.pack(fill="x", pady=(8, 0))
        
        header_frame = tk.Frame(section_frame, bg="#f5f5f5")
        header_frame.pack(anchor="w")
        
        tk.Label(header_frame, text=f"{number}.", font=("微软雅黑", 10, "bold"), fg="#333333", bg="#f5f5f5").pack(side="left")
        tk.Label(header_frame, text=title, font=("微软雅黑", 10, "bold"), fg="#333333", bg="#f5f5f5").pack(side="left", padx=(5, 0))
        
        separator = tk.Frame(section_frame, height=1, bg="#dddddd")
        separator.pack(fill="x", pady=(5, 8))
        
        return section_frame
    
    def create_file_row(self, parent, label, var, browse_cmd):
        row_frame = tk.Frame(parent, bg="#f5f5f5")
        row_frame.pack(fill="x", pady=4)
        
        tk.Label(row_frame, text=label, font=("微软雅黑", 9), fg="#555555", bg="#f5f5f5", width=12, anchor="w").pack(side="left")
        
        entry = tk.Entry(row_frame, textvariable=var, font=("微软雅黑", 9), relief="solid", bd=1)
        entry.pack(side="left", fill="x", expand=True, padx=(5, 5), ipady=4)
        
        tk.Button(row_frame, text="浏览...", command=browse_cmd, font=("微软雅黑", 9), width=10, relief="solid", bd=1, bg="#ffffff", cursor="hand2").pack(side="right")
        
        return row_frame
    
    def setup_delete_tab(self, frame):
        container = tk.Frame(frame, bg="#f5f5f5")
        container.pack(fill="both", expand=True, padx=15, pady=10)
        
        section1 = self.create_section(container, 1, "选择PDF文件")
        self.create_file_row(section1, "输入文件：", self.input_pdf, self.select_input_pdf)
        self.create_file_row(section1, "输出文件：", self.output_pdf, self.select_output_pdf)
        
        section2 = self.create_section(container, 2, "删除页面设置")
        
        page_row = tk.Frame(section2, bg="#f5f5f5")
        page_row.pack(fill="x", pady=4)
        
        tk.Label(page_row, text="页面范围：", font=("微软雅黑", 9), fg="#555555", bg="#f5f5f5", width=12, anchor="w").pack(side="left")
        tk.Entry(page_row, textvariable=self.pages_input, font=("微软雅黑", 9), relief="solid", bd=1).pack(side="left", fill="x", expand=True, padx=(5, 5), ipady=4)
        
        tip_frame = tk.Frame(section2, bg="#f5f5f5")
        tip_frame.pack(anchor="w", pady=(8, 0))
        tips = [
            "• 单个页面：1, 3, 5    • 页面范围：1-5    • 混合格式：1, 3-5, 7",
            "• 负数表示倒数页：-1(最后一页), -2(倒数第二页)"
        ]
        for tip in tips:
            tk.Label(tip_frame, text=tip, font=("微软雅黑", 8), fg="#888888", bg="#f5f5f5").pack(anchor="w")
        
        section3 = self.create_section(container, 3, "执行操作")
        
        btn_frame = tk.Frame(section3, bg="#f5f5f5")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="删除指定页面", command=self.delete_pages, 
                 font=("微软雅黑", 10, "bold"), bg="#4a90d9", fg="white", 
                 width=18, height=2, cursor="hand2", relief="flat").pack(side="left", padx=5)
    
    def setup_image_tab(self, frame):
        container = tk.Frame(frame, bg="#f5f5f5")
        container.pack(fill="both", expand=True, padx=15, pady=10)
        
        section1 = self.create_section(container, 1, "选择文件")
        self.create_file_row(section1, "PDF文件：", self.input_pdf, self.select_input_pdf)
        self.create_file_row(section1, "图片文件：", self.image_path, self.select_image)
        
        section2 = self.create_section(container, 2, "插入位置设置")
        
        pos_row = tk.Frame(section2, bg="#f5f5f5")
        pos_row.pack(fill="x", pady=4)
        
        tk.Label(pos_row, text="插入位置：", font=("微软雅黑", 9), fg="#555555", bg="#f5f5f5", width=12, anchor="w").pack(side="left")
        
        pos_input_frame = tk.Frame(pos_row, bg="#f5f5f5")
        pos_input_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(pos_input_frame, text="第", font=("微软雅黑", 9), bg="#f5f5f5").pack(side="left")
        tk.Entry(pos_input_frame, textvariable=self.image_page, width=8, font=("微软雅黑", 9), relief="solid", bd=1).pack(side="left", padx=3, ipady=4)
        tk.Label(pos_input_frame, text="页之后插入新页面", font=("微软雅黑", 9), bg="#f5f5f5").pack(side="left")
        
        tip_frame = tk.Frame(section2, bg="#f5f5f5")
        tip_frame.pack(anchor="w", pady=(8, 0))
        tk.Label(tip_frame, text="提示：图片将保持原始大小，居中显示在新页面上", font=("微软雅黑", 9), fg="#27ae60", bg="#f5f5f5").pack(anchor="w")
        tk.Label(tip_frame, text="• 如果图片大于PDF页面，超出部分会被裁剪", font=("微软雅黑", 8), fg="#888888", bg="#f5f5f5").pack(anchor="w")
        
        section3 = self.create_section(container, 3, "执行操作")
        
        btn_frame = tk.Frame(section3, bg="#f5f5f5")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="插入图片页", command=self.insert_image_page, 
                 font=("微软雅黑", 10, "bold"), bg="#27ae60", fg="white", 
                 width=18, height=2, cursor="hand2", relief="flat").pack(side="left", padx=5)
    
    def setup_batch_tab(self, frame):
        container = tk.Frame(frame, bg="#f5f5f5")
        container.pack(fill="both", expand=True, padx=15, pady=10)
        
        section1 = self.create_section(container, 1, "选择文件夹")
        self.create_file_row(section1, "文件夹：", self.folder_var, self.select_folder)
        
        section2 = self.create_section(container, 2, "删除页面设置")
        
        page_row = tk.Frame(section2, bg="#f5f5f5")
        page_row.pack(fill="x", pady=4)
        
        tk.Label(page_row, text="页面范围：", font=("微软雅黑", 9), fg="#555555", bg="#f5f5f5", width=12, anchor="w").pack(side="left")
        self.batch_pages = tk.StringVar()
        tk.Entry(page_row, textvariable=self.batch_pages, font=("微软雅黑", 9), relief="solid", bd=1).pack(side="left", fill="x", expand=True, padx=(5, 5), ipady=4)
        
        tip_frame = tk.Frame(section2, bg="#f5f5f5")
        tip_frame.pack(anchor="w", pady=(8, 0))
        tips = [
            "• 单个页面：1, 3, 5    • 页面范围：1-5    • 混合格式：1, 3-5, 7",
            "• 留空则默认删除第一页和最后一页"
        ]
        for tip in tips:
            tk.Label(tip_frame, text=tip, font=("微软雅黑", 8), fg="#888888", bg="#f5f5f5").pack(anchor="w")
        
        section3 = self.create_section(container, 3, "执行操作")
        
        btn_frame = tk.Frame(section3, bg="#f5f5f5")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="批量处理", command=self.batch_process, 
                 font=("微软雅黑", 10, "bold"), bg="#e67e22", fg="white", 
                 width=18, height=2, cursor="hand2", relief="flat").pack(side="left", padx=5)
    
    def select_input_pdf(self):
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf")]
        )
        if file_path:
            self.input_pdf.set(file_path)
            if not self.output_pdf.get():
                base, ext = os.path.splitext(file_path)
                self.output_pdf.set(base + "_processed" + ext)
    
    def select_output_pdf(self):
        file_path = filedialog.asksaveasfilename(
            title="保存PDF文件",
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf")]
        )
        if file_path:
            self.output_pdf.set(file_path)
    
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.image_path.set(file_path)
    
    def select_folder(self):
        folder_path = filedialog.askdirectory(title="选择文件夹")
        if folder_path:
            self.folder_var.set(folder_path)
    
    def parse_pages(self, pages_str, total_pages):
        pages_to_remove = set()
        for part in pages_str.split(','):
            part = part.strip()
            if not part:
                continue
            if '-' in part:
                start, end = part.split('-', 1)
                start = start.strip()
                end = end.strip()
                if start == '':
                    start = 1
                else:
                    start = int(start)
                if end == '' or end == 'end':
                    end = total_pages
                else:
                    end = int(end)
                if start < 1:
                    start = max(1, total_pages + start + 1)
                if end < 1:
                    end = max(1, total_pages + end + 1)
                start = max(1, start)
                end = min(total_pages, end)
                for i in range(start, end + 1):
                    pages_to_remove.add(i)
            else:
                page = int(part)
                if page < 1:
                    page = total_pages + page + 1
                if 1 <= page <= total_pages:
                    pages_to_remove.add(page)
        return pages_to_remove
    
    def delete_pages(self):
        input_file = self.input_pdf.get()
        output_file = self.output_pdf.get()
        pages_str = self.pages_input.get().strip()
        
        if not input_file:
            messagebox.showerror("错误", "请选择输入PDF文件")
            return
        if not output_file:
            messagebox.showerror("错误", "请选择输出PDF文件")
            return
        if not pages_str:
            messagebox.showerror("错误", "请输入要删除的页面")
            return
        
        try:
            self.progress_text.set("处理中...")
            self.progress_var.set(10)
            self.root.update()
            
            reader = PdfReader(input_file)
            total_pages = len(reader.pages)
            
            pages_to_remove = self.parse_pages(pages_str, total_pages)
            pages_to_keep = [i for i in range(1, total_pages + 1) if i not in pages_to_remove]
            
            if not pages_to_keep:
                self.progress_text.set("错误：所有页面都将被删除")
                messagebox.showerror("错误", "所有页面都将被删除")
                return
            
            self.progress_var.set(50)
            self.root.update()
            
            writer = PdfWriter()
            for page_num in pages_to_keep:
                writer.add_page(reader.pages[page_num - 1])
            
            with open(output_file, 'wb') as f:
                writer.write(f)
            
            self.progress_var.set(100)
            removed_desc = ', '.join(str(p) for p in sorted(pages_to_remove))
            self.progress_text.set(f"完成！删除了第 {removed_desc} 页，{total_pages}页 → {len(pages_to_keep)}页")
            messagebox.showinfo("成功", f"处理完成！\n原页数: {total_pages}\n新页数: {len(pages_to_keep)}")
        except Exception as e:
            self.progress_text.set("处理失败")
            messagebox.showerror("错误", str(e))
    
    def insert_image_page(self):
        input_file = self.input_pdf.get()
        output_file = self.output_pdf.get()
        image_file = self.image_path.get()
        after_page = self.image_page.get().strip()
        
        if not input_file:
            messagebox.showerror("错误", "请选择输入PDF文件")
            return
        if not output_file:
            messagebox.showerror("错误", "请选择输出PDF文件")
            return
        if not image_file:
            messagebox.showerror("错误", "请选择图片文件")
            return
        if not after_page:
            messagebox.showerror("错误", "请输入插入位置")
            return
        
        try:
            self.progress_text.set("处理中...")
            self.progress_var.set(10)
            self.root.update()
            
            after_page = int(after_page)
            reader = PdfReader(input_file)
            total_pages = len(reader.pages)
            
            if after_page < 0 or after_page > total_pages:
                self.progress_text.set("错误")
                messagebox.showerror("错误", f"页码必须在0到{total_pages}之间（0表示在最前插入）")
                return
            
            page = reader.pages[0]
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            self.progress_var.set(40)
            self.root.update()
            
            img = Image.open(image_file)
            
            if img.mode == 'RGBA':
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            img_width, img_height = img.size
            
            new_page = Image.new('RGB', (int(page_width), int(page_height)), (255, 255, 255))
            
            paste_x = int((page_width - img_width) / 2)
            paste_y = int((page_height - img_height) / 2)
            
            new_page.paste(img, (paste_x, paste_y))
            
            self.progress_var.set(70)
            self.root.update()
            
            img_byte_arr = io.BytesIO()
            new_page.save(img_byte_arr, format='PDF', resolution=150)
            img_byte_arr.seek(0)
            
            img_reader = PdfReader(img_byte_arr)
            img_page = img_reader.pages[0]
            
            writer = PdfWriter()
            
            for i in range(total_pages):
                if i == after_page:
                    writer.add_page(img_page)
                writer.add_page(reader.pages[i])
            
            if after_page == total_pages:
                writer.add_page(img_page)
            
            with open(output_file, 'wb') as f:
                writer.write(f)
            
            self.progress_var.set(100)
            self.progress_text.set(f"完成！图片已插入到第 {after_page + 1} 页位置")
            messagebox.showinfo("成功", f"处理完成！\n新PDF页数: {total_pages + 1}")
        except Exception as e:
            self.progress_text.set("处理失败")
            messagebox.showerror("错误", f"{str(e)}")
    
    def batch_process(self):
        folder_path = self.folder_var.get()
        pages_str = self.batch_pages.get().strip()
        
        if not folder_path:
            messagebox.showerror("错误", "请选择文件夹")
            return
        
        pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
        
        if not pdf_files:
            messagebox.showerror("错误", "文件夹中没有PDF文件")
            return
        
        if not pages_str:
            pages_str = "1,-1"
        
        success_count = 0
        fail_count = 0
        skip_count = 0
        total = len(pdf_files)
        
        for idx, pdf_file in enumerate(pdf_files):
            try:
                reader = PdfReader(pdf_file)
                total_pages = len(reader.pages)
                
                pages_to_remove = self.parse_pages(pages_str, total_pages)
                pages_to_keep = [i for i in range(1, total_pages + 1) if i not in pages_to_remove]
                
                if not pages_to_keep:
                    skip_count += 1
                    continue
                
                writer = PdfWriter()
                for page_num in pages_to_keep:
                    writer.add_page(reader.pages[page_num - 1])
                
                with open(pdf_file, 'wb') as f:
                    writer.write(f)
                
                success_count += 1
                
                progress = (idx + 1) / total * 100
                self.progress_var.set(progress)
                self.progress_text.set(f"处理中... ({idx + 1}/{total})")
                self.root.update()
            except Exception as e:
                fail_count += 1
        
        self.progress_text.set(f"完成！成功: {success_count}, 跳过: {skip_count}, 失败: {fail_count}")
        messagebox.showinfo("完成", f"批量处理完成！\n成功: {success_count} 个文件\n跳过: {skip_count} 个文件\n失败: {fail_count} 个文件")

def main():
    root = tk.Tk()
    app = PDFApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()