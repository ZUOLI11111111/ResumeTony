import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ResumeUpload.css';

// 创建支持大数据的axios实例
const api = axios.create({
    baseURL: process.env.REACT_APP_PYTHON_API_URL || 'http://localhost:5000/api',  // 使用环境变量
    timeout: 600000, // 增加超时时间到60秒
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Access-Control-Allow-Origin': '*'
    },
    maxContentLength: Infinity, // 允许无限大小的内容
    maxBodyLength: Infinity // 允许无限大小的请求体
});

// 设置后端API的基础URL，确保一致性
const BACKEND_BASE_URL = process.env.REACT_APP_PYTHON_API_URL ? process.env.REACT_APP_PYTHON_API_URL.replace('/api', '') : 'http://localhost:5000';

function ResumeUpload({ languages, apiUrl, onViewHistory }) {
    const [resumeText, setResumeText] = useState('');
    const [modificationRequirements, setModificationRequirements] = useState('');
    const [modifiedResume, setModifiedResume] = useState('');
    const [isModifying, setIsModifying] = useState(false);
    const [sourceLanguage, setSourceLanguage] = useState('zh');  // 修改为代码值而不是显示值
    const [targetLanguage, setTargetLanguage] = useState('zh');  // 修改为代码值而不是显示值
    const [success, setSuccess] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [classifyingStatus, setClassifyingStatus] = useState(''); // 添加分类状态变量
    const [error, setError] = useState(null); // 添加错误状态，使用null表示没有错误
    const [connectionStatus, setConnectionStatus] = useState('未连接'); // 添加SSE连接状态变量
    
    // 添加调试钩子，跟踪状态变化
    useEffect(() => {
        console.log("状态变量 classifyingStatus 更新:", classifyingStatus);
    }, [classifyingStatus]);
    
    useEffect(() => {
        console.log("状态变量 error 更新:", error);
    }, [error]);
    
    useEffect(() => {
        console.log("状态变量 success 更新:", success);
    }, [success]);
    
    useEffect(() => {
        console.log("状态变量 connectionStatus 更新:", connectionStatus);
    }, [connectionStatus]);
    
    const handleTextChange = (e) => {
        setResumeText(e.target.value);
    };
    
    const handleRequirementsChange = (e) => {
        setModificationRequirements(e.target.value);
    };
    
    async function handleTextOutput() {
        setIsModifying(true);
        setModifiedResume(""); // 清空之前的结果
        setSuccess(""); // 清空成功消息
        setClassifyingStatus(""); 
        setError(null); // 清空错误消息
        setConnectionStatus("请求中"); // 设置初始连接状态
        
        try {
            console.log("正在初始化简历处理...");
            console.log("发送数据:", {
                resume_text: resumeText.substring(0, 50) + "...",
                requirements: modificationRequirements,
                source_language: sourceLanguage,
                target_language: targetLanguage
            });
            
            // 第一步：发送初始化请求，获取会话ID
            const initResponse = await api.post('/initialize_resume', {
                resume_text: resumeText,
                requirements: modificationRequirements,
                source_language: sourceLanguage,
                target_language: targetLanguage
            });
            
            console.log("初始化响应:", initResponse);
            
            if (!initResponse.data || initResponse.data.status !== 'success') {
                throw new Error('初始化失败: ' + (initResponse.data?.message || '未知错误'));
            }
            
            const sessionId = initResponse.data.session_id;
            console.log("获取到会话ID:", sessionId);
            
            // 第二步：使用会话ID建立SSE连接
            const sseUrl = `${BACKEND_BASE_URL}/api/modify_resume?session_id=${sessionId}`;
            console.log("建立SSE连接:", sseUrl);
            
            const eventSource = new EventSource(sseUrl);
            console.log("EventSource对象已创建:", eventSource);
            
            // 设置超时保护
            const timeout = setTimeout(() => {
                console.log("请求超时，关闭连接");
                eventSource.close();
                setClassifyingStatus("");
                setError("请求超时，可能是后端服务处理时间过长。请尝试简化简历内容或使用更简单的要求。");
                setIsModifying(false);
            }, 3000000); // 5分钟超时
            
            // 处理连接打开
            eventSource.onopen = (event) => {
                console.log("SSE连接已打开:", event);
                setConnectionStatus('已连接');
                setClassifyingStatus("连接已建立，等待处理...");
            };
            
            // 处理开始事件
            eventSource.addEventListener('start', (event) => {
                console.log("收到start事件:", event.data);
                setConnectionStatus('处理中');
                try {
                    const data = JSON.parse(event.data);
                    console.log("解析后的start数据:", data);
                    setSourceLanguage(data.sourceLanguage || 'zh');
                    setTargetLanguage(data.targetLanguage || 'zh');
                } catch (e) {
                    console.error("解析start事件数据失败:", e, event.data);
                }
            });
            eventSource.addEventListener('is_resume', (event) => {
                console.log("收到is_resume事件:", event.data);
                try {
                    // 解析JSON数据
                    const data = JSON.parse(event.data);
                    console.log("解析后的is_resume数据:", data);
                    
                    // 获取真正的判断结果
                    const result = data.text;
                    console.log("提取的判断结果:", result);
                    
                    if (result === 'no' || result === '"no"') {
                        console.log("判断为不是简历，显示错误信息");
                        setClassifyingStatus("");  // 清除分类状态
                        setModifiedResume("");  // 清空修改后的简历区域
                        
                        // 使用直接显示错误的函数，指定错误类型
                        showError("输入内容不是简历，请重新输入有效的简历内容", "resume-error");
                        
                        // 停止加载状态
                        setIsModifying(false);
                        // 关闭超时计时器
                        clearTimeout(timeout);
                        // 关闭连接
                        eventSource.close();
                    } else if (result === 'yes' || result === '"yes"') {
                        console.log("判断为是简历，继续处理");
                        setClassifyingStatus("输入内容是简历，开始分类...");
                    } else {
                        console.warn("收到未知的is_resume结果:", result);
                        setClassifyingStatus("正在处理输入内容...");
                    }
                } catch (e) {
                    console.error("解析is_resume事件数据失败:", e, event.data);
                    setClassifyingStatus("正在处理输入内容...");
                    // 尝试在解析失败时显示错误
                    showError("解析判断结果失败，请查看控制台日志", "system-error");
                }
            });
            // 处理进度更新
            eventSource.addEventListener('classified_progress', (event) => {
                console.log("收到classified_progress事件:", event.data);
                setConnectionStatus('接收数据');
                try {
                    const data = JSON.parse(event.data);
                    console.log("解析后的progress数据:", data);
                    setClassifyingStatus("简历分类中...");
                } catch (e) {
                    console.error("解析classified_progress事件数据失败:", e, event.data);
                }
            });
            
           

            eventSource.addEventListener('classified', (event) => {
                console.log("收到classified事件:", event.data);
                setClassifyingStatus("简历分类完成，开始具体分类...");
                const data = JSON.parse(event.data);
                setModifiedResume(data.text);
            });
            
            // 处理更新事件
            eventSource.addEventListener('update', (event) => {
                console.log("收到update事件:", event.data);
                try {
                    const data = JSON.parse(event.data);
                    console.log("解析后的update数据:", data);
                    setModifiedResume(data.text);
                } catch (e) {
                    console.error("解析update事件数据失败:", e, event.data);
                }
            });
            
            // 处理分类完成事件
            eventSource.addEventListener('detailed_classified', (event) => {
                console.log("收到detailed_classified事件:", event.data);
                try {
                    const data = JSON.parse(event.data);
                    console.log("解析后的detailed_classified数据:", data);
                    setClassifyingStatus("简历分类完成，开始具体分类...");
                } catch (e) {
                    console.error("解析detailed_classified事件数据失败:", e, event.data);
                }
            });
            
            // 处理详细分类完成事件
            eventSource.addEventListener('detail_classified', (event) => {
                console.log("收到detail_classified事件:", event.data);
                try {
                    const data = JSON.parse(event.data);
                    console.log("解析后的detail_classified数据:", data);
                    setClassifyingStatus("具体分类完成，开始修改...");
                } catch (e) {
                    console.error("解析detail_classified事件数据失败:", e, event.data);
                }
            });
            
            // 处理修改完成事件
            eventSource.addEventListener('modified', (event) => {
                console.log("收到modified事件:", event.data);
                try {
                    const data = JSON.parse(event.data);
                    console.log("解析后的modified数据:", data);
                    setModifiedResume(data.text);
                    setClassifyingStatus("简历修改完成，正在优化格式...");
                } catch (e) {
                    console.error("解析modified事件数据失败:", e, event.data);
                }
            });
            
            // 处理格式更新事件
            eventSource.addEventListener('format_update', (event) => {
                console.log("收到format_update事件:", event.data);
                try {
                    const data = JSON.parse(event.data);
                    console.log("解析后的format_update数据:", data);
                    setModifiedResume(data.text);
                } catch (e) {
                    console.error("解析format_update事件数据失败:", e, event.data);
                }
            });
            
            // 处理最终结果事件
            eventSource.addEventListener('final', (event) => {
                console.log("收到final事件:", event.data);
                try {
                    const data = JSON.parse(event.data);
                    console.log("解析后的final数据:", data);
                    setModifiedResume(data.text);
                    setClassifyingStatus("");
                    
                    // 自动保存到数据库
                    //saveResultToDatabase(resumeText, data.text, modificationRequirements);
                } catch (e) {
                    console.error("解析final事件数据失败:", e, event.data);
                }
            });
            
            // 处理成功事件
            eventSource.addEventListener('success', (event) => {
                console.log("收到success事件:", event.data);
                try {
                    const data = JSON.parse(event.data);
                    console.log("解析后的success数据:", data);
                    setSuccess(data.text);
                    clearTimeout(timeout);
                    eventSource.close();
                    setIsModifying(false);
                } catch (e) {
                    console.error("解析success事件数据失败:", e, event.data);
                }
            });
            
            // 处理错误事件
            eventSource.addEventListener('error', (event) => {
                console.error("SSE错误事件:", event);
                console.error("event.data:", event.data);
                console.error("event类型:", typeof event);
                console.error("event属性:", Object.keys(event));
                
                // 使用直接显示错误函数，指定类型为连接错误
                showError("连接服务器时发生错误，请检查网络连接", "connection-error");
                
                if (event.data) {
                    try {
                        const data = JSON.parse(event.data);
                        console.error("解析后的错误数据:", data);
                        showError(`服务器错误: ${data.text}`, "connection-error");
                    } catch (e) {
                        console.error("解析错误事件数据失败:", e, event.data);
                        showError("服务器错误，无法解析错误信息", "connection-error");
                    }
                } else {
                    showError("与服务器连接出现问题", "connection-error");
                }
                
                clearTimeout(timeout);
                eventSource.close();
                setIsModifying(false);
            });
            
            // 处理默认消息 (onmessage)
            eventSource.onmessage = (event) => {
                console.log("收到默认消息事件 (onmessage):", event.data);
                try {
                    const data = JSON.parse(event.data);
                    console.log("解析后的默认消息数据:", data);
                    setClassifyingStatus("收到服务器消息: " + (data.text || JSON.stringify(data)));
                } catch (e) {
                    console.error("解析默认消息事件数据失败:", e, event.data);
                    setClassifyingStatus("收到服务器消息(无法解析): " + event.data);
                }
            };
            
            // 处理EventSource本身的错误
            eventSource.onerror = (error) => {
                console.error("EventSource错误:", error);
                setConnectionStatus('连接错误');
                clearTimeout(timeout);
                eventSource.close();
                setClassifyingStatus("");
                
                // 获取更详细的错误信息
                let errorMessage = "连接错误，请确认后端服务运行正常。";
                if (error && error.status) {
                    errorMessage += ` 状态码: ${error.status}`;
                }
                if (error && error.statusText) {
                    errorMessage += ` 原因: ${error.statusText}`;
                }
                
                console.error("详细错误信息:", errorMessage);
                // 使用直接显示错误函数
                showError(errorMessage);
                setIsModifying(false);
            };
            
        } catch (error) {
            console.error("请求失败:", error);
            
            if (error.name === 'AbortError') {
                setError("请求超时，可能是后端服务处理时间过长。请尝试简化简历内容或使用更简单的要求。");
            } else if (error.message.includes('Failed to fetch') || error.message.includes('network')) {
                setError("网络连接错误。请确认Python后端服务(端口5000)已启动并且可访问。");
            } else {
                setError("修改过程中出现错误：" + error.message);
            }
            
            setClassifyingStatus("");
            setIsModifying(false);
        }
    }

    // 保存结果到数据库
    const saveResultToDatabase = async (originalContent, modifiedContent, description) => {
        try {
            setIsSaving(true);
            console.log('开始保存简历修改结果到数据库...');
            console.log('原始内容长度:', originalContent.length);
            console.log('修改后内容长度:', modifiedContent.length);
            
            const response = await api.post('/resume', {
                originalContent: originalContent,
                modifiedContent: modifiedContent,
                modificationDescription: description || '',
                userId: 'user123', // 可以从用户登录信息中获取
                status: 1 // 1表示已完成
            });
            
            console.log('保存响应:', response);
            
            if (response.data && response.data.success) {
                setSuccess(prev => prev + " 已保存到历史记录！");
                console.log('保存成功，ID:', response.data.data.id);
            } else {
                console.error('保存失败:', response.data);
                setError(prev => prev + " 保存到历史记录失败！");
            }
        } catch (error) {
            console.error('保存到数据库出错:', error);
            setError(prev => prev + " 保存到数据库出错：" + error.message);
        } finally {
            setIsSaving(false);
        }
    };
    
    // 测试SSE连接
    const testSseConnection = () => {
        setConnectionStatus("测试连接中");
        setClassifyingStatus("正在测试SSE连接...");
        setError("");
        
        console.log("开始测试SSE连接");
        
        // 连接到测试端点
        const eventSource = new EventSource(`${BACKEND_BASE_URL}/api/test_sse`);
        
        // 处理测试消息
        eventSource.addEventListener('test', (event) => {
            console.log("收到测试事件:", event.data);
            try {
                const data = JSON.parse(event.data);
                setClassifyingStatus(data.text);
                setConnectionStatus("连接正常");
            } catch (e) {
                console.error("解析测试事件数据失败:", e, event.data);
            }
        });
        
        // 处理连接打开
        eventSource.onopen = (event) => {
            console.log("测试连接已打开:", event);
            setConnectionStatus("测试连接已打开");
        };
        
        // 处理错误
        eventSource.onerror = (error) => {
            console.error("测试连接错误:", error);
            setConnectionStatus("测试连接失败");
            setError("SSE连接测试失败，请检查后端服务");
            eventSource.close();
        };
        
        // 10秒后自动关闭
        setTimeout(() => {
            console.log("测试完成，关闭连接");
            eventSource.close();
        }, 12000);
    };
    
    // 添加直接显示错误的函数
    const showError = (message, errorType = 'general') => {
        console.log("显示错误:", message, "类型:", errorType);
        
        // 设置React状态
        setError({
            message: message,
            type: errorType
        });
        
        // 滚动到错误消息位置
        setTimeout(() => {
            const errorElement = document.querySelector('.error-message');
            if (errorElement) {
                errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 100);
    };
    
    return (
        <div className="resume-upload">
            <div className="split-container">
                {/* 左侧输入区域 */}
                <div className="input-section">
                    {/* 添加相对定位容器 */}
                    <div className="section-header">
                        <h3 className="section-title">原始简历</h3>
                        
                        {/* 右上角语言选择器和转换箭头 */}
                        <div className="top-right-language-selector">
                            {/* 源语言选择器 */}
                            <select 
                                value={sourceLanguage} 
                                onChange={(e) => setSourceLanguage(e.target.value)}
                                className="language-select-corner"
                            >
                                {Object.entries(languages)
                                    .map(([k, v]) => (
                                        <option key={`source-${k}`} value={k}>{v}</option>
                                    ))
                                }
                            </select>
                            
                            {/* 转换箭头 */}
                            <div className="language-arrow">→</div>
                            
                            {/* 目标语言选择器 */}
                            <select 
                                value={targetLanguage} 
                                onChange={(e) => setTargetLanguage(e.target.value)}
                                className="language-select-corner"
                            >
                                {Object.entries(languages)
                                    .map(([k, v]) => (
                                        <option key={`target-${k}`} value={k}>{v}</option>
                                    ))
                                }
                            </select>
                        </div>
                    </div>
                    
                    {/* 修改要求输入框 */}
                    <div className="requirements-container">
                        <label htmlFor="modification-requirements" className="requirements-label">修改要求：</label>
                        <textarea 
                            id="modification-requirements"
                            className="requirements-input"
                            placeholder="请输入您对简历修改的具体要求..."
                            value={modificationRequirements}
                            onChange={handleRequirementsChange}
                        ></textarea>
                    </div>
                    
                    <div className="text-input-area">
                        <textarea 
                            className="resume-text-input"
                            placeholder="请在此粘贴您的简历文本..."
                            value={resumeText}
                            onChange={handleTextChange}
                        ></textarea>
                    </div>
                </div>
                
                {/* 中间按钮区域 */}
                <div className="action-section">
                    <button 
                        className="submit-button"
                        onClick={handleTextOutput}
                        disabled={isModifying || !resumeText.trim()}
                    >
                        {isModifying ? '修改中...' : '开始修改'}
                    </button>
                    
                    <button 
                        className="history-button" 
                        onClick={onViewHistory}
                    >
                        查看历史
                    </button>
                    
                    <button 
                        className="test-button" 
                        onClick={testSseConnection}
                        disabled={isModifying}
                    >
                        测试连接
                    </button>
                </div>
                
                {/* 右侧结果区域 */}
                <div className="output-section">
                    <h3 className="section-title">修改后的简历</h3>
                    
                    {/* 错误提示消息 - 使用新的样式组件 */}
                    {error && (
                        <div className={`error-message ${error.type || ''}`}>
                            <div className="error-message-header">
                                {error.type === 'connection-error' ? 
                                    <span><i className="error-icon">🔌</i> 连接错误</span> : 
                                    error.type === 'resume-error' ? 
                                    <span><i className="error-icon">📄</i> 简历格式错误</span> : 
                                    <span><i className="error-icon">⚠️</i> 错误提示</span>
                                }
                                <span className="close-button" onClick={() => setError(null)}>×</span>
                            </div>
                            
                            <div className="error-message-body">
                                {error.type === 'connection-error' && <div className="connection-error-icon">🔌</div>}
                                {error.type === 'resume-error' && <div className="connection-error-icon">📄</div>}
                                <p>{error.message}</p>
                            </div>
                            
                            <div className="error-message-footer">
                                <button 
                                    className="try-again-button"
                                    onClick={() => setError(null)}
                                >
                                    我知道了
                                </button>
                            </div>
                        </div>
                    )}
                    
                    {/* 测试错误按钮 */}
                    <button 
                        onClick={() => showError("这是一个测试错误消息", "resume-error")}
                        style={{margin: '5px 0', padding: '5px 10px', background: '#ffdddd', border: '1px solid #ffaaaa', borderRadius: '3px', cursor: 'pointer', fontSize: '12px'}}
                    >
                        测试简历错误
                    </button>
                    <button 
                        onClick={() => showError("这是一个连接错误测试消息", "connection-error")}
                        style={{margin: '5px 0 5px 5px', padding: '5px 10px', background: '#ddddff', border: '1px solid #aaaaff', borderRadius: '3px', cursor: 'pointer', fontSize: '12px'}}
                    >
                        测试连接错误
                    </button>
                    
                    {/* 成功提示消息 */}
                    {success && (
                        <div className="success-message">
                            <span className="success-icon">✓</span> {success}
                            {isSaving && <span className="saving-indicator"> (保存中...)</span>}
                        </div>
                    )}
                    
                    {/* 连接状态显示 */}
                    <div className="connection-status">
                        <span className="connection-label">连接状态:</span> 
                        <span className={`connection-value ${connectionStatus === '未连接' ? 'disconnected' : 
                                        connectionStatus === '连接错误' ? 'error' : 
                                        connectionStatus === '已连接' ? 'connected' : 'processing'}`}>
                            {connectionStatus}
                        </span>
                    </div>
                    
                    {/* 分类状态提示 */}
                    {classifyingStatus && (
                        <div className="classifying-status">
                            <span className="classifying-icon">⏳</span> {classifyingStatus}
                        </div>
                    )}
                    
                    <div className="text-output-area">
                        <textarea 
                            className="resume-text-output"
                            placeholder="修改后的简历将显示在这里"
                            value={modifiedResume}
                            readOnly
                        ></textarea>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ResumeUpload;