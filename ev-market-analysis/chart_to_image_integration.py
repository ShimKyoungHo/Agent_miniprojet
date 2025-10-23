# chart_to_image_integration.py
"""
Chart Generation Agent의 차트를 실제 이미지 파일로 저장하고
보고서에 삽입하는 통합 모듈
"""

from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # GUI 없이 백그라운드에서 실행
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import numpy as np

# Seaborn 스타일 설정
sns.set_style("darkgrid")
sns.set_palette("husl")


class ChartImageGenerator:
    """차트를 이미지 파일로 생성하는 클래스"""
    
    def __init__(self, output_dir: str = "outputs/charts"):
        """
        Args:
            output_dir: 차트 이미지를 저장할 디렉토리
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 생성된 차트 파일 경로 추적
        self.chart_files: Dict[str, str] = {}
    
    def generate_all_charts(self, charts_data: List[Dict]) -> Dict[str, str]:
        """
        모든 차트를 이미지로 생성
        
        Args:
            charts_data: Chart Generation Agent가 생성한 차트 데이터 리스트
            
        Returns:
            {chart_id: image_file_path} 딕셔너리
        """
        for chart in charts_data:
            chart_id = chart.get('id')
            chart_type = chart.get('type')
            
            try:
                if chart_type == 'line':
                    filepath = self.create_line_chart(chart)
                elif chart_type == 'bar':
                    filepath = self.create_bar_chart(chart)
                elif chart_type == 'pie':
                    filepath = self.create_pie_chart(chart)
                elif chart_type == 'bubble' or chart_type == 'scatter':
                    filepath = self.create_scatter_chart(chart)
                elif chart_type == 'horizontal_bar':
                    filepath = self.create_horizontal_bar_chart(chart)
                else:
                    filepath = self.create_generic_chart(chart)
                
                self.chart_files[chart_id] = filepath
                print(f"✅ Chart saved: {filepath}")
                
            except Exception as e:
                print(f"❌ Error creating chart {chart_id}: {e}")
        
        return self.chart_files
    
    def create_line_chart(self, chart_data: Dict) -> str:
        """라인 차트 생성"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        data = chart_data.get('data', {})
        x = data.get('x', [])
        y = data.get('y', [])
        
        ax.plot(x, y, marker='o', linewidth=2, markersize=8)
        
        ax.set_title(chart_data.get('title', ''), fontsize=16, fontweight='bold', pad=20)
        
        layout = chart_data.get('layout', {})
        if 'xaxis' in layout:
            ax.set_xlabel(layout['xaxis'].get('title', ''), fontsize=12)
        if 'yaxis' in layout:
            ax.set_ylabel(layout['yaxis'].get('title', ''), fontsize=12)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 파일 저장
        filename = f"{chart_data.get('id', 'chart')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(filepath)
    
    def create_bar_chart(self, chart_data: Dict) -> str:
        """막대 차트 생성"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        data = chart_data.get('data', {})
        x = data.get('x', [])
        
        # 다중 시리즈 처리
        series = data.get('series', [])
        if 'y_ytd' in data and 'y_1y' in data:
            # 주가 성과 차트 (YTD, 1Y)
            x_pos = np.arange(len(x))
            width = 0.35
            
            ax.bar(x_pos - width/2, data['y_ytd'], width, label='YTD Return (%)', alpha=0.8)
            ax.bar(x_pos + width/2, data['y_1y'], width, label='1Y Return (%)', alpha=0.8)
            
            ax.set_xticks(x_pos)
            ax.set_xticklabels(x, rotation=45, ha='right')
            ax.legend()
        else:
            # 일반 막대 차트
            y = data.get('y', [])
            ax.bar(x, y, alpha=0.8)
            ax.set_xticklabels(x, rotation=45, ha='right')
        
        ax.set_title(chart_data.get('title', ''), fontsize=16, fontweight='bold', pad=20)
        
        layout = chart_data.get('layout', {})
        if 'xaxis' in layout:
            ax.set_xlabel(layout['xaxis'].get('title', ''), fontsize=12)
        if 'yaxis' in layout:
            ax.set_ylabel(layout['yaxis'].get('title', ''), fontsize=12)
        
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        filename = f"{chart_data.get('id', 'chart')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(filepath)
    
    def create_pie_chart(self, chart_data: Dict) -> str:
        """파이 차트 생성"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        data = chart_data.get('data', {})
        labels = data.get('labels', [])
        values = data.get('values', [])
        
        # 색상 팔레트
        colors = sns.color_palette('husl', len(labels))
        
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 10}
        )
        
        # 퍼센트 텍스트 굵게
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(chart_data.get('title', ''), fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        filename = f"{chart_data.get('id', 'chart')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(filepath)
    
    def create_scatter_chart(self, chart_data: Dict) -> str:
        """산점도/버블 차트 생성"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        data = chart_data.get('data', {})
        x = data.get('x', [])
        y = data.get('y', [])
        size = data.get('size', [50] * len(x))  # 기본 크기
        labels = data.get('labels', [])
        
        # 버블 차트
        scatter = ax.scatter(x, y, s=size, alpha=0.6, edgecolors='black', linewidth=1.5)
        
        # 라벨 추가
        for i, label in enumerate(labels):
            ax.annotate(
                label,
                (x[i], y[i]),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=10,
                fontweight='bold'
            )
        
        ax.set_title(chart_data.get('title', ''), fontsize=16, fontweight='bold', pad=20)
        
        layout = chart_data.get('layout', {})
        if 'xaxis' in layout:
            ax.set_xlabel(layout['xaxis'].get('title', ''), fontsize=12)
        if 'yaxis' in layout:
            ax.set_ylabel(layout['yaxis'].get('title', ''), fontsize=12)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filename = f"{chart_data.get('id', 'chart')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(filepath)
    
    def create_horizontal_bar_chart(self, chart_data: Dict) -> str:
        """수평 막대 차트 생성"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        data = chart_data.get('data', {})
        categories = data.get('categories', [])
        values = data.get('values', [])
        
        y_pos = np.arange(len(categories))
        ax.barh(y_pos, values, alpha=0.8)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(categories)
        ax.invert_yaxis()  # 위에서 아래로
        
        ax.set_title(chart_data.get('title', ''), fontsize=16, fontweight='bold', pad=20)
        
        layout = chart_data.get('layout', {})
        if 'xaxis' in layout:
            ax.set_xlabel(layout['xaxis'].get('title', ''), fontsize=12)
        
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        
        filename = f"{chart_data.get('id', 'chart')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(filepath)
    
    def create_generic_chart(self, chart_data: Dict) -> str:
        """기본 차트 (타입 불명확 시)"""
        return self.create_line_chart(chart_data)


# Report Generation Agent 통합 함수들

def insert_chart_in_markdown(
    markdown_content: str,
    chart_id: str,
    chart_image_path: str,
    chart_title: str,
    chart_insights: str = ""
) -> str:
    """
    Markdown 보고서에 차트 이미지 삽입
    
    Args:
        markdown_content: 기존 Markdown 내용
        chart_id: 차트 ID (예: 'stock_performance_chart')
        chart_image_path: 차트 이미지 파일 경로
        chart_title: 차트 제목
        chart_insights: 차트 인사이트 (선택)
        
    Returns:
        차트가 삽입된 Markdown
    """
    # 상대 경로로 변환 (보고서와 차트가 같은 outputs 폴더에 있다고 가정)
    relative_path = Path(chart_image_path).name
    
    chart_section = f"\n\n### 📊 {chart_title}\n\n"
    chart_section += f"![{chart_title}](charts/{relative_path})\n\n"
    
    if chart_insights:
        chart_section += f"**주요 인사이트:** {chart_insights}\n\n"
    
    chart_section += "---\n\n"
    
    return markdown_content + chart_section


def insert_chart_in_html(
    html_content: str,
    chart_image_path: str,
    chart_title: str,
    chart_insights: str = "",
    insert_after: str = None
) -> str:
    """
    HTML 보고서에 차트 이미지 삽입
    
    Args:
        html_content: 기존 HTML 내용
        chart_image_path: 차트 이미지 파일 경로
        chart_title: 차트 제목
        chart_insights: 차트 인사이트
        insert_after: 이 텍스트 이후에 삽입 (없으면 끝에 추가)
        
    Returns:
        차트가 삽입된 HTML
    """
    relative_path = Path(chart_image_path).name
    
    chart_html = f"""
<div class="chart-container" style="margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 8px;">
    <h3 style="color: #2c3e50; margin-bottom: 15px;">📊 {chart_title}</h3>
    <img src="charts/{relative_path}" alt="{chart_title}" style="max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
"""
    
    if chart_insights:
        chart_html += f"""
    <p style="margin-top: 15px; padding: 10px; background: #e8f4f8; border-left: 4px solid #3498db; font-style: italic;">
        <strong>주요 인사이트:</strong> {chart_insights}
    </p>
"""
    
    chart_html += """
</div>
"""
    
    if insert_after:
        # 특정 위치에 삽입
        return html_content.replace(insert_after, insert_after + chart_html)
    else:
        # </body> 태그 앞에 삽입
        return html_content.replace('</body>', chart_html + '</body>')


def create_stock_charts_section(
    stock_analysis: Dict,
    chart_files: Dict[str, str]
) -> str:
    """
    주가 분석 차트 섹션 생성 (Markdown)
    
    Args:
        stock_analysis: 주가 분석 데이터
        chart_files: {chart_id: image_path} 딕셔너리
        
    Returns:
        주가 차트 섹션 Markdown
    """
    section = "\n\n## 📈 주가 분석 차트\n\n"
    
    # 주가 성과 차트
    if 'stock_performance_chart' in chart_files:
        chart_path = chart_files['stock_performance_chart']
        relative_path = Path(chart_path).name
        
        section += "### 주요 전기차 기업 주가 성과 비교\n\n"
        section += f"![주가 성과](charts/{relative_path})\n\n"
        section += "**분석:** 최근 1년간 전기차 관련 주식의 수익률을 비교한 차트입니다. "
        section += "---\n\n"
    
    # 밸류에이션 비교 차트
    if 'valuation_comparison_chart' in chart_files:
        chart_path = chart_files['valuation_comparison_chart']
        relative_path = Path(chart_path).name
        
        section += "### 전기차 기업 밸류에이션 비교 (P/E vs P/S)\n\n"
        section += f"![밸류에이션 비교](charts/{relative_path})\n\n"
        section += "**분석:** 주가수익비율(P/E)과 주가매출비율(P/S)을 통해 각 기업의 밸류에이션을 비교합니다. "
        section += "버블 크기는 시가총액을 나타냅니다.\n\n"
        section += "---\n\n"
    
    return section


# 사용 예시
def example_integration():
    """Chart Generation Agent와 Report Generation Agent 통합 예시"""
    
    # 1. Chart Generation Agent의 출력 (JSON)
    charts_data = [
        {
            'id': 'stock_performance_chart',
            'type': 'bar',
            'title': 'EV Stock Performance Comparison',
            'data': {
                'x': ['TSLA', 'BYD', 'NIO', 'RIVN', 'LCID'],
                'y_ytd': [45.2, 62.1, -15.3, -42.1, -38.5],
                'y_1y': [52.3, 78.4, -8.2, -35.6, -45.2]
            },
            'layout': {
                'xaxis': {'title': 'Stock Ticker'},
                'yaxis': {'title': 'Return (%)'}
            },
            'insights': 'Chinese EV stocks showing strong momentum'
        },
        {
            'id': 'valuation_comparison_chart',
            'type': 'scatter',
            'title': 'EV Stock Valuations: P/E vs P/S Ratio',
            'data': {
                'x': [65.2, 25.3, 18.7, 22.1, 15.6],
                'y': [8.5, 2.3, 1.8, 4.2, 3.1],
                'size': [770, 85, 15, 12, 8],
                'labels': ['TSLA', 'BYD', 'GM', 'F', 'RIVN']
            },
            'layout': {
                'xaxis': {'title': 'P/E Ratio'},
                'yaxis': {'title': 'P/S Ratio'}
            },
            'insights': 'Traditional OEMs showing more reasonable valuations'
        }
    ]
    
    # 2. 차트 이미지 생성
    generator = ChartImageGenerator(output_dir="outputs/charts")
    chart_files = generator.generate_all_charts(charts_data)
    
    print(f"\n생성된 차트 파일:")
    for chart_id, filepath in chart_files.items():
        print(f"  - {chart_id}: {filepath}")
    
    # 3. Markdown 보고서에 삽입
    markdown_report = """
# 전기차 시장 투자 리포트

## Executive Summary

전기차 시장은 2024년 기준 연간 25% 성장률을 기록하고 있습니다.

## 주가 분석

Tesla (TSLA)는 여전히 시장을 선도하고 있으며...
"""
    
    # 주가 차트 섹션 추가
    stock_section = create_stock_charts_section({}, chart_files)
    markdown_report += stock_section
    
    # 4. 파일 저장
    output_path = Path("outputs/report_with_charts.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"\n✅ 보고서 생성 완료: {output_path}")
    
    return chart_files


if __name__ == "__main__":
    example_integration()