import React, { useState } from 'react';
import axios from 'axios';
import './ResumeUpload.css';

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

function ResumeUpload({ languages, apiUrl, onViewHistory }) {
    const [resumeText, setResumeText] = useState('');
    const [modificationRequirements, setModificationRequirements] = useState('');
    const [modifiedResume, setModifiedResume] = useState('');
    const [isModifying, setIsModifying] = useState(false);
    const [sourceLanguage, setSourceLanguage] = useState('中文');
    const [targetLanguage, setTargetLanguage] = useState('中文');
    const [success, setSuccess] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [classifyingStatus, setClassifyingStatus] = useState(''); // 添加分类状态变量
    
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
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 6000000); // 60秒超时
            
            const response = await fetch(`${apiUrl}/api/modify_resume`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    resume_text: resumeText,
                    requirements: modificationRequirements,
                    source_language: sourceLanguage,
                    target_language: targetLanguage
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error("服务器响应错误");
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            setClassifyingStatus("正在分析简历类型...");
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const text = decoder.decode(value);
                console.log("收到的原始数据:", text);
                
                const lines = text.split('\n');
                for (const line of lines) {
                    if (line.trim().startsWith('data:')) {
                        try {
                            const jsonStr = line.substring(5).trim();
                            console.log("解析前的JSON:", jsonStr);
                            const data = JSON.parse(jsonStr);
                            
                            if (data.type === 'start') {
                                // 开始处理，设置语言信息
                                setSourceLanguage(data.sourceLanguage || '中文');
                                setTargetLanguage(data.targetLanguage || '中文');
                                setClassifyingStatus("正在分析简历类型...");
                            } else if (data.type === 'update') {
                                if (data.text) {
                                    setModifiedResume(data.text);
                                }
                            } else if (data.type === 'end1') {
                                setClassifyingStatus("简历分类完成，开始具体分类...");
                            } else if (data.type === 'end12') {
                                setClassifyingStatus("具体分类完成，开始修改...");
                            } else if (data.type === 'end2') {
                                setClassifyingStatus("简历修改完成，正在优化格式...");
                            } else if (data.type === 'end3') {
                                setClassifyingStatus("");
                                setSuccess("简历修改成功！");
                            }
                        } catch (error) {
                            console.error("解析服务器响应出错:", error, line);
                            setClassifyingStatus(`解析响应出错: ${error.message}`);
                        }
                    }
                }
            }
        } catch (error) {
            console.error("请求失败:", error);
            if (error.name === 'AbortError') {
                setModifiedResume("请求超时，可能是后端服务处理时间过长。请尝试简化简历内容或使用更简单的要求。");
            } else if (error.message === 'Failed to fetch' || error.message.includes('network')) {
                setModifiedResume("网络连接错误。请确认Python后端服务(端口5000)已启动并且可访问。");
            } else {
                setModifiedResume("修改过程中出现错误：" + error.message);
            }
            setClassifyingStatus("");
        } finally {
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
            }
        } catch (error) {
            console.error('保存到数据库出错:', error);
        } finally {
            setIsSaving(false);
        }
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
                                <option value="中文">中文</option>
                                {Object.entries(languages)
                                    .filter(([k]) => k !== '中文')
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
                                <option value="中文">中文</option>
                                {Object.entries(languages)
                                    .filter(([k]) => k !== '中文')
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
                </div>
                
                {/* 右侧结果区域 */}
                <div className="output-section">
                    <h3 className="section-title">修改后的简历</h3>
                    
                    {/* 成功提示消息 */}
                    {success && (
                        <div className="success-message">
                            <span className="success-icon">✓</span> {success}
                            {isSaving && <span className="saving-indicator"> (保存中...)</span>}
                        </div>
                    )}
                    
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