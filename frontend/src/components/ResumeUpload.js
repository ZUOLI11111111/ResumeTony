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
        
        try {
            const response = await fetch(`${apiUrl}/api/modify_resume`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    resume_text: resumeText,
                    requirements: modificationRequirements,
                    source_language: sourceLanguage,
                    target_language: targetLanguage
                })
            });
            
            if (!response.ok) {
                throw new Error("服务器响应错误");
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const text = decoder.decode(value);
                const events = text.split('\n\n');
                
                for (const event of events) {
                    if (!event.trim()) continue;
                    
                    // 提取"data:"后面的JSON
                    const match = event.match(/^data:\s*(.+)$/m);
                    if (!match) continue;
                    
                    try {
                        const data = JSON.parse(match[1]);
                        
                        if (data.type === 'update') {
                            setModifiedResume(data.text);
                        } else if (data.type === 'error') {
                            setModifiedResume("抱歉，修改过程中出现错误，请稍后再试。");
                        } else if (data.type === 'end') {
                            setSuccess("修改成功！");
                            // 修改成功后自动保存到数据库
                            saveResultToDatabase(resumeText, data.text, modificationRequirements);
                        }
                    } catch (parseError) {
                        console.error("解析JSON失败:", parseError, match[1]);
                    }
                }
            }
        } catch (error) {
            console.error("请求失败:", error);
            setModifiedResume("抱歉，修改过程中出现错误，请稍后再试。");
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