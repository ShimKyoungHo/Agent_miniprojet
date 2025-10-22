# Base Agent 클래스
# agents/base_agent.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

class BaseAgent(ABC):
    """모든 Agent의 기본 클래스"""
    
    def __init__(self, name: str, llm=None, config: Optional[Dict] = None):
        """
        Args:
            name: Agent 이름
            llm: LLM 인스턴스 (ChatOpenAI 등)
            config: Agent 설정
        """
        self.name = name
        self.llm = llm
        self.config = config or {}
        self.logger = self._setup_logger()
        self.output_dir = Path(f"outputs/{name}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _setup_logger(self):
        """로거 설정"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # UTF-8 인코딩을 명시적으로 설정한 StreamHandler
            import sys
            handler = logging.StreamHandler(sys.stdout)
            
            # Windows에서 UTF-8 출력을 위한 설정
            if sys.platform == 'win32':
                import io
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, 
                    encoding='utf-8', 
                    errors='replace'
                )
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent의 메인 처리 로직 (비동기)
        
        Args:
            state: 현재 상태
            
        Returns:
            업데이트된 상태
        """
        pass
    
    def save_output(self, data: Any, filename: str):
        """결과 저장"""
        output_path = self.output_dir / filename
        
        if filename.endswith('.json'):
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(str(data))
        
        self.logger.info(f"결과 저장 완료: {output_path}")
    
    def load_data(self, filepath: str) -> Any:
        """데이터 로드"""
        path = Path(filepath)
        
        if not path.exists():
            self.logger.warning(f"파일이 존재하지 않습니다: {filepath}")
            return None
        
        if path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def validate_state(self, state: Dict[str, Any], required_fields: list) -> bool:
        """상태 유효성 검증"""
        missing_fields = [field for field in required_fields if field not in state]
        
        if missing_fields:
            self.logger.error(f"필수 필드 누락: {missing_fields}")
            return False
        return True
    
    def get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        return datetime.now().isoformat()
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"