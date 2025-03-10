package com.resume.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 简历结果实体类
 */
@Data
@TableName("resume_result")
public class ResumeResult {
    
    /**
     * 主键ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;
    
    /**
     * 原始简历内容
     */
    private String originalContent;
    
    /**
     * 修改后的简历内容
     */
    private String modifiedContent;
    
    /**
     * 修改描述
     */
    private String modificationDescription;
    
    /**
     * 创建时间
     */
    private LocalDateTime createdTime;
    
    /**
     * 更新时间
     */
    private LocalDateTime updatedTime;
    
    /**
     * 用户ID（如果有用户系统）
     */
    private String userId;
    
    /**
     * 状态（0：草稿，1：完成）
     */
    private Integer status;
} 