# 本轮逐样本对照

固定名称排序，每个数据集/对照/改善或变差方向最多取2例；共175个对照条目、114个dataset/name案例。是探索性阅读池，不代表错误类型频率。
评分变化和人类语义判断分开：HIT/OV映射可能因近义词变化而涨跌；当前附录未重新听看全量音视频。

## 1. MER2023 / sample_00000649 / A-P / improved

参考：happy
字幕：I can't accompany you, I have to stay at home to read. This is the homework assigned by Brother Wei, and I have to finish it today.
中文：我不能陪你去，我得在家看书，这是魏兄布置的功课，今天看完了。
P：The character's emotional state is frustrated, annoyed, resigned, calm, composed, apathetic, lack of enthusiasm.
A：The character's emotional state is frustrated, annoyed, resigned, calm, composed, focused, concentrated, happy, joyful.
诊断质量（并非官方分数贡献）：P=0.6，A=1.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: negation present; text: desire need; text: explicit causal attribution other; audio: speech rate rel slow; audio: vocal intensity rel low; audio: pitch variability low; audio: pause long; audio: intonation falling; audio: intonation flat; visual: brows raised; visual: eyes widened; visual: head lowered | Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high; coping potential: acp low

## 2. MER2023 / sample_00000848 / A-P / improved

参考：happy
字幕：Who else could it be? You are my only idol.
中文：那还能有谁呀？你可是我唯一的偶像呢。
P：The character's emotional state is teasing, humorous, positive.
A：The character's emotional state is happy, affectionate, admiration.
诊断质量（并非官方分数贡献）：P=0.8，A=1.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation positive; text: negation present; text: intensifier present; text: rhetorical question; audio: speech rate rel slow; audio: pitch variability high; audio: intonation rising; visual: brows raised; visual: eyes widened; visual: smile present | Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low | Emotion hypotheses: joy, hopeful, appreciated | Supporting links: visual: smile present -> joy; text: evaluation positive -> appreciated

## 3. MER2023 / sample_00000929 / A-P / worsened

参考：angry
字幕：Cao, Cao Xiaoqiang is wishful thinking.
中文：曹，曹小强他是一厢情愿的。
P：The character's emotional state is mockery, sarcasm, doubt, disbelief, anxiety, excitement.
A：The character's emotional state is frustration, disappointment, sarcasm, mockery, anxiety, excitement.
诊断质量（并非官方分数贡献）：P=1.0，A=0.8
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: desire need; audio: pitch variability high; audio: intonation rising; visual: brows raised; visual: eyes widened | Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

## 4. MER2023 / sample_00001047 / A-P / worsened

参考：happy
字幕：Look here, Saturday.
中文：你看这儿，礼拜六。
P：The character's emotional state is excited, anticipatory, happy, joyful.
A：The character's emotional state is excited, anticipating, positive.
诊断质量（并非官方分数贡献）：P=1.0，A=0.8
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: audio: intonation rising; visual: eyes squinted; visual: smile present; visual: head lowered | Appraisal hypotheses: goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag other; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low | Emotion hypotheses: joy, hopeful, content | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 5. MER2023 / sample_00000436 / C-B / improved

参考：sad
字幕：When he says I'm annoying, I really want to cry.
中文：他说我很烦的时候，我就很想哭。
B：The character's emotional state is annoyance, frustration, dissatisfaction, distress.
C：The character's emotional state is frustrated, annoyed, sad.
诊断质量（并非官方分数贡献）：B=0.6，C=1.0
新增证据：Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high
移除证据：无

## 6. MER2023 / sample_00000929 / C-B / improved

参考：angry
字幕：Cao, Cao Xiaoqiang is wishful thinking.
中文：曹，曹小强他是一厢情愿的。
B：The character's emotional state is frustration, disappointment, sarcasm, mockery, fear, anxiety.
C：The character's emotional state is mockery, sarcasm, doubt, disbelief, anxiety, excitement.
诊断质量（并非官方分数贡献）：B=0.8，C=1.0
新增证据：Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low
移除证据：无

## 7. MER2023 / sample_00000637 / C-B / worsened

参考：angry
字幕：I said I don't have time.
中文：我说我没空。
B：The character's emotional state is anxiety, defeat, distress, pressure.
C：The character's emotional state is anxiety, defeat.
诊断质量（并非官方分数贡献）：B=0.4，C=0.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low
移除证据：无

## 8. MER2023 / sample_00002066 / C-B / worsened

参考：angry
字幕：This wine, you don't drink it, watermelon juice, you don't drink that either, what do you want to do then?
中文：这酒，酒不喝，西瓜汁，西瓜汁不喝，你要干什么呀？
B：The character's emotional state is anxiety, gloom, impatience, dissatisfaction, frustration.
C：The character's emotional state is anxiety, gloom, impatience, dissatisfaction, disappointment.
诊断质量（并非官方分数贡献）：B=0.4，C=0.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low
移除证据：无

## 9. MER2023 / sample_00002034 / E-C / improved

参考：happy
字幕：Haven't I said it all? I will bring you the coffee when the time comes.
中文：我不都说了吗？咖啡到时候我给你送过去。
C：The character's emotional state is confidence, commitment.
E：The character's emotional state is confidence, commitment, positive mood, frustration, annoyance, excitement, urgency.
诊断质量（并非官方分数贡献）：C=0.6，E=0.8
新增证据：Emotion hypotheses: joy, disappointed, hopeful
移除证据：无

## 10. MER2023 / sample_00005399 / E-C / improved

参考：surprise
字幕：Huh
中文：啊
C：The character's emotional state is neutral.
E：The character's emotional state is disagreement, confusion.
诊断质量（并非官方分数贡献）：C=0.0，E=0.5
新增证据：Emotion hypotheses: anxious, care, fear
移除证据：无

## 11. MER2023 / sample_00002203 / E-C / worsened

参考：happy
字幕：Huh
中文：啊
C：The character's emotional state is excited, anticipating, satisfied, happy, relaxed.
E：The character's emotional state is excited, anticipating, positive.
诊断质量（并非官方分数贡献）：C=1.0，E=0.8
新增证据：Emotion hypotheses: joy, hopeful, manic
移除证据：无

## 12. MER2023 / sample_00003601 / E-C / worsened

参考：surprise
字幕：What are you doing there?
中文：你在那干嘛呢？
C：The character's emotional state is questioning, dissatisfaction, misunderstanding, anxiety, stress, overwhelm.
E：The character's emotional state is discontent, worry, questioning, dissatisfaction.
诊断质量（并非官方分数贡献）：C=0.5，E=0.25
新增证据：Emotion hypotheses: care, anxious, apathetic
移除证据：无

## 13. MER2023 / sample_00001047 / P-E / improved

参考：happy
字幕：Look here, Saturday.
中文：你看这儿，礼拜六。
E：The character's emotional state is excited, anticipating, positive.
P：The character's emotional state is excited, anticipatory, happy, joyful.
诊断质量（并非官方分数贡献）：E=0.8，P=1.0
新增证据：Supporting links: visual: smile present -> joy; visual: smile present -> hopeful
移除证据：无

## 14. MER2023 / sample_00002161 / P-E / improved

参考：happy
字幕：However, it seems that this time, it includes performing "The Beautiful Contract".
中文：但是好像这次，包括演《美丽的契约》
E：The character's emotional state is excitement, surprise.
P：The character's emotional state is excited, content.
诊断质量（并非官方分数贡献）：E=0.4，P=0.6
新增证据：Supporting links: visual: smile present -> joy; visual: smile present -> hopeful
移除证据：无

## 15. MER2023 / sample_00001227 / P-E / worsened

参考：happy
字幕：Is everything okay at home?
中文：家里还好吧？
E：The character's emotional state is concern, inquiry, happiness, relaxation.
P：The character's emotional state is concern, worry, care, positive.
诊断质量（并非官方分数贡献）：E=1.0，P=0.8
新增证据：Supporting links: visual: smile present -> joy; visual: smile present -> hopeful
移除证据：无

## 16. MER2023 / sample_00001638 / P-E / worsened

参考：happy
字幕：You don't have to figure it out, isn't it enough that I can come to see you?
中文：您不用弄明白喽，我能来看您不就行了吗？
E：The character's emotional state is excitement, enthusiasm, frustration, annoyance, happiness, relaxation.
P：The character's emotional state is excitement, enthusiasm, frustration, annoyance, dissatisfaction, frustration.
诊断质量（并非官方分数贡献）：E=1.0，P=0.4
新增证据：Supporting links: text: rhetorical question -> disappointed; text: rhetorical question -> anger
移除证据：无

## 17. MER2023 / sample_00001227 / C-P / improved

参考：happy
字幕：Is everything okay at home?
中文：家里还好吧？
P：The character's emotional state is concern, worry, care, positive.
C：The character's emotional state is concern, inquiry, happiness, relaxation.
诊断质量（并非官方分数贡献）：P=0.8，C=1.0
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, manic | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 18. MER2023 / sample_00001638 / C-P / improved

参考：happy
字幕：You don't have to figure it out, isn't it enough that I can come to see you?
中文：您不用弄明白喽，我能来看您不就行了吗？
P：The character's emotional state is excitement, enthusiasm, frustration, annoyance, dissatisfaction, frustration.
C：The character's emotional state is excitement, enthusiasm, frustration, annoyance, happiness, relaxation.
诊断质量（并非官方分数贡献）：P=0.4，C=1.0
新增证据：无
移除证据：Emotion hypotheses: disappointed, anger, bewildered | Supporting links: text: rhetorical question -> disappointed; text: rhetorical question -> anger

## 19. MER2023 / sample_00001047 / C-P / worsened

参考：happy
字幕：Look here, Saturday.
中文：你看这儿，礼拜六。
P：The character's emotional state is excited, anticipatory, happy, joyful.
C：The character's emotional state is excited, anticipating, positive.
诊断质量（并非官方分数贡献）：P=1.0，C=0.8
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, content | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 20. MER2023 / sample_00002161 / C-P / worsened

参考：happy
字幕：However, it seems that this time, it includes performing "The Beautiful Contract".
中文：但是好像这次，包括演《美丽的契约》
P：The character's emotional state is excited, content.
C：The character's emotional state is excitement, surprise.
诊断质量（并非官方分数贡献）：P=0.6，C=0.4
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, hesitant | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 21. MER2024 / sample_00000792 / A-P / improved

参考：happy
字幕：我：开那个小王，挺好的，要不，你就考虑？
中文：我：开那个小王，挺好的，要不，你就考虑？
P：The character's emotional state is positive, anxious, tense.
A：The character's emotional state is positive, hopeful, interested, participatory.
诊断质量（并非官方分数贡献）：P=0.8，A=1.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation positive; text: intensifier present; audio: pitch variability low; audio: intonation rising; visual: brows raised; visual: eyes widened; visual: smile present | Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag other; certainty: act certain; certainty: act uncertain; coping potential: acp high

## 22. MER2024 / sample_00001041 / A-P / improved

参考：surprise
字幕：韩国，又分手了。
中文：韩国，又分手了。
P：The character's emotional state is disappointment, frustration, sadness.
A：The character's emotional state is disappointment, frustration, anxiety, nervousness, irritability, anger.
诊断质量（并非官方分数贡献）：P=0.0，A=0.25
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation negative; text: explicit failure loss outcome; audio: pitch level rel high; audio: pitch variability high; audio: intonation rising; visual: brows furrowed; visual: brows raised; visual: eyes widened; visual: grimace present | Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

## 23. MER2024 / sample_00000655 / A-P / worsened

参考：happy
字幕：你太牛了，你居然会。
中文：你太牛了，你居然会。
P：The character's emotional state is admiration, surprise, excitement, passion.
A：The character's emotional state is admiration, surprise, positive.
诊断质量（并非官方分数贡献）：P=1.0，A=0.4
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation positive; text: intensifier present; audio: pitch variability high; audio: intonation rising; audio: voice tense; visual: brows raised; visual: eyes widened; visual: smile present | Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

## 24. MER2024 / sample_00000954 / A-P / worsened

参考：surprise
字幕：不，你怎么不敲门？哪？
中文：不，你怎么不敲门？哪？
P：The character's emotional state is anger, dissatisfaction, anxiety.
A：The character's emotional state is anger, dissatisfaction, blame, disappointment.
诊断质量（并非官方分数贡献）：P=0.25，A=0.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: negation present; text: rhetorical question; audio: pitch variability high; audio: intonation rising; visual: brows furrowed; visual: eyes widened; visual: mouth corners down | Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; agency: aag other; certainty: act uncertain; coping potential: acp low; coping potential: acp high

## 25. MER2024 / sample_00001635 / C-B / improved

参考：surprise
字幕：我：不。
中文：我：不。
B：The character's emotional state is anxious, angry, frustrated.
C：The character's emotional state is perplexed, dissatisfied, uncertain.
诊断质量（并非官方分数贡献）：B=0.25，C=0.75
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high
移除证据：无

## 26. MER2024 / sample_00002085 / C-B / improved

参考：sad
字幕：不过，孩子，这，这下可好了，全部都来。
中文：不过，孩子，这，这下可好了，全部都来。
B：The character's emotional state is surprise, confusion, relief, concern.
C：The character's emotional state is distress, sorrow, anxiety, confusion, surprise, relief.
诊断质量（并非官方分数贡献）：B=0.2，C=1.0
新增证据：Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag other; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high
移除证据：无

## 27. MER2024 / sample_00001041 / C-B / worsened

参考：surprise
字幕：韩国，又分手了。
中文：韩国，又分手了。
B：The character's emotional state is disappointment, frustration, anger, irritability, anxiety, stress, overwhelm.
C：The character's emotional state is disappointment, frustration, sadness.
诊断质量（并非官方分数贡献）：B=0.5，C=0.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high
移除证据：无

## 28. MER2024 / sample_00002357 / C-B / worsened

参考：worried
字幕：问苏梅，苏梅说：跟你们说，有什么差吗？再说啊，你们已经来了，就说出来了。
中文：问苏梅，苏梅说：跟你们说，有什么差吗？再说啊，你们已经来了，就说出来了。
B：The character's emotional state is impatience, resignation, confusion, anxiety.
C：The character's emotional state is irritated, impatient, uncertain, pressured.
诊断质量（并非官方分数贡献）：B=1.0，C=0.6
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high
移除证据：无

## 29. MER2024 / sample_00003676 / E-C / improved

参考：happy
字幕：毛医生。
中文：毛医生。
C：The character's emotional state is positive, surprise, excitement.
E：The character's emotional state is positive, happy, excited.
诊断质量（并非官方分数贡献）：C=0.8，E=1.0
新增证据：Emotion hypotheses: joy, hopeful, content
移除证据：无

## 30. MER2024 / sample_00006922 / E-C / improved

参考：worried
字幕：是，说得也是，可是，现在这钱的问题，它不是没法解决吗？那也不能让邹一栋他妈就这么一。
中文：是，说得也是，可是，现在这钱的问题，它不是没法解决吗？那也不能让邹一栋他妈就这么一。
C：The character's emotional state is depression, disappointment, anger.
E：The character's emotional state is depression, disappointment, anxiety, tension.
诊断质量（并非官方分数贡献）：C=0.4，E=1.0
新增证据：Emotion hypotheses: disappointed, anger, depressed
移除证据：无

## 31. MER2024 / sample_00002554 / E-C / worsened

参考：happy
字幕：当然啊，大家都这么叫我啊。
中文：当然啊，大家都这么叫我啊。
C：The character's emotional state is humorous, self-deprecating, happy, relaxed.
E：The character's emotional state is humorous, self-deprecating, positive, lighthearted.
诊断质量（并非官方分数贡献）：C=1.0，E=0.8
新增证据：Emotion hypotheses: joy, hopeful, manic
移除证据：无

## 32. MER2024 / sample_00003004 / E-C / worsened

参考：worried
字幕：两个小时才能出，你可要想清楚，这期间，如果出。现。任。
中文：两个小时才能出，你可要想清楚，这期间，如果出。现。任。
C：The character's emotional state is serious, pressured, tense, anxious.
E：The character's emotional state is serious, pressured, urgent, warning, caution.
诊断质量（并非官方分数贡献）：C=1.0，E=0.2
新增证据：Emotion hypotheses: disappointed, anger, depressed
移除证据：无

## 33. MER2024 / sample_00003004 / P-E / improved

参考：worried
字幕：两个小时才能出，你可要想清楚，这期间，如果出。现。任。
中文：两个小时才能出，你可要想清楚，这期间，如果出。现。任。
E：The character's emotional state is serious, pressured, urgent, warning, caution.
P：The character's emotional state is serious, pressured, tense, anxious.
诊断质量（并非官方分数贡献）：E=0.2，P=1.0
新增证据：Supporting links: visual: brows furrowed -> anger; visual: brows furrowed -> disappointed
移除证据：无

## 34. MER2024 / samplenew_00003238 / P-E / improved

参考：happy
字幕：哼，说得也是。
中文：哼，说得也是。
E：The character's emotional state is dissatisfaction, disagreement, acknowledgment.
P：The character's emotional state is dissatisfaction, disagreement, acknowledgment, acceptance, happiness, excitement.
诊断质量（并非官方分数贡献）：E=0.8，P=1.0
新增证据：Supporting links: visual: mouth corners down -> disappointed; visual: brows furrowed -> anger
移除证据：无

## 35. MER2024 / sample_00003669 / P-E / worsened

参考：worried
字幕：当然，你李叔，他不会。
中文：当然，你李叔，他不会。
E：The character's emotional state is understanding, sympathy, stress, frustration.
P：The character's emotional state is neutral.
诊断质量（并非官方分数贡献）：E=0.6，P=0.0
新增证据：Supporting links: visual: grimace present -> anger; visual: mouth corners down -> disappointed
移除证据：无

## 36. MER2024 / sample_00003676 / P-E / worsened

参考：happy
字幕：毛医生。
中文：毛医生。
E：The character's emotional state is positive, happy, excited.
P：The character's emotional state is positive, surprise, excitement.
诊断质量（并非官方分数贡献）：E=1.0，P=0.8
新增证据：Supporting links: visual: smile present -> joy; visual: smile present -> hopeful
移除证据：无

## 37. MER2024 / sample_00002554 / C-P / improved

参考：happy
字幕：当然啊，大家都这么叫我啊。
中文：当然啊，大家都这么叫我啊。
P：The character's emotional state is humorous, self-deprecating, positive, lighthearted.
C：The character's emotional state is humorous, self-deprecating, happy, relaxed.
诊断质量（并非官方分数贡献）：P=0.8，C=1.0
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, manic | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 38. MER2024 / sample_00003206 / C-P / improved

参考：happy
字幕：我被放鸽子了。
中文：我被放鸽子了。
P：The character's emotional state is anxious, tense, let down, disappointed, confused, uncomfortable.
C：The character's emotional state is anxiety, tension, let down, disappointment, dissatisfaction, anger, confidence, determination, humor.
诊断质量（并非官方分数贡献）：P=0.0，C=0.6
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, content | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 39. MER2024 / samplenew_00003238 / C-P / worsened

参考：happy
字幕：哼，说得也是。
中文：哼，说得也是。
P：The character's emotional state is dissatisfaction, disagreement, acknowledgment, acceptance, happiness, excitement.
C：The character's emotional state is dissatisfaction, disagreement, acknowledgment.
诊断质量（并非官方分数贡献）：P=1.0，C=0.8
新增证据：无
移除证据：Emotion hypotheses: disappointed, anger, despair | Supporting links: visual: mouth corners down -> disappointed; visual: brows furrowed -> anger

## 40. MER2024 / samplenew_00003374 / C-P / worsened

参考：happy
字幕：那，你忙你的吧，我赶紧走了。
中文：那，你忙你的吧，我赶紧走了。
P：The character's emotional state is anxiety, agitation, frustration, impatience, surprise, excitement, enjoyment.
C：The character's emotional state is anxiety, stress, urgency, discomfort, desire to leave.
诊断质量（并非官方分数贡献）：P=0.4，C=0.0
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, manic | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 41. MELD / test_dia100_utt14 / A-P / improved

参考：fear
字幕：Why are there only two of you?
中文：为什么只有两个你们？
P：The character's emotional state is anxious, tense, overwhelmed, dissatisfied, perplexed.
A：The character's emotional state is anxious, tense, excited, fast-paced.
诊断质量（并非官方分数贡献）：P=0.2，A=1.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: rhetorical question; audio: intonation rising; visual: brows raised; visual: eyes widened; visual: head lowered | Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

## 42. MELD / test_dia100_utt15 / A-P / improved

参考：fear
字幕：Where is Leslie?
中文：莱斯利在哪里？
P：The character's emotional state is happiness, surprise.
A：The character's emotional state is happiness, excitement, frustration, annoyance, playful, joking, affectionate.
诊断质量（并非官方分数贡献）：P=0.4，A=0.8
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: audio: intonation rising; visual: brows raised; visual: eyes widened; visual: head lowered | Appraisal hypotheses: goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low | Emotion hypotheses: joy, trusting, manic | Supporting links: visual: brows raised -> joy; visual: brows raised -> manic

## 43. MELD / test_dia100_utt10 / A-P / worsened

参考：sadness
字幕：I broke it.
中文：我弄坏了它。
P：The character's emotional state is disappointment, resignation, humor, playfulness.
A：The character's emotional state is calm, normal.
诊断质量（并非官方分数贡献）：P=0.6，A=0.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation negative; text: explicit causal attribution self; audio: pitch level rel high; audio: pitch variability high; audio: intonation rising; visual: head lowered | Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag other; certainty: act uncertain; certainty: act certain; coping potential: acp low | Emotion hypotheses: ashamed, anger, disappointed | Supporting links: text: explicit causal attribution self -> ashamed; text: evaluation negative -> disappointed

## 44. MELD / test_dia102_utt7 / A-P / worsened

参考：sadness
字幕：Well, maybe it won't work out. Maybe Ross won't like her personality.
中文：嗯，也许事情不会成功。也许罗斯不会喜欢她的个性。
P：The character's emotional state is concern, uncertainty, anxiety, tension, stress, overwhelm.
A：The character's emotional state is concern, negative emotion, worry.
诊断质量（并非官方分数贡献）：P=0.2，A=0.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: affect word negative; text: evaluation negative; text: negation present; text: uncertainty hedge; text: exclamation interjection; text: explicit failure loss outcome; audio: speech rate rel fast; audio: pitch level rel high; audio: pitch variability high; audio: intonation rising; audio: voice tense; visual: brows furrowed; visual: eyes widened; visual: mouth corners down | Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

## 45. MELD / test_dia102_utt7 / C-B / improved

参考：sadness
字幕：Well, maybe it won't work out. Maybe Ross won't like her personality.
中文：嗯，也许事情不会成功。也许罗斯不会喜欢她的个性。
B：The character's emotional state is concern, uncertainty, anxiety.
C：The character's emotional state is concern, uncertainty, anxiety, tension, stress, overwhelm.
诊断质量（并非官方分数贡献）：B=0.0，C=0.2
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high
移除证据：无

## 46. MELD / test_dia106_utt2 / C-B / improved

参考：disgust
字幕：Then why are you smoking?
中文：那你为什么在抽烟？
B：The character's emotional state is frustrated, angry, anxiety.
C：The character's emotional state is frustrated, angry, critical, questioning.
诊断质量（并非官方分数贡献）：B=0.0，C=0.6666666666666666
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low
移除证据：无

## 47. MELD / test_dia100_utt14 / C-B / worsened

参考：fear
字幕：Why are there only two of you?
中文：为什么只有两个你们？
B：The character's emotional state is anxious, tense, excited, fast-paced.
C：The character's emotional state is anxious, tense, overwhelmed, dissatisfied, perplexed.
诊断质量（并非官方分数贡献）：B=1.0，C=0.2
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low
移除证据：无

## 48. MELD / test_dia102_utt0 / C-B / worsened

参考：anger
字幕：You said she was bald.
中文：你说她是秃头。
B：The character's emotional state is confused, dissatisfied, critical, negative.
C：The character's emotional state is confused, dissatisfied, anxious, tense.
诊断质量（并非官方分数贡献）：B=0.6，C=0.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high
移除证据：无

## 49. MELD / test_dia102_utt6 / E-C / improved

参考：anger
字幕：Yeah, I said what was okay when I thought she was some weird bald chick. I mean, y'know, that girl has hair got
中文：是的，当我以为她是一个奇怪的秃头女孩时，我说了什么是可以的。我的意思是，你知道的，那个女孩有头发。
C：The character's emotional state is surprise, disbelief, mockery, laughter, negative assessment, sarcasm.
E：The character's emotional state is discontent, anger, unhappiness.
诊断质量（并非官方分数贡献）：C=0.6，E=1.0
新增证据：Emotion hypotheses: anger, disappointed, hesitant
移除证据：无

## 50. MELD / test_dia108_utt9 / E-C / improved

参考：joy
字幕：Aw, all right take this bed, you can make other friends.
中文：好的，拿这张床吧，你可以交其他朋友。
C：The character's emotional state is disappointed, resigned, frustrated, excited, enthusiastic, surprised, pleased.
E：The character's emotional state is disappointed, frustrated, anxious, excited, enthusiastic, supportive, encouraging.
诊断质量（并非官方分数贡献）：C=0.6，E=1.0
新增证据：Emotion hypotheses: joy, hopeful, manic
移除证据：无

## 51. MELD / test_dia112_utt13 / E-C / worsened

参考：surprise
字幕：What?
中文：什么？
C：The character's emotional state is confused, misunderstand, curious, engaged.
E：The character's emotional state is curious, teasing, positive.
诊断质量（并非官方分数贡献）：C=0.75，E=0.0
新增证据：Emotion hypotheses: joy, hopeful, content
移除证据：无

## 52. MELD / test_dia120_utt0 / E-C / worsened

参考：joy
字幕：Sure!
中文：当然！
C：The character's emotional state is excited, enthusiastic, positive, agreement.
E：The character's emotional state is excited, enthusiastic, positive, confident.
诊断质量（并非官方分数贡献）：C=1.0，E=0.8
新增证据：Emotion hypotheses: joy, hopeful, content
移除证据：无

## 53. MELD / test_dia105_utt0 / P-E / improved

参考：anger
字幕：Ow! My ass. Okay. Okay.  Oh, shhh!
中文：哎呀！我的屁股。好的。好的。哦，嘘！
E：The character's emotional state is pain, frustration, excitement, frustration, relaxation, comfort.
P：The character's emotional state is pain, discomfort, excitement, frustration, anger, calmness, satisfaction.
诊断质量（并非官方分数贡献）：E=0.4，P=1.0
新增证据：Supporting links: audio: vocal intensity rel high -> anger; audio: pitch variability high -> anger
移除证据：无

## 54. MELD / test_dia105_utt1 / P-E / improved

参考：fear
字幕：No! No!! It's me! It's me! I-I didn't want to make any noise!
中文：不！不！！是我！是我！我-我不想制造任何噪音！
E：The character's emotional state is frustrated, angry, desperate, defensive.
P：The character's emotional state is frustrated, angry, anxious, tense.
诊断质量（并非官方分数贡献）：E=0.0，P=0.2
新增证据：Supporting links: audio: voice tense -> anger; audio: vocal intensity rel high -> anger
移除证据：无

## 55. MELD / test_dia102_utt6 / P-E / worsened

参考：anger
字幕：Yeah, I said what was okay when I thought she was some weird bald chick. I mean, y'know, that girl has hair got
中文：是的，当我以为她是一个奇怪的秃头女孩时，我说了什么是可以的。我的意思是，你知道的，那个女孩有头发。
E：The character's emotional state is discontent, anger, unhappiness.
P：The character's emotional state is surprise, disbelief, mockery, laughter, negative assessment, sarcasm.
诊断质量（并非官方分数贡献）：E=1.0，P=0.6
新增证据：Supporting links: text: evaluation negative -> disappointed; text: evaluation negative -> anger
移除证据：无

## 56. MELD / test_dia107_utt6 / P-E / worsened

参考：sadness
字幕：You remember not having sex in high school, right?
中文：你还记得在高中时没有发生性行为，对吗？
E：The character's emotional state is relaxed, comfortable, anxious, frustrated, angry.
P：The character's emotional state is relaxed, humorous, playful.
诊断质量（并非官方分数贡献）：E=0.6，P=0.0
新增证据：Supporting links: text: rhetorical question -> disappointed; text: rhetorical question -> anger
移除证据：无

## 57. MELD / test_dia107_utt6 / C-P / improved

参考：sadness
字幕：You remember not having sex in high school, right?
中文：你还记得在高中时没有发生性行为，对吗？
P：The character's emotional state is relaxed, humorous, playful.
C：The character's emotional state is relaxed, comfortable, anxious, frustrated, angry, playful, humorous.
诊断质量（并非官方分数贡献）：P=0.0，C=0.6
新增证据：无
移除证据：Emotion hypotheses: disappointed, anger, bewildered | Supporting links: text: rhetorical question -> disappointed; text: rhetorical question -> anger

## 58. MELD / test_dia113_utt4 / C-P / improved

参考：fear
字幕：No-no! Don't do it! Don't!
中文：不不！不要做！不要！
P：The character's emotional state is tense, anxious, uneasy, possibly fearful.
C：The character's emotional state is tense, anxious, uneasy, possibly fear.
诊断质量（并非官方分数贡献）：P=0.2，C=1.0
新增证据：无
移除证据：Emotion hypotheses: anger, disappointed, anxious | Supporting links: text: evaluation negative -> disappointed; text: evaluation negative -> anger

## 59. MELD / test_dia105_utt0 / C-P / worsened

参考：anger
字幕：Ow! My ass. Okay. Okay.  Oh, shhh!
中文：哎呀！我的屁股。好的。好的。哦，嘘！
P：The character's emotional state is pain, discomfort, excitement, frustration, anger, calmness, satisfaction.
C：The character's emotional state is pain, frustration, excitement, frustration, relaxation, comfort.
诊断质量（并非官方分数贡献）：P=1.0，C=0.4
新增证据：无
移除证据：Emotion hypotheses: anger, disappointed, bewildered | Supporting links: audio: vocal intensity rel high -> anger; audio: pitch variability high -> anger

## 60. MELD / test_dia105_utt1 / C-P / worsened

参考：fear
字幕：No! No!! It's me! It's me! I-I didn't want to make any noise!
中文：不！不！！是我！是我！我-我不想制造任何噪音！
P：The character's emotional state is frustrated, angry, anxious, tense.
C：The character's emotional state is anger, frustration, dissatisfaction, protest.
诊断质量（并非官方分数贡献）：P=0.2，C=0.0
新增证据：无
移除证据：Emotion hypotheses: anger, disappointed, bewildered | Supporting links: audio: voice tense -> anger; audio: vocal intensity rel high -> anger

## 61. IEMOCAPFour / Ses05F_impro01_F018 / A-P / improved

参考：anger
字幕：Why not?
中文：为什么不呢？
P：The character's emotional state is excited, passionate.
A：The character's emotional state is excited, frustrated, passionate, positive, curious.
诊断质量（并非官方分数贡献）：P=0.0，A=0.4
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: negation present; text: rhetorical question; audio: intonation rising; visual: brows raised; visual: eyes widened | Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

## 62. IEMOCAPFour / Ses05F_impro02_F004 / A-P / improved

参考：sad
字幕：I got a call today,
中文：我今天接到了一个电话，
P：The character's emotional state is neutral, tense, anxious.
A：The character's emotional state is neutral, detached.
诊断质量（并非官方分数贡献）：P=0.0，A=0.4
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: audio: intonation rising; visual: eyes squinted; visual: lips pressed | Appraisal hypotheses: expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

## 63. IEMOCAPFour / Ses05F_impro02_F009 / A-P / worsened

参考：sad
字幕：I know.  I know.
中文：我知道。我知道。
P：The character's emotional state is comfort, support, sadness, distress.
A：The character's emotional state is comfort, support, distress, emotional vulnerability.
诊断质量（并非官方分数贡献）：P=1.0，A=0.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: audio: speech rate rel slow; audio: pitch level rel low; audio: vocal intensity rel low; audio: pitch variability high; audio: pause long; audio: intonation falling; audio: voice tense; audio: voice trembling; audio: crying sobbing present; visual: eyes squinted; visual: lips pressed | Appraisal hypotheses: goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

## 64. IEMOCAPFour / Ses05F_impro03_F035 / A-P / worsened

参考：happy
字幕：Thank you.
中文：谢谢你。
P：The character's emotional state is thankful, happy, content.
A：The character's emotional state is gratitude, relief, comfort, support.
诊断质量（并非官方分数贡献）：P=1.0，A=0.4
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation positive; audio: intonation rising; visual: brows raised; visual: eyes squinted; visual: smile present | Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag other; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low | Emotion hypotheses: joy, hopeful, appreciated | Supporting links: visual: smile present -> joy; text: evaluation positive -> appreciated

## 65. IEMOCAPFour / Ses05F_impro02_F009 / C-B / improved

参考：sad
字幕：I know.  I know.
中文：我知道。我知道。
B：The character's emotional state is comfort, support, distress, emotional vulnerability.
C：The character's emotional state is comfort, support, sadness, distress.
诊断质量（并非官方分数贡献）：B=0.0，C=1.0
新增证据：Appraisal hypotheses: goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high
移除证据：无

## 66. IEMOCAPFour / Ses05F_impro02_F027 / C-B / improved

参考：sad
字幕：I know.
中文：我知道。
B：The character's emotional state is neutral, indifferent, detached.
C：The character's emotional state is sadness, anxiety, emotional numbness, irritability, depression.
诊断质量（并非官方分数贡献）：B=0.8，C=1.0
新增证据：Appraisal hypotheses: goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low
移除证据：无

## 67. IEMOCAPFour / Ses05F_impro01_F018 / C-B / worsened

参考：anger
字幕：Why not?
中文：为什么不呢？
B：The character's emotional state is excited, frustrated, angry, excited, joyful.
C：The character's emotional state is excited, passionate.
诊断质量（并非官方分数贡献）：B=1.0，C=0.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low
移除证据：无

## 68. IEMOCAPFour / Ses05F_impro02_F008 / C-B / worsened

参考：sad
字幕：I don't know "sigh".
中文：我不知道“叹气”。
B：The character's emotional state is confused, resigned, overwhelmed, sad, supportive.
C：The character's emotional state is confused, resigned, helpless.
诊断质量（并非官方分数贡献）：B=1.0，C=0.4
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag circumstance; agency: aag self; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high
移除证据：无

## 69. IEMOCAPFour / Ses05F_impro03_F004 / E-C / improved

参考：happy
字幕：Uh-huh.
中文：嗯嗯。
C：The character's emotional state is excited, satisfied, positive.
E：The character's emotional state is excited, happy, positive.
诊断质量（并非官方分数贡献）：C=0.8，E=1.0
新增证据：Emotion hypotheses: joy, hopeful, content
移除证据：无

## 70. IEMOCAPFour / Ses05F_impro03_F059 / E-C / improved

参考：happy
字幕：Total turn on.
中文：总共打开。
C：The character's emotional state is excitement, urgency, anticipation, tension.
E：The character's emotional state is excitement, nervousness, joy, anticipation.
诊断质量（并非官方分数贡献）：C=0.8，E=1.0
新增证据：Emotion hypotheses: joy, content, hopeful
移除证据：无

## 71. IEMOCAPFour / Ses05F_impro03_F020 / E-C / worsened

参考：happy
字幕：Yeah.  Yeah, of course.
中文：是的。是的，当然。
C：The character's emotional state is excited, positive, enthusiastic.
E：The character's emotional state is excited, satisfied.
诊断质量（并非官方分数贡献）：C=0.8，E=0.6
新增证据：Emotion hypotheses: joy, hopeful, delightful
移除证据：无

## 72. IEMOCAPFour / Ses05F_impro03_M001 / E-C / worsened

参考：happy
字幕：Come on, what?
中文：来吧，什么？
C：The character's emotional state is excited, happy, enthusiastic.
E：The character's emotional state is excited, enthusiastic, possibly teasing.
诊断质量（并非官方分数贡献）：C=1.0，E=0.4
新增证据：Emotion hypotheses: joy, hopeful, content
移除证据：无

## 73. IEMOCAPFour / Ses05F_impro02_M041 / P-E / improved

参考：sad
字幕：I love you.
中文：我爱你。
E：The character's emotional state is love, commitment, positive feelings, connection.
P：The character's emotional state is love, commitment, happiness, excitement, calmness, serenity, melancholy, sorrow.
诊断质量（并非官方分数贡献）：E=0.0，P=1.0
新增证据：Supporting links: visual: smile present -> joy; visual: smile present -> hopeful
移除证据：无

## 74. IEMOCAPFour / Ses05F_impro03_M003 / P-E / improved

参考：happy
字幕：No way.
中文：没门。
E：The character's emotional state is disapproval, refusal, negative.
P：The character's emotional state is negative, rejection, disinterest, relaxed, content, lack of motivation.
诊断质量（并非官方分数贡献）：E=0.0，P=0.6
新增证据：Supporting links: visual: smile present -> joy; visual: smile present -> hopeful
移除证据：无

## 75. IEMOCAPFour / Ses05F_impro03_F004 / P-E / worsened

参考：happy
字幕：Uh-huh.
中文：嗯嗯。
E：The character's emotional state is excited, happy, positive.
P：The character's emotional state is excited, satisfied, positive.
诊断质量（并非官方分数贡献）：E=1.0，P=0.8
新增证据：Supporting links: visual: smile present -> joy; visual: smile present -> hopeful
移除证据：无

## 76. IEMOCAPFour / Ses05F_impro03_M049 / P-E / worsened

参考：happy
字幕：So I was one of the first ones? That makes me feel so important.
中文：所以我是第一个之一？这让我感到非常重要。
E：The character's emotional state is important, positive, appreciated, valued, proud.
P：The character's emotional state is important, positive, proud, accomplished.
诊断质量（并非官方分数贡献）：E=1.0，P=0.8
新增证据：Supporting links: text: evaluation positive -> appreciated; visual: smile present -> joy
移除证据：无

## 77. IEMOCAPFour / Ses05F_impro03_F020 / C-P / improved

参考：happy
字幕：Yeah.  Yeah, of course.
中文：是的。是的，当然。
P：The character's emotional state is excited, satisfied.
C：The character's emotional state is excited, positive, enthusiastic.
诊断质量（并非官方分数贡献）：P=0.6，C=0.8
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, delightful | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 78. IEMOCAPFour / Ses05F_impro03_M001 / C-P / improved

参考：happy
字幕：Come on, what?
中文：来吧，什么？
P：The character's emotional state is excited, enthusiastic, possibly teasing.
C：The character's emotional state is excited, happy, enthusiastic.
诊断质量（并非官方分数贡献）：P=0.4，C=1.0
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, content | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 79. IEMOCAPFour / Ses05F_impro02_M041 / C-P / worsened

参考：sad
字幕：I love you.
中文：我爱你。
P：The character's emotional state is love, commitment, happiness, excitement, calmness, serenity, melancholy, sorrow.
C：The character's emotional state is love, commitment, happiness, excitement, calmness, serenity, contentment, enjoyment.
诊断质量（并非官方分数贡献）：P=1.0，C=0.0
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, content | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 80. IEMOCAPFour / Ses05F_impro03_F059 / C-P / worsened

参考：happy
字幕：Total turn on.
中文：总共打开。
P：The character's emotional state is excitement, enthusiasm, joy, humor.
C：The character's emotional state is excitement, urgency, anticipation, tension.
诊断质量（并非官方分数贡献）：P=1.0，C=0.8
新增证据：无
移除证据：Emotion hypotheses: joy, content, hopeful | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 81. CMUMOSI / cM3Yna7AavY_6 / A-P / improved

参考：2.8
字幕：ANYWAY OH YOU CAN SEE IM STILL SPEECHLESS THIS MOVIE WAS JUST BEAUTIFUL
中文：无论如何，哦，你可以看到我仍然无言以对，这部电影实在太美了。
P：The character's emotional state is anxious, tense, overwhelmed, unsatisfied, confused.
A：The character's emotional state is excitement, enthusiasm, admiration.
诊断质量（并非官方分数贡献）：P=0.0，A=1.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation positive; text: intensifier present; text: exclamation interjection; audio: speech rate rel slow; audio: pitch variability high; audio: pause long; audio: pause frequent; audio: intonation falling; visual: brows furrowed; visual: brows raised; visual: eyes squinted; visual: mouth corners down; visual: grimace present | Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

## 82. CMUMOSI / cXypl4FnoZo_19 / A-P / improved

参考：0.8
字幕：UM BUT YEAH WHATEVER UM HE WE THOUGHT IT WOULD BE HIM BECAUSE THEY WERENT SHOWING HIM A LOT BUT THEY SHOWED HIM ENOUGH TO THEY KIND OF BE LIKE OH IT WAS HIM IN THE END
中文：嗯，但是，无论如何，嗯，我们原本以为会是他，因为他们没有给他很多镜头，但他们给了他足够的镜头，让人们在最后会有种“哦，原来是他”的感觉。
P：The character's emotional state is surprised, shocked, disappointed, frustrated.
A：The character's emotional state is surprised, shocked, excited, passionate.
诊断质量（并非官方分数贡献）：P=0.0，A=1.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: negation present; text: contrast present; text: intensifier present; text: exclamation interjection; text: explicit causal attribution other; audio: speech rate rel slow; audio: intonation rising; audio: intonation falling; visual: brows raised; visual: eyes widened; visual: lips pressed | Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc mixed; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

## 83. CMUMOSI / c7UH_rxdZv4_29 / A-P / worsened

参考：0.6
字幕：WHO SEEMED TO HAVE GENUINE AFFECTION FOR OTHER HUMAN BEINGS
中文：似乎对其他人类有真正的感情的人
P：The character's emotional state is serious, genuine, caring.
A：The character's emotional state is serious, concerned, thoughtful, evaluating, possibly disappointed, frustrated, appreciative, approving.
诊断质量（并非官方分数贡献）：P=1.0，A=0.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: intensifier present; text: uncertainty hedge; audio: speech rate rel slow; audio: pitch variability low; audio: intonation falling; visual: brows raised; visual: eyes widened | Appraisal hypotheses: goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

## 84. CMUMOSI / cM3Yna7AavY_1 / A-P / worsened

参考：2.2
字幕：I JUST GOT BACK FROM THE MOVIE THEATERS TO GO SEE A MOVIE IVE BEEN WAITING PROBABLY ABOUT A YEAR AND A HALF TO TWO YEARS FOR
中文：我刚从电影院回来，去看了一部我可能已经等待了一年半到两年的电影。
P：The character's emotional state is excited, anxious, frustrated, positive, anticipatory.
A：The character's emotional state is excited, eager, frustrated, disappointed, longing.
诊断质量（并非官方分数贡献）：P=1.0，A=0.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: intensifier present; text: uncertainty hedge; audio: speech rate rel slow; audio: pitch variability low; audio: pause long; audio: intonation falling; audio: intonation flat; visual: brows raised; visual: eyes widened | Appraisal hypotheses: goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

## 85. CMUMOSI / c7UH_rxdZv4_10 / C-B / improved

参考：0.8
字幕：THERES SOMETHING THAT JUST KIND OF MAKES THAM SO SL SLIGHTLY ENDEARING EVEN THOUGH THEYRE KIND OF THE JACK ASS YOU KNOW
中文：有些东西使他们稍微讨人喜欢，即使他们有点像你知道的那种讨厌鬼。
B：The character's emotional state is sarcastic, mocking, amused.
C：The character's emotional state is sarcastic, mocking, amused, cheerful.
诊断质量（并非官方分数贡献）：B=0.0，C=1.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high; coping potential: acp low
移除证据：无

## 86. CMUMOSI / cXypl4FnoZo_23 / C-B / improved

参考：0.4
字幕：AND IT WOULD MAKE SENSE
中文：并且这是有道理的
B：The character's emotional state is frustrated, irritated, humorous, sarcastic, ironic.
C：The character's emotional state is frustrated, disheartened, positive outlook, hope, optimism.
诊断质量（并非官方分数贡献）：B=0.0，C=1.0
新增证据：Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high
移除证据：无

## 87. CMUMOSI / d3_k5Xpfmik_17 / C-B / worsened

参考：1.6
字幕：BUT ITS A VERY KIND OF UM STYLISTIC EDGE ON IT
中文：但它具有一种非常独特的风格边缘。
B：The character's emotional state is positive, acknowledgment, agreement.
C：The character's emotional state is positive, negative.
诊断质量（并非官方分数贡献）：B=1.0，C=0.0
新增证据：Appraisal hypotheses: goal congruence: agc mixed; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; coping potential: acp high
移除证据：无

## 88. CMUMOSI / d3_k5Xpfmik_7 / C-B / worsened

参考：0.4
字幕：AND UM WHILE ALSO MAINTAINS ITS KIND OF DETACHED UM SATIRE OF THE GENRE
中文：同时，它也保持了对该类型的一种超然的讽刺
B：The character's emotional state is detached, ironic, sarcastic, relaxed, cheerful.
C：The character's emotional state is amused, ironic, detached, sarcastic.
诊断质量（并非官方分数贡献）：B=1.0，C=0.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc mixed; goal congruence: agc incongruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high
移除证据：无

## 89. CMUMOSI / cXypl4FnoZo_4 / E-C / improved

参考：-0.8
字幕：I THOUGHT IT COULD BE REALLY BAD UM BUT IT DIDNT LOOK LIKE IT WOULD BE BUT IT COULDVE BEEN
中文：我原本以为它可能会非常糟糕，但它看起来并不像会那样，但它本可能会那样。
C：The character's emotional state is relief, surprise.
E：The character's emotional state is worry, uncertainty, relief, reassurance.
诊断质量（并非官方分数贡献）：C=0.0，E=1.0
新增证据：Emotion hypotheses: disappointed, hesitant, anger
移除证据：无

## 90. CMUMOSI / fvVhgmXxadc_9 / E-C / improved

参考：-0.4
字幕：THAT KIND OF LOOKS LIKE VIDEO GAME IN A CERTAIN WAY
中文：那在某种程度上看起来像是电子游戏
C：The character's emotional state is positive, appreciative, metaphorical.
E：The character's emotional state is positive, appreciative, metaphorical, analogy.
诊断质量（并非官方分数贡献）：C=0.0，E=1.0
新增证据：Emotion hypotheses: bewildered, hesitant, anxious
移除证据：无

## 91. CMUMOSI / dq3Nf_lMPnE_14 / E-C / worsened

参考：-1.8
字幕：UNLESS YOUR KIDS ARE DYING TO SEE IT ID WAIT FOR THE DVD
中文：除非你的孩子非常想看，否则我会建议你等DVD出来再看。
C：The character's emotional state is excited, enthusiastic, sarcastic, mocking.
E：The character's emotional state is excited, enthusiastic, humorous, sarcastic.
诊断质量（并非官方分数贡献）：C=1.0，E=0.0
新增证据：Emotion hypotheses: hopeful, joy, confident
移除证据：无

## 92. CMUMOSI / jUzDDGyPkXU_6 / E-C / worsened

参考：-1.6
字幕：IN FACT THIS MOVIE ISNT EVEN ON THE SAME LEVEL AS DISTRICT 9 NOR IS IT UM FOR UH BLACK HAWK DOWN WHICH PEOPLE ARE COMPARING IT TO
中文：事实上，这部电影甚至无法与《第九区》相提并论，也无法与人们常拿来比较的《黑鹰坠落》相比。
C：The character's emotional state is disappointment, dissatisfaction, anger, frustration.
E：The character's emotional state is disappointment, dissatisfaction, excitement, enthusiasm, negative assessment, frustration.
诊断质量（并非官方分数贡献）：C=1.0，E=0.0
新增证据：Emotion hypotheses: disappointed, depressed, despair
移除证据：无

## 93. CMUMOSI / dq3Nf_lMPnE_14 / P-E / improved

参考：-1.8
字幕：UNLESS YOUR KIDS ARE DYING TO SEE IT ID WAIT FOR THE DVD
中文：除非你的孩子非常想看，否则我会建议你等DVD出来再看。
E：The character's emotional state is excited, enthusiastic, humorous, sarcastic.
P：The character's emotional state is excited, enthusiastic, sarcastic, teasing.
诊断质量（并非官方分数贡献）：E=0.0，P=1.0
新增证据：Supporting links: visual: brows raised -> joy; visual: brows raised -> hopeful
移除证据：无

## 94. CMUMOSI / etzxEpPuc6I_13 / P-E / improved

参考：-2.2
字幕：LIKE THIS ONE PART WHERE THE GIRLS LIKE MY DADDY TAUGHT ME TO WIN WIN AND THEN SHES LOOKING IN THE CAMERA AND IM LIKE WOW LIKE UM THIS ACTINGS PRETTY BAD
中文：就像这一部分，女孩们喜欢我爸爸教我要赢，然后她看着摄像机，我就像哇，这个表演真的很糟糕。
E：The character's emotional state is excited, joyful, anxious, agitated.
P：The character's emotional state is excited, happy, anxious, confused, distressed, dramatic.
诊断质量（并非官方分数贡献）：E=0.0，P=1.0
新增证据：Supporting links: visual: smile present -> joy; text: evaluation negative -> disappointed
移除证据：无

## 95. CMUMOSI / cXypl4FnoZo_4 / P-E / worsened

参考：-0.8
字幕：I THOUGHT IT COULD BE REALLY BAD UM BUT IT DIDNT LOOK LIKE IT WOULD BE BUT IT COULDVE BEEN
中文：我原本以为它可能会非常糟糕，但它看起来并不像会那样，但它本可能会那样。
E：The character's emotional state is worry, uncertainty, relief, reassurance.
P：The character's emotional state is relief, surprise.
诊断质量（并非官方分数贡献）：E=1.0，P=0.0
新增证据：Supporting links: text: evaluation negative -> disappointed; text: evaluation negative -> anger
移除证据：无

## 96. CMUMOSI / f9O3YtZ2VfI_14 / P-E / worsened

参考：1.2
字幕：JUST GIVE ME A NICE INTERESTING CHOKE
中文：只需给我一个有趣的好的压制技巧
E：The character's emotional state is positive, humorous, sarcastic.
P：The character's emotional state is playful, sarcastic.
诊断质量（并非官方分数贡献）：E=1.0，P=0.0
新增证据：Supporting links: text: evaluation positive -> appreciated; text: evaluation positive -> agc congruent -> hopeful
移除证据：无

## 97. CMUMOSI / f9O3YtZ2VfI_14 / C-P / improved

参考：1.2
字幕：JUST GIVE ME A NICE INTERESTING CHOKE
中文：只需给我一个有趣的好的压制技巧
P：The character's emotional state is playful, sarcastic.
C：The character's emotional state is positive, humorous, sarcastic.
诊断质量（并非官方分数贡献）：P=0.0，C=1.0
新增证据：无
移除证据：Emotion hypotheses: hopeful, appreciated, joy | Supporting links: text: evaluation positive -> appreciated; text: evaluation positive -> agc congruent -> hopeful

## 98. CMUMOSI / f_pcplsH_V0_1 / C-P / improved

参考：0.25
字幕：SO YOU BETTER APPRECIATE THIS REVIEW
中文：所以你最好珍视这篇评论
P：The character's emotional state is challenge, threat, confidence, arrogance.
C：The character's emotional state is challenge, threat, confidence, arrogance, determination, focus.
诊断质量（并非官方分数贡献）：P=0.0，C=1.0
新增证据：无
移除证据：Emotion hypotheses: hopeful, joy, appreciated | Supporting links: text: evaluation positive -> appreciated; text: evaluation positive -> agc congruent -> hopeful

## 99. CMUMOSI / etzxEpPuc6I_13 / C-P / worsened

参考：-2.2
字幕：LIKE THIS ONE PART WHERE THE GIRLS LIKE MY DADDY TAUGHT ME TO WIN WIN AND THEN SHES LOOKING IN THE CAMERA AND IM LIKE WOW LIKE UM THIS ACTINGS PRETTY BAD
中文：就像这一部分，女孩们喜欢我爸爸教我要赢，然后她看着摄像机，我就像哇，这个表演真的很糟糕。
P：The character's emotional state is excited, happy, anxious, confused, distressed, dramatic.
C：The character's emotional state is excited, joyful, anxious, agitated.
诊断质量（并非官方分数贡献）：P=1.0，C=0.0
新增证据：无
移除证据：Emotion hypotheses: anger, disappointed, joy | Supporting links: visual: smile present -> joy; text: evaluation negative -> disappointed

## 100. CMUMOSI / etzxEpPuc6I_6 / C-P / worsened

参考：0.4
字幕：BUT THEY HAVE A LOT OF ADULT SITUATIONS IN IT
中文：但是它们包含了很多成人情境。
P：The character's emotional state is tense, anxious, humorous, teasing.
C：The character's emotional state is tense, concerned.
诊断质量（并非官方分数贡献）：P=1.0，C=0.0
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, manic | Supporting links: visual: brows raised -> joy; visual: brows raised -> hopeful

## 101. CMUMOSEI / -6rXp3zJ3kc_9 / A-P / improved

参考：0.3333333432674408
字幕：So the answer to the question, can I contribute stock to an IRA is absolutely correct but always be mindful of the security that your using it, make sure it's safe.
中文：所以对于这个问题的答案，我可以将股票捐赠给IRA是完全正确的，但是一定要注意你使用的安全性，确保它是安全的。
P：The character's emotional state is neutral, cautious.
A：The character's emotional state is excited, enthusiastic, confident, motivated, passionate.
诊断质量（并非官方分数贡献）：P=0.0，A=1.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation positive; text: contrast present; text: intensifier present; text: desire need; audio: speech rate rel slow; audio: pitch variability low; audio: pause long; audio: intonation falling; audio: intonation flat; visual: lips pressed | Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high; coping potential: acp low

## 102. CMUMOSEI / -RfYyzHpjk4_8 / A-P / improved

参考：0.3333333432674408
字幕：It's pretty, pretty easy to do but you got to set up those numbers ahead of time.
中文：这很容易做，但你必须提前设置好这些数字。
P：The character's emotional state is excitement, anxiety, happiness, sadness.
A：The character's emotional state is excitement, anxiety, humor.
诊断质量（并非官方分数贡献）：P=0.0，A=1.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation positive; text: contrast present; text: intensifier present; text: desire need; audio: pitch variability low; audio: intonation falling; visual: brows furrowed; visual: eyes squinted; visual: mouth corners down | Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high; coping potential: acp low

## 103. CMUMOSEI / -9y-fZ3swSY_6 / A-P / worsened

参考：-0.3333333432674408
字幕：So even if you’re a lady, never call another women or a lady, hey
中文：所以，即使你是一个女士，也不要称呼另一个女性或女士为“嘿”。
P：The character's emotional state is excitement, tension, anxiety.
A：The character's emotional state is positive.
诊断质量（并非官方分数贡献）：P=1.0，A=0.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: negation present; text: contrast present; audio: speech rate rel fast; audio: speech rate rel slow; audio: pitch level rel high; audio: pitch variability high; audio: intonation rising; audio: intonation falling; visual: brows raised; visual: eyes widened | Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

## 104. CMUMOSEI / -HeZS2-Prhc_5 / A-P / worsened

参考：1.0
字幕：So a look at the gold and silver exchange traded funds: SPDR Gold Shares (GLD) popped nearly 1% in early trade on the stock market today.
中文：所以，让我们来看看黄金和白银交易基金：今天早盘，SPDR黄金股份（GLD）在股市上涨了近1%。
P：The character's emotional state is positive, enthusiastic.
A：The character's emotional state is neutral.
诊断质量（并非官方分数贡献）：P=1.0，A=0.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation positive; text: explicit success outcome; audio: speech rate rel slow; audio: intonation rising; audio: intonation falling; visual: brows raised; visual: eyes widened; visual: head lowered | Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high; coping potential: acp low

## 105. CMUMOSEI / -s9qJ7ATP7w_1 / C-B / improved

参考：0.6666666865348816
字幕：But the hardest thing in life to learn, is to lose
中文：但是生活中最难学会的事情是失去。
B：The character's emotional state is ironic, negative, overwhelmed, pressured.
C：The character's emotional state is ironic, humorous, positive.
诊断质量（并非官方分数贡献）：B=0.0，C=1.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag circumstance; agency: aag self; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high
移除证据：无

## 106. CMUMOSEI / 107585_15 / C-B / improved

参考：-1.0
字幕：You don't believe that someone can actually you know believe in the priest and just wanted get married that badly in that church
中文：你不相信有人真的相信神父，只是想在那个教堂里结婚那么急切。
B：The character's emotional state is excitement, nervousness, surprise, disbelief.
C：The character's emotional state is excitement, anger, disappointment.
诊断质量（并非官方分数贡献）：B=0.0，C=1.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high
移除证据：无

## 107. CMUMOSEI / -RfYyzHpjk4_8 / C-B / worsened

参考：0.3333333432674408
字幕：It's pretty, pretty easy to do but you got to set up those numbers ahead of time.
中文：这很容易做，但你必须提前设置好这些数字。
B：The character's emotional state is excitement, anxiety, happiness, satisfaction.
C：The character's emotional state is excitement, anxiety, happiness, sadness.
诊断质量（并非官方分数贡献）：B=1.0，C=0.0
新增证据：Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high; coping potential: acp low
移除证据：无

## 108. CMUMOSEI / -ri04Z7vwnc_2 / C-B / worsened

参考：-0.3333333432674408
字幕：most people think it'll sort itself out, "we'll discuss it later," it's not something too important
中文：大多数人认为这个问题会自行解决，“我们以后再讨论”，这不是什么太重要的事情。
B：The character's emotional state is relaxed, indifferent.
C：The character's emotional state is relaxed, not too concerned.
诊断质量（并非官方分数贡献）：B=1.0，C=0.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high
移除证据：无

## 109. CMUMOSEI / -ri04Z7vwnc_2 / E-C / improved

参考：-0.3333333432674408
字幕：most people think it'll sort itself out, "we'll discuss it later," it's not something too important
中文：大多数人认为这个问题会自行解决，“我们以后再讨论”，这不是什么太重要的事情。
C：The character's emotional state is relaxed, not too concerned.
E：The character's emotional state is relaxed, not taking it seriously, disagreement, disapproval.
诊断质量（并非官方分数贡献）：C=0.0，E=1.0
新增证据：Emotion hypotheses: disappointed, hesitant, anger
移除证据：无

## 110. CMUMOSEI / 112509_4 / E-C / improved

参考：-2.0
字幕：(umm) Felt pretty rehashed
中文：(嗯) 感觉很陈旧
C：The character's emotional state is positive, self-deprecating, humorous.
E：The character's emotional state is positive, negative.
诊断质量（并非官方分数贡献）：C=0.0，E=1.0
新增证据：Emotion hypotheses: hesitant, joy, manic
移除证据：无

## 111. CMUMOSEI / -s9qJ7ATP7w_1 / E-C / worsened

参考：0.6666666865348816
字幕：But the hardest thing in life to learn, is to lose
中文：但是生活中最难学会的事情是失去。
C：The character's emotional state is ironic, humorous, positive.
E：The character's emotional state is ironic, negative, overwhelmed, pressured.
诊断质量（并非官方分数贡献）：C=1.0，E=0.0
新增证据：Emotion hypotheses: disappointed, ashamed, anger
移除证据：无

## 112. CMUMOSEI / -s9qJ7ATP7w_7 / E-C / worsened

参考：1.0
字幕：I used to work for Warren Avis, the guy who started Avis Rent a Car, and he said to me one day, "Robert, "what's the purpose of business
中文：我曾经为沃伦·艾维斯工作，他是Avis租车公司的创始人，有一天他对我说：“罗伯特，企业的目的是什么？”
C：The character's emotional state is tranquil, contemplative.
E：The character's emotional state is calm, contemplative.
诊断质量（并非官方分数贡献）：C=1.0，E=0.0
新增证据：Emotion hypotheses: joy, hopeful, content
移除证据：无

## 113. CMUMOSEI / -s9qJ7ATP7w_1 / P-E / improved

参考：0.6666666865348816
字幕：But the hardest thing in life to learn, is to lose
中文：但是生活中最难学会的事情是失去。
E：The character's emotional state is ironic, negative, overwhelmed, pressured.
P：The character's emotional state is ironic, humorous, positive.
诊断质量（并非官方分数贡献）：E=0.0，P=1.0
新增证据：Supporting links: text: evaluation negative -> disappointed; text: evaluation negative -> anger
移除证据：无

## 114. CMUMOSEI / 0K7dCp80n9c_13 / P-E / improved

参考：0.3333333432674408
字幕：It's really designed for well water because that's the kind of water that typically will have an iron problem.
中文：这个产品真正是为井水设计的，因为井水通常会有铁质问题。
E：The character's emotional state is serious, focused, concerned, professional, stressed, anxious.
P：The character's emotional state is serious, focused, concerned, professional, scientific.
诊断质量（并非官方分数贡献）：E=0.0，P=1.0
新增证据：Supporting links: text: evaluation negative -> disappointed; text: evaluation negative -> anger
移除证据：无

## 115. CMUMOSEI / 108146_7 / P-E / worsened

参考：-2.0
字幕：Ocean's Thirteen, not exciting at all
中文：海洋的十三人，一点都不令人兴奋。
E：The character's emotional state is neutral, negative, sarcastic.
P：The character's emotional state is teasing, sarcasm, playful, lighthearted, positive.
诊断质量（并非官方分数贡献）：E=1.0，P=0.0
新增证据：Supporting links: text: evaluation negative -> disappointed; text: evaluation negative -> anger
移除证据：无

## 116. CMUMOSEI / 173CpFb3clw_3 / P-E / worsened

参考：0.3333333432674408
字幕：Review your draft again and then again make sure that it meets all the requirements for your products and services and the regulations and compliance that you working in.
中文：请再次审查您的草稿，并确保它符合您的产品和服务的所有要求，以及您所从事的法规和合规要求。
E：The character's emotional state is serious, focused, thorough, attentive, concerned, professional, serious.
P：The character's emotional state is serious, focused, thorough, attentive, concerned, demanding, careful, cautious, neutral, mixed.
诊断质量（并非官方分数贡献）：E=1.0，P=0.0
新增证据：Supporting links: text: desire need -> focused; text: desire need -> hopeful
移除证据：无

## 117. CMUMOSEI / -s9qJ7ATP7w_7 / C-P / improved

参考：1.0
字幕：I used to work for Warren Avis, the guy who started Avis Rent a Car, and he said to me one day, "Robert, "what's the purpose of business
中文：我曾经为沃伦·艾维斯工作，他是Avis租车公司的创始人，有一天他对我说：“罗伯特，企业的目的是什么？”
P：The character's emotional state is calm, introspective.
C：The character's emotional state is tranquil, contemplative.
诊断质量（并非官方分数贡献）：P=0.0，C=1.0
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, content | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 118. CMUMOSEI / 108146_7 / C-P / improved

参考：-2.0
字幕：Ocean's Thirteen, not exciting at all
中文：海洋的十三人，一点都不令人兴奋。
P：The character's emotional state is teasing, sarcasm, playful, lighthearted, positive.
C：The character's emotional state is neutral, slightly negative.
诊断质量（并非官方分数贡献）：P=0.0，C=1.0
新增证据：无
移除证据：Emotion hypotheses: disappointed, anger, despair | Supporting links: text: evaluation negative -> disappointed; text: evaluation negative -> anger

## 119. CMUMOSEI / -ri04Z7vwnc_2 / C-P / worsened

参考：-0.3333333432674408
字幕：most people think it'll sort itself out, "we'll discuss it later," it's not something too important
中文：大多数人认为这个问题会自行解决，“我们以后再讨论”，这不是什么太重要的事情。
P：The character's emotional state is relaxed, indifferent.
C：The character's emotional state is relaxed, not too concerned.
诊断质量（并非官方分数贡献）：P=1.0，C=0.0
新增证据：无
移除证据：Emotion hypotheses: disappointed, hesitant, anger | Supporting links: text: evaluation negative -> disappointed; text: evaluation negative -> anger

## 120. CMUMOSEI / 112509_4 / C-P / worsened

参考：-2.0
字幕：(umm) Felt pretty rehashed
中文：(嗯) 感觉很陈旧
P：The character's emotional state is positive, negative.
C：The character's emotional state is positive, self-deprecating, humorous.
诊断质量（并非官方分数贡献）：P=1.0，C=0.0
新增证据：无
移除证据：Emotion hypotheses: hesitant, joy, manic | Supporting links: visual: brows raised -> joy; text: uncertainty hedge -> hesitant

## 121. SIMS / video_0002_0004 / A-P / improved

参考：-1.0
字幕：I think you have no reason to refuse.
中文：我认为你没有理由拒绝。
P：The character's emotional state is confident, firm, serious, contemplative, authoritative.
A：The character's emotional state is confident, firm, urgency, authority, anxiety, stress, blame, pressure, challenge.
诊断质量（并非官方分数贡献）：P=0.0，A=1.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation positive; text: negation present; text: uncertainty hedge; audio: intonation falling; visual: brows raised; visual: eyes widened | Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

## 122. SIMS / video_0025_0018 / A-P / improved

参考：0.2
字幕：Don't look down on them. I have made great efforts to gather all kinds of gods.
中文：你不要瞧不起他们哦，为了把各路大神聚集，我是费了大力气的。
P：The character's emotional state is nervous, excited, proud, angry, disappointed.
A：The character's emotional state is nervous, excited, proud, angry.
诊断质量（并非官方分数贡献）：P=0.0，A=1.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: affect word negative; text: evaluation positive; text: negation present; text: intensifier present; text: exclamation interjection; text: explicit causal attribution self; audio: pitch variability high; audio: intonation rising; visual: brows raised; visual: eyes widened; visual: smile present | Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag other; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low | Emotion hypotheses: joy, hopeful, appreciated | Supporting links: text: evaluation positive -> appreciated; text: evaluation positive -> agc congruent -> hopeful

## 123. SIMS / video_0002_0029 / A-P / worsened

参考：-0.6
字幕：Not ideal, the topic is too high-end.
中文：不太理想，话题太高端。
P：The character's emotional state is anxious, stressed, frustrated.
A：The character's emotional state is anxious, excited.
诊断质量（并非官方分数贡献）：P=1.0，A=0.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation negative; text: negation present; text: intensifier present; audio: pitch variability low; audio: intonation falling; visual: brows raised; visual: eyes squinted | Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high | Emotion hypotheses: disappointed, anger, helpless | Supporting links: text: evaluation negative -> disappointed; text: evaluation negative -> anger

## 124. SIMS / video_0012_0016 / A-P / worsened

参考：1.0
字幕：Don't be sad, Guantao will always be with you
中文：你别难过，馆陶会一直陪着你的
P：The character's emotional state is comfort, encouragement, sympathy.
A：The character's emotional state is comfort, encouragement, sadness.
诊断质量（并非官方分数贡献）：P=1.0，A=0.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: affect word negative; text: negation present; text: intensifier present; audio: speech rate rel slow; audio: pitch variability low; audio: intonation falling; visual: mouth corners down; visual: head lowered | Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

## 125. SIMS / video_0012_0016 / C-B / improved

参考：1.0
字幕：Don't be sad, Guantao will always be with you
中文：你别难过，馆陶会一直陪着你的
B：The character's emotional state is comfort, encouragement, solitude, distress.
C：The character's emotional state is comfort, encouragement, sympathy.
诊断质量（并非官方分数贡献）：B=0.0，C=1.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high
移除证据：无

## 126. SIMS / video_0015_0035 / C-B / improved

参考：-0.6
字幕：Even if this diary is true, you cannot prove me to be a murderer.
中文：就算这本日记是真的，你也不能指证我是凶手。
B：The character's emotional state is cool, calm, confident, calm, confident, defense, rebuttal.
C：The character's emotional state is defensive, frustrated, angry.
诊断质量（并非官方分数贡献）：B=0.0，C=1.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc mixed; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high
移除证据：无

## 127. SIMS / video_0035_0011 / C-B / worsened

参考：1.0
字幕：Bai Juyi, he's crazy
中文：白居易，他可狂得很
B：The character's emotional state is excited, crazy, positive.
C：The character's emotional state is excitement, frustration, humor, sarcasm, mockery.
诊断质量（并非官方分数贡献）：B=1.0，C=0.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; coping potential: acp low; coping potential: acp high
移除证据：无

## 128. SIMS / video_0045_0045 / E-C / worsened

参考：-0.6
字幕：Jack Ma was only an English teacher when he was 30 years old. He could only earn a few hundred dollars a month by translating.
中文：马云在三十岁的时候也只是英语老师，一个月靠翻译只能挣到几百块钱
C：The character's emotional state is excited, enthusiastic, proud, frustrated, disappointed.
E：The character's emotional state is excited, enthusiastic, proud.
诊断质量（并非官方分数贡献）：C=1.0，E=0.0
新增证据：Emotion hypotheses: disappointed, anger, depressed
移除证据：无

## 129. SIMS / video_0029_0016 / P-E / improved

参考：1.0
字幕：Hey, do you have any cigarettes
中文：哎，有烟吗
E：The character's emotional state is relaxed, smiling, happy, comfortable, tense, anxious.
P：The character's emotional state is relaxed, friendly, anticipatory.
诊断质量（并非官方分数贡献）：E=0.0，P=1.0
新增证据：Supporting links: visual: smile present -> joy; visual: smile present -> hopeful
移除证据：无

## 130. SIMS / video_0045_0045 / P-E / improved

参考：-0.6
字幕：Jack Ma was only an English teacher when he was 30 years old. He could only earn a few hundred dollars a month by translating.
中文：马云在三十岁的时候也只是英语老师，一个月靠翻译只能挣到几百块钱
E：The character's emotional state is excited, enthusiastic, proud.
P：The character's emotional state is excited, enthusiastic, frustrated, angry.
诊断质量（并非官方分数贡献）：E=0.0，P=1.0
新增证据：Supporting links: visual: brows furrowed -> anger; visual: brows furrowed -> disappointed
移除证据：无

## 131. SIMS / video_0025_0018 / P-E / worsened

参考：0.2
字幕：Don't look down on them. I have made great efforts to gather all kinds of gods.
中文：你不要瞧不起他们哦，为了把各路大神聚集，我是费了大力气的。
E：The character's emotional state is nervous, excited, proud, anxious, confident.
P：The character's emotional state is nervous, excited, proud, angry, disappointed.
诊断质量（并非官方分数贡献）：E=1.0，P=0.0
新增证据：Supporting links: text: evaluation positive -> appreciated; text: evaluation positive -> agc congruent -> hopeful
移除证据：无

## 132. SIMS / video_0058_0002 / P-E / worsened

参考：-0.8
字幕：You are not good enough.
中文：你确实还差点意思
E：The character's emotional state is anxious, stressed, overwhelmed, critical, negative.
P：The character's emotional state is anxious, stressed, overwhelmed, happy, content, at ease.
诊断质量（并非官方分数贡献）：E=1.0，P=0.0
新增证据：Supporting links: visual: smile present -> joy; text: evaluation negative -> disappointed
移除证据：无

## 133. SIMS / video_0025_0018 / C-P / improved

参考：0.2
字幕：Don't look down on them. I have made great efforts to gather all kinds of gods.
中文：你不要瞧不起他们哦，为了把各路大神聚集，我是费了大力气的。
P：The character's emotional state is nervous, excited, proud, angry, disappointed.
C：The character's emotional state is nervous, excited, proud, angry.
诊断质量（并非官方分数贡献）：P=0.0，C=1.0
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, appreciated | Supporting links: text: evaluation positive -> appreciated; text: evaluation positive -> agc congruent -> hopeful

## 134. SIMS / video_0058_0002 / C-P / improved

参考：-0.8
字幕：You are not good enough.
中文：你确实还差点意思
P：The character's emotional state is anxious, stressed, overwhelmed, happy, content, at ease.
C：The character's emotional state is anxious, stressed, overwhelmed, critical, negative.
诊断质量（并非官方分数贡献）：P=0.0，C=1.0
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, disappointed | Supporting links: visual: smile present -> joy; text: evaluation negative -> disappointed

## 135. SIMS / video_0029_0016 / C-P / worsened

参考：1.0
字幕：Hey, do you have any cigarettes
中文：哎，有烟吗
P：The character's emotional state is relaxed, friendly, anticipatory.
C：The character's emotional state is excited, anxious.
诊断质量（并非官方分数贡献）：P=1.0，C=0.0
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, manic | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 136. SIMSv2 / aqgy3_0003_00002 / A-P / improved

参考：0.4
字幕：More proof that I'm right.
中文：更能证明我是正确的。
P：The character's emotional state is confidence, self-righteousness, anger.
A：The character's emotional state is confidence, self-assurance, victory, firmness.
诊断质量（并非官方分数贡献）：P=0.0，A=1.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation positive; text: intensifier present; audio: intonation rising; visual: brows raised; visual: eyes widened | Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; certainty: act uncertain; certainty: act certain; coping potential: acp high

## 137. SIMSv2 / aqgy5_0013_00019 / A-P / improved

参考：-1.0
字幕：I warn you, don't take my tolerance as your shameless capital.
中文：我警告你，别拿我的容忍，当成你们不要脸的资本。
P：The character's emotional state is anger, frustration, confidence, determination.
A：The character's emotional state is anger, frustration, anxiety, stress.
诊断质量（并非官方分数贡献）：P=0.0，A=1.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: affect word negative; text: evaluation negative; text: negation present; audio: speech rate rel fast; audio: pitch level rel high; audio: vocal intensity rel high; audio: pitch variability high; audio: intonation rising; audio: intonation falling; audio: voice tense; visual: brows furrowed; visual: eyes widened; visual: mouth corners down | Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high | Emotion hypotheses: anger, disappointed, despair | Supporting links: audio: voice tense -> anger; text: evaluation negative -> disappointed

## 138. SIMSv2 / aqgy3_0003_00007 / A-P / worsened

参考：0.4
字幕：You are so important to me, how could I forget about you?
中文：你对我那么重要我怎么会把你忘了呢。
P：The character's emotional state is important, affectionate, significant, positive.
A：The character's emotional state is important, significant, commitment.
诊断质量（并非官方分数贡献）：P=1.0，A=0.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation positive; text: negation present; text: intensifier present; text: rhetorical question; audio: pitch variability high; audio: intonation rising; visual: brows raised; visual: eyes widened | Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

## 139. SIMSv2 / aqgy4_0001_00053 / A-P / worsened

参考：-0.4
字幕：You actually don't know who she can't get along with.
中文：你居然不知道她跟谁过不去。
P：The character's emotional state is anger, frustration, happiness, confusion, dissatisfaction.
A：The character's emotional state is anger, frustration, happiness, satisfaction.
诊断质量（并非官方分数贡献）：P=1.0，A=0.0
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation negative; text: negation present; text: intensifier present; audio: pitch variability high; audio: intonation rising; visual: brows raised; visual: eyes widened | Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

## 140. SIMSv2 / aqgy4_0001_00053 / C-B / improved

参考：-0.4
字幕：You actually don't know who she can't get along with.
中文：你居然不知道她跟谁过不去。
B：The character's emotional state is anger, frustration, happiness, satisfaction, contempt.
C：The character's emotional state is anger, frustration, happiness, confusion, dissatisfaction.
诊断质量（并非官方分数贡献）：B=0.0，C=1.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high
移除证据：无

## 141. SIMSv2 / aqgy4_0022_00001 / C-B / improved

参考：0.8
字幕：Wow, how do you know everything?
中文：哇你怎么什么都知道啊。
B：The character's emotional state is admiration, envy, admiration.
C：The character's emotional state is admiration, surprise, positive.
诊断质量（并非官方分数贡献）：B=0.0，C=1.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low
移除证据：无

## 142. SIMSv2 / aqgy3_0003_00002 / C-B / worsened

参考：0.4
字幕：More proof that I'm right.
中文：更能证明我是正确的。
B：The character's emotional state is confidence, self-assurance, emphasis, argument, persuasive, convincing.
C：The character's emotional state is confidence, self-righteousness, anger.
诊断质量（并非官方分数贡献）：B=1.0，C=0.0
新增证据：Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; certainty: act uncertain; certainty: act certain; coping potential: acp high
移除证据：无

## 143. SIMSv2 / aqgy4_0015_00000 / C-B / worsened

参考：0.8
字幕：Friends in the media circle, are they all brothers?
中文：媒体圈的朋友，都是兄弟嘛。
B：The character's emotional state is positive, humorous, curious.
C：The character's emotional state is surprised, curious.
诊断质量（并非官方分数贡献）：B=1.0，C=0.0
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low
移除证据：无

## 144. SIMSv2 / aqgy3_0005_00042 / E-C / improved

参考：0.6
字幕：The dog is anxious, does it look like Teacher Zeng?
中文：狗急了，长得像不像曾老师。
C：The character's emotional state is humor, mockery, relief, stress, anxiety.
E：The character's emotional state is humor, mockery, relief, positive.
诊断质量（并非官方分数贡献）：C=0.0，E=1.0
新增证据：Emotion hypotheses: joy, anger, disappointed
移除证据：无

## 145. SIMSv2 / aqgy4_0015_00000 / E-C / improved

参考：0.8
字幕：Friends in the media circle, are they all brothers?
中文：媒体圈的朋友，都是兄弟嘛。
C：The character's emotional state is surprised, curious.
E：The character's emotional state is positive, humorous, curious.
诊断质量（并非官方分数贡献）：C=0.0，E=1.0
新增证据：Emotion hypotheses: joy, hopeful, content
移除证据：无

## 146. SIMSv2 / aqgy4_0021_00000 / E-C / worsened

参考：-0.6
字幕：I was just casually saying, but you came up with so many excuses that made me curious.
中文：我真是随便一说，可你找了那么多借口我才开始好奇的。
C：The character's emotional state is curious, frustrated, annoyed, teasing, mocking.
E：The character's emotional state is curious, amused, slightly annoyed.
诊断质量（并非官方分数贡献）：C=1.0，E=0.0
新增证据：Emotion hypotheses: anger, disappointed, joy
移除证据：无

## 147. SIMSv2 / aqgy5_0018_00023 / E-C / worsened

参考：0.2
字幕：Zhang Wei's stomach growled, and the WIFI signal immediately became full bars.
中文：张伟肚子一叫，WIFI信号马上满格了。
C：The character's emotional state is anxious, nervous, excited.
E：The character's emotional state is anxious, nervous, emotionally detached.
诊断质量（并非官方分数贡献）：C=1.0，E=0.0
新增证据：Emotion hypotheses: joy, hopeful, content
移除证据：无

## 148. SIMSv2 / aqgy4_0022_00009 / P-E / improved

参考：-1.0
字幕：Nolan is the radio station's darling, you should also take a look at yourself before criticizing her.
中文：诺兰是电台台花，你也不撒泡尿照照，还嫌弃她。
E：The character's emotional state is teasing, ironic, positive.
P：The character's emotional state is teasing, challenging.
诊断质量（并非官方分数贡献）：E=0.0，P=1.0
新增证据：Supporting links: audio: voice tense -> anger; text: evaluation negative -> disappointed
移除证据：无

## 149. SIMSv2 / aqgy5_0012_00028 / P-E / improved

参考：-0.4
字幕：I'm sorry, this is a misunderstanding. It's a well-intentioned lie.
中文：对不起这是个误会这是个善意的谎言。
E：The character's emotional state is apology, clarification, understanding, positive.
P：The character's emotional state is understanding, forgiveness, tension, pressure, relief.
诊断质量（并非官方分数贡献）：E=0.0，P=1.0
新增证据：Supporting links: text: affect word negative -> ashamed; audio: vocal intensity rel low -> depressed
移除证据：无

## 150. SIMSv2 / aqgy5_0013_00019 / P-E / worsened

参考：-1.0
字幕：I warn you, don't take my tolerance as your shameless capital.
中文：我警告你，别拿我的容忍，当成你们不要脸的资本。
E：The character's emotional state is anger, frustration, anxiety, stress.
P：The character's emotional state is anger, frustration, confidence, determination.
诊断质量（并非官方分数贡献）：E=1.0，P=0.0
新增证据：Supporting links: audio: voice tense -> anger; text: evaluation negative -> disappointed
移除证据：无

## 151. SIMSv2 / aqgy5_0031_00016 / P-E / worsened

参考：-0.6
字幕：When are you coming back?
中文：你什么时候回来啊？
E：The character's emotional state is anxious, anticipation, concern, urgency, desperation.
P：The character's emotional state is anxious, anticipation, concern, curiosity.
诊断质量（并非官方分数贡献）：E=1.0，P=0.0
新增证据：Supporting links: audio: intonation rising -> act uncertain -> anxious; audio: intonation rising -> act uncertain -> care
移除证据：无

## 152. SIMSv2 / aqgy4_0021_00000 / C-P / improved

参考：-0.6
字幕：I was just casually saying, but you came up with so many excuses that made me curious.
中文：我真是随便一说，可你找了那么多借口我才开始好奇的。
P：The character's emotional state is teasing, curious.
C：The character's emotional state is curious, frustrated, annoyed, teasing, mocking.
诊断质量（并非官方分数贡献）：P=0.0，C=1.0
新增证据：无
移除证据：Emotion hypotheses: anger, disappointed, joy | Supporting links: audio: pitch variability high -> anger; text: explicit causal attribution other -> anger

## 153. SIMSv2 / aqgy5_0013_00019 / C-P / improved

参考：-1.0
字幕：I warn you, don't take my tolerance as your shameless capital.
中文：我警告你，别拿我的容忍，当成你们不要脸的资本。
P：The character's emotional state is anger, frustration, confidence, determination.
C：The character's emotional state is anger, frustration, anxiety, stress.
诊断质量（并非官方分数贡献）：P=0.0，C=1.0
新增证据：无
移除证据：Emotion hypotheses: anger, disappointed, despair | Supporting links: audio: voice tense -> anger; text: evaluation negative -> disappointed

## 154. SIMSv2 / aqgy3_0005_00042 / C-P / worsened

参考：0.6
字幕：The dog is anxious, does it look like Teacher Zeng?
中文：狗急了，长得像不像曾老师。
P：The character's emotional state is humor, mockery, ease, joy.
C：The character's emotional state is humor, mockery, relief, stress, anxiety.
诊断质量（并非官方分数贡献）：P=1.0，C=0.0
新增证据：无
移除证据：Emotion hypotheses: joy, anger, disappointed | Supporting links: visual: smile present -> joy; text: evaluation negative -> disappointed

## 155. SIMSv2 / aqgy4_0015_00000 / C-P / worsened

参考：0.8
字幕：Friends in the media circle, are they all brothers?
中文：媒体圈的朋友，都是兄弟嘛。
P：The character's emotional state is positive, humorous, curious.
C：The character's emotional state is surprised, curious.
诊断质量（并非官方分数贡献）：P=1.0，C=0.0
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, content | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 156. OVMERDPlus / sample_00000153 / A-P / improved

参考：surprised, relaxed, positive, joyful, pleasant, happy
字幕：Director Bai, you're also paying attention to this matter!
中文：
P：The character's emotional state is agreement, surprise, light-hearted, humorous.
A：The character's emotional state is agreement, surprise, happiness, engagement, positive.
诊断质量（并非官方分数贡献）：P=0.85，A=0.9
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: evaluation positive; text: intensifier present; audio: intonation rising; visual: brows raised; visual: eyes widened; visual: smile present | Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag other; certainty: act uncertain; certainty: act certain; coping potential: acp high | Emotion hypotheses: joy, hopeful, content | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 157. OVMERDPlus / sample_00000218 / A-P / improved

参考：impatient, excited, angry, dissatisfied
字幕：Isn't it thirty eight degrees that hasn't arrived yet? Thirty eight degrees is considered a fever, isn't it funny when I go here?
中文：
P：The character's emotional state is surprised, concerned, disbelief, anxiety, humor, irony.
A：The character's emotional state is anger, frustration, anxiety, confusion, amusement.
诊断质量（并非官方分数贡献）：P=0.2833333333333333，A=0.7916666666666666
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: affect word positive; text: evaluation positive; text: negation present; text: rhetorical question; audio: speech rate rel fast; audio: pitch level rel high; audio: pitch variability high; audio: intonation rising; audio: voice tense; visual: brows furrowed; visual: eyes squinted; visual: mouth corners down; visual: grimace present | Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

## 158. OVMERDPlus / sample_00000021 / A-P / worsened

参考：suspect, question, doubt
字幕：Are you really willing to be with Xiaochuan?
中文：
P：The character's emotional state is questioning, challenging, curious, focused, anxious, frustrated, angry.
A：The character's emotional state is questioning, challenging, anxiety, anger, frustration, skepticism, dissatisfaction.
诊断质量（并非官方分数贡献）：P=0.75，A=0.74
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: intensifier present; text: rhetorical question; text: desire need; audio: speech rate rel slow; audio: pitch variability low; audio: intonation falling; visual: brows raised; visual: eyes widened | Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low | Emotion hypotheses: hopeful, joy, delightful | Supporting links: visual: brows raised -> joy; visual: brows raised -> hopeful

## 159. OVMERDPlus / sample_00000039 / A-P / worsened

参考：angry, mad
字幕：I tell you, Cao Xiaoqiang, I am marrying you now.
中文：
P：The character's emotional state is humorous, teasing, sarcastic, joking.
A：The character's emotional state is joking, teasing, ironic, amusing, tension, excitement, determination.
诊断质量（并非官方分数贡献）：P=0.6，A=0.45
新增证据：无
移除证据：Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them. | Observed cues: text: desire need; audio: pitch variability high; audio: intonation rising; visual: brows raised; visual: eyes widened | Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

## 160. OVMERDPlus / sample_00000021 / C-B / improved

参考：suspect, question, doubt
字幕：Are you really willing to be with Xiaochuan?
中文：
B：The character's emotional state is questioning, challenging, curious, focused, tense, anxious, dissatisfaction, discontent, unhappiness.
C：The character's emotional state is questioning, challenging, curious, focused, tense, frustrated, irritable, questioning, evaluating.
诊断质量（并非官方分数贡献）：B=0.6399999999999999，C=0.7333333333333333
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low
移除证据：无

## 161. OVMERDPlus / sample_00000039 / C-B / improved

参考：angry, mad
字幕：I tell you, Cao Xiaoqiang, I am marrying you now.
中文：
B：The character's emotional state is joking, teasing, ironic, humorous, positive.
C：The character's emotional state is humorous, teasing, sarcastic, joking.
诊断质量（并非官方分数贡献）：B=0.45，C=0.6
新增证据：Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low
移除证据：无

## 162. OVMERDPlus / sample_00000068 / C-B / worsened

参考：unease, anxiety, worry, fear, sadness, nervousness
字幕：The Fang's family can't sweep me out of the house.
中文：
B：The character's emotional state is anger, helplessness, frustration, powerlessness.
C：The character's emotional state is anger, frustration.
诊断质量（并非官方分数贡献）：B=0.4833333333333332，C=0.26666666666666666
新增证据：Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high
移除证据：无

## 163. OVMERDPlus / sample_00000153 / C-B / worsened

参考：surprised, relaxed, positive, joyful, pleasant, happy
字幕：Director Bai, you're also paying attention to this matter!
中文：
B：The character's emotional state is agreement, surprise, happiness, engagement, interest.
C：The character's emotional state is agreement, surprise, light-hearted, humorous.
诊断质量（并非官方分数贡献）：B=0.9，C=0.85
新增证据：Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag other; certainty: act uncertain; certainty: act certain; coping potential: acp high
移除证据：无

## 164. OVMERDPlus / sample_00000021 / E-C / improved

参考：suspect, question, doubt
字幕：Are you really willing to be with Xiaochuan?
中文：
C：The character's emotional state is questioning, challenging, curious, focused, tense, frustrated, irritable, questioning, evaluating.
E：The character's emotional state is questioning, challenging, curious, focused, anxious, frustrated, angry.
诊断质量（并非官方分数贡献）：C=0.7333333333333333，E=0.75
新增证据：Emotion hypotheses: hopeful, joy, delightful
移除证据：无

## 165. OVMERDPlus / sample_00000068 / E-C / improved

参考：unease, anxiety, worry, fear, sadness, nervousness
字幕：The Fang's family can't sweep me out of the house.
中文：
C：The character's emotional state is anger, frustration.
E：The character's emotional state is anger, helplessness, frustration, powerlessness.
诊断质量（并非官方分数贡献）：C=0.26666666666666666，E=0.4833333333333332
新增证据：Emotion hypotheses: disappointed, anger, despair
移除证据：无

## 166. OVMERDPlus / sample_00000294 / E-C / worsened

参考：relax, joyful, positive, happy
字幕：A few days ago, didn't you introduce a potential partner to him?
中文：
C：The character's emotional state is expectation, concern, tension, anxiety, happiness, positivity, satisfaction, comfort.
E：The character's emotional state is expectation, concern, tension, excitement, joy, happiness, satisfaction, nervousness.
诊断质量（并非官方分数贡献）：C=0.7666666666666666，E=0.7333333333333333
新增证据：Emotion hypotheses: joy, hopeful, content
移除证据：无

## 167. OVMERDPlus / sample_00000346 / E-C / worsened

参考：concerned, negative, worried
字幕：Which one do you want, the child or the woman?
中文：
C：The character's emotional state is questioning, challenging, confused, anxious, stressed.
E：The character's emotional state is questioning, challenging, confused, uncertain.
诊断质量（并非官方分数贡献）：C=0.7166666666666666，E=0.4333333333333333
新增证据：Emotion hypotheses: disappointed, anger, depressed
移除证据：无

## 168. OVMERDPlus / sample_00000648 / P-E / improved

参考：angry, dissatisfied
字幕：Don't talk to me about feelings anymore.
中文：
E：The character's emotional state is anger, disappointment.
P：The character's emotional state is anger, frustration, emotional distress.
诊断质量（并非官方分数贡献）：E=0.9，P=1.0
新增证据：Supporting links: audio: voice tense -> anger; audio: vocal intensity rel high -> anger
移除证据：无

## 169. OVMERDPlus / sample_00000956 / P-E / improved

参考：surprised
字幕：You've been in love since you were in the hospital these past few days
中文：
E：The character's emotional state is teasing, lighthearted, humorous, calm, contemplative.
P：The character's emotional state is concerned, curious.
诊断质量（并非官方分数贡献）：E=0.0，P=0.1875
新增证据：Supporting links: text: affect word positive -> joy; visual: brows raised -> joy
移除证据：无

## 170. OVMERDPlus / sample_00000294 / P-E / worsened

参考：relax, joyful, positive, happy
字幕：A few days ago, didn't you introduce a potential partner to him?
中文：
E：The character's emotional state is expectation, concern, tension, excitement, joy, happiness, satisfaction, nervousness.
P：The character's emotional state is expectation, dissatisfaction.
诊断质量（并非官方分数贡献）：E=0.7333333333333333，P=0.6
新增证据：Supporting links: visual: smile present -> joy; visual: smile present -> hopeful
移除证据：无

## 171. OVMERDPlus / sample_00000346 / P-E / worsened

参考：concerned, negative, worried
字幕：Which one do you want, the child or the woman?
中文：
E：The character's emotional state is questioning, challenging, confused, uncertain.
P：The character's emotional state is questioning, challenging, confusion, frustration, contemplation, curiosity.
诊断质量（并非官方分数贡献）：E=0.4333333333333333，P=0.3
新增证据：Supporting links: visual: mouth corners down -> disappointed; visual: brows furrowed -> anger
移除证据：无

## 172. OVMERDPlus / sample_00000294 / C-P / improved

参考：relax, joyful, positive, happy
字幕：A few days ago, didn't you introduce a potential partner to him?
中文：
P：The character's emotional state is expectation, dissatisfaction.
C：The character's emotional state is expectation, concern, tension, anxiety, happiness, positivity, satisfaction, comfort.
诊断质量（并非官方分数贡献）：P=0.6，C=0.7666666666666666
新增证据：无
移除证据：Emotion hypotheses: joy, hopeful, content | Supporting links: visual: smile present -> joy; visual: smile present -> hopeful

## 173. OVMERDPlus / sample_00000346 / C-P / improved

参考：concerned, negative, worried
字幕：Which one do you want, the child or the woman?
中文：
P：The character's emotional state is questioning, challenging, confusion, frustration, contemplation, curiosity.
C：The character's emotional state is questioning, challenging, confused, anxious, stressed.
诊断质量（并非官方分数贡献）：P=0.3，C=0.7166666666666666
新增证据：无
移除证据：Emotion hypotheses: disappointed, anger, depressed | Supporting links: visual: mouth corners down -> disappointed; visual: brows furrowed -> anger

## 174. OVMERDPlus / sample_00000021 / C-P / worsened

参考：suspect, question, doubt
字幕：Are you really willing to be with Xiaochuan?
中文：
P：The character's emotional state is questioning, challenging, curious, focused, anxious, frustrated, angry.
C：The character's emotional state is questioning, challenging, curious, focused, tense, frustrated, irritable, questioning, evaluating.
诊断质量（并非官方分数贡献）：P=0.75，C=0.7333333333333333
新增证据：无
移除证据：Emotion hypotheses: hopeful, joy, delightful | Supporting links: visual: brows raised -> joy; visual: brows raised -> hopeful

## 175. OVMERDPlus / sample_00000068 / C-P / worsened

参考：unease, anxiety, worry, fear, sadness, nervousness
字幕：The Fang's family can't sweep me out of the house.
中文：
P：The character's emotional state is anger, helplessness, frustration, powerlessness.
C：The character's emotional state is anger, frustration.
诊断质量（并非官方分数贡献）：P=0.4833333333333332，C=0.26666666666666666
新增证据：无
移除证据：Emotion hypotheses: disappointed, anger, despair | Supporting links: text: evaluation negative -> disappointed; text: evaluation negative -> anger

