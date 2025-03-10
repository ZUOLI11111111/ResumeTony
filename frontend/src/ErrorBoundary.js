import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // 更新 state 以便下次渲染时显示降级 UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // 可以将错误日志上报给服务器
    console.error('ErrorBoundary捕获到错误:', error, errorInfo);
    this.setState({ errorInfo });
    
    // 移除React错误覆盖层
    this.removeErrorOverlay();
  }
  
  removeErrorOverlay = () => {
    // 立即尝试移除错误覆盖层
    const removeOverlay = () => {
      const errorOverlays = document.querySelectorAll('body > div');
      errorOverlays.forEach(node => {
        if (node.textContent && node.textContent.includes('Uncaught runtime errors')) {
          node.style.display = 'none';
          node.remove();
        }
      });
    };
    
    // 立即执行一次
    removeOverlay();
    
    // 然后每100ms执行一次，持续1秒
    let count = 0;
    const interval = setInterval(() => {
      removeOverlay();
      count++;
      if (count > 10) {
        clearInterval(interval);
      }
    }, 100);
  }

  render() {
    if (this.state.hasError) {
      // 降级后的 UI
      return (
        <div style={{
          padding: '20px',
          textAlign: 'center',
          color: '#666',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          margin: '20px'
        }}>
          <h2 style={{ color: '#d32f2f' }}>应用遇到了问题</h2>
          <p>我们已经记录了这个错误，请尝试以下操作：</p>
          <ul style={{ 
            listStyle: 'none', 
            padding: 0,
            textAlign: 'left',
            maxWidth: '400px',
            margin: '0 auto',
            lineHeight: '1.8'
          }}>
            <li>- 刷新页面</li>
            <li>- 清除浏览器缓存</li>
            <li>- 检查网络连接</li>
          </ul>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: '10px 20px',
              background: '#4a7bda',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginTop: '20px',
              fontSize: '16px'
            }}
          >
            刷新页面
          </button>
          
          {/* 显示错误详情（仅在开发环境） */}
          {process.env.NODE_ENV === 'development' && (
            <details style={{ 
              marginTop: '20px', 
              textAlign: 'left',
              backgroundColor: '#f1f1f1',
              padding: '10px',
              borderRadius: '4px'
            }}>
              <summary>错误详情</summary>
              <pre style={{ 
                overflow: 'auto', 
                backgroundColor: '#333', 
                color: '#fff',
                padding: '10px',
                borderRadius: '4px' 
              }}>
                {this.state.error && this.state.error.toString()}
                <br />
                {this.state.errorInfo && this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children; 
  }
}

export default ErrorBoundary; 