import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ResumeUpload from './components/ResumeUpload';
import ResumeReviewHistory from './components/ResumeReviewHistory';
import ErrorBoundary from './ErrorBoundary';

const API_URL = window.location.hostname === 'localhost' ? 'http://localhost:5000' : `https://${window.location.hostname}`;
axios.defaults.timeout = 300000;

// 全局错误处理器
const withErrorHandling = (Component) => {
    return (props) => {
        const [hasError, setHasError] = useState(false);
        
        useEffect(() => {
            const handleError = (error) => {
                console.log('捕获到错误:', error);
                setHasError(true);
            };
            
            window.addEventListener('error', handleError);
            return () => window.removeEventListener('error', handleError);
        }, []);
        
        if (hasError) {
            return (
                <div style={{textAlign: 'center', padding: '20px'}}>
                    <h2>应用出现问题</h2>
                    <p>请刷新页面重试</p>
                    <button 
                        onClick={() => window.location.reload()}
                        style={{
                            padding: '8px 16px',
                            background: '#4a7bda',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }}
                    >
                        刷新页面
                    </button>
                </div>
            );
        }
        
        return (
            <ErrorBoundary>
                <Component {...props} />
            </ErrorBoundary>
        );
    };
};

function AppContent() {
    const [activeView, setActiveView] = useState('resumeUpload');
    const [languages, setLanguages] = useState({});
    
    useEffect(() => {
        checkPythonBackendHealth();
        
        // 清除错误覆盖层
        const clearErrorOverlay = setInterval(() => {
            const errorOverlay = document.querySelector('body > div:first-child');
            if (errorOverlay && 
                errorOverlay.textContent && 
                errorOverlay.textContent.includes('Uncaught runtime errors')) {
                errorOverlay.style.display = 'none';
            }
        }, 100);
        
        return () => clearInterval(clearErrorOverlay);
    }, []);
    
    async function checkPythonBackendHealth() {
        try {
            const response = await axios.get(`${API_URL}/api/health`, {timeout: 5000});
            getLanguages();
        } catch (error) {
            console.error('Python backend is not running');
            try {
                getLanguages();
            } catch (error) {
                console.error('Failed to get languages');
            }
        }
    }
    
    async function getLanguages() {
        try {
            const response = await axios.get(`${API_URL}/api/language`, {timeout: 5000});
            setLanguages(response.data);
        } catch (error) {
            console.error('Failed to get languages');
        }
    }
    
    const showResumeUpload = () => {
        setActiveView('resumeUpload');
    }
    
    const showResumeReviewHistory = () => {
        setActiveView('resumeReviewHistory');
    }
    
    return (
        <div className="app-container">
            <h1>简历修改工具</h1>
            <div className="button">
                <button
                    className={activeView === 'resumeUpload' ? 'active' : ''}
                    onClick={showResumeUpload}
                >上传简历</button>
                <button
                    className={activeView === 'resumeReviewHistory' ? 'active' : ''}
                    onClick={showResumeReviewHistory}
                >查看简历</button>
            </div> 
            {activeView === 'resumeUpload' ? (
                <ResumeUpload languages={languages} apiUrl={API_URL} onViewHistory={showResumeReviewHistory}/>
            ) : (
                <ResumeReviewHistory onBack={showResumeUpload}/>
            )}
        </div>
    );
}

// 使用高阶组件包装App
const App = withErrorHandling(AppContent);

export default App;