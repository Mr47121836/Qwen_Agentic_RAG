"""
文档处理模块
"""
import os
import hashlib
import json
from typing import List, Optional, Dict, Any, Union
import logging
from pathlib import Path
import io
from utils.decorators import error_handler, log_execution
from datetime import datetime
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP, SEPARATORS

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.documents import Document

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    文档处理器类，用于处理PDF文档
    """

    # 1. 初始化文档处理器
    def __init__(self, cache_dir: str = ".cache", max_workers: int = 4):
        """
        cache_dir - 缓存目录
        max_workers - 最大工作线程数
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_workers = max_workers
        
        # 创建项目temp目录
        self.temp_dir = Path("./temp")
        self.temp_dir.mkdir(exist_ok=True)
        logger.info(f"临时文件目录: {self.temp_dir.absolute()}")
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=SEPARATORS,
            length_function=len,
            is_separator_regex=False
        )
    
    # 2. 获取缓存文件路径
    def _get_cache_path(self, file_content: bytes, file_name: str) -> Path:
        """
        file_content - 文件内容
        file_name - 文件名

        @return 缓存文件路径
        """
        cache_key = hashlib.md5(file_content + file_name.encode()).hexdigest()
        return self.cache_dir / f"{cache_key}.json"
    
    # 3. 从缓存加载处理结果
    def _load_from_cache(self, cache_path: str) -> Optional[List[Document]]:
        """
        @param {str} cache_path - 缓存文件路径
        @return {Optional[List[Document]]} 处理结果，如果缓存不存在则返回None
        """
        try:
            path = Path(cache_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [Document(**doc) for doc in data]
        except Exception as e:
            logger.warning(f"从缓存加载失败: {str(e)}")
        return None
    
    # 4. 保存处理结果到缓存
    def _save_to_cache(self, cache_path: Path, documents: List[Document]):
        """
        @param {Path} cache_path - 缓存文件路径
        @param {List[Document]} documents - 处理结果
        """
        try:
            # 将Document对象转换为可序列化的字典
            docs_data = [doc.dict() for doc in documents]
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(docs_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存到缓存失败: {str(e)}")
    
    # 5. 创建安全的临时文件
    def _create_temp_file(self, file_content: bytes, suffix: str = '.pdf') -> Path:
        """
        在项目temp目录中创建临时文件
        
        @param file_content - 文件内容
        @param suffix - 文件后缀
        
        @return 临时文件路径
        """
        import uuid
        # 生成唯一的文件名
        temp_filename = f"temp_{uuid.uuid4().hex}{suffix}"
        temp_path = self.temp_dir / temp_filename
        
        # 写入文件内容
        with open(temp_path, 'wb') as f:
            f.write(file_content)
        
        logger.debug(f"创建临时文件: {temp_path}")
        return temp_path
    
    # 6. 清理临时文件
    def _cleanup_temp_file(self, temp_path: Path):
        """
        清理临时文件
        
        @param temp_path - 临时文件路径
        """
        try:
            if temp_path.exists():
                os.unlink(temp_path)
                logger.debug(f"已清理临时文件: {temp_path}")
        except Exception as e:
            logger.warning(f"清理临时文件失败 {temp_path}: {str(e)}")
    
    # 7. 处理PDF文件
    @error_handler()
    @log_execution
    def _process_pdf(self, file_content: bytes, file_name: str) -> List[Document]:
        """
        file_content - PDF文件内容
        file_name - PDF文件名

        @return 处理后的文档列表
        """
        # 检查缓存
        cache_path = self._get_cache_path(file_content, file_name)
        cached_docs = self._load_from_cache(str(cache_path))
        if cached_docs is not None:
            logger.info(f"从缓存加载文件: {file_name}")
            return cached_docs
        
        # 处理PDF
        logger.info(f"处理文件: {file_name}")
        
        temp_path = None
        try:
            # 在项目temp目录中创建临时文件
            temp_path = self._create_temp_file(file_content, '.pdf')
            
            # 使用临时文件加载PDF
            loader = PyPDFLoader(str(temp_path))
            documents = loader.load()
            
            # 使用文本分割器分割文档
            split_docs = self.text_splitter.split_documents(documents)
            
            # 保存到缓存
            if split_docs:
                self._save_to_cache(cache_path, split_docs)
            
            return split_docs
            
        except Exception as e:
            logger.error(f"处理PDF文件失败: {str(e)}")
            raise
        finally:
            # 确保清理临时文件
            if temp_path:
                self._cleanup_temp_file(temp_path)
    
    # 8. 清除所有缓存
    def clear_cache(self):
        try:
            for file in self.cache_dir.glob("*.json"):
                file.unlink()
            logger.info("缓存已清除")
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")
            raise
    
    # 9. 清理所有临时文件
    def clear_temp_files(self):
        """
        清理temp目录中的所有临时文件
        """
        try:
            if self.temp_dir.exists():
                for file in self.temp_dir.iterdir():
                    if file.is_file():
                        os.unlink(file)
                logger.info(f"已清理临时目录: {self.temp_dir}")
        except Exception as e:
            logger.error(f"清理临时文件失败: {str(e)}")
            raise
    
    # 10. 处理上传的文件，支持多种文件类型
    @error_handler()
    @log_execution
    def process_file(self, uploaded_file_or_content, file_name: str = None) -> Union[str, List[Document]]:
        """
        uploaded_file_or_content - Streamlit上传的文件对象或文件内容
        file_name - 文件名，当第一个参数为文件内容时需要提供

        @return  处理结果，可能是文本内容或Document对象列表
        """
        try:
            # 判断输入类型
            if hasattr(uploaded_file_or_content, 'getvalue') and hasattr(uploaded_file_or_content, 'name'):
                # Streamlit上传的文件对象
                file_content = uploaded_file_or_content.getvalue()
                file_name = uploaded_file_or_content.name
            elif isinstance(uploaded_file_or_content, bytes) and file_name:
                # 直接传入的文件内容和文件名
                file_content = uploaded_file_or_content
            else:
                raise ValueError("参数错误：需要提供有效的文件对象或文件内容和文件名")
            
            # 根据文件类型进行特定处理
            if file_name.lower().endswith('.pdf'):
                docs = self._process_pdf(file_content, file_name)
                # 如果是从Streamlit上传的文件，返回文本内容，否则返回文档对象
                if hasattr(uploaded_file_or_content, 'getvalue'):
                    return "\n\n".join(doc.page_content for doc in docs)
                return docs
            elif file_name.lower().endswith('.txt'):
                return file_content.decode('utf-8')
            else:
                return f"不支持的文件类型: {file_name}"
            
        except Exception as e:
            logger.error(f"处理文件失败: {str(e)}")
            raise Exception(f"处理文件失败: {str(e)}")