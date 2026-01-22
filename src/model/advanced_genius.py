"""
Advanced Code Genius - Gelişmiş Kod Üretim Motoru
Diğer AI'lardan daha iyi kod yazmak için özel optimizasyonlar
"""

import torch
from typing import List, Dict, Optional, Tuple
import re
import ast
from src.model.deepseek import CodeGenius


class AdvancedCodeGenius(CodeGenius):
    """
    Gelişmiş kod üretim motoru: 
    - Multi-step planning
    - Self-correction
    - Quality assurance
    - Test-driven development
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quality_threshold = 0.9
        self.max_retries = 3
    
    def generate_with_planning(
        self,
        requirements: str,
        max_tokens: int = 4000,
        include_tests: bool = True,
        architecture:  str = "modular"
    ) -> Dict[str, str]:
        """
        Planlama ile kod üret - daha kaliteli sonuçlar
        
        Steps:
        1. Analiz ve planlama
        2. Dosya yapısı oluşturma
        3. Her modül için kod üretimi
        4. Test oluşturma
        5. Entegrasyon
        6. Kalite kontrolü
        """
        
        # Step 1: Analiz
        plan = self._create_plan(requirements, architecture)
        
        # Step 2: Dosya yapısı
        structure = self._design_structure(plan)
        
        # Step 3: Kod üretimi (her dosya için)
        files = {}
        for file_path, file_spec in structure.items():
            code = self._generate_file(file_path, file_spec, plan)
            
            # Kalite kontrolü
            if self._check_quality(code):
                files[file_path] = code
            else:
                # Retry ile daha iyi kod
                code = self._regenerate_with_feedback(file_path, file_spec, code)
                files[file_path] = code
        
        # Step 4: Testler
        if include_tests:
            test_files = self._generate_comprehensive_tests(files)
            files.update(test_files)
        
        # Step 5: README ve dokümantasyon
        files['README. md'] = self._generate_documentation(plan, files)
        
        return files
    
    def _create_plan(self, requirements: str, architecture: str) -> Dict:
        """Detaylı proje planı oluştur"""
        
        planning_prompt = f"""
Sen bir üst düzey yazılım mimarısın.  Aşağıdaki gereksinimleri analiz et ve detaylı bir plan oluştur: 

Gereksinimler:
{requirements}

Mimari:  {architecture}

Şu formatta cevap ver: 

## Analiz
[Gereksinimler analizi]

## Bileşenler
- Bileşen 1: [açıklama]
- Bileşen 2: [açıklama]

## Dosya Yapısı
[Önerilen dosya yapısı]

## Teknik Kararlar
- Teknoloji 1: [neden seçildi]
- Pattern 1: [neden kullanılacak]

## Riskler ve Çözümler
[Potansiyel sorunlar ve çözümleri]
"""
        
        plan_text = self. generate(planning_prompt, max_tokens=1500, temperature=0.3)
        
        return {
            'requirements': requirements,
            'architecture':  architecture,
            'plan_text': plan_text
        }
    
    def _design_structure(self, plan:  Dict) -> Dict[str, Dict]:
        """Dosya yapısını tasarla"""
        
        structure_prompt = f"""
Şu plan için detaylı dosya yapısı oluştur:

{plan['plan_text']}

Her dosya için şunları belirt:
- Dosya yolu
- Sorumluluklar
- Ana fonksiyonlar/sınıflar
- Bağımlılıklar

JSON formatında ver:
{{
    "path/to/file. py": {{
        "description": ".. .",
        "responsibilities": ["... "],
        "main_components": ["..."],
        "dependencies": ["..."]
    }}
}}
"""
        
        structure_text = self.generate(structure_prompt, max_tokens=2000, temperature=0.2)
        
        # Parse JSON (basitleştirilmiş)
        try:
            import json
            structure = json.loads(structure_text)
        except:
            # Fallback: basit yapı
            structure = {
                "main. py": {"description": "Main application file"},
                "utils.py": {"description": "Utility functions"}
            }
        
        return structure
    
    def _generate_file(
        self,
        file_path: str,
        file_spec: Dict,
        plan: Dict
    ) -> str:
        """Tek bir dosya için optimize edilmiş kod üret"""
        
        prompt = f"""
Şu dosyayı yaz:  {file_path}

Proje Planı:
{plan['plan_text']}

Dosya Özellikleri:
{file_spec}

ÖNEMLİ KURALLAR:
1. Production-ready kod yaz
2. Type hints kullan
3. Docstring ekle (Google style)
4. Error handling ekle
5. Logging ekle
6. Clean code prensiplerine uy
7. SOLID prensipleri uygula
8. Security best practices
9. Performance optimize et
10. Test edilebilir yaz

SADECE KOD VER, açıklama ekleme: 
"""
        
        code = self.generate(prompt, max_tokens=2000, temperature=0.4)
        
        # Kod temizleme
        code = self._clean_code(code)
        
        return code
    
    def _check_quality(self, code: str) -> bool:
        """Kod kalitesini kontrol et"""
        
        checks = {
            'has_docstrings': '"""' in code or "'''" in code,
            'has_type_hints': '->' in code or ': ' in code,
            'has_error_handling': 'try:' in code or 'except' in code,
            'reasonable_length': len(code) > 100,
            'no_placeholder':  'TODO' not in code and 'FIXME' not in code
        }
        
        # En az %80 checks geçmeli
        score = sum(checks.values()) / len(checks)
        
        return score >= 0.8
    
    def _regenerate_with_feedback(
        self,
        file_path: str,
        file_spec: Dict,
        previous_code: str
    ) -> str:
        """Feedback ile kodu yeniden üret"""
        
        feedback_prompt = f"""
Şu kodu iyileştir: 

İyileştirmeler:
- Eksik docstring varsa ekle
- Type hints ekle
- Error handling güçlendir
- Daha temiz kod yaz
- Best practices uygula

İYİLEŞTİRİLMİŞ KOD: 
"""
        
        improved = self.generate(feedback_prompt, max_tokens=2000, temperature=0.3)
        
        return self._clean_code(improved)
    
    def _generate_comprehensive_tests(self, files: Dict[str, str]) -> Dict[str, str]:
        """Kapsamlı testler üret"""
        
        test_files = {}
        
        for file_path, code in files.items():
            if file_path.endswith('.py') and 'test_' not in file_path:
                test_path = f"tests/test_{file_path.replace('/', '_')}"
                
                test_prompt = f"""
Şu kod için kapsamlı pytest testleri yaz:

```python
{code}
            test_code = self.generate(test_prompt, max_tokens=1500, temperature=0.4)
            test_files[test_path] = self._clean_code(test_code)
    
    return test_files

def _generate_documentation(self, plan: Dict, files: Dict[str, str]) -> str:
    """README ve dokümantasyon üret"""
    
    doc_prompt = f"""
        readme = self.generate(doc_prompt, max_tokens=2000, temperature=0.5)
    
    return readme

def _clean_code(self, code: str) -> str:
    """Kod temizleme ve formatlama"""
    
    # Markdown code block'ları temizle
    code = re.sub(r'```python\n? ', '', code)
    code = re.sub(r'```\n?', '', code)
    
    # Ekstra açıklamaları kaldır
    lines = code.split('\n')
    cleaned_lines = []
    
    in_code = False
    for line in lines:
        # Kod satırlarını tut
        if line.strip().startswith(('import ', 'from ', 'class ', 'def ', '@', '#', ' ', '\t')) or in_code:
            cleaned_lines.append(line)
            in_code = True
        elif line.strip() == '':
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()

def generate_optimized(
    self,
    prompt: str,
    optimize_for: str = "quality",  # quality, speed, size
    **kwargs
) -> str:
    """Optimizasyon hedefine göre kod üret"""
    
    optimization_hints = {
        "quality": "En yüksek kod kalitesi, best practices, SOLID prensipleri",
        "speed": "Maximum performance, optimize edilmiş algoritmalar, caching",
        "size":  "Minimal kod, compact ama okunabilir, az bağımlılık"
    }
    
    enhanced_prompt = f"""
              {current_code}
           improved_code = self.generate(improve_prompt, temperature=0.3, max_tokens=2000)
        
        if self._check_quality(improved_code):
            improvements.append(f"Iteration {i+1}: {focus} iyileştirildi")
            current_code = self._clean_code(improved_code)
    
    return current_code, improvements
    # Planlı kod üretimi
project = genius.generate_with_planning(
    requirements="""
    Bir task yönetim API'si: 
    - Kullanıcı authentication
    - CRUD operasyonları
    - Task prioritization
    - Deadline tracking
    - Team collaboration
    """,
    include_tests=True,
    architecture="clean architecture"
)

for file_path, code in project. items():
    print(f"\n{'='*60}")
    print(f"📁 {file_path}")
    print('='*60)
    print(code[: 500])  # İlk 500 karakter
    
**Bu dosyayı ekleyin ve commit edin!  **

---

## 🎯 Sonra Ne Yapacağız?

Bu dosyayı ekledikten sonra, diğer dosyaları da tek tek ekleyeceğiz:

1. ✅ `advanced_genius.py` (ŞİMDİ)
2. ⏳ `fine_tune. py` (Sonra)
3. ⏳ `code_quality.py` (Sonra)
4. ⏳ Diğerleri... 

**Hazır mısınız?** Dosyayı ekleyin, ben de sonraki dosyayı hazırlayayım!  🚀          
