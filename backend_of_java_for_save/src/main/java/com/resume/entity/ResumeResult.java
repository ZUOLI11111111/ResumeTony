package com.resume.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
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
     * 原始内容
     */
    @TableField("original_content")
    private String originalContent;
    
    /**
     * 修改后的内容
     */
    @TableField("modified_content")
    private String modifiedContent;
    
    /**
     * 修改描述
     */
    @TableField("modification_description")
    private String modificationDescription;
    
    /**
     * 创建时间
     */
    @TableField("created_time")
    private LocalDateTime createdTime;
    
    /**
     * 更新时间
     */
    @TableField("updated_time")
    private LocalDateTime updatedTime;
    
    /**
     * 用户ID
     */
    @TableField("user_id")
    private String userId;
    
    /**
     * 状态
     */
    @TableField("status")
    private Integer status;

    /**
     * 简历分类
     */
    @TableField("resume_classification")
    private String resumeClassification;


    /**
     * 具体的简历分类
     */
    @TableField("modified_resume_classification")
    private String modifiedResumeClassification;
} 