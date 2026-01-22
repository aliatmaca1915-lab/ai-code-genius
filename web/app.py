"""
Gradio Web Arayüzü - AI Code Genius
"""

import gradio as gr
import sys
from pathlib import Path

# Proje kök dizinini ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model.deepseek import CodeGenius


# Global model (önbellekleme için)
genius = None


def load_model(model_size, quantization):
    """Model yükle veya mevcut olanı kullan"""
    global genius
    
    if genius is None:
        quant = None if quantization == "None" else quantization.lower()
        genius = CodeGenius(model_size=model_size, quantization=quant)
    
    return genius


def generate_code(prompt, model_size, quantization, max_tokens, temperature):
    """Kod üret"""
    try:
        model = load_model(model_size, quantization)
        
        code = model.generate(
            prompt=prompt,
            max_tokens=int(max_tokens),
            temperature=float(temperature)
        )
        
        return code, "✅ Kod başarıyla üretildi!"
    
    except Exception as e:
        return "", f"❌ Hata: {str(e)}"


def generate_project_ui(description, tech_stack, features, model_size):
    """Proje üret"""
    try:
        model = load_model(model_size, "4bit")
        
        tech_list = [t.strip() for t in tech_stack.split(',')]
        feature_list = [f.strip() for f in features.split(',')]
        
        files = model.generate_project(
            description=description,
            tech_stack=tech_list,
            features=feature_list
        )
        
        # Dosyaları formatla
        output = ""
        for filepath, content in files.items():
            output += f"\n{'='*60}\n"
            output += f"📁 {filepath}\n"
            output += f"{'='*60}\n\n"
            output += content + "\n"
        
        return output, f"✅ {len(files)} dosya oluşturuldu!"
    
    except Exception as e:
        return "", f"❌ Hata: {str(e)}"


def refactor_code_ui(code, requirements, model_size):
    """Kod iyileştir"""
    try:
        model = load_model(model_size, "4bit")
        
        req_list = [r.strip() for r in requirements.split(',')]
        
        improved = model.refactor(code, req_list)
        
        return improved, "✅ Kod iyileştirildi!"
    
    except Exception as e:
        return "", f"❌ Hata: {str(e)}"


def generate_tests_ui(code, framework, model_size):
    """Test üret"""
    try:
        model = load_model(model_size, "4bit")
        
        tests = model.generate_tests(code, framework=framework)
        
        return tests, "✅ Testler oluşturuldu!"
    
    except Exception as e:
        return "", f"❌ Hata: {str(e)}"


# Gradio Arayüzü
with gr.Blocks(title="AI Code Genius", theme=gr.themes.Soft()) as app:
    
    gr.Markdown("""
    # 🚀 AI Code Genius
    **DeepSeek Coder V2** ile kusursuz kod üretimi
    """)
    
    # Model Ayarları (sidebar)
    with gr.Row():
        model_size = gr.Dropdown(
            choices=["1.3b", "6.7b", "16b", "33b"],
            value="6.7b",
            label="Model Boyutu"
        )
        quantization = gr.Dropdown(
            choices=["4bit", "8bit", "None"],
            value="4bit",
            label="Quantization"
        )
    
    # Tab'lar
    with gr.Tabs():
        
        # Tab 1: Kod Üretimi
        with gr.Tab("💻 Kod Üret:"):
            with gr.Row():
                with gr.Column():
                    prompt_input = gr.Textbox(
                        label="Kod Talebi",
                        placeholder="Örn: Python ile FastAPI REST API yaz, PostgreSQL veritabanı kullansın...",
                        lines=5
                    )
                    
                    with gr.Row():
                        max_tokens = gr.Slider(
                            minimum=256,
                            maximum=8000,
                            value=2048,
                            step=256,
                            label="Max Tokens"
                        )
                        temperature = gr.Slider(
                            minimum=0.1,
                            maximum=1.0,
                            value=0.7,
                            step=0.1,
                            label="Temperature"
                        )
                    
                    generate_btn = gr.Button("🚀 Kod Üret", variant="primary")
                
                with gr.Column():
                    code_output = gr.Code(label="Üretilen Kod", language="python")
                    status_1 = gr.Textbox(label="Durum", interactive=False)
            
            generate_btn.click(
                generate_code,
                inputs=[prompt_input, model_size, quantization, max_tokens, temperature],
                outputs=[code_output, status_1]
            )
        
        # Tab 2: Proje Üretimi
        with gr.Tab("📦 Proje Üret:"):
            with gr.Row():
                with gr.Column():
                    project_desc = gr.Textbox(
                        label="Proje Açıklaması",
                        placeholder="E-ticaret platformu",
                        lines=3
                    )
                    project_tech = gr.Textbox(
                        label="Teknolojiler (virgülle ayırın)",
                        placeholder="Python, FastAPI, PostgreSQL, React, Docker",
                        lines=2
                    )
                    project_features = gr.Textbox(
                        label="Özellikler (virgülle ayırın)",
                        placeholder="Kullanıcı yönetimi, Ürün kataloğu, Sepet sistemi",
                        lines=3
                    )
                    
                    project_btn = gr.Button("🏗️ Proje Oluştur", variant="primary")
                
                with gr.Column():
                    project_output = gr.Code(label="Proje Dosyaları", language="markdown")
                    status_2 = gr.Textbox(label="Durum", interactive=False)
            
            project_btn.click(
                generate_project_ui,
                inputs=[project_desc, project_tech, project_features, model_size],
                outputs=[project_output, status_2]
            )
        
        # Tab 3: Kod İyileştirme
        with gr.Tab("♻️ Kod İyileştir:"):
            with gr.Row():
                with gr.Column():
                    code_input = gr.Code(
                        label="Mevcut Kod",
                        language="python",
                        lines=10
                    )
                    refactor_reqs = gr.Textbox(
                        label="İyileştirme Gereksinimleri (virgülle ayırın)",
                        placeholder="Daha temiz kod, Daha iyi performans, Tip eklentileri",
                        lines=2
                    )
                    
                    refactor_btn = gr.Button("🔧 İyileştir", variant="primary")
                
                with gr.Column():
                    refactored_output = gr.Code(label="İyileştirilmiş Kod", language="python")
                    status_3 = gr.Textbox(label="Durum", interactive=False)
            
            refactor_btn.click(
                refactor_code_ui,
                inputs=[code_input, refactor_reqs, model_size],
                outputs=[refactored_output, status_3]
            )
        
        # Tab 4: Test Üretimi
        with gr.Tab("🧪 Test Üret:"):
            with gr.Row():
                with gr.Column():
                    test_code_input = gr.Code(
                        label="Test Edilecek Kod",
                        language="python",
                        lines=10
                    )
                    test_framework = gr.Dropdown(
                        choices=["pytest", "unittest", "jest", "mocha"],
                        value="pytest",
                        label="Test Framework"
                    )
                    
                    test_btn = gr.Button("🧪 Test Üret", variant="primary")
                
                with gr.Column():
                    test_output = gr.Code(label="Test Kodu", language="python")
                    status_4 = gr.Textbox(label="Durum", interactive=False)
            
            test_btn.click(
                generate_tests_ui,
                inputs=[test_code_input, test_framework, model_size],
                outputs=[test_output, status_4]
            )
    
    # Footer
    gr.Markdown("""
    ---
    ⭐ **AI Code Genius** - DeepSeek Coder V2 ile güçlendirilmiştir
    
    📖 [GitHub](https://github.com/aliatmaca1915-lab/ai-code-genius) | 
    📚 [Dokümantasyon](https://github.com/aliatmaca1915-lab/ai-code-genius/docs)
    """)


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
