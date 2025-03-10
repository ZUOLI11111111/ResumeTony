import React, { useState, useEffect } from 'react';
import './ResumeReviewHistory.css';
import axios from 'axios';
import ErrorBoundary from '../ErrorBoundary';

// 创建支持大数据的axios实例
const api = axios.create({
    baseURL: 'http://localhost:8080/api',
    timeout: 30000, // 增加超时时间到30秒
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    maxContentLength: Infinity, // 允许无限大小的内容
    maxBodyLength: Infinity // 允许无限大小的请求体
});

function ResumeReviewHistoryContent({ onBack }) {
    const [loading, setLoading] = useState(true);
    const [resumeHistory, setResumeHistory] = useState([]);
    const [filteredHistory, setFilteredHistory] = useState([]);
    const [selectedResume, setSelectedResume] = useState(null);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [isDeleting, setIsDeleting] = useState(false);
    const [confirmDelete, setConfirmDelete] = useState(null); // 存储要删除的ID

    // 全局错误处理
    useEffect(() => {
        const handleError = (event) => {
            console.error('全局错误捕获:', event.error);
            setError('应用发生错误，请刷新页面重试');
        };

        window.addEventListener('error', handleError);
        
        return () => {
            window.removeEventListener('error', handleError);
        };
    }, []);

    // 获取简历修改历史
    useEffect(() => {
        fetchResumeHistory();
    }, []);

    // 筛选历史记录
    useEffect(() => {
        if (!searchTerm.trim()) {
            setFilteredHistory(resumeHistory);
            return;
        }
        
        const filtered = resumeHistory.filter(resume => {
            // 在内容和描述中搜索
            const descMatch = resume.modificationDescription && 
                              resume.modificationDescription.toLowerCase().includes(searchTerm.toLowerCase());
            const origMatch = resume.originalContent && 
                             resume.originalContent.toLowerCase().includes(searchTerm.toLowerCase());
            const modMatch = resume.modifiedContent && 
                            resume.modifiedContent.toLowerCase().includes(searchTerm.toLowerCase());
            return descMatch || origMatch || modMatch;
        });
        
        setFilteredHistory(filtered);
    }, [searchTerm, resumeHistory]);

    const fetchResumeHistory = async () => {
        try {
            setLoading(true);
            console.log('开始请求历史数据...');
            const response = await api.get('/resume/page');
            console.log('收到响应:', response);
            if (response.data && response.data.success) {
                const records = response.data.data.records || [];
                console.log('解析记录:', records);
                setResumeHistory(records);
                setFilteredHistory(records);
            } else {
                console.error('API返回错误:', response.data);
                setError(`获取历史记录失败: ${response.data?.message || '未知错误'}`);
            }
        } catch (err) {
            console.error('获取简历历史出错详情:', err.message, err.response || '无响应');
            if (err.code === 'ECONNABORTED') {
                setError('请求超时，请检查后端服务是否启动');
            } else {
                setError('无法连接到服务器，请稍后再试');
            }
        } finally {
            setLoading(false);
        }
    };

    // 查看详情
    const viewResumeDetail = async (id) => {
        try {
            setLoading(true);
            console.log(`开始请求ID为${id}的简历详情...`);
            const response = await api.get(`/resume/${id}`);
            console.log('收到详情响应:', response);
            if (response.data && response.data.success) {
                console.log('修改描述内容:', response.data.data.modificationDescription);
                
                // 处理数据，注意防御性编程，确保所有属性都存在
                const resumeData = {...response.data.data};
                
                // 确保所有属性都是可用的，防止undefined错误
                resumeData.modificationDescription = resumeData.modificationDescription || '';
                resumeData.originalContent = resumeData.originalContent || '';
                resumeData.modifiedContent = resumeData.modifiedContent || '';
                resumeData.updatedTime = resumeData.updatedTime || new Date().toISOString();
                
                // 如果修改描述是"简历优化"默认值，则视为空
                if (resumeData.modificationDescription === '简历优化') {
                    resumeData.modificationDescription = '';
                }
                
                setSelectedResume(resumeData);
                console.log('设置选中的简历:', resumeData);
            } else {
                console.error('API返回详情错误:', response.data);
                setError(`获取简历详情失败: ${response.data?.message || '未知错误'}`);
            }
        } catch (err) {
            console.error('获取简历详情出错:', err.message, err.response || '无响应');
            setError('无法获取简历详情，请稍后再试');
        } finally {
            setLoading(false);
        }
    };

    // 返回列表
    const backToList = () => {
        setSelectedResume(null);
        setError(null);
    };

    // 格式化日期
    const formatDate = (dateString) => {
        if (!dateString) return '无日期信息';
        try {
            const date = new Date(dateString);
            // 检查日期是否有效
            if (isNaN(date.getTime())) {
                return '日期格式无效';
            }
            return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
        } catch (error) {
            console.error('日期格式化错误:', error);
            return '日期处理错误';
        }
    };

    // 重试加载数据
    const retryLoading = () => {
        setError(null);
        setLoading(true);
        // 使用setTimeout确保状态更新后再重试
        setTimeout(() => {
            const fetchResumeHistory = async () => {
                try {
                    console.log('重新尝试请求数据...');
                    const response = await api.get('/resume/page');
                    if (response.data && response.data.success) {
                        const records = response.data.data.records || [];
                        setResumeHistory(records);
                    } else {
                        setError(`获取历史记录失败: ${response.data?.message || '未知错误'}`);
                    }
                } catch (err) {
                    console.error('重试获取简历历史出错:', err);
                    setError('重试失败，无法连接到服务器');
                } finally {
                    setLoading(false);
                }
            };
            fetchResumeHistory();
        }, 100);
    };

    // 获取截断的描述文本
    const getTruncatedDescription = (text, maxLength = 50) => {
        if (!text || text === '简历优化') return '无描述';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    };

    // 删除确认
    const handleDeleteConfirm = (id, event) => {
        event.stopPropagation(); // 阻止事件冒泡，避免触发点击整个条目的事件
        setConfirmDelete(id);
    };

    // 取消删除
    const handleDeleteCancel = (event) => {
        if (event) event.stopPropagation();
        setConfirmDelete(null);
    };

    // 执行删除
    const handleDeleteResume = async (id, event) => {
        if (event) event.stopPropagation();
        try {
            setIsDeleting(true);
            console.log(`删除ID为${id}的简历记录...`);
            const response = await api.delete(`/resume/${id}`);
            
            if (response.data && response.data.success) {
                // 从列表中移除已删除的记录
                const updatedHistory = resumeHistory.filter(resume => resume.id !== id);
                setResumeHistory(updatedHistory);
                setFilteredHistory(prevFiltered => prevFiltered.filter(resume => resume.id !== id));
                console.log('删除成功');
            } else {
                console.error('删除失败:', response.data);
                setError(`删除失败: ${response.data?.message || '未知错误'}`);
            }
        } catch (err) {
            console.error('删除过程出错:', err);
            setError('删除过程中发生错误，请稍后再试');
        } finally {
            setIsDeleting(false);
            setConfirmDelete(null);
        }
    };

    // 处理搜索输入
    const handleSearchChange = (e) => {
        setSearchTerm(e.target.value);
    };

    // 清除搜索
    const clearSearch = () => {
        setSearchTerm('');
    };

    // 格式化简历内容，将纯文本转换为结构化的HTML
    const formatResumeContent = (content) => {
        if (!content) return null;
        
        // 检测内容是否已经包含HTML标签
        const hasHtml = /<[a-z][\s\S]*>/i.test(content);
        if (hasHtml) {
            // 如果已经是HTML，直接返回
            return <div dangerouslySetInnerHTML={{ __html: content }} style={{ textAlign: 'left' }} />;
        }
        
        // 将内容按行分割
        const lines = content.split('\n');
        
        // 识别基本信息部分
        let inSection = '';
        const formattedLines = [];
        
        lines.forEach((line, index) => {
            line = line.trim();
            if (!line) {
                // 空行作为分隔符
                formattedLines.push(<div key={`empty-${index}`} className="section-divider"></div>);
                return;
            }
            
            // 检测是否是新的章节标题
            if (line.includes('基本信息') || line.includes('教育背景') || line.includes('工作经验') || 
                line.includes('项目经验') || line.includes('技能') || line.includes('主修课程')) {
                inSection = line;
                formattedLines.push(<h3 key={`section-${index}`} className="resume-section-title">{line}</h3>);
                return;
            }
            
            // 检测是否是项目条目
            if (/^\d+\.\s+/.test(line)) {
                formattedLines.push(<h4 key={`project-${index}`} className="resume-project-title">{line}</h4>);
                return;
            }
            
            // 检测是否是项目描述（以'-'或'•'开头）
            if (/^[-•]\s+/.test(line)) {
                formattedLines.push(
                    <div key={`bullet-${index}`} className="resume-bullet-point">
                        <span className="bullet-symbol">•</span>
                        <span className="bullet-content">{line.replace(/^[-•]\s+/, '')}</span>
                    </div>
                );
                return;
            }
            
            // 尝试检测键值对（例如：姓名：张三）
            const kvMatch = line.match(/^(.+?)[:：]\s*(.+)$/);
            if (kvMatch) {
                formattedLines.push(
                    <div key={`kv-${index}`} className="resume-key-value">
                        <span className="resume-key">{kvMatch[1]}：</span>
                        <span className="resume-value">{kvMatch[2]}</span>
                    </div>
                );
                return;
            }
            
            // 默认作为普通段落
            formattedLines.push(<p key={`text-${index}`} className="resume-paragraph">{line}</p>);
        });
        
        return <div style={{ textAlign: 'left' }}>{formattedLines}</div>;
    };

    // 使用try/catch包装渲染内容
    try {
        return (
            <div className="resume-history">
                <div className="dialog-container">
                    <div className="dialog-box">
                        <h2>简历修改历史</h2>
                        
                        {loading ? (
                            <div className="loading">加载中...</div>
                        ) : error ? (
                            <div className="error-container">
                                <div className="error-message">{error}</div>
                                <button className="retry-button" onClick={retryLoading}>重试</button>
                            </div>
                        ) : selectedResume ? (
                            // 简历详情视图
                            <div className="resume-detail">
                                <h3>修改详情</h3>
                                <div className="detail-section">
                                    <h4>修改时间</h4>
                                    <p>{formatDate(selectedResume.updatedTime || '')}</p>
                                </div>
                                <div className="detail-section">
                                    <h4>修改描述</h4>
                                    {selectedResume.modificationDescription ? (
                                        <div className="description-content">
                                            <p>{selectedResume.modificationDescription}</p>
                                        </div>
                                    ) : (
                                        <div className="empty-description">未提供修改描述</div>
                                    )}
                                </div>
                                
                                <div className="resume-comparison">
                                    <div className="comparison-column">
                                        <div className="comparison-header">原始简历</div>
                                        <div className="resume-content-card">
                                            {selectedResume.originalContent ? (
                                                <div className="formatted-resume">
                                                    {formatResumeContent(selectedResume.originalContent)}
                                                </div>
                                            ) : (
                                                <div className="empty-content">原始简历内容为空</div>
                                            )}
                                        </div>
                                    </div>
                                    
                                    <div className="arrow-divider">
                                        <div className="arrow">→</div>
                                    </div>
                                    
                                    <div className="comparison-column">
                                        <div className="comparison-header">修改后的简历</div>
                                        <div className="resume-content-card">
                                            {selectedResume.modifiedContent ? (
                                                <div className="formatted-resume">
                                                    {formatResumeContent(selectedResume.modifiedContent)}
                                                </div>
                                            ) : (
                                                <div className="empty-content">修改后内容为空</div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="action-buttons">
                                    <button className="back-button" onClick={backToList}>返回列表</button>
                                </div>
                            </div>
                        ) : resumeHistory.length > 0 ? (
                            // 简历列表视图
                            <div className="resume-list">
                                <p className="dialog-description">您的简历修改记录</p>
                                
                                {/* 搜索框 */}
                                <div className="search-container">
                                    <input 
                                        type="text" 
                                        className="search-input"
                                        placeholder="搜索历史记录..."
                                        value={searchTerm}
                                        onChange={handleSearchChange}
                                    />
                                    {searchTerm && (
                                        <button 
                                            className="search-clear-button"
                                            onClick={clearSearch}
                                        >
                                            ✕
                                        </button>
                                    )}
                                </div>
                                
                                {/* 搜索结果计数 */}
                                {searchTerm && (
                                    <div className="search-result-count">
                                        找到 {filteredHistory.length} 条匹配记录
                                    </div>
                                )}
                                
                                <div className="history-list">
                                    {filteredHistory.length > 0 ? (
                                        filteredHistory.map(resume => (
                                            <div key={resume.id || Math.random()} className="history-item">
                                                <div className="history-item-content" onClick={() => viewResumeDetail(resume.id)}>
                                                    <div className="item-time">{formatDate(resume.createdTime)}</div>
                                                    <div className="item-description">
                                                        {getTruncatedDescription(resume.modificationDescription)}
                                                    </div>
                                                    <div className="item-arrow">➡️</div>
                                                </div>
                                                
                                                {/* 删除按钮 */}
                                                <div className="item-actions">
                                                    {confirmDelete === resume.id ? (
                                                        <div className="confirm-delete">
                                                            <span>确认删除?</span>
                                                            <button 
                                                                className="confirm-yes"
                                                                onClick={(e) => handleDeleteResume(resume.id, e)}
                                                                disabled={isDeleting}
                                                            >
                                                                {isDeleting ? '删除中...' : '是'}
                                                            </button>
                                                            <button 
                                                                className="confirm-no"
                                                                onClick={handleDeleteCancel}
                                                            >
                                                                否
                                                            </button>
                                                        </div>
                                                    ) : (
                                                        <button 
                                                            className="delete-button" 
                                                            onClick={(e) => handleDeleteConfirm(resume.id, e)}
                                                            title="删除此记录"
                                                        >
                                                            🗑️
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="no-results">
                                            <p>没有找到匹配的记录</p>
                                            {searchTerm && (
                                                <button 
                                                    className="clear-search-button"
                                                    onClick={clearSearch}
                                                >
                                                    清除搜索
                                                </button>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ) : (
                            // 空状态
                            <div>
                                <p className="dialog-description">您还没有上传过简历</p>
                                <div className="empty-state">
                                    <div className="empty-icon">📄</div>
                                    <p>上传简历后可以在这里查看历史记录</p>
                                </div>
                            </div>
                        )}
                        
                        <div className="action-buttons">
                            {!selectedResume && <button className="back-button" onClick={onBack}>返回上传</button>}
                        </div>
                    </div>
                </div>
            </div>
        );
    } catch (error) {
        console.error('渲染时发生错误:', error);
        return (
            <div className="error-container">
                <div className="error-message">渲染过程中发生错误</div>
                <button className="retry-button" onClick={() => window.location.reload()}>刷新页面</button>
            </div>
        );
    }
}

// 主导出组件，使用ErrorBoundary包装内容组件
function ResumeReviewHistory(props) {
    return (
        <ErrorBoundary>
            <ResumeReviewHistoryContent {...props} />
        </ErrorBoundary>
    );
}

export default ResumeReviewHistory; 