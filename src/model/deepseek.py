"""
DeepSeek Coder V2 Model Wrapper
Kusursuz kod üretimi için ana model sınıfı
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import Optional, List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeGenius:
    """DeepSeek Coder tabanlı kod üretim motoru"""
    
    MODEL_VARIANTS = {
        "1.3b": "deepseek-ai/deepseek-coder-1.3b-instruct",
        "6.7b": "deepseek-ai/deepseek-coder-6.7b-instruct",
        "16b": "deepseek-ai/deepseek-coder-16b-instruct",
        "33b": "deepseek-ai/deepseek-coder-33b-instruct",
    }
    
    def __init__(self,
        model_size: str = "6.7b",
        device: str = "auto",
        quantization: Optional[str] = "4bit",
        custom_model_path: Optional[str] = None
    ):
        """
        Args:
            model_size: Model boyutu (1.3b, 6.7b, 16b, 33b)
            device: Cihaz (auto, cuda, cpu)
            quantization: Quantization tipi (None, 4bit, 8bit)
            custom_model_path: Fine-tuned model yolu
        """
        self.model_size = model_size
        self.device = device
        self.quantization = quantization
        
        # Model yolunu belirle
        if custom_model_path:
            model_name = custom_model_path
        else:
            model_name = self.MODEL_VARIANTS.get(model_size)
            if not model_name:
                raise ValueError(f"Geçersiz model boyutu: {model_size}")
        
        logger.info(f"Model yükleniyor: {model_name}")
        
        # Tokenizer yükle
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Quantization config
        quantization_config = None
        if quantization == "4bit":
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        elif quantization == "8bit":
            quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        
        # Model yükle
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map=device,
            torch_dtype=torch.bfloat16 if quantization is None else None,
            trust_remote_code=True
        )
        
        logger.info("Model başarıyla yüklendi!")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 50,
        num_return_sequences: int = 1,
        stop_sequences: Optional[List[str]] = None
    ) -> str:
        """
        Kod üretimi
        
        Args:
            prompt: Kod üretim talimatı
            max_tokens: Maksimum token sayısı
            temperature: Yaratıcılık seviyesi (0-1)
            top_p: Nucleus sampling
            top_k: Top-k sampling
            num_return_sequences: Üretilecek kod sayısı
            stop_sequences: Durma dizileri
            
        Returns:
            Üretilen kod
        """
        # Prompt formatla
        formatted_prompt = self._format_prompt(prompt)
        
        # Tokenize
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096
        ).to(self.model.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                num_return_sequences=num_return_sequences,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        # Decode
        generated_text = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )
        
        # Promptu çıkar
        code = self._extract_code(generated_text, formatted_prompt)
        
        return code
    
    def generate_project(
        self,
        description: str,
        tech_stack: List[str],
        features: List[str],
        architecture: str = "modular"
    ) -> Dict[str, str]:
        """
        Tam bir proje yapısı üret
        
        Args:
            description: Proje açıklaması
            tech_stack: Teknoloji stack'i
            features: Özellikler listesi
            architecture: Mimari tipi
            
        Returns:
            Dosya yolu: kod içeriği dictionary'si
        """
        prompt = f"""
Aşağıdaki özelliklere sahip tam bir proje oluştur:

Açıklama: {description}

Teknolojiler: {', '.join(tech_stack)}

Özellikler:
{chr(10).join(f'- {feature}' for feature in features)}

Mimari: {architecture}

Lütfen şunları içeren tam bir proje yapısı oluştur:
1. Tüm gerekli dosyaları
2. Düzgün klasör organizasyonu
3. Her dosya için tam kod
4. README ve dokümantasyon
5. Test dosyaları
6. Konfigürasyon dosyaları

Her dosyayı şu formatta ver:
=== DOSYA: dosya/yolu/isim.ext ===
[kod içeriği]
=== DOSYA SONU ===
"""
        
        # Büyük proje için daha fazla token
        generated = self.generate(prompt, max_tokens=8000, temperature=0.6)
        
        # Dosyaları parse et
        files = self._parse_project_files(generated)
        
        return files
    
    def refactor(
        self,
        code: str,
        requirements: List[str],
        language: Optional[str] = None
    ) -> str:
        """
        Kod iyileştirme
        
        Args:
            code: İyileştirilecek kod
            requirements: İyileştirme gereksinimleri
            language: Programlama dili
            
        Returns:
            İyileştirilmiş kod
        """
        lang_hint = f" ({language})" if language else ""
        
        prompt = f"""
Aşağıdaki kodu{lang_hint} iyileştir:

```
{code}
```

İyileştirme gereksinimleri:
{chr(10).join(f'- {req}' for req in requirements)}

İyileştirilmiş, temiz ve profesyonel kod ver.
"""
        
        return self.generate(prompt, max_tokens=3000, temperature=0.5)
    
    def generate_tests(
        self,
        code: str,
        framework: str = "pytest",
        coverage_target: int = 90
    ) -> str:
        """
        Test kodu üret
        
        Args:
            code: Test edilecek kod
            framework: Test framework'ü
            coverage_target: Hedef kapsama yüzdesi
            
        Returns:
            Test kodu
        """
        prompt = f"""
Aşağıdaki kod için {framework} testleri yaz:

```
{code}
```

Gereksinimler:
- %{coverage_target} kod kapsamı hedefle
- Edge case'leri test et
- Mock'ları uygun şekilde kullan
- Açıklayıcı test isimleri

Tam test dosyası ver.
"""
        
        return self.generate(prompt, max_tokens=2000, temperature=0.4)
    
    def _format_prompt(self, prompt: str) -> str:
        """DeepSeek için prompt formatla"""
        # DeepSeek Coder instruction format
        return f"### Instruction:\n{prompt}\n\n### Response:\n"
    
    def _extract_code(self, generated_text: str, prompt: str) -> str:
        """Üretilen metinden kodu çıkar"""
        # Promptu kaldır
        if prompt in generated_text:
            code = generated_text.split(prompt)[-1]
        else:
            code = generated_text
        
        return code.strip()
    
    def _parse_project_files(self, generated_text: str) -> Dict[str, str]:
        """Üretilen projeden dosyaları parse et"""
        files = {}
        current_file = None
        current_content = []
        
        for line in generated_text.split('\n'):
            if line.startswith('=== DOSYA:'):
                # Önceki dosyayı kaydet
                if current_file:
                    files[current_file] = '\n'.join(current_content)
                
                # Yeni dosya başlat
                current_file = line.replace('=== DOSYA:', '').replace('===', '').strip()
                current_content = []
            elif line.startswith('=== DOSYA SONU ==='):
                # Dosyayı kaydet
                if current_file:
                    files[current_file] = '\n'.join(current_content)
                current_file = None
                current_content = []
            elif current_file:
                current_content.append(line)
        
        return files


if __name__ == "__main__":
    # Test
    genius = CodeGenius(model_size="6.7b", quantization="4bit")
    
    code = genius.generate(
        "Python'da bir Fibonacci hesaplayıcı yaz, hem iterative hem recursive versiyonları içersin"
    )
    
    print("Üretilen Kod:")
    print(code)