# 开发集详细诊断（确认实验尚未完成）

案例依据数据集标签、字幕与模型输出定位差异，未额外人工复核音视频，不据此推断具体图边的因果错误。

|权重|组|任务|平均抽取标签数|平均回答词数|
|---|---|---|---:|---:|
|original_epoch40|A|MER_track1_discrete|3.145|8.28|
|original_epoch40|A|MER_OV|3.474|8.57|
|original_epoch40|B|MER_track1_discrete|3.312|11.98|
|original_epoch40|B|MER_OV|3.271|15.72|
|original_epoch40|C|MER_track1_discrete|3.694|12.74|
|original_epoch40|C|MER_OV|3.859|12.24|
|original_epoch40|S|MER_track1_discrete|3.704|11.72|
|original_epoch40|S|MER_OV|3.930|15.29|
|original_epoch40|P|MER_track1_discrete|3.456|14.09|
|original_epoch40|P|MER_OV|3.578|13.15|
|fixed_graph45_to54|A|MER_track1_discrete|3.542|8.77|
|fixed_graph45_to54|A|MER_OV|3.815|8.97|
|fixed_graph45_to54|B|MER_track1_discrete|3.475|8.72|
|fixed_graph45_to54|B|MER_OV|3.841|9.09|
|fixed_graph45_to54|C|MER_track1_discrete|3.510|8.74|
|fixed_graph45_to54|C|MER_OV|3.682|9.10|
|fixed_graph45_to54|S|MER_track1_discrete|3.496|8.71|
|fixed_graph45_to54|S|MER_OV|3.708|9.15|
|fixed_graph45_to54|P|MER_track1_discrete|3.514|8.73|
|fixed_graph45_to54|P|MER_OV|3.690|9.09|

## original_epoch40 C 对 original_epoch40 S

### sample_00005537 / harmed / 标签 happy

咱们两个人一人一杯奶茶，再来一盒甜甜圈。
Let's each have a cup of milk tea and also get a box of donuts.
三种子平均逐样本HIT差值：-66.667百分点。
- seed 42: 当前回答：In the text, the caption reads: "Let's have a cup of milk tea and a box of doughnuts each." This sentence might be a suggestion or plan proposed by a female character to someone else. Given the visual clues in the video, such as the female character's head lowered and her expression of looking down, and the audio clues describing the speaker feeling tense or anxious, we can infer that this sentence might be how the female character is asking asking for or suggesting something, possibly with a certain emotional weight. The sentence may reflect the female character's desire for a special drink and treat, possibly to change her mood or improve her feelings.；参照回答：The character's emotional state is excited, joyful.。
- seed 2026: 当前回答：；参照回答：The character's emotional state is excited, anticipating, uncertain, confident, relaxed.。
- seed 2027: 当前回答：In the text, the caption reads: "Let's have a cup of milk tea and also a box of pastries." This sentence suggests that the individual has a positive attitude and desire towards food and drink, which is consistent with the relaxed and positive emotions described in the audio cues. At the same time, the woman's's lip-closing and head-lowering posture in the video clues may indicate that she is considering or pondering something, so this sentence could be a suggestion or proposal she is making to herself or others. Overall, this sentence expresses the individual's's love for food and drink, as well as her active participation in social activities.；参照回答：In the text, the caption reads: "Let's have a cup of milk tea and a box of donuts." This sentence might be spoken by a female speaker suggesting or proposing to someone or a group. Given the emotional cues described in the audio, such as personal desire or need, and the visual hints showing the woman lowering her head with her lips together, we can infer that this sentence may carry a casual or cheerful tone. The woman might be expressing her interest or proposing an idea that alignss with the emotional state described in the audio clues.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: desire need; audio: intonation rising; visual: lips pressed; visual: head lowered
Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag other; certainty: act uncertain; coping potential: acp high; coping potential: acp low

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: desire need; audio: intonation rising; visual: lips pressed; visual: head lowered
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; coping potential: acp low; coping potential: acp high

### samplenew_00010887 / harmed / 标签 angry

我走了，你陪他？
I'm leaving, will you stay with him?
三种子平均逐样本HIT差值：-66.667百分点。
- seed 42: 当前回答：The character's emotional state is anxiety, high pressure, overwhelmed, anger, sadness, uncertainty, confusion.；参照回答：The character's emotional state is anxiety, high pressure, overwhelmed, anger, sadness, uncertainty, confusion.。
- seed 2026: 当前回答：；参照回答：The character's emotional state is uncertain, concerned, angry.。
- seed 2027: 当前回答：；参照回答：The character's emotional state is sadness, anger, determination.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: desire need; audio: pitch level rel high; audio: vocal intensity rel high; audio: pitch variability high; audio: intonation rising; visual: brows furrowed; visual: brows raised; visual: eyes widened; visual: mouth corners down
Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: desire need; audio: pitch level rel high; audio: vocal intensity rel high; audio: pitch variability high; audio: intonation rising; visual: brows furrowed; visual: brows raised; visual: eyes widened; visual: mouth corners down
Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

### sample_00004630 / harmed / 标签 worried

华仔，你真的爱叶莎莎吗？
Wah Zai, do you really love Ye Sha Sha?
三种子平均逐样本HIT差值：-46.667百分点。
- seed 42: 当前回答：The character's emotional state is excited, enthusiastic.；参照回答：The character's emotional state is excited, enthusiastic, amused.。
- seed 2026: 当前回答：The character's emotional state is excited, anticipating, tense.；参照回答：The character's emotional state is excited, anticipating, mixed anxiety and surprise.。
- seed 2027: 当前回答：The character's emotional state is positive, strong emotional state, uncertain.；参照回答：The character's emotional state is positive, strong emotional state, uncertain emotional state.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word positive; text: intensifier present; text: rhetorical question; audio: intonation rising; visual: brows raised; visual: eyes widened; visual: smile present
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word positive; text: intensifier present; text: rhetorical question; audio: intonation rising; visual: brows raised; visual: eyes widened; visual: smile present
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

### sample_00005425 / improved / 标签 worried

小姐真的非常不好意思。
I'm really very sorry, miss.
三种子平均逐样本HIT差值：86.667百分点。
- seed 42: 当前回答：The character's emotional state is contrition, regret, remorse, guilt, apology, tension, anxiety, stress.；参照回答：The character's emotional state is contrition, regret, guilt, remorse, sadness, melancholy.。
- seed 2026: 当前回答：The character's emotional state can be inferred to be apologetic, regretful, anxious, tense, stressed, depressed.；参照回答：The character's emotional state is regret, apology, disappointment.。
- seed 2027: 当前回答：The character's emotional state is sorry, apologetic, regretful, guilty, anxious, tense, uncertain, sad, disappointed.；参照回答：The character's emotional state is sorry, sad.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word negative; text: intensifier present; audio: speech rate rel slow; audio: intonation rising; visual: mouth corners down
Appraisal hypotheses: goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag circumstance; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp low

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word negative; text: intensifier present; audio: speech rate rel slow; audio: intonation rising; visual: mouth corners down
Appraisal hypotheses: goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag other; certainty: act uncertain; certainty: act certain; coping potential: acp high

### samplenew_00037990 / improved / 标签 angry

我想你，你小佝偻你什么意思啊？我告诉你，你不动我也不动，我看咱俩谁能耗得过谁？我突然明白了。
I miss you, what do you mean by your hunchback? Let me tell you, if you don't move, I won't move either. Let's see who can outlast the other? I suddenly understand now.
三种子平均逐样本HIT差值：66.667百分点。
- seed 42: 当前回答：The character's emotional state is anger, frustration.；参照回答：The character's emotional state is anger, frustration, anxiety, irritability, helplessness, pressure.。
- seed 2026: 当前回答：The character's emotional state is anger, frustration, anxiety.；参照回答：。
- seed 2027: 当前回答：The character's emotional state is anger, frustration, annoyance.；参照回答：。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word negative; text: evaluation negative; text: negation present; text: rhetorical question; text: exclamation interjection; text: desire need; audio: speech rate rel fast; audio: pitch level rel high; audio: vocal intensity rel high; audio: pitch variability high; audio: intonation rising; audio: voice tense; audio: laughter present; visual: brows raised; visual: eyes widened
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word negative; text: evaluation negative; text: negation present; text: rhetorical question; text: exclamation interjection; text: desire need; audio: speech rate rel fast; audio: pitch level rel high; audio: vocal intensity rel high; audio: pitch variability high; audio: intonation rising; audio: voice tense; audio: laughter present; visual: brows raised; visual: eyes widened
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

### samplenew_00045677 / improved / 标签 sad

一直都知道肖晨喜欢我，我从来都没有回应过他
I've always known that Xiao Chen likes me, but I've never responded to him.
三种子平均逐样本HIT差值：40.000百分点。
- seed 42: 当前回答：The character's emotional state is sadness, anxiety, uncertainty.；参照回答：The character's emotional state is confused, conflicted, contemplative, emotionally fragile.。
- seed 2026: 当前回答：The character's emotional state is uncertain, conflicted, sorrowful, defeated, reflective, thoughtful.；参照回答：The character's emotional state is confused, disappointed, uncertain.。
- seed 2027: 当前回答：The character's emotional state is sadness, self-doubt, uncertainty.；参照回答：The character's emotional state is sadness, self-doubt, uncertainty.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word positive; text: evaluation positive; text: negation present; text: contrast present; audio: speech rate rel slow; audio: pitch level rel low; audio: vocal intensity rel low; audio: pitch variability low; audio: pause long; audio: intonation falling; audio: intonation flat; audio: voice trembling; visual: mouth corners down; visual: head lowered
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word positive; text: evaluation positive; text: negation present; text: contrast present; audio: speech rate rel slow; audio: pitch level rel low; audio: vocal intensity rel low; audio: pitch variability low; audio: pause long; audio: intonation falling; audio: intonation flat; audio: voice trembling; visual: mouth corners down; visual: head lowered
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high; coping potential: acp low

## fixed_graph45_to54 C 对 fixed_graph45_to54 S

### samplenew_00020732 / harmed / 标签 sad

可是又能怎么样呢？我们也只能，微笑着去接受它。
But what can we do? We can only accept it with a smile.
三种子平均逐样本HIT差值：-53.333百分点。
- seed 42: 当前回答：The character's emotional state is helplessness, optimism, contemplative, reflective, facing challenges, choosing to accept and cope positively.；参照回答：The character's emotional state is helplessness, optimism, contemplative, sorrowful, humorous, sarcastic.。
- seed 2026: 当前回答：The character's emotional state is helplessness, resignation, contemplation, reflection, stress.；参照回答：The character's emotional state is helplessness, resignation, sorrow.。
- seed 2027: 当前回答：The character's emotional state is helplessness, optimism, acceptance.；参照回答：The character's emotional state is helplessness, optimism, acceptance.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word positive; text: evaluation positive; text: negation present; text: contrast present; text: rhetorical question; audio: speech rate rel slow; audio: vocal intensity rel low; audio: pitch variability low; audio: pause long; audio: intonation falling; audio: intonation flat; visual: brows raised; visual: eyes widened
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word positive; text: evaluation positive; text: negation present; text: contrast present; text: rhetorical question; audio: speech rate rel slow; audio: vocal intensity rel low; audio: pitch variability low; audio: pause long; audio: intonation falling; audio: intonation flat; visual: brows raised; visual: eyes widened
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc mixed; goal congruence: agc incongruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

### sample_00001671 / harmed / 标签 happy

你老婆怎么敢嫁给你，说你没生活来源
How could your wife dare to marry you, saying you have no source of livelihood?
三种子平均逐样本HIT差值：-40.000百分点。
- seed 42: 当前回答：The character's emotional state is playful, teasing, amused.；参照回答：The character's emotional state is playful, teasing, positive.。
- seed 2026: 当前回答：The character's emotional state is excited, amused, teasing, positive.；参照回答：The character's emotional state is excited, amused, teasing, positive.。
- seed 2027: 当前回答：The character's emotional state is teasing, mocking, humorous.；参照回答：The character's emotional state is teasing, mocking, humorous, positive.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation negative; text: negation present; text: rhetorical question; audio: intonation rising; audio: laughter present; visual: brows raised; visual: eyes squinted; visual: smile present
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation negative; text: negation present; text: rhetorical question; audio: intonation rising; audio: laughter present; visual: brows raised; visual: eyes squinted; visual: smile present
Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high; coping potential: acp low

### sample_00005291 / harmed / 标签 worried

好姑娘多着呢，咱慢慢找，行吗？
There are many good girls, can we take our time to find one?
三种子平均逐样本HIT差值：-33.333百分点。
- seed 42: 当前回答：The character's emotional state is anxiety, irritability, frustration, hopelessness, encouragement, hope.；参照回答：The character's emotional state is anxiety, irritability, frustration, hopelessness, encouragement, hope.。
- seed 2026: 当前回答：The character's emotional state is urgency, frustration, disappointment.；参照回答：The character's emotional state is urgency, frustration, disappointment.。
- seed 2027: 当前回答：The character's emotional state is urgent, emotional, sad, hopeful, confident.；参照回答：The character's emotional state is urgent, anxious, sad, disappointed.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation positive; text: intensifier present; text: desire need; audio: speech rate rel slow; audio: pitch variability low; audio: intonation falling; visual: brows furrowed; visual: eyes squinted; visual: mouth corners down; visual: grimace present
Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation positive; text: intensifier present; text: desire need; audio: speech rate rel slow; audio: pitch variability low; audio: intonation falling; visual: brows furrowed; visual: eyes squinted; visual: mouth corners down; visual: grimace present
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

### sample_00000065 / improved / 标签 worried

收到。继续监视，注意隐蔽啊。
Received. Continue monitoring and stay concealed.
三种子平均逐样本HIT差值：26.667百分点。
- seed 42: 当前回答：The character's emotional state is serious, focused, calm, satisfied, fear, anxiety, tension, stress.；参照回答：The character's emotional state is serious, focused, calm, confident, tense, urgent.。
- seed 2026: 当前回答：The character's emotional state is neutral, authoritative, professional.；参照回答：The character's emotional state is neutral, authoritative, professional.。
- seed 2027: 当前回答：The character's emotional state is neutral, cool.；参照回答：The character's emotional state is neutral, cool.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: exclamation interjection; audio: pitch variability low; audio: intonation falling; visual: eyes widened
Appraisal hypotheses: goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: exclamation interjection; audio: pitch variability low; audio: intonation falling; visual: eyes widened
Appraisal hypotheses: goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag other; certainty: act uncertain; certainty: act certain; coping potential: acp high

### sample_00001978 / improved / 标签 angry

我看你这几天就不对劲，你他妈吃错药啦?
I've noticed something off about you these past few days, did you take the wrong medication or something?
三种子平均逐样本HIT差值：20.000百分点。
- seed 42: 当前回答：The character's emotional state is questioning, concern, negative.；参照回答：The character's emotional state is questioning, concern, negative.。
- seed 2026: 当前回答：The character's emotional state is questioning, observation, negative.；参照回答：The character's emotional state is questioning, observation, negative.。
- seed 2027: 当前回答：The character's emotional state is questioning, concern, suspicion.；参照回答：The character's emotional state is questioning, concern, worry, dissatisfaction.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word negative; text: evaluation negative; text: rhetorical question; text: explicit causal attribution other; audio: speech rate rel fast; audio: pitch level rel high; audio: vocal intensity rel high; audio: pitch variability high; audio: intonation rising; audio: intonation falling; audio: voice tense; visual: brows furrowed; visual: lips pressed
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word negative; text: evaluation negative; text: rhetorical question; text: explicit causal attribution other; audio: speech rate rel fast; audio: pitch level rel high; audio: vocal intensity rel high; audio: pitch variability high; audio: intonation rising; audio: intonation falling; audio: voice tense; visual: brows furrowed; visual: lips pressed
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

### samplenew_00063053 / improved / 标签 happy

刘星二号，瞧这名字，多么像杂交小麦啊
Liu Xing No.2, look at this name, it's so much like a hybrid wheat.
三种子平均逐样本HIT差值：13.333百分点。
- seed 42: 当前回答：The character's emotional state is excited, amused, joyful.；参照回答：The character's emotional state is excited, amused, joyful.。
- seed 2026: 当前回答：The character's emotional state is humorous, amused, positive.；参照回答：The character's emotional state is humorous, amused, positive.。
- seed 2027: 当前回答：The character's emotional state is humorous, playful, positive.；参照回答：The character's emotional state is humorous, playful, amused.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation positive; text: intensifier present; text: exclamation interjection; audio: speech rate rel slow; audio: pitch level rel high; audio: pitch variability high; audio: intonation rising; audio: laughter present; visual: brows raised; visual: eyes widened; visual: eyes squinted; visual: smile present
Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation positive; text: intensifier present; text: exclamation interjection; audio: speech rate rel slow; audio: pitch level rel high; audio: pitch variability high; audio: intonation rising; audio: laughter present; visual: brows raised; visual: eyes widened; visual: eyes squinted; visual: smile present
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

## fixed_graph45_to54 C 对 fixed_graph45_to54 A

### sample_00001747 / harmed / 标签 sad

我真的需要人帮我，我知道你是个好人。
I really need someone to help me, I know you are a good person.
三种子平均逐样本HIT差值：-66.667百分点。
- seed 42: 当前回答：The character's emotional state is distress, anxiety, hope.；参照回答：The character's emotional state is distress, plea for help, sadness, despair, hope.。
- seed 2026: 当前回答：The character's emotional state is distress, plea for help, sadness, despair, hope.；参照回答：The character's emotional state is distress, plea for help, sadness, distress, longing for assistance.。
- seed 2027: 当前回答：The character's emotional state is distress, urgency, emotional need, desire for support.；参照回答：The character's emotional state is sadness, distress, need for help.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation positive; text: intensifier present; text: desire need; audio: speech rate rel slow; audio: pitch level rel low; audio: vocal intensity rel low; audio: pitch variability high; audio: pause long; audio: intonation falling; audio: voice tense; audio: voice trembling; audio: crying sobbing present; visual: mouth corners down; visual: head lowered
Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag other; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation positive; text: intensifier present; text: desire need; audio: speech rate rel slow; audio: pitch level rel low; audio: vocal intensity rel low; audio: pitch variability high; audio: pause long; audio: intonation falling; audio: voice tense; audio: voice trembling; audio: crying sobbing present; visual: mouth corners down; visual: head lowered
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

### sample_00005668 / harmed / 标签 angry

你，你能不能不闹了你啊?
You, can you stop making trouble?
三种子平均逐样本HIT差值：-66.667百分点。
- seed 42: 当前回答：The character's emotional state is fear, anxiety, tension, dissatisfaction, disturbance.；参照回答：The character's emotional state is fear, anxiety, tension, overwhelm, pressure, negative sentiment, anger, dissatisfaction.。
- seed 2026: 当前回答：The character's emotional state is dissatisfaction, frustration, anxiety.；参照回答：The character's emotional state is dissatisfaction, frustration, anxiety.。
- seed 2027: 当前回答：The character's emotional state is fear, anxiety, stress, emotional distress, dissatisfaction.；参照回答：The character's emotional state is fear, anxiety, stress, fear, anger, frustration.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word negative; text: evaluation negative; text: negation present; text: rhetorical question; text: exclamation interjection; text: desire need; audio: speech rate rel slow; audio: vocal intensity rel low; audio: pause long; audio: intonation rising; audio: voice tense; visual: brows furrowed; visual: mouth corners down; visual: head lowered
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word negative; text: evaluation negative; text: negation present; text: rhetorical question; text: exclamation interjection; text: desire need; audio: speech rate rel slow; audio: vocal intensity rel low; audio: pause long; audio: intonation rising; audio: voice tense; visual: brows furrowed; visual: mouth corners down; visual: head lowered
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

### sample_00006803 / harmed / 标签 worried

我猜跟她平时自尊心强有关，你看她过得多光鲜，她可能不希望我们看到她
I guess it's related to her strong self-esteem usually, you see how glamorous she is, she probably doesn't want us to see her.
三种子平均逐样本HIT差值：-60.000百分点。
- seed 42: 当前回答：The character's emotional state is disapproval, misunderstanding, negative, anger, frustration.；参照回答：The character's emotional state is disapproval, negativity, dissatisfaction, confusion, anxiety, stress.。
- seed 2026: 当前回答：The character's emotional state is disapproval, negativity, discomfort, overwhelm.；参照回答：The character's emotional state is disapproval, secrecy, concern.。
- seed 2027: 当前回答：The character's emotional state is speculation, disdain.；参照回答：The character's emotional state is speculation, evaluation.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation positive; text: evaluation negative; text: negation present; text: intensifier present; text: uncertainty hedge; text: explicit causal attribution other; audio: speech rate rel slow; audio: vocal intensity rel low; audio: pitch variability low; audio: pause long; audio: intonation falling; audio: intonation flat; visual: brows furrowed; visual: eyes squinted; visual: mouth corners down; visual: head lowered
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high
Text contains mixed affect; overall polarity is unresolved.

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation positive; text: evaluation negative; text: negation present; text: intensifier present; text: uncertainty hedge; text: explicit causal attribution other; audio: speech rate rel slow; audio: vocal intensity rel low; audio: pitch variability low; audio: pause long; audio: intonation falling; audio: intonation flat; visual: brows furrowed; visual: eyes squinted; visual: mouth corners down; visual: head lowered
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high
Text contains mixed affect; overall polarity is unresolved.

### sample_00000099 / improved / 标签 angry

有洗澡玩游戏的吗？你手机防水的？
Is there any game to play while bathing? Is your phone waterproof?
三种子平均逐样本HIT差值：46.667百分点。
- seed 42: 当前回答：The character's emotional state is excited, interested.；参照回答：The character's emotional state is excited, interested.。
- seed 2026: 当前回答：The character's emotional state is excited, interested, teasing, joking.；参照回答：The character's emotional state is excited, interested, surprised, curious.。
- seed 2027: 当前回答：The character's emotional state is excited, interested, surprised, incredulous.；参照回答：The character's emotional state is excited, interested.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: negation present; text: rhetorical question; audio: pitch variability high; audio: intonation rising; visual: brows raised; visual: eyes widened
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: negation present; text: rhetorical question; audio: pitch variability high; audio: intonation rising; visual: brows raised; visual: eyes widened
Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high; coping potential: acp low

### sample_00005537 / improved / 标签 happy

咱们两个人一人一杯奶茶，再来一盒甜甜圈。
Let's each have a cup of milk tea and also get a box of donuts.
三种子平均逐样本HIT差值：40.000百分点。
- seed 42: 当前回答：The character's emotional state is enthusiastic, excited, joyful, satisfied, content, positive.；参照回答：The character's emotional state is excited, enthusiastic.。
- seed 2026: 当前回答：The character's emotional state is excited, anticipating, positive.；参照回答：The character's emotional state is excited, anticipating, positive.。
- seed 2027: 当前回答：The character's emotional state is excited, anticipatory, happy, satisfied.；参照回答：The character's emotional state is excited, anticipatory.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: desire need; audio: intonation rising; visual: lips pressed; visual: head lowered
Appraisal hypotheses: goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag other; certainty: act uncertain; coping potential: acp high; coping potential: acp low

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: desire need; audio: intonation rising; visual: lips pressed; visual: head lowered
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; coping potential: acp low; coping potential: acp high

### sample_00004710 / improved / 标签 worried

唉，你都找了这么多年了，放弃哪有那么容易啊？你真的能放弃吗？
Ah, you've been searching for so many years, how can it be so easy to give up? Can you really give up?
三种子平均逐样本HIT差值：40.000百分点。
- seed 42: 当前回答：The character's emotional state is concern, doubt, anxiety, uncertainty, frustration.；参照回答：The character's emotional state is concern, doubt, anxiety, stress, frustration.。
- seed 2026: 当前回答：The character's emotional state is dissatisfaction, disappointment, anxiety.；参照回答：The character's emotional state is dissatisfaction, disappointment, frustration.。
- seed 2027: 当前回答：The character's emotional state is disappointment, discontent, anxiety.；参照回答：The character's emotional state is disappointment, dissatisfaction, frustration.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word negative; text: evaluation negative; text: negation present; text: intensifier present; text: rhetorical question; text: exclamation interjection; audio: speech rate rel slow; audio: vocal intensity rel low; audio: pitch variability low; audio: pause long; audio: intonation rising; audio: intonation falling; audio: intonation flat; visual: brows furrowed; visual: eyes widened; visual: mouth corners down
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc mixed; expectedness: aex unexpected; expectedness: aex expected; agency: aag self; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: affect word negative; text: evaluation negative; text: negation present; text: intensifier present; text: rhetorical question; text: exclamation interjection; audio: speech rate rel slow; audio: vocal intensity rel low; audio: pitch variability low; audio: pause long; audio: intonation rising; audio: intonation falling; audio: intonation flat; visual: brows furrowed; visual: eyes widened; visual: mouth corners down
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

## fixed_graph45_to54 A 对 original_epoch40 A

### samplenew_00019650 / harmed / 标签 sad

不说这些，快点好起来。
Stop talking about these, get better soon.
三种子平均逐样本HIT差值：-100.000百分点。
- seed 42: 当前回答：The character's emotional state is concern, blessing, comfort.；参照回答：The character's emotional state is concern, blessing, sadness.。
- seed 2026: 当前回答：The character's emotional state is concern, worry, panic.；参照回答：The character's emotional state is concern, blessing, sadness.。
- seed 2027: 当前回答：The character's emotional state is concern, blessing, worry, care.；参照回答：The character's emotional state is sadness, anger, despair.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation positive; text: negation present; text: desire need; audio: speech rate rel slow; audio: vocal intensity rel low; audio: pitch variability low; audio: pause long; audio: intonation falling; visual: brows raised; visual: eyes widened; visual: smile present
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high; coping potential: acp low

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation positive; text: negation present; text: desire need; audio: speech rate rel slow; audio: vocal intensity rel low; audio: pitch variability low; audio: pause long; audio: intonation falling; visual: brows raised; visual: eyes widened; visual: smile present
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp high; coping potential: acp low

### sample_00003853 / harmed / 标签 worried

小智啊，他是单亲，他妈妈从来都没有陪他过过生日和儿童节。
Xiao Zhi, he is from a single-parent family, his mother has never celebrated his birthday or Children's Day with him.
三种子平均逐样本HIT差值：-66.667百分点。
- seed 42: 当前回答：The character's emotional state is sad, frustrated.；参照回答：The character's emotional state is sadness, despair, helplessness, emotional turmoil, stress.。
- seed 2026: 当前回答：The character's emotional state is sad, disappointed, angry.；参照回答：The character's emotional state is sad, disappointed, angry.。
- seed 2027: 当前回答：The character's emotional state is sadness, anger, frustration.；参照回答：The character's emotional state is sadness, anger, hopelessness, loneliness, stress, anxiety, worry.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: negation present; text: exclamation interjection; audio: pitch variability low; audio: intonation falling; visual: brows furrowed; visual: mouth corners down; visual: head lowered
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: negation present; text: exclamation interjection; audio: pitch variability low; audio: intonation falling; visual: brows furrowed; visual: mouth corners down; visual: head lowered
Appraisal hypotheses: goal relevance: agr irrelevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

### sample_00004903 / harmed / 标签 angry

黄兰登你什么意思？
What do you mean, Huang Landeng?
三种子平均逐样本HIT差值：-53.333百分点。
- seed 42: 当前回答：The character's emotional state is questioning, dissatisfaction.；参照回答：The character's emotional state is questioning, dissatisfaction.。
- seed 2026: 当前回答：The character's emotional state is confused, dissatisfied, frustrated.；参照回答：The character's emotional state is confused, dissatisfied, frustrated, anxious, tense, angry.。
- seed 2027: 当前回答：The character's emotional state is confused, dissatisfied, unhappy, fearful, anxious, tense.；参照回答：The character's emotional state is anger, dissatisfaction.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: audio: vocal intensity rel high; audio: intonation rising; audio: voice tense; visual: brows furrowed; visual: eyes squinted; visual: mouth corners down; visual: grimace present
Appraisal hypotheses: goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: audio: vocal intensity rel high; audio: intonation rising; audio: voice tense; visual: brows furrowed; visual: eyes squinted; visual: mouth corners down; visual: grimace present
Appraisal hypotheses: goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low

### sample_00006065 / improved / 标签 worried

搁我这儿，指不定哪天就丢了。
Leave it with me, who knows it might get lost one day.
三种子平均逐样本HIT差值：100.000百分点。
- seed 42: 当前回答：The character's emotional state is anxiety, stress, feeling overwhelmed, concerned, worried.；参照回答：The character's emotional state is comfort, assurance, availability, relaxation, contentment.。
- seed 2026: 当前回答：The character's emotional state is anxious, tense, worried.；参照回答：The character's emotional state is comfort, willingness, assurance.。
- seed 2027: 当前回答：The character's emotional state is anxious, under pressure, concerned, uncertain.；参照回答：The character's emotional state is comfort, assurance, availability.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation negative; text: uncertainty hedge; text: explicit failure loss outcome; audio: intonation rising; visual: brows raised; visual: eyes widened
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: evaluation negative; text: uncertainty hedge; text: explicit failure loss outcome; audio: intonation rising; visual: brows raised; visual: eyes widened
Appraisal hypotheses: goal relevance: agr irrelevant; goal relevance: agr relevant; goal congruence: agc incongruent; goal congruence: agc congruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act certain; certainty: act uncertain; coping potential: acp low; coping potential: acp high

### sample_00005090 / improved / 标签 happy

樊姐。
Sister Fan.
三种子平均逐样本HIT差值：86.667百分点。
- seed 42: 当前回答：The character's emotional state is content, joyful.；参照回答：The character's emotional state is neutral.。
- seed 2026: 当前回答：The character's emotional state is excited, anticipating, nervous.；参照回答：The character's emotional state is neutral.。
- seed 2027: 当前回答：The character's emotional state is peaceful, content, excited, curious.；参照回答：The character's emotional state is neutral.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: audio: intonation rising; visual: brows furrowed; visual: eyes squinted; visual: smile present; visual: grimace present
Appraisal hypotheses: goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex unexpected; expectedness: aex expected; agency: aag other; agency: aag self; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: audio: intonation rising; visual: brows furrowed; visual: eyes squinted; visual: smile present; visual: grimace present
Appraisal hypotheses: goal congruence: agc congruent; goal congruence: agc incongruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high; coping potential: acp low

### sample_00006593 / improved / 标签 angry

我离开民政局，我就一想我离开。
I left the Civil Affairs Bureau, and I just thought about my departure.
三种子平均逐样本HIT差值：73.333百分点。
- seed 42: 当前回答：The character's emotional state is frustrated, angry, overwhelmed, anxious, negative.；参照回答：The character's emotional state is anxiety, irritability, stress, dissatisfaction, worry, turmoil, inner conflict.。
- seed 2026: 当前回答：The character's emotional state is dissatisfaction, frustration, disappointment.；参照回答：The character's emotional state is anxious, tense, emotionally detached, negative, stressed, dissatisfied.。
- seed 2027: 当前回答：The character's emotional state is frustrated, angry, overwhelmed, anxious, negative.；参照回答：The character's emotional state is anxious, uneasy, tense.。

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: intensifier present; audio: speech rate rel slow; audio: intonation falling; visual: brows raised; visual: eyes widened
Appraisal hypotheses: goal congruence: agc congruent; goal congruence: agc mixed; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act certain; certainty: act uncertain; coping potential: acp high; coping potential: acp low

Evidence hypotheses; associations are not probabilities. Use current media to accept or reject them.
Observed cues: text: intensifier present; audio: speech rate rel slow; audio: intonation falling; visual: brows raised; visual: eyes widened
Appraisal hypotheses: goal congruence: agc mixed; goal congruence: agc congruent; expectedness: aex expected; expectedness: aex unexpected; agency: aag self; agency: aag circumstance; certainty: act uncertain; certainty: act certain; coping potential: acp low; coping potential: acp high
