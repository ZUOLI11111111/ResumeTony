package com.resume.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.resume.entity.ResumeResult;

/**
 * 简历结果服务接口
 */
public interface ResumeResultService extends IService<ResumeResult> {
    
    /**
     * 保存简历结果
     * @param resumeResult 简历结果对象
     * @return 保存后的简历结果
     */
    ResumeResult saveResumeResult(ResumeResult resumeResult);
    
    /**
     * 根据ID获取简历结果
     * @param id 简历结果ID
     * @return 简历结果对象
     */
    ResumeResult getResumeResultById(Long id);
    
    /**
     * 分页查询简历结果
     * @param page 分页参数
     * @param userId 用户ID
     * @return 分页简历结果
     */
    Page<ResumeResult> pageResumeResults(Page<ResumeResult> page, String userId);
    
    /**
     * 更新简历结果
     * @param resumeResult 简历结果对象
     * @return 更新后的简历结果
     */
    ResumeResult updateResumeResult(ResumeResult resumeResult);
    
    /**
     * 删除简历结果
     * @param id 简历结果ID
     * @return 是否删除成功
     */
    boolean deleteResumeResult(Long id);
} 