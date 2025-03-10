import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './app';
import './styles/App.css';
import ErrorBoundary from './ErrorBoundary';

// 完全禁用React错误覆盖层
if (typeof window !== 'undefined') {
  // 覆盖console.error
  const originalConsoleError = console.error;
  console.error = (...args) => {
    // 忽略React特定的错误消息
    if (
      typeof args[0] === 'string' && (
        args[0].includes('React will try to recreate this component tree') ||
        args[0].includes('Uncaught runtime errors') ||
        args[0].includes('Uncaught Invariant Violation') ||
        args[0].includes('Warning:')
      )
    ) {
      return;
    }
    originalConsoleError(...args);
  };

  // 覆盖console.warn
  const originalConsoleWarn = console.warn;
  console.warn = (...args) => {
    // 忽略React特定的警告消息
    if (
      typeof args[0] === 'string' && (
        args[0].includes('Warning:') ||
        args[0].includes('React')
      )
    ) {
      return;
    }
    originalConsoleWarn(...args);
  };

  // 禁用错误处理
  window.addEventListener('error', (event) => {
    // 阻止默认错误处理
    event.preventDefault();
    
    // 检查是否是React错误覆盖层
    if (event.target && event.target.textContent && 
        event.target.textContent.includes('Uncaught runtime errors')) {
      // 阻止事件传播
      event.stopPropagation();
      return false;
    }
  }, true);
  
  // 定期移除错误覆盖层
  setInterval(() => {
    const errorOverlay = document.querySelector('body > div:first-child');
    if (errorOverlay && 
        errorOverlay.textContent && 
        errorOverlay.textContent.includes('Uncaught runtime errors')) {
      errorOverlay.style.display = 'none';
      errorOverlay.remove();
    }
  }, 100);
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <ErrorBoundary>
            <App />
        </ErrorBoundary>
    </React.StrictMode>
);