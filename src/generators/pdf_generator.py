# -*- coding: utf-8 -*-
import os
import random
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from src.core.base_generator import BaseGenerator

class PDFGenerator(BaseGenerator):
    """Generador de archivos PDF con tamaños específicos."""
    
    def generate_batch(self, count: int, size_mb: float = 1.0, output_dir: str = "data/pdfs"):
        os.makedirs(output_dir, exist_ok=True)
        generated_files = []
        
        for i in range(count):
            filename = f"test_doc_{i+1}_{size_mb}mb.pdf"
            filepath = os.path.join(output_dir, filename)
            
            if self._create_pdf(filepath, size_mb):
                generated_files.append(filepath)
                
        return generated_files

    def _create_pdf(self, filepath: str, size_mb: float) -> bool:
        try:
            target_size_bytes = int(size_mb * 1024 * 1024)
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter
            
            c.setFont("Helvetica", 12)
            c.drawString(100, height - 100, f"OMNISYRAX Test PDF")
            c.drawString(100, height - 120, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(100, height - 140, f"Target Size: {size_mb} MB")
            
            c.save()
            
            # Padding to reach target size
            current_size = os.path.getsize(filepath)
            padding_needed = target_size_bytes - current_size
            
            if padding_needed > 0:
                with open(filepath, "ab") as f:
                    f.write(b"\0" * padding_needed)
            
            return True
        except Exception:
            return False

    def generate_single(self):
        pass
