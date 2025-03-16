example_resume = """
            个人简历
基本信息
姓名:安永瑞  		     
学校:深圳大学(本科大二)
年龄:19岁 				
专业:自动化 2023-09 - 2027-07
性别:男					
身高体重 :176cm / 77kg
民族:朝鲜族				
籍贯:天津
手机号码:18902013621		
邮箱:254054663@qq.com
主修课程：C/C++程序设计、数据结构、操作系统、数据库、计算机网络
项目经验
ShardKV(基于MIT6.824课程)：
1.完成了基于MapReduce论文的分布式计算框架实现，深入理解了分布式计算的设计理念和执行流程。
2.实现了完整的Raft协议，包括Leader Election、AppendEntry RPC等关键组件，并通过Labrpc模拟网络环境进行测试。
3. 基于Raft协议开发了KV数据库，并实现了Snapshot RPC功能，增强了系统的可扩展性和数据一致性。
4.在KV数据库基础上实现了Sharding分片功能，提升了系统的横向扩展能力，并实现了multi Raft功能，增强了系统的容错性。
Bustub:
1.设计并实现了一个高效的LRU缓存淘汰算法，用于管理buffer pool
2.利用B+树索引结构，优化了数据的存储和检索过程
HM点评:
1.负责项目中Redis技术栈的选型和应用，实现了短信登录、商户查询缓存、优惠券秒杀等功能。
2.设计并实现了共享Session登录流程，解决了集群环境下的Session共享问题。
3.实现了商户查询缓存，包括缓存一致性、缓存穿透、雪崩和击穿的解决方案。
4.利用Redis的计数器功能和Lua脚本完成了高性能的秒杀下单操作。
5.通过Redis分布式锁防止了优惠券秒杀中的超卖问题。 
技能特长
C++:熟练使用stl 理解RAII思想
Java:熟练掌握OOP编程思想 掌握JavaSE基础知识
熟悉cursor windsurf bolt.new v0.dev 主流ai工具 
熟悉linux操作系统 
了解过langchain langgraph rag           
            """
error_format = """
            错误格式：
           **简历**

**一、教育背景**

- 2018年9月 - 2022年6月，XX大学，计算机科学与技术专业，本科

**二、专业**

- 熟练掌握Java编程语言，熟悉面向对象编程思想
- 熟悉计算机网络、操作系统、数据结构与算法等计算机基础知识

**三、项目经验**

- **项目名称**：XX电商平台
  - **时间**：2021年3月 - 2021年6月
  - **职责**：负责商品模块的后端开发，包括商品信息管理、订单处理等
  - **技术**：Java、Spring Boot、MySQL

- **项目名称**：XX教育管理系统
  - **时间**：2020年9月 - 2021年1月
  - **职责**：参与系统整体架构设计，负责用户管理模块的开发
  - **技术**：Java、Spring Cloud、MyBatis

**四、技能特长**

- 熟练使用Java、Spring Boot、MyBatis等开发框架
- 熟悉MySQL数据库操作和优化
- 熟练使用Git进行版本控制
- 良好的代码编写习惯和团队协作精神

**五、自我评价**

本人性格开朗，学习能力强，对新技术有较强的兴趣。在项目开发过程中，能够快速适应新技术，具备独立解决问题的能力。具备良好的沟通能力和团队合作精神。

**六、实习经历**

- **实习单位**：XX科技有限公司
  - **时间**：2021年7月 - 2021年9月
  - **职责**：参与公司内部项目的开发，负责模块的单元测试和bug修复
  - **收获**：提高了实际项目开发经验，加深了对软件工程的理解

**七、竞赛经历**

- **竞赛名称**：XX大学程序设计竞赛
  - **时间**：2019年11月
  - **成绩**：一等奖

**八、荣誉奖项**

- XX大学优秀毕业生
- XX大学三好学生

**九、其他经历**

- 参与组织XX大学计算机协会活动，负责技术分享和活动策划
- 参与编写XX大学计算机专业教材，负责编写部分章节

**请注意**：以上简历内容为示例，具体信息请根据个人实际情况进行修改。
            """
example_text_4_java = """
简 历

基本信息：
姓　 名：　吴春雷 学　　历：　本科
性　　别：　男 籍 贯： 湖北
年　　龄：　26 现居住地：　武汉
毕业院校： 湖北文理学院 工作年限：　3年
联系电话：　18307202857 E-Mail ： work_account@foxmail.com

自我评价：

学习能力强，思路清晰，善于从整体上分析、把握复杂事物，对细节难题具备快速钻研解决能力；
能快速地融入、凝聚团队；
良好的表达与沟通能力，积极主动，对工作尽心尽责；
能够适应加班出差，具有良好的抗压能力；
6、马拉松、中长线徒步、中长线骑行爱好者，能够将体能的韧性迁移到工作中来。
求职意向：
工作性质： 全职
目标地点： 武汉
目标职能： java开发工程师
目前状况： 在职(考虑工作机会)
期望薪资： 面议
开发技能：

Java基础扎实，理解并能使用Java 多线程及线程池，集合框架，IO类库等，良好的编程习惯
熟悉主流Spring、SpringBoot、SpringMVC、MyBatis等框架，快速上手新型框架
熟练使用Oracle、MySQL关系型数据库
熟悉利用redis来实现的缓存、分布式锁、分布式session、前后端分离、页面静态化、秒杀优化等技术
熟悉dubbo+zookeeper（分布式服务框架）、webService、HttpClient远程服务调用技术
熟悉rabbitMq消息队列
熟练使用Eclipse,MyEclipse做Junit单元测试
熟练的优化能力(代码优化、业务优化、sql优化等)
熟练使用tomcat服务器、SVN版本管理工具、Maven项目构建工具、FindBugs项目管理工具
熟练使用js、jQuery、ECharts等前台集成UI框架技术
掌握编写接口文档和接口开发
具有一定的开发小组管理经验、能够完成公共组件的封装
熟悉linux常用命令、redis服务部署、RabbitMQ的安装、MySQL数据库的安装使用
了解nginx
工作经历：
软通动力信息技术有限公司华为事业部
职位名称：JAVA开发工程师（开发组小组长）
工作时间：2017年02月 –至今
工作描述：1、与产品部门对接相关需求及可行性讨论，落地。
2、开发相关模块代码编写和相关接口设计。
3、与第三方公司进行业务协调，接口通信。
4、负责将小组任务交付测试，协助运维上线。
5、修改线上BUG，设计后期项目调优。
武汉兰芯数据定向媒体有限公司
职位名称：JAVA开发工程师
工作时间：2015年9月 – 2017年01月
工作描述：1、参与系统部分设计以及功能模块的详细设计
2、配合小组完成系统模块任务分配、开发工作。
3、解决系统的流程问题、数据采集问题、整改问题。
4、配合对现有系统的升级做出升级方案。

项目经历：
项目一：2017.02-至今 中国移动湖北网上营业厅
软件环境： Struts2+Spring + Mybatis + duboo + zookeeper + nginx + weblogic
开发工具： Eclipse + Oracle+ Tomcat8.0 + JDK1.8 + SVN + Ant
责任描述： 主要参与湖北移动天猫对账重构；网厅在线号卡销售流程技术方案选型与设计开发，订单管理，数据库优化以及相关文档编写；融合家庭宽带充值缴费重构优化；京东物流系统开发对接；带领新人等
项目描述： 本项目为一个网上购物平台，包含前台购物平台，我的移动平台，后台管理系统。前端网站主要是一个形成订单的过程，涉及了选号，套餐，流量专区，宽带专区，增值业务，手机以及智能硬件，其中选号与宽带专区为移动首推重点业务；前台购物平台主要是一个形成订单的过程，涵盖首页的产品导航展示，充值缴费，产品的订购。我的移动平台
主要包括个人信息，花费账单，套餐使用量，增值业务，上网日志，历史记录，我的宽带等；后台管理模块主要包括权限模块，产品配置，问题处理中心，订单管理模块(派单，审批，流转等功能)等
项目二：2017.02-至今 中国移动湖北网厅能力开放平台
软件环境： JFina + duboo + zookeeper + nginx + weblogic
开发工具： Eclipse + Oracle+ Tomcat8.0 + JDK1.8 + SVN + Ant
责任描述： 主要参与湖北移动在线号卡销售流程接口设计与开发；湖北移动网厅与集团商城号卡销售订单对接模块的设计与开发；号卡销售与京东物流对接的接口开发；裸宽续费接口开发；优惠券接口开发；带领新人等
项目描述： 为提供运营商特色能力服务、做大连接，达到连接更简单合作更容易的目的，衍生出网厅能力开放平台，为各渠道提供丰富的能力接口

项目三：2016.11-2017.01 武汉市公安局数据定制平台（号卡标准化项目子项目）
软件环境： SpringMVC+Hibernate+Spring jdbc(jeecg 开源框架)
开发工具： Eclipse + Oracle11g+ Tomcat5.5 + JDK1. + SVN + Maven
责任描述： 主要参与需求调研、需求分析、业务模块的划分、Bug修复；采用多线程技术完成大数据量的数据推送，echarts技术为分局用户做到丰富数据的图形化展示
项目描述： 依赖业务系统数据源采用反向建表方式按照公安部标准在目标库中创建相应的标准表结构，将数据推送到用户表中完成数据定制
项目四：2016.09-2016.11 任务调度平台
软件环境： LTS轻量级分布式任务调度开源框架
开发工具： MyEclipse + Oracle11g + jdk1.6 +tomcat5.5+Maven
责任描述： 主要参与需求分析，业务模块划分；执行ktr文件模块开发及单元测试，集成测试
项目描述： 为提高频繁手动通过kettle执行大量ktr文件效率，减少单个kettle的负载压力，采用分布式任务调度形式定时执行ktr文件,保证各大轨迹类数据每日增量稳定抽取。
项目五：2015.09-2016.09 武汉市公安局标准化平台
软件环境： SDC开发平台 （Struts2+spring+ibatis 基础架构）
开发工具： Eclipse + Oracle11g + jdk1.6 + tomcat5.5 + svn + Maven
责任描述： 主要完成项目经理分配需求的程序设计及Bug修复。前端、终端数据采集模块；数据地图模块；数据推送模块；数据质量管理模块；数据元模块；数据预警模块；数据对标等
项目描述： 公安部颁发数据元标准后，为了规范公安系统的管理与建设，建立此支撑项目。公安局将各个支队及分局的数据结构和数据抽入汇集库统一管理。标准化项目是对汇集库的各个表及数据的管理。标准化项目主要分为数据标准子系统、数据质量子系统、数据服务子系统等。	
"""

example_text_4_marketing = """
市场营销专业简历：
求职意向
求职类型：全职   
意向岗位：市场营销专家   
意向城市：广东广州   
薪资要求：面议   
求职状态：随时到岗   
工作经历
时间：20xx.2-20xx.2   公司名称：幻主简历公司1   职位名称：市场营销部营销组长   
-企业钻石系列推广，使用各类营销手段打破老产品的瓶颈期，实现项目的正常增长。 成绩：从负增长到正两位数增长；开创525活动日；产品微杂志推广。
-Forevermark钻石-负责门店管理，活动方案策划，大型精品展/VIP活动策划。 成绩：年均复合增长达45% 。
3、营销策划：
-门店爆点营销：根据不同地域的门店进行线上/线下营销活动、大型落地活动策划，打造不同地域特色的爆点营销。成绩：年度ROI大于400% 。
-节假日营销：重大节日和月度营销活动策划，激活会员，带动门店销售，传递品牌理念。
总结：擅长营销策划、数据分析、产品文案、项目管理等，具有良好的全局观，能有条不紊地推动项目持续增长。同时，擅长创新营销方式，并通局部实验提供可供复制和大面积推广的方案。
时间：20xx.8-20xx.4   公司名称：幻主简历公司2   职位名称：市场策划主管   
负责异业合作方案策划
负责对外培训活动
负责各类宣传册制作
因公司业务转变，故离职。
时间：20xx.5-至今   公司名称：幻主简历公司3   职位名称：宣传策划经理   
1、建立并运营网络推广渠道：微信、官网、知乎、今日头条、微博等自媒体平台。自媒体每月曝光量达3w+，官网收录量从0到30/月。
2、创新内容：行业内尚没有杰出先例，率先建立用户之间的沟通、互动，增加用户的粘性。2018年上半年客户转化率已达标。
3、竞品/客户/政策分析：独立分析竞品的产品、市场动态，寻找竞我双方的异同点，为市场、产品创造机会；分析客户动态，寻求潜在客户，为市场扩展提供机会；搜集行业相关政策信息，为产品的延申提供支撑点。
4、负责媒体联络，与媒体保持良好的关系，负责各类新闻活动策划。建立以客户为中心的营销模式，用客户营销辅助企业自身营销，扩大企业的影响力。
5、负责企业各类宣传资料规划制作。
6、负责各类展销活动策划。
总结: 1、 首创行业先例的营销模式，增加客户的信任，与客户建立良好的互动 2、 擅长新闻活动策划，建立线上快速的传播渠道 3、 根据品牌和产品特征进行品牌创意和推广
自我评价
职业评价:7年市场营销与品牌营销经验，精通产品文案撰写，活动策划（线上与线下），新闻策划，项目管理；熟悉各类报表及数据分析；同时负责过对外合作，具有优秀的谈判技巧与沟通能力；热爱时尚流行事物，具有良好的创意，并进行执行，所负责项目获得不菲成绩。		
"""

example_text_4_electric_engineer = """
电气工程师个人简历 篇1：
求职意向
求职类型：全职
意向岗位：电气工程师
意向城市：广东广州
薪资要求：12000-18000元/月（根据具体工作内容和公司福利可面议）
求职状态：随时到岗
教育背景
时间：20xx.9-20xx.6
学校名称：幻主简历大学
专业名称：电气工程及其自动化（本科）
学术成绩：在校期间，GPA保持3.8/4.0，专业排名前10%，多次获得校级学术奖学金。
学术奖学金：20xx-20xx学年，荣获“优秀学生奖学金”一等奖；20xx-20xx学年，荣获“科技创新奖学金”。
校内活动和荣誉：积极参与学校组织的各项活动，如“电气工程创新设计大赛”，并荣获一等奖；担任电气工程系学生会宣传部部长，组织策划多场校园活动，获得师生一致好评。
学校描述：主修课程包括电路理论、电机学、PLC原理及应用、继电保护、高压电技术、电力系统分析、电力拖动、电力电子技术等，通过系统学习，打下了坚实的理论基础。
工作经验
时间：20xx.3-至今
公司名称：幻主简历工作经验案例（1）
职位名称：电力设计师
工作内容及成果：
- 配合供电公司对现场进行详尽勘测，出具初步施工图纸，确保设计符合实际需求。期间，共参与并完成50余项勘测任务，图纸准确率高达98%。
- 结合甲方要求和现场施工过程中的具体问题，灵活调整图纸设计，有效解决了20余次现场突发问题，确保了施工进度和质量。
- 通过优化设计方案，为公司节省了约10%的工程造价成本。
时间：20xx.4-20xx.8
"""