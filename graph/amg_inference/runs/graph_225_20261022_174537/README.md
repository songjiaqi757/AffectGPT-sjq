# 图增强续训后的自动推理
全部操作、模型、缓存、日志和结果均在本服务器。

训练队列：GPU 0 = from_30 → from_40 → from_50；GPU 1 = from_35 → from_45。
各5轮、全部保存，共25个新checkpoint，乘9个固定官方测试分区，共225个逻辑任务、319975条样本预测。
九个集合共12799条原始测试输入；标签仅由受限NumPy读取器提取官方成员名称，不进入模型、Cue、图查询或参数选择。
查询沿用仅3076源域验证集选定的冻结配置，不用目标集选择权重、参数或提示。

独立服务器监督进程等待各卡训练队列完整成功，并获得与训练相同的GPU排他锁。
首张空闲卡先生成一次可复用的原生单记录Cue/图缓存；每卡正式推理前各做3进程同时满窗口的源域生成显存探针。
显存探针要求1530–1536输入token及1200实际输出token；探针失败会暂停该卡推理并留下failed状态。
每卡最多3个持久推理进程；两张卡均空闲后最多6个。GPU 1无需等待GPU 0全部训练完，可以处理已经发布的权重。
任务只能消费训练器原子发布的checkpoints.json中路径与SHA256，校验续训来源，独占任务锁，逐样本落盘，崩溃后续跑且最多3次尝试。
输入为原始8个人脸帧、8段音频、字幕和与训练相同的冻结图证据格式。
零样本开放词表问题及生成参数沿用原版（sampling=true, top_p=.9, temperature=1, beam=1, max_new_tokens=1200）。
输入上限1536，窗口2736，防止旧窗口2000左裁剪多模态占位符。逐样本seed由固定42、权重SHA和样本ID确定。
本次只自动生成预测，不自动按目标标签打分或挑选最优权重。

观察 controller_status.json、gpu_0_status.json、gpu_1_status.json、cache_status.json 和 jobs/*.json。
最终每个任务目录 predictions/<job_id>/ 含可恢复样本JSON、predictions.jsonl及兼容原版的name2reason.npz。
容量实测尚未执行：当前两卡仍在训练，调度器只等待，不提前分配GPU显存。

## 四路执行覆盖（2026-10-23）
用户已授权每卡四路。原三路监督器和已生成结果保留；独立 fourth_lane.py 监督每卡slot 3。GPU1四路共存容量测试通过，GPU0训练完成、原三路就绪后再自动接入第四路。实际并发以 parallelism_override.json、fourth_lane_controller_status.json、gpu_*_fourth_lane_status.json 为准；原plan及主监督器中的3为历史基础通道数。四路测试报告：gpu_1_four_lane_capacity.json；短窗口吞吐记录：four_lane_throughput_observation.json。
