package com.resume.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.resume.entity.ResumeResult;
import com.resume.service.ResumeResultService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 简历结果控制器
 */
@RestController
@RequestMapping("/resume")
public class ResumeResultController {

    private static final Logger logger = LoggerFactory.getLogger(ResumeResultController.class);

    @Autowired
    private ResumeResultService resumeResultService;

    /**
     * 保存简历结果
     * @param resumeResult 简历结果对象
     * @return 响应实体
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> saveResumeResult(@RequestBody ResumeResult resumeResult) {
        logger.info("接收到保存简历请求，内容长度：original={}, modified={}",
                resumeResult.getOriginalContent() != null ? resumeResult.getOriginalContent().length() : 0,
                resumeResult.getModifiedContent() != null ? resumeResult.getModifiedContent().length() : 0);
        
        try {
            ResumeResult saved = resumeResultService.saveResumeResult(resumeResult);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "简历结果保存成功");
            response.put("data", saved);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("保存简历时发生错误", e);
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "保存失败: " + e.getMessage());
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 获取简历结果详情
     * @param id 简历结果ID
     * @return 响应实体
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getResumeResult(@PathVariable Long id) {
        ResumeResult resumeResult = resumeResultService.getResumeResultById(id);
        
        Map<String, Object> response = new HashMap<>();
        if (resumeResult != null) {
            response.put("success", true);
            response.put("data", resumeResult);
        } else {
            response.put("success", false);
            response.put("message", "未找到ID为" + id + "的简历结果");
        }
        
        return ResponseEntity.ok(response);
    }

    /**
     * 分页查询简历结果
     * @param current 当前页码
     * @param size 每页大小
     * @param userId 用户ID
     * @return 响应实体
     */
    @GetMapping("/page")
    public ResponseEntity<Map<String, Object>> pageResumeResults(
            @RequestParam(defaultValue = "1") long current,
            @RequestParam(defaultValue = "10") long size,
            @RequestParam(required = false) String userId) {
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            // 验证参数
            if (current < 1) {
                current = 1;
            }
            if (size < 1 || size > 100) {
                size = 10; // 限制每页最大记录数
            }
            
            Page<ResumeResult> page = new Page<>(current, size);
            Page<ResumeResult> resultPage = resumeResultService.pageResumeResults(page, userId);
            
            response.put("success", true);
            response.put("data", resultPage);
        } catch (Exception e) {
            logger.error("分页查询简历结果时发生错误", e);
            response.put("success", false);
            response.put("message", "查询失败: " + e.getMessage());
            // 提供空的分页结果，避免前端解析错误
            Page<ResumeResult> emptyPage = new Page<>(current, size);
            response.put("data", emptyPage);
        }
        
        return ResponseEntity.ok(response);
    }

    /**
     * 更新简历结果
     * @param id 简历结果ID
     * @param resumeResult 简历结果对象
     * @return 响应实体
     */
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateResumeResult(
            @PathVariable Long id,
            @RequestBody ResumeResult resumeResult) {
        
        resumeResult.setId(id);
        ResumeResult updated = resumeResultService.updateResumeResult(resumeResult);
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "简历结果更新成功");
        response.put("data", updated);
        
        
        return ResponseEntity.ok(response);
    }

    /**
     * 删除简历结果
     * @param id 简历结果ID
     * @return 响应实体
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteResumeResult(@PathVariable Long id) {
        logger.info("接收到删除简历请求，ID: {}", id);
        
        Map<String, Object> response = new HashMap<>();
        
        try {
            // 先检查记录是否存在
            ResumeResult resumeResult = resumeResultService.getResumeResultById(id);
            if (resumeResult == null) {
                logger.warn("尝试删除不存在的记录，ID: {}", id);
                response.put("success", false);
                response.put("message", "删除失败，记录不存在");
                return ResponseEntity.ok(response);
            }
            
            // 执行删除操作
            boolean deleted = resumeResultService.deleteResumeResult(id);
            
            if (deleted) {
                logger.info("成功删除简历记录，ID: {}", id);
                response.put("success", true);
                response.put("message", "简历结果删除成功");
            } else {
                logger.error("删除简历记录失败，ID: {}", id);
                response.put("success", false);
                response.put("message", "删除操作失败");
            }
        } catch (Exception e) {
            logger.error("删除简历时发生异常，ID: {}", id, e);
            response.put("success", false);
            response.put("message", "删除过程中发生错误: " + e.getMessage());
        }
        
        return ResponseEntity.ok(response);
    }
} 