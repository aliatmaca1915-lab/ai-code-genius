"""
CLI aracı - Kod üretimi için komut satırı arayüzü
"""

import click
import sys
import os
from pathlib import Path

# Proje kök dizinini ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model.deepseek import CodeGenius


@click.group()
def cli():
    """AI Code Genius - Kusursuz kod üretimi"""
    pass


@cli.command()
@click.argument('prompt')
@click.option('--model-size', '-m', default='6.7b', help='Model boyutu (1.3b, 6.7b, 16b, 33b)')
@click.option('--output', '-o', help='Çıktı dosyası')
@click.option('--max-tokens', '-t', default=2048, help='Maksimum token sayısı')
@click.option('--temperature', '-T', default=0.7, help='Temperature (0-1)')
@click.option('--quantization', '-q', default='4bit', help='Quantization (4bit, 8bit, none)')
def generate(prompt, model_size, output, max_tokens, temperature, quantization):
    """Tek komutla kod üret"""
    
    click.echo(f"🚀 AI Code Genius başlatılıyor...")
    click.echo(f"📦 Model: DeepSeek Coder {model_size}...\n    # Model yükle
    quant = None if quantization == 'none' else quantization
    genius = CodeGenius(model_size=model_size, quantization=quant)
    
    click.echo(f"💭 Kod üretiliyor...")
    
    # Kod üret
    code = genius.generate(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    # Çıktı
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(code)
        click.echo(f"✅ Kod '{output}' dosyasına kaydedildi!")
    else:
        click.echo("\n" + "="*60)
        click.echo("📝 ÜRETILEN KOD:")
        click.echo("="*60 + "\n")
        click.echo(code)
        click.echo("\n" + "="*60)


@cli.command()
@click.option('--description', '-d', required=True, help='Proje açıklaması')
@click.option('--tech', '-t', required=True, help='Teknolojiler (virgülle ayrılmış)')
@click.option('--features', '-f', required=True, help='Özellikler (virgülle ayrılmış)')
@click.option('--output-dir', '-o', default='./generated_project', help='Çıktı dizini')
@click.option('--model-size', '-m', default='6.7b', help='Model boyutu')
def project(description, tech, features, output_dir, model_size):
    """Tam proje yapısı üret"""
    
    click.echo(f"🚀 Proje üretiliyor: {description}")
    
    # Model yükle
    genius = CodeGenius(model_size=model_size, quantization='4bit')
    
    # Parametreleri parse et
    tech_stack = [t.strip() for t in tech.split(',')]
    feature_list = [f.strip() for f in features.split(',')]
    
    click.echo(f"🔧 Teknolojiler: {', '.join(tech_stack)}")
    click.echo(f"✨ Özellikler: {', '.join(feature_list)}")
    
    # Proje üret
    click.echo("💭 Proje oluşturuluyor (bu biraz zaman alabilir)...")
    
    project_files = genius.generate_project(
        description=description,
        tech_stack=tech_stack,
        features=feature_list
    )
    
    # Dosyaları kaydet
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for filepath, content in project_files.items():
        file_path = output_path / filepath
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        click.echo(f"✅ {filepath}")
    
    click.echo(f"\n🎉 Proje '{output_dir}' dizininde oluşturuldu!")
    click.echo(f"📁 Toplam {len(project_files)} dosya oluşturuldu")


@cli.command()
@click.argument('code-file', type=click.Path(exists=True))
@click.option('--requirements', '-r', multiple=True, help='İyileştirme gereksinimleri')
@click.option('--output', '-o', help='Çıktı dosyası')
def refactor(code_file, requirements, output):
    """Kod iyileştirme"""
    
    click.echo(f"🔧 Kod iyileştiriliyor: {code_file}")
    
    # Kodu oku
    with open(code_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Model yükle
    genius = CodeGenius(model_size='6.7b', quantization='4bit')
    
    # İyileştir
    req_list = list(requirements) if requirements else [
        "Daha temiz kod",
        "Daha iyi performans",
        "Daha iyi dokümantasyon"
    ]
    
    click.echo(f"📋 Gereksinimler: {', '.join(req_list)}")
    
    improved_code = genius.refactor(code, req_list)
    
    # Çıktı
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(improved_code)
        click.echo(f"✅ İyileştirilmiş kod '{output}' dosyasına kaydedildi!")
    else:
        click.echo("\n" + "="*60)
        click.echo("📝 İYİLEŞTİRİLMİŞ KOD:")
        click.echo("="*60 + "\n")
        click.echo(improved_code)


@cli.command()
@click.argument('code-file', type=click.Path(exists=True))
@click.option('--framework', '-f', default='pytest', help='Test framework')
@click.option('--output', '-o', help='Çıktı dosyası')
def test(code_file, framework, output):
    """Test kodu üret"""
    
    click.echo(f"🧪 Test üretiliyor: {code_file}")
    
    # Kodu oku
    with open(code_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Model yükle
    genius = CodeGenius(model_size='6.7b', quantization='4bit')
    
    # Test üret
    test_code = genius.generate_tests(code, framework=framework)
    
    # Çıktı
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(test_code)
        click.echo(f"✅ Test kodu '{output}' dosyasına kaydedildi!")
    else:
        click.echo("\n" + "="*60)
        click.echo("📝 TEST KODU:")
        click.echo("="*60 + "\n")
        click.echo(test_code)


def main():
    cli()


if __name__ == '__main__':
    main()