package com.resume.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.resume.entity.ResumeResult;
import com.resume.mapper.ResumeResultMapper;
import com.resume.service.ResumeResultService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Objects;

/**
 * 简历结果服务实现类
 */
@Service
public class ResumeResultServiceImpl extends ServiceImpl<ResumeResultMapper, ResumeResult> implements ResumeResultService {

    private static final Logger logger = LoggerFactory.getLogger(ResumeResultServiceImpl.class);

    @Override
    @Transactional
    public ResumeResult saveResumeResult(ResumeResult resumeResult) {
        // 设置创建时间和更新时间
        LocalDateTime now = LocalDateTime.now();
        resumeResult.setCreatedTime(now);
        resumeResult.setUpdatedTime(now);
        
        // 如果状态为空，设置为草稿状态(0)
        if (resumeResult.getStatus() == null) {
            resumeResult.setStatus(0);
        }
        
        // 保存到数据库
        this.save(resumeResult);
        logger.info("保存简历结果成功，ID: {}", resumeResult.getId());
        return resumeResult;
    }

    @Override
    public ResumeResult getResumeResultById(Long id) {
        ResumeResult result = this.getById(id);
        if (result != null) {
            logger.debug("获取简历结果，ID: {}", id);
        } else {
            logger.warn("尝试获取不存在的简历结果，ID: {}", id);
        }
        return result;
    }

    @Override
    public Page<ResumeResult> pageResumeResults(Page<ResumeResult> page, String userId) {
        LambdaQueryWrapper<ResumeResult> queryWrapper = new LambdaQueryWrapper<>();
        
        // 如果用户ID不为空，则按用户ID查询
        if (Objects.nonNull(userId) && !userId.isEmpty()) {
            queryWrapper.eq(ResumeResult::getUserId, userId);
            logger.debug("按用户ID查询简历结果列表，userId: {}", userId);
        } else {
            logger.debug("查询所有简历结果列表");
        }
        
        // 按创建时间降序排列
        queryWrapper.orderByDesc(ResumeResult::getCreatedTime);
        
        Page<ResumeResult> resultPage = this.page(page, queryWrapper);
        logger.debug("查询结果：总条数={}, 当前页={}, 每页大小={}", 
                resultPage.getTotal(), resultPage.getCurrent(), resultPage.getSize());
        return resultPage;
    }

    @Override
    @Transactional
    public ResumeResult updateResumeResult(ResumeResult resumeResult) {
        logger.info("更新简历结果，ID: {}", resumeResult.getId());
        
        // 先检查记录是否存在
        if (!this.getBaseMapper().exists(new LambdaQueryWrapper<ResumeResult>()
                .eq(ResumeResult::getId, resumeResult.getId()))) {
            logger.warn("尝试更新不存在的简历结果，ID: {}", resumeResult.getId());
            return null;
        }
        
        // 设置更新时间
        resumeResult.setUpdatedTime(LocalDateTime.now());
        
        // 更新
        boolean updated = this.updateById(resumeResult);
        if (updated) {
            logger.info("简历结果更新成功，ID: {}", resumeResult.getId());
            return this.getById(resumeResult.getId());
        } else {
            logger.error("简历结果更新失败，ID: {}", resumeResult.getId());
            return null;
        }
    }

    @Override
    @Transactional
    public boolean deleteResumeResult(Long id) {
        logger.info("删除简历结果，ID: {}", id);
        
        // 先检查记录是否存在
        if (!this.getBaseMapper().exists(new LambdaQueryWrapper<ResumeResult>()
                .eq(ResumeResult::getId, id))) {
            logger.warn("尝试删除不存在的简历结果，ID: {}", id);
            return false;
        }
        
        try {
            boolean result = this.removeById(id);
            if (result) {
                logger.info("简历结果删除成功，ID: {}", id);
            } else {
                logger.error("简历结果删除失败，ID: {}", id);
            }
            return result;
        } catch (Exception e) {
            logger.error("删除简历结果时发生异常，ID: {}", id, e);
            throw e; // 重新抛出异常，交由上层处理
        }
    }
} 