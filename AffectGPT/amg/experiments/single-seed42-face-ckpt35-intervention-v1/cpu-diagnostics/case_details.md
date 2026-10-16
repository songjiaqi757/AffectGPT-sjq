# 112条逐样本文本证据

仅文本审查，未进行视频盲审。F1及TP/FP/FN直接引用既有评分。邻居文本仅供离线诊断，不是模型Memory输入。所有“候选”均未加入词表、未用于重算分数。

## 1. samplenew3_00001134｜decline｜ΔF1 -1.000000

gold：anxiety, concern, nervousness

query字幕：Why can't you rest assured?

源标注描述：In the text, the subtitle content "Why can't you rest assured" based on the description of the man's serious facial expression and tightly clasped hands in the video clues, as well as the method mentioned in the audio clues to analyze emotions through sound clues, we can infer that this sentence may be the man expressing his concerns or uneasiness. The man's serious expression and tightly clasped hands may indicate that he is experiencing an anxious or nervous emotional state. Therefore, this sentence may be his expression of concern about a certain issue or situation.

off原始输出：The character's emotional state is anxious, nervous, concerned.

retrieval原始输出：The character's emotional state is worry, unease.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, concern, nervousness|1.000000|3|0|0|
|retrieval|unease, worry|0.000000|0|2|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由1.000000变为0.000000，差值-1.000000。
- TP变化-3，FP变化+2，FN变化+3。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：anxiety, concern, nervousness。
- 相对off新增未精确匹配gold的标签：unease, worry。

gate：0.119937718；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "unease", "unmatched_gold_label": "anxiety"}, {"prediction_label": "unease", "unmatched_gold_label": "concern"}, {"prediction_label": "unease", "unmatched_gold_label": "nervousness"}, {"prediction_label": "worry", "unmatched_gold_label": "anxiety"}, {"prediction_label": "worry", "unmatched_gold_label": "concern"}, {"prediction_label": "worry", "unmatched_gold_label": "nervousness"}]}

实际5近邻证据：

### 近邻1：samplenew3_00012986

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction, frustration, urgency
- 与query gold精确词面重合：∅
- 字幕：I have already requested to see you three times, but you have been blocking me. Please inform the Prime Minister that I also have important matters to discuss.
- 描述：In the text, the subtitle reads: "I have requested an audience three times, but you have always blocked me. Please inform the Prime Minister that I also have important matters." This sentence indicates that the speaker has tried multiple times to meet with someone but has been consistently blocked. Based on the audio clues describing the individual's feelings of anxiety, frustration, and urgency, as well as the video clues of the man's facial expression and body language showing confusion and impatience, we can infer that this sentence may carry a sense of urgency and dissatisfaction. The speaker may feel that being obstructed is highly unfair and is frustrated and angry that their important matters are being ignored.

### 近邻2：samplenew3_00113381

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction
- 与query gold精确词面重合：∅
- 字幕：I have already repaid him.
- 描述：In the text, the caption reads: "He has already repaid him." This sentence could be a response from a man to someone or something. Given the emotional context described in the audio clues, which portrays a person's as tense, frustrated, and anxious, and the visual cues of the man's's serious expression and the oppressive atmosphere around him, we can infer that the sentence might be delivered with a tone of dissatisfaction or anger. Therefore, this sentence could be the man's's way of expressing his dissatisfaction or complaint towards someone or something, which alignss well with his overall negative mood.

### 近邻3：samplenew3_00062074

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, questioning, uncertainty, worry
- 与query gold精确词面重合：concern
- 字幕：If I use you as my generals, there may be objections and it may be shaken.
- 描述：In the text, the subtitle reads: "If I were to use your generals, there would probably be objections." This sentence may be the man's evaluation or reaction to someone or something. Based on the audio clue describing the individual speaking with a clear and confident voice but with a slight tremor, indicating that they may feel anxious or nervous, and the serious expression and focused body language of the man in the video, it suggests that he is in a tense or focused state. Therefore, this sentence may carry a sense of concern or uncertainty, possibly questioning or worrying about someone or something.

### 近邻4：samplenew3_00081020

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, discontent, fury
- 与query gold精确词面重合：∅
- 字幕：I had no choice but to kill Kong Xiu. It has nothing to do with you. Quickly inform the Prime Minister and tell him to order all officials not to trouble me anymore. Did you hear me?
- 描述：In the text, the caption reads: "When I killed Kong Xi, it was under duress and not something to do with any of you. Quickly inform the chancellor and tell him to hurry and order all officials to stop causing trouble for me. Did you hear that?" Given the intense anger and aggressive tone of the individual's's voice as described by the audio clues, along with the serious expression, confident posture, and formal attire of the man depicted in the video clues, we can infer that this statement is likely an expression of his discontent and fury. He might be explaining to those around him or the audience why he killed Kong Xi, and demanding that he be informed by the chancellor to issue orders to all officials to cease bothering him. The strong negative emotions and anger in this statement align with the personal emotional state described in the audio clues.

### 近邻5：samplenew3_00065427

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, committed, determination, worry
- 与query gold精确词面重合：anxiety
- 字幕：Your Majesty, I am willing to guarantee it with my life.
- 描述：In the text, the caption reads: "Your Majesty, I swear by my life." This sentence could be what a man says while discussing or explaining an issue. Given the man's's concern and serious demeanor as indicated in the video clues, along with the audio cues suggesting he is experiencing strong emotions, we can infer that this statement might be his expression of the significance and commitment to something he is addressing. He may feel so worried or anxious that he is willing to stake his life on the truth or importance of something. This phrase might reflect the man's current predicament or challenge, and his determination and commitment to resolving it.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 2. samplenew3_00017831｜decline｜ΔF1 -0.500000

gold：concern, worry

query字幕：

源标注描述：In the text, caption content: "You think Zhang Chao might be angry at me." This sentence might be a speculation or concern from a woman over the phone to the other person. Based on the visual clues showing the woman's fists clenched and possibly feeling stressed or worried, as well as audio clues where she mentions that as an AI language model she cannot analyze the acoustic information in the audio to identify relevant emotional cues, we can infer that this sentence might be her expression of concern or worry towards Zhang Chao's emotional state, fearing he might be upset or unhappy for some reason.

off原始输出：The character's emotional state is concern, worry.

retrieval原始输出：The character's emotional state is concerned, warning.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|concern, worry|1.000000|2|0|0|
|retrieval|concern, warning|0.500000|1|1|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由1.000000变为0.500000，差值-0.500000。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：worry。
- 相对off新增未精确匹配gold的标签：warning。

gate：0.119977102；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00020419

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：doubt, skepticism, uncertainty
- 与query gold精确词面重合：∅
- 字幕：He said by the tree but you look
- 描述：In the text, the subtitle reads: "He said next to the tree, but you see." This sentence may be a question or reaction from the woman to the police officer. Based on the monotone and emotionless tone described in the audio clues, as well as the curiosity and concern displayed by the woman in the video clues, we can infer that this sentence may carry a tone of doubt or uncertainty. The woman may have some skepticism about the police officer's answer or instructions and is hoping to confirm or understand what the police officer said by observing the surrounding environment. Therefore, this sentence may be a reaction from the woman when asking the police officer for specific directions about a certain location.

### 近邻2：samplenew3_00088959

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：cold, unfriendly
- 与query gold精确词面重合：∅
- 字幕：Go back obediently and take a good look at the information about your interrogation subject, Ouyang Jing.
- 描述：In the text, the caption reads: "Behave and go back to interrogate your subject, OuYang Qing. Go through these documents carefully." Based on the speaker's's voice described in the audio clues - calm and composed, with a neutral tone that does not exhibit strong emotion - and the video clues which do not clearly reveal the woman's exact emotional state through her facial expressions and body language, we can infer that this statement might be a command or an instruction, delivered in a serious or detached manner. Therefore, this sentence likely does not carry a positive emotion, but instead comes across as cold or unfriendly, aligning with the woman's's uncomfortable expression in the video.

### 近邻3：samplenew3_00037963

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, dissatisfaction, suspicion
- 与query gold精确词面重合：concern
- 字幕：Did Hongyu really not contact you?
- 描述：In the text, caption content: "Red Jade really didn't contact you at all, right?" This sentence might be a query or doubt from a woman to someone nearby. Given the emotional cues from the individual's voice, which seems trembling and detached, as well as the woman's expressed anger, sadness, and anxiety in the video, we can infer that this statement might carry tones of suspicion, dissatisfaction, or concern. The woman might be dissatisfied or worried about the answer or behavior of the person beside her, thus posing such a question.

### 近邻4：samplenew3_00057628

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, determination
- 与query gold精确词面重合：∅
- 字幕：The overall business quality is very high.
- 描述：In the text, the subtitle reads: "High level of business competence." This sentence may be an evaluation or description of the woman. Based on the visual cues of the woman's neutral expression, relaxed posture, and simple environment in the video, as well as the confident and authoritative voice in the audio, we can infer that this sentence is likely a recognition and praise of the woman's abilities and qualities. The woman may be displaying a confident and determined emotional state, aligning with the description of high competence in the subtitle.

### 近邻5：samplenew3_00113889

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, disappointment, frustration
- 与query gold精确词面重合：∅
- 字幕：I would definitely pull him away if I had to rush, as I usually do.
- 描述：In the text, the subtitle says, "I would have dragged him away without hesitation if it were a normal day." This sentence may be the woman's reaction to someone or a situation. Based on the audio clues describing the individual's sense of urgency and frustration, as well as the serious facial expression and body language of the woman in the video, we can infer that this sentence may carry an anxious or frustrated tone. The woman may feel pressed for time and want to resolve a problem quickly, but for some reason, she feels powerless or hindered. Therefore, this sentence expresses the woman's sense of frustration and disappointment.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 3. samplenew3_00101197｜decline｜ΔF1 -0.500000

gold：anger, dissatisfaction

query字幕：No qualification to boast here

源标注描述：In the text, the subtitle reads: "Not qualified to boast here." This sentence may be the individual's evaluation or reaction to someone or something. Based on the audio clues describing the trembling voice and slow, cautious speech, as well as the confident and composed behavior displayed in the video, we can infer that this sentence may carry a sense of anger or dissatisfaction. The individual may be displeased with someone's bragging or self-importance in a certain area and is expressing this dissatisfaction by controlling their emotions. Therefore, this sentence may be a way of expressing criticism or warning, contrasting with the overall confident and composed emotions displayed by the individual.

off原始输出：The character's emotional state is anger, dissatisfaction.

retrieval原始输出：The character's emotional state is anger, frustration.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, dissatisfaction|1.000000|2|0|0|
|retrieval|anger, frustration|0.500000|1|1|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由1.000000变为0.500000，差值-0.500000。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：dissatisfaction。
- 相对off新增未精确匹配gold的标签：frustration。

gate：0.120073564；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "frustration", "unmatched_gold_label": "dissatisfaction"}]}

实际5近邻证据：

### 近邻1：samplenew3_00020053

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：dissatisfaction, exhaustion, frustration
- 与query gold精确词面重合：dissatisfaction
- 字幕：This person relies on selling their life to make a living.
- 描述：In the text, the caption reads: "This man lives and breathes through his labor." This phrase could be an evaluation or description of himself or others by the man. Given the audio cues that describe a personal voice with a sense of urgency and tension, and possibly an inflection suggesting excessive stress or pressure, we can infer that this statement might carry a negative emotional undertone. The phrase may imply that the man feels under immense pressure, possibly due to the demands of his work or responsibilities, which require significant effort and sacrifice from him. Therefore, this statement might convey feelings of frustration, exhaustion, or dissatisfaction, in line with the serious and tense demeanor portrayed in the video.

### 近邻2：samplenew3_00031058

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, tension
- 与query gold精确词面重合：∅
- 字幕：How did Xu Ru Gui say that she ate the pill?
- 描述：In the text, caption content: "How did Xu Ruigui say she ate that pill?" This sentence might be a man's's question or confusion about an event or plot. Based on the video clues, such as the man's's serious and focused expression and body language, as well as the audio cues describing a highly tense state, we can infer that this sentence might be said with a sense of anxiety or tension. The man's's facial features and overall demeanor indicate that he is very serious about what he is doing, which could be due to his attention and concern for the event. Therefore, this sentence might be the man's's questioning or misunderstanding of a crucial detail or plot, fitting in with his overall tense emotion.

### 近邻3：samplenew3_00102593

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, overwhelm, tension, unease
- 与query gold精确词面重合：∅
- 字幕：The place where the incident occurred has already been shown to you.
- 描述：In the text, the caption reads: "The place where the incident occurred, you've already seen it." This phrase could be a personal response or explanation to someone else. Considering the video hints of the individual avoiding the camera lens, feeling shy and introspective, and the audio clues of a slight tremble in their voice and an anxious tone, we can infer that this sentence might carry a sense of tension or unease. The person may be responding to someone's inquiry or pressure, attempting to explain or justify that the scene of the incident has already been viewed. This tension could stem from the individual feeling overwhelmed or in a difficult situation but still making an effort to remain calm.

### 近邻4：samplenew3_00043193

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, tension, unease, urgency
- 与query gold精确词面重合：∅
- 字幕：The two people who are going to kill Xu Rugu on that day.
- 描述：In the text, caption content: "The two people who were to kill Xu Rougui that day." This sentence might have been said by a man in the video. Based on the audio clues describing the man's's voice with a tremble trait, the tone with a sense of urgency, and the man's's calm and relaxed emotional state shown in the video clues, we can infer that this sentence might be the man describing a tense, urgent situation or event. Such description contrasts with his overall calm and composed emotional presentation, possibly implying that he is concerned or uneasy about this incident.

### 近邻5：samplenew3_00049602

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, approval, respect
- 与query gold精确词面重合：∅
- 字幕：Only the official embroidery workshop can produce such high-quality filial piety.
- 描述：In the text, caption content: "Only pieces of this quality would be found at the official embroidery workshop as an act of respect." This sentence might be a man's's evaluation or praise for something or an item. Based on the high-pitched tone, quick pace of speech, and the serious expression and authoritative demeanor displayed by the man in the audio clues, we can infer that the sentence might carry a tone of admiration or approval. The man might be praising the high quality of some item or someone's capability. Therefore, this sentence alignss with the overall solemn and authoritative presence of the man.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 4. samplenew3_00027108｜decline｜ΔF1 -0.500000

gold：anger, frustration

query字幕：

源标注描述：In the text, caption reads: "I'm being polite to you because of your daughter, but my father is much more fierce than you, I'm scared of him, some people." This sentence could be a man's's evaluation or response to someone else. Given the male voice's tone in the audio clues that conveys a sense of frustration and anger, and the man's's surprised facial expression and body language in the video clues, we can infer that this sentence might carry an aggressive or confrontational tone. The man might be feeling angry and frustrated due to something that the other person did or said, and through this sentence, he expresses his dissatisfaction towards this person and compares himself to his father. Therefore, this sentence might be a negative evaluation or an aggressive manner of expression, consistent with the man's's overall negative emotion.

off原始输出：The character's emotional state is anger, frustration.

retrieval原始输出：The character's emotional state is anger, dissatisfaction.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, frustration|1.000000|2|0|0|
|retrieval|anger, dissatisfaction|0.500000|1|1|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由1.000000变为0.500000，差值-0.500000。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：frustration。
- 相对off新增未精确匹配gold的标签：dissatisfaction。

gate：0.120035738；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "dissatisfaction", "unmatched_gold_label": "frustration"}]}

实际5近邻证据：

### 近邻1：samplenew3_00110560

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, irritability, tension
- 与query gold精确词面重合：∅
- 字幕：Did you not see those foreign students?
- 描述：In the text, with subtitles: "You didn't see those foreign students, right?" Given the man's excited or agitated state and his passionate conversation with another individual in the video clues, we can infer that this phrase might be a question or accusation directed at someone nearby. Considering the high-pitched tone, rapid speech pattern, and negative emotion speculated from the audio cues, we can assume that the statement might carry an anxious, tense, or irritable tone. Therefore, this sentence could be a way for the man to express blame or concern towards someone nearby, contrasting with his overall display of excitement or agitation.

### 近邻2：samplenew3_00045845

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：humor, positive
- 与query gold精确词面重合：∅
- 字幕：I have other things to do, please lend me some money quickly.
- 描述：In the text, the caption reads: "Hurry, lend me some rice, I have other things to do." This sentence could be a request or response from a man to someone else. Given the comedic and surprised facial expressions and body language of the man in the video clues, we can infer that the tone might be lighthearted or humorous. The man may be joking around or teasing the other person, conveying the message that he has other things to attend to. Therefore, this statement alignss with the overall positive mood displayed by the man. Since there are no emotional cues provided in the audio clues, we primarily base our speculation on the video clues to determine the man's's emotional state.

### 近邻3：samplenew3_00076416

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration, impatience
- 与query gold精确词面重合：anger, frustration
- 字幕：You don't believe it, how long will it take?
- 描述：In the text, the subtitle says, "You don't believe it, it won't take long." This sentence may be the individual's response or comment to someone or something. Based on the audio clues describing the individual's voice as filled with anger and frustration, with an aggressive and confrontational tone, as well as speaking at a fast pace, we can infer that this sentence may carry a sense of anger and impatience. The individual may be dissatisfied with someone or something and trying to emphasize their point. Therefore, this sentence expresses the individual's dissatisfaction and impatience.

### 近邻4：samplenew3_00089252

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, irritation
- 与query gold精确词面重合：anger
- 字幕：This woman is the same, Jiazhen is always arguing with me every day.
- 描述：In the text, the subtitle reads: "All these women are like treasures causing me trouble every day." Based on the man's's expressions and body language in the video clues, it can be inferred that he has a strong emotional response to the current situation, possibly including negative emotions such as surprise, disbelief, or anger. The phrase "causing me trouble every day" in this subtitle suggests that the man is dissatisfied or annoyed with the woman's's behavior or attitude. Therefore, it can be speculated that the man's's emotional state might be one of anger or irritation.

### 近邻5：samplenew3_00042764

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, encouragement, firm, support
- 与query gold精确词面重合：∅
- 字幕：There is nothing that you can't accomplish as long as you speak up, I am here to help.
- 描述：In the text, caption content: "Whatever you need, just ask, there's nothing my second happiness can't accomplish." This sentence might be a response or promise from one speaker to another. Given the speaker's's assertive tone, emphasis on certain words, and the use of repetitive phrases, it can be inferred that this sentence carries a confident and firm tone. Additionally, considering the positive emotional state described in the audio clues and the cheerful environment, it can be deduced that this sentence is likely an expression of encouragement or support, aligning with the overall positive demeanor portrayed.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 5. samplenew3_00027335｜decline｜ΔF1 -0.500000

gold：anger, dissatisfaction

query字幕：Why do you always speak nonsense as soon as you open your mouth?

源标注描述：In the text, the subtitle reads, "Why do you always speak nonsense?" This sentence may be a criticism or accusation directed at the individual. Based on the audio clues describing the trembling voice, slow and cautious speech, as well as the emotions of disdain and challenge displayed by the woman in the video, we can infer that this sentence may carry an angry or dissatisfied tone. Therefore, this sentence may be a reproach or accusation directed at the individual, aligning with the overall negative emotions exhibited by the woman.

off原始输出：The character's emotional state is anger, dissatisfaction.

retrieval原始输出：The character's emotional state is anger, frustration.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, dissatisfaction|1.000000|2|0|0|
|retrieval|anger, frustration|0.500000|1|1|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由1.000000变为0.500000，差值-0.500000。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：dissatisfaction。
- 相对off新增未精确匹配gold的标签：frustration。

gate：0.119846404；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "frustration", "unmatched_gold_label": "dissatisfaction"}]}

实际5近邻证据：

### 近邻1：samplenew3_00043657

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, concern, frustration, worry
- 与query gold精确词面重合：anger
- 字幕：I can't risk your future either.
- 描述：In the text, the caption reads: "I can't risk your future too." This phrase might be a concern or worry that a man expresses to a woman. Given the tone of frustration and anger conveyed in the personal voice as described by the audio clues, and the positive listening behavior shown by the woman along with the man's's reflective and attentive response depicted in the video clues, we can infer that this statement might carry a tone of concern or worry. The man may be worried about the woman's decision or action, fearing it could have negative repercussions on her future. Thus, this sentence might be an expression of concern and worry that alignss with the overall sense of frustration and anger displayed by the man.

### 近邻2：samplenew3_00037746

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：advising, care, comfort, concern, relaxing
- 与query gold精确词面重合：∅
- 字幕：Your Highness, you have worked hard all night, please go back and rest.
- 描述：In the text, the subtitle reads: "Your Highness, you have worked hard all night, go rest." This sentence is likely an expression of care and concern from the man to the woman. Based on the description of the high-pitched and gentle manner of speaking in the audio clues, as well as the calming effect of the accompanying clock sound, it can be inferred that this sentence is likely comforting and advising the woman to relax and rest, expressing care and concern for her. At the same time, based on the woman's expression and body language in the video, showing curiosity and excitement, it can be inferred that the woman may have gone through a difficult work or activity, while the man displays calmness and concern. Therefore, this sentence is likely the man caring for the woman while reminding her to relax and rest, reflecting his care and concern for her.

### 近邻3：samplenew3_00056089

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, excitement
- 与query gold精确词面重合：∅
- 字幕：Is that so? Then I'll go take a look.
- 描述：In the text, with subtitles reading: "Is that so? I'll go and check then." This line could be a response from one female to another. Given the audio cues of a shaky personal voice and slightly faster pace, as well as the video clues showing the women's focused in thought and lacking interaction, we can infer that this line might carry an air of tension and excitement. Therefore, this line may be a positive response, expressing anticipation and excitement for an upcoming event or performance.

### 近邻4：samplenew3_00083834

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, tension
- 与query gold精确词面重合：∅
- 字幕：You must never tell him that I'm afraid of him, I know.
- 描述：In the text, the caption reads: "You mustn not tell him I'm afraid he'll be alright. I got it." Based on the description of the woman's high-pitched voice in the audio clues, and the complex emotions and busy actions portrayed by the female in the video clues, we can infer that this line may carry a tone of tension or anxiety. The woman might be expressing her concerns or fear to someone over the phone, hoping they won't relay this information to another person. This alignss with the complex emotions and busy movements shown by the female in the video clues, suggesting she is possibly handling an urgent or difficult situation.

### 近邻5：samplenew3_00028433

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：enthusiasm, excitement
- 与query gold精确词面重合：∅
- 字幕：Isn't that adding wings to the tiger when doing business with me, revealing that the password technique is very high.
- 描述：In the text, caption content: "That would be like giving me an advantage in doing business with cryptography being high." This sentence might be what this woman said in the video. Based on the audio clues described by the higher pitch and sharp staccato rhythm, as well as the video hints showing the woman's happy and satisfied emotion, we can infer that the tone of this sentence might convey excitement or enthusiasm. Therefore, this sentence could be the woman expressing her excitement or surprise about a certain situation, which alignss with her overall positive mood.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 6. samplenew3_00105401｜decline｜ΔF1 -0.457143

gold：annoyance, determination, frustration

query字幕：It's better not to have been beaten, but you can give it a try. Also, go and tell Lao Zhou that I won't show up.

源标注描述：In the text, the subtitle reads: "It's better not to have been hit in the waist, but you can give it a try. Also, go and tell Lao Zhou that I won't show up." Based on the description of the speaker in the audio speaking in a calm and cautious tone with a hint of nervousness in their voice, as well as the serious facial expression and body language of the man in the video, we can infer that this sentence may be delivered with a calm and determined tone. The speaker mentions having taught someone how to ride a bicycle before, but they did not learn, and then mentions being willing to try teaching this person again. This sentence indicates that the speaker feels frustrated or annoyed by this situation but is still willing to try. Therefore, this sentence may be the speaker expressing a response to a suggestion from someone nearby or expressing their decision. Based on the overall calm and determined emotional state displayed by the speaker, we can infer that this sentence may be an expression of a decision or suggestion that aligns with the speaker's emotional state.

off原始输出：The character's emotional state is determination, resolve, frustration, annoyance.

retrieval原始输出：The character's emotional state is anger, frustration.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|annoyance, determination, frustration, resolve|0.857143|3|1|0|
|retrieval|anger, frustration|0.400000|1|1|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.857143变为0.400000，差值-0.457143。
- TP变化-2，FP变化+0，FN变化+2。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：annoyance, determination。
- 相对off新增未精确匹配gold的标签：anger。
- 相对off移除未精确匹配gold的标签：resolve。

gate：0.119953893；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00009761

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：boredom, contentful, thoughtful
- 与query gold精确词面重合：∅
- 字幕：It's either a wealthy family or not at all.
- 描述：In the text, caption content: "It's not just that he's from a big family, it's as if he is." Given the video hints of the man's's calm facial expression and relaxed body language, along with the presence of books and coffee in the environment, it's hard to determine his emotional state. He might be content, thoughtful, or even bored while sipping his coffee with a blank stare. However, the aggressive and hostile description of the speaker in the audio clues, coupled with anger and frustration, contradict the man's's calm and relaxed emotional state. Therefore, it's not possible to accurately infer the man's's emotional state.

### 近邻2：samplenew3_00005883

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：important, urgency
- 与query gold精确词面重合：∅
- 字幕：You just go ahead and prepare for today, I will talk to him later to confirm the time.
- 描述：In the text, the caption reads: "You just follow through with what we've planned for today and I'll get back to you to finalize the timing later." This sentence might be an instruction or advice from one person to another. Given the urgency and importance conveyed by the speaker's's tone as per the audio cues, and the individual's focused and serious demeanor indicated in the video clues, we can infer that this statement might carry a sense of urgency and importance. Therefore, the sentence likely emphasizes that the other person should prepare according to today's arrangements and later confirm the time with him. This suggests that the speaker attaches great importance to the topic of discussion and expects the other party to make timely preparations.

### 近邻3：samplenew3_00033656

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：complaint, dissatisfaction, frustration, helplessness, negativity
- 与query gold精确词面重合：frustration
- 字幕：Why does it have to be me, Kuanglu?
- 描述：In the text, the subtitle reads, "Craig, why does it have to be me?" This sentence is likely spoken by the man in the video. Based on the description of the individual feeling sad and frustrated in the audio clues, as well as the man's relaxed posture and funny facial expressions in the video clues, we can infer that this sentence may carry a tone of helplessness or complaint. The man may feel that he has been unfairly assigned a certain task or responsibility and is feeling pressure and dissatisfaction about it. Therefore, this sentence expresses the man's negative emotions and complaining attitude.

### 近邻4：samplenew3_00075990

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, confusion, frustration, pressure, uncertainty, unease
- 与query gold精确词面重合：frustration
- 字幕：No, no, Jiang Jiang Jiang, please be more specific about what you want me to do.
- 描述：In the text, caption content: "No, no, Jiang Jiang Jiang, you say, be more specific, tell me exactly what I'm supposed to do." This sentence could be a man's response or inquiry to his superior or leader. Based on the pitch and agitated tone described in the audio clues, as well as the man's's serious expression and gestures in the video clues, we can infer that this sentence might carry an anxious or uneasy emotion. The man might feel pressured and frustrated, confused and uncertain about the requirements of his superior or leader. Therefore, this sentence could be the man expressing his confusion and requesting for more specific instructions or demands from the other party.

### 近邻5：samplenew3_00026709

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, stress
- 与query gold精确词面重合：∅
- 字幕：Senior brother, I, Hou Liangping, am telling you, are you guys tricking us? Our person who went to the guesthouse was intercepted by comrades from the municipal bureau. How did they know we were using the back door?
- 描述：In the text, the subtitle reads: "Senior brother, I'm Hou Liangping, I say, are you cheating people? Our people went to the accommodation center to pick up someone, but were blocked by the city bureau comrades. How do they know we took the back door?" Given the speaker's's aggressive and confrontational tone described in the audio clues, along with their rapid speech pace indicating of urgency and frustration, we can infer that the speaker is likely experiencing negative emotional states such as anger, anxiety, and stress. The expressions in the subtitle reflect this emotional state; he is questioning if they are cheating people and describing being blocked by city bureau comrades. These expressions align with the negative emotional state indicated in the audio clues.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 7. samplenew3_00096603｜decline｜ΔF1 -0.428571

gold：concern, tension, uncertainty

query字幕：But Yina hasn't interviewed me yet.

源标注描述：In the text, the caption reads: "But I haven't been interviewed by Ina yet." This sentence might be the woman's response to a certain interview. Based on the mixed emotions of curiosity and concern shown by the woman in the video clues, along with her slight tilt of the head and downward gaze, it can be inferred that she feels somewhat tense and uncertain about this interview. Additionally, according to the audio clues describing the person's's trembling voice and breathing, it can be speculated that the person is struggling to control their emotions, possibly due to the pressure or anxiety from the interview. Therefore, this sentence may reflect the woman's concern or uncertainty about the interview, which alignss with her overall complex emotions.

off原始输出：The character's emotional state is concern, uncertainty, tense.

retrieval原始输出：The character's emotional state is concern, uncertainty, calm, composed.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|concern, tension, uncertainty|1.000000|3|0|0|
|retrieval|calm, composed, concern, uncertainty|0.571429|2|2|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由1.000000变为0.571429，差值-0.428571。
- TP变化-1，FP变化+2，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：tension。
- 相对off新增未精确匹配gold的标签：calm, composed。

gate：0.119996615；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00015992

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, frustration
- 与query gold精确词面重合：∅
- 字幕：Just now I happened to have said a few bad words about Sun.
- 描述：In the text, the caption states: "Just now, I said a few bad things about Son." Given the description of the individual speaking at a high pitch and in an excited manner in the audio clues, it indicates that the person might be experiencing intense negative emotions such as anger, frustration, or anxiety. The fact that the caption mentions the individual just said bad things about Son suggests that they person may currently be in an angry or frustrated emotional state. This negative emotion could be triggered by something related to Son, but the specific circumstances need further clarification. Based on the analysis of the audio and the caption, it is recommended that this individual seeks professional assistance to cope with emotional stress.

### 近邻2：samplenew3_00063431

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：enthusiasm, positively emotionally engaged
- 与query gold精确词面重合：∅
- 字幕：I still feel that the battle of the circulating water pump bearings is a bit abnormal, so I want to take advantage of the free time during the shift to take a closer look at these.
- 描述：In the text, caption content: "I still find the circular pump bearing fight a bit odd, so I want to take advantage of my break time to learn more about these." This sentence might be a woman discussing a problem or challenge at work. Based on the curious and expectant expression of the woman in the video clues, as well as the audio clue where the female speaks with confidence and authority about the importance of emotional intelligence in the workplace, we can infer that this sentence is the woman expressing her viewpoint on an unusual situation at work, and she hopes to delve deeper into this issue during her break times. Therefore, this sentence indicates that the woman is enthusiastic and positively emotionally engaged at work.

### 近邻3：samplenew3_00094234

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：friendliness, warm
- 与query gold精确词面重合：∅
- 字幕：Can you come to my sister's house for dinner tonight, Xiaobei?
- 描述：In the text, the subtitle content says, "Xiao Bei, can you come to my sister's house for dinner tonight?" Based on the description of the woman's facial expressions and body movements in the video clues, she appears to be at ease or relaxed during the conversation. Her overall demeanor is calm and composed, which contradicts the description in the audio clues of an individual trying to control their emotions. Therefore, we can infer that this sentence is not spoken with an anxious or fearful tone, but rather as an invitation or request. The woman may be inviting Xiao Bei to come to her sister's house for dinner, which could be a friendly and warm invitation.

### 近邻4：samplenew3_00085209

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：overwhelm, stress, under pressure
- 与query gold精确词面重合：∅
- 字幕：My company is adding pressure and I still have to.
- 描述：In the text, the subtitle reads, "My stress is increasing and I can't handle it anymore." This sentence may be expressing the speaker's difficulties and stress. Based on the audio clues describing the speaker's trembling voice, heavy breathing, and the tone indicating feeling overwhelmed or under a lot of pressure, we can infer that this sentence is describing the challenges and stress the speaker is currently facing. This sentence indicates that the speaker feels an increase in stress, possibly due to work or other personal issues. This contrasts sharply with the joyful and pleasant emotions displayed by the woman in the video, showing a difference in emotional states between the two individuals.

### 近邻5：samplenew3_00038964

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, embarrassment, fear
- 与query gold精确词面重合：∅
- 字幕：Director Wu, I'm sorry, I didn't know he came to see you.
- 描述：In the text, the caption reads: "Director Wu is embarrassed, I didn't know he came to see you." Based on the audio clues describing the speaker's's voice trembling slightly and speaking rapidly with urgency, and the video clues showing a neutral facial expression from the woman along with a lack of obvious body language cues, we can infer that this sentence might be an apology or explanation from the speaker to the woman. Given that the audio clues suggest the speakerer might be experiencing strong emotions such as fear, anxiety, or tension, and considering the video clues where the woman shows no clear reaction or exhibits a detached or indifferent attitude, we can deduce that the woman may not be visibly responding to the speaker's's emotional state. Therefore, this sentence could be the speaker feeling embarrassed in their apology or explanation, hoping for the woman's understanding or forgiveness for his actions.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 8. samplenew3_00051112｜decline｜ΔF1 -0.400000

gold：encouragement, energetic, positive

query字幕：Come, come, come

源标注描述：In the text, the caption reads: "Come on, come on." This phrase might be a man addressing his surroundings, either as an invitation or encouragement. Given the context of laughter in the audio cues and the man's's comical or surprised facial expression depicted in the video cues, we can infer that this phrase likely carries a positive, energetic tone. Therefore, it seems that the man is encouraging those around him to join in an activity or performance, which alignss with his overall positive demeanor.

off原始输出：The character's emotional state is encouraging, comforting.

retrieval原始输出：The character's emotional state is excitement, anticipation.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|comforting, encouragement|0.400000|1|1|2|
|retrieval|anticipation, excitement|0.000000|0|2|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.400000变为0.000000，差值-0.400000。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：encouragement。
- 相对off新增未精确匹配gold的标签：anticipation, excitement。
- 相对off移除未精确匹配gold的标签：comforting。

gate：0.119845092；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00088757

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：amusement, energetic, enthusiasm, humor
- 与query gold精确词面重合：energetic
- 字幕：What country is not isolated?
- 描述：In the text, the caption reads: "What country is known for not isolating?" This sentence might be part of a conversation that a woman had. Based on the audio cues where describe the woman speaking with a sharp voice and the audience's laughter, it can be inferred that she might have been telling something interesting or amusing. Her sharp voice accompanied by the audience's laughter suggests that her speech might have had a humorous tone, causing the audience to laugh. Therefore, this sentence could be part of a joke or teasing, fitting with her overall energetic and enthusiastic demeanor.

### 近邻2：samplenew3_00011070

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confusion, distressed, needing support, seeking help
- 与query gold精确词面重合：∅
- 字幕：Call me Guo Cun
- 描述：In the text, the caption reads: "Calling upon the passage through the village," given the man's facial expressions filled with anguish in the video hints, and the woman's efforts to console and support him, along with the audio clues depicting a range of emotions from sadness to fear that the man experiences, we can infer that this phrase might be the man expressing his confusion and distress, seeking the help and support of the lady. This phrase may suggest that the man is facing some difficulties or challenges, needing assistance and support to overcome them.

### 近邻3：samplenew3_00078722

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：humor, playfulness, positive
- 与query gold精确词面重合：positive
- 字幕：This is nonsense.
- 描述：In the text, the subtitle content "What nonsense is this?" is likely the man's response to someone or something. Based on the audio clue describing the individual laughing loudly and experiencing positive emotions, as well as the video clue of the man smiling and laughing, it can be inferred that this sentence is likely a sarcastic or joking response. The man's positive emotions and laughter also support this inference. Therefore, this sentence is likely not a negative evaluation but rather a humorous or playful expression that aligns with the overall positive mood displayed by the man.

### 近邻4：samplenew3_00058384

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, confusion, frustration, unease
- 与query gold精确词面重合：∅
- 字幕：What's the matter?
- 描述：In the text, the caption content: "What's going on" could be a response to an event that occurred or someone else's words. Given the emotional state of the individual as described by the audio cues, which includes confusion and frustration, along with a tense and tight tone of voice, we can infer that this phrase might be delivered with a sense of anxiety or unease. Therefore, this sentence could be an expression of the individual's confusion and dissatisfaction with the current situation, as well as their urgent need for a solution.

### 近邻5：samplenew3_00052901

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, confidence, importance, tension, urgency
- 与query gold精确词面重合：∅
- 字幕：The most important thing is that the enemy can be killed.
- 描述：In the text, the caption reads: "The most important thing is to be able to kill Japanese." This sentence might be what a man says in a video. Based on the audio cues, such as the drumbeat reminiscent of military marches and the speaker's firm tone, along with the visual clues like the man's serious expression and body language in the video, we can infer that this phrase may carry an air of tension, anger, or frustration. At the same time, the mention of "important" and "be able to kill Japanese" in the caption suggests that the individual may feel a sense of urgency and importance. Therefore, this sentence could possibly be the man expressing his tension and anger about something significant, as well as his emphasis on his responsibilities and confidence in them.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 9. samplenew3_00086539｜decline｜ΔF1 -0.400000

gold：frustration, helplessness, overwhelm

query字幕：It's really not easy.

源标注描述：In the text, the caption reads: "It's really not easy." Given the speaker's's voice tension and frustration as described in the audio cues, along with the man's serious facial expression, stern look, and conservative body language depicted in the video clues, we can infer that this statement might be the man expressing his feelings about the difficulties or issues he is currently facing. This sentence conveys a sense of being overwhelmed and helpless under pressure, which alignss well with the man's overall portrayal of seriousness and tension.

off原始输出：The character's emotional state is disappointment, helplessness.

retrieval原始输出：The character's emotional state is disappointment, exhaustion.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|disappointment, helplessness|0.400000|1|1|2|
|retrieval|disappointment, exhaustion|0.000000|0|2|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.400000变为0.000000，差值-0.400000。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：helplessness。
- 相对off新增未精确匹配gold的标签：exhaustion。

gate：0.119988181；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00026709

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, stress
- 与query gold精确词面重合：∅
- 字幕：Senior brother, I, Hou Liangping, am telling you, are you guys tricking us? Our person who went to the guesthouse was intercepted by comrades from the municipal bureau. How did they know we were using the back door?
- 描述：In the text, the subtitle reads: "Senior brother, I'm Hou Liangping, I say, are you cheating people? Our people went to the accommodation center to pick up someone, but were blocked by the city bureau comrades. How do they know we took the back door?" Given the speaker's's aggressive and confrontational tone described in the audio clues, along with their rapid speech pace indicating of urgency and frustration, we can infer that the speaker is likely experiencing negative emotional states such as anger, anxiety, and stress. The expressions in the subtitle reflect this emotional state; he is questioning if they are cheating people and describing being blocked by city bureau comrades. These expressions align with the negative emotional state indicated in the audio clues.

### 近邻2：samplenew3_00005883

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：important, urgency
- 与query gold精确词面重合：∅
- 字幕：You just go ahead and prepare for today, I will talk to him later to confirm the time.
- 描述：In the text, the caption reads: "You just follow through with what we've planned for today and I'll get back to you to finalize the timing later." This sentence might be an instruction or advice from one person to another. Given the urgency and importance conveyed by the speaker's's tone as per the audio cues, and the individual's focused and serious demeanor indicated in the video clues, we can infer that this statement might carry a sense of urgency and importance. Therefore, the sentence likely emphasizes that the other person should prepare according to today's arrangements and later confirm the time with him. This suggests that the speaker attaches great importance to the topic of discussion and expects the other party to make timely preparations.

### 近邻3：samplenew3_00023724

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：contentment, excitement, pride, surprise
- 与query gold精确词面重合：∅
- 字幕：What a blessing from heaven
- 描述：In the text, the caption reads: "Surely, a blessing from heaven." This phrase might be a man's's self-assessment or response to his surroundings. Given the audio clues that describe the man's voice as high-pitched with slight tremors, spoken at a quick pace, and the video hints suggesting a smile and an indication of luxurious surroundings, we can infer that this sentence may be conveyed with excitement or surprise. Therefore, this statement could be the man's's praise or reflection on himself or his environment, aligning with his overall positive mood.

### 近邻4：samplenew3_00013102

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration
- 与query gold精确词面重合：frustration
- 字幕：Can you do it or not?
- 描述：In the text, the subtitle says, "Can you not do it?" This sentence may be a response or comment from the older man to the other man. Based on the description of the individual's angry and frustrated emotions in the audio clues, as well as the video clues of the older man actively participating in the conversation, maintaining eye contact, and having a relaxed posture, we can infer that this sentence may carry a tone of challenge or dissatisfaction. Therefore, this sentence may be the older man questioning or refuting the other man, aligning with the overall negative emotions displayed by the individual.

### 近邻5：samplenew3_00095102

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：indifference, lack of concern
- 与query gold精确词面重合：∅
- 字幕：It has nothing to do with me.
- 描述：In the text, the subtitle says, "It has nothing to do with me." This sentence may be the man's response to a certain question or discussion. Based on the serious expression and posture of the man in the video clues, as well as the calm and cautious tone of the individual in the audio clues, we can infer that this sentence may be spoken with a tone of indifference or lack of concern. The man may not be interested in the question or discussion, or he may consider it unrelated to himself. Therefore, this sentence expresses the man's emotional state of indifference or lack of concern.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 10. samplenew3_00028156｜decline｜ΔF1 -0.400000

gold：anxiety, concern, worry

query字幕：Will it affect you and the Four Seas Group?

源标注描述：In the text, caption reads: "Could it affect you and the Forsea Group?" This sentence might be an expression of concern and worry from the speaker about a certain decision or situation. Based on the man's's serious expression and posture in the video clues, as well as the trembling tone and hesitant inflection in the speaker's's voice in the audio clues, we can infer that this sentence may be expressing concern over the potential impact of some important decision or situation on both the speaker and the forsea Group. This concern and worry aligns with the man's's overall serious and anxious emotional state.

off原始输出：The character's emotional state is worry, anxiety.

retrieval原始输出：The character's emotional state is worry, unease.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, worry|0.800000|2|0|1|
|retrieval|unease, worry|0.400000|1|1|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.800000变为0.400000，差值-0.400000。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：anxiety。
- 相对off新增未精确匹配gold的标签：unease。

gate：0.119994909；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "unease", "unmatched_gold_label": "anxiety"}, {"prediction_label": "unease", "unmatched_gold_label": "concern"}]}

实际5近邻证据：

### 近邻1：samplenew3_00083704

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：discontent, distrust, suspicion
- 与query gold精确词面重合：∅
- 字幕：He is here without invitation, always feeling that the visitor is not good.
- 描述：In the text, the caption states: "There's always an uneasy feeling when someone just shows up uninvited." Given the man's serious, thoughtful, and possibly perplexed expression described in the video clues, along with his monotonous and indifferent tone of voice mentioned in the audio cues, which is slow-paced yet purposeful, we can infer that this phrase might be the man's's negative assessment or response to someone or something. The man's's serious facial expression and flat tone, combined with the negative evaluation in the caption, indicate that he might feel discontented, suspicious, or distrustful. Therefore, this sentence could be the man's's expression of a negative impression or suspicion towards someone, aligning with the overall serious and contemplative mood he exhibits.

### 近邻2：samplenew3_00088058

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, threat
- 与query gold精确词面重合：∅
- 字幕：If the cat appears under the tea house today
- 描述：In the text, the subtitle reads, "If the cat appears in the teahouse today." This sentence may be a reaction or response from the woman to the man. Based on the surprise and strong emotional reaction displayed by the woman in the video clues, as well as the high pitch, tension, and strain in the individual's voice in the audio clues, we can infer that this sentence may carry a tone of anger or threat. The woman may be very dissatisfied with the man's behavior or words, and therefore uses this sentence to express her emotions and stance.

### 近邻3：samplenew3_00042300

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, intense stress
- 与query gold精确词面重合：anxiety
- 字幕：San ge, I am not embarrassed at all. I was originally going to explain the situation to him today.
- 描述：In the text, the caption reads: "Brother three, I'm not at all embarrassed. I was planning to clarify things with him today." Given the audio cues, which describe the individual's voice trembling, uneven breathing, and relatively slow speech, it can be inferred that this person is experiencing negative emotions, possibly fear, anxiety, or intense stress. The spoken words in the caption indicates that the person does not feel embarrassed but intends to explain the truth to "Brother three". This suggests they they may be facing some difficulty or need to explain an issue, which could lead to them feeling tense and anxious. Thus, the caption alignss with the emotional state suggested by the audio clues.

### 近邻4：samplenew3_00058035

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：assertive, blame, dissatisfaction, misunderstanding, negative
- 与query gold精确词面重合：∅
- 字幕：Is one month not enough for you to practice the set of knife techniques I taught you a few days ago?
- 描述：In the text, caption content: "Didn't the sword technique you taught me a few days ago suffice for a month's?" This sentence might be a question or blame from a man towards someone else. Considering the mixed emotions of personal anger and frustration described in the audio clues, along with the man's's threatening facial expressions and tense posture depicted in the video hints, we can infer that this sentence might carry an assertive or blaming tone. Therefore, this sentence could be the man's's way of expressing his dissatisfaction or misunderstanding, aligning with his overall negative emotional state.

### 近邻5：samplenew3_00038685

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, gloom, sadness, stress
- 与query gold精确词面重合：anxiety
- 字幕：I just don't know why I'm anxious.
- 描述：In the text, the caption reads: "I just don't know how anxious I am." This statement suggests that the man is aware of his own anxiety. Given the tone of voice described in the audio cues, which is high-pitched and anxious, as well as the man's's expression of sadness or gloom in the video cues through his body language, we can infer that this sentence describes or acknowledges his state of anxiety. Consequently, this statement further confirms that the man is experiencing a high level of anxiety or stress.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 11. samplenew3_00029792｜decline｜ΔF1 -0.400000

gold：confidence, positivity, pride

query字幕：To be able to stay

源标注描述：In the text, the caption reads: "Capable of surviving," this phrase could be an evaluation or response from the man about himself. Given the audio cues that describe a strong, loud voice with a sense of urgency, and the video clues showing the man smiling while seemingly unconcerned about adverse weather conditions, we can infer that the phrase might be delivered with a tone of pride or confidence. Therefore, this statement could be a positive affirmation and praise of the man's ability to persevere through difficulties, aligning with his overall positive demeanor.

off原始输出：The character's emotional state is pride, confidence.

retrieval原始输出：The character's emotional state is pride, affirmation.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|confidence, pride|0.800000|2|0|1|
|retrieval|affirmation, pride|0.400000|1|1|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.800000变为0.400000，差值-0.400000。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：confidence。
- 相对off新增未精确匹配gold的标签：affirmation。

gate：0.119900264；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00014600

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, importance, urgency
- 与query gold精确词面重合：∅
- 字幕：If we don't go back, he wouldn't have died in vain.
- 描述：In the text, the subtitle content "If we don't go back, he won't die in vain" based on the video clue of the man's tense facial expression and the suggestion of bad weather in the environment, as well as the audio clue of the speaker's sense of urgency and intensity in their voice, we can infer that this sentence may be the man expressing a concern or sense of urgency. The man may be discussing an important decision or action and believes that if they don't go back, someone may suffer negative consequences. This sentence expresses the man's importance and urgency of this decision, as well as his concern for someone's safety.

### 近邻2：samplenew3_00062133

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, excitement, satisfaction, tension, under pressure
- 与query gold精确词面重合：∅
- 字幕：Hello, is this Teacher Banhang? What do you say?
- 描述：In the text, the subtitle reads: "Hello, Teacher Banchang, you say." This phrase could be a greeting or an opening line in a phone conversation between a man and another person. Given the audio clues where the individual's has a high pitch voice with slight tremble, and speaks quickly, it suggests he might feel anxious, tense, and under too much pressure. However, based on the video clues where the man is smiling, his eyes are bright, and he generally behaves friendly and approachable, we can infer that he may feel satisfied or even excited in the phone call, which contradicts the emotional state suggested by the audio clues. Therefore, this phrase could possibly be the man displaying a false positive emotion in the phone call, trying to hide his anxiety and tension.

### 近邻3：samplenew3_00016144

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：encouragement, motivated, positive
- 与query gold精确词面重合：∅
- 字幕：Go find our tomorrow
- 描述：In the text, the caption reads: "Seek our tomorrow." This line might be directed at someone off-camera by a man. Given the urgency and determination implied in the speaker's's male voice as described in the audio clues, and the man's's portrayal of deep conversation and possibly excitement in the video clues, we can infer that this statement might be an expression of encouragement or motivation. The man may be urging the other person to positively tackle up to current challenges or to look for hope in the future. This alignss with the overall positive sentiment of the man and the content of their dialogue.

### 近邻4：samplenew3_00082754

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：challenging, important, seriousness, tension
- 与query gold精确词面重合：∅
- 字幕：General, you now only have two choices.
- 描述：In the text, the subtitle says, "General Binglu, you only have two choices now." This sentence may be a suggestion or guidance to the man. Based on the description of the individual's nervous and anxious voice characteristics in the audio clues, as well as the serious and focused emotions displayed by the man in the video clues, we can infer that this sentence may carry a serious or tense tone. Therefore, this sentence may be reminding the man of the importance of the choices he is facing and may involve some difficulties or challenges.

### 近邻5：samplenew3_00101704

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：positive, pride, satisfaction
- 与query gold精确词面重合：pride
- 字幕：I said the conditions have improved in the past two years.
- 描述：In the text, caption content: "I say these two years have been better." This sentence could be a line a man might say in conversation with another person. Considering the mixed emotional state described in the audio cues, including experiences of both positive and negative emotions, we can infer that this statement might carry a tone of pride or satisfaction. The man might be discussing improvements in his living conditions, expressing a positive emotional disposition. This alignss with the video cues showing the man's's relaxed and comfortable emotional state.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 12. samplenew3_00072861｜decline｜ΔF1 -0.400000

gold：excitement, joy, tension

query字幕：As long as you give the note to your mom, your mom will know everything.

源标注描述：In the text, the caption reads: "As long as you give the note to your mom, she will know everything." This sentence might be what a girl tells a boy. Given the high pitch and urgency in the speaker's's voice as described by the audio clues, and considering the lively conversation or shared joy suggested by the video clues, we can infer that the statement might carry an element of excitement or tension. The girl might be reminding the boy that once he hands over the note to his mother, she will uncover all the secrets. This line might hint at some secret or significant information that alignss with the overall positive interaction and high level of emotional engagement portrayed between the girl and the boy.

off原始输出：The character's emotional state is excitement, enthusiasm.

retrieval原始输出：The character's emotional state is anger, frustration.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|enthusiasm, excitement|0.400000|1|1|2|
|retrieval|anger, frustration|0.000000|0|2|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.400000变为0.000000，差值-0.400000。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：excitement。
- 相对off新增未精确匹配gold的标签：anger, frustration。
- 相对off移除未精确匹配gold的标签：enthusiasm。

gate：0.120029002；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00019115

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction
- 与query gold精确词面重合：∅
- 字幕：
- 描述：In the text, the caption reads: "It's definitely him, always throwing things around haphazardly." This sentence might be a woman's evaluation or complaint about someone. Based on the audio clues described, such as a high-pitched female voice, a fast pace, a sense of urgency, and an enthusiastic and passionate tone, along with the video hints showing the woman's surprised expression and gestures, we can infer that the sentence may carry an angry or dissatisfied emotion. The woman might be displeased with someone's behavior of constantly tossing things carelessly, which surprises and frustrates her. Therefore, this sentence might be the woman expressing her dissatisfaction and complaint.

### 近邻2：samplenew3_00059234

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, neutral
- 与query gold精确词面重合：∅
- 字幕：He said that Xiao Fang has been on a business trip for eight days.
- 描述：In the text, caption content: "He said Xiao Fang has been out on business for eight days." This sentence might be a fact or information mentioned in the conversation by a woman. Given the speaker's's highly emotional state described in the audio clues, possibly accompanied by anxiety or tension, and the mixed emotions of the woman in the video cues along with the neutral expression of the man, we can infer that this sentence might be part of a discussion or sharing about "X Fang being out on business for eight days ". Since both parties maintain a calm demeanor in the video, this statement may not involve strong emotions or argument, but rather a relatively light topic.

### 近邻3：samplenew3_00076288

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：self-conscious, tension
- 与query gold精确词面重合：tension
- 字幕：It's not like that. Listen to me. Didn't I tell you that I went to a small stall to buy meat that day?
- 描述：In the text, the caption reads: "It's not like that you have to listen to me, I'll tell you what happened. The day I went to the street vendor to buy meat." Given the personal intonation described in the audio cues - calm and controlled with a slight tremor, and a speech pattern with a hint of accent - it can be inferred that the individual might feel anxious, tense, and self-conscious. The manner in which the content is expressed also supports this inference. The person seems to be explaining or justifying something, with a tone that carries a certain level of tension and uncertainty. Therefore, it can be deduced that the individual likely felt tense and self-conscious during this conversation, possibly due to the need to explain or justify an issue.

### 近邻4：samplenew3_00078238

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confusion, defensiveness, resentment
- 与query gold精确词面重合：∅
- 字幕：Why are you angry? This can only explain this magazine.
- 描述：In the text, the caption reads: "Why are you upset with me?" This phrase could be a woman's response or explanation to someone. Given the audio cues that describe the speaker's as having an aggressive and hostile tone, and the woman displaying a serious expression and body language in the video clues, we can infer that this statement might carry a tone of resignation or confusion. The woman might be responding to the other person's's anger or frustration, expressing her innocence or lack of understanding. Therefore, this sentence could be the woman's attempt to calm down the other person, or to explain her position.

### 近邻5：samplenew3_00062150

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：agitation, concern, defense
- 与query gold精确词面重合：∅
- 字幕：I'll tell you, it's not easy for him to make money. How many calls does he have to answer in a day?
- 描述：In the text, the caption reads: "I'm telling you, show you care, he earns money hard, how many calls does he have to take in a day." This sentence might be a woman's explanation or defense for someone. Given the audio clues, where the woman speaks quickly and in a high-pitched voice, emphasizing certain words and phrases, and the video clues showing the woman with a serious and focused demeanor, we can infer that this statement might carry an emotional tone of agitation or defense. The woman might be defending or explaining a situation for someone, she seems very concerned about this issue and wishes for the other person to understand.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 13. samplenew3_00059251｜decline｜ΔF1 -0.400000

gold：anger, dissatisfaction, unhappy

query字幕：I didn't discuss with you before contacting the courtiers.

源标注描述：In the text, the subtitle reads: "I didn't consult with you before contacting the courtiers." This sentence may be an expression of complaint or dissatisfaction from one individual to another. Based on the description of the individual's tense and anxious speaking style in the audio cues, as well as the negative emotions displayed by the individual in the video cues, we can infer that this sentence may carry a tone of dissatisfaction or anger. Therefore, this sentence may indicate that the individual is unhappy with another person's decision or action and believes that they did not consult or seek their opinion. This expression aligns with the overall negative emotions displayed by the individual.

off原始输出：The character's emotional state is anger, dissatisfaction.

retrieval原始输出：The character's emotional state is anger, frustration.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, dissatisfaction|0.800000|2|0|1|
|retrieval|anger, frustration|0.400000|1|1|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.800000变为0.400000，差值-0.400000。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：dissatisfaction。
- 相对off新增未精确匹配gold的标签：frustration。

gate：0.120068118；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "frustration", "unmatched_gold_label": "dissatisfaction"}]}

实际5近邻证据：

### 近邻1：samplenew3_00030937

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, optimism
- 与query gold精确词面重合：∅
- 字幕：The vacant position of the book will inevitably affect the daily affairs of the two departments. It will be fine once the new book takes office.
- 描述：In the text, caption content: "The vacancy of the position of the scribe inevitably affects the daily affairs of the two, and everything will be fine once the new scribe takes up the role." This sentence might be a man discussing or explaining an issue. Given the audio cues with the speaker's exuding confidence and authority, along with the video clues showing the man in a serious expression and formal attire, we can infer that this sentence could be the man explaining or reassuring about a vacant position. His tone suggests he has a good understanding and control over the issue, and he holds an optimistic outlook on the solution. Therefore, this sentence carries a sense of calmness and optimism, aligning well with the man's's overall serious and formal demeanor.

### 近邻2：samplenew3_00038729

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration
- 与query gold精确词面重合：anger
- 字幕：What does it mean for you to come over early in the morning and say these words?
- 描述：In the text, the caption reads: "What do you mean by saying all this at such an early hour?" This phrase might be spoken by one man to another. Given the aggressive and confrontational tone described in the audio cues, as well as the serious and focused demeanor and body language of the man portrayed in the video clues, we can infer that this statement might be laced with emotions of anger or frustration. The man might feel overwhelmed or threatened by what the other man has said, thus expressing his dissatisfaction and confusion in a strong manner.

### 近邻3：samplenew3_00017453

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：happiness, satisfaction
- 与query gold精确词面重合：∅
- 字幕：The mirror driver guessed correctly and cancelled the closure of various disaster-stricken areas this year. I have nothing to be unhappy about with such smooth political affairs.
- 描述：In the text, caption content: "The Mirror Office successfully guessed and withdrew today's's decision on settling the sealing of warehouses in various regions. With politics running so smoothly, what should I be unhappy about?" Given the audio clues described by an individual speaking in a calm and even tone, and the video clues featuring a man with a serious expression who may play a significant role, we can infer that this sentence might be the man expressing his satisfaction and happiness over the smooth progress of politics and matters. Although the acoustic information in the audio does not clearly indicate the individual's emotional state, combined with the video clues of the man's serious expression and potential key role, we can infer that this sentence might be expressed in a satisfied and happy tone by the man.

### 近邻4：samplenew3_00030601

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：assertive, confidence, courageous, fighting prowess, powerful, pride, strong
- 与query gold精确词面重合：∅
- 字幕：So proud and arrogant, striving for victory on the battlefield, the silver robe and long spear whistling back and forth.
- 描述：In the text, the caption reads: "So proud and assertive, always striving for victory on the battlefield, with the silver armor and long spear sweeping back and forth." Given the speaker's's deep and resonant voice, filled with confidence and decisiveness, as well as the man's serious expression and thoughtful posture suggested by the audio and video clues respectively, we can infer that this sentence might be describinging certain traits or behaviors of the man. The words "proud and assertive," "striving for victory," and the action phrase "s howling back and forth" all carry positive, confident, and powerful connotations. Therefore, it seems plausible that this sentence could be praising the man's's courage, strength, and fighting prowess, aligning well with his displayed serious and thoughtful demeanor.

### 近邻5：samplenew3_00113741

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：adventurous, confidence, positive, slightly irritated
- 与query gold精确词面重合：∅
- 字幕：How can you know the result without doing many things? Let me try and see what happens.
- 描述：In the text, the caption reads: "How can you know the outcome without trying many things? What harm is there in me trying?" This sentence might be spoken by a man in a video. Based on the audio cues, the speaker's has a calm and measured tone, with an undercurrent of slight irritation. Additionally, considering the video clues where the man exhibits a smile and a confident posture while looking directly into the camera, we can infer that this sentence might carry a tone of challenge or adventure. The man may be expressing a positive attitude, encouraging himself or others to try new things without fear of failure. This alignss well with the overall impression of the man's being at ease and positive.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 14. samplenew3_00063274｜decline｜ΔF1 -0.377778

gold：anxiety, curiosity, engaged, fear, tension, unease

query字幕：How long do you think this gold can last?

源标注描述：In the text, the caption reads: "This gold, do you think how long it can last". Based on the video hints where the woman's interest and focused expression towards the object in the man's's hand, as well as her maintaining eye contact and tilting her body, it can be inferred that she is curious and engaged with the object or the topic of discussion. Therefore, this phrase could be a question posed by the woman to the man about the object or part of a discussion about it. According to the audio clues, the speaker's's voice is trembling and shaking, accompanied by a tight and tense tone, suggesting that the speaker might be experiencing strong emotional distress, such as fear, anxiety, or tension. Thus, this phrase may carry a sense of tension or unease, possibly reflectinging the speaker's's concern or uncertainty about the duration of the gold's accommodation.

off原始输出：The character's emotional state is curious, interested, anxious, tense.

retrieval原始输出：The character's emotional state is curious, interested, challenging.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, curiosity, interested, tension|0.600000|3|1|3|
|retrieval|challenging, curiosity, interested|0.222222|1|2|5|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.600000变为0.222222，差值-0.377778。
- TP变化-2，FP变化+1，FN变化+2。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：anxiety, tension。
- 相对off新增未精确匹配gold的标签：challenging。

gate：0.120021112；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00098694

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, neutral
- 与query gold精确词面重合：∅
- 字幕：Did the scrap materials that Qige brought down sell as scrap steel? Did the money for each roll come in or not?
- 描述：In the text, caption content: "That Brother Seven's discarded waste sold as scrap steel, a roll more or less, and doesn't that money come from that?" Based on the video clues, the female's facial expressions and body movements do not show any strong emotions, and her wearinging of a professional coat may indicate a formal or work-related setting. Combined with the monotonous tone of the audio clue, it suggests she is in an emotionally detached state. Given these clues, we can infer that this sentence might be described by the female in a calm or neutral tone, without showing strong emotions.

### 近邻2：samplenew3_00033058

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：dissatisfaction, indifference
- 与query gold精确词面重合：∅
- 字幕：She is just like that, not very pleasant.
- 描述：In the text, the caption reads: "She's just that way with my mom." This phrase could be an evaluation or response from an individual towards their mother. Given the audio context where the individual's presents themselves in a flat and monotonous tone, indicating of feeling detached or disengaged emotionally, and considering the video clues showing the individual's's facial expressions as neutral without clear signs of mental stress or joy, we can infer that this statement might carry a tone of indifference or dissatisfaction. Therefore, this sentence could be seen as an individual's's assessment of their mother's behavior, aligning well with the overall emotional detachment portrayed by the individual.

### 近邻3：samplenew3_00090986

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, dissatisfaction, tension
- 与query gold精确词面重合：anxiety, tension
- 字幕：The boss is actually innocent, just like Li Junwei.
- 描述：In the text, the subtitle reads: "Actually, the boss, Li Junwei, is also innocent." This sentence may be the individual's defense or explanation of someone or a situation. Based on the audio clues describing the individual's trembling voice and the tone indicating feeling overwhelmed or under a lot of pressure, as well as the video clue of the woman's serious facial expression and furrowed eyebrows, we can infer that this sentence may carry a tense or anxious tone. The individual may feel nervous and anxious while defending someone or a situation because they believe that this person or situation is innocent. The person's emotional state appears to be tense, anxious, and may also have a hint of anger or dissatisfaction as they try to defend an innocent person.

### 近邻4：samplenew3_00005646

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：appreciation, emotional, gratitude, negative, stress
- 与query gold精确词面重合：∅
- 字幕：I hope you can stand with me in the wind and rain. High school righteousness did not pass the test, but you did. I am very touched.
- 描述：In the text, the subtitle says, "I hope you can stand with me in the wind and rain. High school love did not pass the test, but you did, and I am touched." This sentence may be an expression from the speaker to someone, possibly expressing gratitude or appreciation towards them. Based on the audio clues describing the speaker's trembling and shaking voice, as well as the stress and negative emotions that may be expressed in the speaker's tone of voice, we can infer that this sentence may carry a sense of gratitude and emotion. This sentence may be expressing gratitude for someone's support and companionship during difficult or challenging times.

### 近邻5：samplenew3_00091239

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：longing, melancholy, nostalgia, sadness
- 与query gold精确词面重合：∅
- 字幕：See the fallen leaves drifting in the courtyard.
- 描述：In the text, the subtitle content "Seeing the fallen leaves drifting in the courtyard" is likely a description of the environment in the video. Based on the clues in the video, such as the white and gold background and the women wearing traditional Chinese clothing, it can be inferred that the scene in the video is likely a courtyard or outdoor environment. The description of fallen leaves drifting implies autumn or seasonal changes, which may align with the traditional Chinese ceremony or performance shown in the video. Based on the audio clues describing the individual's possible experience of sadness, melancholy, nostalgia, and longing, it can be inferred that this sentence may carry a sense of sadness or nostalgia. Therefore, this sentence is likely describing the environment in the video and resonating with the individual's emotional state.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 15. samplenew3_00072568｜decline｜ΔF1 -0.333333

gold：disappointment, longing, regret, sadness

query字幕：It's just losing the days that I have been with you for more than ten years.

源标注描述：In the text, the subtitle reads: "It's just losing more than ten years of accompanying you." This sentence may express an emotion from the man to the other person. Based on the angry and sad facial expressions of the man in the video clues and the tense and anxious feeling in the individual's voice in the audio clues, we can infer that this sentence may carry a sense of sadness and disappointment. The man may be expressing longing and regret for the days of companionship lost, as well as the feeling of a broken or lost relationship with the person he is watching. This sentence expresses the man's emotional state towards the past and reflection on the current situation, aligning with the overall display of anger and sadness.

off原始输出：The character's emotional state is sadness, disappointment.

retrieval原始输出：The character's emotional state is sadness, loss.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|disappointment, sadness|0.666667|2|0|2|
|retrieval|loss, sadness|0.333333|1|1|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.333333，差值-0.333333。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：disappointment。
- 相对off新增未精确匹配gold的标签：loss。

gate：0.119943962；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00019333

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, despair, fear
- 与query gold精确词面重合：∅
- 字幕：I am in danger because two gangsters have moved into my mouse hole.
- 描述：In the text, caption content: "Rats in my house have moved in two gangsters, I'm in danger." This sentence might be a man's description of an event or situation. Based on the audio cues where the individual's's voice is shaking, their breathing becomes faster and shallower, and the tone and vocabulary reveal a sense of urgency and desperation, we can infer that this sentence expresses the man's's feelings of fear, anxiety, and despair. He mentions being in danger, further emphasizing the emergency and threat he is experiencing. Therefore, this sentence reflects the man's's current emotional state.

### 近邻2：samplenew3_00007764

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration, irritation, provocation, stress
- 与query gold精确词面重合：∅
- 字幕：If you don't like me, you can come at me.
- 描述：In the text, the caption reads: "If you don't like me, come at me." This phrase might be perceived as a challenge or threat by a man towards someone or some people. Considering the anger, frustration, and stress displayed by the man in the video cues, along with the trembling and accelerated speech rate of an individual's voice in the audio cues, we can infer that this sentence carries an antagonistic or threatening tone. The man might feel provoked or irritated by someone or some people, hence he uses this statement to express his dissatisfaction and intention to confront.

### 近邻3：samplenew3_00025001

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, sadness, stress
- 与query gold精确词面重合：sadness
- 字幕：Actually, I feel quite complicated in my heart.
- 描述：In the text, the subtitle reads, "Actually, I feel quite complicated inside." This sentence may be the inner monologue of the man during his process of thinking or reflection. Based on the serious facial expression and body language of the man in the video clues, as well as the description of increased heart rate, shallow and rapid breathing, and tense voice in the audio clues, we can infer that this sentence may express the man's complex emotions. These complex emotions may include anxiety, stress, anger, or sadness. Therefore, this sentence reflects the man's inner struggle and confusion that he is experiencing.

### 近邻4：samplenew3_00097503

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, praise
- 与query gold精确词面重合：∅
- 字幕：What a good girl this is
- 描述：In the text, the caption reads: "What a good little girl, huh." This sentence might be an appraisal or praise from the bald old man towards a certain female. Considering the emotional context described in the audio clues, which includes expressions of sadness, anger, and frustration, as well as visual cues such as the bald old man's's surprise or shock facial expression and tense or uneasy body language in the video, we can infer that the tone of this statement might be one of praise or admiration. Therefore, it is likely that this sentence is a form of praise or commendation from the bald old man for a particular female, aligning with the overall emotional state he exhibits.

### 近邻5：samplenew3_00013664

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：excitement, friendliness, humor, irony, liking, mockery, sarcasm
- 与query gold精确词面重合：∅
- 字幕：Like a man with a home
- 描述：In the text, the subtitle content "Liking a married man" can be inferred from the serious expression of the man and the woman's smiling and nodding in the video clues. Based on the description of the individual's happy and excited emotional state in the audio clues, as well as the friendly attitude of the woman in the video clues, we can deduce that this sentence may be the woman expressing her liking for the man in a joking or teasing manner. However, due to the man's serious expression and the environmental background in the video clues, this sentence may also carry a sarcastic or mocking meaning. Therefore, this sentence may be the woman expressing her liking for the man in a humorous way, but with some irony or sarcasm.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 16. samplenew3_00048216｜decline｜ΔF1 -0.333333

gold：excitement, friendliness, positive

query字幕：You also came to Rongzhou for work.

源标注描述：In the text, the subtitle reads: "You also came to Rongzhou for work." This sentence may be a greeting or inquiry from the man to the woman. Based on the description of the calm and steady voice of the woman in the audio clues, the more excited voice of the man, and the facial expression of the man smiling and laughing in the video clues, we can infer that this sentence may have a friendly or excited tone. Therefore, this sentence may be a positive greeting or inquiry from the man to the woman, consistent with the overall positive emotions displayed by the man.

off原始输出：The character's emotional state is friendly, inquiring, positive.

retrieval原始输出：The character's emotional state is positive, happy, satisfied.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|friendliness, inquiring, positive|0.666667|2|1|1|
|retrieval|happiness, positive, satisfaction|0.333333|1|2|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.333333，差值-0.333333。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：friendliness。
- 相对off新增未精确匹配gold的标签：happiness, satisfaction。
- 相对off移除未精确匹配gold的标签：inquiring。

gate：0.120018288；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00050383

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, direct, straightforward
- 与query gold精确词面重合：∅
- 字幕：Wu Xiong, you are a smart person, so I won't beat around the bush.
- 描述：In the text, with subtitles: "Brother Wu, you're a smart person, so I won't beat around the bush." This sentence might be an evaluation or response from one man to another. Given the speaker's's voice shaking and a slightly monotonous tone as described in the audio clues, along with the man's's confident and decisive demeanor shown in the video clues, we can infer that this sentence likely carries a direct and straightforward tone. Therefore, this sentence might be the man expressing his viewpoint or opinion directly, which would align with the overall sense of confidence he presents.

### 近邻2：samplenew3_00092261

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, frustration, skepticism, tension
- 与query gold精确词面重合：∅
- 字幕：When it comes to drawing, let's assume I am a scammer first, and then each of you can feel if there is anything a scammer can covet in your pockets.
- 描述：In the text, the caption reads: "When discussing what to depict, first assume I'm a con artist, then feel for yourselves if you have anything a con artist might covet in your pockets." This sentence might be the speaker's's skepticism or accusation towards those around them. Given the audio clues, the speaker's's voice is tense, agitated, with an attacking and confrontational tone, and they speaks quickly, indicating they might feel angry, frustrated, anxious, and tense. Therefore, this sentence could be interpreted as the speaker's's skepticism or accusation towards their surroundings, expressing their dissatisfaction and lack of trust.

### 近邻3：samplenew3_00035753

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：incredulous, surprise
- 与query gold精确词面重合：∅
- 字幕：This kind of gift is unheard of.
- 描述：In the text, caption content: "Such a gift, unheard of." This sentence might be spoken by one man to another. Given the video clues, such as the serious expression and body language of the man, as well as the voice fluctuations and tone variations in the audio that describe multiple emotions of personal experiences, we can infer that this statement might carry an element of surprise or incredulity. Therefore, this sentence could be spoken by one man to another, expressing his astonishment and disbelief at a particular gift or situation.

### 近邻4：samplenew3_00008925

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, pride, satisfaction
- 与query gold精确词面重合：∅
- 字幕：
- 描述：In the text, the subtitle reads: "That's what I still do for morning runs." This sentence is likely a male speaker's response or self-description regarding a certain topic. Based on the description of the speaker's clear and confident tone in the audio cues and the comfortable and at ease emotion displayed by the man in the video cues, we can infer that this sentence may carry a tone of pride or confidence. The male speaker may be talking about his morning running habit and feeling satisfied or proud of it. Therefore, this sentence expresses the positive emotional state of the male speaker.

### 近邻5：samplenew3_00086943

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, tension
- 与query gold精确词面重合：∅
- 字幕：But wife, now I want to tell you my decision. I plan to give up.
- 描述：In the text, the subtitle reads: "But now I want to tell you my decision, I am planning to give up." This sentence might be what a man says to his wife. Based on the audio cues described in the personal voice trembling and shaking, along with very slow speech pace, it indicates that he is experiencing intense emotional stress and difficulty. This sentence might be him expressing a significant decision, and due to his emotional state, he may feel extremely tense and anxious. Therefore, this sentence carries an air of tension and unease, which alignss with the described personal emotional state in the audio clues.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 17. samplenew3_00049162｜decline｜ΔF1 -0.333333

gold：anticipatory, joy, positive

query字幕：Time flies by quickly.

源标注描述：In the text, the caption reads: "Time flies so fast." This phrase might be uttered by a man in the video. Given the audio clues that describe a personal high-pitched singing, energetic and enthusiastic rhythm, as well as the video hints showing the man's friendly, approachable, and cheerful mood state, we can infer that this phrase might be the man expressing his sentiment about the fleeting nature of time or his excitement and anticipation for the fast-paced life. Therefore, this phrase likely carries a positive emotion, in line with the overall joyful and pleasant demeanor that the man exhibits.

off原始输出：The character's emotional state is positive, joyful, satisfied.

retrieval原始输出：The character's emotional state is positive, enjoyment, nostalgia.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|joy, positive, satisfaction|0.666667|2|1|1|
|retrieval|enjoyment, nostalgia, positive|0.333333|1|2|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.333333，差值-0.333333。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：joy。
- 相对off新增未精确匹配gold的标签：enjoyment, nostalgia。
- 相对off移除未精确匹配gold的标签：satisfaction。

gate：0.120022267；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "enjoyment", "unmatched_gold_label": "joy"}]}

实际5近邻证据：

### 近邻1：samplenew3_00072404

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction
- 与query gold精确词面重合：∅
- 字幕：Don't say "if" anymore if they have affected the Nirvana Plan.
- 描述：In the text, the caption reads: "Don't keep saying they affected the rebirth plan." This sentence might be a man's response or advice to someone or something. Given the description of an individual speaking in a high-pitched, agitated manner and with a tone indicating of frustration or anger, we can infer that this sentence may be conveyed with a sense of dissatisfaction or anger. Therefore, this sentence could be the man's's way of expressing his dissatisfaction or criticism towards someone or something, which aligns with his overall negative emotion.

### 近邻2：samplenew3_00067299

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, enthusiasm, positive
- 与query gold精确词面重合：positive
- 字幕：This mushroom substitute for crop stalks is likely to have better effects.
- 描述：In the text, caption reads: "This grass substitute for crop stalks might yield better results." This sentence could be part of a speaker's's discussion on the potential benefits of plant-based fertilizers. Given the speaker's's confident and enthusiastic tone as described in the audio cues, along with the caption mentioning the effect of grass replacing crop stalks, we can infer that this sentence is part of the speaker's's discourse on assessing the effects of usinging plant-based fertilizers. The speaker's's positive sentiment and enthusiasm about the topic suggests they they firmly believe that usinging plant-based fertilizers can lead to superior results.

### 近邻3：samplenew3_00062232

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, leadership, positive
- 与query gold精确词面重合：positive
- 字幕：You belong to the first stage of breaking the ice, which is very important. I will take care of the remaining second stage.
- 描述：In the text, caption content: "You belong to the first wave that breaks the ice and is crucial, the rest of the second stage is left to me." This sentence could be a man's's evaluation or commitment to someone or a team. Based on the video clues showing his enthusiasm, confidence, and decisive body language, as well as the audio clues describing the man's's firm and confident tone and control over his emotions, we can infer that this sentence might be the man expressing his affirmation and appreciation for someone or a team's work or performance in the first phase, and promising to continue supporting and assisting them in the second phase. This sentence conveys the man's's positive, confident, and leadership emotional state, which aligns with his positive emotions shown in the video.

### 近邻4：samplenew3_00114981

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：encouragement, positive, support
- 与query gold精确词面重合：positive
- 字幕：Your insistence on justice and Li Fangning's are consistent. Both of you hope to change the current situation of society by speaking out. No problem.
- 描述：In the text, the subtitle reads: "Your commitment to justice is consistent with Li Fangning. Both of you hope to change the current situation of society through speaking out, and that's no problem." This sentence may be the man's evaluation or support for someone or a group. Based on the audio clues describing a fast-paced, high-pitched, and urgent voice, as well as the video clues of the man's serious expression and formal body language, we can infer that this sentence may carry an encouraging or supportive tone. The man may be expressing recognition and appreciation for someone or a group, as well as supporting their actions to change the current situation of society. Therefore, this sentence may convey a positive and supportive emotional state.

### 近邻5：samplenew3_00080179

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, disappointment, dissatisfaction, overwhelm, under immense pressure
- 与query gold精确词面重合：∅
- 字幕：Zhang Zhongping is no longer interested.
- 描述：In the text, the caption reads: "Zhang Zhongping is no longer worth considering." This sentence might be a personal evaluation or response to Zhang Zhongping. Given the context of the audio cues, including an aggressive tone, sharpness, and a sense of hopelessness in the voice, it can be inferred that this phrase carries a negative emotional undertone. The individual may feel disappointed, angry, or dissatisfied with Zhang Zhongping, possibly feeling overwhelmed or under immense pressure by Zhang Zhongping. Thus, this sentence expresses the individual's negative feelings and evaluation towards Zhang Zhongping.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 18. samplenew3_00012271｜decline｜ΔF1 -0.333333

gold：confidence, control, positive attitude

query字幕：Fine wine

源标注描述：In the text, the caption reads: "Fine Wines and Beverages." This phrase might be a term or theme that the speaker mentioned in their speech. Given the video cues, which describe the speaker's as confident, in control, and with well-lit surroundings, we can infer that the speaker has a positive attitude, possibly introducing or praising fine wines and beverages. This alignss with the emotional state of confidence and control depicted in the video cues.

off原始输出：The character's emotional state is appreciation, pride, confidence.

retrieval原始输出：The character's emotional state is appreciation, admiration, positive.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|appreciation, confidence, pride|0.333333|1|2|2|
|retrieval|admiration, appreciation, positive|0.000000|0|3|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.333333变为0.000000，差值-0.333333。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：confidence。
- 相对off新增未精确匹配gold的标签：admiration, positive。
- 相对off移除未精确匹配gold的标签：pride。

gate：0.119951695；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": [{"prediction_label": "positive", "unmatched_gold_label": "positive attitude"}]}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00056786

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：positive, pride, satisfaction
- 与query gold精确词面重合：∅
- 字幕：But I can't help but say a few more words to praise our wine.
- 描述：In the text, caption content: "But still, I just can't help but say more to praise our wine." Given the body language of the speaker, characterized by confidence and control as described in the video clues, along with the audience's focused attention and interest in the content of the speech, and the deliberate and intentional expression and gestures of the speaker, it can be inferred that the speaker is in a positive emotional state, feeling proud and satisfied. This caption content indicates that the speaker just can't help praising the wine, which further supports the positive emotional state of the speaker.

### 近邻2：samplenew3_00074241

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：accountable, concentrated, engaged, responsible, seriousness
- 与query gold精确词面重合：∅
- 字幕：We both apologize in front of all the teachers and students in the school.
- 描述：In the text, the caption reads: "We are going to make an apology in front of the entire school staff and students." This sentence could be one of the topics being discussed by a man. Based on the video hints showing the man listening attentively and responding to what is being said, along with his body language that indicates focus and seriousness, we can infer that this sentence might describe an action requiring thoughtful and focused consideration - making an apology in front of the entire school staff and students. The topic may evoke a sense of responsibility and accountability in the man, which alignss well with his overall display of engagement, concentration, and seriousness.

### 近邻3：samplenew3_00080179

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, disappointment, dissatisfaction, overwhelm, under immense pressure
- 与query gold精确词面重合：∅
- 字幕：Zhang Zhongping is no longer interested.
- 描述：In the text, the caption reads: "Zhang Zhongping is no longer worth considering." This sentence might be a personal evaluation or response to Zhang Zhongping. Given the context of the audio cues, including an aggressive tone, sharpness, and a sense of hopelessness in the voice, it can be inferred that this phrase carries a negative emotional undertone. The individual may feel disappointed, angry, or dissatisfied with Zhang Zhongping, possibly feeling overwhelmed or under immense pressure by Zhang Zhongping. Thus, this sentence expresses the individual's negative feelings and evaluation towards Zhang Zhongping.

### 近邻4：samplenew3_00114529

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, confidence, control, excitement
- 与query gold精确词面重合：confidence, control
- 字幕：We establish a data group.
- 描述：In the text, caption content: "We set up a data team." This sentence could be an important piece of information mentioned by a man during a speech or discussion. Based on the video cues, such as the serious expression and body language of the man, along with the professional setting indicated by the background, we can infer that this sentence might have been mentioned by the man when introducing their ongoing work or plans. Considering the audio cues, where the speaker's's voice is calm and organized, and there is a slight rise in pitch, which suggests excitement or anticipation, we can deduce that the man might feel a sense of control and confidence while mentioning this data team. This inference is grounded in the man's's facial expressions, body language, environmental context, and vocal characteristics described in the audio.

### 近邻5：samplenew3_00067299

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, enthusiasm, positive
- 与query gold精确词面重合：confidence
- 字幕：This mushroom substitute for crop stalks is likely to have better effects.
- 描述：In the text, caption reads: "This grass substitute for crop stalks might yield better results." This sentence could be part of a speaker's's discussion on the potential benefits of plant-based fertilizers. Given the speaker's's confident and enthusiastic tone as described in the audio cues, along with the caption mentioning the effect of grass replacing crop stalks, we can infer that this sentence is part of the speaker's's discourse on assessing the effects of usinging plant-based fertilizers. The speaker's's positive sentiment and enthusiasm about the topic suggests they they firmly believe that usinging plant-based fertilizers can lead to superior results.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 19. samplenew3_00071523｜decline｜ΔF1 -0.333333

gold：anxiety, depression, pressure, unease

query字幕：I did indeed suffer a lot of expenses for the blood sea head.

源标注描述：In the text, caption content: "I indeed bear the debt of blood and head for phone bills." This sentence might be a man expressing his distress or dissatisfaction. Given the serious and sorrowful facial expression of the man in the video clues, as well as the heavy atmosphere of the environment, we can infer that this phrase may carry a sense of depression or unease. Furthermore, according to the audio clues describing the high pitch and urgency of the speaking speed, we can speculate that the man may feel under pressure or anxious. Therefore, this sentence might be the man expressing his distress or dissatisfaction, which is consistent with the overall solemn and sorrowful emotion he exhibits.

off原始输出：The character's emotional state is stress, anxiety.

retrieval原始输出：The character's emotional state is stress, frustration.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, stress|0.333333|1|1|3|
|retrieval|frustration, stress|0.000000|0|2|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.333333变为0.000000，差值-0.333333。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：anxiety。
- 相对off新增未精确匹配gold的标签：frustration。

gate：0.119969733；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [{"prediction_label": "stress", "unmatched_gold_label": "pressure"}], "retrieval": [{"prediction_label": "stress", "unmatched_gold_label": "pressure"}]}

实际5近邻证据：

### 近邻1：samplenew3_00010211

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, contemplation, doubt, fear, melancholic, pressure, sadness, self-blame
- 与query gold精确词面重合：anxiety, pressure
- 字幕：I, Liu Qing, cannot complete the task.
- 描述：In the text, the subtitle content "I, Liu Qing, cannot complete the task" may be an expression of the man's confusion, frustration, or feelings of incompetence. Based on the video clue of the man closing his eyes and lowering his head, as well as the quiet and simple environment, we can infer that he may be experiencing a contemplative, sad, or melancholic emotion. Additionally, based on the audio clue of the slight tremor in the individual's voice and the increased speech rate, we can speculate that he may be experiencing intense negative emotions such as fear, anxiety, or pressure. Therefore, this sentence may be his expression of doubt or self-blame regarding his abilities, aligning with his overall display of contemplation and negative emotions.

### 近邻2：samplenew3_00094829

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confusion, disappointment, regret, stress, uncertainty
- 与query gold精确词面重合：∅
- 字幕：Since I gave him money.
- 描述：In the text, caption content: "Since I gave him the money." This sentence might be what a man said in the video. Given the description of an individual's's voice shaking in the audio clues, which could indicate nervousness or anxiety, and a flat tone suggesting emotional detachment, combined with the video clues showing the man's's facial expressions and body language expressing sadness or grief, we can infer that this sentence might be the man expressing his confusion, disappointment, or stress about a particular situation or event. He might be describing giving someone money, hinting at uncertainty or regret over this decision or action.

### 近邻3：samplenew3_00114096

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction, overwhelm, unhappiness
- 与query gold精确词面重合：∅
- 字幕：Very uncomfortable with those little ones and shameless people.
- 描述：In the text, the caption reads: "Very uncomfortable around those little ones and the shameless." This sentence could be this person's's evaluation or reaction to certain individuals or situations. Given the vocal cues described in the audio, such as a tense, anxious voice with trembling, and the tone and choice of words that indicate anger and frustration, we can infer that the statement might carry an element of anger and dissatisfaction. The person may feel overwhelmed by certain individuals or circumstances and be unhappy and angry about their behavior or qualities. Therefore, this sentence expresses their negative appraisal and emotional response towards these individuals or situations.

### 近邻4：samplenew3_00101531

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：annoyance, anxiety, dissatisfaction, frustration, stress
- 与query gold精确词面重合：anxiety
- 字幕：This person under my hand is also a headache for me.
- 描述：In the text, the subtitle reads, "This guy under my hand is giving me a headache." This sentence may be the man's evaluation or reaction to someone or a situation. Based on the man's contemplative state, slight frown, and the formal or professional environment indicated by the video clues, we can infer that this sentence may carry a sense of dissatisfaction or annoyance. Additionally, based on the description of the speaker's voice in the audio clues, including the slight tremor, nervousness, and feeling of pressure, we can further speculate that this sentence may be the man expressing his anxiety, stress, and frustration towards someone or a situation. Therefore, this sentence may be the man complaining or expressing his frustration and dissatisfaction.

### 近邻5：samplenew3_00021090

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：The first proved the operation of the planet, the trajectory of the image comet, and the plagiarism of the sea.
- 描述：In the text, the subtitle content: "First proved the motion of planets, followed by the trajectory of comets, and the plagiarism of the ocean." This sentence may be some scientific or astronomical content mentioned by the man in the conversation. Based on the audio clues describing the individual's high-pitched and clear voice, relatively fast speech rate, and the video clue of the man's neutral expression and focused attitude, we can infer that this sentence may be part of a knowledgeable or professional discussion by the man. Therefore, this sentence may not involve personal emotional states but rather describe some scientific or astronomical facts or viewpoints.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 20. samplenew3_00111680｜decline｜ΔF1 -0.333333

gold：admiration, calm, gratitude, support

query字幕：You are the most precious to me.

源标注描述：In the text, the caption reads: "It's the most precious to me." This phrase could be something a man might say to a woman. Given the audio clues that describe a somewhat muddled personal voice with an undertone of excitement, and the video clues showing the man with a serious expression and focused on his smartphone, we can infer that this statement might carry a tone of gratitude or admiration. The man may be expressing his gratitude towards the woman, considering her as the most precious to him. This alignss with the woman's calm demeanor and supportive role in the situation.

off原始输出：The character's emotional state is gratitude, admiration.

retrieval原始输出：The character's emotional state is gratitude, appreciation.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|admiration, gratitude|0.666667|2|0|2|
|retrieval|appreciation, gratitude|0.333333|1|1|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.333333，差值-0.333333。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：admiration。
- 相对off新增未精确匹配gold的标签：appreciation。

gate：0.119940117；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "appreciation", "unmatched_gold_label": "admiration"}]}

实际5近邻证据：

### 近邻1：samplenew3_00025298

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：disappointment, resignation
- 与query gold精确词面重合：∅
- 字幕：But I feel like this is as far as it can go.
- 描述：In the text, the caption reads: "But I think that's about it." This sentence might be spoken by a man in conversation. Given the audio cues described by the rustling of leaves and the howling wind, as well as the video clues showing the man expressing pain or sorrow through his body language and facial expressions, we can infer that the tone might be one of resignation or disappointment. The man could be conveying his feelings about the limitations or impossibility of resolving a particular situation or issue. The supportive or empathetic posture and positioning of the woman also corroborates this inference. Therefore, this sentence might reflect the man's negative emotion or attitude towards the current situation.

### 近邻2：samplenew3_00015883

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, seriousness, tension
- 与query gold精确词面重合：∅
- 字幕：In the future, if you follow me to do things, you must always explain to the government.
- 描述：In the text, caption content: "From now on, whenever you do something, you'll have to account for it to the governor's." This sentence might be spoken by one man to another. Given the audio cues, the individual's's tone is clear, confident, with a relatively high pitch, speaking at a fast pace, and with a slight tremor in their voice, we can infer that this sentence may carry a sense of urgency or importance. Therefore, this sentence might be the man emphasizing that the other person must account for matters to the governor, displaying a serious or tense emotional state. This contrasts with the emotional state portrayed in the video clues where the man appears friendly and focused, suggesting that the other person did not follow his request or expectations, causing him to feel tense or anxious.

### 近邻3：samplenew3_00003126

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：eagerness, excitement, passion
- 与query gold精确词面重合：∅
- 字幕：I just want to get back to the state of learning, as long as I can learn new knowledge, it doesn't matter if it's in college or not.
- 描述：In the text, the caption reads: "I just want to get back into the rhythm of learning; it's the acquisition of new knowledge that matters, whether it's at a university or not." This statement conveys a person's's longing for learning and interest in gaining new knowledge. Given the tone conveyed by the audio cues, which suggests determination and focus, as well as the emotional expressions shown in the video such as frustration, defeat, or hostility, we can infer that this line might be spoken with a tone that carries an element of eagerness and excitement. Thus, this sentence expresses the individual's passion for learning and desire to expand their knowledge, aligning with their overall positive demeanor.

### 近邻4：samplenew3_00011796

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：commanding, defensiveness, tension, urgency
- 与query gold精确词面重合：∅
- 字幕：You go in first and see if there is anyone worth seeing. If not, hurry up and come out, Qiyi, you take it.
- 描述：In the text, the caption reads: "You go in first to see if there's anyone inside. Don't waste time, get out quick once you're done. Uncle, you hold on." This sentence might be an instruction or command directed from one person to another. Given the audio clue with its calm and organized tone of the male voice, and the video clue showing intense or emotionally charged body language and facial expressions between the two individuals, we can infer that this sentence might carry a sense of urgency or command. Therefore, this sentence could be a strong request or directive, fitting with the tense or defensive postures shown by the characters in the video.

### 近邻5：samplenew3_00020168

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：entertainment, joy, praise
- 与query gold精确词面重合：∅
- 字幕：Among all the classmates, the gift given by student Liu Xing is the most meaningful.
- 描述：In the text, caption content: "Among all the classmates, Liu Xing's gift is the most meaningful." Based on the audio clues with its higher pitch and relatively faster pace, as well as the video clues showing the man's's comical facial expressions and laughter, we can infer that this sentence might be an evaluation or reaction to the gift given by Liu Xing. Given that both the audio and video clues depict the man in a positive emotional state, we can deduce that this statement is likely a form of praise or affirmative expression, aligning with his overall display of joy and entertainment.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 21. samplenew3_00059981｜decline｜ΔF1 -0.321429

gold：anxiety, concern, disagreement, excitement, nervousness

query字幕：That would be too deliberate, Teacher Wu.

源标注描述：In the text, the subtitle content "That would be too deliberate, Teacher Wu." This sentence is likely a response from the elderly Asian man to a suggestion or viewpoint. Based on the audio clues describing a slight tremor in the individual's voice, which may indicate anxiety or nervousness, as well as a slightly faster speech rate, which may suggest excitement or energy, we can infer that this sentence may carry a tone of concern or disagreement. Therefore, this sentence is likely the man's response expressing disagreement or considering the suggestion or viewpoint to be too deliberate.

off原始输出：The character's emotional state is concern, disagreement.

retrieval原始输出：The character's emotional state is doubt, concern, worry.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|concern, disagreement|0.571429|2|0|3|
|retrieval|concern, doubt, worry|0.250000|1|2|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.571429变为0.250000，差值-0.321429。
- TP变化-1，FP变化+2，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：disagreement。
- 相对off新增未精确匹配gold的标签：doubt, worry。

gate：0.119992495；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "worry", "unmatched_gold_label": "anxiety"}, {"prediction_label": "worry", "unmatched_gold_label": "nervousness"}]}

实际5近邻证据：

### 近邻1：samplenew3_00008906

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：Li Dakang is best without any problems.
- 描述：In the text, based on the provided information, it is not possible to infer the character's emotional state from the subtitle content. The mention of "Li Dakang has no problem, the better" in the subtitle does not have a clear emotional tone, so it is not possible to determine the character's emotional state. To speculate on the character's emotional state, it is necessary to analyze the facial expressions and body language in the video clues, as well as the sound characteristics in the audio clues.

### 近邻2：samplenew3_00069581

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, stress, tension
- 与query gold精确词面重合：anxiety, concern
- 字幕：Comrade Chen Yanshi, the former chief prosecutor, must not have any accidents.
- 描述：In the text, the caption reads: "Comrade Chen Yishan, the old procurator, must not suffer any mishaps." Based on the audio cues that describe a fast pace, high pitch, and an intonation suggesting defensiveness and aggression, we can infer that this phrase might carry a sense of tension and anxiety. Simultaneously, the background bookshelves in the video hint that the man may be in a professional or scholarly setting, which could increase his stress and tension. Consequently, this sentence could be a warning or emphasis directed at Comrade Chen Yishan, expressing concern for his safety and smoothness.

### 近邻3：samplenew3_00013102

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration
- 与query gold精确词面重合：∅
- 字幕：Can you do it or not?
- 描述：In the text, the subtitle says, "Can you not do it?" This sentence may be a response or comment from the older man to the other man. Based on the description of the individual's angry and frustrated emotions in the audio clues, as well as the video clues of the older man actively participating in the conversation, maintaining eye contact, and having a relaxed posture, we can infer that this sentence may carry a tone of challenge or dissatisfaction. Therefore, this sentence may be the older man questioning or refuting the other man, aligning with the overall negative emotions displayed by the individual.

### 近邻4：samplenew3_00073262

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, excitement, positive, satisfaction
- 与query gold精确词面重合：excitement
- 字幕：If everything goes well, we can enter the urban area of Chongqing tomorrow.
- 描述：In the text, the caption reads: "Assuming everything goes well, we should be able to advance into the city of Chongqing tomorrow." Based on the video clues, which depict the elderly man with a serious expression and focused demeanor, and the audio clues featuring an energetic and enthusiastic musical rhythm, we can infer that this sentence likely refers to the man discussing the progress in Chongqing, and he is excited and satisfied at the prospect of successfully entering the city. This sentence expresses his positive attitude towards the progress in Chongqing and his anticipation, aligning with his overall portrayal of concentration and vitality.

### 近邻5：samplenew3_00096867

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：depression, lacking motivation, sadness, tiredness
- 与query gold精确词面重合：∅
- 字幕：You can't stop talking even when you're eating.
- 描述：In the text, the subtitle reads: "Eating doesn't stop your talking." Based on the video hints, including the serious expression and body language of the man, as well as the presence of a table and phone in the environment, it can be inferred that this is likely a social or professional setting, possibly a business meeting or gathering with friends or colleagues. Considering the audio cues, the person's speaks with a low, monotonous tone at a slower pace, suggesting they might feel sad, depressed, tired, or lacking motivation. Therefore, this phrase could be an ironic or playful way to express towards the man, implying he might have been continuously speaking or expressing his opinions without considering others' feelings in the situation. The statement might carry a light-hearted or humorous tone, contrasting with the man's overall serious and focused demeanor.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 22. samplenew3_00010449｜decline｜ΔF1 -0.321429

gold：confusion, discomfort, dissatisfaction, longing

query字幕：I also want to adapt to this kind of life.

源标注描述：In the text, the subtitle content says, "I also want to adapt to this kind of life." This sentence may express the woman's discomfort or confusion with her current life situation. Based on the video clues of the woman crying and having a sad expression, as well as the potted plant in the background of the environment, we can infer that she may be going through a difficult or painful situation. At the same time, based on the confident and determined voice characteristics of the individual in the audio clues, we can infer that this sentence may carry a sense of longing or dissatisfaction. The woman may feel unable to adapt to her current life situation and may be hoping for a change or seeking a solution.

off原始输出：The character's emotional state is longing, confusion, sadness.

retrieval原始输出：The character's emotional state is sadness, contemplation, longing, desire.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|confusion, longing, sadness|0.571429|2|1|2|
|retrieval|contemplation, desire, longing, sadness|0.250000|1|3|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.571429变为0.250000，差值-0.321429。
- TP变化-1，FP变化+2，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：confusion。
- 相对off新增未精确匹配gold的标签：contemplation, desire。

gate：0.120000787；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00030581

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：depression, despair, dissatisfaction, sadness, unwillingness
- 与query gold精确词面重合：dissatisfaction
- 字幕：We don't want this kind of life.
- 描述：In the text, the caption reads: "We don't want to live like this." This phrase might be a woman expressing her dissatisfaction or disinterest in her current lifestyle. Given the audio clues where the female voice is described as pitched high and filled with emotion, accompanied by sobbinging sounds, and considering the video hints of the woman showing a mix of surprise and sadness, we can infer that the statement might carry a sense of sadness, despair, or depression. Therefore, this sentence could be the woman expressing her dissatisfaction or unwillingness towards her current lifestyle, aligning well with the overall emotional tone she portrays.

### 近邻2：samplenew3_00013437

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：distress, sadness, struggle
- 与query gold精确词面重合：∅
- 字幕：
- 描述：In the text, the subtitle reads: "It is a constant and endless hurt on this day." This sentence may be a description of the individual's emotional state or experience. Based on the fluctuations in the individual's voice described in the audio clues and the surprise, sadness, and vulnerability displayed by the woman in the video, we can infer that this sentence may be describing a continuous and endless hurt or struggle, aligning with the overall sadness and difficulty exhibited by the woman. This sentence may imply that the individual is going through a profound pain or distress, possibly related to personal or cultural issues.

### 近邻3：samplenew3_00000211

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, tension, uncertainty
- 与query gold精确词面重合：∅
- 字幕：To have a clearer understanding of one's own personality.
- 描述：In the text, the caption reads: "Getting clearer about one's personality." This sentence might be a woman's introspection or self-reflection. Given the audio cues that describe an individual feeling anxious, tense, and uncertain, as well as the video clues showing the woman with a neutral expression and slumped body language, we can infer that this sentence might be her pondering over her personality traits, attempting to better understand her emotional state and the reasons behind her emotional distress. Therefore, this sentence could be a way for the woman to seek self-awareness and emotional adjustment, aligning with the complex emotions she exhibits overall.

### 近邻4：samplenew3_00012635

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：disappointment, frustration, hope, sadness
- 与query gold精确词面重合：∅
- 字幕：But I hope that Nian Gengyao can leave the country soon, and Hua Fei can also have less.
- 描述：In the text, the subtitle reads: "But hoping that Nian Gengyao can leave soon, and the Empress Huafu can have less influence." This sentence may express the woman's expectation or hope towards a certain character. Based on the description of the individual experiencing mixed negative emotions such as sadness, disappointment, and frustration in the audio clues, as well as the woman's display of sadness and anger in the video clues, we can infer that this sentence may carry a sense of hope or expectation. The woman may hope for Nian Gengyao to leave soon in order to reduce the troubles and pain caused by Empress Huafu. This sentence expresses the woman's dissatisfaction with her situation and her hopes for the future.

### 近邻5：samplenew3_00091580

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration
- 与query gold精确词面重合：∅
- 字幕：Even if you kill me and curse me
- 描述：In the text, the subtitle reads, "Even if you kill me and curse me." This sentence may be a strong reaction or expression from the speaker towards someone or a certain situation. Based on the description of strong anger and frustration in the speaker's voice, as well as the aggressive and confrontational tone, we can infer that this sentence is spoken by the speaker in a state of anger and frustration. This sentence expresses the speaker's extreme dissatisfaction and anger towards someone or a certain situation, even willing to endure extreme consequences. This aligns with the woman's display of sadness and difficulty in the video, suggesting that the speaker feels anger and helplessness towards the woman's situation or ordeal.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 23. samplenew3_00101806｜decline｜ΔF1 -0.318182

gold：anxiety, bewilderment, discontent, dissatisfaction, frustration, perplexity, stress, unhappiness

query字幕：What kind of days am I living day by day? What am I doing?

源标注描述：In the text, the caption reads: "What kind of life am I living day by day? This is it." This phrase might be someone speaking to themselves or expressing dissatisfaction. Considering the visual clues from the woman's serious expression and body language, as well as the audio hints of her hurried speech and urgent tone, we can infer that this sentence may convey a sense of frustration, discontent, or bewilderment. The woman might be experiencing stress, anxiety, or dissatisfaction, feeling unhappy or perplexed about her life or a particular particular situation.

off原始输出：The character's emotional state is confused, dissatisfied, stressed, anxious.

retrieval原始输出：The character's emotional state is anger, frustration, confusion.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, confusion, dissatisfaction, stress|0.500000|3|1|5|
|retrieval|anger, confusion, frustration|0.181818|1|2|7|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.500000变为0.181818，差值-0.318182。
- TP变化-2，FP变化+1，FN变化+2。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：anxiety, dissatisfaction, stress。
- 相对off新增未精确匹配gold的标签：anger。
- 相对off新增命中的gold标签：frustration。

gate：0.120113507；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [{"prediction_label": "confusion", "unmatched_gold_label": "bewilderment"}, {"prediction_label": "confusion", "unmatched_gold_label": "perplexity"}], "retrieval": [{"prediction_label": "confusion", "unmatched_gold_label": "bewilderment"}, {"prediction_label": "confusion", "unmatched_gold_label": "perplexity"}]}

实际5近邻证据：

### 近邻1：samplenew3_00013439

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, disappointment, dissatisfaction
- 与query gold精确词面重合：anxiety, dissatisfaction
- 字幕：But the attention of this fire ship route is not at all on the approval document.
- 描述：In the text, the subtitle reads, "But the attention on this fireboat route is not on the approval document at all." This sentence may be the individual's evaluation or reaction to a certain issue or situation. Based on the audio clues describing a fast speech rate, high pitch, and a confident and decisive tone, we can infer that this sentence may carry a strong emotion, possibly a feeling of dissatisfaction, anxiety, or disappointment. Therefore, this sentence may be the individual's criticism or complaint about something, aligning with the complex and multifaceted emotional state exhibited by the individual as a whole.

### 近邻2：samplenew3_00005042

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, blame, criticism, disappointment, dissatisfaction, tension, unease
- 与query gold精确词面重合：anxiety, dissatisfaction
- 字幕：You are the one who made the company like this, so you are the one at fault.
- 描述：In the text, the caption reads: "It's wrong for you to have made the company that way." This phrase could be the woman's assessment or reaction to someone or something. Considering the audio clues that describe a trembling voice and tone, as well as the video hints of the woman's hesitancy, introspective gaze, and elegant attire, we can infer that this sentence might carry a tense, anxious, or uneasy emotion. The woman may be expressing her dissatisfaction or disappointment towards someone or something, while also feeling under immense pressure. Therefore, this statement could be a form of criticism or blame, fitting with the complex emotions she exhibits overall.

### 近邻3：samplenew3_00056512

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, care, concern, empathy, fear, reassurance
- 与query gold精确词面重合：anxiety
- 字幕：There will also be some inconvenience in doing surgery.
- 描述：In the text, the caption reads: "Surgeries can also cause a certain amount of distress." This sentence might be a woman offering comfort or understanding to a patient. Given the high emotional arousal level described in the audio clues, which indicates feelings of anxiety or fear, and the woman's serious facial expression and focused demeanor shown in the video clues, we can infer that this sentence likely reflects her attempt to empathize with and reassure the patient about their concerns and distress regarding surgery. The woman may be attempting to alleviate the patient's tension, expressing care and empathy for them.

### 近邻4：samplenew3_00076962

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, blame, criticism
- 与query gold精确词面重合：∅
- 字幕：How many years have you been carrying the burden of words?
- 描述：In the text, the subtitle reads, "How many years have you been carrying the burden of writing characters?" This sentence may be a questioning or blaming statement directed at the individual. Based on the description of the individual's voice trembling and shaking in the audio clues, as well as the aggressive and confrontational tone, we can infer that this sentence may carry an angry or provocative tone. Therefore, this sentence may be an expression of blame or criticism, consistent with the negative emotions displayed by the individual in the audio.

### 近邻5：samplenew3_00022634

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：blame, criticism, excitement, sadness, surprise
- 与query gold精确词面重合：∅
- 字幕：You don't even have basic impulses, you don't care from the root.
- 描述：In the text, the caption reads: "You lack even the most basic impulse, you just don't care at your core." This phrase could be a male voice's's evaluation or response to someone or a situation. Given the audio cues of a fast-paced, sharp tone and an emphasis on the importance of conveying the message with enthusiasm, we can infer that the tone might carry a critical or blaming nature. The woman's's varying emotional states depicted in the video clues, such as surprise, excitement, and sadness, may relate to the emotions conveyed by this statement. However, without specific background information or further description of the context, we cannot determine the exact meaning or target of this sentence.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 24. samplenew3_00106018｜decline｜ΔF1 -0.285714

gold：anticipation, challenge, curiosity, uncertainty

query字幕：I am really interested in hearing your thoughts

源标注描述：In the text, the caption reads: "I do wonder what you think about it." This phrase could be a response or invitation from an Asian man to someone else. Given the description of the speaker's's voice being shaky and hesitant, along with a tone that is provocative and confrontational, we can infer that this statement might carry an element of uncertainty or challenge. Therefore, this sentence could be a way of expressing curiosity, anticipation, or a challenge, consistent with the overall sense of curiosity and interest shown by the Asian man.

off原始输出：The character's emotional state is open, receptive, curious.

retrieval原始输出：The character's emotional state is open to discussion, interested in others' perspectives.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|curiosity, open, receptive|0.285714|1|2|3|
|retrieval|interested in others' perspectives, open to discussion|0.000000|0|2|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.285714变为0.000000，差值-0.285714。
- TP变化-1，FP变化+0，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：curiosity。
- 相对off新增未精确匹配gold的标签：interested in others' perspectives, open to discussion。
- 相对off移除未精确匹配gold的标签：open, receptive。

gate：0.120008096；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00102089

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, cautious, concern
- 与query gold精确词面重合：∅
- 字幕：I cannot risk the country and the people's livelihood for this.
- 描述：In the text, the caption reads: "I cannot risk the empire and nation for such a gamble." This statement could reflect an individual expressing their concerns and unwillingness to take risks. Given the tension and anxiety evident in the person's's voice as described by the audio clues, and the mix of solemnity and irony in their facial expressions as shown in the video clues, we can infer that this statement might carry a tone of concern and caution. The individual may be discussing a significant decision or action, and they is worried about the risks associated with taking such a step, thereby expressing their stance against it. This alignss with the overall sense of tension and anxiety exhibited by the individual.

### 近邻2：samplenew3_00049811

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：authoritative, concentrated, confidence, focused
- 与query gold精确词面重合：∅
- 字幕：Both are the holy and unparalleled national history.
- 描述：In the text, the caption reads: "A tale of unparalleled imperial history under Heaven." This sentence might be spoken by a male narrator recounting a significant historical event or fact. Given the speaker's's confident and restrained tone, as well as the emphasis on certain wordsings and phrases suggested by the audio clues, we can infer that this statement is intended to convey importance or authority. Furthermore, the video hints at the man's's intense focus and concentration while reading, possibly indicating deep study or narration of important historical content. Therefore, this phrase could be used when the male narrator is recounting a significant historical event or fact.

### 近邻3：samplenew3_00094352

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration, tension
- 与query gold精确词面重合：∅
- 字幕：How dare you intrude into the prince's mansion and attempt to assassinate him.
- 描述：In the text, the caption reads: "Dare to intrude into this imperial prince's residence and attempt murder." This sentence might be spoken by an Asian man. Based on the vocal cues described, such as the aggressive and accusatory tone of voice, with a high pitch and uneven rhythm, we can infer that the statement conveys a sense of anger, tension, and frustration. The speaker seems to be enraged and aggrieved because someone has trespassed in his residence attempting to assassinate him. This emotional state contrasts with the relaxed posture and closed-eyed expression described in the video clues, suggesting he may feel anger and tension when recalling or narrating the event.

### 近邻4：samplenew3_00086052

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, panic
- 与query gold精确词面重合：∅
- 字幕：The Wu State case eight years ago and today's conspiracy of benevolence and love are probably all orchestrated by the Crown Prince.
- 描述：In the text, caption content: "Eight years ago's Wu case and today's Co-conspirator Benevolence might all be engineered by the Crown Prince." Based on the caption mentioning the "Wu case eight years ago" and "today's Co-conspirator Benevolence," along with the man's's serious expression in the video clues and the formal setting implied by the environment, we can infer that the man may be discussing or contemplating some significant political or legal events. These events might be related to his position or duties within the imperial palace, hence he might feel under pressure or concern. Given the audio clues describing the person's's trembling voice, rapid and shallow breathing, and emotional analysis by an expert in the emotional field, we can speculate that the man might be experiencing intense negative emotions, such as fear, anxiety, and panic. This might be due to the important events or responsibilities he is facing.

### 近邻5：samplenew3_00073807

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, dissatisfaction, fear, tension
- 与query gold精确词面重合：∅
- 字幕：Do you really think that just with your family of three
- 描述：In the text, the caption reads: "Do you really think it's just you and your family of three." This sentence might be a man's's evaluation or reaction to someone or something. Given the audio clues describing the individual's's voice trembling and swaying, along with an extremely fast pace, it indicates they're experiencing intense negative emotions such as fear, anxiety, or tension, possibly feeling overwhelmed or under significant pressure. Coupled with video clues showing the man in deep thought with a slight look of concern and posture, we can infer that the sentence might carry an angry, dissatisfied, or challenging tone. Therefore, this sentence likely represents a man's's negative evaluation or doubt of someone or something, consistent with his overall emotional state.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 25. samplenew3_00056461｜decline｜ΔF1 -0.285714

gold：happiness, optimism, positive, satisfaction

query字幕：This is just a blank piece of paper.

源标注描述：In the text, the subtitle content "This is a blank sheet of paper" can be inferred from the calm and relaxed state of the old man in the video, as well as his smiling expression, that he is experiencing a positive emotional state, possibly feeling satisfied and happy. This aligns with the description of a "blank sheet of paper" in the subtitle, as a blank sheet of paper is often seen as a blank canvas representing infinite possibilities and creativity. Therefore, this sentence may be the old man's positive evaluation of the surrounding environment, expressing his optimistic attitude towards life.

off原始输出：The character's emotional state is positive, focused, engaged.

retrieval原始输出：The character's emotional state is neutral.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|engaged, focused, positive|0.285714|1|2|3|
|retrieval|neutral|0.000000|0|1|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.285714变为0.000000，差值-0.285714。
- TP变化-1，FP变化-1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：positive。
- 相对off新增未精确匹配gold的标签：neutral。
- 相对off移除未精确匹配gold的标签：engaged, focused。

gate：0.119991146；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00073580

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concentrated, firm belief, hope, solemn, stress, tension
- 与query gold精确词面重合：∅
- 字幕：One day we will meet.
- 描述：In the text, based on the video hints describing the man's serious and focused expression, as well as clues suggesting he is in a formal or professional setting, we can infer that he might be engaged in a task requiring intense concentration or dialogue. Coupled with audio cues depicting the speaker feeling anxious, tense, and under a lot of stress, we can speculate that this line likely a self-motivating or comforting statement made by the man to himself. He may be facing a challenging task or approaching a deadline, feeling overwhelmed and uncertain, yet he maintains a positive attitude and believes that there will come a day when he will achieve his goal. Therefore, this sentence expresses the man's's hope and firm belief, aligning with the overall solemn and concentrated emotional tone he exhibits.

### 近邻2：samplenew3_00108073

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, rational
- 与query gold精确词面重合：∅
- 字幕：Studying science is the right thing to do, let's go.
- 描述：In the text, the caption reads: "Study science, this is serious stuff. Let's go." This sentence could be a suggestion or proposal from a woman to a man. Given the emotional experiences of the individual described in the audio clues, including excitement, anticipation, tension, and anxiety, as well as the woman's displayed confusion or uncertainty in the video clues, we can infer that this phrase might be her attempt to change the subject or propose a new direction to alleviate her confusion and uncertainty. Therefore, the tone of the sentence might be calm and rational, aligning with the woman's overall emotional state.

### 近邻3：samplenew3_00103229

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：amusement, anxiety, estranged, positive
- 与query gold精确词面重合：positive
- 字幕：Today I will take a step forward.
- 描述：In the text, the caption reads: "I'm just having an old one today." This sentence could be a man describing his actions or feelings. Given the video clues of the man's smiling and in a relaxed posture, as well as the audio hints indicating that the speaker feels anxious and estranged, we can infer that this phrase might carry a self-deprecating or humorous tone. The man may be using a casual or humorous way to describe his actions, which aligns with his overall positive mood.

### 近邻4：samplenew3_00003632

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：I do not have the right to recruit workers.
- 描述：In the text, the subtitle content "I don't have the right to hire." This sentence may be one person's response or explanation to the other person. Based on the description of the old man's attire and the environment in the video clues, it can be inferred that these two individuals may be discussing work or recruitment-related topics. However, since the emotional state cannot be directly observed in the video clues, and the audio clues describe the individual experiencing intense negative emotions, we cannot determine the emotional inclination of this sentence.

### 近邻5：samplenew3_00068106

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, disappointment
- 与query gold精确词面重合：∅
- 字幕：When it comes to the occasion of needing your presence, how dare you continue to resist and make excuses? I will personally go.
- 描述：In the text, caption reads: "Even at the point of needing your assistance, still hesitating and procrastinating. What, do you think I should personally go and handle it?"  This sentence might be the speaker's's reprimand or criticism directed towards someone else. Given the urgency and tension conveyed in the speaker's's voice as described by the audio cues, along with a strong and aggressive tone, we can infer that this statement carries an angry and disappointed emotion. Moreover, the wording of the caption suggests that the speaker is dissatisfied with the other person's's actions, possibly due to their reluctance to take responsibility or cooperation. Hence, this statement reflects the speakerer's's negative feelings and dissatisfaction towards the other party.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 26. samplenew3_00109309｜decline｜ΔF1 -0.285714

gold：longing, sadness, yearning

query字幕：Today, my son snuggled up next to you and made a nest for himself, waiting for his death to come back and take care of you properly if you feel cold.

源标注描述：In the text, the subtitle reads: "Today, the son snuggled up to you and made a nest for himself, waiting for the son to die and come back to take care of you, in case you get cold." This sentence may be an expression or expectation from the elderly person to the people nearby. Based on the description of the melancholic melody played by the individual in the audio clues, as well as the sad or indifferent facial expression and body language of the elderly person in the video clues, it can be inferred that this sentence may carry a sense of longing, yearning, or sadness. The elderly person may be expressing longing and anticipation for their son to come back and take care of them. The phrase "waiting for the son to die and come back to take care of you" in this sentence may be an expectation or humorous expression from the elderly person, aligning with the overall display of sadness and contemplation.

off原始输出：The character's emotional state is longing, desire, care, warmth.

retrieval原始输出：The character's emotional state is nostalgia, warmth, concern.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|care, desire, longing, warmth|0.285714|1|3|2|
|retrieval|concern, nostalgia, warmth|0.000000|0|3|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.285714变为0.000000，差值-0.285714。
- TP变化-1，FP变化+0，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：longing。
- 相对off新增未精确匹配gold的标签：concern, nostalgia。
- 相对off移除未精确匹配gold的标签：care, desire。

gate：0.119938530；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [{"prediction_label": "desire", "unmatched_gold_label": "yearning"}], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00082431

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, negative, seriousness
- 与query gold精确词面重合：∅
- 字幕：You can't be fickle.
- 描述：In the text, the caption reads: "You can't be wishy-washy." This phrase might be a warning or reminder from a man to someone else. Given the audio cues with the speaker's's trembling voice and the video clues showing the man with a serious and thoughtful expression, we can infer that the tone of this sentence could be quite serious or concerned. Therefore, this statement might be the man expressing concern or giving advice to someone, aligning well with his overall negative emotional state.

### 近邻2：samplenew3_00087964

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, confusion, dissatisfaction
- 与query gold精确词面重合：∅
- 字幕：Did the text not teach you about people's hearts and minds?
- 描述：In the text, the caption reads: "Didn't you learn anything about people's inclinations?" This sentence might be a man's questioning or countering someone or something. Given the speaker's tone described as high-pitched, clear, and distinctive in the audio clues, and the man's's incredulous or shocked state portrayed in the video clues, we can infer that this statement might carry a strong emotional charge, possibly anger, dissatisfaction, or confusion. Therefore, this sentence could be the man's's questioning or rebuttal of someone or something, aligning with his overall displayed emotional state.

### 近邻3：samplenew3_00096678

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, calm, seriousness, urgency
- 与query gold精确词面重合：∅
- 字幕：Funding is a big problem now. Come back soon, I'll be waiting for you in Hanzhou.
- 描述：In the text, the caption reads: "F of money is a big issue now, come back immediately, I'm waiting for you in Hanzhou." Given the audio hints describing a person speaking with a sharp and agitated tone, with a sense of urgency in their voice as they speak quickly and energetically, and video clues showing a man with an anxious and serious expression, with body language suggesting that he is actively dealing with the situation while making a conscious effort to remain calm, we can infer that this sentence might be part of an urgent or significant situation conveyed over the phone by a man. The complexity of the man's's emotions likely stems from the tension and anxiety evident in this phone conversation.

### 近邻4：samplenew3_00014600

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, importance, urgency
- 与query gold精确词面重合：∅
- 字幕：If we don't go back, he wouldn't have died in vain.
- 描述：In the text, the subtitle content "If we don't go back, he won't die in vain" based on the video clue of the man's tense facial expression and the suggestion of bad weather in the environment, as well as the audio clue of the speaker's sense of urgency and intensity in their voice, we can infer that this sentence may be the man expressing a concern or sense of urgency. The man may be discussing an important decision or action and believes that if they don't go back, someone may suffer negative consequences. This sentence expresses the man's importance and urgency of this decision, as well as his concern for someone's safety.

### 近邻5：samplenew3_00105117

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, excitement
- 与query gold精确词面重合：∅
- 字幕：Prime Minister, let us stay in Fancheng and wait for orders to attack. It seems like we will be going to battle immediately, according to the General's intention.
- 描述：In the text, the caption reads: "The prime minister has instructed us to remain in Fancheng and await orders for an offensive, it seems as if the general is about to engage in battle at any moment." The speaker's, based on the audio clues of the male voice speaking quickly with urgency and a hint of provocation, along with the sound of footsteps in the background, can be inferred to be full of energy and enthusiasm. Their confidence in their beliefs is strong. Simultaneously, the facial expressions and body language of the man in the video hints at a complex mix of emotions, possibly related to the activities or performances he was involved in. Therefore, based on the description in the text, one can deduce that the man is filled with excitement and confidence as he prepares for battle.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 27. samplenew3_00051302｜decline｜ΔF1 -0.285714

gold：anxiety, frustration, helplessness, hesitation

query字幕：But what should I do if I don't want to see you either?

源标注描述：In the text, the caption reads: "But what if I don't want to see you either." This sentence could be something a woman might say on the phone. Given the audio clues described with her high-pitched voice, possible anxiety and frustration, and the video clues showing her expressing worry and self-reflection, we can infer that this statement might carry a tone of hesitation or helplessness. The woman might be discussing an issue that is troubling or uncomfortable for her, hence she expresses a contradictory emotional state.

off原始输出：The character's emotional state is anxiety, frustration, helplessness.

retrieval原始输出：The character's emotional state is anxiety, frustration, anger.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, frustration, helplessness|0.857143|3|0|1|
|retrieval|anger, anxiety, frustration|0.571429|2|1|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.857143变为0.571429，差值-0.285714。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：helplessness。
- 相对off新增未精确匹配gold的标签：anger。

gate：0.119952604；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00080946

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：comfort, concern
- 与query gold精确词面重合：∅
- 字幕：Let's talk about you, ignoring them.
- 描述：In the text, the caption reads: "Forget about them, let's talk about you." This sentence could be a suggestion or proposal from a woman to someone nearby in a video. Given the individual's tone of voice described as agitated and urgent, along with the sense of frustration conveyed through their words, combined with the woman's serious expression and body language in the video clues, we can infer that this statement might carry a tone of concern or comfort. The woman may want to divert the individual's attention away from negative feelings for a moment, shifting the conversation to another topic. Therefore, this sentence might be the woman's attempt to alleviate the individual's negative emotions, offering them support and care.

### 近邻2：samplenew3_00022390

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：boredom, joy, melancholy, sadness
- 与query gold精确词面重合：∅
- 字幕：During the New Year's Eve, I was still thinking about how boring this year has been. Now, I'm wondering where all the boredom has gone.
- 描述：In the text, the caption reads: "On New Year's's Eve, I was still thinking that this year has been dull enough, now it's wonderful, I just wish to be dull anywhere." This sentence might be a self-reflection or deep contemplation from a woman. By inferringencing from the woman's facial expressions and body language in the video clues, as well as the melancholic song performed by the singer in the audio clues, we can deduce that this sentence expresses her feelings about the past year. She felt that the time had been boring, but now she might have found joy or changed her perspective on life. The sentence may carry a tone of self-mockery or humor, which fits with the woman's overall portrayal of a mix of boredom and sadness.

### 近邻3：samplenew3_00069926

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, tension
- 与query gold精确词面重合：anxiety
- 字幕：I am Auntie, come to me immediately.
- 描述：In the text, the caption reads: "I'm your aunt, come over here right away." This sentence might be spoken by a woman to someone on the phone. Given the audio clues that describe the woman speaking quickly with a tense and impatient tone, as well as the video clues showing the woman's body language expressing concern or urgency, we can infer that this sentence might be a woman conveying an urgent or pressing request or demand over the phone. She likely needs the other person to come immediately to help or address some issue, hence her emotional state is quite tense and anxious.

### 近邻4：samplenew3_00063989

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, detachment, introspection, self-reflection
- 与query gold精确词面重合：∅
- 字幕：All businesses related to him.
- 描述：In the text, interpreting the neutral expression and composed posture of the woman in the video clues, along with the high-pitched and clear tone of her voice in the audio clues, suggests that she she might be in a state of calmness, detachment, introspection, or self-reflection. Consequently, the term "all businesses associated with him" mentioned in the subtitles could possibly refer to how the woman is contemplating or assessing businesses related to a certain individual or event. This kind of expression might carry a sense of calm and objectivity, which alignss well with the woman's overall demeanor of neutrality and composure.

### 近邻5：samplenew3_00080386

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：excitement, tension
- 与query gold精确词面重合：∅
- 字幕：Hello, this is how it is. I just received a call from your hotel and I want to know which room it was from.
- 描述：In the text, the caption reads: "Hello, it's like this, I just received a call from your hotel. I'm wondering which room it was from." Given the personal voice described in the audio clues with slight tremble and faster pace, and the neutral expression of the woman and her relaxed body language in the video clues, we can infer that this sentence might carry an emotional tone of tension and excitement. The woman might be asking for information about a hotel room over the phone, which could be a significant question, leading to her feeling tense and excited. Therefore, this sentence could possibly reflect the woman's inquiry and excitement.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 28. samplenew3_00014689｜decline｜ΔF1 -0.285714

gold：anticipation, excitement, invitation, urgency

query字幕：Come and help me gather together Zhang Lu.

源标注描述：In the text, caption content: "Come and join me with Zhang Lu." This sentence might be said by a man holding chocolate. Given the man's joyful and excited emotional expression shown in the video clues, as well as the described emotional state of anxiety or tension in the audio clues, we can infer that this sentence might reflect a sense of excitement mixed with a feeling of urgency or pressure, as he hopes for someone to come and assist him in enjoying the chocolate together. Therefore, this sentence may carry an element of anticipation and invitation.

off原始输出：The character's emotional state is excited, enthusiastic, urgent.

retrieval原始输出：The character's emotional state is excited, enthusiastic, joyful.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|enthusiasm, excitement, urgency|0.571429|2|1|2|
|retrieval|enthusiasm, excitement, joy|0.285714|1|2|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.571429变为0.285714，差值-0.285714。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：urgency。
- 相对off新增未精确匹配gold的标签：joy。

gate：0.119967125；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00107582

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：determination, positive
- 与query gold精确词面重合：∅
- 字幕：Then I will lend you three thousand elite soldiers.
- 描述：In the text, the caption reads: "So, I'll lend you three thousand elite troops." This sentence might be a response or decision made by the speaker to someone or a situation. Given the urgency and determination conveyed in the speaker's's voice as described in the audio cues, along with their firm and confident tone, it can be inferred that this statement reflects a positive attitude and resolve from the speaker, willing to offer aid or support. The phrase "lend you three thousand elite troops" could be a metaphorical or figurative expression, indicating the speaker's's willingness to provide substantial support or resources. Therefore, this sentence embodies the speaker's's positive mood and determination, aligning with the observations made from the audio cues.

### 近邻2：samplenew3_00063257

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：controlled, intense, irony, mockery, negative
- 与query gold精确词面重合：∅
- 字幕：I can't believe the leader of the largest gang in the world is so delicate and weak.
- 描述：In the text, caption content: "Who would have thought that the leader of the largest gang in the world would be so refined and weak-willed." This sentence might be an evaluation or reaction to the bald elderly man. Given the audio cues describing the individual's voice as hoarse and tense, indicating they might be experiencing intense negative emotions, and with a slow pace of speech that is purposeful, suggesting they are trying to control their emotions, we can infer that this sentence may carry a tone of mockery or sarcasm. Therefore, this sentence could be a mocking or ironic comment on the bald elderly man's appearance or image, which would be consistent with the described individual's experiencing negative emotions.

### 近邻3：samplenew3_00003859

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, tension
- 与query gold精确词面重合：∅
- 字幕：I just arrived after a long journey.
- 描述：In the text, caption content: "One has traveled a great distance just now." This sentence could be a description or evaluation by a man of someone or an event. Given the man's's serious and focused emotional cues in the video hints, as well as the personal characteristics indicated by the audio clues such as rapid speech, trembling voice, and high pitch tone, we can infer that this sentence might carry a sense of tension or anxiety. The man may be describing his own or others' journey or arrival at a place, and feeling tense or anxious for some reason.

### 近邻4：samplenew3_00030666

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：impatience, weariness
- 与query gold精确词面重合：∅
- 字幕：If you keep talking endlessly
- 描述：In the text, caption content: "If any of you keep talking endlessly." This sentence could be a response or warning from a man to those around him. Based on the audio cues described with an individual's voice tense and tight, the tone conveying a sense of urgency and impatience, and the video clues showing the man with a serious and firm expression, his brows furrowed, we can infer that this sentence might be delivered in an impatient or weary manner. Therefore, this sentence could be a reaction from the man to excessive talk from those around him, expressing his impatience or weariness. This alignss with the overall solemn and focused emotional state he displays.

### 近邻5：samplenew3_00079164

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, appreciation, gratitude
- 与query gold精确词面重合：anticipation
- 字幕：If I have the honor of keeping your name until today, I will be with you, my king.
- 描述：In the text, the caption reads: "If fortunate enough to keep my name until today, I would surely engage with you all." This sentence might be a statement that a man in the video addresses to his audience or students. Given the audio cues describing the individual's urgent and decisive tone, as well as the man's serious expression and self-assured presence in the video clues, we can infer that this phrase might carry an element of anticipation and appreciation. The man may be expressing gratitude towards his audience or students, and indicating that if he could retain his name, there would be more opportunities for interaction and collaboration. This statement reflects the man's's emphasis on the importance of his audience or students and his desire to establish stronger connections with them.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 29. samplenew3_00025316｜decline｜ΔF1 -0.266667

gold：anticipation, pleading, respect

query字幕：Your Highness, since you already know this king's intentions, I hope you won't hesitate to give guidance.

源标注描述：In the text, the subtitle reads: "Your Grace, knowing Your Majesty's intentions, I hope for Your Grace's generous guidance." This sentence might be a request or an expectation from a man to a certain prince. Given the speaker's's tone in the audio clue, which is calm and orderly with a trace of sadness, and the man's's facial expression being calm and composed in the video clue, we can infer that the sentence may carry a tone of pleading or anticipation. Therefore, this sentence might be a man's request for the prince to provide him with guidance or advice, expressing his respect and anticipation for Your Grace.

off原始输出：The character's emotional state is anticipation, respect, solemnity.

retrieval原始输出：The character's emotional state is anticipation, longing.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anticipation, respect, solemnity|0.666667|2|1|1|
|retrieval|anticipation, longing|0.400000|1|1|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.400000，差值-0.266667。
- TP变化-1，FP变化+0，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：respect。
- 相对off新增未精确匹配gold的标签：longing。
- 相对off移除未精确匹配gold的标签：solemnity。

gate：0.120059952；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00094135

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：assertive, confidence
- 与query gold精确词面重合：∅
- 字幕：
- 描述：In the text, the caption reads: "This is it, Your Highnesses, I invite both of you tonight." This sentence could be a proposal or invitation made by a man to others. Given the confidence and authoritative tone of the male voice as described in the audio cues, along with a slight challenging inflection, we can infer that the statement might be delivered with a confident and assertive manner. Thus, this sentence appears to express the man's's decision and invite others to join, aligning with his overall display of confidence and self-assuredness.

### 近邻2：samplenew3_00113494

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, confusion, decision, firm, resolute, resolve
- 与query gold精确词面重合：∅
- 字幕：No need to ask more, Xingye returned to Xiaoting.
- 描述：In the text, the caption reads: "No need for further inquiries, Xing Ye is returning to Xiao Ting." This sentence could be a man's's response to someone or some event. Given the urgency, tension, and determination conveyed by the audio cues, along with the man's's confusion, anger, and heightened emotions as depicted in the video clues, we can infer that this phrase might be spoken with a firm and resolute tone. Therefore, this sentence might be the man expressing his resolve and decision, aligning with his overall emotional state.

### 近邻3：samplenew3_00026871

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：advice, assurance, comfort
- 与query gold精确词面重合：∅
- 字幕：You can rest assured to collect silk and weave fabric.
- 描述：In the text, caption reads: "Just rest assured when you receive the silk cloth." This sentence might be a suggestion or comfort offered by the speaker to others. Given the audio cues that suggest the speaker has a calm, confident, and firm tone, along with the video hints showing people smiling and in a relaxed mood, we can infer that this statement could be an encouragement or a way of assuringance. Therefore, the sentence might be the speaker's providing comfort or advice to others, aligning with the positive emotions portrayed in the video.

### 近邻4：samplenew3_00101518

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction
- 与query gold精确词面重合：∅
- 字幕：Don't you really understand why I'm angry?
- 描述：In the text, caption content: "Don't you understand why I am angry?" This sentence could be the interrogation or expression of dissatisfaction from the bald man to someone. Based on the audio cues with the description of the angry and frustrated vocal characteristics, along with the video clues featuring the man's's solemn expression and the dignified atmosphere of the room, we can infer that the tone carries an element of anger and discontent. Therefore, this sentence might be the man expressing his dissatisfaction and anger, fitting well with the overall display of his angry emotion.

### 近邻5：samplenew3_00076805

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：distress, nervousness, pressure, worry
- 与query gold精确词面重合：∅
- 字幕：Should consider the overall situation
- 描述：In the text, the subtitle says, "Should have considered the bigger picture." This sentence may be spoken by the man while he is contemplating or expressing his viewpoint. Based on the facial expression and body language of the man in the video clues, as well as the trembling in the individual's voice and the slow and cautious speech in the audio clues, we can infer that this sentence may carry a sense of worry or distress. The man may be contemplating an important decision or issue and feeling pressure and nervousness. Therefore, this sentence may be the man expressing his concerns and attention to the overall situation.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 30. samplenew3_00108391｜decline｜ΔF1 -0.266667

gold：appreciation, humility, politeness

query字幕：Thank you for your kind words, respected person.

源标注描述：In the text, the caption reads: "Thanks for the praise from the esteemed leader." This phrase could be a response or an expression of gratitude by a character in the video to someone else. Given the serious facial expressions and focused posture of the character based on the video hints, and considering the audio cues that suggest the speaker might be experiencing intense emotional turmoil, we can infer that this sentence might be conveyed with a tone of humility or appreciation. Therefore, this could be a courteous or polite reply, fitting well with the overall serious and pressured emotional portrayal of the character.

off原始输出：The character's emotional state is gratitude, humility, appreciation.

retrieval原始输出：The character's emotional state is gratitude, humility.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|appreciation, gratitude, humility|0.666667|2|1|1|
|retrieval|gratitude, humility|0.400000|1|1|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.400000，差值-0.266667。
- TP变化-1，FP变化+0，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：appreciation。

gate：0.120017670；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "gratitude", "unmatched_gold_label": "appreciation"}]}

实际5近邻证据：

### 近邻1：samplenew3_00113741

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：adventurous, confidence, positive, slightly irritated
- 与query gold精确词面重合：∅
- 字幕：How can you know the result without doing many things? Let me try and see what happens.
- 描述：In the text, the caption reads: "How can you know the outcome without trying many things? What harm is there in me trying?" This sentence might be spoken by a man in a video. Based on the audio cues, the speaker's has a calm and measured tone, with an undercurrent of slight irritation. Additionally, considering the video clues where the man exhibits a smile and a confident posture while looking directly into the camera, we can infer that this sentence might carry a tone of challenge or adventure. The man may be expressing a positive attitude, encouraging himself or others to try new things without fear of failure. This alignss well with the overall impression of the man's being at ease and positive.

### 近邻2：samplenew3_00079107

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, excitement
- 与query gold精确词面重合：∅
- 字幕：The king is jumping with anger just for this matter. Didn't Your Highness notice that this is a privilege only for the prince?
- 描述：In the text, the subtitle content: "The prince is furious about this. Didn't Your Highness notice that this is a privilege only the prince has?" This sentence may be the speaker's comment or reaction to a person or event. Based on the audio cues describing the speaker's assertive and confident tone, high pitch, and fast rhythm, as well as the calm and focused emotional state exhibited by the man in the video, we can infer that this sentence may carry an excited or angry tone. Therefore, this sentence may be an expression of criticism or complaint, consistent with the overall emotional state displayed by the speaker.

### 近邻3：samplenew3_00061395

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, doubt, tension, worry
- 与query gold精确词面重合：∅
- 字幕：When the beloved concubine was at the height of her power, she couldn't do anything to the queen, but now she can succeed.
- 描述：In the text, caption content: "Even during her peak, Empress Jingwei couldn't do anything to the Empress. It's impossible for her to succeed now." This sentence might be a man's evaluation or reaction to someone or a situation. Given the audio clues with a person's sounding tense and urgent, as well as high-pitched music used, we can infer that the tone of this sentence might carry a sense of tension, anxiety, or concern. Additionally, based on the video clues where the man is shown in deep thought with a smile, we can deduce that he might be contemplating an issue or situation and feels concerned about it. Therefore, this sentence could be the man's's worry and doubt towards someone or some situation, which alignss with his overall tense demeanor.

### 近邻4：samplenew3_00078038

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：assured, attention, confidence, focused
- 与query gold精确词面重合：∅
- 字幕：I believe the Jade Scripture is like this.
- 描述：In the text, caption content: "I believe Jade Scripture is like this." This sentence might be a man expressing his belief or viewpoint in a conversation. Based on the video hints of the man being fully engrossed in the dialogue, with a serious expression and body language, as well as the audio clues describing a high-pitched, clear and crisp voice, we can infer that this sentence might be the man expressing his confidence and self-assurance on a particular topic. This alignss with the man's overall appearance of focused attention and confidence.

### 近邻5：samplenew3_00000258

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：enthusiasm, passion, tension
- 与query gold精确词面重合：∅
- 字幕：Lord Hou's words, Su naturally remembers.
- 描述：In the text, caption content: "Baron Su naturally remembers what Lord Hou said back then." Based on the urgency and intensity in the individual's's voice as described in the audio clues, along with the tremble in their tone, we can infer that this sentence might be spoken with a tense or passionate tone. Concurrently, considering the man is depicted wearinging a heavy coat in the video clues, he might be experiencing comfort or warmth, which suggests that this sentence could be his response or recollection of Lord Hou's words. Given the emotional agitation described in the audio clues, this sentence might be spoken with enthusiasm or passion, aligning with the man's overall emotional state.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 31. samplenew3_00099442｜decline｜ΔF1 -0.266667

gold：excitement, positive, satisfaction

query字幕：Definitely can eat dumplings three times.

源标注描述：In the text, the caption reads: "Absolutely can eat three dumplings twice." This phrase might be a woman commenting on or responding to some food or dietary habits. Given the confident and authoritative tone of the female voice as described in the audio clues, and the visual hints of a woman standing in a kitchen, possibly making a face, we can infer that the statement might carry a positive sentiment, such as excitement or satisfaction. The woman might be expressing her love for a particular food or exaggerating her eating capacity. Thus, this statement alignss with the overall positive emotion she is portraying.

off原始输出：The character's emotional state is positive, excited, enthusiastic.

retrieval原始输出：The character's emotional state is excited, happy.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|enthusiasm, excitement, positive|0.666667|2|1|1|
|retrieval|excitement, happiness|0.400000|1|1|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.400000，差值-0.266667。
- TP变化-1，FP变化+0，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：positive。
- 相对off新增未精确匹配gold的标签：happiness。
- 相对off移除未精确匹配gold的标签：enthusiasm。

gate：0.120018631；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00078238

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confusion, defensiveness, resentment
- 与query gold精确词面重合：∅
- 字幕：Why are you angry? This can only explain this magazine.
- 描述：In the text, the caption reads: "Why are you upset with me?" This phrase could be a woman's response or explanation to someone. Given the audio cues that describe the speaker's as having an aggressive and hostile tone, and the woman displaying a serious expression and body language in the video clues, we can infer that this statement might carry a tone of resignation or confusion. The woman might be responding to the other person's's anger or frustration, expressing her innocence or lack of understanding. Therefore, this sentence could be the woman's attempt to calm down the other person, or to explain her position.

### 近邻2：samplenew3_00054122

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, frustration, tension
- 与query gold精确词面重合：∅
- 字幕：If you see me taking it back, the child will definitely be sad.
- 描述：In the text, caption content: "You see, if I were to bring this back, the child would definitely be upset." This sentence might be what a woman is saying to another woman. Given the video clues, the woman's mixed expressions of anger and frustration, along with her body language supporting her emotional state, suggests she may be engaged in a heated argument or disagreement with another woman. From the audio cues, where the speaker has a higher pitched tone with slight tremble, and speaks with a firm and confident manner, it can be inferred that the speaker feels anxious and tense, attempting to persuade the listener of something. Therefore, this sentence could be the woman expressing her viewpoint, worried about how her child would feel if they was to share this viewpoint with them and cause them distress.

### 近邻3：samplenew3_00071652

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：enthusiasm, optimism, positive
- 与query gold精确词面重合：positive
- 字幕：Each person only needs 80 yuan per month.
- 描述：In the text, the caption reads: "It's only eighty yuan per person per month." This sentence might be a woman expressing an idea or opinion in a conversation. Given the video hints of her displaying joy and an optimistic demeanor, as well as audio cues like her quick pace and high pitch in speech, we can infer that this statement might be made with a positive, optimistic, or enthusiastic tone. Therefore, this sentence could be the woman articulating a positive attitude or an optimistic perspective on a certain topic or viewpoint.

### 近邻4：samplenew3_00103787

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, disappointment, frustration
- 与query gold精确词面重合：∅
- 字幕：Otherwise, it would be like being a cauliflower.
- 描述：In the text, the caption reads: "Otherwise, they'd just be as unappealinging as broccoli." This sentence could be something a woman might say in conversation. Given the high pitch and excited tone described in the audio clues, along with the woman's mixed emotions shown in the video hints, we can infer that the statement might carry an undertone of anger or frustration. In Chinese culture, broccoli is often used to describe someone who doesn't look good or has an unattractive appearance. Therefore, this sentence might reflect her expression of dissatisfaction or disappointment, aligning well with her overall negative emotional state.

### 近邻5：samplenew3_00056145

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, concern, frustration, unhappiness
- 与query gold精确词面重合：∅
- 字幕：You must explain to me why you skipped school that day.
- 描述：In the text, caption content: "So you have to explain to me clearly why you skipped school that day." This sentence might be a demand or question from a woman to someone else. Given the sharp shrieking sound and the use of the word "must" in the audio cues described, as well as the woman's frowning and negative demeanor shown in the video clues, we can infer that the sentence carries a strong negative emotion, possibly anger or frustration, and the woman is unhappy or concerned about the person skipping school. Therefore, this sentence expresses the woman's emotional state of questioning and demanding an explanation for the other person's behavior.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 32. samplenew3_00103397｜decline｜ΔF1 -0.250000

gold：agreement, enthusiasm, excitement, positivity, support

query字幕：At the same time, we can also bring the New Youth to Beijing for development.

源标注描述：In the text, caption reads: "At the same time, it's also about bringing the new generation to Beijing for development." This sentence might be what this woman said in the video. Based on the description of the individual's voice in the audio cues, which carries a sense of urgency and determination, as well as the video clues showing the woman's curiosity and openness, we can infer that this phrase could be her way of expressing agreement and support for a certain topic or suggestion. The woman may have a positive attitude towards bringing the new generation to Beijing for development and expresses excitement and enthusiasm about it. This alignss with her overall positive mood and comfort with her surroundings.

off原始输出：The character's emotional state is positive, excited, enthusiastic.

retrieval原始输出：The character's emotional state is positive, confident, excited.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|enthusiasm, excitement, positive|0.500000|2|1|3|
|retrieval|confidence, excitement, positive|0.250000|1|2|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.500000变为0.250000，差值-0.250000。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：enthusiasm。
- 相对off新增未精确匹配gold的标签：confidence。

gate：0.120033838；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [{"prediction_label": "positive", "unmatched_gold_label": "positivity"}], "retrieval": [{"prediction_label": "positive", "unmatched_gold_label": "positivity"}]}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00014144

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, nervousness
- 与query gold精确词面重合：∅
- 字幕：If the situation on Luo Sibing's side is not good, then we have to ask a lawyer to act as Pian Kun's agent.
- 描述：In the text, the subtitle reads, "If Luo Shisoldier's situation is not good, then we will have to ask a lawyer to be Kun's representative." This sentence is likely spoken by the man on the phone. Based on the description of slight tremors in the speaker's voice and the monotonous tone of voice in the audio clues, as well as the strong facial expression and body language exhibited by the man in the video clues, it can be inferred that this sentence may carry a tone of nervousness or anxiety. The man may be discussing some important issues or decisions on the phone, which could be causing his emotions to become tense and his stress to increase. Therefore, this sentence may be the man expressing his concerns about the current situation and the need for a lawyer to act as Kun's representative.

### 近邻2：samplenew3_00040411

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, contentment, tranquility
- 与query gold精确词面重合：∅
- 字幕：Our country is already undergoing a major transformation.
- 描述：In the text, the caption reads: "Our country is undergoing a great transformation." Based on the video hints describing a character seated in a tranquil garden, dressed in a serene brown robe, and with his facial expression showing a state of calmness and relaxed body language, it can be inferred that this person is experiencing a state of tranquility and contentment. Therefore, this statement might be their observation or evaluation of the current situation in their nation. Given the audio hints describing the speaker's's tone as informative and educational without any emotional overtones, and with high-quality audio, it suggests that this statement is likely a description or analysis of the current situation in the nation provided by the speaker in an objective and cool-headed manner.

### 近邻3：samplenew3_00111128

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, professional
- 与query gold精确词面重合：∅
- 字幕：What do you want to talk about? Just listen and you will know, right?
- 描述：In the text, the subtitle reads, "You'll know what to talk about when you listen to me." This sentence may be a response or suggestion from the man to the audience. Based on the description of the man's calm and composed state in the video clues, as well as his confident and in-control body language, we can infer that this sentence may carry a calm and professional tone. The man may be offering advice to the audience on how to solve a problem or obtain information. Therefore, this sentence may be a guiding or suggesting statement that aligns with the overall calm and professional image portrayed by the man.

### 近邻4：samplenew3_00058993

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：authoritative, confidence, contemplation, seriousness
- 与query gold精确词面重合：∅
- 字幕：That should become our main stronghold.
- 描述：In the text, caption content: "That will be our primary battleground." This sentence might be a conclusion or suggestion made by a man after some thought. Given the video clues such as the man's's serious expression and his action of deep in thought with his head down, as well as the audio cues like the speaker's's confident and authoritative tone, we can infer that this sentence might be a decision or proposal made by the man after some contemplation. The man's's focused and thoughtful state, along with the presence of bookshelves, suggests that he is in a professional or academic environment, which may influence his emotional state.

### 近邻5：samplenew3_00035314

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, emotional detachment, frustration
- 与query gold精确词面重合：∅
- 字幕：Are you deliberately mocking your father?
- 描述：In the text, the subtitle reads: "Is this deliberate, pushing your own father around?" This sentence might be a man's's questioning or accusation directed at someone else. Based on the audio cues described with an individual's voice filled with anger and frustration, a sharp and aggressive tone, and a very fast pace, indicating of feeling overwhelmed and frustrated, possibly experiencing anxiety or high stress. Furthermore, the individual's tone is rather flat, indicating of feeling emotionally detached. Therefore, this sentence could be a man's's aggressive question or accusation in a state of anger and frustration, fitting well with the overall mood of anger, frustration, anxiety, and emotional detachment that the man exhibits.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 33. samplenew3_00088108｜decline｜ΔF1 -0.250000

gold：anger, complaint, doubt, frustration

query字幕：Is it mine or is it Zhenpiao's or Guibin's?

源标注描述：In the text, the caption reads: "It's either my voucher or VIP." This sentence might be what a man said over the phone. Given the speaker's's aggressive and confrontational tone as described in the audio cues, along with an angry or frustrated emotional state, we can infer that this phrase might carry a sense of challenge or dissatisfaction. Therefore, this sentence could be the man's's way of expressing doubt or complaint to the other party over the phone, which is consistent with the serious and focused mood he exhibits overall.

off原始输出：The character's emotional state is anxious, tense, irritable, frustrated.

retrieval原始输出：The character's emotional state is anxious, tense, irritable.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, frustration, irritability, tension|0.250000|1|3|3|
|retrieval|anxiety, irritability, tension|0.000000|0|3|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.250000变为0.000000，差值-0.250000。
- TP变化-1，FP变化+0，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：frustration。

gate：0.120050676；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00025032

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, discontent
- 与query gold精确词面重合：∅
- 字幕：I still have to take a taxi back and forth. I can't give you the ticket. No, no, I didn't mean that at all.
- 描述：In the text, the caption reads: "I still have to arrange for round trip taxi tickets, I'll reimburse you. No, no, no, that's not what I mean. Not a word." This sentence might be spoken by a male on the phone. Based on the audio cues described in the voice of the male sounding angry and anxious, with a sense of urgency, and the video clues showing the male's appearing frustrated and thoughtful, we can infer that this sentence might be a male expressing his distress and dissatisfaction over the phone. He may be discussing an issue or having a difficult conversation with the other party, which could increase his stress and frustration. Therefore, this sentence expresses the male's discontent and anxiety.

### 近邻2：samplenew3_00005883

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：important, urgency
- 与query gold精确词面重合：∅
- 字幕：You just go ahead and prepare for today, I will talk to him later to confirm the time.
- 描述：In the text, the caption reads: "You just follow through with what we've planned for today and I'll get back to you to finalize the timing later." This sentence might be an instruction or advice from one person to another. Given the urgency and importance conveyed by the speaker's's tone as per the audio cues, and the individual's focused and serious demeanor indicated in the video clues, we can infer that this statement might carry a sense of urgency and importance. Therefore, the sentence likely emphasizes that the other person should prepare according to today's arrangements and later confirm the time with him. This suggests that the speaker attaches great importance to the topic of discussion and expects the other party to make timely preparations.

### 近邻3：samplenew3_00090625

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, determination, emotionally detached, frustration, tension
- 与query gold精确词面重合：anger, frustration
- 字幕：The lawyer ate chicken, but didn't eat the speaker's food.
- 描述：In the text, caption content: "Lawyer Ge eats chicken quai, he didn't eat the speaker's's meal." This sentence might be an evaluation or reaction from one person to another. Considering the emotional state of the speaker described in the audio clues, feeling anxious, tense, and emotionally detached, and the emotional state portrayed by the person making facial expressions, showing anger, frustration, or determination, we can infer that the sentence might have a negative, provocative tone. Therefore, this sentence could be an expression of criticism or irony, which alignss with the observed emotional states in the video.

### 近邻4：samplenew3_00092579

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, pleasant, relaxation
- 与query gold精确词面重合：∅
- 字幕：This hot spring is right under this ground.
- 描述：In the text, the caption reads: "This hot spring is underground here." Based on the audio cues describing the sound of water and the feeling of relaxation and calmness, as well as the visual clues of the expressions and actions of the two people in the video, we can infer that this sentence might have been said by the man in the white robe with the hair bun to the man in the black robe. Given the relaxing and peaceful feeling described in the audio cues, and the active and expressive emotion shown by the man in the white robe, we can infer that this sentence might be describing a pleasant and relaxing place, which alignss with the overall positive emotion the man in the white robe displays.

### 近邻5：samplenew3_00075072

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, positive, pride
- 与query gold精确词面重合：∅
- 字幕：Strengthening the authoritative position of Yue Sheng Company in the HiHi field.
- 描述：In the text, the caption reads: "Strengthening Moonpro's's authority in the HiHi domain." Given the character's serious expression and posture described within the video clues, and the speaker's high energy and enthusiasm as described in the audio cues, we can infer that this phrase might be the speaker emphasizing Moonpropro's's expertise and authority in the HiHi domain. The speaker's passion and exuberant tone suggest their deep interest in the subject and their desire to highlight the company's significance in the field. Consequently, this statement may be expressed in a positive emotional state, conveying pride and confidence in the company.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 34. samplenew3_00046428｜decline｜ΔF1 -0.228571

gold：open, positive

query字幕：But I am willing to learn to be closer to you.

源标注描述：In the text, the caption reads: "But I am willing to learn and align with you." This sentence might be the man's's response to someone or an idea. Given that the audio clues describe him speaking in a clear and confident tone, and the video clues show him intently looking at something, possibly pondering or reflectingively, we can infer that this statement expresses his willingness to learn and accept the other person's's viewpoint. Therefore, the phrase may carry an open and positive emotional state, which is consistent with his focused and reflective behavior.

off原始输出：The character's emotional state is positive, open, willing.

retrieval原始输出：The character's emotional state is positive, open, willing, anxious, tense.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|open, positive, willing|0.800000|2|1|0|
|retrieval|anxiety, open, positive, tension, willing|0.571429|2|3|0|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.800000变为0.571429，差值-0.228571。
- TP变化+0，FP变化+2，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：anxiety, tension。

gate：0.119952217；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00041750

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：content, hope, positive
- 与query gold精确词面重合：positive
- 字幕：Nowadays society is very normal.
- 描述：In the text, the caption reads: "Everything is normal in society now." This sentence might be spoken by a man in a video. Based on the audio cues describing the individual's voice trembling and shaking, along with an extremely fast pace, it indicates that he might be experiencing strong emotions such as fear, anxiety, or nervousness. However, according to the visual clues in the video of the man's's expression and body language, he appears relaxed, comfortable, and even smiling. Therefore, this statement might be the man responding to his current situation, expressing his view on the normality and stability of the current societal state, which alignss with his overall positive mood.

### 近邻2：samplenew3_00113203

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：excitement, satisfaction, upbeat
- 与query gold精确词面重合：∅
- 字幕：The number of times we two have dated is also quite frequent.
- 描述：In the text, caption content: "We've been going out quite often." This sentence might be a man discussing the frequency of his dates with someone else. Given the audio cues, such as the individual speaking with a high pitch and fast pace, as well as the video clues showing the man's exuding confidence and a comfortable emotional state, we can infer that this statement might carry an upbeat, excited, or satisfied tone. Therefore, this sentence could be the man expressing his satisfaction and excitement about the dating frequency, which alignss with his overall positive mood.

### 近邻3：samplenew3_00086790

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, appreciation, surprise
- 与query gold精确词面重合：∅
- 字幕：The general class teacher, Mr. Ma, also believes in his students.
- 描述：In the text, caption content: "Principal Ma, the teacher, has come to believe in his student." This sentence could be an evaluation or reaction of an individual towards a particular student or event. Considering the excited and tense emotions described in the audio clues and the person's's appearance of deep thought and reflection in the video clues, we can infer that this sentence might carry a tone of surprise or admiration. Therefore, this sentence could be a positive and appreciative statement about a student's performance or the outcome of an event, which alignss with the overall excitement and tension emotions expressed.

### 近邻4：samplenew3_00031698

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, appreciation, encouragement, favorable, positive mood, praise, recognition, relaxed posture, tension
- 与query gold精确词面重合：∅
- 字幕：You must be able to become a professional chess player.
- 描述：In the text, the caption reads: "You can definitely become a professional player." This statement might be an evaluation or encouragement from a smiling man to a frowning one. Given the audio cues describing an individual feeling anxious or tense, and the lively pace of speech, we can infer that this statement is likely an expression of encouragement or praise aimed at boosting the confidence of the frowning person. Additionally, based on the video cues showing the positive mood and relaxed posture of the smiling man, we can speculate that his assessment is favorable, possibly a recognition and appreciation of the other person's's chess skills.

### 近邻5：samplenew3_00082937

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：encouragement, hope, optimism, positive attitude
- 与query gold精确词面重合：∅
- 字幕：I think we should turn this fight into a good thing that motivates them to improve.
- 描述：In the text, the subtitle content "I think turning this fight into something that motivates them to improve is a good idea" suggests that based on the description of the man's serious and contemplative expression in the video clues, as well as the angry and frustrated emotions described in the audio clues, we can infer that this sentence may be the man's thoughts and expression of his viewpoint. The man may believe that even though something bad like a fight has occurred, it can be turned into something that motivates them to improve. This viewpoint may indicate that the man has a positive attitude and optimistic emotions, despite facing some challenges or difficulties. Therefore, this sentence may be the man expressing a sense of hope and encouragement, aligning with the overall mixture of seriousness and contemplation he displays.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 35. samplenew3_00115051｜decline｜ΔF1 -0.222222

gold：calm, pressure, relaxation, stress, urgency

query字幕：The matter of relocating the entire village

源标注描述：In the text, the caption reads: "Our whole village relocation matter." Based on the video hints such as the man's relaxed posture and neutral facial expression, along with the calm and serene environment, it can be inferred that the man is likely in a state of calmness and relaxation, without any obvious emotional distress or excitement. From the audio clues, the speaker's's urgent and important tone, coupled with a slight sense of tension in their voice, suggests that the speakerer may feel stressed or under pressure about the whole village relocation. Considering both the video and audio clues, it can be deduced that while the man feels urgency and importance in handling the whole village relocation task, he still maintains a relatively calm and relaxed emotional state.

off原始输出：The character's emotional state is serious, focused, urgent, tense.

retrieval原始输出：The character's emotional state is serious, important, nervous.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|focused, seriousness, tension, urgency|0.222222|1|3|4|
|retrieval|important, nervousness, seriousness|0.000000|0|3|5|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.222222变为0.000000，差值-0.222222。
- TP变化-1，FP变化+0，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：urgency。
- 相对off新增未精确匹配gold的标签：important, nervousness。
- 相对off移除未精确匹配gold的标签：focused, tension。

gate：0.119982854；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00090625

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, determination, emotionally detached, frustration, tension
- 与query gold精确词面重合：∅
- 字幕：The lawyer ate chicken, but didn't eat the speaker's food.
- 描述：In the text, caption content: "Lawyer Ge eats chicken quai, he didn't eat the speaker's's meal." This sentence might be an evaluation or reaction from one person to another. Considering the emotional state of the speaker described in the audio clues, feeling anxious, tense, and emotionally detached, and the emotional state portrayed by the person making facial expressions, showing anger, frustration, or determination, we can infer that the sentence might have a negative, provocative tone. Therefore, this sentence could be an expression of criticism or irony, which alignss with the observed emotional states in the video.

### 近邻2：samplenew3_00027288

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction
- 与query gold精确词面重合：∅
- 字幕：Who says that you two are unrelated? You don't know about the Zhao family.
- 描述：In the text, the subtitle content: "Whoever said that you two are irrelevant, you don't know anything, this is the Zhao family." This sentence may be a response or explanation from the man to the person next to him. Based on the audio clues describing the speaker's low and monotonous voice, the stern and authoritative tone of the speech, as well as the complex emotions and face-covering actions displayed by the man in the video, we can infer that this sentence may have a tone of dissatisfaction or anger. The man may be responding to a comment or questioning from the person next to him and expressing his viewpoint in a stern tone. This sentence may imply that the man is going through some troubles or challenges, and his emotional reaction is due to dissatisfaction or anger towards these troubles.

### 近邻3：samplenew3_00069266

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：defensiveness, explanatory, frustration, incredulous, surprise, tension, urgency
- 与query gold精确词面重合：urgency
- 字幕：But he was hurt like that, it's difficult for us to achieve exactly the same as in the photo, I don't care.
- 描述：In the text, the caption reads: "But given his condition, it's hard for us to match it exactly as in the picture, I don't care." This sentence might be an explanation or defense against the cause of argument or disagreement from an elderly man. Given the speaker's's tense, frustrated, and urgent tone described in the audio clues, and the elderly man's incredulous or surprised emotion portrayed in the video clues, we can infer that this sentence might carry a tone of defense or explanation. The speaker might be attempting to explain why they couldn't not match it exactly as in the picture, possibly due to some reason causing injury or change. Therefore, this sentence could serve as an explanation for the argument or disagreement, aligning with the elderly man's overall display of incredulity or surprise.

### 近邻4：samplenew3_00015239

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, gratitude
- 与query gold精确词面重合：∅
- 字幕：Thank you thank you thank you for watching the action in the future.
- 描述：In the text, the caption reads: "Thanks a lot, looking forward to future actions." This sentence might be the speaker expressing gratitude towards someone or something, and mentioning future actions. Considering the urgency and tension in the speaker's's voice as described in the audio clues, along with an excited tone, we can infer that this statement might carry feelings of gratitude and anticipation. Therefore, this sentence could be the speaker thanking someone for their help or support and expressing hope and expectation for future actions.

### 近邻5：samplenew3_00079222

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：curiosity, enthusiasm, excitement, interested, pride
- 与query gold精确词面重合：∅
- 字幕：Well, to be honest, as a little brother, Cao Zheng has also had some interactions with people in the rivers and lakes, and has also lost some guns and sticks.
- 描述：In the text, the subtitle content says, "Hey, to be honest, this little brother Cao Zheng has also had some interactions with people in the martial arts world." Based on the audio clues describing the speaker's use of a high pitch, emphasis on words, and the use of slang and colloquial language, it can be inferred that the speaker may be feeling excited or enthusiastic and trying to establish a more personal connection with the audience. And based on the video clues of the man's facial expressions and body movements indicating that he is experiencing complex emotions and possibly feeling curious and interested in the other person's speech. Therefore, this sentence may be the man introducing or sharing his experiences in the martial arts world and interactions with people, expressing a sense of pride and excitement.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 36. samplenew3_00076871｜decline｜ΔF1 -0.222222

gold：concern, decisive, engaged, seriousness, tension

query字幕：Why did his marriage with Li Dakang reach the point of breaking up?

源标注描述：In the text, the subtitle reads: "What led their marriage to such a breaking point with Li Dakang." Given the man's's serious facial expressions and body language described in the video clues, as well as the excited, expectant, and anxious emotions indicated in the audio, we can infer that this statement might be part of a speech or discussion he is making. The seriousness in his expression and body language suggests that he is deeply engaged and perhaps even somewhat tense and decisive about this issue or perspective. Therefore, this statement could represent an important question or viewpoint he is raising in exploring the reasons behind their marriage's breakdown, expressing his concern and seriousness about the matter.

off原始输出：The character's emotional state is serious, focused, urgent, tense.

retrieval原始输出：The character's emotional state is serious, focused, urgent, frustrated.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|focused, seriousness, tension, urgency|0.444444|2|2|3|
|retrieval|focused, frustration, seriousness, urgency|0.222222|1|3|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.444444变为0.222222，差值-0.222222。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：tension。
- 相对off新增未精确匹配gold的标签：frustration。

gate：0.120043516；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00111298

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger
- 与query gold精确词面重合：∅
- 字幕：Is Gao Xiaoqin from Shanshui Group the one who gave you a severance payment of 35 million?
- 描述：In the text, captioned content: "Did the High Xiaokuan of the Shanshui Group ever offer you thirty-five million yuan as severance pay for job placement?" Based on the man's's depiction in the video clues, showing him with a thoughtful or focused expression, and the audio clues indicating the speaker having an aggressive tone and a sharp voice, we can infer that this sentence might be a question or accusation directed at the man by the speaker. Given the speaker's aggressive tone and sharp voice, along with the large amount of severance pay mentioned in the caption, it is likely that the speaker has expressed anger or dissatisfaction. However, due to the lack of more contextual information, it cannot be accurately determined the exact emotional state of the speaker.

### 近邻2：samplenew3_00069070

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, burdened with responsibility, tension
- 与query gold精确词面重合：tension
- 字幕：So the charges we reported are suspected to exceed five years.
- 描述：In the text, caption content: "So, the charges we're facing could exceed five years." This sentence might be a man discussing a significant issue or conveying a sense of urgency. Based on the video cues of the man's's serious facial expression and posture, as well as the audio cues of his trembling voice and increased pace, we can infer that this discussion might pertain to a serious crime or something with grave repercussions. Such a discussion could lead the man to feel tense, anxious, and burdened with responsibility.

### 近邻3：samplenew3_00081204

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：dynamism, inspiration, motivation, positive
- 与query gold精确词面重合：∅
- 字幕：We must uphold the righteousness of heaven and earth.
- 描述：In the text, the caption reads: "We shall cultivate the righteous energy of heaven and earth." Given the speaker's tone in the audio cues, characterized by clarity, confidence, and an overt sense of excitement or anticipation, coupled with the positive and energetic expression within the caption, it can be inferred that this statement conveys a state of positivity and dynamism. The phrase might be used by the speaker to motivate or inspire oneself or others, embodying an upwardly focused mindset.

### 近邻4：samplenew3_00086111

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：bewilderment, disappointment, surprise
- 与query gold精确词面重合：∅
- 字幕：I didn't expect Li Dakang to be such a person.
- 描述：In the text, the caption reads: "I didn't think Li Dakang would be this kind of person." This phrase might be an evaluation or response from the speaker about Li Dakang. Given the audio cues indicating that the speaker's has a calm and measured voice with a subtle hint of sadness but it doesn't dominate everything, and video clues showing the character in deep thought, seriousness, or focused state, we can infer that the phrase might carry a sense of disappointment, surprise, or bewilderment. Therefore, this sentence could imply that the speaker is taken aback or dissatisfied by Li Dakang's actions or personality, which alignss with the character's contemplative, serious demeanor in the video.

### 近邻5：samplenew3_00057905

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：authoritative, confidence, positive
- 与query gold精确词面重合：∅
- 字幕：According to the confession of the criminal suspect Zhao Dehan, Ding Yizhen is not a small vendor but a wealthy merchant.
- 描述：In the text, the caption reads: "According to criminal suspect Zhao Dehan, Ding Yizhen is not a small fry, but he's big game and big time." Given the speaker's's voice described in the audio clues as clear and confident, along with an informative and authoritative tone, we can infer that this sentence might be the speaker's's evaluation or description of Ding Yizhen. With the speaker's's tone showing confidence and authority, the statement appears to affirm Ding Yizhen's wealth and status, which alignss with the overall positive mood conveyed by the speaker.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 37. samplenew3_00104945｜decline｜ΔF1 -0.214286

gold：anticipation, concern, disappointment, excitement, frustration

query字幕：Always no different from the major families competing for the wind.

源标注描述：In the text, caption content: "It's always akin to the major clans vying for supremacy." This phrase might be an individual's assessment or reaction to the current situation or event. Given the emotional cues described in the audio, where the individual is experiencing a range of emotions including excitement, anticipation, frustration, and disappointment, as well as the expressions and body language of the injured man and the standing man in the video clues, we can infer that this statement might carry a complex emotion. It includes both excitement and anticipation for the current situation, as well as concern over potential setbacks and disappointment. Therefore, this statement might be an observation and evaluation of the current situation, expressing the individual's's nuanced feelings about the various forces competing for benefits.

off原始输出：The character's emotional state is excitement, anger, frustration.

retrieval原始输出：The character's emotional state is anger, frustration.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, excitement, frustration|0.500000|2|1|3|
|retrieval|anger, frustration|0.285714|1|1|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.500000变为0.285714，差值-0.214286。
- TP变化-1，FP变化+0，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：excitement。

gate：0.119990736；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00088555

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, caring, excitement, warm
- 与query gold精确词面重合：excitement
- 字幕：After finishing the meal, I will accompany you for a walk.
- 描述：In the text, the subtitle content says, "So after we finish our meal, I will accompany you for a walk." This sentence is likely spoken by the person in the black robe to the person lying down. Based on the audio clue of the individual feeling a mixed emotion of excitement and anxiety, and the video clue of the person lying down smiling indicating an open attitude or finding the situation interesting, we can infer that this sentence is likely an invitation or proposal expressing the old man's care and willingness to accompany the person lying down. This sentence may carry a sense of warmth and care, contrasting with the serious conversation between the two individuals in the video.

### 近邻2：samplenew3_00026871

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：advice, assurance, comfort
- 与query gold精确词面重合：∅
- 字幕：You can rest assured to collect silk and weave fabric.
- 描述：In the text, caption reads: "Just rest assured when you receive the silk cloth." This sentence might be a suggestion or comfort offered by the speaker to others. Given the audio cues that suggest the speaker has a calm, confident, and firm tone, along with the video hints showing people smiling and in a relaxed mood, we can infer that this statement could be an encouragement or a way of assuringance. Therefore, the sentence might be the speaker's providing comfort or advice to others, aligning with the positive emotions portrayed in the video.

### 近邻3：samplenew3_00113494

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, confusion, decision, firm, resolute, resolve
- 与query gold精确词面重合：∅
- 字幕：No need to ask more, Xingye returned to Xiaoting.
- 描述：In the text, the caption reads: "No need for further inquiries, Xing Ye is returning to Xiao Ting." This sentence could be a man's's response to someone or some event. Given the urgency, tension, and determination conveyed by the audio cues, along with the man's's confusion, anger, and heightened emotions as depicted in the video clues, we can infer that this phrase might be spoken with a firm and resolute tone. Therefore, this sentence might be the man expressing his resolve and decision, aligning with his overall emotional state.

### 近邻4：samplenew3_00090049

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：appreciation, astonishment
- 与query gold精确词面重合：∅
- 字幕：So can it be like flowing across
- 描述：In the text, "thus it can flow like a tide." This sentence might be a male character's evaluation of some performance or achievement. Given the audio clues with an individual who is described to have an excited tone, a British accent, and the video hints showing a serious expression and meditative posture from the male character, we can infer that this sentence might carry an appreciative or astonished tone. Therefore, this sentence could be a positive and praising affirmation, fitting well with the male character's's overall serious and focused demeanor.

### 近邻5：samplenew3_00101518

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction
- 与query gold精确词面重合：∅
- 字幕：Don't you really understand why I'm angry?
- 描述：In the text, caption content: "Don't you understand why I am angry?" This sentence could be the interrogation or expression of dissatisfaction from the bald man to someone. Based on the audio cues with the description of the angry and frustrated vocal characteristics, along with the video clues featuring the man's's solemn expression and the dignified atmosphere of the room, we can infer that the tone carries an element of anger and discontent. Therefore, this sentence might be the man expressing his dissatisfaction and anger, fitting well with the overall display of his angry emotion.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 38. samplenew3_00063813｜decline｜ΔF1 -0.200000

gold：disappointment, frustration, helplessness

query字幕：My daughter doesn't believe that I have just arrived in Ninghu.

源标注描述：In the text, the caption reads: "My daughter doesn't believe me, even after my arrival in Ninghu." This sentence might be what a man says in a video. Based on the audio hints where which the speaker's's voice is trembling and the tone is monotonous, as well as the video clues featuring the man with a serious expression and a traditional setting, we can infer that this statement might carry a sense of disappointment or helplessness. The man may be expressing his predicament or frustration, while the woman's smile and calm demeanor could be a response to his emotions. Overall, the atmosphere in the video is respectful and culturally meaningful, which supports the idea that the man might be havinging an important conversation or discussing serious matters.

off原始输出：The character's emotional state is disappointment, helplessness, frustration.

retrieval原始输出：The character's emotional state is disappointment, helplessness.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|disappointment, frustration, helplessness|1.000000|3|0|0|
|retrieval|disappointment, helplessness|0.800000|2|0|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由1.000000变为0.800000，差值-0.200000。
- TP变化-1，FP变化+0，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：frustration。

gate：0.119990982；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00007068

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：disappointment, regret, sorry
- 与query gold精确词面重合：disappointment
- 字幕：Unfortunately, the person I met twenty years ago was not you.
- 描述：In the text, caption content: "Alas, if I had encountered you twenty years ago, things might have been different..." This sentence might be an expression of regret or disappointment from a woman towards someone or a situation. Given the audio cues describing the individual's with a monotonous tone, a slower pace of speech, and language usage that appears stiff and formal, we can infer that this phrase may carry a sense of dejection or regret. The woman's's facial expressions and body language suggest that she is experiencing a complex emotional state, possibly feeling disappointed or sorry about a particular person or situation in the past.

### 近邻2：samplenew3_00071230

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：contemplation, tranquility
- 与query gold精确词面重合：∅
- 字幕：Act with more dignity in every move.
- 描述：In the text, the subtitle reads: "Be more solemn in every move." Based on the calm posture of the woman, the serene environment, and the neutral facial expression, it can be inferred that she is experiencing a sense of tranquility or contemplation. Her direct gaze and neutral expression further suggest that she may be focused on her thoughts or the surroundings. This aligns with the subtitle's message of "Be more solemn in every move," implying that she may be contemplating or preparing for some important action. The urgency and importance conveyed by the female voice in the audio also support this speculation. Therefore, it can be inferred that the woman may be facing some important decision or task, and she needs to remain calm and focused.

### 近邻3：samplenew3_00049639

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：lighthearted, playfulness, positive
- 与query gold精确词面重合：∅
- 字幕：Do you think the runway is cute?
- 描述：In the text, the caption reads: "Do you find the track cute?" This sentence could be either a question or an evaluation from the woman to someone nearby or in the audience. Based on the video clues, the woman's exuberant laughter and positive emotional expression, as well as the audio clues of her slow and deliberate speech pattern with an indiscernible accent, we can infer that the tone of this statement might be lighthearted or playful. The woman's positive emotions and smile also support this assumption. Therefore, this sentence could be the woman making a joke about how cute she finds the track, which alignss with her overall positive demeanor.

### 近邻4：samplenew3_00105202

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：distress, gloom, pressure, resignation, stress
- 与query gold精确词面重合：∅
- 字幕：Those grieving family members still rely on me, and they hope to find comfort from us.
- 描述：In the text, caption content: "Those grieving families still rely on me, they still hope to find comfort from us." Based on the audio clues with its description of a trembling voice and rapid breathing, and the video clues showing the woman's confidence and relaxed demeanor, we can infer that this sentence might be the woman expressing her distress and pressure. She could be a professional, possibly a doctor, nurse, or other occupational roles related to grieving families. She might feel under a lot of stress as she bears a great expectation, people looking for solace and support from her. The sentence might carry a sense of gloom or resignation, contrasting with the confident and relaxed posture shown in the video.

### 近邻5：samplenew3_00009163

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：humor, playfulness, positive
- 与query gold精确词面重合：∅
- 字幕：Cousin likes to engage in big battles, the emperor's army is strong and powerful, those who understand it will become my cousin's wise inner circle.
- 描述：In the text, the subtitle reads: "Cousin likes to engage in big battles. Only those with strong soldiers and horses can do it. If I don't understand even a little bit of military affairs, how can I become cousin's wise wife in the future?" This sentence may be spoken by the woman while contemplating her expectations and demands of her cousin. Based on the description of the fast-paced and cheerful background music in the audio cues, the child's excited voice, and the woman's smiling and confident expression in the video cues, we can infer that this sentence may be delivered in a humorous or playful tone. The woman may be expressing her expectations of her cousin in a lighthearted manner, consistent with the overall positive emotions she displays.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 39. samplenew3_00062925｜decline｜ΔF1 -0.194444

gold：desolate, enthusiasm, hope, positive, sincere, uplifting

query字幕：I sincerely hope that you can unite in good faith.

源标注描述：In the text, the caption reads: "I sincerely hope that you can unite as one." Given the emphasis on the words "hope" and "sincerely" in the audio cues provided by the speaker, along with any sense of urgency or desolation they might convey, we can infer that this statement expresses the speaker's's heartfelt desire for unity and cooperation. This message likely carries a positive, uplifting tone, which alignsss with the video cues showing a man making a silly face and potentially engaging in lighthearted banter.

off原始输出：The character's emotional state is optimistic, hopeful, positive.

retrieval原始输出：The character's emotional state is optimistic, hopeful.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|hope, optimism, positive|0.444444|2|1|4|
|retrieval|hope, optimism|0.250000|1|1|5|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.444444变为0.250000，差值-0.194444。
- TP变化-1，FP变化+0，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：positive。

gate：0.120025419；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00044189

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, distrust, doubt, skepticism
- 与query gold精确词面重合：∅
- 字幕：If he really has no problem
- 描述：In the text, the caption reads: "If he truly has no issues." This sentence might be the speaker's expressing doubt or skepticism about someone or a certain situation. Given the video hints of the male subject displaying intense focus, seriousness, and a strong sense of purpose, coupled with the audio cues of the speaker's's slightly shaky voice and hesitant tone, we can infer that the statement might carry an undertone of suspicion, concern, or distrust. Therefore, this sentence could be a way for the speaker to express doubt or worry about someone or a situation, aligning with the overall tense and anxious emotional atmosphere portrayed by the speaker.

### 近邻2：samplenew3_00014510

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anticipation, authority, confidence, determination, excitement
- 与query gold精确词面重合：∅
- 字幕：We are going to set a few fires in the backyard of the Communist Party.
- 描述：In the text, the subtitle reads, "We need to set a fire in the backyard of the communist army." This sentence may indicate that the man is discussing or planning some kind of action or strategy. Based on the serious facial expression and fierce look of the man in the video clues, as well as the formal environment, we can infer that this sentence may express a sense of determination or anger from the man. Additionally, based on the description of the man's deep voice, slow and cautious way of speaking, and the steady and rhythmic drumming accompanying the voice in the audio clues, we can speculate that this sentence may have an authoritative and confident tone, while also implying a sense of excitement and anticipation. Therefore, this sentence may be the man expressing his determination and anger towards some kind of action or strategy, while also showcasing his sense of power, control, excitement, and anticipation.

### 近邻3：samplenew3_00096450

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：empowerment, excitement, joy, motivation
- 与query gold精确词面重合：∅
- 字幕：The core is to do a good job in the clever article, which can induce the cleverness of Yue Sheng Company and the hidden wisdom in the cleverness is to be foolish.
- 描述：In the text, the caption reads: "The essence is to make clever moves in the small realm that can deceive the big wisdom of the Moon Success Company, while the bigger wisdom lies in the apparent foolishness lurking within the small realm." Given the man's's calm and composed demeanor and his neutral facial expression as described in the video hints, along with the positive emotions of joy, excitement, empowerment, and motivation as described in the audio clues, we can infer that this sentence might be the man's's thoughts or viewpoint on a particular topic or plan. Considering the man's's overall display of positive emotions, this sentence could be a reflection of his deep consideration and wisdom on an issue, which alignss with his overall positive demeanor.

### 近邻4：samplenew3_00091390

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：important, respect, seriousness, subdued
- 与query gold精确词面重合：∅
- 字幕：This is the minimum respect I have for you.
- 描述：In the text, the subtitle says, "This is the least respect I can give you." This sentence may be said by one of the men to the other. Based on the description of tension in the individual's voice and possible negative emotions in the audio clues, as well as the serious and focused emotional state of the two men in the video clues, it can be inferred that this sentence may have a serious or subdued tone. This sentence may be expressing respect for the other person in the conversation or emphasizing the importance of respect for the other person. Therefore, this sentence may be emphasizing the importance of the conversation and the value of the other person.

### 近邻5：samplenew3_00104304

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, worry
- 与query gold精确词面重合：∅
- 字幕：He refuses to accept me, I'm afraid I'll be eliminated.
- 描述：In the text, the caption reads: "He just won't accept me; I'm afraid I might be out." Based on the individual's anger and frustration towards the person's's behavior towards the child, as well as their sadness and fear regarding the potential outcome, it can be inferred that this sentence expresses the individual's's concern and unease about possibly failing in their relationship with the child. The phrase "I'm afraid I might be out" suggests the individual's's worry about being excluded or rejected in this situation. Therefore, this sentence conveys feelings of anxiety and concern, aligning with the emotional state of worry and concern displayed by the man in the video clues.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 40. samplenew3_00087639｜decline｜ΔF1 -0.190476

gold：anxiety, confusion, puzzled

query字幕：Who is this person?

源标注描述：In the text, the caption reads: "Who is this person?" This sentence might be a woman's question or curiosity about the identity or actions of someone in the video. Based on the video clues where the woman is focused on her phone, her facial expression is neutral, and her body language does not indicate any clear emotions, along with audio cues indicating a shaky individual voice suggesting they is overwhelmed or under too much stress, we can infer that the sentence may carry an element of confusion, puzzlement, or anxiety. Therefore, this sentence could be the woman expressing her doubts or concerns about the person in the video.

off原始输出：The character's emotional state is confused, puzzled, anxious, tense.

retrieval原始输出：The character's emotional state is confused, puzzled, unfamiliar.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, confusion, puzzled, tension|0.857143|3|1|0|
|retrieval|confusion, puzzled, unfamiliar|0.666667|2|1|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.857143变为0.666667，差值-0.190476。
- TP变化-1，FP变化+0，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：anxiety。
- 相对off新增未精确匹配gold的标签：unfamiliar。
- 相对off移除未精确匹配gold的标签：tension。

gate：0.120029688；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00027868

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confusion, overwhelm, unease
- 与query gold精确词面重合：confusion
- 字幕：Really, I really don't know anything.
- 描述：In the text, the caption reads: "I really, really don't know anything." This line might be said by the woman in the video. Considering the audio cues that describe a personal tone of tension and anxiety, as well as the video clues showing the woman looking down at paper with an anxious facial expression, we can infer that this sentence could be her expression of her ignorance or confusion about a particular problem or task. Her voice is tense and anxious, likely due to feeling overwhelmed and unsure of how to handle the situation. Therefore, this sentence conveys the woman's confusion and unease.

### 近邻2：samplenew3_00015595

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：disappointment, sadness
- 与query gold精确词面重合：∅
- 字幕：Just a few months' time
- 描述：In the text, the subtitle content says, "It's only been a few months." This sentence may be a statement or response from the individual in the conversation. Based on the fluctuations in voice tone and intonation described in the audio clues, as well as the scene of the young woman's focused reading in the video clues, it can be inferred that this sentence may carry a sense of disappointment or sadness. The sentence may imply that the individual is dissatisfied or disappointed with a time constraint or limitation related to something, aligning with the overall emotional state displayed by the individual.

### 近邻3：samplenew3_00028540

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：A person named Li Ziwei
- 描述：In the text, the subtitle content says, "A person named Li Ziwei." This sentence provides a character's name but does not directly reveal the character's emotional state. Based on the neutral expression and lack of clear emotional signs in the video clues, as well as the possibility of the individual experiencing intense negative emotions in the audio clues, we cannot accurately infer Li Ziwei's emotional state. More context or visual clues are needed to gain a deeper understanding of her emotional state.

### 近邻4：samplenew3_00069594

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, lack of experience, sadness, uncertainty
- 与query gold精确词面重合：anxiety
- 字幕：I also don't know, I have never encountered such a thing before, I have no experience.
- 描述：In the text, caption reads: "I don't know, I've never encountered anything like this before, no experience." Based on the woman's gender-neutral facial expression and relaxed body language in the video clues, as well as the speaker's's slight tremble and monotonous tone in the audio cues, we can infer that this sentence might be her response to a particular topic or situation. The woman's gender-neutral expression and relaxed body language suggest that she may not have any particularly strong emotional reaction to the topic or situation. The audio cues, however, hint at negative emotions such as fear, anxiety, or sadness through the speaker's's trembling voice and monotonous tone. Therefore, this sentence could be her response to a new, unfamiliar situation or problem, reflecting her uncertainty and lack of experience.

### 近邻5：samplenew3_00105202

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：distress, gloom, pressure, resignation, stress
- 与query gold精确词面重合：∅
- 字幕：Those grieving family members still rely on me, and they hope to find comfort from us.
- 描述：In the text, caption content: "Those grieving families still rely on me, they still hope to find comfort from us." Based on the audio clues with its description of a trembling voice and rapid breathing, and the video clues showing the woman's confidence and relaxed demeanor, we can infer that this sentence might be the woman expressing her distress and pressure. She could be a professional, possibly a doctor, nurse, or other occupational roles related to grieving families. She might feel under a lot of stress as she bears a great expectation, people looking for solace and support from her. The sentence might carry a sense of gloom or resignation, contrasting with the confident and relaxed posture shown in the video.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 41. samplenew3_00073984｜decline｜ΔF1 -0.190476

gold：anticipating, excitement, happiness, satisfaction

query字幕：Going back to hometown.

源标注描述：In the text, the caption reads: "Back to hometown." This phrase might be what a woman says over the phone to someone else. Considering the video hints of the woman using an old-fashioned telephone and her smile, along with the audio cues of the individual's's high-pitched tone and rapid breathing, we can infer that this statement might carry an element of excitement or anticipation. The woman might feel happy and satisfied about going back home, which alignss with her overall positive demeanor.

off原始输出：The character's emotional state is excited, anticipating, happy.

retrieval原始输出：The character's emotional state is excited, happy.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anticipating, excitement, happiness|0.857143|3|0|1|
|retrieval|excitement, happiness|0.666667|2|0|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.857143变为0.666667，差值-0.190476。
- TP变化-1，FP变化+0，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：anticipating。

gate：0.120012656；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00000368

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：excitement, surprise
- 与query gold精确词面重合：excitement
- 字幕：Gaga, this is new.
- 描述：In the text, caption content: "Brand new, this is a big deal!" This sentence could be describing or comment on something new or a new situation by the speaker. Given the audio clues, where the speaker's full of energy and passionate tone, as well as the video clues, the woman's's expression of surprise or shock, we can infer that the sentence might carry an excited or surprised tone. Therefore, this sentence could be a way for the speaker to express their excitement or surprise about something new or a new situation, which would fit with the woman's overall expression of surprise or shock.

### 近邻2：samplenew3_00076305

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：at ease, caring, concern, content, pleased, relief, satisfaction
- 与query gold精确词面重合：satisfaction
- 字幕：Is your body feeling better now? Much better.
- 描述：In the text, the caption reads: "Is your health better now?" "Much better." This dialogue could be between a woman and another individual. Given the audio cues where describe a voice with a slight rasp, possibly indicating throat discomfort or an itchy sensation, along with a relatively fast pace, which might suggest feelings of anxiety or tension, we can infer that the woman is inquiring about the other person's's well-being, and feels relieved and at ease upon receiving their response, displaying a relaxed and satisfied emotion. Therefore, this conversation might be the woman expressing concern and care, and being pleased and content with the other person's's improvement.

### 近邻3：samplenew3_00078238

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confusion, defensiveness, resentment
- 与query gold精确词面重合：∅
- 字幕：Why are you angry? This can only explain this magazine.
- 描述：In the text, the caption reads: "Why are you upset with me?" This phrase could be a woman's response or explanation to someone. Given the audio cues that describe the speaker's as having an aggressive and hostile tone, and the woman displaying a serious expression and body language in the video clues, we can infer that this statement might carry a tone of resignation or confusion. The woman might be responding to the other person's's anger or frustration, expressing her innocence or lack of understanding. Therefore, this sentence could be the woman's attempt to calm down the other person, or to explain her position.

### 近邻4：samplenew3_00076288

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：self-conscious, tension
- 与query gold精确词面重合：∅
- 字幕：It's not like that. Listen to me. Didn't I tell you that I went to a small stall to buy meat that day?
- 描述：In the text, the caption reads: "It's not like that you have to listen to me, I'll tell you what happened. The day I went to the street vendor to buy meat." Given the personal intonation described in the audio cues - calm and controlled with a slight tremor, and a speech pattern with a hint of accent - it can be inferred that the individual might feel anxious, tense, and self-conscious. The manner in which the content is expressed also supports this inference. The person seems to be explaining or justifying something, with a tone that carries a certain level of tension and uncertainty. Therefore, it can be deduced that the individual likely felt tense and self-conscious during this conversation, possibly due to the need to explain or justify an issue.

### 近邻5：samplenew3_00003436

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：comfort, consolation, contentment, peace, satisfaction, tranquility
- 与query gold精确词面重合：satisfaction
- 字幕：Everything is fine, don't worry anymore.
- 描述：In the text, caption content: "Everything is fine, don't worry anymore." This phrase could be an elderly woman comforting or advising someone. Given the audio cues of the character speaking in a calm and relaxed manner, with a soft and soothing voice, and a slow and organized pace, it suggests that the person might feel a sense of peace and tranquility, satisfaction and contentment. Therefore, this phrase may be an expression of comfort or consolation, implying that everything is alright and there's no need to worry any longer. It alignss with the overall portrayal of the elderly woman as focused, serious, or thoughtful.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 42. samplenew3_00083096｜decline｜ΔF1 -0.181818

gold：anxiety, confusion, dissatisfaction, fear, nervousness, questioning, suspicion

query字幕：The words you said to me before

源标注描述：In the text, the subtitle reads, "You said something to me before." This sentence may be a man's response or questioning to someone. Based on the facial expression and body posture of the man in the video clues, he appears to be contemplating or deep in thought, which may indicate that he is confused or suspicious about something said to him earlier. Additionally, based on the trembling of the individual's voice and the fluctuation in tone in the audio clues, we can infer that he may be experiencing intense emotions such as fear, anxiety, or nervousness. Therefore, this sentence may carry a tone of questioning or dissatisfaction, expressing the man's confusion or dissatisfaction with something said to him earlier.

off原始输出：The character's emotional state is suspicion, questioning, dissatisfaction, unease.

retrieval原始输出：The character's emotional state is suspicion, distrust, anxiety, unease.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|dissatisfaction, questioning, suspicion, unease|0.545455|3|1|4|
|retrieval|anxiety, distrust, suspicion, unease|0.363636|2|2|5|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.545455变为0.363636，差值-0.181818。
- TP变化-1，FP变化+1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：dissatisfaction, questioning。
- 相对off新增未精确匹配gold的标签：distrust。
- 相对off新增命中的gold标签：anxiety。

gate：0.119832002；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [{"prediction_label": "unease", "unmatched_gold_label": "anxiety"}, {"prediction_label": "unease", "unmatched_gold_label": "nervousness"}], "retrieval": [{"prediction_label": "unease", "unmatched_gold_label": "nervousness"}]}

实际5近邻证据：

### 近邻1：samplenew3_00096921

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：loss, nostalgia, sadness
- 与query gold精确词面重合：∅
- 字幕：Those days are no more.
- 描述：In the text, the caption reads: "Those days are gone." This sentence might be a man addressing a woman. Based on the emotional tone of sadness and despair conveyed in the audio clues, as well as the man's's perplexed facial expression and the woman's smile depicted in the video clues, we can infer that this sentence might be a man recalling some past time, expressing nostalgia for and a sense of loss about those good old times. Therefore, this sentence conveys the man's's emotional state, which is a loss and sadness regarding some emotion of the past.

### 近邻2：samplenew3_00088965

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration
- 与query gold精确词面重合：∅
- 字幕：As soon as Cai Chenggong entered the detention center, he was severely beaten.
- 描述：In the text, the subtitle reads: "Cai Chenggong was severely injured as soon as he entered the detention center." This sentence is likely a comment or description in the video. Based on the tense and anxious tone described in the audio clue, as well as the low-frequency rumbling sound in the background, we can infer that this sentence may carry a sense of anger or frustration. The sentence describes Cai Chenggong being severely injured after entering the detention center, which may evoke anger or frustration from the commentator. Therefore, this sentence may be a negative evaluation or a complaint about unfair treatment, aligning with the highly emotional and urgent tone described in the audio clue.

### 近邻3：samplenew3_00043657

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, concern, frustration, worry
- 与query gold精确词面重合：∅
- 字幕：I can't risk your future either.
- 描述：In the text, the caption reads: "I can't risk your future too." This phrase might be a concern or worry that a man expresses to a woman. Given the tone of frustration and anger conveyed in the personal voice as described by the audio clues, and the positive listening behavior shown by the woman along with the man's's reflective and attentive response depicted in the video clues, we can infer that this statement might carry a tone of concern or worry. The man may be worried about the woman's decision or action, fearing it could have negative repercussions on her future. Thus, this sentence might be an expression of concern and worry that alignss with the overall sense of frustration and anger displayed by the man.

### 近邻4：samplenew3_00037746

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：advising, care, comfort, concern, relaxing
- 与query gold精确词面重合：∅
- 字幕：Your Highness, you have worked hard all night, please go back and rest.
- 描述：In the text, the subtitle reads: "Your Highness, you have worked hard all night, go rest." This sentence is likely an expression of care and concern from the man to the woman. Based on the description of the high-pitched and gentle manner of speaking in the audio clues, as well as the calming effect of the accompanying clock sound, it can be inferred that this sentence is likely comforting and advising the woman to relax and rest, expressing care and concern for her. At the same time, based on the woman's expression and body language in the video, showing curiosity and excitement, it can be inferred that the woman may have gone through a difficult work or activity, while the man displays calmness and concern. Therefore, this sentence is likely the man caring for the woman while reminding her to relax and rest, reflecting his care and concern for her.

### 近邻5：samplenew3_00113131

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, positive mood, surprise
- 与query gold精确词面重合：∅
- 字幕：You really impress me.
- 描述：In the text, the caption reads: "You've really caught my attention." This phrase might be the speaker's evaluation or reaction to someone. Given the high pitch, rapid pace of speech indicated in the audio cues, and the man's's interesting facial expressions and involvement in creative activities shown in the video clues, we can infer that this sentence might carry a tone of surprise or admiration. Therefore, it could be a positive appraisal or praise, aligning with the overall positive mood the man exhibits.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 43. samplenew3_00033402｜decline｜ΔF1 -0.166667

gold：apathetic, boredom, negative

query字幕：It's really boring. This is completely harmful to others and not beneficial to oneself.

源标注描述：In the text, the caption reads: "It's really boring, it's just self-defeating." Given the description of the female voice in the audio cues with its flat and emotionless characteristic, as well as her possible experience of negative emotions and respiratory issues, we can infer that this statement might carry a negative, bored, or apathetic tone. Additionally, considering the female's neutral expression and calm demeanor depicted in the video cues, we can deduce that this statement is likely the woman's evaluation of something or an environment, expressing her boredom and dissatisfaction with it. Therefore, this sentence could be the woman's negative assessment of something mundane and unbeneficial to herself.

off原始输出：The character's emotional state is negative, bored, uninterested.

retrieval原始输出：The character's emotional state is negative, bored, uninterested, harmful, useless.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|boredom, negative, uninterested|0.666667|2|1|1|
|retrieval|boredom, harmful, negative, uninterested, useless|0.500000|2|3|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.500000，差值-0.166667。
- TP变化+0，FP变化+2，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：harmful, useless。

gate：0.120072752；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00010116

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：annoyance, disappointment, frustration, pressure, unhappy
- 与query gold精确词面重合：∅
- 字幕：All the money we received for our wedding.
- 描述：In the text, caption content: "We're collecting all the molecules for our wedding." This sentence might be someone in the video discussing the cost issues of their wedding. Given the individual's frustration and annoyance described through audio cues, as well as the impression of confidence and readiness to interact with the audience conveyed by the woman in the video, we can infer that this sentence might carry an undertone of dissatisfaction or complaint. The individual may feel under pressure or unhappy about the arrangements for the wedding expenses, hence expressing such sentiments.

### 近邻2：samplenew3_00071230

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：contemplation, tranquility
- 与query gold精确词面重合：∅
- 字幕：Act with more dignity in every move.
- 描述：In the text, the subtitle reads: "Be more solemn in every move." Based on the calm posture of the woman, the serene environment, and the neutral facial expression, it can be inferred that she is experiencing a sense of tranquility or contemplation. Her direct gaze and neutral expression further suggest that she may be focused on her thoughts or the surroundings. This aligns with the subtitle's message of "Be more solemn in every move," implying that she may be contemplating or preparing for some important action. The urgency and importance conveyed by the female voice in the audio also support this speculation. Therefore, it can be inferred that the woman may be facing some important decision or task, and she needs to remain calm and focused.

### 近邻3：samplenew3_00079284

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, dissatisfaction, frustration, tension, urgency
- 与query gold精确词面重合：∅
- 字幕：There's nothing, I just like money.
- 描述：In the text, the caption reads: "I just like weird money." Based on the video hints, such as the woman's's body language and surroundings, and audio cues like the deep voice of an individual and echoes, we can infer that this phrase might carry a negative or gloomy tone. The woman's's deep contemplation and focused expression, along with the clock in the environment, suggest a sense of urgency or time pressure, while the deep voice and echoes suggest anxiety or tension. Therefore, this sentence could be the woman's self-reproach or negative self-assessment, expressing her frustration or dissatisfaction with her liking for 'weird' money.

### 近邻4：samplenew3_00094188

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：affection, anticipation, aspiration, longing, peace, tranquility
- 与query gold精确词面重合：∅
- 字幕：I sincerely hope that the official can often come to Yong'an Building in the future to taste the dishes I have newly made.
- 描述：In the text, the caption reads: "Sincerely, I hope that the official will often come to Yongan Tower to taste the dishes I've made." Based on the woman's expressions and body language in the video hints, which show a mixture of curiosity and anticipation, along with her overall demeanor suggesting she is in a reflective moment, it can be inferred that the woman's emotional state is one of anticipation and longing. Simultaneously, the tranquil and soothing voice in the audio cues, along with the gentle piano melody, hint at a sense of peace and tranquility she is experiencing. Therefore, the woman's expression in the caption for her wish for the official to frequently visit to taste the dishes she has made can be understood as an expression of her desire and longing to share food with the official, reflecting her affection for him and her aspiration for a good life.

### 近邻5：samplenew3_00069594

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, lack of experience, sadness, uncertainty
- 与query gold精确词面重合：∅
- 字幕：I also don't know, I have never encountered such a thing before, I have no experience.
- 描述：In the text, caption reads: "I don't know, I've never encountered anything like this before, no experience." Based on the woman's gender-neutral facial expression and relaxed body language in the video clues, as well as the speaker's's slight tremble and monotonous tone in the audio cues, we can infer that this sentence might be her response to a particular topic or situation. The woman's gender-neutral expression and relaxed body language suggest that she may not have any particularly strong emotional reaction to the topic or situation. The audio cues, however, hint at negative emotions such as fear, anxiety, or sadness through the speaker's's trembling voice and monotonous tone. Therefore, this sentence could be her response to a new, unfamiliar situation or problem, reflecting her uncertainty and lack of experience.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 44. samplenew3_00063108｜decline｜ΔF1 -0.100000

gold：cheerful, excitement

query字幕：Yeah, love is great.

源标注描述：In the text, the subtitle content "Yes, hello, my loves" may be the old man's greeting or hello to the people around him. Based on the description of the individual's voice in the audio clues, which is filled with a sense of excitement and enthusiasm, as well as the surprised and joyful facial expression and body language displayed by the old man in the video clues, we can infer that this sentence may have an excited and cheerful tone. Therefore, this sentence may be the old man's friendly greeting to the people around him, aligning with the overall positive emotion he is displaying.

off原始输出：The character's emotional state is excited, happy.

retrieval原始输出：The character's emotional state is positive, happy, excited.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|excitement, happiness|0.500000|1|1|1|
|retrieval|excitement, happiness, positive|0.400000|1|2|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.500000变为0.400000，差值-0.100000。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：positive。

gate：0.119926095；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00039888

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：joy, satisfaction
- 与query gold精确词面重合：∅
- 字幕：Special delivery for you
- 描述：In the text, the caption reads: "Special delivery for you, a small gift." Given the audio cues described by the high-pitched male voice, fast pace, and tense, excited tone, along with the video clues showing the man's's focused, friendly, and enthusiastic facial expressions and body language, we can infer that this phrase might be spoken by the man during a speech, performance, or in some ceremonial context. Considering the overall positive emotional state of the man, as well as the video's environmental hints suggesting cultural and historical significance to the event, this sentence could be part of the man's's introduction or presentation of a small gift, conveying his joy and satisfaction to the audience.

### 近邻2：samplenew3_00081020

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, discontent, fury
- 与query gold精确词面重合：∅
- 字幕：I had no choice but to kill Kong Xiu. It has nothing to do with you. Quickly inform the Prime Minister and tell him to order all officials not to trouble me anymore. Did you hear me?
- 描述：In the text, the caption reads: "When I killed Kong Xi, it was under duress and not something to do with any of you. Quickly inform the chancellor and tell him to hurry and order all officials to stop causing trouble for me. Did you hear that?" Given the intense anger and aggressive tone of the individual's's voice as described by the audio clues, along with the serious expression, confident posture, and formal attire of the man depicted in the video clues, we can infer that this statement is likely an expression of his discontent and fury. He might be explaining to those around him or the audience why he killed Kong Xi, and demanding that he be informed by the chancellor to issue orders to all officials to cease bothering him. The strong negative emotions and anger in this statement align with the personal emotional state described in the audio clues.

### 近邻3：samplenew3_00040183

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：indifference, nonchalant, positive
- 与query gold精确词面重合：∅
- 字幕：So what if it's big?
- 描述：In the text, caption content: "Big deal, right?" This phrase could be the man's response to some issue or challenge. Given the video hints of the man's's smile and the joyful mood he exhibits, as well as the audio cues describing tension, excitement, and negative emotions, we can infer that this sentence might carry a tone of nonchalance or indifference. The man might express a lack of concern or importance in his response to something, aligning with the overall positive emotion he portrays.

### 近邻4：samplenew3_00030666

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：impatience, weariness
- 与query gold精确词面重合：∅
- 字幕：If you keep talking endlessly
- 描述：In the text, caption content: "If any of you keep talking endlessly." This sentence could be a response or warning from a man to those around him. Based on the audio cues described with an individual's voice tense and tight, the tone conveying a sense of urgency and impatience, and the video clues showing the man with a serious and firm expression, his brows furrowed, we can infer that this sentence might be delivered in an impatient or weary manner. Therefore, this sentence could be a reaction from the man to excessive talk from those around him, expressing his impatience or weariness. This alignss with the overall solemn and focused emotional state he displays.

### 近邻5：samplenew3_00081604

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：apology, denial, tension, unease
- 与query gold精确词面重合：∅
- 字幕：I'm sorry, I have to apologize to you first.
- 描述：In the text, the caption reads: "I have to apologize to you first." This sentence could be a man's's apology or denial to someone or something. Given the audio clues that describe a trembling voice and an aggressive tone, as well as the video clues showing the man's in a relaxed physical stance, we can infer that this statement might carry a tense or uneasy emotion. Therefore, this sentence may be the man's's attempt to alleviate tension through an apology or denial when facing some sort of stress or setback.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 45. samplenew3_00025865｜decline｜ΔF1 -0.100000

gold：excitement, nervousness

query字幕：I suggest that we hold the wedding at Mr. Shi's place at this time.

源标注描述：In the text, the subtitle content says, "I said let's have the wedding at this time in Shizong." This sentence may indicate that the man is thinking or discussing the arrangements and timing of the wedding. Based on the audio clues describing a slight tremor in the speaker's voice and a high-pitched tone, as well as the video clues of the man's hesitant facial expression and body posture, we can infer that this sentence may carry a sense of nervousness and excitement. The man may be considering the arrangements and preparations for the wedding while feeling both nervous and excited about the upcoming event.

off原始输出：The character's emotional state is confident, excited.

retrieval原始输出：The character's emotional state is confident, excited, enthusiastic.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|confidence, excitement|0.500000|1|1|1|
|retrieval|confidence, enthusiasm, excitement|0.400000|1|2|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.500000变为0.400000，差值-0.100000。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：enthusiasm。

gate：0.120084643；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00001289

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, tension, under pressure
- 与query gold精确词面重合：∅
- 字幕：I have deceived half of Beijing now, if I don't deceive the other half, they will kill me.
- 描述：In the text, the subtitle reads: "I have deceived half of Beijing now, and if I don't deceive the other half, they will kill me." This sentence expresses a very tense and fearful emotional state. Based on the description of the individual's tense and strained voice, aggressive and confrontational tone, and fast pace in the audio clues, we can infer that this sentence is spoken in a state of tension and fear. The individual may feel extremely anxious and under pressure because they have deceived some people and are now facing serious consequences. This tense and fearful emotion aligns with the negative emotions described in the audio clues.

### 近邻2：samplenew3_00002681

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：The master means that Fengzhi is now in Jin Siyu's hands.
- 描述：In the text, the caption reads: "Master's intention is to honor it as currently in Jin Siyu's possession." Given the audio clues, where the speaker uses a monotonous tone and a flat pitch with no inflection or emotion, and at a moderate pace, we can infer that this statement is conveyed in a calm and objective manner. Additionally, the video clues show the person with their eyes closed, head slightly tilted, conveying a sense of tranquility and serenity. Thus, this sentence might be describing or discussing someone's situation being in Jin Siyu's hands, without any apparent emotional connotations.

### 近邻3：samplenew3_00049602

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, approval, respect
- 与query gold精确词面重合：∅
- 字幕：Only the official embroidery workshop can produce such high-quality filial piety.
- 描述：In the text, caption content: "Only pieces of this quality would be found at the official embroidery workshop as an act of respect." This sentence might be a man's's evaluation or praise for something or an item. Based on the high-pitched tone, quick pace of speech, and the serious expression and authoritative demeanor displayed by the man in the audio clues, we can infer that the sentence might carry a tone of admiration or approval. The man might be praising the high quality of some item or someone's capability. Therefore, this sentence alignss with the overall solemn and authoritative presence of the man.

### 近邻4：samplenew3_00065411

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, confusion, emotional detachment, puzzlement, tension
- 与query gold精确词面重合：∅
- 字幕：Teacher Hu is not feeling well.
- 描述：In the text, the caption reads: "Mr. Hu isn't doing well mentally." Given the individual's anxiety, tension, and emotional detachment as described by audio cues, and the confusion or misunderstanding of the man towards the woman's comical expression as indicated by video clues, we can infer that this sentence might be an evaluation or description of Mr. Hu's current mental state. Considering the individual's anxiety and emotional detachment, as well as the man's confusion or puzzlement over the woman's comical expression, we can deduce that this phrase likely describes Mr. Hu's mental state not being well, possibly due to anxiety, tension, or emotional detachment.

### 近邻5：samplenew3_00031058

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, tension
- 与query gold精确词面重合：∅
- 字幕：How did Xu Ru Gui say that she ate the pill?
- 描述：In the text, caption content: "How did Xu Ruigui say she ate that pill?" This sentence might be a man's's question or confusion about an event or plot. Based on the video clues, such as the man's's serious and focused expression and body language, as well as the audio cues describing a highly tense state, we can infer that this sentence might be said with a sense of anxiety or tension. The man's's facial features and overall demeanor indicate that he is very serious about what he is doing, which could be due to his attention and concern for the event. Therefore, this sentence might be the man's's questioning or misunderstanding of a crucial detail or plot, fitting in with his overall tense emotion.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 46. samplenew3_00040801｜decline｜ΔF1 -0.095238

gold：appreciation, gratitude, joy, sorrow

query字幕：Prisov gave me the winning man

源标注描述：In the text, the caption reads: "Pissfu gives me the winning person." This sentence could be an evaluation or praise of Pissfu made by the speaker. Given the emotional tone described in the audio clues, where the speaker might experience a mix of joy and sorrow, as well as the video clues showing the girl's displaying a light-hearted and cheerful demeanor, we can infer that this phrase might carry a tone of appreciation or gratitude. Therefore, the sentence could be a commendation of Pissfu's's performance in winninging the match, which alignss with the overall positive mood of the girl.

off原始输出：The character's emotional state is appreciation, gratitude.

retrieval原始输出：The character's emotional state is satisfaction, appreciation, gratitude.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|appreciation, gratitude|0.666667|2|0|2|
|retrieval|appreciation, gratitude, satisfaction|0.571429|2|1|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.571429，差值-0.095238。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：satisfaction。

gate：0.120027848；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00021047

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, nervousness, overwhelm, stress
- 与query gold精确词面重合：∅
- 字幕：Auntie said that only children who lie are afraid of thunder.
- 描述：In the text, the subtitle reads: "According to the girl's expression in the video hints, which suggests she is either deep in thought or contemplating something, and the audio cues describing a trembling and shivering voice, it indicates that the individual might be experiencing intense emotions such as fear, anxiety, or nervousness. Moreover, the tone of the audio also suggests that the person feels overwhelmed or under significant stress. Therefore, based on these clues, we can infer that the subtitle's 'According to Great Auntie, only liars are afraid of thunder' could be the girl's self-evaluation or reaction. This phrase may imply that the girl feels frightened or anxious, possibly due to facing a stressful or troubling situation."

### 近邻2：samplenew3_00035117

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：distressed, empty, loneliness, sadness
- 与query gold精确词面重合：∅
- 字幕：Suddenly I feel empty in my heart.
- 描述：In the text, the subtitle reads: "Suddenly, I feel empty inside." This sentence is likely a description of the woman's inner feelings. Based on the audio cues describing the individual's voice filled with a sense of surprise and shock, as well as the tense and strained intonation, we can infer that this sentence may express the woman's feelings of emptiness, loss, or loneliness. This aligns with the woman's sad and distressed facial expression in the video, as well as her posture of holding her head and lowering it. Therefore, this sentence may be the woman expressing her current negative emotions and inner turmoil.

### 近邻3：samplenew3_00053187

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：tension, unease
- 与query gold精确词面重合：∅
- 字幕：What's different when there's something, it's just soaring in the sky, where is it?
- 描述：In the text, caption content: "There's something different, it's all about soaring, soaring where." This sentence might be a woman expressing her troubles or anxiety. Based on the woman's anxious expression and body language in the video clues, as well as the speaker's's high-pitched and excited tone of voice in the audio clues, we can infer that this statement may carry an uneasy or tense emotion. The woman might be expressing her troubles or anxiety and hoping to find a solution to the problem.

### 近邻4：samplenew3_00090986

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, dissatisfaction, tension
- 与query gold精确词面重合：∅
- 字幕：The boss is actually innocent, just like Li Junwei.
- 描述：In the text, the subtitle reads: "Actually, the boss, Li Junwei, is also innocent." This sentence may be the individual's defense or explanation of someone or a situation. Based on the audio clues describing the individual's trembling voice and the tone indicating feeling overwhelmed or under a lot of pressure, as well as the video clue of the woman's serious facial expression and furrowed eyebrows, we can infer that this sentence may carry a tense or anxious tone. The individual may feel nervous and anxious while defending someone or a situation because they believe that this person or situation is innocent. The person's emotional state appears to be tense, anxious, and may also have a hint of anger or dissatisfaction as they try to defend an innocent person.

### 近邻5：samplenew3_00098694

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, neutral
- 与query gold精确词面重合：∅
- 字幕：Did the scrap materials that Qige brought down sell as scrap steel? Did the money for each roll come in or not?
- 描述：In the text, caption content: "That Brother Seven's discarded waste sold as scrap steel, a roll more or less, and doesn't that money come from that?" Based on the video clues, the female's facial expressions and body movements do not show any strong emotions, and her wearinging of a professional coat may indicate a formal or work-related setting. Combined with the monotonous tone of the audio clue, it suggests she is in an emotionally detached state. Given these clues, we can infer that this sentence might be described by the female in a calm or neutral tone, without showing strong emotions.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 47. samplenew3_00027140｜decline｜ΔF1 -0.095238

gold：anxiety, concern, stress, tension, worry

query字幕：I have discovered a long-term danger to Minghai.

源标注描述：In the text, the subtitle reads: "I have discovered a long-term harm to Minghai." Based on the serious expression, focus, and thoughtful body language of the man in the video clues, as well as the trembling voice and tense tone of the individual in the audio clues, we can infer that this sentence may be the man discussing an important issue or evaluating a situation, and he is concerned or worried about the long-term impact of this issue or situation. This sentence expresses his concern about the potential threat or harm to Minghai's future. Taking into account the video and audio clues, we can speculate that the man may be facing a tense, anxious, and stressful situation, and he is concerned about the seriousness of this situation and the potential negative impact it may have.

off原始输出：The character's emotional state is concern, worry, urgency, anxiety.

retrieval原始输出：The character's emotional state is concern, worry.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, concern, urgency, worry|0.666667|3|1|2|
|retrieval|concern, worry|0.571429|2|0|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.571429，差值-0.095238。
- TP变化-1，FP变化-1，FN变化+1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：anxiety。
- 相对off移除未精确匹配gold的标签：urgency。

gate：0.120066963；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00019126

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, friendliness, introspective, meditative, open, peaceful
- 与query gold精确词面重合：∅
- 字幕：Do I have the honor of being acquainted with you, ladies?
- 描述：In the text, the subtitle content: "Do you have the fate to meet with you, noble ladies?" Based on the man's focused and calm attitude displayed in the video, as well as the peaceful and serene atmosphere created in the environment, we can infer that this person may be in a state of introspection or meditation. Considering his clothing and the environment, he may be seeking connection with others or searching for spiritual resonance. Therefore, this sentence may be his friendly and peaceful greeting to the audience, expressing his desire to meet others with fate. Overall, the person's emotional state appears calm and open.

### 近邻2：samplenew3_00000340

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, excitement, surprise
- 与query gold精确词面重合：∅
- 字幕：To me, you are like a divine presence that adds wings to a tiger.
- 描述：In the text, the subtitle reads: "To me, the Heavenly Court is also like a tiger with wings." This sentence may be the man's evaluation or reaction to a certain event or situation. Based on the facial expressions and body movements of the man in the video, which show curiosity, entertainment, and a sense of formality or ceremony, as well as the trembling and shaking, hoarse and breathless voice in the audio clues, we can infer that this sentence may carry a sense of excitement, admiration, or surprise. Therefore, this sentence may be the man's expression of excitement, admiration, or surprise towards an event or situation that has impressed him.

### 近邻3：samplenew3_00027997

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction, resentment, sadness
- 与query gold精确词面重合：∅
- 字幕：The one who caused harm to you, Liu Meiduo
- 描述：In the text, caption content: "The originator of all your troubles, Liu Meiduo," based on the character's's deep contemplation and sadness depicted in the video clues along with the suggestion of solemnity and reflective moments from the environment, coupled with the audio hints of a personal voice trembling and shaking, a hesitant and uncertain tone, we can infer that this phrase might be an accusation or blame the speaker is directing towards Liu Meiduo. The phrase might carry an element of anger or sadness, expressing dissatisfaction and resentment over the negative impact Liu Meiduo has had. Overall, this statement implies that the speaker is undergoing a challenging emotional or psychological struggle and is attributing the responsibility to Liu Meiduo.

### 近邻4：samplenew3_00088558

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：guilt, perplexed, unease, worry
- 与query gold精确词面重合：worry
- 字幕：I can't even describe my faults with him.
- 描述：In the text, caption content: "I can't even describe my fault with him." This sentence might be a man's evaluation or response to someone or an event. Given the audio clues where his voice is shaky, he speaks slightly faster, and in the video clues, the man shows expressions of surprise and shock along with his body language, we can infer that this sentence might carry a tense, anxious emotion. The man's's reaction indicates that he is perplexed, unable to articulate his fault with someone or an event due to feelings of guilt, unease, or worry. Without more contextual information, we cannot determine the specific situation and cause, but we can speculate that the man is experiencing a complex emotional state.

### 近邻5：samplenew3_00092809

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, humor, positive
- 与query gold精确词面重合：∅
- 字幕：I am willing to compromise in order to achieve my desires.
- 描述：In the text, caption content: "The king wants to achieve what he desires hence some compromise." This sentence might be spoken by a man in the video. Based on the video clues, including the man's smiling face, body language, and his relaxed and joyful emotional state as indicated by the environment, along with the acoustic feature description provided by an expert in the emotional domain from the audio clues, we can infer that this sentence might have a tone of confidence and humor. The man may be expressing his own intentions and goals, indicating willing to make some compromises for achieving them, but also with a sense of ease and humor. This alignss with the overall positive emotion the man is conveying.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 48. samplenew3_00041408｜decline｜ΔF1 -0.095238

gold：encouragement, positive, praise

query字幕：Simayi is a good assistant to help the Prime Minister achieve great success.

源标注描述：In the text, the caption reads: "Wei Sima, well done as the deputy chancellor for this great endeavor." This line might be spoken by an Asian man in the video. Given the speaker's voice, described as lively and enthusiastic, along with the visual cues of the man's smiling and positive demeanor, we can infer that this phrase could be a form of praise or encouragement. The speaker may be commending or supporting someone ( Wei Sima, for their contribution or assistance in the chancellor's great endeavor. The tone of the statement alignss with the overall positive mood displayed by the man.

off原始输出：The character's emotional state is praise, encouragement, positive mood.

retrieval原始输出：The character's emotional state is praise, encouragement, pride, accomplishment.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|encouragement, positive mood, praise|0.666667|2|1|1|
|retrieval|accomplishment, encouragement, praise, pride|0.571429|2|2|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.571429，差值-0.095238。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：accomplishment, pride。
- 相对off移除未精确匹配gold的标签：positive mood。

gate：0.119949259；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [{"prediction_label": "positive mood", "unmatched_gold_label": "positive"}], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00112458

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：disappointment, discontent, dissatisfaction, fear, tension
- 与query gold精确词面重合：∅
- 字幕：Brother, this statement may not be appropriate. Let's continue with our secret plan, but be careful not to violate orders and create chaos.
- 描述：In the text, caption content: "Brother, this might be inappropriate. Following to our receipt of the secret edict, it's being misused as a false decree." Based on the audio cues describing the speaker's's voice tense and tight, with tremors, and the use of words such as "treason" and "disappointment", it can be inferred that the speaker is likely experiencing a state of tension, fear, and disappointment. The words in this sentence also suggest the speaker's dissatisfaction and disagreement with some action or decision, further supporting the assumption that they may be in a negative emotional state. Therefore, this sentence could be the speaker's's expression of criticism or discontent towards someone or a decision.

### 近邻2：samplenew3_00062463

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, stress, worry
- 与query gold精确词面重合：∅
- 字幕：Nowadays, it is difficult to return after the court of the Holy Morning is hit.
- 描述：In the text, caption reads: "Today's's imperial hall cannot be returned to." This phrase might be a man's inner monologue or an evaluation of the current situation. Given the man's's deep contemplation and neutral expression as depicted in the video clues, and the audio hints suggesting the speaker is speaking in a high-pitched and agitated manner, with rapid and staccato speech, we can infer that this sentence carries a sense of heaviness, anxiety, or stress. Therefore, this sentence could possibly be a way for the man to express his concern or worry about the current work or personal issues, aligning with the overall serious or thoughtful mood he portrays.

### 近邻3：samplenew3_00079134

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：determination, hope, inspired, passion, urgency
- 与query gold精确词面重合：∅
- 字幕：Born in a chaotic world is unfortunate, but if we can turn chaos into ambition.
- 描述：In the text, the caption reads: "Born in turmoil is unfortunate, but yet to turn chaos into resolve." This phrase might be a statement made by the speaker during their speech. Given the audio clues that depict the speaker's with enthusiasm and emotional investment, their voice conveying urgency and importance, as well as the video clues showing the man's's passion, intense discussion, and sense of urgency, we can infer that this phrase could be part of the speaker's emphasizing the unfortunate circumstances of being born in turmoil, while expressing a determination to transform the chaos into a resolve. The sentence may carry an inspiring or uplifting tone, aligning with the overall passion and sense of urgency displayed by the man.

### 近邻4：samplenew3_00085192

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：intense, resolute, seriousness, urgency
- 与query gold精确词面重合：∅
- 字幕：Go, I once ordered them to stick together.
- 描述：In the text, the subtitle reads: "Go, I once commanded them to stand firm." This sentence may be the man expressing his command or request. Based on the description of the individual's tone with a sense of urgency and intensity in the audio cues, as well as the serious expression and focused gaze of the man in the video cues, we can infer that this sentence may carry a serious and resolute tone. Therefore, this sentence may be the man emphasizing an important matter or making a request to others, aligning with the overall display of focus and determination by the man.

### 近邻5：samplenew3_00002131

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, discontent, disgust, dissatisfaction, stress
- 与query gold精确词面重合：∅
- 字幕：Rather than saying they hate Dong Zhuo
- 描述：In the text, the caption reads: "More than hatred towards Zhong Zhuo." Given the individual's voice in the audio clues, which is filled with tension and urgency, speaking with a tight, rapid, and serious tone, and the video clues showing the individual in a calm, composed state with open body language, we can infer that this statement might be an evaluation or reaction from the individual towards someone or a situation. Considering the negative emotions described in the audio cues, including stress, anxiety, and urgency, it is plausible to assume that the sentiment behind this statement could be negative, possibly encompassing dissatisfaction, anger, or disgust. Therefore, this statement might reflect the individual's's discontent or anger towards Zhong Zhuo, aligning with their overall expression of tension and anxiety.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 49. samplenew3_00083364｜decline｜ΔF1 -0.083333

gold：determination, eagerness, positive, urgency

query字幕：Go and see him tonight.

源标注描述：In the text, the caption reads: "Go and see him tonight." This sentence could be a suggestion or decision made by a woman towards someone or something. Given the urgency and excitement conveyed in the speaker's's voice as described through audio clues, and the enthusiastic and expectant emotional display of the woman depicted in video clues, we can infer that this sentence might be expressing the woman's eagerness and sense of urgency towards a particular specific goal or task. She desires to act quickly and accomplish this goal. Therefore, this sentence conveys the woman's positive emotions and determination.

off原始输出：The character's emotional state is urgency, excitement.

retrieval原始输出：The character's emotional state is urgency, importance, excitement, anticipation.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|excitement, urgency|0.333333|1|1|3|
|retrieval|anticipation, excitement, importance, urgency|0.250000|1|3|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.333333变为0.250000，差值-0.083333。
- TP变化+0，FP变化+2，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：anticipation, importance。

gate：0.120010950；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00039627

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, enthusiasm, excitement
- 与query gold精确词面重合：∅
- 字幕：The late nobleman has always been favored by the emperor.
- 描述：In the text, the subtitle reads: "The evening noblewoman has always been favored by the emperor." This sentence is likely spoken by the woman in the video. Based on the confident, excited, and enthusiastic tone described in the audio clues, as well as the serious facial expression and traditional clothing background in the video clues, it can be inferred that the sentence is about an important figure or event. The woman's confident and excited tone suggests positive emotions and attitude towards this figure or event. Based on these observations, it is likely that the woman in the video is discussing an important historical figure, conveying the significance of this figure in history and the emperor's favor towards her with confidence and excitement.

### 近邻2：samplenew3_00085805

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：attention, concern, worry
- 与query gold精确词面重合：∅
- 字幕：You should be careful and take care of your health since you are so young.
- 描述：In the text, the caption reads: "Be careful and take care of your health, you're so young." This phrase might be a concern or reminder from a woman to someone else. Given the individual's described in the audio cues feeling anxious, stressed, and overwhelmed, and the woman's expression of surprise and concern shown in the video clues, we can infer that this phrase might be a concern or reminder from the woman to someone else. She may be worried about the other person's physical condition, or perhaps they is facing stress and challenges. This sentence conveys the woman's concern and attention for the other person.

### 近邻3：samplenew3_00031360

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration
- 与query gold精确词面重合：∅
- 字幕：What is he doing wrong that makes you angry?
- 描述：In the text, the subtitle reads, "He didn't do anything to make you angry." This sentence may be the speaker's questioning or reproach towards someone. Based on the aggressive and confrontational tone described in the audio clues, the high pitch and loud volume, as well as the surprised and frowning expression displayed by the woman in the video, we can infer that this sentence may carry a tone of anger or frustration. Therefore, this sentence may be the speaker's expression of dissatisfaction or lack of understanding towards someone, aligning with the overall negative emotions displayed by the speaker.

### 近邻4：samplenew3_00017954

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, stress, tension
- 与query gold精确词面重合：∅
- 字幕：Your Majesty, please go easy on your punishment.
- 描述：In the text, the caption reads: "Let the emperor show leniency." This phrase could be a plea or beseeching from a female character to the emperor. The audio cues, with their description of a trembling and shaking voice, coupled with rapid and stuttering speech, indicate that the speaker is experiencing intense negative emotions, such as fear or anxiety, and may feel overwhelmed or under considerable stress. Therefore, this sentence might be a plea or request from a female character, expressed due to her tension and fear when facing the emperor, hoping for leniency in her punishment.

### 近邻5：samplenew3_00007791

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, haste
- 与query gold精确词面重合：∅
- 字幕：It's late, you should all leave.
- 描述：In the text, the caption reads: "It's getting late, everyone, disperse." This phrase could be an appeal or suggestion from the speaker to those around them. Given the audio cues describing the speaker's voice filled with urgency and despair, with an agitated tone, and video cues showing a woman displaying confidence and pride, we can infer that this statement might carry a sense of urgency or anxiety. Therefore, the sentence likely conveys a sense of haste, hoping that the people around will leave or end an activity soon. This alignss with the negative emotional state described in the audio cues.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 50. samplenew3_00107358｜decline｜ΔF1 -0.071429

gold：anger, anxiety, dissatisfaction, frustration, pressure

query字幕：But who is willing to die?

源标注描述：In the text, the caption reads: "But who would willingly die." This sentence might be a response or rebuttal in a conversation from a man. Given the speaker's's tone described as tense and agitated, with a high-pitched voice, tight articulation, and a fast pace, along with the video clue showing the man with a serious expression and focused body language, we can infer that this line may carry an undertone of anger or frustration. The man might be expressing his dissatisfaction or opposing view in the conversation, feeling under pressure and anxious due to the context he is in. Therefore, this sentence could be seen as an emotionally charged statement the man makes while expressing his stance.

off原始输出：The character's emotional state is anger, frustration.

retrieval原始输出：The character's emotional state is anger, frustration, despair.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, frustration|0.571429|2|0|3|
|retrieval|anger, despair, frustration|0.500000|2|1|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.571429变为0.500000，差值-0.071429。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：despair。

gate：0.119991370；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00055313

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, confusion
- 与query gold精确词面重合：anxiety
- 字幕：You guys should give me some more time to think.
- 描述：In the text, the subtitle reads, "Give me a moment to think." This sentence may be a request or response from the man to someone nearby. Based on the audio clues describing the individual's high pitch, fast-paced, and energetic speaking style, as well as the video clues showing the man's complex mix of emotions, including furrowed eyebrows, tightly closed lips, and slumped posture, we can infer that this sentence may carry an anxious or confused tone. Therefore, the man may be asking the person next to him to give him some time to think or decide, aligning with the overall display of the man's complex emotions.

### 近邻2：samplenew3_00106739

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：criticism, disappointment, dissatisfaction, judgment, negative emotion
- 与query gold精确词面重合：dissatisfaction
- 字幕：We can't compare to your father
- 描述：In the text, the subtitle content "We are far better than you, your father" can be inferred based on the description of the speaker using an aggressive tone, emphasizing words, and the high-pitched voice in the audio clues. This sentence may be the speaker's way of belittling or mocking certain people, possibly expressing their dissatisfaction or disappointment. Based on the sad facial expression and wiping tears action of the old man in the video clues, as well as the background of him standing in front of a wall, it can be inferred that this sentence may be a criticism or critique of the old man, possibly emphasizing his inability to meet certain standards or expectations. Overall, this sentence expresses a negative emotion and judgment, contradicting the sad emotion displayed by the old man in the video.

### 近邻3：samplenew3_00037157

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, content, indifference, reflective, seriousness
- 与query gold精确词面重合：∅
- 字幕：I have been thinking about it for the first two days.
- 描述：In the text, the caption reads: "I've been thinking about it for the first couple of days." This sentence might be a man describing his process of contemplating on a particular issue or situation. Based on the audio clues where the individual's has a trembling voice, a deliberate and slow pace, and the video cues showing the man with a neutral facial expression, a relaxed or thoughtful posture, we can infer that the tone might be serious or reflective. Therefore, this sentence might describe the man's deep thought process on a particular problem, aligning with his overall calm, content, or indifferent emotional state.

### 近邻4：samplenew3_00060193

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, disappointment
- 与query gold精确词面重合：anger
- 字幕：Also take away this batch of silk in my hand.
- 描述：In the text, the caption reads: "And take away this batch of silk worms from my hands." This line might be uttered by an Asian male in conversation. Given the personal's high-pitched and agitated tone described in the audio clues, as well as the Asian male's complex emotional state depicted in the video clues, which includes curiosity, confusion, and potentially a sense of frustration, we can infer that this statement might carry an undertone of anger or disappointment. The Asian male might feel angry or disappointed about someone taking away the silk worms he is holding, which also explains the emotions conveyed through his facial expressions and body language.

### 近邻5：samplenew3_00110349

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, urgency
- 与query gold精确词面重合：anxiety
- 字幕：If Mogu rises up at this time, we will indeed be caught off guard.
- 描述：In the text, caption content: "If Mog starts a rebellion now, we are indeed caught off guard." This sentence might be spoken by an elderly person in a dialogue within the video. Given the emotional cues described in the audio, such as the individual experiencing high levels of tension and anxiety, along with the video's depiction of the elder's focused demeanor and active participation in the conversation, we can infer that this statement might reflect their concern and sense of urgency about a particular event or situation. They might believe that if Mog does not start a rebellion, we will be caught off guard, meaning unable to respond promptly. The sentence expresses their worry and sense of urgency, aligning with the overall tense and anxious emotional state portrayed.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 51. samplenew3_00006927｜decline｜ΔF1 -0.066667

gold：confusion, curiosity, doubt

query字幕：What are you doing?

源标注描述：In the text, caption content: "What are they doing, anyway?" This sentence might be a question or inquiry about the actions of Asian people in the video. Based on the description of the Asian person's's focused gaze and body posture at something in the video clues, as well as the description of an individual voice that is high-pitched, gasping, nasalized, and sharp in the audio clues, we can infer that this sentence might carry a tone of doubt, curiosity, or confusion. Therefore, this sentence could be a question or doubt about the actions of Asian people, consistent with their emotional state described by the video and audio clues.

off原始输出：The character's emotional state is questioning, confusion.

retrieval原始输出：The character's emotional state is questioning, confusion, dissatisfaction.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|confusion, questioning|0.400000|1|1|2|
|retrieval|confusion, dissatisfaction, questioning|0.333333|1|2|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.400000变为0.333333，差值-0.066667。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：dissatisfaction。

gate：0.119997725；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00077858

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, nervousness, worry
- 与query gold精确词面重合：∅
- 字幕：Did the princess not receive any news from the safety king?
- 描述：In the text, the subtitle reads, "Has the princess not received any messages from the safety king?" This sentence may be the speaker's inquiry about communication or contact between the princess and the safety king. Based on the description of the speaker's calm and restrained voice with a slight tremor, as well as the characteristic of a slight nasal tone in the audio clues, we can infer that the speaker may be experiencing a mixture of emotions, such as fear and anxiety, but is trying to control their emotions. This emotion may be related to the communication or contact between the princess and the safety king, possibly a feeling of worry or nervousness. Therefore, this sentence may carry a tone of concern or nervousness, consistent with the overall emotional state displayed by the speaker.

### 近邻2：samplenew3_00089014

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, surprise
- 与query gold精确词面重合：∅
- 字幕：This Xuanji princess is really different from ordinary people.
- 描述：In the text, the caption reads: "This Princess Xuanji really is unlike anyone else." This sentence could be an evaluation or reaction to Princess Xuanji. Given the man's's serious and focused expression as described in the video hints, and the audio information's tone, we can infer that this statement might carry a tone of admiration or surprise. Therefore, this phrase might be expressing appreciation or amazement at Princess Xuanji's distinctive qualities.

### 近邻3：samplenew3_00058457

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, dissatisfaction, gloom, tension
- 与query gold精确词面重合：∅
- 字幕：Then there will really be no one to talk to in the future.
- 描述：In the text, caption reads: "Then there truly was no one to speak after that." This sentence could be a comment or reaction by a man towards someone or some situation. Given the speaker's's tone described as tense, high-pitched, and with a trembling voice in the audio clues, we can infer that the sentence might carry an air of tension, anxiety, or gloom. Therefore, this sentence might be the man expressing his concern or dissatisfaction about a particular situation, aligning well with the overall serious and tense demeanor he portrays.

### 近邻4：samplenew3_00023055

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, worry
- 与query gold精确词面重合：∅
- 字幕：What if they encounter some problems?
- 描述：In the text, the caption reads: "In case anything goes wrong between them," this phrase might represent an individual's expressing concern or worry about a potential situation or event about to unfold. Given the serious expression of the person and the tense atmosphere in the video clues, as well as the high pitch, tremble, and faster pace of the individual's's voice in the audio clues, we can infer that this sentence might stem from the individual's concern and tension regarding possible issues or difficulties. Therefore, this sentence conveys an individual's feeling of worry and anxiety, which alignss with the tense atmosphere suggested by the video and audio clues.

### 近邻5：samplenew3_00053790

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, determination, seriousness
- 与query gold精确词面重合：∅
- 字幕：As a brother, I will naturally pass the message to you.
- 描述：In the text, the subtitle content: "As a brother, I naturally would convey a message to you," based on the man's's serious facial expression and posture described in the video clues, as well as the speaker's confident and authoritative tone described in the audio clues, we can infer that this statement might be a commitment or assurance made by the man to someone. The man may be responding to someone's request or demand, and expressing his intention to fulfill his responsibility. This statement reflects the man's determination and confidence, which is consistent with his overall display of seriousness and confidence in his emotional state.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 52. samplenew3_00096472｜decline｜ΔF1 -0.066667

gold：challenge, mockery, negative assessment

query字幕：You are here to provoke me.

源标注描述：In the text, caption content: "You've come to provoke me." This phrase might be a man's's evaluation or response to someone. Given the audio cues describing the individual's voice trembling and shaking, with a wavering tone, as well as the video clues showing the man in a state of calmness with his eyes closed, we can infer that this phrase might carry a tone of mockery or challenge. Therefore, this sentence could be a negative assessment or a form of provocative expression, contradicting the man's's overall contemplative and self-reflective demeanor.

off原始输出：The character's emotional state is provocation, mockery.

retrieval原始输出：The character's emotional state is ironic, mocking, negative.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|mockery, provocation|0.400000|1|1|2|
|retrieval|irony, mockery, negative|0.333333|1|2|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.400000变为0.333333，差值-0.066667。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：irony, negative。
- 相对off移除未精确匹配gold的标签：provocation。

gate：0.120035060；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00041485

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, possibly content, satisfaction
- 与query gold精确词面重合：∅
- 字幕：The homestay continues to be built over there in Shenzhen and continues to cooperate with the treatment.
- 描述：In the text, the subtitle reads: "The homestay continues to be built over there in Shenzhen and continues to cooperate with the treatment." This sentence may be the man discussing the progress of a project or plan. Based on the description of the man's calm and steady tone in the audio clue, as well as the posture of the man thinking with his head down in the video clue, it can be inferred that this sentence may be the man describing an ongoing project and expressing satisfaction and calmness about the progress of the project. However, due to the lack of specific background information, we cannot determine the exact emotional state of this person.

### 近邻2：samplenew3_00011267

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：contemplation, exploration, playfulness, positive
- 与query gold精确词面重合：∅
- 字幕：But everything in this world is constantly changing.
- 描述：In the text, caption reads: "Yet everything in this world is ever-changing." This phrase could be an observation or reflection of the world around by an individual. Given the emotional tone described in the audio clues, which conveys a sense of awe and wonder, and the state of confusion and curiosity portrayed in the video clues, we can infer that this sentence might emphasize the fluidity and complexity of the world. Therefore, this statement may carry a tone of contemplation and exploration, aligning with the overall positive and playful mood of the individual.

### 近邻3：samplenew3_00052843

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：If everything goes as planned, I will wear a black tie inside my suit. If there is a change in plans.
- 描述：In the text, caption content: "I'll wear a black tie under my suit if everything goes as planned, or if the plan changes." This sentence might be mentioned by a male character in the context of discussions or negotiations. Given the formal setting and serious atmosphere described in the video cues, along with the male character's's attire, we can infer that this statement might be part of a discussion or arrangement about a plan. The male character mentions that he will wear a black tie under his suit. The sentence lacks any obvious emotional tone but can serve as an explanation or statement about the nature of the discussion or negotiation.

### 近邻4：samplenew3_00017453

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：happiness, satisfaction
- 与query gold精确词面重合：∅
- 字幕：The mirror driver guessed correctly and cancelled the closure of various disaster-stricken areas this year. I have nothing to be unhappy about with such smooth political affairs.
- 描述：In the text, caption content: "The Mirror Office successfully guessed and withdrew today's's decision on settling the sealing of warehouses in various regions. With politics running so smoothly, what should I be unhappy about?" Given the audio clues described by an individual speaking in a calm and even tone, and the video clues featuring a man with a serious expression who may play a significant role, we can infer that this sentence might be the man expressing his satisfaction and happiness over the smooth progress of politics and matters. Although the acoustic information in the audio does not clearly indicate the individual's emotional state, combined with the video clues of the man's serious expression and potential key role, we can infer that this sentence might be expressed in a satisfied and happy tone by the man.

### 近邻5：samplenew3_00021486

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, fear
- 与query gold精确词面重合：∅
- 字幕：If Xie Yu continues to control the Forbidden Army, I'm afraid in the future
- 描述：In the text, the subtitle content "If Xie Yu gains control of the Forbidden Army, it will be troublesome in the future." This sentence may express the man's concern or worry about the current situation or a certain character. Based on the words "if," "dread," and "despair" described in the audio clues, as well as the man's serious facial expression and the solemn atmosphere of the room in the video clues, we can infer that this sentence may express the man's concern about the negative consequences of Xie Yu gaining control of the Forbidden Army. This indicates that the man's emotional state may be one of concern, fear, and anxiety.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 53. samplenew3_00100552｜decline｜ΔF1 -0.047619

gold：humor, light-hearted, positive, teasing

query字幕：We can go up a few more times.

源标注描述：In the text, the caption reads: "We can go up a few more times." This sentence might be a suggestion or proposal from a lady regarding some activity or thing. Based on the video clues showing the lady's in a relaxed and amused state with a touch of embarrassment, and the audio cues describing her with a high-pitched tone and hurried breaths, we can infer that this statement could be a suggestion made by her in a humorous or teasing manner. Therefore, this sentence may carry a light-hearted and humorous tone, consistent with the lady's's overall positive mood.

off原始输出：The character's emotional state is positive, optimistic.

retrieval原始输出：The character's emotional state is positive, optimistic, encouraging.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|optimism, positive|0.333333|1|1|3|
|retrieval|encouragement, optimism, positive|0.285714|1|2|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.333333变为0.285714，差值-0.047619。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：encouragement。

gate：0.119997904；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00030835

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, enthusiasm, humility, uncertainty
- 与query gold精确词面重合：∅
- 字幕：I suddenly have an immature little plan.
- 描述：In the text, the caption reads: "I suddenly had an immature little plan." This sentence might be what the lady says to someone off-camera in the video. Considering the video hints such as her confident smile, gestures, and fully engaged facial expressions and body movements, along with the audio cues of the speaker's's hesitation and uncertain tone, we can infer that this sentence could be her way of expressing a new idea or plan with humility and uncertainty. She might be sharing an idea or plan that is not yet fully developed or certain, and she hopes to receive feedback or opinions from the other person. This alignss with the overall confidence and enthusiasm she displays for participating in discussions.

### 近邻2：samplenew3_00081105

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：disappointment, frustration, unhappiness
- 与query gold精确词面重合：∅
- 字幕：At least others dare to be themselves, what about you?
- 描述：In the text, caption reads: "At least others dare to be themselves, what about you?" This phrase could be the young woman's evaluation or reaction to someone or a situation. Based on the audio clues, her voice is high-pitched, fast-paced, and loud, suggesting it might carry an element of excitement or tension. Considering the video clues showing her with an unhappy expression and body language, along with the described supermarket setting that might provoke negative feelings, this phrase could be her expression of dissatisfaction or frustration towards someone or a situation. Therefore, it may come across as critical or blaming, aligning with her overall mood of unhappiness or disappointment.

### 近邻3：samplenew3_00106076

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：encouragement, mutual assistance, recognition, support
- 与query gold精确词面重合：∅
- 字幕：Chinese people should definitely help each other.
- 描述：In the text, the subtitle content says, "Chinese people should definitely help Chinese people." This statement indicates the individual's attitude towards mutual assistance among Chinese people. Based on the audio clues describing the individual's experience of intense negative emotions such as fear or anxiety, as well as the positive and close emotions displayed by the women in the video, we can infer that this statement may carry an encouraging or supportive tone. The individual may be expressing their recognition and support for mutual assistance among Chinese people, aligning with the overall positive emotions exhibited by the women.

### 近邻4：samplenew3_00054951

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, unease
- 与query gold精确词面重合：∅
- 字幕：Uncle, I really feel
- 描述：In the text, caption content: "Grandpa, I really feel." This sentence might represent the speaker's's personal view or feelings on a particular subject or situation. Given the audio cues describing the speaker's voice shaking and the tone conveying stress and overwhelmingness, as well as the video cues showing the woman's comical expression and relaxed posture, we can infer that the sentence may carry an anxious or uneasy emotion. Therefore, this sentence could be the speaker expressing their concerns or dissatisfaction, contrasting with the joyful mood the woman is portrayed to have in the video.

### 近邻5：samplenew3_00108093

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, confusion, disappointment, tension
- 与query gold精确词面重合：∅
- 字幕：I think I may not have expressed my story well just now. Can you listen to me for a moment?
- 描述：In the text, caption content: "I think I might not have articulated my story well just now, could you listen to me for a moment more?" This sentence might be spoken by a woman wearing a beige coat to another woman. From the video clues, there's a sudden change in the woman's expression, from smiling to crying, and with the pitch and tone variations in the female voice in the audio clues, we can infer that this sentence may carry a tone of request, pleading, or explanation. The woman might feel confused, dissatisfied, or misunderstood in the conversation and thus requests the other person to listen for a moment more to better express her story. This sentence conveys the emotional state of the woman, possibly feeling anxious, tense, confused, or disappointed.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 54. samplenew3_00087166｜decline｜ΔF1 -0.047619

gold：anxiety, determination, fear

query字幕：He will definitely repay double in the future.

源标注描述：In the text, the caption states: "He shall pay back in full someday." Given the individual's facial expressions described in the video clues, which show a neutral demeanor with no clear indication of strong emotions or reactions, and the audio clues suggesting that the individual might be experiencing intense emotions such as fear, anxiety, or anger, we can infer that this statement might be an internal self-affirmation or determination for the individual. The individual may be facing some difficulties or challenges, feeling anxious and overwhelmed, but he is determined to repay or overcome these difficulties in the future. Therefore, this phrase might express the individual's's firmness and determination, which alignss with the emotional state indicated by the neutral facial expressions observed in the video clues.

off原始输出：The character's emotional state is anger, frustration, determination.

retrieval原始输出：The character's emotional state is anger, frustration, confidence, determination.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, determination, frustration|0.333333|1|2|2|
|retrieval|anger, confidence, determination, frustration|0.285714|1|3|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.333333变为0.285714，差值-0.047619。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：confidence。

gate：0.120018534；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00020439

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, frustration
- 与query gold精确词面重合：anxiety
- 字幕：How can you say such embarrassing words
- 描述：In the text, with subtitles stating: "How can you say such shameful words." Given the audio cues describing the individual speaking quickly, with a tone of frustration or anger, and video clues suggesting the setting is dim, possibly indicating a serious or intense conversation, we can infer that this statement might be a negative evaluation or reaction to the content of the individual's's speech. Considering the person may be experiencing a series of negative emotions including anxiety, frustration, and anger, this statement could reflect dissatisfaction or criticism towards the content of the individual's's speech. Therefore, the sentence carries a negative emotional undertone, aligning with the overall display of negative emotions from the individual.

### 近邻2：samplenew3_00078377

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：excitement, pride
- 与query gold精确词面重合：∅
- 字幕：My dear, I appoint you as the Grand General for the protection of the country. You shall travel across the land, carrying out the emperor's orders and commanding the army.
- 描述：In the text, the subtitle reads: "My dear subject, I hereby confer upon you the title of Great General for National Protection, with the responsibility to lead the troops directly and fulfill imperial commands. You will bear the carriage of the emperor's's vehicle and command the forces across the land under the auspices of heaven." Given the mix of excitement and pride conveyed through the audio clues describing personal experiences, along with the respectful language and prestigious titles bestowed, we can infer that this sentence likely represents an official appointment or commendation. It is meant to acknowledge and affirm the achievements and contributions of the individual. Consequently, this statement might be delivered in a solemn and formal tone, which alignss well with the overall emotion of excitement and pride exhibited by the person.

### 近邻3：samplenew3_00100760

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, stress, worry
- 与query gold精确词面重合：anxiety
- 字幕：The Shu army has already left Chang'an, less than a hundred miles away. If this continues, within a few months, I will become the ruler of a doomed country.
- 描述：In the text, caption reads: "The Shu army is less than one hundred miles away from Chang'an. At this rate, I'm looking at being a fallen kingdom's's last ruler within a few months." This statement could be an evaluation or prediction of the current situation by the speaker. Given the audio cues describing the speaker's in a high-pitched and agitated tone, with a rapid speech pattern and repetition of words, we can infer that the speaker might be experiencing a state of intense, anxious, and stressful emotions. Therefore, this statement likely expresses the speaker's's concern and worry about the nation's's future prospects and their awareness of the dilemma as the ruler of the kingdom.

### 近邻4：samplenew3_00022982

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, excitement, satisfaction
- 与query gold精确词面重合：∅
- 字幕：I hereby appoint you as the Grand General for the Western Expedition.
- 描述：In the text, caption content: "I have ordered to summon as the Great General of the West Campaign." This sentence might be spoken by a man in the video. Based on the tone described in the audio clues, which is clear and confident, and the emotional cues from the video such as the man's's calm demeanor and smile, we can infer that he might be proudly announcing his appointment as the Great General of the West Campaign. This suggests that he may feel excited and satisfied, while also showcasing his confidence and ability to control his emotions.

### 近邻5：samplenew3_00053999

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration
- 与query gold精确词面重合：∅
- 字幕：What kind of person is this Cai Quan and where did he come from?
- 描述：In the text, with subtitles: "What kind of person is this Cai Quan? Where did he pop up from?" Based on the speaker's's challenging tone in the audio cues, their rapid speech rate, and the repetitive use of specific phrases and emphasized words, it can be inferred that the speaker might be experiencing intense negative emotions, such as anger or frustration. The questioning and discontented tone, along with the evaluation of "Cai Quan," further support this inference. Therefore, this sentence likely represents the speakerer's negative assessment or dissatisfaction with "Cai Quan."

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 55. samplenew3_00069803｜decline｜ΔF1 -0.044444

gold：attentive, cool, humor, interesting, irony, unconventional

query字幕：Sometimes fake works better than real.

源标注描述：In the text, the caption reads: "Sometimes a lie is more effective than the truth." This statement could be what a man says in a video. Given the audio cues that describe an individual with a high-pitched voice, speaking very quickly, and the video clues showing the man with a calm and focused demeanor, we can infer that this phrase might be delivered with a hint of irony or humor. Therefore, this sentence could be the man expressing an interesting or unconventional viewpoint in a situation, which alignss with his overall portrayal of being cool and attentive.

off原始输出：The character's emotional state is ironic, humorous, attention-grabing.

retrieval原始输出：The character's emotional state is ironic, humorous, thought-provoking, complex.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|attention-grabing, humor, irony|0.444444|2|1|4|
|retrieval|complex, humor, irony, thought-provoking|0.400000|2|2|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.444444变为0.400000，差值-0.044444。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：complex, thought-provoking。
- 相对off移除未精确匹配gold的标签：attention-grabing。

gate：0.119950406；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00008261

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, excitement, pride
- 与query gold精确词面重合：∅
- 字幕：Heroes and heroes can surpass a hundred thousand gold and silver.
- 描述：In the text, caption reads: "A hero's feats surpass ten thousand golds." This sentence might be used by a speaker to describe a situation or express an opinion. Given the audio cues of the speaker's's passionate and confident tone, as well as the neutral or calm demeanor of the man in the video clues, we can infer that this statement could be used by the speaker to emphasize their point of view or express a positive emotion such as excitement, pride, or confidence. However, without more context or information about the situation, it is difficult to accurately predict the specific emotional state of the speaker.

### 近邻2：samplenew3_00079134

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：determination, hope, inspired, passion, urgency
- 与query gold精确词面重合：∅
- 字幕：Born in a chaotic world is unfortunate, but if we can turn chaos into ambition.
- 描述：In the text, the caption reads: "Born in turmoil is unfortunate, but yet to turn chaos into resolve." This phrase might be a statement made by the speaker during their speech. Given the audio clues that depict the speaker's with enthusiasm and emotional investment, their voice conveying urgency and importance, as well as the video clues showing the man's's passion, intense discussion, and sense of urgency, we can infer that this phrase could be part of the speaker's emphasizing the unfortunate circumstances of being born in turmoil, while expressing a determination to transform the chaos into a resolve. The sentence may carry an inspiring or uplifting tone, aligning with the overall passion and sense of urgency displayed by the man.

### 近邻3：samplenew3_00112458

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：disappointment, discontent, dissatisfaction, fear, tension
- 与query gold精确词面重合：∅
- 字幕：Brother, this statement may not be appropriate. Let's continue with our secret plan, but be careful not to violate orders and create chaos.
- 描述：In the text, caption content: "Brother, this might be inappropriate. Following to our receipt of the secret edict, it's being misused as a false decree." Based on the audio cues describing the speaker's's voice tense and tight, with tremors, and the use of words such as "treason" and "disappointment", it can be inferred that the speaker is likely experiencing a state of tension, fear, and disappointment. The words in this sentence also suggest the speaker's dissatisfaction and disagreement with some action or decision, further supporting the assumption that they may be in a negative emotional state. Therefore, this sentence could be the speaker's's expression of criticism or discontent towards someone or a decision.

### 近邻4：samplenew3_00111704

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：care, concern
- 与query gold精确词面重合：∅
- 字幕：Is your illness getting better?
- 描述：In the text, the subtitle says, "Are you feeling better?" This sentence may be the bald man's inquiry or concern for someone. Based on the audio clues describing the individual's higher pitch voice, positive and enthusiastic tone, as well as the video clues of the man's serious and focused expression and the formality of the environment, we can infer that this sentence may carry a tone of care or concern. Therefore, this sentence may be the man's inquiry about someone's health, expressing his care and concern.

### 近邻5：samplenew3_00115309

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction, unhappiness
- 与query gold精确词面重合：∅
- 字幕：In this way, Yuan Shao, the only person in the world, will enjoy it alone.
- 描述：In the text, caption content: "This way, the mighty man, Yuan Shao, has everything to himself." This sentence could be a comment or reaction by a man to some situation or event. Given the high-pitched tone and possible sense of anxiety or irritation suggested in the audio clues, as well as the man's's angry expression and body language in the video clues, we can infer that this phrase might carry an undertone of dissatisfaction or anger. The man may be unhappy with some unfair or unjust situation, feeling that someone is monopolizing certain rights or benefits, which further supports his state of anger.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 56. samplenew3_00034822｜decline｜ΔF1 -0.035714

gold：anger, anxiety, displeased, under pressure

query字幕：My mom is called Xichuan on the upper side, not not not.

源标注描述：In the text, the caption reads: "My mother is on top of West Sichuan and she won't listen no matter what." This sentence might be said by a woman in the video. Based on the audio cues where describes an individual speaking with a high pitch, tense voice, indicatinging they may feel anxious or under pressure. Additionally, considering the woman's displeased or angry expression as depicted in the video, along with her facial expressions and body language suggesting negative emotions, we can infer that this sentence might be the woman expressing her dissatisfaction or refusal towards someone or something. This alignss with the overall negative emotion she portrays.

off原始输出：The character's emotional state is anxious, tense, uneasy.

retrieval原始输出：The character's emotional state is anxious, tense, dissatisfied, unhappy.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, tension, unease|0.285714|1|2|3|
|retrieval|anxiety, dissatisfaction, tension, unhappy|0.250000|1|3|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.285714变为0.250000，差值-0.035714。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：dissatisfaction, unhappy。
- 相对off移除未精确匹配gold的标签：unease。

gate：0.120071501；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00057406

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, interested, solemn, thoughtful
- 与query gold精确词面重合：∅
- 字幕：I love Winnie the Pooh.
- 描述：In the text, the caption reads: "So, I reckon Venerabilis." This sentence might be a woman's inner monologue as she contemplates or ponders. Based on the video hints of her serious and focused facial expression and body language, as well as the audio clues indicating of the speaker's's trembling voice and hesitant tone, we can infer that this sentence expresses the woman's's evaluation or thoughts about Venerabilis. Given the seriousness and concentration in her emotional state, this statement likely carries a solemn or thoughtful tone, suggesting that she has a certain interest or concern for Venerabilis.

### 近邻2：samplenew3_00022634

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：blame, criticism, excitement, sadness, surprise
- 与query gold精确词面重合：∅
- 字幕：You don't even have basic impulses, you don't care from the root.
- 描述：In the text, the caption reads: "You lack even the most basic impulse, you just don't care at your core." This phrase could be a male voice's's evaluation or response to someone or a situation. Given the audio cues of a fast-paced, sharp tone and an emphasis on the importance of conveying the message with enthusiasm, we can infer that the tone might carry a critical or blaming nature. The woman's's varying emotional states depicted in the video clues, such as surprise, excitement, and sadness, may relate to the emotions conveyed by this statement. However, without specific background information or further description of the context, we cannot determine the exact meaning or target of this sentence.

### 近邻3：samplenew3_00034490

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：annoyance, confidence, determination, frustration, resolve, self-assuredness
- 与query gold精确词面重合：∅
- 字幕：I will never let him be in a sorry state.
- 描述：In the text, the caption reads: "I will never let him suffer from my favor." Given the speaker's's delivery as described in the audio cues, with confidence and firmness, the tone being assertive and strong, it suggests that she has control over the situation and possibly experienced feelings of frustration and annoyance. From this, we can infer that the statement expresses the speaker's's determination and resolve, that she will not allow someone to gain her favor or exploit her. This statement reflects the speaker's's confidence and determination, aligning with their overall display of steadfastness and self-assuredness.

### 近邻4：samplenew3_00095635

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：appreciation, gratitude, positive
- 与query gold精确词面重合：∅
- 字幕：Thank you for your liking and affirmation.
- 描述：In the text, the caption reads: "Thank you for your liking and affirmation." This phrase might be a woman expressing gratitude to someone off-screen. Given contextual clues from the video such as the woman enjoying food and engaging in conversation, and emotional domain experts analyzing the acoustic information within the audio to predict the individual's's emotional state, we can infer that this phrase likely represents her expression of appreciation and gratitude towards the other person. Thus, this sentence conveys the woman's positive and appreciative emotional state.

### 近邻5：samplenew3_00079885

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, disappointment, dissatisfaction, negative
- 与query gold精确词面重合：anxiety
- 字幕：That big financial company
- 描述：In the text, the subtitle content says, "That big financial company." This sentence may be one of the reasons the woman is expressing her emotional distress. Based on the woman's painful and sad expression in the video clues, as well as the trembling and tension in her voice in the audio clues, we can infer that this sentence may be related to the problems or difficulties she encountered at the financial company. This sentence may imply that she is dissatisfied, anxious, or disappointed with her experience at the financial company, further exacerbating her negative emotions.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 57. samplenew3_00060874｜decline｜ΔF1 -0.035714

gold：familiar, friendliness, light-hearted, trusting

query字幕：There's no need to be so polite among ourselves.

源标注描述：In the text, the caption reads: "We're all friends here, no need for formalities." This sentence might be one person addressing to another. Given the speaker's's casual and conversational tone as described in the audio clues, and the two people's relaxed body language and smiling expressions depicted in the video clues, we can infer that the phrase might carry a light-hearted or friendly tone. Therefore, this sentence could be a friendly reminder or suggestion, conveying familiarity and trust between the two individuals.

off原始输出：The character's emotional state is friendly, intimate, positive.

retrieval原始输出：The character's emotional state is friendly, close, relaxed, comfortable.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|friendliness, intimate, positive|0.285714|1|2|3|
|retrieval|close, comfortable, friendliness, relaxation|0.250000|1|3|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.285714变为0.250000，差值-0.035714。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：close, comfortable, relaxation。
- 相对off移除未精确匹配gold的标签：intimate, positive。

gate：0.120008752；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00049714

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, challenge, encouragement, motivation, positive mood
- 与query gold精确词面重合：∅
- 字幕：Let's see who volunteers to help us with reading comprehension, okay?
- 描述：In the text, the caption reads: "Let's see who volunteers to give us an interpretation of this passage, shall we?" This sentence might be a request or challenge directed at someone off-camera or the audience by a man. Given the character's tone described in the audio cues, which is fast-paced and energetic, along with the video clues showing the man's expressing confusion and anxious emotions, we can infer that the sentence might carry a tone of challenge or anticipation. Therefore, this statement could be a form of encouragement or motivational expression, aligning with the overall positive mood conveyed by the man.

### 近邻2：samplenew3_00004179

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, firmness
- 与query gold精确词面重合：∅
- 字幕：I am indeed a senior student at the School of Economics and Trade and also a volunteer for the Sunshine Action.
- 描述：In the text, the caption reads: "Indeed, they is a fourth-year student at the University of Economics and Business, and also a volunteer for the Sunlight Action." Given the individual's tone being high and their speech pace being fast, as well as the confidence and firmness in the voice according to the audio cues, we can infer that this sentence might be a response to some doubt or challenge. The individual might feel challenged about their identity or qualifications for participating in an activity, hence the response carries a note of confidence and firmness. This response could be aimed at proving one's identity and qualifications, as well as defending the legality of the activity they is involved in. Therefore, this sentence might carry a sense of confidence and firmness.

### 近邻3：samplenew3_00062232

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, leadership, positive
- 与query gold精确词面重合：∅
- 字幕：You belong to the first stage of breaking the ice, which is very important. I will take care of the remaining second stage.
- 描述：In the text, caption content: "You belong to the first wave that breaks the ice and is crucial, the rest of the second stage is left to me." This sentence could be a man's's evaluation or commitment to someone or a team. Based on the video clues showing his enthusiasm, confidence, and decisive body language, as well as the audio clues describing the man's's firm and confident tone and control over his emotions, we can infer that this sentence might be the man expressing his affirmation and appreciation for someone or a team's work or performance in the first phase, and promising to continue supporting and assisting them in the second phase. This sentence conveys the man's's positive, confident, and leadership emotional state, which aligns with his positive emotions shown in the video.

### 近邻4：samplenew3_00111163

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：congratulatory, excitement, positive
- 与query gold精确词面重合：∅
- 字幕：Congratulations, you have become the male lead in the play.
- 描述：In the text, the subtitle reads, "Congratulations on becoming the male lead in the flow play." This sentence is likely a congratulatory or praising remark towards the man. Based on the audio clue describing the individual's high pitch, excited tone, and the video clue of the man's smiling face and positive emotional state, we can infer that this sentence is a positive expression, possibly congratulating the man on his success in a role or performance. This aligns with the overall positive emotions displayed by the man.

### 近邻5：samplenew3_00072404

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction
- 与query gold精确词面重合：∅
- 字幕：Don't say "if" anymore if they have affected the Nirvana Plan.
- 描述：In the text, the caption reads: "Don't keep saying they affected the rebirth plan." This sentence might be a man's response or advice to someone or something. Given the description of an individual speaking in a high-pitched, agitated manner and with a tone indicating of frustration or anger, we can infer that this sentence may be conveyed with a sense of dissatisfaction or anger. Therefore, this sentence could be the man's's way of expressing his dissatisfaction or criticism towards someone or something, which aligns with his overall negative emotion.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 58. samplenew3_00084882｜decline｜ΔF1 -0.022222

gold：anxiety, confusion, dissatisfaction, gloom, puzzled, tension, under pressure

query字幕：I never understand what you are saying.

源标注描述：In the text, the caption reads: "I never quite get what you're trying to say." This phrase might be a man expressing confusion and lack of understanding towards a woman. Given the high-pitched, agitated tone of speech described in the audio clues, as well as the video clues showing the man gripping his hands in a private or domestic setting, we can infer that he may feel anxious, tense, or under pressure, and is puzzled and unable to understand the woman's's words. Therefore, this sentence might carry an undertone of dissatisfaction or gloom, fitting with the man's's overall portrayal of tension and anxiety.

off原始输出：The character's emotional state is confused, frustrated.

retrieval原始输出：The character's emotional state is confused, frustrated, overwhelmed.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|confusion, frustration|0.222222|1|1|6|
|retrieval|confusion, frustration, overwhelm|0.200000|1|2|6|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.222222变为0.200000，差值-0.022222。
- TP变化+0，FP变化+1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：overwhelm。

gate：0.120080523；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [{"prediction_label": "frustration", "unmatched_gold_label": "dissatisfaction"}], "retrieval": [{"prediction_label": "frustration", "unmatched_gold_label": "dissatisfaction"}]}

实际5近邻证据：

### 近邻1：samplenew3_00098366

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern
- 与query gold精确词面重合：anxiety
- 字幕：What will happen to the official career of the Wang family in the future?
- 描述：In the text, the subtitle reads, "What will happen to the Wang family's future generations?" Based on the calm and composed attitude displayed by the woman in the video, as well as the serene and peaceful facial expression, we can infer that this sentence may be something the woman is saying during her process of thinking or introspection. Additionally, based on the description in the audio of the individual's trembling voice and rapid, shallow breathing, as well as the indication of high emotional distress, we can infer that this sentence may carry a sense of worry or anxiety. Therefore, this sentence may indicate that the woman is concerned or anxious about the future development of the Wang family and is contemplating the direction their official careers will take.

### 近邻2：samplenew3_00066072

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：comfortable, confidence, firm, relaxation
- 与query gold精确词面重合：∅
- 字幕：Practice is the only criterion for testing whether something can work or not.
- 描述：In the text, the subtitle says, "Practice is the only criterion for testing whether something can be done." This sentence may be an individual's viewpoint or statement in the conversation. Based on the description of fluctuations in the individual's tone and intonation in the audio clues, as well as the relaxed and comfortable emotional state exhibited by the woman in the video clues, we can infer that this sentence may be spoken with a confident or firm tone. Therefore, this sentence may be the individual expressing their viewpoint or belief in the conversation, aligning with the overall relaxed and comfortable emotional state displayed by the woman.

### 近邻3：samplenew3_00060507

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：comforting, concern, important, support, urgency
- 与query gold精确词面重合：∅
- 字幕：I'm going to see your Uncle Guangming.
- 描述：In the text, the caption reads: "I went to see your bright uncle." This sentence might be spoken by a woman to a man. Given the video hints of concern and attention shown by the woman, as well as the man's's expressions and posture suggesting he might be troubled, depressed, or deep in thought, we can infer that the woman's intention in saying this is to provide support and comfort. Additionally, based on the audio clues of a trembling voice and slightly faster pace, we can deduce that this statement might carry a sense of urgency or importance. It could be that the woman is trying to inform the man that she will visit his uncle to help alleviate his stress or offer support.

### 近邻4：samplenew3_00061231

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：positive, satisfaction, stable
- 与query gold精确词面重合：∅
- 字幕：
- 描述：In the text, the caption reads: "It's more like in these days of Bo Yuan." This sentence might be spoken by a woman in the video. Based on the video clues describing her calm expression, relaxed body language, and the surrounding environment suggesting she is in a social setting interacting with others, we can infer that this phrase could be her evaluation or reminiscence about someone or somewhere. According to the audio clues described as "as an expert in emotional fields, I can analyze the acoustic information in the audio to identify clues related to personal emotions", we can infer that this sentence might be her emotional evaluation or analysis of someone or somewhere. Therefore, this sentence could be a positive and satisfying way for her to reflect on or evaluate the past days spent in Bo Yuan, consistent with her overall display of emotional stability and satisfaction.

### 近邻5：samplenew3_00004528

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, criticism, dissatisfaction, frustration
- 与query gold精确词面重合：dissatisfaction
- 字幕：Opposing the judge, I believe that the plaintiff's attorney cannot set the interests of the party against the interests of the impoverished farmers.
- 描述：In the text, caption reads: "Against the presiding judge, I believe that the plaintiff's attorney should not pit the interests of the party against those of impoverished farmers." Given the speaker's's voice filled with intense anger and frustration as described in the audio cues, along with an aggressive and confrontational tone, we can infer that this statement is the speaker's's opposition and criticism of the plaintiff's attorney's viewpoint. The speaker likely feels that the plaintiff's attorney has not taken into account the interests of the party and impoverished farmers while handling the case, which has provoked their anger and dissatisfaction. Thus, this sentence expresses the speaker's's criticism of unjust actions and their angry emotions.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 59. samplenew3_00059383｜gain｜ΔF1 +0.027778

gold：attention, concern, doubt, skepticism

query字幕：Are you absolutely sure?

源标注描述：In the text, the caption reads: "Are you completely sure?" This sentence might be a man's inquiry or assessment about a task or decision. Based on the man's serious facial expression and body language in the video clues, as well as the uncertainty and fluctuation of his voice tone and volume in the audio clues, we can infer that this sentence may carry a note of skepticism or concern. The man might be asking if the other person has enough assurance or confidence to accomplish a certain task or make a decision. Therefore, this sentence may imply the man's attention to the importance and risks of the task or decision, as well as his doubt over whether the other person is capable.

off原始输出：The character's emotional state is skepticism, challenge, urgency, tension, anxiety.

retrieval原始输出：The character's emotional state is skepticism, challenge, uncertainty, anxiety.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, challenge, skepticism, tension, urgency|0.222222|1|4|3|
|retrieval|anxiety, challenge, skepticism, uncertainty|0.250000|1|3|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.222222变为0.250000，差值+0.027778。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：uncertainty。
- 相对off移除未精确匹配gold的标签：tension, urgency。

gate：0.120007157；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [{"prediction_label": "anxiety", "unmatched_gold_label": "concern"}], "retrieval": [{"prediction_label": "anxiety", "unmatched_gold_label": "concern"}]}

实际5近邻证据：

### 近邻1：samplenew3_00039997

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, nervousness
- 与query gold精确词面重合：∅
- 字幕：Introducing everyone to you
- 描述：In the text, the subtitle content "Introducing everyone" suggests that based on the relaxed posture and smiling facial expression of the man in the video, as well as the social gathering and the man's formal attire in the environment, we can infer that this sentence may be spoken by the man in the role of a host or someone responsible for introducing others, displaying a confident and satisfied emotional state. This aligns with the positive emotions displayed by the man in the video clues. At the same time, based on the slight tremor in the speaker's voice and the slightly monotonous tone in the audio clues, we can speculate that this sentence may carry a certain level of nervousness and emotional detachment. Therefore, this sentence may be spoken by the man while introducing others, while feeling a certain level of nervousness and confidence, displaying a complex emotional state.

### 近邻2：samplenew3_00030334

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, pressure, seriousness
- 与query gold精确词面重合：concern
- 字幕：Difficulty in employment for the affluent labor force.
- 描述：In the text, the caption content: "Struggling with ample labor employment" might be a description or summary of what a man is thinking about or dealing with. Based on the man's's deep thought and focused expression in the video clues, as well as the tense and anxious voice characteristics described in the audio cues, we can infer that this phrase could be the man's's evaluation or summary of a particular problem or situation. The seriousness and focused emotional state of the man indicates that he is pondering an important issue, while the tense and anxious voice characteristics described in the audio clues suggest that he is concerned and under pressure about the issue of employment difficulties for ample labor. Therefore, this phrase could be the man's's description or evaluation of the issue of employment difficulties for ample labor.

### 近邻3：samplenew3_00015776

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：humor, irony
- 与query gold精确词面重合：∅
- 字幕：Do you think we are all blind?
- 描述：In the text, the caption reads: "Thought we were all blind, huh?" This phrase could be a response from a man to a particular of situation or dialogue. Based on the comedic facial expressions and body language displayed by the man in the video clues, as well as the audio clues of his voice shaking and his tone wavering, we can infer that this statement might carry a humorous or ironic tone. The man may be responding to a situation or dialogue in a humorous way; however, due to the lack of more contextual information, it's unclear about the exact emotional state.

### 近邻4：samplenew3_00058490

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：appreciation, confidence, seriousness, thoughtful
- 与query gold精确词面重合：∅
- 字幕：You are a lovely girl with affection.
- 描述：In the text, the subtitle reads: "You are a thoughtful and kind girl." Based on the serious and thoughtful facial expression of the man in the video, as well as the confidence and focus conveyed through his body language, it can be inferred that he is discussing an important or serious topic. This subtitle may be a compliment or praise from the man to the woman. It is difficult to determine the man's emotional state based on the description of the individual's speech in the audio, which suggests a relatively low tone indicating sadness or depression, as well as a relatively high volume indicating anxiety or agitation. However, based on the man's confident and focused demeanor in the video, it can be speculated that he is saying this sentence in a serious and appreciative manner, aligning with his overall serious and focused state.

### 近邻5：samplenew3_00005883

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：important, urgency
- 与query gold精确词面重合：∅
- 字幕：You just go ahead and prepare for today, I will talk to him later to confirm the time.
- 描述：In the text, the caption reads: "You just follow through with what we've planned for today and I'll get back to you to finalize the timing later." This sentence might be an instruction or advice from one person to another. Given the urgency and importance conveyed by the speaker's's tone as per the audio cues, and the individual's focused and serious demeanor indicated in the video clues, we can infer that this statement might carry a sense of urgency and importance. Therefore, the sentence likely emphasizes that the other person should prepare according to today's arrangements and later confirm the time with him. This suggests that the speaker attaches great importance to the topic of discussion and expects the other party to make timely preparations.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 60. samplenew3_00046607｜gain｜ΔF1 +0.033333

gold：anxiety, confusion, contemplation, fear, remorseful, seriousness, stress

query字幕：Why did you become a bandit when you first went up the mountain?

源标注描述：In the text, caption content: "Why would he have joined the bandits back then?" Based on the man's's solemn expression and relaxed body language in the video clues, along with the dark atmosphere of the setting, we can infer that he might be in a state of deep contemplation or serious thought. This caption suggests that he is reflectinging on past decisions or actions, feeling confused or regretful about his choices. This alignss with the man's's solemn demeanor and focused gaze in the video. Considering the audio clues describing a trembling voice, fluctuating pitch, and urgent, desperate speaking manner, we can deduce that he may be experiencing intense feelings of fear, anxiety, and stress. Therefore, this caption content might be what he was saying to himself as he reflects and questions his own decisions, expressing his confusion and remorse over past behaviors.

off原始输出：The character's emotional state is contemplative, introspective, sorrowful, anger, frustration.

retrieval原始输出：The character's emotional state is contemplative, introspective, sorrowful.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, contemplation, frustration, introspective, sorrowful|0.166667|1|4|6|
|retrieval|contemplation, introspective, sorrowful|0.200000|1|2|6|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.166667变为0.200000，差值+0.033333。
- TP变化+0，FP变化-2，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：anger, frustration。

gate：0.119992085；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00048324

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：challenge, criticism, questioning
- 与query gold精确词面重合：∅
- 字幕：Why can Zhang Mazi solve your goods but not enter your house?
- 描述：In the text, the subtitle reads: "Why can Zhang Mazi solve your problems but not enter your home?" This sentence may be a question or a rhetorical question posed by the speaker. Based on the description of the speaker's fast-paced, energetic speaking style in the audio clues, as well as the sense of urgency and hint of impatience in the tone, we can infer that this sentence may carry a tone of challenge or questioning. The speaker may be attempting to persuade the listener of something important and questioning the listener's actions or decisions. Therefore, this sentence may carry a tone of criticism or challenge, aligning with the emotional state of the speaker described in the audio clues.

### 近邻2：samplenew3_00078695

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, firm, hope, optimism, positive
- 与query gold精确词面重合：∅
- 字幕：No matter how you fly, as long as he is willing to treat me sincerely, it's fine.
- 描述：In the text, caption content: "But no matter how he flies, as long as he pays attention to me, that's enough." This sentence might be a man expressing his expectations or demands for someone. Given the speaker's's tone described in the audio cues as firm and confident, along with the use of words and phrases conveying determination and energy, we can infer that this sentence might be a man emphasizing the importance and expectations he has for someone else. He hopes that person will genuinely care about him. Therefore, this sentence may carry a sense of firmness and anticipation, aligning with the overall positive and optimistic emotional state portrayed by the man.

### 近邻3：samplenew3_00049862

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, tension
- 与query gold精确词面重合：anxiety, fear
- 字幕：In my impression, it is on the list of bandits.
- 描述：In the text, the subtitle reads: "In my mind, the kidnapper list." Based on the man's's serious facial expression and body language in the video clues, as well as his professional appearance dressed in a suit with a tie, it can be inferred that he might be contemplating or thinking about work-related matters. The audio clues describe his voice as shaky with a rapid pace, indicating he may be experiencing feelings of fear or anxiety, and is attempting to convey a sense of urgency or importance. Therefore, the content of the subtitle could refer to him discussing or contemplating matters related to the kidnapper list, which further supports the assumption that he might be in a tense or anxious state.

### 近邻4：samplenew3_00094352

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration, tension
- 与query gold精确词面重合：∅
- 字幕：How dare you intrude into the prince's mansion and attempt to assassinate him.
- 描述：In the text, the caption reads: "Dare to intrude into this imperial prince's residence and attempt murder." This sentence might be spoken by an Asian man. Based on the vocal cues described, such as the aggressive and accusatory tone of voice, with a high pitch and uneven rhythm, we can infer that the statement conveys a sense of anger, tension, and frustration. The speaker seems to be enraged and aggrieved because someone has trespassed in his residence attempting to assassinate him. This emotional state contrasts with the relaxed posture and closed-eyed expression described in the video clues, suggesting he may feel anger and tension when recalling or narrating the event.

### 近邻5：samplenew3_00066361

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：cautious, concern, warning
- 与query gold精确词面重合：∅
- 字幕：That is because I am afraid that others will take advantage of you.
- 描述：In the text, the caption reads: "That's because they fear others will ask you to do something on their behalf." This sentence could be an evaluation or advice from the speaker to someone. Considering the audio hints of a slight tremble in the speaker's's voice and a deliberate slow tone, along with the video clues showing an older man with a serious and firm expression while a younger man displays a relaxed and composed demeanor, we can infer that the statement might carry a tone of concern or warning. Therefore, this sentence may be reminding someone to be cautious about others' requests, to avoid being exploited or forced to do something for them. This alignss with the inference that the older man might be in a position of authority or importance.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 61. samplenew3_00040565｜gain｜ΔF1 +0.035714

gold：comfortable, confidence, encouragement, positive

query字幕：That's really okay, that's good.

源标注描述：In the text, caption content: "That's good, then it's fine." This sentence might be the speaker's response to some situation or issue. Considering the emotional state described in the audio cues, where the speaker appears anxious, tense, and emotionally detached, as well as the video cues showing a woman with a friendly smile and self-assured demeanor, we can infer that this phrase may be an expression of comfort or encouragement. The speaker might be responding to someone's concern or question, attempting to convey an "it's okay" message to alleviate their tension. This response alignss with the overall positive emotion and confidence displayed by the female character.

off原始输出：The character's emotional state is comfort, encouragement, sadness, contemplation.

retrieval原始输出：The character's emotional state is comfort, encouragement, support.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|comfort, contemplation, encouragement, sadness|0.250000|1|3|3|
|retrieval|comfort, encouragement, support|0.285714|1|2|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.250000变为0.285714，差值+0.035714。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：support。
- 相对off移除未精确匹配gold的标签：contemplation, sadness。

gate：0.120002501；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00039188

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, commitment, contemplation, fear, inner conflict, loyalty, reflection, uncertainty
- 与query gold精确词面重合：∅
- 字幕：Why should I leave him? He is pure and has never betrayed me emotionally. I won't leave him.
- 描述：In the text, the subtitle reads, "Why should I leave him when he has been pure and never betrayed me emotionally? I won't leave him." Based on the emotional mixture described in the audio clues, including fear, anxiety, and uncertainty, as well as the facial expression and posture of the woman in the video indicating a state of contemplation or reflection, it can be inferred that this sentence may be the woman contemplating why she should leave someone and expressing her sense of loyalty and commitment to this person. She mentions not leaving this person, indicating that she may feel trapped or bound, while also expressing fear and anxiety about the consequences of leaving. Therefore, this sentence reflects the woman's inner conflict and emotional state.

### 近邻2：samplenew3_00015313

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction
- 与query gold精确词面重合：∅
- 字幕：The translation for the input is: The power of God does not mean that he has committed a crime now. If he commits a crime, he should be handed over to the public security organs. Why do you, the security department, arrest people and even hold trials? This is illegal.
- 描述：In the text, caption content: "God's isn't not your meaning that he has already committed a crime. If he did, he should be handed over to the public security authorities. Why are you, the department for security, arresting and trying people? This is illegal." This sentence indicates that the speaker is angry and dissatisfied with someone's actions or accusations. Based on the pitch and agitated tone described in the audio cues, as well as the strong language and questions used in the caption content, we can infer that the speaker is expressing strong dissatisfaction and anger towards someone's behavior. This emotion might correspond with the woman's anxiety and contemplative state described in the video clues, suggesting a tense and confrontational situation.

### 近邻3：samplenew3_00080609

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, discomfort, emotional distress, fear, insecurity, shyness, tension
- 与query gold精确词面重合：∅
- 字幕：I feel embarrassed to go out every day now.
- 描述：In the text, the caption reads: "I'm not comfortable going out every day now." This sentence might be describing a man's's emotional state. Based on the audio cues indicating of his high anxiety and tension, as well as the video clues showing his serious, aloof, and thoughtful expressions and body language, we can infer that this sentence might be a description of his social anxiety or emotional distress. He might feel insecure, shy, or fearful of external judgment, hence feeling uncomfortable to go out. This alignss with the overall negative emotions he displays.

### 近邻4：samplenew3_00042537

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：astonishment, shocked, tension, unease
- 与query gold精确词面重合：∅
- 字幕：Hesitate for a moment, and half of the building is gone.
- 描述：In the text, caption content: "Hold on for a bit, half a floor could be gone." This sentence might be a response from a woman who has just experienced something astonishing or shocking. Given the visual clues of the woman's surprised or startled facial expression and audio cues such as her voice trembling and speaking quickly reflectinging an emotional state, we can infer that this sentence might be delivered in a tense or panicked tone. Therefore, this sentence might be an emotional outburst from a woman who has just experienced something astonishing or shocking, conveying her tension and unease.

### 近邻5：samplenew3_00055511

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, optimism, positive, tension
- 与query gold精确词面重合：positive
- 字幕：He can only take a risk and try it seems that you are lucky.
- 描述：In the text, caption reads: "He could only take a chance, looks like you're in for a lucky break." Based on the video hints such as the serious facial expression and body language of the woman, along with audio cues like the high-pitched voice, rapid speech, and sense of urgency from an individual's tone, we can infer that this sentence might be the woman's evaluation or response to someone. The woman's serious demeanor and tone of voice that suggests urgency imply she might be concerned or tense about someone's adventurous behavior or decision. However, given the caption's mention of "you're in for a lucky break", it can be speculated that the woman holds an optimistic or positive attitude towards this adventurous act, believing that the person may have good luck. Therefore, this sentence might be the woman's evaluation or response between concern and optimism.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 62. samplenew3_00003061｜gain｜ΔF1 +0.036364

gold：confusion, disappointment, dissatisfaction, questioning, sadness, unhappy

query字幕：There is nothing in his place, why is there a cup?

源标注描述：In the text, the caption reads: "There's nothing much there, just cups and whatever." This sentence could be a comment or a doubt by a woman towards another person or an item in her environment. Given the audio clues where the woman uses a high-pitched, monotonous tone, and the video clues showing the woman expressing sadness and confusion, we can infer that the sentence might carry a tone of dissatisfaction or questioning. The woman might be feeling disappointed or unhappy with another person or an item in her environment, hence making such a comment.

off原始输出：The character's emotional state is discontent, questioning, surprise, sadness, anger.

retrieval原始输出：The character's emotional state is discontent, questioning, surprise, sadness.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, discontent, questioning, sadness, surprise|0.363636|2|3|4|
|retrieval|discontent, questioning, sadness, surprise|0.400000|2|2|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.363636变为0.400000，差值+0.036364。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：anger。

gate：0.120010443；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [{"prediction_label": "discontent", "unmatched_gold_label": "dissatisfaction"}], "retrieval": [{"prediction_label": "discontent", "unmatched_gold_label": "dissatisfaction"}]}

实际5近邻证据：

### 近邻1：samplenew3_00102668

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, concern, curiosity, heightened alertness, soothing
- 与query gold精确词面重合：∅
- 字幕：You go back and rest well.
- 描述：In the text, the caption reads: "Go back and get some good rest." This phrase could be a suggestion or expression of concern from a woman to someone else. Given that the audio clue describes the woman speaking in a calm and soothing tone, her voice suggests she is attempting to comfort the listener, with a relatively low pitch, aiming to create a sense of tranquility. Simultaneously, based on the visual clues provided by the woman's facial expressions and body language, it can be inferred that she is in a state of heightened alertness and curiosity, possibly awaiting a significant event or decision. Therefore, this sentence might be a woman's concern and advice for someone under stress or anxiety, hoping that they person could return to get some well-deserved rest and relaxation.

### 近邻2：samplenew3_00071154

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：frustration, humor, irritation, self-deprecation
- 与query gold精确词面重合：∅
- 字幕：When are we leaving, immortal? Are you trying to chase me away?
- 描述：In the text, the caption reads: "When will the immortal depart? This is trying to get me to leave." This phrase might be a form of self-mockery or humor from the speaker. Given the individual's possible feelings of frustration or irritation as indicated by the audio clues, and the woman's mixed expression of surprise and disbelief in the video hints, we can infer that this statement might carry a tone of self-deprecation or humor. The woman may be using humor as a way to cope with some difficulties or challenges she is facing.

### 近邻3：samplenew3_00051064

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：conflicted, confusion, frustration, irritation, overwhelm, shocked
- 与query gold精确词面重合：confusion
- 字幕：Why does it sound like saying if I want to have a child, it is impossible to have company shares? Who can choose between these two things?
- 描述：In the text, caption content: "Sounds like I can't have kids and company shares at the same time, who am I supposed to choose? How do I pick between the two?" Given the personal experiences of frustration and irritation described in the audio cues, along with the urgency and desperation in the speaker's's tone, we can infer that this sentence might be expressing an individual's confusion and conflict. The person might be facing a choice between having children or acquiring company shares, feeling unable to have both. This confusion and conflict aligns with the video hints of the woman's surprise and shock facial expression, suggesting that she may be taken aback or overwhelmed by this decision. Therefore, this sentence could be a response or question from the woman regarding the individual's's choices and dilemmas.

### 近邻4：samplenew3_00091924

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：frustration, sadness, vulnerability
- 与query gold精确词面重合：sadness
- 字幕：I should say that I did have the idea when you left that year, I wanted to find you. At that time, I was too young and couldn't bear to see you all in such pain.
- 描述：In the text, caption content: "I must admit that I did have that thought, when you left that year I considered going to find you, but I was too young then, seeing you in so much pain, it was just unbearable." This sentence might be an expression of emotion and experience in a conversation. Given the audio cues described by the individual's's fast pace of speaking, stern tone, and sniffs and snorting sounds, we can infer that this statement may carry an emotional tone of sadness, frustration, and vulnerability. The person describes their thoughts and longing for those who left them, as well as their own helplessness at seeing them suffer, suggesting they they may have experienced a range of emotions including sadness and frustration.

### 近邻5：samplenew3_00092543

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：burdened, complaint, dissatisfaction, down
- 与query gold精确词面重合：dissatisfaction
- 字幕：Not because I love to eat
- 描述：In the text, the caption reads: "Not because I love eating," this sentence could be the woman's response to a question or an explanation for her actions. Considering the video hints of the woman's serious expression and body language, along with the audio clue of her high-pitched speaking tone, we can infer that the statement might carry a sense of dissatisfaction or complaint. The woman might be expressing that she isn't doing something not because she likes eating, but there is some other reason. This emotion could align with the overall feeling of the woman being down or heavily burdened.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 63. samplenew3_00064542｜gain｜ΔF1 +0.044444

gold：criticism, extremely, negative

query字幕：This person is extreme.

源标注描述：In the text, the caption reads: "This person is extremely so." This phrase could be an evaluation or description of an elderly man in a video. Given the clues from the video such as the serious expression and focused demeanor of the old man, and the audio hints like a fast-paced individual speech with an inflection suggesting negative emotion, we can infer that this sentence might be describing the elderly person as exhibiting extreme behavior or going overboard in a certain aspect. It could be criticizing their excessive focus or deep contemplation, or even hinting at inappropriate or irrational behavior or attitude. Thus, this sentence might carry a negative evaluation or a critical tone.

off原始输出：The character's emotional state is extreme, negative.

retrieval原始输出：The character's emotional state is critical, negative, extreme, anxiety, tension, stress.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|extreme, negative|0.400000|1|1|2|
|retrieval|anxiety, criticism, extreme, negative, stress, tension|0.444444|2|4|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.400000变为0.444444，差值+0.044444。
- TP变化+1，FP变化+3，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：anxiety, stress, tension。
- 相对off新增命中的gold标签：criticism。

gate：0.119918667；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [{"prediction_label": "extreme", "unmatched_gold_label": "extremely"}], "retrieval": [{"prediction_label": "extreme", "unmatched_gold_label": "extremely"}]}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00092994

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：evaluated negatively, neutral
- 与query gold精确词面重合：∅
- 字幕：Jin Fu is self-deceiving.
- 描述：In the text, the subtitle content says, "Jin Fu, he is self-deceiving." This sentence may be a comment or reaction to the Asian man. Based on the description of the Asian man's calm and composed facial expression in the video clues, as well as the peaceful environment around him, we can infer that this sentence may carry a negative evaluation or criticism. This sentence may imply that the Asian man is to some extent deceiving himself or being unreal. However, since the audio clues do not provide specific sound information, we cannot further determine the emotional state of the Asian man.

### 近邻2：samplenew3_00113103

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, anxiety, excitement
- 与query gold精确词面重合：∅
- 字幕：The Lord will definitely ask about the strategy of the commander-in-chief tomorrow.
- 描述：In the text, the subtitle reads: "Tomorrow, the lord will surely ask the general for his strategy in battle." This sentence may be the old man's prediction or expectation regarding a decision or plan. Based on the calm and composed demeanor of the old man in the video clues, as well as the mixed emotions of excitement and anxiety in the audio clues, we can infer that this sentence may carry a sense of anticipation and nervousness. The old man may feel excited about the decision or plan for tomorrow, but at the same time, he may also feel anxious about its outcome. This sentence may be his expression of anticipation and concern for the upcoming decision or plan.

### 近邻3：samplenew3_00105108

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：humor, irony, joy, satisfaction
- 与query gold精确词面重合：∅
- 字幕：I really overestimated myself. Last autumn, I was given a prince who had just been released from prison.
- 描述：In the text, caption content: "He really underestimated me, giving me a prince newly released from prison in the Autumn semester." This sentence might be an evaluation or response of the speaker to someone or something. Given the audio clues where the speaker's has a clear, confident voice, a firm and authoritative tone, and video clues of the elderly man smiling, smiling, and relaxing, we can infer that the sentence may carry a humorous or ironic tone. Therefore, this sentence might be a way of making fun or mocking, consistent with the overall joyful and satisfied mood the elderly man exhibits.

### 近邻4：samplenew3_00071022

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration
- 与query gold精确词面重合：∅
- 字幕：This idea is beyond your capability.
- 描述：In the text, the subtitle reads: "Your father cannot do this idea." This sentence may be a response or comment from the Asian man in the video to the woman. Based on the described high pitch, urgent tone, and the anger or frustration conveyed in the tone of the speaker in the audio clues, as well as the intense conversation or discussion depicted by the Asian man in the video, we can infer that this sentence may carry an angry or frustrated tone. This sentence may be a denial or rebuttal of the idea proposed by the woman, expressing his dissatisfaction or disagreement. Therefore, this sentence may carry a negative emotion, aligning with the intense conversation and the angry or frustrated emotions displayed by the Asian man overall.

### 近邻5：samplenew3_00037952

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, frustration
- 与query gold精确词面重合：∅
- 字幕：The military unexpectedly has more than three thousand non-combat casualties every day.
- 描述：In the text, caption content: "The troops actually have over three thousand non-battle casualties daily." This sentence might be the speaker's's reaction to the situation or decision of a certain troop, expressing anger and frustration. Given the audio clues where the speaker's is tense, agitated, with a high-pitched tone, and video clues that describe an elderly man with a serious face, wearinging large glasses, sitting in a dim room, we can infer that this statement could be the speaker's's negative evaluation or response to the troop's non-battle casualty figures. The person may feel angry and frustrated about the number of non-battle casualties, considering it a serious issue leading to their anxiety and tension. This alignss with the video clue that describes the elderly man as focused, thoughtful, even sternly in his emotion state.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 64. samplenew3_00030524｜gain｜ΔF1 +0.044444

gold：anxiety, concern, excitement, full of energy, happiness, nervousness, tension

query字幕：There is something I don't know whether I should say or not.

源标注描述：In the text, considering the man's's facial expressions that blend smiles with worry as described in the video cues, and his body language indicating of full engagement in conversation while attempting to balance his emotions, it can be inferred that he might be experiencing both positive and negative emotions simultaneously, such as happiness from establishing a relationship with the other party, coupled with concern about the topic being discussed. Based on the audio cues, the slight tremor in the individual's's voice and speaking speed faster than average, suggests they might feel anxious or tense, yet also excited or full of energy. Therefore, he might be feeling nervous about an upcoming event or performance, while also being excited about the opportunity to showcase his skills. Given these inferences, the phrase "There's something I don't know if I should say or not" in the subtitle could represent the man's's internal hesitation and worry as he contemplates whether to bring up a certain topic or express a particular viewpoint.

off原始输出：The character's emotional state is excited, nervous, positive.

retrieval原始输出：The character's emotional state is nervous, excited.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|excitement, nervousness, positive|0.400000|2|1|5|
|retrieval|excitement, nervousness|0.444444|2|0|5|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.400000变为0.444444，差值+0.044444。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：positive。

gate：0.120040417；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00014273

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：humor, relaxation, self-doubt, uncertainty
- 与query gold精确词面重合：∅
- 字幕：I can't think of any improvements for the time being, maybe it's because my thinking is not broad enough.
- 描述：In the text, caption content: "For the moment, I can't think of anything to improve, perhaps my thinking is not broad enough." This sentence might be spoken by a man in conversation with another person. Based on the speaker's's shaky voice and hesitant tone described in the audio clues, as well as the man's smile and cheerful mood depicted in the video clues, we can infer that this statement might carry a tone of self-doubt or self-mockery. The man may be expressing uncertainty about a particular problem or his own capabilities, but also showing a relaxed and humorous attitude. This alignss with the overall positive emotion the man exhibits in the video.

### 近邻2：samplenew3_00037315

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：humor, relaxation, satisfaction
- 与query gold精确词面重合：∅
- 字幕：The hot spring vacation at the booth collapsed, and I felt bored, so I just came over and killed you.
- 描述：In the text, the subtitle content "I think it's boring to just relax at the hot spring resort, so I came straight here" aligns with the man's smile and relaxed posture in the video, as well as the atmosphere of the public space in the background. It can be inferred that the man is enjoying his time and feels comfortable and satisfied. The phrase "I think it's boring" in the subtitle may be a sarcastic or humorous expression about the way of vacationing, while "I came straight here" may be an expression of pride or satisfaction about his decision and action. Therefore, it can be inferred that the man expresses a relaxed, humorous, and satisfied emotional state in the subtitle content.

### 近邻3：samplenew3_00019860

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, nervousness
- 与query gold精确词面重合：anxiety, nervousness
- 字幕：What will the store become after the representative of the Eighth Route Army leaves?
- 描述：In the text, the subtitle says, "What will happen to the store after the representative of the Eighth Route Army leaves?" This sentence may be one man's speculation or concern about the other man. Based on the audio clues describing a sense of urgency and tension in the individual's voice, as well as the individual speaking with a fast pace and forceful tone, it suggests that they may be feeling anxious or nervous. Additionally, based on the facial expressions and body movements of the two men in the video, they seem to be enjoying the conversation and possibly sharing a lighthearted moment. Therefore, this sentence may express one man's concern or curiosity about the future changes in the store, but it does not affect their current relaxed and pleasant interaction.

### 近邻4：samplenew3_00047267

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：unease, worry
- 与query gold精确词面重合：∅
- 字幕：My point is, if you find out that I am pretending to be sick to fool you, will you not understand me?
- 描述：In the text, the subtitle reads: "What I mean is, if you find out that I was pretending to be sick to fool you, would you not understand me?" This sentence is likely spoken by the man in the conversation. Based on the audio clues describing the individual's high pitch, anxiety or irritability, as well as the video clue of the man's smiling and relaxed expression, we can infer that this sentence may carry a tone of worry or unease. The man may be expressing his concern about being misunderstood or not being understood. Therefore, this sentence may reflect the man's negative emotions and worries in the conversation.

### 近邻5：samplenew3_00115213

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：joking, positive, relaxation, teasing
- 与query gold精确词面重合：∅
- 字幕：There won't be any seats if your class arrives a little late.
- 描述：In the text, the caption reads: "If you arrive a bit late, there won't be seats available." This sentence might be something a man could say to a woman. Given the audio cues described with a person's's voice trembling, speaking quickly, and video clues showing the man exhibiting positive and relaxed emotions, we can infer that this sentence might be delivered in a tense yet excited tone. Therefore, it seems plausible that the man is joking or teasing the woman, which alignss well with the overall positive demeanor he presents.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 65. samplenew3_00062410｜gain｜ΔF1 +0.047619

gold：comfortable, confidence, in control, relaxation

query字幕：I can't explain it to you now, wait a moment and you will understand.

源标注描述：In the text, the caption reads: "It's hard to explain, just wait, you'll understand in a bit." This phrase could be a man's response or promise to someone else. Based on the audio cues describing the individual speaking with clarity and brevity, it suggests they might feel confident and in control of their emotions. Furthermore, the audio cues suggest that the individual speaks at a moderate pace, indicating they may feel comfortable and relaxed. Therefore, this sentence could be the man expressing confidence and relaxation when telling someone that it's hard to explain, and they will understand soon. This manner of expression alignss with the man's's overall depiction of calmness and organization.

off原始输出：The character's emotional state is anticipation, excitement, confidence.

retrieval原始输出：The character's emotional state is calm, confident.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anticipation, confidence, excitement|0.285714|1|2|3|
|retrieval|calm, confidence|0.333333|1|1|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.285714变为0.333333，差值+0.047619。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：calm。
- 相对off移除未精确匹配gold的标签：anticipation, excitement。

gate：0.120023564；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "calm", "unmatched_gold_label": "relaxation"}]}

实际5近邻证据：

### 近邻1：samplenew3_00006225

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, introspective, positive mood, respect
- 与query gold精确词面重合：∅
- 字幕：Master, what you taught us is correct.
- 描述：In the text, the caption reads: "Master's teachings are indeed applicable." This phrase might be this person's self-assessment or response to someone else. Given the description of the individual speaking in a high-pitched and energetic tone, along with their facial expressions and posture in the video suggesting introspection or contemplation, we can infer that the statement may carry a tone of respect or admiration. Therefore, the sentence could be a confirmation and acknowledgment of the master's's teachings or guidance, aligning with the individual's overall positive mood and introspective nature.

### 近邻2：samplenew3_00104016

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：amusement, interested, joking, positive
- 与query gold精确词面重合：∅
- 字幕：Then I can move out.
- 描述：In the text, the caption reads: "Well, I might just move then." This sentence could be the man's's response to a woman showing him a piece of fabric. Based on the audio cues described with a high-pitched, clear tone and a quick pace, as well as the video clues indicating of the man's's curiosity and interest in the fabric, we can infer that this sentence may carry a humorous or teasing tone. The man might be joking about how interested he is in the fabric that the woman has shown him, to the extent that he would be willing to move for it. This alignss with the overall positive mood the man displays.

### 近邻3：samplenew3_00109729

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, contentment, contrast, happiness, inner peace, metaphor
- 与query gold精确词面重合：∅
- 字幕：Doing business is like fighting a war.
- 描述：In the text, the subtitle content "Like doing business and going to war" is possibly the man describing a certain experience or metaphor. Based on the calm and contented emotions displayed by the man in the video clues, as well as the intense emotions that the individual may be experiencing in the audio clues, we can infer that this sentence may be describing a contrast or metaphor, expressing the happiness and inner peace the man feels in the tranquil and balanced environment compared to the intense emotions he may be experiencing.

### 近邻4：samplenew3_00083277

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：celebratory, joy
- 与query gold精确词面重合：∅
- 字幕：I've finally understood what the spirit of the team means.
- 描述：In the text, caption content: "I finally get what team spirit means." This sentence might be a man expressing his understanding of the concept of team spirit. Based on the speaker's's confusion and uncertainty described in the audio clues, as well as the humorous facial expressions and playful body language shown in the video clue, we can infer that this statement might be delivered with a casual or humorous tone. The man may have been struggling to understand the concept of team spirit, experiencing a period of confusion and frustration, but he eventually comprehended it. Therefore, this sentence could be a celebratory or joyful expression, consistent with the overall positive mood displayed by the man.

### 近邻5：samplenew3_00057721

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, unease, worry
- 与query gold精确词面重合：∅
- 字幕：Linzhou is probably occupied.
- 描述：In the text, the caption reads: "Linchuan is probably fallen." This sentence might be a youth's evaluation or speculation about a particular place or situation. Given that the individual described in the audio clues appears to be anxious or tense, and with a slightly faster pace of speech indicating of energy, it can be inferred that the tone of this statement may carry a sense of concern or unease. Therefore, this sentence could be a youth's speculation or worry about a place falling, which alignss with his overall serious and thoughtful demeanor.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 66. samplenew3_00000254｜gain｜ΔF1 +0.047619

gold：anxiety, tension

query字幕：Is strangling him from the front or the back?

源标注描述：In the text, the caption reads: "It's from the front or the back to strangle him." This sentence might be a man contemplating or discussing an issue. Given the man's's serious expression and posture in the video clues, as well as the speaker's's shaky voice and lack of emotional tone in the audio clues, we can infer that this sentence might be delivered with a sense of tension or anxiety. Therefore, this sentence might be part of a discussion on a serious or tense topic, possibly involving violent or dangerous actions. However, without further context, it is unclear what his exact emotional state is.

off原始输出：The character's emotional state is serious, contemplative, focused, tense, stressed.

retrieval原始输出：The character's emotional state is serious, contemplative, tense, urgent.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|contemplation, focused, seriousness, stress, tension|0.285714|1|4|1|
|retrieval|contemplation, seriousness, tension, urgency|0.333333|1|3|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.285714变为0.333333，差值+0.047619。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：urgency。
- 相对off移除未精确匹配gold的标签：focused, stress。

gate：0.119926222；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00041849

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：I don't have this drawing
- 描述：In the text, given the information provided, it is not possible to infer the emotional state of the characters from the subtitle content. The subtitle content merely describes the scenes in the video and the external manifestations of the characters, without providing direct clues about their emotional states. To infer the emotional state of the characters, it is necessary to analyze video cues such as expressions and movements, as well as audio cues such as voice characteristics and tone."

### 近邻2：samplenew3_00089049

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, respect
- 与query gold精确词面重合：∅
- 字幕：Director Hou, you are an experienced detective.
- 描述：In the text, the caption reads: "Director Liu, you're a seasoned investigator." This phrase might be a compliment or praise from a woman to a man. Given the woman's expression of surprise or shock in the video clues, and the man's intense gaze at her, we can infer that this statement could be an acknowledgment and appreciation of his professional experience or abilities. Therefore, this sentence might carry a tone of admiration or respect, fitting with the tense and focused emotions portrayed in the video.

### 近邻3：samplenew3_00086246

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：curiosity, focus, misunderstanding, skepticism
- 与query gold精确词面重合：∅
- 字幕：What strange symbol written by Jingqian is the secret symbol that Lord Qin recognizes?
- 描述：In the text, the caption reads: "What strange runes did Jing Qian write that Old Qin, the Ruler of Secrets, recognizes." This sentence might be what a seated man says to a standing man. Given the speaker's's description in the audio clues being in a highly aroused and negative emotional state, as well as the seated man displaying a curious and focused expression in the video clues, we can infer that this sentence might carry a tone of doubt or challenge. Therefore, this sentence could be the seated man expressing skepticism or misunderstanding about the content on the paper shown by the standing man, which alignss with the seated man's overall curious and focused emotion.

### 近邻4：samplenew3_00079485

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, gratitude, irony, sarcasm
- 与query gold精确词面重合：∅
- 字幕：Thank you, old man.
- 描述：In the text, caption reads: "Thank you, sir." This sentence could be a man expressing gratitude or admiration towards someone. Based on the audio cues, the individual's voice tone is high with slight tremble and spoken at a fast pace, indicating they might be experiencing intense negative emotions such as fear and anxiety, possibly feeling a sense of urgency or panic. However, the way the expression is made - a thank-you and an admiring phrase - contrasts with the negative emotions conveyed by the audio clues. Therefore, we can infer that this statement might be a form of irony or sarcasm, perhaps humorously expressing gratitude or admiration for someone in contrast to the negative emotions indicated by the audio cues.

### 近邻5：samplenew3_00011706

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, doubt, speculation
- 与query gold精确词面重合：∅
- 字幕：Mo Fēngzi, could it be that Brother Mo Fēngzi was killed by that poisonous insect?
- 描述：In the text, the subtitle content: "Could it be that Brother Yuan was killed by that poisonous insect?" This sentence may be the man's speculation or conjecture about the other people around him. Based on the audio clues describing the individual expressing a range of emotions, including happiness, sadness, anger, and fear, as well as the serious expression and contemplative state of the man in the video, we can infer that this sentence may carry a tone of doubt or concern. The man may be pondering on a certain issue or event and making some guesses or speculations about the surrounding context and the presence of other people. Therefore, this sentence may be the man's speculation or conjecture about an event or situation, aligning with the overall serious and contemplative state displayed by the man.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 67. samplenew3_00019107｜gain｜ΔF1 +0.047619

gold：caring, hope, reluctant, sadness

query字幕：Sister, you have to go on your own.

源标注描述：In the text, the caption reads: "The sister is about to walk on her own." This phrase might be a farewell statement made by a woman to an infant. Considering the video hints such as the woman's smiling facial expression while holding the infant and her engaging body language, along with the audio clues indicating that the woman may have experienced negative emotions, we can infer that this sentence might be spoken in a warm and caring tone. The woman might feel reluctant and sad, but also hopes for the infant's independent growth. Therefore, this sentence could be a way of expressing a mixture of positive and negative feelings during a farewell.

off原始输出：The character's emotional state is sadness, helplessness, melancholy.

retrieval原始输出：The character's emotional state is sadness, helplessness.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|helplessness, melancholy, sadness|0.285714|1|2|3|
|retrieval|helplessness, sadness|0.333333|1|1|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.285714变为0.333333，差值+0.047619。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：melancholy。

gate：0.119984560；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00075193

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：despair, disappointment
- 与query gold精确词面重合：∅
- 字幕：There are words from me expressing my love for you.
- 描述：In the text, caption content: "There's a line I say that I like you." This sentence might be a woman expressing her feelings to someone. Based on clues from the video such as the woman's crying, heavy expression, and the shaking and trembling in her personal voice from the audio, we can infer that this sentence may carry a sense of sadness or despair. The woman might be bravely expressing her liking for someone at this emotional moment, but possibly without receiving a response from the other person, or a negative one, which intensifies her negative emotions. Therefore, this sentence could be the woman expressing her feelings with a tone of disappointment or despair.

### 近邻2：samplenew3_00061231

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：positive, satisfaction, stable
- 与query gold精确词面重合：∅
- 字幕：
- 描述：In the text, the caption reads: "It's more like in these days of Bo Yuan." This sentence might be spoken by a woman in the video. Based on the video clues describing her calm expression, relaxed body language, and the surrounding environment suggesting she is in a social setting interacting with others, we can infer that this phrase could be her evaluation or reminiscence about someone or somewhere. According to the audio clues described as "as an expert in emotional fields, I can analyze the acoustic information in the audio to identify clues related to personal emotions", we can infer that this sentence might be her emotional evaluation or analysis of someone or somewhere. Therefore, this sentence could be a positive and satisfying way for her to reflect on or evaluate the past days spent in Bo Yuan, consistent with her overall display of emotional stability and satisfaction.

### 近邻3：samplenew3_00074220

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, disbelief, frustration, helplessness
- 与query gold精确词面重合：∅
- 字幕：How is it possible to be fine?
- 描述：In the text, the caption reads: "How could anything be okay?" This phrase might be a response from a woman to a certain situation or event. Given the description of the woman's complex expression in the video hints, one that is both surprised and angry, and the emotional cues from her audio delivery of anger, frustration, and helplessness, we can infer that this sentence might be conveyed with a tone of disbelief or anger. The woman may find it hard to accept or believe the occurrence of a certain situation, thus expressing this negative emotion.

### 近邻4：samplenew3_00071154

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：frustration, humor, irritation, self-deprecation
- 与query gold精确词面重合：∅
- 字幕：When are we leaving, immortal? Are you trying to chase me away?
- 描述：In the text, the caption reads: "When will the immortal depart? This is trying to get me to leave." This phrase might be a form of self-mockery or humor from the speaker. Given the individual's possible feelings of frustration or irritation as indicated by the audio clues, and the woman's mixed expression of surprise and disbelief in the video hints, we can infer that this statement might carry a tone of self-deprecation or humor. The woman may be using humor as a way to cope with some difficulties or challenges she is facing.

### 近邻5：samplenew3_00046817

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：mockery, negative, seriousness, solemn, suppressed
- 与query gold精确词面重合：∅
- 字幕：As your lover's burial concubine
- 描述：In the text, the subtitle content "As your burial concubine" is possibly a term of address or description of the person the man is speaking to. Based on the man's calm and composed facial expression and formal attire in the video clues, we can infer that this phrase may carry a serious or solemn tone. At the same time, based on the description in the audio clues that the individual may be experiencing negative emotions, we can speculate that this phrase may have a suppressed or negative emotional connotation. Therefore, this phrase may be a negative evaluation or mockery of someone by the man, consistent with the overall calm and composed emotions displayed by the man.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 68. samplenew3_00044508｜gain｜ΔF1 +0.047619

gold：anger, anxiety, fear, nervousness

query字幕：Without Xu Shanchuan's consent, it is you.

源标注描述：In the text, the caption reads: "It's you, without Xu Shanchuan's consent." Based on the video hints of the female character appearing thoughtful or serious, and the audio cues of the speaker's's voice trembling and shaking, it indicates that the speaker is experiencing intense emotions, possibly fear, anxiety, or nervousness. This caption could be the female character's accusation or criticism of someone, likely due to the other party acting without Xu Shanchuan's consent, which has made the female feel discontented or angry.

off原始输出：The character's emotional state is sadness, contemplation, anger.

retrieval原始输出：The character's emotional state is anger, sadness.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, contemplation, sadness|0.285714|1|2|3|
|retrieval|anger, sadness|0.333333|1|1|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.285714变为0.333333，差值+0.047619。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：contemplation。

gate：0.120010294；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00094132

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, empathetic, gentle, tender, warning
- 与query gold精确词面重合：∅
- 字幕：Do you still remember that I told you one day when you sit on this chair, you will have no chance anymore?
- 描述：In the text, caption content: "Even if Kuan still remembers, did I tell you that one day when you sat on this stool, there was would be no chance for you." Based on the description of the female voice in the audio cues, which is gentle and tender, full of empathy and concern, with a hint of tremble, it can be inferred that this sentence might be spoken by a woman either comforting or warning the other party. The softness and caring nature of her voice suggest she may be attempting to reassure the other person, while the trembling in her voice could indicate her concern for the other's's situation or future. Therefore, this sentence might be a warning or reminder, suggesting that the other person might have missed an opportunity and is about to face difficulties or challenges.

### 近邻2：samplenew3_00083829

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, disappointment, frustration
- 与query gold精确词面重合：anger
- 字幕：You went to Shaotianwei and said that I have a problem in my heart.
- 描述：In the text, caption content: "Yet you went to Shaotianwei and said there's something wrong with me." This sentence could be a form of accusation or response from a woman to a man. Given the emotional tone described in the audio clues, such as sadness or disappointment, and the visual cues of the woman crying and the man's showing concern, we can infer that this sentence might carry an angry or dissatisfied tone. The woman might feel betrayed or misunderstood by the man, thus expressing her dissatisfaction with his actions. This statement suggests conflict and tension between the two individuals.

### 近邻3：samplenew3_00071704

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, pressure, tension
- 与query gold精确词面重合：anxiety
- 字幕：Cancelled everything in one minute.
- 描述：In the text, the subtitle reads, "Cancelled everything in one minute." This sentence is likely spoken by the individual in the audio. Based on the description of the individual's tense and anxious voice characteristics in the audio cues, as well as the expression of canceling everything in the subtitle, we can infer that this sentence is a decision or reaction made by the individual under anxiety and pressure. The individual may be facing an urgent situation or pressure that causes them to feel anxious and unsettled. Therefore, this sentence expresses the individual's state of tension and pressure.

### 近邻4：samplenew3_00083349

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：focused, positive, thoughtful
- 与query gold精确词面重合：∅
- 字幕：Isn't it also a kind of resource grafting?
- 描述：In the text, caption content: "Isn't that also a form of resource grafting?" This sentence might be a response or viewpoint in a conversation by a woman. Given the individual's experiences described in the audio cues, which include complex emotions such as excitement, anticipation, and nervousness, and the woman's portrayed serious and focused emotional state in the video clues, we can infer that this statement might carry a positive attitude and thought process. The woman may have presented an idea or suggestion in the discussion, positing that some form of resource grafting is valuable. Therefore, this sentence could be the woman expressing her viewpoint in the conversation, demonstrating her attention and focus on the discussion topic.

### 近邻5：samplenew3_00106844

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, heartbroken, sympathy
- 与query gold精确词面重合：∅
- 字幕：Just breaking this sad person
- 描述：In the text, caption content: "Just this heartbroken one." This sentence might be a woman's evaluation or reaction to someone or some event. Given the mixed expression of surprise and anticipation on her face, along with her focused body language in the video hints, it can be inferred that she has a strong emotional response towards the person or event. Meanwhile, according to the audio hints, her voice is hoarse with rapid breaths, and there's a slight tremble, suggesting that this person might be experiencing a strong emotion like fear or anxiety. Therefore, this sentence might be an expression of her sympathy or concern for this person or event, believing him to be heartbroken, and hoping to help or comfort him.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 69. samplenew3_00038000｜gain｜ΔF1 +0.055556

gold：anger, contemplation, despair, helplessness, powerless, sadness, sorrow

query字幕：My silly child

源标注描述：In the text, the caption reads: "My foolish child," suggesting that the elderly man depicted in the video's hints through facial expressions and body language might be experiencing complex emotions such as sorrow, contemplation, and anger. Simultaneously, the individual voice described in the audio clues is filled with sadness and despair, having a heavy tone, indicating they may feel helpless and powerless. Based on these clues, we can infer that "my foolish child" in the caption might be a term of endearment or a way to express care. This phrase could possibly be how someone close addresses the elderly man or offers comfort, attempting to alleviate his emotional distress.

off原始输出：The character's emotional state is sadness, contemplation.

retrieval原始输出：The character's emotional state is sadness, contemplation, anger, frustration, disappointment.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|contemplation, sadness|0.444444|2|0|5|
|retrieval|anger, contemplation, disappointment, frustration, sadness|0.500000|3|2|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.444444变为0.500000，差值+0.055556。
- TP变化+1，FP变化+2，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：disappointment, frustration。
- 相对off新增命中的gold标签：anger。

gate：0.119915158；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00032871

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：distress, sadness
- 与query gold精确词面重合：sadness
- 字幕：My second younger brother just left.
- 描述：In the text, caption content: "My second younger brother just left." Based on the individual's crying facial expression and tears in the video clues, as well as the trembling and shivering in the speaker's's voice indicated in the audio clues, we can infer that this sentence might be conveying the individual's sadness or distress. The individual may have just lost his second younger brother, which could be the reason for his low spirits. Due to a lack of additional contextual information, we cannot ascertain the specific emotional state or cause, but can speculate that the individual is experiencing a sorrowful emotion.

### 近邻2：samplenew3_00021845

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：incredulous, surprise
- 与query gold精确词面重合：∅
- 字幕：
- 描述：In the text, the caption reads: "Isn't it so cool." This sentence might be a response from a male speaker to an event or situation. Considering the enthusiastic and passionate tone described in the audio clues and the surprised or shocked facial expression of the man shown in the video hints, we can infer that this sentence might carry a sense of surprise or incredulity. Therefore, this sentence could be the male speaker's's reaction to an unexpected or surprising circumstance, which alignss well with the man's overall strong emotional response.

### 近邻3：samplenew3_00011070

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confusion, distressed, needing support, seeking help
- 与query gold精确词面重合：∅
- 字幕：Call me Guo Cun
- 描述：In the text, the caption reads: "Calling upon the passage through the village," given the man's facial expressions filled with anguish in the video hints, and the woman's efforts to console and support him, along with the audio clues depicting a range of emotions from sadness to fear that the man experiences, we can infer that this phrase might be the man expressing his confusion and distress, seeking the help and support of the lady. This phrase may suggest that the man is facing some difficulties or challenges, needing assistance and support to overcome them.

### 近邻4：samplenew3_00016147

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：attentive, caring, enthusiasm, gratitude, positive
- 与query gold精确词面重合：∅
- 字幕：Dedicated and enthusiastic
- 描述：In the text, the caption reads: "Skilled Enthusiasm". Given the man's positive emotional state and willingness to engage in social interaction as portrayed in the video clues, and considering the description of the man possibly experiencing intense negative emotions in the audio cues, we can infer that this phrase might be an expression of praise or gratitude from the man towards others. Despite the man possibly undergoing negative emotions, he still demonstrates a caring and attentive attitude towards others, which alignss with his overall positive demeanor.

### 近邻5：samplenew3_00041362

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, confusion, detachment, dissatisfaction, frustration, self-blame
- 与query gold精确词面重合：∅
- 字幕：Being a real father
- 描述：In the text, the subtitle content says, "Truly being a father." This sentence may be the man's self-evaluation or reflection. Based on the troubled state displayed by the man in the video clues and the mixed emotion of anxiety and detachment felt by the individual in the audio clues, we can infer that this sentence may carry a sense of self-blame or frustration. The man may be contemplating his role and responsibility as a father and feeling confused and unsatisfied. Therefore, this sentence may be a negative evaluation or self-criticism by the man, consistent with the overall display of his troubled and anxious emotions.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 70. samplenew3_00102175｜gain｜ΔF1 +0.066667

gold：admiration, joy, surprise

query字幕：Awesome, awesome

源标注描述：In the text, the caption reads: "Wow, impressive." This phrase might be a commentary or reaction to an Asian man in the video. Given the audio cues of a shaky and trembling voice, speaking at a rapid pace, as well as visual hints of the man's displaying a comical expression and a teasing mood, we can infer that this statement may carry a tone of surprise or admiration. Therefore, this sentence might be a praise for the man's's actions or skills, aligning with his overall sense of joy.

off原始输出：The character's emotional state is admiration, excitement, enthusiasm.

retrieval原始输出：The character's emotional state is admiration, excitement.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|admiration, enthusiasm, excitement|0.333333|1|2|2|
|retrieval|admiration, excitement|0.400000|1|1|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.333333变为0.400000，差值+0.066667。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：enthusiasm。

gate：0.119937815；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00086375

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：bewilderment, surprise
- 与query gold精确词面重合：surprise
- 字幕：But I never expected that Li Yan actually convinced Meng Da to change his mind.
- 描述：In the text, caption content: "Who would have thought that Li Yan actually convinced Meng Da to rebel." This sentence might be a man expressing surprise and confusion over an unexpected event or someone's behavior. Given the unusual facial expressions of the man and the emphasis in his body language as well as the trembling and uncertain tone of his voice based on audio clues, we can infer that this sentence expresses the man's shock and bewilderment at Li Yan's ability to persuade Meng Da to oppose. Therefore, this sentence may carry an element of surprise and bewilderment, aligning with the strong emotional state the man is portraying.

### 近邻2：samplenew3_00081020

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, discontent, fury
- 与query gold精确词面重合：∅
- 字幕：I had no choice but to kill Kong Xiu. It has nothing to do with you. Quickly inform the Prime Minister and tell him to order all officials not to trouble me anymore. Did you hear me?
- 描述：In the text, the caption reads: "When I killed Kong Xi, it was under duress and not something to do with any of you. Quickly inform the chancellor and tell him to hurry and order all officials to stop causing trouble for me. Did you hear that?" Given the intense anger and aggressive tone of the individual's's voice as described by the audio clues, along with the serious expression, confident posture, and formal attire of the man depicted in the video clues, we can infer that this statement is likely an expression of his discontent and fury. He might be explaining to those around him or the audience why he killed Kong Xi, and demanding that he be informed by the chancellor to issue orders to all officials to cease bothering him. The strong negative emotions and anger in this statement align with the personal emotional state described in the audio clues.

### 近邻3：samplenew3_00073788

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：The first, third, and fourth teams are respectively stationed at the southwest, northwest, and north gates.
- 描述：In the text, caption content: "One three teams are respectively deployed at the south, north, and west gates." Given the description of the man's's serious expression and confident body language in the video clues, along with the environment and attire suggesting it might be a historical or cultural performance related to Chinese traditions or history, we can infer that this caption content might refer to the man describing or explaining some strategy or layout. Since the man shows a focused state without any obvious emotional expression, there is no basis for speculating about the man's's emotional state from this caption content.

### 近邻4：samplenew3_00109740

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, frustration, impatience, nervousness, worry
- 与query gold精确词面重合：∅
- 字幕：Did Peiyuan Ju Ci go deep into the enemy's territory for nearly 200 miles? Did he take 20,000 iron riders with him?
- 描述：In the text, the subtitle reads, "Did Peiyuan take his 20,000 cavalry deep into the enemy's territory for nearly 200 miles?" This sentence may be the man's dialogue or conversation in the video. Based on the high pitch of the speaker described in the audio clues and the repeated use of phrases, it suggests that he may be feeling anxious, nervous, frustrated, and impatient. The context described in this sentence may be related to war, military operations, or a tense situation. The man's facial expressions and body language also imply that he may be experiencing a range of emotions such as nervousness, worry, or anxiety. Therefore, this sentence may be the man expressing his concerns and unease about the war or military operation.

### 近邻5：samplenew3_00105117

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, excitement
- 与query gold精确词面重合：∅
- 字幕：Prime Minister, let us stay in Fancheng and wait for orders to attack. It seems like we will be going to battle immediately, according to the General's intention.
- 描述：In the text, the caption reads: "The prime minister has instructed us to remain in Fancheng and await orders for an offensive, it seems as if the general is about to engage in battle at any moment." The speaker's, based on the audio clues of the male voice speaking quickly with urgency and a hint of provocation, along with the sound of footsteps in the background, can be inferred to be full of energy and enthusiasm. Their confidence in their beliefs is strong. Simultaneously, the facial expressions and body language of the man in the video hints at a complex mix of emotions, possibly related to the activities or performances he was involved in. Therefore, based on the description in the text, one can deduce that the man is filled with excitement and confidence as he prepares for battle.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 71. samplenew3_00085875｜gain｜ΔF1 +0.083333

gold：disappointment, dissatisfaction, frustration, irritability, stress, worry

query字幕：I am not an expert.

源标注描述：In the text, the subtitle reads "I'm not good at this." Based on the man's worried expression and body language in the video clues, as well as the implication of a formal or professional setting in the room's environment, we can infer that the man may be experiencing a negative emotion such as stress or worry. The audio clue of the individual's confident and slightly sharp tone of voice suggests a feeling of frustration or irritability, but still being able to control their emotions. Therefore, the words in the subtitle may be the man's self-deprecating or self-blaming remark, expressing his dissatisfaction or disappointment with his abilities. This aligns with the overall display of concern and negative emotions by the man.

off原始输出：The character's emotional state is dissatisfaction, impatience.

retrieval原始输出：The character's emotional state is stress, contemplation, frustration, annoyance, sadness, anger, frustration.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|dissatisfaction, impatience|0.250000|1|1|5|
|retrieval|anger, annoyance, contemplation, frustration, sadness, stress|0.333333|2|4|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.250000变为0.333333，差值+0.083333。
- TP变化+1，FP变化+3，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：dissatisfaction。
- 相对off新增未精确匹配gold的标签：anger, annoyance, contemplation, sadness。
- 相对off新增命中的gold标签：frustration, stress。
- 相对off移除未精确匹配gold的标签：impatience。

gate：0.119933970；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "annoyance", "unmatched_gold_label": "dissatisfaction"}]}

实际5近邻证据：

### 近邻1：samplenew3_00047597

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, mockery, negative, nervousness, sarcasm
- 与query gold精确词面重合：∅
- 字幕：This Yu Zhenjia is a stubborn person who doesn't listen to advice.
- 描述：In the text, caption content: "This is a hard-nosed character for Zhenjia." Given the speaker's's voice tone described as high-pitched with a trembling quality in the audio clues, and the man's's facial expressions suggesting he might feel confident, decisive, even slightly defensive, we can infer that this phrase may be an evaluation or reaction to the speaker. Considering the speaker's's possible experience of anxiety, fear, and nervousness based on the audio clues, and the man's's expressions and body language in the video clues, we can speculate that this phrase might carry a sarcastic or mocking tone. Therefore, this sentence might be a negative evaluation or mockery, contradicting the man's's overall emotional state.

### 近邻2：samplenew3_00014622

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, happiness, impression, pleased
- 与query gold精确词面重合：∅
- 字幕：I admire you more in my heart.
- 描述：In the text, the caption reads: "Deep down, I have even more admiration for you." This sentence could be a man's's evaluation or reaction to someone else. Given the speaker's tone in the audio clues, which is confident and decisive, with a relatively high pitch indicating of excitement or enthusiasm, and the video clues showing the man smiling and giving a thumbs up, indicating of positive, satisfied, and happy emotions, we can infer that this statement might be a form of praise or admiration. The man might be highly impressed and admiring of someone's actions or accomplishments, which alignss well with his overall positive demeanor.

### 近邻3：samplenew3_00000070

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, defeated
- 与query gold精确词面重合：∅
- 字幕：Don't say these words about the tree being big and having deep roots.
- 描述：In the text, the caption reads: "Don't say 'tree roots run deep'." This phrase might be this man expressing his viewpoint or countering someone else's statement. Given the audio cues that describe the speaker's aggressive tone and insistence, as well as the video clues showing the man yelling and making a fist gesture, we can infer that the sentence might carry an angry or defeated emotion. The phrase might be the man expressing his dissatisfaction or opposition, attempting to assert his point of view through a strong tone. Therefore, the sentence might have a confrontational or argumentative connotation, fitting with the overall tense and playful mood he exhibits.

### 近邻4：samplenew3_00083977

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：authentic, confidence, firm, honest
- 与query gold精确词面重合：∅
- 字幕：Let's not lie in front of honest people.
- 描述：In the text, the caption reads: "We'll be honest people and not tell lies." This phrase might be used by the speaker to emphasize honesty and authenticity. Given the audio cues describing the speaker's in a firm and confident manner, along with the video clues of the man's appearing serious with a focused gaze, we can infer that this statement might be the speaker emphasizing their own authenticity and honesty, conveying a sense of firmness and confidence. Therefore, this statement might be highlighting a genuine and honest approach towards the topic discussed or cultural heritage being talked about.

### 近邻5：samplenew3_00085960

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, stress, urgency
- 与query gold精确词面重合：stress
- 字幕：Take down Jin Fu Chen Huang
- 描述：In the text, caption content: "Remove Jin Fu Chen Huang". This phrase might refer to an older man discussing or deciding on the removal or dissolution of an individual or team. Given the serious and intense facial expressions described in the video clues, along with the concentration and determination in his body language, it can be inferred that he is engaged in a critical conversation or addressing important matters. The audio clues also support this inference, describing a shaky personal voice, rapid speech with urgency, and feelings of anxiety, stress, and urgency. Therefore, this phrase could be what the older man says when making decisions about removal or dissolution of someone or a team.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 72. samplenew3_00059841｜gain｜ΔF1 +0.083333

gold：anticipation, excitement, longing, tension, uncertainty

query字幕：If I could really join Master Lin's team

源标注描述：In the text, caption content: "If one were to actually make it into Master Lin Li's team." This sentence might be spoken by a man in the video. Based on the personal voice tremble, hesitation, and uncertainty described in the audio clues, as well as the man's's calm, smile, and relaxed demeanor depicted in the video, we can infer that this phrase may carry an element of anticipation, desire, or yearning. The man might be excited and thrilled at the prospect of joining Master Lin Li's team, but he may also feel a bit tense and uncertain. Therefore, this statement expresses the man's's longing and anticipation for joining Master Lin Li's team, which alignss with his overall positive mood.

off原始输出：The character's emotional state is anticipation, longing, excitement, nervousness.

retrieval原始输出：The character's emotional state is anticipation, longing, excitement.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anticipation, excitement, longing, nervousness|0.666667|3|1|2|
|retrieval|anticipation, excitement, longing|0.750000|3|0|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.750000，差值+0.083333。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：nervousness。

gate：0.120074637；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00037328

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：pride, satisfaction
- 与query gold精确词面重合：∅
- 字幕：The outcome of me and him should be considered a half-point difference.
- 描述：In the text, the subtitle reads: "The outcome of our competition should be a half-point difference." This sentence may be the speaker's evaluation or viewpoint on the result of a match or competition. Based on the confident and firm tone described in the audio clues, as well as the use of the word "victory" implying a sense of triumph or success, we can infer that the speaker may hold a proud and satisfied attitude towards the outcome of their competition with someone else. Therefore, this sentence expresses a positive emotional state, feeling proud and satisfied with their achievements.

### 近邻2：samplenew3_00100962

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：inspiring, positive, uplifting
- 与query gold精确词面重合：∅
- 字幕：I saw a poem that is powerful enough to turn your defeat into victory.
- 描述：In the text, the caption reads: "I've seen a melody so enchanting it could turn defeat into victory." Given the description of the male voice in the audio cues as calm and soothing, along with the serene and tranquil ambiance created by the background music, this statement can be inferred to possibly describe a piece of music or artwork. Moreover, considering the character's's calm and organized demeanor in the video clues, coupled with his apparent deep contemplation, this statement might describe a piece of music that brings about inner peace and reflection, or could be offering someone a positive encouragement and support. Therefore, this phrase may carry an uplifting and inspiring emotional tone, aligning well with the male's's overall calm and positive disposition.

### 近邻3：samplenew3_00090541

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipatory, blessing, calm, excitement, good fortune, happiness, nervousness, serene
- 与query gold精确词面重合：excitement
- 字幕：He already has you in his heart, and now if you let you two meet again, I'm afraid we will be attending your wedding tomorrow.
- 描述：In the text, with subtitles stating: "He's already overwhelmed with everything now, and if we meet you guys again, perhaps we'll be drinking your wedding feast tomorrow," the individual in the audio clip experiences a series of emotions, including excitement, anticipation, and nervousness, along with the use of high-pitched and rapid speech. This suggests that the statement likely carries an excited and anticipatory tone.   Conversely, based on the video clues showing the woman in a calm posture and expression, amidst a serene environment, we can infer that this statement might represent her anticipation and blessing for someone or something. Therefore, it appears that she is expressing her excitement and anticipation for a wedding or a joyful event, possibly wishing someone happiness and good fortune.

### 近邻4：samplenew3_00082255

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, respect, surprise
- 与query gold精确词面重合：∅
- 字幕：Could it be that you have really seen the strongest in the three realms?
- 描述：In the text, caption content: "Could it be that they really encountered the supreme power of the Three Realms." This sentence might be something a man said to a woman. Based on the audio clues described with a personal voice that is calm and restrained, showing no signs of excitement or anxiety, and considering the video clues where the man has a focused gaze and the woman's attire suggests a formal or semi-formal setting, we can infer that this sentence could be an expression of admiration or surprise from the man directed towards the woman. Therefore, this phrase might carry a tone of respect or astonishment, fitting with the man's's overall demeanor of engagement and interest.

### 近邻5：samplenew3_00114551

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：criticism, discontent, questioning
- 与query gold精确词面重合：∅
- 字幕：Why does a little grass watch these fights and killings all day?
- 描述：In the text, the caption reads: "What's the point of watching all these fights and killings?" This phrase might be a man's's evaluation or reaction to a certain behavior or activity. Based on the audio clues described in the individual's speaking at a high pitch, quickly, and in fragments, as well as the video clues showing the man in a state of contemplation or self-reflection, we can infer that this sentence might carry an undertone of dissatisfaction or questioning. The man may hold a critical attitude towards a violent or combat activity, considering such activities meaningless or unworthy of attention. Therefore, this sentence could be a negative assessment of a particular behavior or activity by the man.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 73. samplenew3_00075057｜gain｜ΔF1 +0.085714

gold：confusion, dejection, dissatisfaction, helplessness, resignation

query字幕：If the fire is too dim, I really can't see clearly.

源标注描述：In the text, caption content: "If the fire is too dim to see clearly." This sentence might be a lady's description or commentary on a certain situation or scene. Based on the neutral facial expression and stiff body language shown by the lady in the video clues, as well as the audio clues describing a low-pitched voice, a monotone tone, and a lack of emotion, we can infer that the sentence might carry a sense of resignation or dejection. The lady may be describing a dimly lighted scenario where she feels confused and helpless due to being unable to clearly see. Therefore, this sentence might reflect the lady's negative emotions and dissatisfaction with the situation.

off原始输出：The character's emotional state is anxiety, tension, stress, dissatisfaction, disappointment.

retrieval原始输出：The character's emotional state is frustration, helplessness.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, disappointment, dissatisfaction, stress, tension|0.200000|1|4|4|
|retrieval|frustration, helplessness|0.285714|1|1|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.200000变为0.285714，差值+0.085714。
- TP变化+0，FP变化-3，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：dissatisfaction。
- 相对off新增未精确匹配gold的标签：frustration。
- 相对off新增命中的gold标签：helplessness。
- 相对off移除未精确匹配gold的标签：anxiety, disappointment, stress, tension。

gate：0.120039128；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "frustration", "unmatched_gold_label": "dissatisfaction"}]}

实际5近邻证据：

### 近邻1：samplenew3_00039777

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：apathetic, indifference
- 与query gold精确词面重合：∅
- 字幕：Since I can't get it, there's no need to be sad in vain.
- 描述：In the text, the caption reads: "There's no point in being heartbroken if you can't have it." This phrase might be a woman expressing her viewpoint or advice. Given the visual clues conveyed through the woman's facial expressions and body language, which suggest defiance or disagreement, as well as the audio hints of a monotonous tone and possibly negative emotions, we can infer that the statement might be delivered with a tone of indifference or apathy. Therefore, this sentence could be the woman telling someone not to feel sad about not getting something, reflectinging her attitude towards giving up or accepting reality.

### 近邻2：samplenew3_00096933

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, tension
- 与query gold精确词面重合：∅
- 字幕：Your father also has a face in front of the emperor.
- 描述：In the text, the caption reads: "Your father is also favored by the emperor." This phrase might be a comment or response from a woman to someone else. Considering the audio hints that include a trembling voice and a slightly quicker pace, along with the video clues showing a woman with a neutral expression and body language, we can infer that this sentence might be delivered in a tense or concerned tone. Therefore, the statement could be the woman reminding someone about their father's image or status before the emperor, possibly hinting at some sort of pressure or significance.

### 近邻3：samplenew3_00097481

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：complaint, dissatisfaction, frustration
- 与query gold精确词面重合：dissatisfaction
- 字幕：General Xiao's words are heavy, it's just that my elder brother is currently bedridden.
- 描述：In the text, the caption reads: "General Xiao, you're overstating it, my brother is currently bedridden." Given the audio cues describing a person's with a tense, pressured voice, fluctuating pitch and volume, and a quick pace, along with the caption mentioning that the brother is ill in bed, we can infer that this line might be a woman'sting back or explaining to General Xiao. Considering the individual described in the audio went through a series of negative emotions, we can deduce that the statement might carry an undertone of dissatisfaction or complaint. The woman might feel that General Xiao has exaggerated, not sufficiently understanding her brother's illness and predicament, leading her to express her perspective and feelings.

### 近邻4：samplenew3_00106844

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, heartbroken, sympathy
- 与query gold精确词面重合：∅
- 字幕：Just breaking this sad person
- 描述：In the text, caption content: "Just this heartbroken one." This sentence might be a woman's evaluation or reaction to someone or some event. Given the mixed expression of surprise and anticipation on her face, along with her focused body language in the video hints, it can be inferred that she has a strong emotional response towards the person or event. Meanwhile, according to the audio hints, her voice is hoarse with rapid breaths, and there's a slight tremble, suggesting that this person might be experiencing a strong emotion like fear or anxiety. Therefore, this sentence might be an expression of her sympathy or concern for this person or event, believing him to be heartbroken, and hoping to help or comfort him.

### 近邻5：samplenew3_00053586

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：excitement, frustration, suspicion
- 与query gold精确词面重合：∅
- 字幕：The matters of flowers seem to be right in front of me again.
- 描述：In the text, the caption reads: "The matter of flowers seems to be right before my eyes." This phrase might be a lady's comment or reaction to a particular event or situation. By inferringing from the pitch and rhythm fluctuations, as well as the tone changes in the personal voice described in the audio clues, we can deduce that this sentence might carry a complex emotion, including excitement, frustration, suspicion, etc. The lady's's facial expressions and body language indicate that she is experiencing an important and challenging moment. Therefore, this sentence could be her reaction to a sudden incident or news, expressing her complicated emotions and concerns about the event.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 74. samplenew3_00097673｜gain｜ΔF1 +0.100000

gold：dissatisfaction, worry

query字幕：That in heaven's spirit does not want to see Your Majesty for him.

源标注描述：In the text, the caption reads: "Even the spirits in heaven would not wish to see Your Majesty for him." This phrase could be a speaker's's commentary or reaction to someone or a situation. Given the audio cues where the speaker's's voice is pitched high and slightly trembling, along with the tranquil atmosphere of the setting depicted in the video and the calm expression of the individuals involved, we can infer that the statement might convey a sense of concern, anxiety, or disapproval. Therefore, this statement might be expressing dissatisfaction or worry about a particular or action, contrasting with the peaceful and serene ambiance portrayed in the video.

off原始输出：The character's emotional state is dissatisfaction, disapproval, anger.

retrieval原始输出：The character's emotional state is dissatisfaction, anger.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, disapproval, dissatisfaction|0.400000|1|2|1|
|retrieval|anger, dissatisfaction|0.500000|1|1|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.400000变为0.500000，差值+0.100000。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：disapproval。

gate：0.119979858；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00086052

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, panic
- 与query gold精确词面重合：∅
- 字幕：The Wu State case eight years ago and today's conspiracy of benevolence and love are probably all orchestrated by the Crown Prince.
- 描述：In the text, caption content: "Eight years ago's Wu case and today's Co-conspirator Benevolence might all be engineered by the Crown Prince." Based on the caption mentioning the "Wu case eight years ago" and "today's Co-conspirator Benevolence," along with the man's's serious expression in the video clues and the formal setting implied by the environment, we can infer that the man may be discussing or contemplating some significant political or legal events. These events might be related to his position or duties within the imperial palace, hence he might feel under pressure or concern. Given the audio clues describing the person's's trembling voice, rapid and shallow breathing, and emotional analysis by an expert in the emotional field, we can speculate that the man might be experiencing intense negative emotions, such as fear, anxiety, and panic. This might be due to the important events or responsibilities he is facing.

### 近邻2：samplenew3_00023724

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：contentment, excitement, pride, surprise
- 与query gold精确词面重合：∅
- 字幕：What a blessing from heaven
- 描述：In the text, the caption reads: "Surely, a blessing from heaven." This phrase might be a man's's self-assessment or response to his surroundings. Given the audio clues that describe the man's voice as high-pitched with slight tremors, spoken at a quick pace, and the video hints suggesting a smile and an indication of luxurious surroundings, we can infer that this sentence may be conveyed with excitement or surprise. Therefore, this statement could be the man's's praise or reflection on himself or his environment, aligning with his overall positive mood.

### 近邻3：samplenew3_00066361

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：cautious, concern, warning
- 与query gold精确词面重合：∅
- 字幕：That is because I am afraid that others will take advantage of you.
- 描述：In the text, the caption reads: "That's because they fear others will ask you to do something on their behalf." This sentence could be an evaluation or advice from the speaker to someone. Considering the audio hints of a slight tremble in the speaker's's voice and a deliberate slow tone, along with the video clues showing an older man with a serious and firm expression while a younger man displays a relaxed and composed demeanor, we can infer that the statement might carry a tone of concern or warning. Therefore, this sentence may be reminding someone to be cautious about others' requests, to avoid being exploited or forced to do something for them. This alignss with the inference that the older man might be in a position of authority or importance.

### 近邻4：samplenew3_00086943

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, tension
- 与query gold精确词面重合：∅
- 字幕：But wife, now I want to tell you my decision. I plan to give up.
- 描述：In the text, the subtitle reads: "But now I want to tell you my decision, I am planning to give up." This sentence might be what a man says to his wife. Based on the audio cues described in the personal voice trembling and shaking, along with very slow speech pace, it indicates that he is experiencing intense emotional stress and difficulty. This sentence might be him expressing a significant decision, and due to his emotional state, he may feel extremely tense and anxious. Therefore, this sentence carries an air of tension and unease, which alignss with the described personal emotional state in the audio clues.

### 近邻5：samplenew3_00055197

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction
- 与query gold精确词面重合：dissatisfaction
- 字幕：Where do you suspect it's easy for them not to say it earlier?
- 描述：In the text, the subtitle reads, "Why didn't they say it earlier if they suspect it?" This sentence may be the man questioning or criticizing the actions or decisions of a team or individual. Based on the serious expression and posture of the man in the video clues, as well as the high-pitched, excited, and fast-paced tone of the individual in the audio clues, we can infer that this sentence may carry a sense of dissatisfaction or anger. The man may be disappointed or dissatisfied with the actions of a team or individual and wishes they had expressed themselves or taken action earlier. This emotion may align with the overall serious and focused demeanor displayed by the man.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 75. samplenew3_00076031｜gain｜ΔF1 +0.107143

gold：friendliness, passion, respect, seriousness

query字幕：Also my senior and big brother for so many years.

源标注描述：In the text, the caption reads: "Also my old senior, my big brother for so many years." This phrase might be a title or evaluation that the man in front addresses or comments on the man behind him. Given the audio cues where describe the characters' voices as high-energy and passionate, and the video hints showing the man in front with a serious and thoughtful demeanor, we can infer that this statement might carry a tone of intimacy or respect. Therefore, this phrase could be a friendly greeting or praise, aligning with the overall serious mood displayed by the man in front.

off原始输出：The character's emotional state is friendly, respectful, serious, focused.

retrieval原始输出：The character's emotional state is friendly, respectful, serious.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|focused, friendliness, respect, seriousness|0.750000|3|1|1|
|retrieval|friendliness, respect, seriousness|0.857143|3|0|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.750000变为0.857143，差值+0.107143。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：focused。

gate：0.120018013；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00079292

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, overwhelm, under pressure
- 与query gold精确词面重合：∅
- 字幕：And I have taken all the responsibility.
- 描述：In the text, the caption reads: "And I took all the blame." This sentence might be a statement made by a man in a discussion. Given the speaker's's voice description in the audio clues with a sense of urgency and tension, and the man's facial expressions and body language in the video clues showing complex emotions, we can infer that this sentence might be the man expressing the weight and burden of taking responsibility. This implies that the man may feel anxious, under pressure, and overwhelmed, which alignss with his overall complex emotional state.

### 近邻2：samplenew3_00096678

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, calm, seriousness, urgency
- 与query gold精确词面重合：seriousness
- 字幕：Funding is a big problem now. Come back soon, I'll be waiting for you in Hanzhou.
- 描述：In the text, the caption reads: "F of money is a big issue now, come back immediately, I'm waiting for you in Hanzhou." Given the audio hints describing a person speaking with a sharp and agitated tone, with a sense of urgency in their voice as they speak quickly and energetically, and video clues showing a man with an anxious and serious expression, with body language suggesting that he is actively dealing with the situation while making a conscious effort to remain calm, we can infer that this sentence might be part of an urgent or significant situation conveyed over the phone by a man. The complexity of the man's's emotions likely stems from the tension and anxiety evident in this phone conversation.

### 近邻3：samplenew3_00079649

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：appreciation, enthusiasm
- 与query gold精确词面重合：∅
- 字幕：This is so obvious, my master is showing off his car skills here.
- 描述：In the text, the caption reads: "How obvious it is that my master is showing off his car skills here." Given the tone of high pitch and excitement described in the audio cues, along with the expression style in the caption, we can infer that this sentence might carry an enthusiastic and appreciative emotion. The character may be commenting on or praising the demonstration of driving skills by his master, which alignss with the positive emotional description in the audio clues.

### 近邻4：samplenew3_00086545

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：aspirational, confidence, enthusiasm, focused
- 与query gold精确词面重合：∅
- 字幕：Transform Red Star into a great international enterprise.
- 描述：In the text, the caption reads: "Transforming Red Star Heavy Industry into a world-class great enterprise." Based on the visual cues in the video, which depict the man's with an intense and passionate expression and body language, and the audio clues that highlight his voice as sharp and tense, we can infer that this statement might be part of a speech or dialogue where he expresses his enthusiasm and aspirations for transforming Red Star Heavy Industry into a world-class enterprise. His facial expressions and body language suggest that he is confident and assured about this goal, also indicating his deep engagement and focus on the topic. Consequently, this statement can be interpreted as a reflection of the individual's's positive attitude and ambitious vision towards business development.

### 近邻5：samplenew3_00022627

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：depression, guilt, self-doubt
- 与query gold精确词面重合：∅
- 字幕：Is it because I haven't studied well enough?
- 描述：In the text, the caption reads: "Is it because I'm not learning well enough." This sentence might be a young Asian male expressing doubt or self-blame regarding his learning abilities. Based on the visual clues described in the video, such as his sad, hopeless expression and eyes filled with tears, along with the audio clues of his trembling voice and slightly faster speech pace, we can infer that this statement might carry a sense of guilt, self-doubt, or depression. He may be pondering over his learning capabilities, feeling disappointed and perplexed by his performance.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 76. samplenew3_00090033｜gain｜ΔF1 +0.126984

gold：anger, anxiety, confusion, sadness, surprise

query字幕：Why are my clothes so big?

源标注描述：In the text, the subtitle reads, "Why are my clothes so big?" Based on the description of the young man's attire and the room environment in the video clues, it can be inferred that he may be surprised or confused about his clothes. This could be because the size of the clothes is too big and does not meet his expectations or habits. Combined with the individual's emotional state described in the audio clues, including anxiety, anger, and sadness, it can be inferred that he is dissatisfied or frustrated with the issue of clothing size. This sentence may be a complaint or question he is expressing about his clothes size.

off原始输出：The character's emotional state is confused, dissatisfied, frustrated, angry.

retrieval原始输出：The character's emotional state is surprised, confused.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, confusion, dissatisfaction, frustration|0.444444|2|2|3|
|retrieval|confusion, surprise|0.571429|2|0|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.444444变为0.571429，差值+0.126984。
- TP变化+0，FP变化-2，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：anger。
- 相对off新增命中的gold标签：surprise。
- 相对off移除未精确匹配gold的标签：dissatisfaction, frustration。

gate：0.119966216；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00033059

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, annoyance, frustration
- 与query gold精确词面重合：anger
- 字幕：I have seen unreasonable people, but I have never seen someone as unreasonable as you.
- 描述：In the text, caption content: "I've seen rude behavior before, but you take the cake." This phrase could be a boy's evaluation or reaction to someone or a particular situation. The speaker's's tone, as described by the audio cues, suggests feelings of frustration or annoyance, and the laughter of the audience in response to the speaker's's predicament implies that the statement might carry an element of anger or resignation. The boy might be extremely displeased with someone or a situation, considering their actions to be exceptionally rude. Thus, this line might be the boy expressing his dissatisfaction and anger, aligning with the overall confusion and uncertainty in his demeanor.

### 近邻2：samplenew3_00019916

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, confusion, tension
- 与query gold精确词面重合：anxiety, confusion
- 字幕：What's wrong here?
- 描述：In the text, the caption content: "Hey, what's going on here" could be a young person expressing confusion or lack of understanding about their surroundings or an event happening. Based on the audio cues described with a high-pitched, rapid, and urgent tone of voice, along with the video clues showing the young person's comical expressions and awkward actions, we can infer that this phrase might be delivered in a tone conveying anxiety or tension. Therefore, this sentence likely represents a young person expressing their confusion or unease about the situation around them.

### 近邻3：samplenew3_00064876

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：attachment, encouragement, positive emotions, support
- 与query gold精确词面重合：∅
- 字幕：Just let my dad help you with your composition in his competition.
- 描述：In the text, the caption reads: "Let my dad take your essay in his game." This sentence expresses the speaker's's anticipation and hope for their father's participation in the competition. Given the enthusiastic and passionate tone described in the audio cues, along with the high level of commitment to their father's success, we can infer that this sentence conveys the speaker's's support and encouragement. Therefore, this sentence reflects the speaker's's positive emotions and attachment to their father.

### 近邻4：samplenew3_00002291

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：agitated, anger, anxiety, frustration
- 与query gold精确词面重合：anger, anxiety
- 字幕：Who is your boss? I am your undercover agent. I have some information in my hands. I must report it to you immediately.
- 描述：In the text, caption content: "Who's on your inside, I'm your mole, so I have intel that I need to report to you immediately." This sentence might be said by a man to a woman. Based on the audio cues described in the personal speaking tone which is high-pitched and aggressive, and the manner of speaking being fast and staccato, it indicates that he might feel frustrated, angry, anxious, and agitated. The tone and content of this sentence suggest an urgent and pressing emotion, possibly because he has important information that he needs to report to the woman. Therefore, this statement hints at the man's negative emotions and tense state.

### 近邻5：samplenew3_00045845

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：humor, positive
- 与query gold精确词面重合：∅
- 字幕：I have other things to do, please lend me some money quickly.
- 描述：In the text, the caption reads: "Hurry, lend me some rice, I have other things to do." This sentence could be a request or response from a man to someone else. Given the comedic and surprised facial expressions and body language of the man in the video clues, we can infer that the tone might be lighthearted or humorous. The man may be joking around or teasing the other person, conveying the message that he has other things to attend to. Therefore, this statement alignss with the overall positive mood displayed by the man. Since there are no emotional cues provided in the audio clues, we primarily base our speculation on the video clues to determine the man's's emotional state.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 77. samplenew3_00070085｜gain｜ΔF1 +0.126984

gold：aggression, discomfort, impatience, tension, urgency

query字幕：Please lend me three hundred yuan more.

源标注描述：In the text, the caption reads: "Borrow another three hundred silver coins from me." This sentence could be an expression of a person requesting to borrow money from another. Given the audio cues that describe the individual's speaking in a strong, aggressive tone, and with urgency and impatience, as well as the video clues showing the lady displaying a mix of surprise and curiosity along with positive body language, we can infer that this phrase might convey a sense of urgency and dissatisfaction. Therefore, this sentence could be a request or demand made by the person in a tense or uncomfortable situation, contrasting with the overall positive mood portrayed by the lady.

off原始输出：The character's emotional state is urgent, impatient, stressed, frustrated.

retrieval原始输出：The character's emotional state is urgent, impatient.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|frustration, impatience, stress, urgency|0.444444|2|2|3|
|retrieval|impatience, urgency|0.571429|2|0|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.444444变为0.571429，差值+0.126984。
- TP变化+0，FP变化-2，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：frustration, stress。

gate：0.120052390；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00007895

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, disbelief, fear, nervousness, surprise, warning
- 与query gold精确词面重合：∅
- 字幕：I'm afraid he will repeat the events of the afternoon of Zetian
- 描述：In the text, the subtitle reads: "I'm afraid he will repeat the events of that afternoon." This sentence may be the woman expressing her concern or warning to the man. Based on the emotional clues described in the audio, including fear, anxiety, and nervousness, as well as the woman's surprised and disbelieving expression in the video, we can infer that this sentence may be the woman's concern about a past event involving the man or a warning about something that may happen in the future. The woman's emotional reaction and the man's attempt to understand or react to her emotional state further support this inference.

### 近邻2：samplenew3_00111030

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：open-minded, positive
- 与query gold精确词面重合：∅
- 字幕：But the more I walk, the more cheerful my mood becomes, and then
- 描述：In the text, the caption reads: "Yet, as I walked, my mood became increasingly open-minded. Later on." This sentence might be a lady's way of describing or summarizing her emotional state. Given the video hints such as the lady dressed in traditional attire, her smile, and the formal or culturally themed setting of the room, we can infer that this sentence might describe her emotional shift after participating in an event. She may have felt tense or anticipation before the event started, but however, as the event progressed, her mood turned to being open-minded and positive. Therefore, this sentence could be understood as the lady describing her transformation in emotional state from a closed mindset to an open one.

### 近邻3：samplenew3_00082037

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, concern, deep thought, disappointment, overwhelm, pressure, sadness, tranquility
- 与query gold精确词面重合：∅
- 字幕：The store finally reopened after a lot of effort.
- 描述：In the text, the subtitle reads: "The store has struggled to reopen." Based on the description of the woman's pale complexion, downcast gaze, calm and composed expression, and the quiet and serene environment in the video clues, it can be inferred that she might be experiencing a state of tranquility or deep thought. The audio clues depict an individual speaking slowly and purposefully, suggesting they has experienced various negative emotions such as disappointment, anger, or sadness, feeling overwhelmed or under great stress. Therefore, the subtitle's's reference to "the store has struggled to reopen" could be interpreted as the woman's reflection on the reopening of the store, possibly accompanied by feelings of concern or pressure.

### 近邻4：samplenew3_00094403

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, bewildered, concern, confusion
- 与query gold精确词面重合：∅
- 字幕：Aunt Zhou is rich, do you still lack money?
- 描述：In the text, the subtitle reads: "Aunt Zhou has money, do you still lack funds?" Given the woman's's expression in the video, which is a blend of curiosity and concern, and her focused observation of another woman's body language, we can infer that she might be contemplating or worrying about some issue related to money. The phrase in the subtitles could be a question or an inquiry directed at the other person, suggesting that she believes the other shouldn't not be lacking funds because Aunt Zhou has money. Based on the audio description of the speaker's having a high tone, speaking quickly, and with enthusiasm, we can speculate that this sentence might carry a sense of excitement or intensity. Therefore, this sentence might be the woman expressing her confusion or bewilderment about the other person's's financial situation, possibly infused with anxiety or concern.

### 近邻5：samplenew3_00048494

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, anxiety, excitement, fear, positivity, satisfaction, tension
- 与query gold精确词面重合：tension
- 字幕：And it has to be sold at a higher price than before.
- 描述：In the text, caption content: "And sell for more than before." Given the woman's calm and relaxed facial expression described in the video hints, along with the serene and peaceful atmosphere in the environment, we can infer that she might be in a state of satisfaction and positivity. However, based on the emotional description from the audio hints, it could be excitement, anticipation, or tension, or there might also be negative emotions such as fear or anxiety. We cannot determine the woman's's exact emotional state. Therefore, this sentence could be an expression of the woman towards a certain plan or decision, but we cannot ascertain her emotional inclination.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 78. samplenew3_00059688｜gain｜ΔF1 +0.133333

gold：anxiety, tension, urgency

query字幕：Here is Xia Chuchang pleading for you.

源标注描述：In the text, the subtitle reads: "Here is the line where Director Xia is pleading for you." This sentence may be the man's explanation or clarification about someone or something. Based on the serious expression and focused body language of the man in the video clues, as well as the audio clue suggesting that the individual may be experiencing intense emotions such as fear or anxiety and may feel a sense of urgency or pressure, we can infer that this sentence may be the man explaining an important or urgent situation and may involve Director Xia's plea. Therefore, this sentence may carry a sense of tension, anxiety, or urgency, which aligns with the man's overall serious and focused emotional state.

off原始输出：The character's emotional state is urgent, anxious, frustrated.

retrieval原始输出：The character's emotional state is urgent, anxious.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, frustration, urgency|0.666667|2|1|1|
|retrieval|anxiety, urgency|0.800000|2|0|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.800000，差值+0.133333。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：frustration。

gate：0.120044939；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00037756

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration
- 与query gold精确词面重合：∅
- 字幕：My wife who takes care of our livelihood, do you think the lottery company is owned by your family and you can win it ten or eight times? Just one time is enough to knock both of us out.
- 描述：In the text, the caption reads: "My rice and oil wife, do you think lottery companies are run by your family, winninging ten or eight times, once would be enough to knock both of us out." This sentence might be a rebuke or criticism from the speaker towards the woman. Given the aggressive and confrontational tone of the speaker as described in the audio clues, along with the use of repetition to emphasize their point, we can infer that this statement carries an emotional charge of anger and frustration. Additionally, the video clues showing the woman's concern and the man's expression suggest a tense or conflict-filled atmosphere. Therefore, this sentence might be an intense reaction from the speaker towards the woman, expressing his disappointment and expectations regarding her lottery winnings.

### 近邻2：samplenew3_00022048

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, concern, frustration, overwhelm, sadness, under immense pressure, unease
- 与query gold精确词面重合：∅
- 字幕：I'm worried that my body can't hold on.
- 描述：In the text, the caption reads: "I'm worried my body can't take it." This sentence might be spoken by a man in a conversation. Given the individual's experiences described through audio cues, which include negative emotions such as sadness, anger, or frustration, along with feelings of being overwhelmed or under immense pressure, it can be inferred that this sentence expresses the man's concern and unease about his physical condition. This alignss with the video hints showing the man's sad facial expressions and negative emotions, suggesting he may be discussing or contemplating issues related to health or the body.

### 近邻3：samplenew3_00036112

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：bewilderment, shock, surprise
- 与query gold精确词面重合：∅
- 字幕：This person actually knew it early.
- 描述：In the text, the caption reads: "This person knew so early." This phrase might be the reaction of this individual to some event or situation, expressed in surprise or confusion. Given the video hints that depict the person's with a serious expression and intense focus, as well as audio cues indicating a trembling and shuddering voice, we can infer that the sentence likely conveys feelings of surprise, shock, or bewilderment. Therefore, it could be a response to an unexpected or surprising situation, aligning with the overall mood of seriousness and tension.

### 近邻4：samplenew3_00083183

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：frustration, innocence
- 与query gold精确词面重合：∅
- 字幕：It was him who proposed to leave, not me.
- 描述：In the text, the caption reads: "It was him who first suggested leaving, not me." This sentence could be a response or explanation from a lady to a gentleman. Based on the visual cues where the man is frowning and the lady is smiling, as well as audio hints of the speaker speaking in a monotonous tone without any emotional variation, we can infer that this statement might carry an undertone of resignation or explanation. The lady might be responding to the man's's accusations or reproaches, stating that she wasn't the cause of the departure. Therefore, this sentence may reflect the lady's sense of frustration or innocence.

### 近邻5：samplenew3_00067658

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：high pressure, negative
- 与query gold精确词面重合：∅
- 字幕：Mexico and Yucatan will definitely go to slide towards the feather's destiny.
- 描述：In the text, the caption reads: "Mex and will definitely slide into Yusheng's's fate." This sentence might be spoken by a man in a video. Given the man's serious expression and posture in the video clues, along with the formal and neatly arranged setting of the environment, we can infer that the man may be in a state of high pressure or negative emotions. The sentence might be his evaluation or reaction to someone or some situation. However, according to the analysis of an expert in the emotional domain based on the acoustic information provided, it is not possible to accurately predict the man's's emotional state just from the given audio cues. Therefore, we cannot determine the specific emotional state this sentence expresses.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 79. samplenew3_00059379｜gain｜ΔF1 +0.133333

gold：anger, dissatisfaction, frustration

query字幕：Prevent me from applying for the major I like.

源标注描述：In the text, caption content: "Preventing me from pursuing my preferred major." This phrase might represent an emotional state expressed by a male in Asia within a video. Based on the visual clues depicting him staring into space and being deeply thoughtful, as well as the audio clues describing his voice trembling and speech being fast, we can infer that this sentence might carry emotions of anger, frustration, or dissatisfaction. He might be complaining or expressing discontent over some hindrance or limitation, possibly related to wanting to pursue his preferred major. Therefore, this sentence reflects his emotional state and inner conflict.

off原始输出：The character's emotional state is anger, frustration, disappointment.

retrieval原始输出：The character's emotional state is anger, frustration.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, disappointment, frustration|0.666667|2|1|1|
|retrieval|anger, frustration|0.800000|2|0|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.800000，差值+0.133333。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：disappointment。

gate：0.120048597；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00050325

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, enthusiasm, expectation, love, positive mood, satisfaction
- 与query gold精确词面重合：∅
- 字幕：I want to be a good chef and cook delicious food for my mom so that she can also be healthy.
- 描述：In the text, the caption reads: "I want to be a good cook, I want to make delicious food for my mom so she can stay healthy too." This sentence conveys the boy's's aspirations and objectives, his desire to become a proficient chef and prepare tasty meals for his mother in order to ensure her well-being. Given the enthusiastic tone and high pitch of the voice as described in the audio clues, and the relaxed posture and calm expression shown in the video clues, we can infer that this statement expresses the boy's's expectations and enthusiasm for his future, along with his concern and love for his mother. This alignss with the overall positive mood and satisfaction that the boy demonstrates.

### 近邻2：samplenew3_00061768

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, scared, tension, timid
- 与query gold精确词面重合：∅
- 字幕：I admit it, I'm scared.
- 描述：In the text, the caption reads: "I'll just admit it, I'm just scared." This sentence could be a self-assessment or response from a young person to themselves. Given the character's voice in the audio cues is tense, shaky, and fast-paced, and the facial expressions of the young person in the video appear surprised and confused, we can infer that this statement might carry an air of tension and anxiety. Therefore, this sentence might be a young person admitting to feeling scared (afraid or timid) when facing a challenge or stress, which alignss with their overall display of tension and anxiety.

### 近邻3：samplenew3_00072413

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：Auntie, hello. I want to ask where Mr. Lin, who lives upstairs in room 301, has gone.
- 描述：In the text, the caption reads: "Hello aunt, I was wondering where's Teacher Lin from Apartment 301 upstairs has gone." This statement indicates the lady's inquiry about Teacher Lin. Given the video clues such as the lady's's active listening and her body language that shows concentration, and the audio hints of an individual speaking calmly and in a relaxed manner, we can infer that the lady's's curiosity about Teacher Lin's whereabouts might be out of normal interest or work-related needs. Therefore, this sentence does not carry any obvious emotional undertones, but is rather an objective query.

### 近邻4：samplenew3_00088908

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, uncertainty
- 与query gold精确词面重合：∅
- 字幕：I'm afraid it's not my mom who's stable.
- 描述：In the text, the caption reads: "It's probably not my mom who's stable." This sentence could be spoken by a young person on the phone. Based on the tremble and hesitation in the speaker's's voice as described in the audio clues, as well as the video clues showing the young person deeply engaged in the conversation with their phone pressed to their ear, we can infer that this statement might have been made by the young person when facing some tense or anxious situation. The sentence might suggest their concern or uncertainty about someone or something, which alignss with the inference that the individual is experiencing strong emotions based on the audio clues.

### 近邻5：samplenew3_00002681

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：The master means that Fengzhi is now in Jin Siyu's hands.
- 描述：In the text, the caption reads: "Master's intention is to honor it as currently in Jin Siyu's possession." Given the audio clues, where the speaker uses a monotonous tone and a flat pitch with no inflection or emotion, and at a moderate pace, we can infer that this statement is conveyed in a calm and objective manner. Additionally, the video clues show the person with their eyes closed, head slightly tilted, conveying a sense of tranquility and serenity. Thus, this sentence might be describing or discussing someone's situation being in Jin Siyu's hands, without any apparent emotional connotations.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 80. samplenew3_00079563｜gain｜ΔF1 +0.133333

gold：disappointment, remorse, sadness

query字幕：I should have known that I don't have any place in your heart.

源标注描述：In the text, the caption reads: "I should have realized I had no place in your heart." This sentence might be a form of self-reflection or self-doubt from a woman towards another person. Given the audio clues describing the personal voice as trembling, with a soft and hesitant tone, and the video clues showing the woman expressing happiness and positive emotions, we can infer that this sentence carries feelings of disappointment, remorse, or sadness. The woman might have come to realize at that moment that she is not considered important in the other person's's heart, which could lead to feelings of disappointment and dissatisfaction.

off原始输出：The character's emotional state is disappointment, guilt, sadness.

retrieval原始输出：The character's emotional state is disappointment, sadness.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|disappointment, guilt, sadness|0.666667|2|1|1|
|retrieval|disappointment, sadness|0.800000|2|0|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.800000，差值+0.133333。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：guilt。

gate：0.119946755；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00099723

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, excitement, positive
- 与query gold精确词面重合：∅
- 字幕：Okay, I'll drink for the Emperor's prosperity.
- 描述：In the text, the subtitle content says, "Okay, I'll drink for the Emperor's Longzi." This sentence may be the speaker's response or decision regarding a person or an event. Based on the audio clues describing the speaker's high-pitched and clear voice, relatively fast speech rate, confident and decisive tone, as well as the complex emotional mix displayed by the woman in the video, including surprise, nervousness, and fear, we can infer that this sentence may carry a positive, excited, and confident emotion. Therefore, this sentence may be the speaker's positive response or decision to an important event or decision, aligning with the overall complex emotions exhibited by the woman.

### 近邻2：samplenew3_00043218

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipatory, encouragement, excitement, motivated
- 与query gold精确词面重合：∅
- 字幕：How about thinking about how to follow up on our success?
- 描述：In the text, the subtitle says, "Think about how to seize the opportunity." This sentence may be the individual's suggestion or reflection on a situation or problem. Based on the description of the mixed emotion of excitement and anticipation in the audio clues, as well as the woman's confused expression and calm body language in the video clues, we can infer that this sentence may be the individual's thoughts on how to maintain motivation and pursue more success or progress in the context of excitement and anticipation. Therefore, this sentence may be a positive suggestion or encouragement that aligns with the overall display of excitement and anticipation by the individual.

### 近邻3：samplenew3_00085986

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration
- 与query gold精确词面重合：∅
- 字幕：He dared to hide from me and spread the news that the emperor has arrived.
- 描述：In the text, the subtitle reads: "He actually dared to hide from me that the emperor has arrived." This sentence may be a reproach or dissatisfaction from the female speaker towards the male speaker. Based on the description of the female speaker's voice tone and intensity increasing in the audio clues, as well as the male speaker's voice tone and intensity noticeably decreasing, we can infer that the female speaker may be experiencing strong negative emotions such as anger or frustration. Therefore, this sentence may be the female speaker expressing her dissatisfaction or reproach towards the male speaker for hiding the fact that the emperor has arrived.

### 近邻4：samplenew3_00069224

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, confidence, excitement, joy, pride
- 与query gold精确词面重合：∅
- 字幕：Sister, you won.
- 描述：In the text, caption content: "Sister, you won." This phrase might be another person's's evaluation or response to a lady. Given the speaker's voice tone is high in the audio cues, it suggests they may be experiencing a positive emotion such as excitement or joy. The speaker's's voice is clear and distinct, indicating they feel confident and are able to control their emotions. Simultaneously, based on the video cues where the lady is smiling and fully engaged in the discussion, along with her facial expressions and body language displaying an upbeat mood state, we can infer that this phrase may be an expression of praise or admiration, aligning with the lady's overall positive emotional display.

### 近邻5：samplenew3_00113470

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：curiosity, excitement, happiness
- 与query gold精确词面重合：∅
- 字幕：This Yilan flower is so enchanting, what would happen if it meets the fragrance in the E Li tent?
- 描述：In the text, the caption reads: "This elegant beauty of the orchid evokes emotion, what if it were to encounter the fragrance of the Ngali pavilion." Given the individual's voice in the audio clue has a tremble, indicating they is experiencing intense emotions, and the higher pitch of the voice suggests they is experiencing positive feelings, combined with the video clue showing a woman dressed in traditional Asian attire with a facial expression that seems to be a mix of curiosity and anticipation, we can infer that this sentence might be her praise or anticipation for something beautiful or evocative, expressing her excitement and state of happiness in that emotional context.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 81. samplenew3_00017876｜gain｜ΔF1 +0.133333

gold：anger, dissatisfaction, unhappiness

query字幕：Zhou Yu should not have led these people.

源标注描述：In the text, the subtitle reads, "Zhou Yu should not have led these people." This sentence may be an evaluation or reaction from the speaker towards Zhou Yu. Based on the audio clues describing the speaker's voice as filled with tension and urgency, a forceful and aggressive tone, and a higher pitch, we can infer that this sentence may carry a sense of anger or dissatisfaction. The speaker may be unhappy with Zhou Yu's actions or decisions, believing that he should not have led these people or made certain choices. Therefore, this sentence expresses the speaker's negative and dissatisfied emotions.

off原始输出：The character's emotional state is dissatisfaction, disappointment, anger.

retrieval原始输出：The character's emotional state is anger, dissatisfaction.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, disappointment, dissatisfaction|0.666667|2|1|1|
|retrieval|anger, dissatisfaction|0.800000|2|0|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为0.800000，差值+0.133333。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：disappointment。

gate：0.120006457；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00070210

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, conflicted, confusion, disappointment, perplexed, tension
- 与query gold精确词面重合：anger
- 字幕：I am torn between two sides.
- 描述：In the text, the caption reads: "I am caught between a rock and a hard place." This sentence might be a form of self-expression or inner monologue for a man in a video. Given the audio cues, such as signs of tension, anxiety, disappointment, or anger in his voice, and visual clues like the man's's facial expressions and body language during moments of deep thought or self-reflection, we can infer that this phrase could be the man's expressing his inner conflict and confusion when faced with two or more difficult choices or conflicts. The statement indicates that the man may feel perplexed and at a loss, unable to make a clear decision or choice.

### 近邻2：samplenew3_00075586

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, contemplation, fear, profound, puzzled, spiritual, tension, unease
- 与query gold精确词面重合：∅
- 字幕：There is something unusual about this Cao Cao. He has always been fond of young girls and withered flowers.
- 描述：In the text, caption content: "This Cao Cao has something peculiar, he's always been a beauty turned into a withereded flower." Based on the video clues such as the man's's serious expression, his closed eyes, and the dim room and candlelight background, it can be inferred that he is experiencing a profound, contemplative, or spiritual emotional state. The mention of "Cao Cao having something peculiar" in the caption suggests that he is puzzled or uneasy about Cao Cao's actions or state. Considering the audio clues where the description of trembling voice and slower pace, it can be deduced that he might be experiencing fear, anxiety, or tension. Therefore, the evaluation in the caption content could possibly reflect his concern or unease about Cao Cao's actions or state.

### 近邻3：samplenew3_00058127

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, focused, seriousness, tension
- 与query gold精确词面重合：∅
- 字幕：He wishes the young master could be absent.
- 描述：In the text, the subtitle content says, "He most hopes that the young master is not present." This sentence may be the man's expectation or hope for someone or a certain situation. Based on the description of a male voice with a sense of urgency and determination in the audio clues, as well as the serious expression and focused body language of the man in the video clues, we can infer that this sentence may carry an anxious or tense emotion. The man may hope that someone or a certain situation does not appear because he believes that this person or situation would interfere or hinder the task or situation he is engaged in. Therefore, this sentence expresses the man's expectation and hope, aligning with the overall serious and focused emotion he displays.

### 近邻4：samplenew3_00072873

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：enthusiasm, excitement, positive
- 与query gold精确词面重合：∅
- 字幕：Please take me there quickly, sir.
- 描述：In the text, the subtitle content says, "Please take me there quickly, sir." This sentence may be a man's request or invitation to someone or something. Based on the fast-paced and energetic voice described in the audio cues, as well as the man's smiling and funny expressions in the video cues, we can infer that this sentence may have an excited or enthusiastic tone. Therefore, this sentence may be the man joking or teasing, expressing his positive attitude towards someone or something.

### 近邻5：samplenew3_00064236

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, helplessness, stress, urgency, worry
- 与query gold精确词面重合：∅
- 字幕：It will cause resistance from Liu Biao's former subordinates.
- 描述：In the text, the caption states: "It will provoke resistance from Liu Biao's former forces." Given the individual's voice trembling, speaking quickly according to audio clues, and their relaxed or contemplative posture and facial expressions in the video hints, we can infer that this sentence might be an expression of the individual's concern or worry about a challenging situation or traumatic event. The individual may feel urgency, stress, and helplessness, hence foreseeing that this situation could lead to resistance from Liu Biao's former forces. This sentence reflects the individual's's negative emotions and worries, aligning with the emotional state suggested by both audio and video clues.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 82. samplenew3_00005647｜gain｜ΔF1 +0.138889

gold：anxiety, confusion, lacking confidence, tension, uncertainty

query字幕：I really don't know what the intention of the elder brother is, so please tell me, elder brother.

源标注描述：In the text, the subtitle reads: "Subject Brother, I'm truly at a loss as to what King Brother intends. Please enlighten me." This sentence might be a response or query from one speaker to another. Given the audio cues describing the speaker feeling anxious, tense, and lacking confidence in themselves, and the video cues suggesting that the person in costume might feel somewhat disoriented, we can infer that this phrase carries an element of confusion and uncertainty. Therefore, this sentence could be the speaker requestingfully asking for clarification or explanation of something they doesn't understand, which alignss with the costume person's portrayal.

off原始输出：The character's emotional state is anxious, tense, lacking confidence.

retrieval原始输出：The character's emotional state is anxious, tense, confused, uncertain.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, lacking confidence, tension|0.750000|3|0|2|
|retrieval|anxiety, confusion, tension, uncertainty|0.888889|4|0|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.750000变为0.888889，差值+0.138889。
- TP变化+1，FP变化+0，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：lacking confidence。
- 相对off新增命中的gold标签：confusion, uncertainty。

gate：0.120072775；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00063277

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：empathy, loyalty, pressure, respect, tension, understanding
- 与query gold精确词面重合：tension
- 字幕：Your child can better understand the thoughts of the father
- 描述：In the text, the caption reads: "Son can better empathize with Father's thoughts." This sentence might be a response or expression from a male to some superior or elder. Given the video clues showing the man in a state of concentration and deep thought, as well as his posture and demeanor projecting authority and confidence, we can infer that this sentence could be an expression of respect and loyalty towards a superior or elder. Additionally, based on the audio clues describing the speaker as having a sense of urgency and tension, possibly feeling anxious or under pressure, we can speculate that the man may have been responding with a degree of tension and pressure, but still maintaining respect and loyalty towards his superior or elder. Therefore, this sentence might be the man expressing his understanding and empathy towards the thoughts of his superior or elder.

### 近邻2：samplenew3_00098257

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：composure, confidence, determination, tranquility
- 与query gold精确词面重合：∅
- 字幕：This king violates the doctor's ability to have a righteous heart and righteous behavior.
- 描述：In the text, the subtitle content says, "This king violates the doctor's ability to have a righteous heart and righteous behavior." Based on the calm and composed attitude displayed by the man in the video, as well as the peaceful and serene atmosphere in the environment, it can be inferred that this person is experiencing a state of tranquility and composure. He shows a certain level of confidence and respect, which aligns with his body language and facial expressions. Based on the audio clue of the individual's voice having a sense of urgency, speaking quickly and with a sense of importance, and a firm and confident tone of voice, it can be inferred that the individual is feeling determination and confidence. The individual may feel positive and determined to achieve goals or overcome obstacles. By analyzing the video and audio clues together, it can be inferred that this person's emotional state is one of determination and confidence.

### 近邻3：samplenew3_00049589

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concentration, deep thought, humor, relief, tension
- 与query gold精确词面重合：anxiety, tension
- 字幕：It shouldn't be for training this king, right?
- 描述：In the text, caption content: "Not for training this king, right?" This sentence might be what a man says while in deep thought or concentration. Given the video clues such as the serious expression on the man's's face and the solemn atmosphere of the environment, as well as audio clues describing the man feeling anxious or tense, and full of energetic emotions, we can infer that this statement might carry a tone of wit or humor. Therefore, this sentence could be the man's's way of relieving tension or making fun of himself while in a state of contemplation.

### 近邻4：samplenew3_00001997

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：admiration, capability, confidence, dedication, seriousness
- 与query gold精确词面重合：∅
- 字幕：Yue Shang Gong is so confident.
- 描述：In the text, the caption reads: "The palace lady is so confident." This phrase could be a man's's evaluation or response to a woman. Given the various emotional cues described in the audio context, including feelings of tension and subtle excitement, as well as the serious expression on the man's's face and the woman's attire suggesting their seriousness about the situation, we can infer that this phrase might be a compliment or praise from the man to the woman. The man may have observed that she showed confidence and capability in her performance during a task or activity, hence his acknowledgment and admiration for her confidence. This alignss with the overall focused, serious, and fully dedicated emotional atmosphere portrayed by both men and women.

### 近邻5：samplenew3_00106993

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, frustration
- 与query gold精确词面重合：anxiety
- 字幕：Your general is the only one who, besides being loyal and obedient to the lord, obeys the imperial decree.
- 描述：In the text, the caption reads: "Your general is under the imperial edict to serve loyallyly besides your lord." This sentence might be an evaluation of someone or a reminder of their responsibilities and duties. Given the speaker's's elevated and agitated tone as described in the audio cues, along with the tense, angry, and frustrated sounds in the audio, we can infer that the sentence might carry a tone of blame or warning. Therefore, this sentence could be criticizing or reminding someone about the importance of loyalty and service to the sovereign, which alignss with the overall expression of anger, frustration, and anxiety from the speakerer.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 83. samplenew3_00042172｜gain｜ΔF1 +0.142857

gold：anxiety, appreciation, calm, discouraged, encouragement, focused, impatience, inner peace, satisfaction, tension

query字幕：the air of holding the crown

源标注描述：In the text, caption content: "Grip of the Aura" could be a line for a woman to a man. Based on the role's using a high and fast pitch tone of voice, possibly feeling anxious or tense, and a stammering way of speaking, indicating they may feel impatient or discouraged. Coupled with video clues showing the woman's calm and focused expression, fully immersed in the conversation, and her attention on the man suggests she may have experienced inner peace and satisfaction. Therefore, this phrase could be the woman's encouragement or appreciation for the man, indicating he is performing excellently or confidently in the conversation. This alignss with the overall serene and aware emotional state the woman displays.

off原始输出：The character's emotional state is confidence, determination, happiness.

retrieval原始输出：The character's emotional state is confidence, decisiveness, happiness, encouragement.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|confidence, determination, happiness|0.000000|0|3|10|
|retrieval|confidence, decisiveness, encouragement, happiness|0.142857|1|3|9|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.000000变为0.142857，差值+0.142857。
- TP变化+1，FP变化+0，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：decisiveness。
- 相对off新增命中的gold标签：encouragement。
- 相对off移除未精确匹配gold的标签：determination。

gate：0.119922049；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00037507

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, tension
- 与query gold精确词面重合：anxiety, tension
- 字幕：The punishment law has been abolished.
- 描述：In the text, caption content: "Punishment has reached its limit." This sentence might be describing the enforcement situation of some laws or regulations by the speaker. Considering the slight tremble in the speaker's's voice, the tone suggesting a sense of helplessness or heavy pressure, and the video clues showing the woman's curiosity and interest, we can infer that this statement might carry a tense or anxious tone. Therefore, this sentence might describe severe legal enforcement or punishment measures, which would be consistent with the overall emotional state of the speaker.

### 近邻2：samplenew3_00049926

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：curiosity, joking, pleased, relaxation, teasing
- 与query gold精确词面重合：∅
- 字幕：I still want to add a flourish.
- 描述：In the text, caption content: "I'll add one more thing though." This sentence might be a response to some suggestion or request made by the speaker. Given the audio cues where describe the speaker speaking casually and seemingly in good spirits, as well as the video cues showing the woman's expression of curiosity and pleasure along with her relaxed body language, we can infer that the tone of this statement might be light-hearted or humorous. Therefore, this phrase could be an expression of joking or teasing nature, which would fit in well with the overall sense of curiosity, pleasure, and relaxation the woman exhibits.

### 近邻3：samplenew3_00052358

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：engaged, enthusiasm, excitement, favorable view, happiness, positive
- 与query gold精确词面重合：∅
- 字幕：Our family Li Tianran is still very useful, right?
- 描述：In the text, the subtitle reads: "Our Li Tianyuan is still quite useful, huh?" Based on the video clues, where a woman's posture and facial expressions while focused on her work, and the man's's thoughtful state with his hands in prayer, it can be inferred that both individuals in the video are deeply engaged in their tasks. The audio cues describe a person experiencing a series of positive emotions, such as happiness, excitement, and enthusiasm, with an energetic and optimistic tone. This suggests that they person has a favorable view of "Li Tianyuan," whether as a person or something else. Therefore, this phrase could possibly be a compliment or affirmation from the woman to the man, expressing recognition of the value and role "Li Tianyuan" plays in his work.

### 近邻4：samplenew3_00081105

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：disappointment, frustration, unhappiness
- 与query gold精确词面重合：∅
- 字幕：At least others dare to be themselves, what about you?
- 描述：In the text, caption reads: "At least others dare to be themselves, what about you?" This phrase could be the young woman's evaluation or reaction to someone or a situation. Based on the audio clues, her voice is high-pitched, fast-paced, and loud, suggesting it might carry an element of excitement or tension. Considering the video clues showing her with an unhappy expression and body language, along with the described supermarket setting that might provoke negative feelings, this phrase could be her expression of dissatisfaction or frustration towards someone or a situation. Therefore, it may come across as critical or blaming, aligning with her overall mood of unhappiness or disappointment.

### 近邻5：samplenew3_00023417

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction, irritation
- 与query gold精确词面重合：∅
- 字幕：You also make fun of me.
- 描述：In the text, with subtitles: "You're laughing at me too," this phrase might be a response from a female character to someone. Considering the audio cues that describe an individual with a sharp tone, a sense of urgency, and an emotional state suggesting anger or irritation, and the video clues showing the woman's focused and determined demeanor, we can infer that the statement might be infused with anger or dissatisfaction. The woman may feel that someone is laughing at her or mocking her, leading her to respond in an agitated manner. This contrasts with the woman's's portrayed focused and resolute emotions in the video.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 84. samplenew3_00060221｜gain｜ΔF1 +0.155556

gold：anxiety, depression, introspective, irritation, philosophical, stress

query字幕：Life is actually a practice of death.

源标注描述：In the text, the caption reads: "Life is essentially a practice of death." This statement might be reflectinging on or expressing one's perspective or feelings within the video. Based on the video's depiction where he sits in a red chair, holding a book, his gaze focused on the pages, and surrounded by a serene and soothing environment, we can infer that he might be engrossed in reading a book about philosophy or profound contemplation. The phrase embodies an introspective view on life, possibly infused with a deep and philosophical emotional state. Considering the audio description which portrays an individual experiencing a high level of stress and anxiety, coupled with feelings of depression and irritability, we can speculate that this statement might reflect a pessimistic attitude towards life, possibly stemming from the challenges he currently faces.

off原始输出：The character's emotional state is contemplative, philosophical, introspective.

retrieval原始输出：The character's emotional state is contemplative, philosophical, stressed, anxious.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|contemplation, introspective, philosophical|0.444444|2|1|4|
|retrieval|anxiety, contemplation, philosophical, stress|0.600000|3|1|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.444444变为0.600000，差值+0.155556。
- TP变化+1，FP变化+0，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：introspective。
- 相对off新增命中的gold标签：anxiety, stress。

gate：0.119980291；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00051495

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, criticism, mockery, tension
- 与query gold精确词面重合：anxiety
- 字幕：This young master Zhao Lichun is too ostentatious.
- 描述：In the text, caption content: "This son of Zhao Lichun is too show-big-for-his-pants legs." This sentence might be an evaluation or reaction to a man in the video. Based on the audio cues describing an individual experiencing a higher level of anxiety or tension and attempting to control their emotions, along with the serious and focused expression of the man in the video, we can infer that this statement might carry a critical or negative tone. Therefore, this sentence might be a criticism or mocking of the man's overly assertive or conceited behavior, which contradicts the serious and focused emotion he displays.

### 近邻2：samplenew3_00038367

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, challenging, questioning, tension
- 与query gold精确词面重合：anxiety
- 字幕：Is the most difficult not popular?
- 描述：In the text, caption content: "Is it not so popular that it's hardest?" This sentence could be a man's's evaluation or response to his own thoughts or reflections. Given the man's's serious and focused expression in the video clues, as well as an individual feeling anxious or tense in the audio clues with a slightly elevated tone of voice, we can infer that this statement might carry a questioning or challenging tone. The man may be contemplating some difficult or unpopular issues, and this sentence could be his evaluation or response to his own thoughts.

### 近邻3：samplenew3_00098185

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：curiosity, dissatisfaction, frustration, puzzled
- 与query gold精确词面重合：∅
- 字幕：What do you mean by "not Sun Dong"?
- 描述：In the text, the subtitle reads, "What do you mean, Mr. Sun?" Based on the video clues of the man in the blue jacket displaying complex emotions including curiosity, confusion, and frustration, as well as his focused gaze and fidgeting with his hands, it can be inferred that he may be puzzled and dissatisfied with the other person's words or actions. The questioning and dissatisfied tone in this subtitle further supports this inference. Therefore, this sentence may be the man in the blue jacket expressing his questioning or dissatisfaction towards the other person.

### 近邻4：samplenew3_00039825

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, determination, humor
- 与query gold精确词面重合：∅
- 字幕：Give me another chance, I believe I can squeeze out something from myself.
- 描述：In the text, the caption reads: "Give me another try, I reckon I can wring something out of it." This sentence might be spoken by a man addressing a camera. Based on the speaker's's calm and restrained tone as described in the audio cues, and the man's's facial expressions and body language displayed in the video, we can infer that the statement might be delivered with a firm and confident demeanor. The speaker may be expressing their determination and confidence in tackling a task or challenge, while possibly also injecting a hint of humor, aligning with the complex emotional state the man exhibits overall.

### 近邻5：samplenew3_00022048

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, concern, frustration, overwhelm, sadness, under immense pressure, unease
- 与query gold精确词面重合：∅
- 字幕：I'm worried that my body can't hold on.
- 描述：In the text, the caption reads: "I'm worried my body can't take it." This sentence might be spoken by a man in a conversation. Given the individual's experiences described through audio cues, which include negative emotions such as sadness, anger, or frustration, along with feelings of being overwhelmed or under immense pressure, it can be inferred that this sentence expresses the man's concern and unease about his physical condition. This alignss with the video hints showing the man's sad facial expressions and negative emotions, suggesting he may be discussing or contemplating issues related to health or the body.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 85. samplenew3_00108740｜gain｜ΔF1 +0.155556

gold：anger, disappointment, frustration, helplessness, melancholy, powerlessness, sense of defeat

query字幕：We definitely can't accomplish this task just by the two of us.

源标注描述：In the text, the caption reads: "Without both of our powers, we definitely can't pull this off." Based on the speaker's's evident frustration, disappointment, anger, sense of defeat, and helplessness as described through audio cues, along with the video showing the girl in deep thought, self-reflection, and possibly displaying signs of melancholy, we can infer that this statement might be an evaluation or response from the girl about herself or her collaborator. This sentence conveys a sense of powerlessness and defeat, suggesting that the girl believes she and the other person together cannot accomplish something, implying they might need assistance from others or additional resources. This alignss with the overall impression of the girl being deeply thoughtful and possibly feeling melancholic.

off原始输出：The character's emotional state is disappointment, helplessness.

retrieval原始输出：The character's emotional state is frustration, disappointment, helplessness.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|disappointment, helplessness|0.444444|2|0|5|
|retrieval|disappointment, frustration, helplessness|0.600000|3|0|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.444444变为0.600000，差值+0.155556。
- TP变化+1，FP变化+0，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：frustration。

gate：0.120043263；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00078238

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confusion, defensiveness, resentment
- 与query gold精确词面重合：∅
- 字幕：Why are you angry? This can only explain this magazine.
- 描述：In the text, the caption reads: "Why are you upset with me?" This phrase could be a woman's response or explanation to someone. Given the audio cues that describe the speaker's as having an aggressive and hostile tone, and the woman displaying a serious expression and body language in the video clues, we can infer that this statement might carry a tone of resignation or confusion. The woman might be responding to the other person's's anger or frustration, expressing her innocence or lack of understanding. Therefore, this sentence could be the woman's attempt to calm down the other person, or to explain her position.

### 近邻2：samplenew3_00014812

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：joy, satisfaction
- 与query gold精确词面重合：∅
- 字幕：
- 描述：In the text, caption content: "Think of her as our family's sanitation ambassador, overseeing our household cleanliness tasks, and others." This sentence might be a comment or reaction from a young person about a young woman. Given the context provided by the audio clues, where the characters speaks in a clear and confident tone, and the video clues show both the young man and woman smiling and laughing, it can be inferred that the sentence may carry a tone of praise or encouragement. Therefore, this sentence could be interpreted as a young person complimenting a young woman for her performance in household hygiene work, and hoping she continues to do well. This alignss with the joyful and satisfied emotions displayed by both the young man and woman in the video.

### 近邻3：samplenew3_00062150

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：agitation, concern, defense
- 与query gold精确词面重合：∅
- 字幕：I'll tell you, it's not easy for him to make money. How many calls does he have to answer in a day?
- 描述：In the text, the caption reads: "I'm telling you, show you care, he earns money hard, how many calls does he have to take in a day." This sentence might be a woman's explanation or defense for someone. Given the audio clues, where the woman speaks quickly and in a high-pitched voice, emphasizing certain words and phrases, and the video clues showing the woman with a serious and focused demeanor, we can infer that this statement might carry an emotional tone of agitation or defense. The woman might be defending or explaining a situation for someone, she seems very concerned about this issue and wishes for the other person to understand.

### 近邻4：samplenew3_00011856

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, frustration, helplessness
- 与query gold精确词面重合：anger, frustration, helplessness
- 字幕：This time it's completely hopeless. My dad also gave me a command, saying that we must celebrate the Mid-Autumn Festival together as a family.
- 描述：In the text, the subtitle content says, "This time it's completely hopeless, my dad has also given me an order, saying that we must celebrate the Mid-Autumn Festival together as a family." Based on the description of the individual's tense and strained voice, the sense of urgency and despair in their tone, and the description of negative emotions in the audio clues, it can be inferred that this sentence may be the individual expressing their distress and dissatisfaction. The individual may feel frustrated, angry, and helpless because of their father's order, and they may not want to celebrate the Mid-Autumn Festival with the whole family. The negative emotions in this sentence align with the negative emotions the individual in the audio is experiencing.

### 近邻5：samplenew3_00050162

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：encouragement, expectation, positive mood
- 与query gold精确词面重合：∅
- 字幕：Only when you come, the three of us can dig up this mine.
- 描述：In the text, the subtitle reads, "Only you can help us three to mine this ore." This sentence may be an evaluation or expectation of someone. Based on the visual clue of the woman's active listening and focused expression in the video, as well as the audio clue of the individual possibly experiencing a range of negative emotions, it can be inferred that this sentence may be an encouragement or expectation, hoping that someone can participate in a task or work to solve the current dilemma or problem. This sentence may carry a tone of expectation and encouragement, aligning with the overall positive mood displayed by the woman.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 86. samplenew3_00012363｜gain｜ΔF1 +0.166667

gold：concern, excitement, tension, unease

query字幕：I am no longer scared by the atmosphere of the Yue family.

源标注描述：In the text, the caption reads: "Impressed by that Qi from Yue's side." This sentence could be a man's evaluation or reaction to someone or something. Given the audio cues with its high pitch, rapid pace, and energetic tone, along with the video clues showing the man with a thoughtful and possibly melancholic facial expression, we can infer that the sentence might carry a sense of tension, anxiety, and excitement. Therefore, this sentence might express the man's's feelings of being tense and excited about something, possibly also accompanied by some concern or unease.

off原始输出：The character's emotional state is excited, enthusiastic.

retrieval原始输出：The character's emotional state is excited, enthusiastic, nervous, tense.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|enthusiasm, excitement|0.333333|1|1|3|
|retrieval|enthusiasm, excitement, nervousness, tension|0.500000|2|2|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.333333变为0.500000，差值+0.166667。
- TP变化+1，FP变化+1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：nervousness。
- 相对off新增命中的gold标签：tension。

gate：0.120089017；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": [{"prediction_label": "nervousness", "unmatched_gold_label": "concern"}, {"prediction_label": "nervousness", "unmatched_gold_label": "unease"}]}

实际5近邻证据：

### 近邻1：samplenew3_00051129

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：complaint, contemplation, dissatisfaction, frustration, insecurity, irritation
- 与query gold精确词面重合：∅
- 字幕：How did it become that I owe you a game of chess?
- 描述：In the text, the caption reads: "How did it become me owing you a game?" This phrase might be a reaction or response from a young person to another individual. Given the described mood of frustration and irritation in the audio cues, as well as the young person's feelings of insecurity and contemplation shown in the video cues, we can infer that the statement might carry a tone of dissatisfaction or complaint. It could be the young person's reprimand or rebuttal towards another, expressing their dissatisfaction or misunderstanding with the current situation.

### 近邻2：samplenew3_00086855

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：happiness, positive
- 与query gold精确词面重合：∅
- 字幕：He ranks first in the network.
- 描述：In the text, the caption reads: "He's ranked number one on the internet." This phrase could be a youth's evaluation or commentary on someone or something. Given the audio cues with a lively and positive tone, as well as the video clues showing the young person with a smile and an overall positive mood state, we can infer that this sentence might be praising or complimenting someone for achieving first place online. This alignss with the young person's overall display of a positive mood.

### 近邻3：samplenew3_00009301

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, fear, worry
- 与query gold精确词面重合：concern
- 字幕：What if one day he needs money again?
- 描述：In the text, the caption reads: "Who knows if he might need money someday." This phrase could be an expression of concern or worry from one person to another. Given the individual's is experiencing strong feelings of fear or anxiety as described by audio cues, and without clear emotional cues from the video such as facial expressions and body language, we can infer that the tone might be one of concern or unease. Therefore, this sentence might be expressing a worry or concern about a situation where someone may need money again.

### 近邻4：samplenew3_00007427

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：impatience, indifference
- 与query gold精确词面重合：∅
- 字幕：What does it have to do with me?
- 描述：In the text, the caption reads: "What does it matter to me?" This phrase could be a response from a young person to someone or something. Given the audio cues that describe an individual with a trembling voice, a monotone tone, and the video hints showing a young person displaying thoughtful, serious, and introspective emotions, we can infer that this sentence might be spoken with an air of impatience or indifference. Therefore, this statement may serve as a response in a conversation, expressing a young person's's lack of concern or interest in someone or something.

### 近邻5：samplenew3_00074227

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, frustration, tension
- 与query gold精确词面重合：tension
- 字幕：The key has been obtained, what is the password?
- 描述：In the text, the caption reads: "The key is in hand, what's the password?" This sentence could be a man asking either asking to or confirming information about a password. Given the man's serious expression in the video hints and the described tense, anxious, frustrated, and angry emotions in the audio clues, we can infer that this phrase might be delivered with a sense of urgency and anxiety. Therefore, this sentence might be a man in a critical situation, urgently seeking password information, and his feelings of tension and anxiety reflect the importance and pressure he places on this issue.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 87. samplenew3_00020194｜gain｜ΔF1 +0.194444

gold：anxiety, disappointment, dissatisfaction, frustration, stress, tension

query字幕：

源标注描述：In the text, the caption reads: "Say it once and you'll remember it." This might be something a woman says to someone nearby. Given the woman's concerned facial expressions and body language in the video hints, along with the high-pitched tone of her voice and the slight tremble in her speech in the audio clues, we can infer that this phrase might be said with an air of impatience or stress. The woman might feel anxious and tense as she is going through a difficult situation, and is possibly dissatisfied or disappointed with the person next to her for their memory. Therefore, this sentence could be the woman expressing her frustration and stress.

off原始输出：The character's emotional state is worry, anxiety.

retrieval原始输出：The character's emotional state is anxious, tense, worried.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, worry|0.250000|1|1|5|
|retrieval|anxiety, tension, worry|0.444444|2|1|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.250000变为0.444444，差值+0.194444。
- TP变化+1，FP变化+0，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：tension。

gate：0.120030485；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00053264

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, nervousness, suspicion
- 与query gold精确词面重合：anxiety
- 字幕：Liu Jie, has your scent changed?
- 描述：In the text, caption content: "Sis Liu, has your scent changed?" This sentence could be spoken by a female either to herself or in conversation. Based on the video hints showing the female's expression of surprise and frustration, along with her clenched fists and tense posture, it can be inferred that the sentence might carry a tone of suspicion or concern. Additionally, according to the audio clues describing a shaky voice and slightly faster pace, it can be speculated that the speaker may feel anxious and nervous. Therefore, this sentence might be a female expressing concern or questioning about changes in Sis Liu's scent, which alignss with her overall emotional state.

### 近邻2：samplenew3_00005607

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, loss, reluctance, worry
- 与query gold精确词面重合：anxiety
- 字幕：I haven't had time to be happy about finally growing up, and now it's all gone in an instant and I'm about to become someone else's.
- 描述：In the text, caption content: "It's been a long journey to grow up and haven't had a chance to be happy yet, this sudden departure is about to take flight, destined to become someone else's." This sentence might be a woman's reflection and concern for her child about to leave the family. Given the personal emotional state described in the audio clues as despair and hopelessness, along with the woman's tense expression and focused gaze in the video clue, we can infer that this sentence might carry a sense of loss and anxiety. The woman may be worried about her child's life and future after leaving, thus expressing her reluctance and worry about her child's departure.

### 近邻3：samplenew3_00037212

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, urgency
- 与query gold精确词面重合：anxiety
- 字幕：Can you help me take care of Tao Tao at home?
- 描述：In the text, the caption reads: "Can you help me look after TaoTao at home?" Based on the woman's perplexed expression in the video clues and the sense of urgency and desperation in her voice as described in the audio clues, we can infer that this sentence might be a way for the woman to request assistance or support from the other person. The woman may be facing some difficulty or challenge and needs the other person to take care of her child, TaoTao, at home. Such a request often comes with a sense of anxiety, concern, or urgency, which alignss with the emotional state described in the audio clues.

### 近邻4：samplenew3_00079418

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, excitement, happiness, surprise, tension
- 与query gold精确词面重合：anxiety, tension
- 字幕：I heard that it's a boy and a girl.
- 描述：In the text, caption: "I heard it might be one boy and one girl." Based on the visual clues in the video such as the woman's facial expressions and body language suggesting she may feel excited, happy, even slightly surprised, and her partner's being fully engaged in her and occasionally nodding along, this conversation can be inferred to possibly revolve around a family-related topic. The woman's mouth is agape, indicating she is passionately discussing the subject or sharing a story related to it. From the audio cues describing the person speaking in a high pitch voice, feeling anxious or tense, and the higher tone potentially indicating excitement or enthusiasm, we can deduce that the woman may be experiencing complex emotions while discussing this family topic, including excitement, anxiety, and tension.

### 近邻5：samplenew3_00115135

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：excitement, urgency
- 与query gold精确词面重合：∅
- 字幕：When these big wild wolves were about to eat the frog prince, they suddenly heard the princess in the castle screaming for help.
- 描述：In the text, the caption reads: "These big wolves were about to eat the frog prince when suddenly they heard the princess inside the castle screaming for help, 'Save me! Save me!'" This sentence describes a scene where the wolves are about to consume the frog prince but hear the princess's cries for assistance from within the castle. Given the audio clues that depict a high-pitched female voice and an agitated tone, as well as the visual cues of a woman's facial expressions and body language indicating with surprise and agitation, we can infer that this sentence might be a female describing a tense, exciting, or perilous situation. She might be portraying a character in the story or recounting it. Thus, this sentence conveys the female's's sense of urgency and excitement, which alignss with her overall expression and vocal inflection.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 88. samplenew3_00030999｜gain｜ΔF1 +0.200000

gold：pride, respect

query字幕：When I serve my king

源标注描述：In the text, the caption reads: "When serving my king," this sentence might be spoken by a female character in the video. Based on the clues from the video that show the female character dressed in elegant traditional attire, adorned with floral headdresses, and her body language exuding confidence and pride, we can infer that this sentence might describe her identity and role as a servant to the royal family. This sentence may carry an undertone of pride and respect, aligning well with the overall positive emotion portrayed by the female character.

off原始输出：The character's emotional state is loyalty, respect, pride.

retrieval原始输出：The character's emotional state is pride, respect.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|loyalty, pride, respect|0.800000|2|1|0|
|retrieval|pride, respect|1.000000|2|0|0|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.800000变为1.000000，差值+0.200000。
- TP变化+0，FP变化-1，FN变化+0。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off移除未精确匹配gold的标签：loyalty。

gate：0.120037027；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00046404

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：assertive, authoritative, composed, confidence, decisive
- 与query gold精确词面重合：∅
- 字幕：The decree left by the former king has already been delivered to all the ministers in the court, so there is no need for further delay from me in the palace.
- 描述：In the text, the subtitle reads: "The emperor's edicts have been conveyed to all the court officials, this palace shall not prolong the matter any further." This phrase could be part of a sentence spoken by a woman. Given the audio cues describing the woman's assertive tone, decisiveness, and firm stance, along with the visual clues showing her calm and composed demeanor, we can infer that this sentence might be part of her expressing her decision or announcing an important matter. The woman's tone and posture reflect her confidence and authority, which aligns with the overall serene emotional state portrayed.

### 近邻2：samplenew3_00047688

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, excitement, focused, nervousness, seriousness
- 与query gold精确词面重合：∅
- 字幕：Your vision needs to be broader, after all, you still have a long way to go.
- 描述：In the text, the subtitle reads, "You need to broaden your perspective, at least you still have a chance." This sentence may be the woman's advice or criticism to someone. Based on the woman's serious and confident expression in the video clues, as well as her calm and controlled body language, we can infer that this sentence may have a serious and calm tone. Additionally, based on the slight tremor in the individual's voice and the slightly faster speech rate in the audio clues, we can speculate that the individual may be feeling nervous and excited. Therefore, this sentence may be the woman giving advice to someone with a certain level of seriousness and nervousness, while also demonstrating her confidence and focus.

### 近邻3：samplenew3_00103433

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：disapproving, discontent, dismissive, indifference
- 与query gold精确词面重合：∅
- 字幕：He is just playing with you.
- 描述：In the text, the caption reads: "He's just stringing you along for fun." This phrase might be a woman's evaluation or commentary on someone. Considering the emotional fluctuations and changes described in the audio clues, as well as the woman's neutral facial expression and relaxed body language in the video, we can infer that this statement may carry an indifferent or dismissive tone. The woman might feel discontented or disapproving towards someone's behavior or attitude, thus using a mocking or condescending manner of expression.

### 近邻4：samplenew3_00013751

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, self-aware, tension
- 与query gold精确词面重合：∅
- 字幕：How do you see this looks old?
- 描述：In the text, caption content: "How does this make me look old?" This sentence might be a man's questioning or reflectinging on his age. Based on the hesitation and uncertainty in the personal voice described in the audio clues, as well as the trembling voice, we can infer that the sentence may carry an anxious or tense emotion. At the same time, the calm and composed body language of the woman in the video clues suggests her support for the man. Therefore, this sentence might be a manifestation of the man's's self-awareness about his age, while the presence of the woman gives him a sense of stability and support.

### 近邻5：samplenew3_00049260

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：indifference, nonchalant
- 与query gold精确词面重合：∅
- 字幕：There is nothing that cannot be said. I have no intention of returning to the state of Qin.
- 描述：In the text, the subtitle reads: "There is nothing else to say about not intending to return to the state of Qin." This sentence may be the woman's response to someone's question or an expression of her own thoughts. Based on the description of the speaker's monotone and emotionless tone in the audio clue, as well as the surprise and concern shown by the woman in the video clue, we can infer that this sentence may be delivered with a sense of indifference or nonchalance. Therefore, this sentence may not reflect the woman's true emotions, but rather a dismissive or indifferent attitude that contradicts the concern and vulnerability she displays overall.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 89. samplenew3_00082658｜gain｜ΔF1 +0.250000

gold：assertive, authoritative, confidence, passion, persuasive

query字幕：Whoever earns money supports the family and has the final say.

源标注描述：In the text, caption content: "Who earns it, who provides for the family, and who makes the decisions." This phrase could be spoken by a woman with a high-pitched, agitated tone. Given the audio cues described as the woman speaking rapidly, with a sense of urgency, and accompanied by upbeat, lively background music, we can infer that this statement might carry a strong persuasive and authoritative tone. Therefore, this sentence might be the woman emphasizing an important point or expressing her stance in a debate. In contrast to the video hints where the lady smiling, showing happiness and satisfaction, this phrase could be the lady passionately articulating her viewpoint or insisting on her rights, in line with her overall positive mood.

off原始输出：The character's emotional state is confident, firm, joyful.

retrieval原始输出：The character's emotional state is confident, authoritative, positive.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|confidence, firm, joy|0.250000|1|2|4|
|retrieval|authoritative, confidence, positive|0.500000|2|1|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.250000变为0.500000，差值+0.250000。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：positive。
- 相对off新增命中的gold标签：authoritative。
- 相对off移除未精确匹配gold的标签：firm, joy。

gate：0.119972259；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00078238

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confusion, defensiveness, resentment
- 与query gold精确词面重合：∅
- 字幕：Why are you angry? This can only explain this magazine.
- 描述：In the text, the caption reads: "Why are you upset with me?" This phrase could be a woman's response or explanation to someone. Given the audio cues that describe the speaker's as having an aggressive and hostile tone, and the woman displaying a serious expression and body language in the video clues, we can infer that this statement might carry a tone of resignation or confusion. The woman might be responding to the other person's's anger or frustration, expressing her innocence or lack of understanding. Therefore, this sentence could be the woman's attempt to calm down the other person, or to explain her position.

### 近邻2：samplenew3_00115576

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：joy, positive
- 与query gold精确词面重合：∅
- 字幕：Take a look at those children.
- 描述：In the text, the caption reads: "See those kids over there." This sentence might be a woman's evaluation or commentary on certain children or scene in the video frame. Based on the woman's facial expressions, body language, and the casual setting of the video clue, it can be inferred that her emotional state is positive and joyful. Therefore, this sentence could be the woman's observation and evaluation of the children, expressing her affection and appreciation for them.

### 近邻3：samplenew3_00094292

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：encouragement, support
- 与query gold精确词面重合：∅
- 字幕：Think about it carefully.
- 描述：In the text, the subtitle reads, "You should consider it carefully." This sentence may be the woman's advice or suggestion to someone. Based on the audio clue describing the individual speaking quickly and with a high pitch, as well as the video clue of the woman smiling and having a positive attitude, we can infer that this sentence may carry an encouraging or supportive tone. The woman's positive emotions and body language also support this inference. Therefore, this sentence may be the woman encouraging someone to carefully consider a certain issue or make a certain decision.

### 近邻4：samplenew3_00021720

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, dissatisfaction, excitement, nervousness, questioning
- 与query gold精确词面重合：∅
- 字幕：Why did he resign from this place in summer in the East China Sea for no reason?
- 描述：In the text, the subtitle content reads: "Why did he resign from this place?" Based on the serious facial expression and focused body language of the woman in the video clues, as well as the nervousness and energetic tone of the individual in the audio clues, we can infer that this sentence may be the woman discussing an important topic or expressing her dissatisfaction or questioning. Her serious facial expression and focused body language indicate that she is very concerned about this topic and may be expressing her dissatisfaction or questioning someone's resignation. The nervousness and energetic tone of the individual in the audio clues also support this inference, indicating that she may be discussing an important topic and feeling nervous and excited about it.

### 近邻5：samplenew3_00088295

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：expectant, happiness, joy, satisfaction
- 与query gold精确词面重合：∅
- 字幕：Let's eat together here today.
- 描述：In the text, the subtitle reads: "Having dinner together here today?" This sentence might be a female inviting or suggesting to someone off-camera to have dinner together. Given the video hints of the female's smiling and being in an upbeat mood, and the audio cues of an individual speaking at a higher pitch and with excitement, we can infer that this sentence expresses the female's's joyful and expectant feelings. The overall performance of the female alignss with the content of the sentence, indicating a state of happiness and satisfaction.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 90. samplenew3_00000170｜gain｜ΔF1 +0.250000

gold：anxiety, stress, tension, unease, worry

query字幕：A little bit of leisure makes me panic

源标注描述：In the text, the caption reads: "Even when idle, my mind still feels uneasy." This phrase might be a self-description or reaction of this person. Given the audio cues such as the speaker's's trembling voice, slightly faster pace, and video clues featuring a neutral expression with somewhat stiff body language, we can infer that this sentence expresses feelings of anxiety, tension, or unease. The individual might feel some stress or worry while waiting for someone or something, leading to their psychological state being in a heightened state of arousal.

off原始输出：The character's emotional state is anxiety, unease, tension.

retrieval原始输出：The character's emotional state is anxiety, tension, unease, stress, worry.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, tension, unease|0.750000|3|0|2|
|retrieval|anxiety, stress, tension, unease, worry|1.000000|5|0|0|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.750000变为1.000000，差值+0.250000。
- TP变化+2，FP变化+0，FN变化-2。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：stress, worry。

gate：0.119939923；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00002291

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：agitated, anger, anxiety, frustration
- 与query gold精确词面重合：anxiety
- 字幕：Who is your boss? I am your undercover agent. I have some information in my hands. I must report it to you immediately.
- 描述：In the text, caption content: "Who's on your inside, I'm your mole, so I have intel that I need to report to you immediately." This sentence might be said by a man to a woman. Based on the audio cues described in the personal speaking tone which is high-pitched and aggressive, and the manner of speaking being fast and staccato, it indicates that he might feel frustrated, angry, anxious, and agitated. The tone and content of this sentence suggest an urgent and pressing emotion, possibly because he has important information that he needs to report to the woman. Therefore, this statement hints at the man's negative emotions and tense state.

### 近邻2：samplenew3_00025119

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：excitement, happiness, positive, vitality
- 与query gold精确词面重合：∅
- 字幕：Li Tang looks very honest.
- 描述：In the text, the caption states: "Li Tang looks very honest." Based on the audio clues describing an individual with a high-pitched voice, clear tone, and relatively fast pace, indicating of positive emotions such as happiness, excitement, and vitality. The caption's describes "Li Tang looks very honest," without any obvious signs of negative emotion, which alignss with the positive emotions indicated by the audio clues. Therefore, it can be inferred that this statement might be a positive assessment or description, consistent with the emotional state suggested by the audio cues.

### 近邻3：samplenew3_00035554

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：annoyance, contradictory, distressed, energetic, excitement, inner turmoil, tension, torn
- 与query gold精确词面重合：tension
- 字幕：You really make it difficult for people.
- 描述：In the text, caption content: "You really put me in a spot." This sentence might be a man's's evaluation or reaction to certain individuals or situations. Given the description of the person feeling anxious or tense, yet also excited and full of energy from the audio clues, we can infer that this statement might carry an element of annoyance or contradiction. The man may be facing a dilemma or decision and feeling torn between options, while simultaneously experiencing a mix of tension and excitement. Therefore, this sentence could be the man expressing his inner turmoil and distress, contrasting with the overall sense of satisfaction and ease he presents.

### 近邻4：samplenew3_00047022

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, nervousness
- 与query gold精确词面重合：∅
- 字幕：Liang Baogen just coughed up some blood and was arranged to go to Jiuyuan County Hospital first.
- 描述：In the text, the subtitle reads, "Liang Baogen just coughed up some blood, so he was sent to Jiuyuan County Hospital." Based on the description of the individual's tension and anxiety in the audio clues, as well as the strong emotions displayed by the man in the suit in the video clues, we can infer that this sentence may be the reaction of the man in the suit to Liang Baogen's physical condition. Since the facial expression and body language of the man in the suit suggest that he may be experiencing a negative emotion, this sentence may carry a tone of concern or nervousness. At the same time, based on the composed demeanor of the man in the white shirt and glasses in the video clues, we can infer that he may be providing some information about Liang Baogen's condition to the man in the suit. Therefore, this sentence may be conveying medical information, causing the man in the suit to feel worried and nervous.

### 近邻5：samplenew3_00112882

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, tension
- 与query gold精确词面重合：anxiety, tension
- 字幕：Why did you change lawyers? I haven't even had a chance to persuade him yet.
- 描述：In the text, the subtitle reads: "Changing lawyers for reasons you advised me before I had the chance." Given the man's's calm and composed demeanor in the video cues, along with his relaxed and at ease body language, it can be inferred that he is in a state of stable and balanced emotions. Furthermore, the background environment in the video suggests that he might be in an urban setting, possibly engrossed in his thoughts or enjoying the journey in his vehicle. Based on the audio cues describing a slight tremor in an individual's voice, a slightly faster pace, and an attempt to convey a sense of urgency or importance, it can be speculated that the individual may be experiencing strong emotions such as fear or anxiety. Therefore, considering the reason the man mentions for changing lawyers in the subtitles, it can be deduced that he might be feeling tense or anxious due to some reason and needs to change lawyers to address the issue.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 91. samplenew3_00013653｜gain｜ΔF1 +0.250000

gold：gentle, polite, positive, requesting

query字幕：I would like to ask you to think of a solution.

源标注描述：In the text, the subtitle says, "I would like you to think of a solution." This sentence may be a young man's request or suggestion to someone. Based on the relaxed and comfortable state of the young man in the video clues, as well as the description of his voice and emotional state in the audio clues, it can be inferred that this sentence may have a gentle and requesting tone. Therefore, this sentence may be a polite request or suggestion, consistent with the overall positive emotion displayed by the young man.

off原始输出：The character's emotional state is polite, gentle, requesting, positive mood.

retrieval原始输出：The character's emotional state is polite, gentle, requesting, positive.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|gentle, polite, positive mood, requesting|0.750000|3|1|1|
|retrieval|gentle, polite, positive, requesting|1.000000|4|0|0|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.750000变为1.000000，差值+0.250000。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：positive。
- 相对off移除未精确匹配gold的标签：positive mood。

gate：0.120038100；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [{"prediction_label": "positive mood", "unmatched_gold_label": "positive"}], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00109729

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, contentment, contrast, happiness, inner peace, metaphor
- 与query gold精确词面重合：∅
- 字幕：Doing business is like fighting a war.
- 描述：In the text, the subtitle content "Like doing business and going to war" is possibly the man describing a certain experience or metaphor. Based on the calm and contented emotions displayed by the man in the video clues, as well as the intense emotions that the individual may be experiencing in the audio clues, we can infer that this sentence may be describing a contrast or metaphor, expressing the happiness and inner peace the man feels in the tranquil and balanced environment compared to the intense emotions he may be experiencing.

### 近邻2：samplenew3_00088440

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, confidence, excitement, important, pride, urgency
- 与query gold精确词面重合：∅
- 字幕：Actually, I have ulterior motives for wanting to help you and Lynch.
- 描述：In the text, caption content: "Actually, I wanted to help you and Lin Chi also had selfish intentions." This sentence could be the explainer or explanation of the motive of the speaker's providing assistance. Given the audio cues describing the tone of the speaker as urgent, important, and with an emphasis on their excitement, anticipation, pride, and confidence, we can infer that this sentence might be the speaker emphasizing their motive for offering help is self-serving, possibly due to some private interest or motivation they has towards collaborating with Lin Chi or their relationship. Therefore, this sentence might carry a tone of honesty or explanation, fitting with the overall positive emotion displayed by the speaker.

### 近邻3：samplenew3_00036016

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：joy, longing, nostalgia, satisfaction
- 与query gold精确词面重合：∅
- 字幕：I will go to the village temple later to see if the rice has been harvested.
- 描述：In the text, caption content: "I'll go to the village shrine to check if all the rice has been harvested." This sentence might be what a man says to someone off-screen in a video. Given the audio clues describing the background with bird chirping sounds, and the man's's smile and positive mood shown in the video, we can infer that this sentence might be about the status of crops, particularly rice harvest. The man's's positive mood and smile may indicate his satisfaction and joy over the rice harvest. Simutaneously, the bird chirping sound might be associated with nostalgia and longing for past crop yields, further supporting this inference.

### 近邻4：samplenew3_00027665

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：joy, nostalgic, positive, satisfaction
- 与query gold精确词面重合：positive
- 字幕：At that time, I was only twelve years old. It's been so many years since we last met, so it's no wonder that Chen Qian didn't recognize me at once.
- 描述：In the text, caption content: "It's no wonder Senior Chen Qian didn't recognize me at first glance; I was only twelve then time." This sentence might be spoken by a man in a suit during a conversation. Given the audio clues that describe his voice as high-pitched and energetic, conveying excitement and anticipation, along with the video clues showing him smiling and actively participating in discussions, we can infer that this statement could be about him sharing a personal success story or memory related to his life. He mentions being twelve years old and his relationship with Senior Chen Qian, possibly describing a scenario involving his childhood or reuniting with an old friend. Overall, the sentence reflects his positive mood and joyful memories, aligning with his cheerful and satisfied emotional state portrayed in the video.

### 近邻5：samplenew3_00109790

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：amusement, delighted, excitement, tension
- 与query gold精确词面重合：∅
- 字幕：Do you believe such a story? I am particularly good at diving. I can lift you up with one jump. We swim in the oil factory swimming pool in the summer and swim in the winter here.
- 描述：In the text, caption content: "Do you believe such stories? I'm crystal good, a vigorous thrust lifts you up, we swim in the swimming pool of the oil factory during summer, and here we go for winter swimming." This sentence might be a man recounting an interesting story or experience. Based on the audio clues where the man's's voice starts to shake, his breathing quickens, and the visual cues of happiness and satisfaction on both the man's and woman's faces and body language, we can infer that the sentence might carry an element of excitement and tension. The man might be telling a story that excites and unsettles him, while the woman finds it amusing and delightful. Therefore, this sentence could be the man sharing an exciting and thrilling story, fitting with his overall emotional state.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 92. samplenew3_00094323｜gain｜ΔF1 +0.266667

gold：confusion, dissatisfaction, questioning

query字幕：Why do you want to install a camera at Mr. Mahan's house?

源标注描述：In the text, the subtitle reads, "Why did you install a camera at Mr. Mahanzi's house?" This sentence is likely a woman's questioning or questioning someone. Based on the woman's facial expression and body language in the video clues, as well as the calm and steady tone of the speaker in the audio clues, we can infer that this sentence may have a tone of questioning or reproach. The woman's expression and body language suggest that she may be dissatisfied or confused about someone installing a camera at Mr. Mahanzi's house, so she asks this question.

off原始输出：The character's emotional state is questioning, puzzled.

retrieval原始输出：The character's emotional state is confused, dissatisfied, concerned.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|puzzled, questioning|0.400000|1|1|2|
|retrieval|concern, confusion, dissatisfaction|0.666667|2|1|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.400000变为0.666667，差值+0.266667。
- TP变化+1，FP变化+0，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：questioning。
- 相对off新增未精确匹配gold的标签：concern。
- 相对off新增命中的gold标签：confusion, dissatisfaction。
- 相对off移除未精确匹配gold的标签：puzzled。

gate：0.120055221；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [{"prediction_label": "puzzled", "unmatched_gold_label": "confusion"}], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00092830

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：enthusiasm, importance, positivity, responsibility
- 与query gold精确词面重合：∅
- 字幕：The plan is to reduce the operating costs of our products by adjusting the operating mode, thus benefiting more Chinese patients.
- 描述：In the text, the caption reads: "With the plan to reduce the operational cost of our products by adjusting our operating model, we aim to benefit more Chinese patients." This statement suggests that the speaker is discussing a plan focused on lowering operational costs for their product in order to reach and assist more Chinese patients. Based on the video cues, such as the lady's's serious facial expression and confident body language, and audio clues like the speaker's's determination and confident voice, it can be inferred that the speaker might feel a sense of responsibility and importance when discussing this plan. They could be enthusiastic about this plan and believe it will have a positive impact on Chinese patients.

### 近邻2：samplenew3_00092079

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, composed
- 与query gold精确词面重合：∅
- 字幕：If it were so easy to tidy up Jingfei
- 描述：In the text, the subtitle reads: "If it were truly that simple to settle Empress Jing's affairs." Considering the woman's calm and composed facial expressions in the video clues, as well as her sense of safety and comfort in an opulent setting, we can infer that this statement might be her thoughts or commentary on a particular situation or issue. Based on the audio cues, described by an expert in emotional domains, one's's acoustic qualities can reflect their emotional state, but yet, solely relying on voice cannot accurately predict the emotional state. Therefore, this statement might be her thoughts on a particular situation, suggesting that resolving issues may not be as straightforward as it appears on the surface, possibly requiring more effort or contemplation. This kind of thinking or commentary alignss with her overall display of calm and composed emotions.

### 近邻3：samplenew3_00084434

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, curiosity, positive
- 与query gold精确词面重合：∅
- 字幕：Bring it next time and let me have a look too.
- 描述：In the text, the caption reads: "Bring it over next time for me to check as well." This sentence could be what a lady says to someone nearby. Given the audio clues describing an individual who is excited and anxious, and the video clues showing the lady in a calm and thoughtful state, we can infer that this statement might carry a tone of anticipation and curiosity. The lady might be interested in what the person mentioned and wishes to be part of it, displaying a positive emotional state.

### 近邻4：samplenew3_00020177

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：positive, self-assured, tranquil
- 与query gold精确词面重合：∅
- 字幕：You can rest assured that my troubles have nothing to do with the present moment or Mr. Su.
- 描述：In the text, the caption reads: "Don't worry, my worries have nothing to do with the present situation or Mr. Su." This statement indicates that the woman is explaining her emotional state and asserting that her concerns is not related to the current context or Mr. Su. Given the personal emotional state described in the audio cues as calm and restrained, and the visual cues showing the woman's calm, composed, and satisfied demeanor, we can infer that this sentence is her explanation and comfort for her own emotions. It expresses her detachment from the current situation and her control over her feelings. Consequently, this statement further supports the idea that the woman is in a positive, tranquil, and self-assured emotional state.

### 近邻5：samplenew3_00112065

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：despair, heaviness, hopelessness, pressure, regret, regretfulness, remorse, shame
- 与query gold精确词面重合：∅
- 字幕：He committed suicide back then out of fear of punishment.
- 描述：In the text, the caption reads: "He took his own life out of guilt." This statement might be a woman's evaluation or description of someone. Given the emotional cues described in the audio, where the individual is experiencing feelings of remorse, shame, regret, regretfulness, heaviness, pressure, despair, or hopelessness, and considering the serious facial expression and focused body language of the female in the video, we can infer that this sentence likely describes someone's past actions or events. These event may be related to the person's's feelings of remorse, shame, regret, regretfulness, heaviness, pressure, despair, or hopelessness. Therefore, this sentence might be describing a situation where someone chose to take their own life out of guilt, which aligns with the overall serious and focused emotional presentation of the woman.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 93. samplenew3_00038338｜gain｜ΔF1 +0.266667

gold：anxiety, confusion, dissatisfaction

query字幕：I can't handle it alone and I don't have the ability to manage it. If I really lose the case,

源标注描述：In the text, the subtitle content: "I can't handle it alone and I don't have the ability to handle it if I lose." This sentence may be a complaint or blame from one woman to another. Based on the negative emotions such as anger, frustration, or sadness displayed by the woman described in the video clues, as well as the inner turmoil reflected in her body language and facial expressions, we can infer that this sentence may carry a sense of dissatisfaction or anxiety. Therefore, this sentence may be the woman expressing her confusion and dissatisfaction, feeling that she is unable to cope with a certain situation or task, possibly because she cannot handle it alone or she feels she lacks the ability to handle it. This emotion may be related to an important or personal event she is going through.

off原始输出：The character's emotional state is anxiety, helplessness.

retrieval原始输出：The character's emotional state is anxiety, concern, dissatisfaction.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, helplessness|0.400000|1|1|2|
|retrieval|anxiety, concern, dissatisfaction|0.666667|2|1|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.400000变为0.666667，差值+0.266667。
- TP变化+1，FP变化+0，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：concern。
- 相对off新增命中的gold标签：dissatisfaction。
- 相对off移除未精确匹配gold的标签：helplessness。

gate：0.120037422；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00095284

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, pressure, tension
- 与query gold精确词面重合：anxiety
- 字幕：I just found out that I brought a fish hook to make such a cheesy request for you.
- 描述：In the text, the caption reads: "I only realized I was asking you for such a tacky request with the fishing hook." Given the individual's's high-pitched voice tone, fast pace of speech, and the use of filler words, it can be inferred that this line may carry an emotion of anxiety, tension, and pressure. Additionally, based on the video clue where the woman's shows of neutral facial expression and contemplative state, it is unclear what her emotional state is. Therefore, this statement might be a form of questioning or response from the woman towards someone nearby, possibly conveying a sense of dissatisfaction or misunderstanding.

### 近邻2：samplenew3_00076288

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：self-conscious, tension
- 与query gold精确词面重合：∅
- 字幕：It's not like that. Listen to me. Didn't I tell you that I went to a small stall to buy meat that day?
- 描述：In the text, the caption reads: "It's not like that you have to listen to me, I'll tell you what happened. The day I went to the street vendor to buy meat." Given the personal intonation described in the audio cues - calm and controlled with a slight tremor, and a speech pattern with a hint of accent - it can be inferred that the individual might feel anxious, tense, and self-conscious. The manner in which the content is expressed also supports this inference. The person seems to be explaining or justifying something, with a tone that carries a certain level of tension and uncertainty. Therefore, it can be deduced that the individual likely felt tense and self-conscious during this conversation, possibly due to the need to explain or justify an issue.

### 近邻3：samplenew3_00069774

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, reflection, stress, tension, unease, worry
- 与query gold精确词面重合：∅
- 字幕：Saying that the lawyer touched the tiger's butt can cause a big commotion.
- 描述：In the text, the caption says: "Speaking of Lawyer Ge touching the tiger's butt, this has caused quite a stir." Based on the facial expressions and body language of the female in the video clues, as well as the tone and distinctive features of the individual's's voice in the audio clues, it can be inferred that this sentence might be a comment or reaction from a female to an event or situation. The sad and thoughtful facial expression, along with self-reflection body language, suggests she might be under some stress or in a reflective state. While the emotional cues in the audio clues, such as anxiety, embarrassment, and tension, indicate a tense and uneasy atmosphere. Therefore, this sentence might reflect the female's concern or worry about a particular event or situation, accompanied by a sense of tension or unease.

### 近邻4：samplenew3_00024233

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, scared, unease
- 与query gold精确词面重合：anxiety
- 字幕：So there are many things I dare not do and many words I dare not say.
- 描述：In the text, the subtitle reads: "So there are many things I dare not do and many words I dare not say." Based on the visual cues of the woman's facial expressions and body language in the video, she appears to be in a state of emotional distress, with a furrowed forehead and eyes that seem to be on the verge of tears. Actions such as fidgeting with her hands suggest that she is feeling nervous or agitated. At the same time, her smoking behavior also indicates that she is using self-soothing methods to cope with her emotional state. Based on these cues, we can infer that this subtitle may be the woman describing her emotional state, feeling scared or uneasy, which leads her to not dare to do many things or say many words. This sentence expresses her inner anxiety and uneasiness.

### 近邻5：samplenew3_00044933

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：firm, motivational, positive
- 与query gold精确词面重合：∅
- 字幕：You stop beating around the bush and get to the point.
- 描述：In the text, caption content: "Just get to the point already." This phrase might be the speaker's advice or demand to someone. Based on the audio cues describing the speaker's voice being high-pitched and excited tone, and using of the phrase "you don't need to worry" attempting to comfort the audience, we can infer that this sentence may carry a firm or motivational tone. Therefore, this sentence could be the speaker encouraging someone to bravely face issues or pursue their goals, which is in line with the video clues showing the woman's positive mood.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 94. samplenew3_00096901｜gain｜ΔF1 +0.285714

gold：anger, confusion, defeat, disappointment

query字幕：Although we claim to have a hundred thousand soldiers, we actually only have fifty thousand.

源标注描述：In the text, caption content: "Although we boast of having ten thousand soldiers, in reality, we only have five thousand." This sentence might be what this man said in the video. Based on the emotional cues described in the audio, which suggest personal excitement and anticipation, and the video's emotional cues showing the man's confusion and anger, we can infer that the statement might carry a tone of disappointment or defeat. The man may be expressing dissatisfaction or disappointment with a fact or situation, which alignss with his overall display of confusion and anger.

off原始输出：The character's emotional state is disappointment, defeat, frustration.

retrieval原始输出：The character's emotional state is disappointment, defeat, anger.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|defeat, disappointment, frustration|0.571429|2|1|2|
|retrieval|anger, defeat, disappointment|0.857143|3|0|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.571429变为0.857143，差值+0.285714。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：anger。
- 相对off移除未精确匹配gold的标签：frustration。

gate：0.120007284；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00095808

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, tension, urgency, worry
- 与query gold精确词面重合：∅
- 字幕：Prime Minister has wanted to kill me several times.
- 描述：In the text, the caption reads: "Prime Minister has attempted to kill me several times." This sentence might be an Asian man's describing his predicament or danger. Given the emotional cues from the audio description of the individual feeling fear, anxiety, and tension, as well as the video showing the Asian man in a calm and focused state, we can infer that this sentence is likely describing the situation he is facing, and that he is worried and uneasy about it. The tone of the sentence carries a sense of urgency and anxiety, contrasting with the overall sense of inner calm and composure exhibited by the Asian man.

### 近邻2：samplenew3_00040110

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, disappointment, dissatisfaction, frustration, stress
- 与query gold精确词面重合：anger, disappointment
- 字幕：It was your suggestion to cut off Zhang Song's head.
- 描述：In the text, caption content: "It was you who suggested cutting Zhang Song's head off." This sentence could be a statement of blame or reproach from one man to someone nearby. Based on the audio clues describing a personal voice tense, agitated, and trembling, with rapid speech and a sense of urgency, we can infer that this sentence might carry emotions of anger, frustration, anxiety, and stress. Therefore, this sentence may be the man expressing his dissatisfaction and disappointment, which alignss well with his overall negative emotional state.

### 近邻3：samplenew3_00048759

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, seriousness
- 与query gold精确词面重合：∅
- 字幕：Uncle Huang, don't you know what kind of person Gong Jin is? He has already planned everything.
- 描述：In the text, caption content: "Uncle, don't you know what Gong Jin is like? He had everything planned out from the beginning." This sentence might be an evaluation or commentary by the speaker on someone or a situation. Given the audio clues with the speaker's having a calm voice, a gentle tone, and showing empathy, along with the video cues of the man presenting a serious expression and body language, we can infer that the sentence may carry a serious or concerned tone. Therefore, this sentence might be expressing concern or warning about someone or a situation, fitting well with the man's's overall serious demeanor.

### 近邻4：samplenew3_00108411

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：aggression, anxiety, criticism, defensiveness, nervousness, reproachful, seriousness
- 与query gold精确词面重合：∅
- 字幕：Since Zhang Fei violated the military regulations, he should be subject to military law. Everything should be decided by the master.
- 描述：In the text, the subtitle reads: "Since Zhang Fei violated military regulations, he should be subject to military law. Everything depends on the decision of the master." This sentence may be the man's evaluation or decision regarding someone or an event. Based on the audio clues describing the individual's high-pitched voice, fast speaking speed, and tone indicating anxiety, nervousness, defensiveness, and aggressiveness, we can infer that this sentence may carry a serious or reproachful tone. Therefore, this sentence may be the man's criticism or decision regarding someone's violation of military regulations, expressing his serious attitude towards the issue.

### 近邻5：samplenew3_00095203

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, enthusiasm, hope, optimism, passion
- 与query gold精确词面重合：∅
- 字幕：But I didn't expect it to take six months to a year.
- 描述：In the text, the caption reads: "But I didn't anticipate it to be within half to a year." This sentence might be a man expressing his prediction or expectation. Given the audio cues where describe the individual's tone being clear, confident, and exhibiting an enthusiastic and passionate emotional state, we can infer that this sentence may carry an optimistic and hopeful tone. Therefore, this sentence could be the man's's prediction or expectation about the future, aligning with his overall positive emotional demeanor.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 95. samplenew3_00051364｜gain｜ΔF1 +0.285714

gold：dependence, gratitude, helplessness, pressure, seriousness

query字幕：If it weren't for the girl saving me today

源标注描述：In the text, the caption reads: "If it weren't not for Miss saving me today." This phrase could be a scenario or event mentioned by the man in their conversation. Considering the speaker's's anxious, dependent, and helpless emotions as described by audio cues, and the man's serious expression and body language depicted in the video clues, we can infer that this sentence might carry an element of gratitude or dependence. The man may be expressing his appreciation for Miss's help, also implying his helplessness and dependence in that situation. Therefore, this sentence might be the man's way of thanking or praising Miss, which alignss with his overall portrayal of seriousness and pressure.

off原始输出：The character's emotional state is gratitude, appreciation.

retrieval原始输出：The character's emotional state is gratitude, dependence.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|appreciation, gratitude|0.285714|1|1|4|
|retrieval|dependence, gratitude|0.571429|2|0|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.285714变为0.571429，差值+0.285714。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：dependence。
- 相对off移除未精确匹配gold的标签：appreciation。

gate：0.120044790；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00013738

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：contemplation, doubt, focused, sadness
- 与query gold精确词面重合：∅
- 字幕：What did the great wizard deceive His Highness about?
- 描述：In the text, the subtitle reads, "I wonder what the great wizard could have deceived Your Highness with." This sentence may be a comment or reaction to the man. Based on the audio clues describing the individual speaking in a calm and cautious tone, with a consistent voice tone indicating control over their emotions, and speaking in a clear and concise manner, indicating confidence in their abilities. At the same time, based on the video clues of the man's posture and facial expression, he may be experiencing various emotions such as contemplation, focus, or even sadness. Therefore, this sentence may be a questioning or doubting of the man, implying that the man may have been deceived by the great wizard, contradicting the overall display of the man's contemplative and focused emotions.

### 近邻2：samplenew3_00062463

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, stress, worry
- 与query gold精确词面重合：∅
- 字幕：Nowadays, it is difficult to return after the court of the Holy Morning is hit.
- 描述：In the text, caption reads: "Today's's imperial hall cannot be returned to." This phrase might be a man's inner monologue or an evaluation of the current situation. Given the man's's deep contemplation and neutral expression as depicted in the video clues, and the audio hints suggesting the speaker is speaking in a high-pitched and agitated manner, with rapid and staccato speech, we can infer that this sentence carries a sense of heaviness, anxiety, or stress. Therefore, this sentence could possibly be a way for the man to express his concern or worry about the current work or personal issues, aligning with the overall serious or thoughtful mood he portrays.

### 近邻3：samplenew3_00106198

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：heavy, seriousness, tension
- 与query gold精确词面重合：seriousness
- 字幕：The witchcraft case eight years ago.
- 描述：In the text, the subtitle content "The Witchcraft Case Eight Years Ago" suggests that based on the description of the man's serious expression and wearing a robe in the video clues, as well as the slight tremor and slow and cautious speech in the audio clues, we can infer that this man may be in a heavy, serious, or tense emotional state. The mention of the "witchcraft case eight years ago" in the subtitle content may be a sensitive topic that could be related to the man's current emotional state. However, it is difficult to determine the exact emotional state of the man based solely on the video and audio clues, so we need to further observe his facial expressions and body language to gather more information.

### 近邻4：samplenew3_00032689

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：commitment, determination, overwhelm, pressure, resolve
- 与query gold精确词面重合：pressure
- 字幕：To die with one's duty fulfilled, this is the end.
- 描述：In the text, with subtitles stating: "Dedication to the utmost until the end", based on the man's's facial expressions and body language in the video clues, and the deep and powerful tone of his voice from audio cues, by using of words conveying power and feelings of despair, we can infer that this statement might be the man expressing a sense of determination or commitment. He might feel under pressure and overwhelmed, but still resolved to give it his all. This statement could reflect the man's's firmness and resolve, aligning with the complex emotions he exhibits overall.

### 近邻5：samplenew3_00026871

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：advice, assurance, comfort
- 与query gold精确词面重合：∅
- 字幕：You can rest assured to collect silk and weave fabric.
- 描述：In the text, caption reads: "Just rest assured when you receive the silk cloth." This sentence might be a suggestion or comfort offered by the speaker to others. Given the audio cues that suggest the speaker has a calm, confident, and firm tone, along with the video hints showing people smiling and in a relaxed mood, we can infer that this statement could be an encouragement or a way of assuringance. Therefore, the sentence might be the speaker's providing comfort or advice to others, aligning with the positive emotions portrayed in the video.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 96. samplenew3_00108798｜gain｜ΔF1 +0.285714

gold：anxiety, distrust, suspicion, under pressure

query字幕：

源标注描述：In the text, caption reads: "Persuading Zhou Xizhong to see through Chang Zhongxin's disloyal intentions." Based on the speaker's's tense and anxious tone, rapid speech, and repetitive use of phrases as well as the frequent use of rhetorical questions suggested in the audio clues, it can be inferred that the speaker is feeling anxious and under pressure about something, possibly attempting to convince themselves or an audience of a point. Thus, this caption might indicate the speaker's's attempt to persuade Zhou Xizhong to see through Chang Zhongxin's disloyalty, expressing their suspicion and distrust towards Zhou Xizhong. This contrasts with the calm and confident facial expressions and body language of the female figure in the video clues, highlighting differing emotional states.

off原始输出：The character's emotional state is neutral.

retrieval原始输出：The character's emotional state is anxious, tense, uncertain.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|neutral|0.000000|0|1|4|
|retrieval|anxiety, tension, uncertainty|0.285714|1|2|3|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.000000变为0.285714，差值+0.285714。
- TP变化+1，FP变化+1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：tension, uncertainty。
- 相对off新增命中的gold标签：anxiety。
- 相对off移除未精确匹配gold的标签：neutral。

gate：0.120038949；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00023345

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, demand, dissatisfaction, frustration
- 与query gold精确词面重合：∅
- 字幕：It is enough to flatten the sea and not allow the court to allocate military expenses.
- 描述：In the text, the caption reads: "Enough to level the sea and prevent the court from allocating military funds." This sentence could be the proposer's's demand or suggestion regarding a certain situation or issue. Given the aggressive and provocative tone described in the audio cues, along with the proposer's's apparent anger and frustration, we can infer that this sentence might carry a strong sense of demand or dissatisfaction. Therefore, this sentence could be the proposer's's protest or demand against unfair treatment or an unsatisfactory situation.

### 近邻2：samplenew3_00113641

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, happiness
- 与query gold精确词面重合：∅
- 字幕：We two are both extraordinary women.
- 描述：In the text, the caption reads: "The two of us were always standard girls." Based on the comedic facial expressions and body language of the female figure in the video clues, as well as the clear and confident voice and moderate speaking pace in the audio clues, it can be inferred that this woman is experiencing positive emotions such as happiness or confidence. The term "standard girl" in the caption might be a way for her to express pride and confidence in herself, which alignss with the positive emotions indicated by the video and audio clues.

### 近邻3：samplenew3_00023700

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：blessing, confidence, determination, heartfelt, protective, solemn
- 与query gold精确词面重合：∅
- 字幕：This palace will also ensure the prosperity and wealth of his whole family.
- 描述：In the text, caption reads: "This palace will ensure their prosperity and grandeur." This sentence might be spoken by a female character. Based on audio clues that suggest the speaker uses a high-pitched tone, emphasizes certain words, and exhibits energetic and enthusiastic emotions, we can infer that the statement may carry a tone of confidence and determination. Simultaneously, considering the video clues showing the female character in a calm and composed state, along with an overall serene atmosphere, we can speculate that this statement might be the female character expressing her protection and blessing for someone or something, infused with a solemn and heartfelt sentiment.

### 近邻4：samplenew3_00035559

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confusion, doubt, surprise, uncertainty, unease
- 与query gold精确词面重合：∅
- 字幕：How did the soldiers catch up so quickly?
- 描述：In the text, caption content: "How did the soldiers already come knocking on the door." This sentence might be a woman's reaction to some unexpected event or situation. Given the video clues showing the woman's calm, serene, and satisfied mood, as well as the audio clues describing an excitement, anticipation, and nervousness, we can infer that this sentence might carry a tone of surprise, confusion, or unease. The woman might be surprised and puzzled by the sudden appearance of the soldiers, which contrasts with her previous calm and satisfied mood. Therefore, this sentence might be the woman's way of expressing her doubt or confusion about the unexpected event.

### 近邻5：samplenew3_00045207

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, pressure, stress, worry
- 与query gold精确词面重合：∅
- 字幕：Try your best to preserve your prosperity and honor.
- 描述：In the text, the subtitle reads: "Try your best to preserve your prosperity and glory." This sentence may be the speaker's advice or warning to someone. Based on the description of the speaker's tense and anxious voice in the audio clues, as well as the possibility that the speaker is experiencing a range of negative emotions, we can infer that this sentence may carry a tone of concern or worry. Therefore, this sentence may be a reminder to someone to protect their identity and status in order to avoid losing their prosperity and wealth. This aligns with the description of the speaker in the audio clues possibly being under significant stress or pressure.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 97. samplenew3_00062291｜gain｜ΔF1 +0.285714

gold：calm, discomfort, frustration, suffering, surprise

query字幕：Always make you suffer.

源标注描述：In the text, caption content: "It must make you suffer all the time." This sentence could be a description or reaction by a female in a video about herself or others. Based on the acoustic information of high tension and discomfort described in the audio cues, as well as the visual clues of the female's showing surprise, furrowing her brows, and trying to maintain calm body language, we can infer that this sentence might be a female describing their own or someone else's difficult situation or problem, as well as the negative emotions caused by it, such as suffering and discomfort. This is consistent with the complex emotions displayed by the female in the video.

off原始输出：The character's emotional state is anger, sadness.

retrieval原始输出：The character's emotional state is anger, frustration.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, sadness|0.000000|0|2|5|
|retrieval|anger, frustration|0.285714|1|1|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.000000变为0.285714，差值+0.285714。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：frustration。
- 相对off移除未精确匹配gold的标签：sadness。

gate：0.120045491；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00041526

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, firm
- 与query gold精确词面重合：∅
- 字幕：There is absolutely no intention to show off.
- 描述：In the text, the caption reads: "And there's absolutely no bragging in that." This sentence could be a self-explanation or justification by a lady for herself. Given the description of the female speaker's's voice being high-pitched with confidence and firmness, and accompanied by a fast-paced conga rhythm in the audio cues, we can infer that this sentence might carry a tone of confidence and firmness. The lady might be responding to someone's evaluation or viewpoint about her, and she wants to express that she did not have any intention to boast but was for other reasons. Therefore, this sentence could be the lady's's own justification for her behavior or statement, fitting well with the confident and firm emotion described in the audio cues.

### 近邻2：samplenew3_00069487

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：hopelessness, sadness
- 与query gold精确词面重合：∅
- 字幕：I have lost my loved ones.
- 描述：In the text, the caption reads: "I've lost my closest family member." Given the personal voice's trembling and shaking described in the audio cues, along with rapid and shallow breathing, we can infer that this statement is being made by an individual expressing feelings of sadness and hopelessness. This phrase suggests that the person may have experienced a significant loss or traumatic event, causing them immense pain and heartache. Consequently, this sentence reflects the individual's current emotional state.

### 近邻3：samplenew3_00003761

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction
- 与query gold精确词面重合：∅
- 字幕：If he makes even more outrageous mistakes in the future
- 描述：In the text, the subtitle reads: "If he gets even more out of line in the future." This sentence may be an individual's evaluation or reaction to someone or something. Based on the frustration and anger expressed by the individual described in the audio clues, as well as the rough and aggressive tone in the audio, we can infer that this sentence carries a sense of anger and dissatisfaction. The individual may feel angry and disappointed with someone's wrongful behavior, believing that their actions have crossed a certain boundary. Therefore, this sentence expresses the individual's strong dissatisfaction and anger towards someone's behavior.

### 近邻4：samplenew3_00047605

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, dissatisfaction, distrust, tension, unhappy
- 与query gold精确词面重合：∅
- 字幕：They are trying to pin the blame on their father.
- 描述：In the text, caption content: "They're pinning' the blame on old man." This sentence might be a woman's evaluation or response to some group or individual's actions or plans. Given the emotional cues described in the audio, such as an individual feeling anxious, tense, guilty, and regretful, as well as the woman's surprised facial expression, furrowed brow, and tense body language in the video, we can infer that this statement might carry a tone of concern, dissatisfaction, or distrust. The woman may be unhappy with some group or individual's behavior, believing they're trying to attribute fault to her father, which could have triggered her anxiety and tension.

### 近邻5：samplenew3_00070931

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：enthusiasm, excitement, happiness
- 与query gold精确词面重合：∅
- 字幕：
- 描述：In the text, caption reads: "I was in high school with Junyi, we were classmates and sat together at Saint Mary's Girls' School." Based on the video clues, the woman's tense or hesitant body language and the formal or professional setting suggest that she might be feeling a certain level of anxiety or nervousness when conversing with someone in uniform. However, according to the audio clues, the female voice is filled with enthusiasm and excitement, indicating that she expresses a positive emotion when mentioning her relationship with Junyi. Therefore, while the video clues suggest a sense of tension, the audio clues convey excitement and enthusiasm, suggesting that she feels happy or thrilled when talking about her relationship with Junyi.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 98. samplenew3_00041830｜gain｜ΔF1 +0.333333

gold：affirmative, appreciation, confidence

query字幕：You should be considered outstanding.

源标注描述：In the text, the subtitle reads: "You should be considered outstanding." This sentence may be a man's evaluation or comment on someone or something. Based on the man's serious and focused facial expression, his prepared and alert body language in the video, as well as the deep and resonant voice and the feeling of confidence and authority in the audio clues, we can infer that this sentence may carry a tone of appreciation or affirmation. This sentence may be the man's expression of appreciation for someone's achievements or performance, aligning with the overall focused and confident emotions displayed by the man.

off原始输出：The character's emotional state is positive, affirmation, praise.

retrieval原始输出：The character's emotional state is positive, acknowledgment, appreciation.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|affirmation, positive, praise|0.000000|0|3|3|
|retrieval|acknowledgment, appreciation, positive|0.333333|1|2|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.000000变为0.333333，差值+0.333333。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：acknowledgment。
- 相对off新增命中的gold标签：appreciation。
- 相对off移除未精确匹配gold的标签：affirmation, praise。

gate：0.120008878；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [{"prediction_label": "affirmation", "unmatched_gold_label": "affirmative"}], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00083232

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：If Qiao Zheng did not develop the corpse, it means that he arrived at the same time as us, which is the time of Xu Huiwen's death.
- 描述：In the text, caption content: "If Joe Zheng did not develop the corpse, it means that his arrival time was in line with ours, coinciding with Xu Hwen's's death time. Based on the description in the audio clues, by analyzing the acoustic attributes of an individual's voice, such as pitch, tone, and volume, one can determine their emotional state. The speaker also notes that an individual's emotional state may be influenced by factors such as age, gender, and cultural background. Given this information, we cannot directly infer the emotional state of the character mentioned in the caption content. Therefore, we need more background information or additional visual clues to better understand the situation."

### 近邻2：samplenew3_00006447

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：defeat, disappointment, dissatisfaction, frustration, seriousness, tension
- 与query gold精确词面重合：∅
- 字幕：I die before achieving success.
- 描述：In the text, the subtitle reads, "I died before achieving victory." This sentence is likely spoken by the person sitting behind the table. Based on the audio clues describing the individual speaking in an urgent and desperate tone, with a tense pitch and fast pace, we can infer that this sentence may carry a sense of disappointment or frustration. It may be the man expressing his sense of defeat or dissatisfaction with a certain situation. This aligns with the serious and tense emotions displayed by the man in the video.

### 近邻3：samplenew3_00041727

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：at ease, casual, confidence, content, positive
- 与query gold精确词面重合：confidence
- 字幕：Show me your real skills and come here tomorrow for a fishing competition.
- 描述：In the text, the caption reads: "Your real skill, come here tomorrow and give me a fishing competition." Given the video hints such as the man's's calm and relaxed facial expression and comfortable body posture, along with the surrounding environment of boats floating on water, it can be inferred that he is in a positive emotional state, feeling content and at ease. The audio clues suggest that the man's's voice is cool and rhythmic, deep and resonant, without any background noise or other sounds, indicating a stable and confident tone. Therefore, based on the man's's invitation to come and participate in a fishing competition the next day as stated in the caption, it can be deduced that he is issuing the invite in a confident and casual manner, reflectinging a positive emotional state.

### 近邻4：samplenew3_00052212

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：friendliness, positive
- 与query gold精确词面重合：∅
- 字幕：Just say these attackers have a good sense of measure when they start.
- 描述：In the text, caption content: "These attackers handle their actions with precision." This sentence might be one man's's evaluation or reaction to another man. Without emotional cues from the pitch and rhythm of the audio, it's hard to determine the sentiment. However, based on the video clues showing the two men's body language and facial expressions, we can infer that their conversation is relatively positive and non-threatening. Therefore, this statement could be an appreciation or affirmative evaluation, fitting with the friendly interaction between the two men.

### 近邻5：samplenew3_00015776

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：humor, irony
- 与query gold精确词面重合：∅
- 字幕：Do you think we are all blind?
- 描述：In the text, the caption reads: "Thought we were all blind, huh?" This phrase could be a response from a man to a particular of situation or dialogue. Based on the comedic facial expressions and body language displayed by the man in the video clues, as well as the audio clues of his voice shaking and his tone wavering, we can infer that this statement might carry a humorous or ironic tone. The man may be responding to a situation or dialogue in a humorous way; however, due to the lack of more contextual information, it's unclear about the exact emotional state.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 99. samplenew3_00043155｜gain｜ΔF1 +0.333333

gold：anxiety, concern, tension, unease

query字幕：The photo of Shen with cancer is very likely me.

源标注描述：In the text, caption content: "The cancer photo of Shen is probably me." This sentence might be what a man said on the phone. Based on the audio cues where describe the speaker's having a slight tremble in their voice, and the tone is hesitant and cautious, we can infer that this statement might carry a sense of tension or anxiety. The man might have been discussing topics related to Shen's cancer over the phone, which could have triggered his emotional response. Therefore, this sentence expresses the man's concern or unease about the possibility of the Shen cancer photo being connected to him.

off原始输出：The character's emotional state is worry, unease.

retrieval原始输出：The character's emotional state is tension, anxiety.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|unease, worry|0.333333|1|1|3|
|retrieval|anxiety, tension|0.666667|2|0|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.333333变为0.666667，差值+0.333333。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 原已命中的gold标签被移除：unease。
- 相对off新增命中的gold标签：anxiety, tension。
- 相对off移除未精确匹配gold的标签：worry。

gate：0.119973600；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [{"prediction_label": "worry", "unmatched_gold_label": "anxiety"}, {"prediction_label": "worry", "unmatched_gold_label": "concern"}], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00077854

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：assistance, expectations, hopes, needing assistance, under pressure, work-life balance
- 与query gold精确词面重合：∅
- 字幕：Can I take your son to the city to work?
- 描述：In the text, the caption reads: "Can I take your little son to the city for work?" Given the man's's relaxed posture and the comfortable atmosphere in the video clues, along with the anxious, tense, depressed, and overwhelmed emotional tone of the speaker in the audio clues, we can infer that this statement might be a request or suggestion put forward by the man to the other party. The man might feel under a lot of pressure, needing assistance to manage his work-life balance. Hence, this sentence might convey the man's's expectations and hopes, wishing for the other person's's help in looking after his little son so he can better handle his own affairs.

### 近邻2：samplenew3_00078465

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern
- 与query gold精确词面重合：anxiety, concern
- 字幕：Where did I put my cousin's Mercedes car?
- 描述：In the text, the caption reads: "Looking for my cousin's Mercedes is parked there." This sentence could be one person asking another about the location of the Mercedes. Given the personal tone and controlled manner described in the audio clues, along with the body language and environmental influences shown in the video hints, we can infer that this statement might carry an element of anxiety or concern. Therefore, this sentence might imply that one of the individuals is worried or anxious about the location of the Mercedes.

### 近邻3：samplenew3_00096131

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern, stress, tension
- 与query gold精确词面重合：anxiety, concern, tension
- 字幕：My company has always been doing very well, but now it's difficult to come up with this amount of money.
- 描述：In the text, the caption reads: "Our business has always been particularly good, but it's just this money that's causing the problem now." Given the emotional cues described in the audio and the mention of an insurmountable financial issue in the caption, we can infer that the individual might be experiencing concern or stress. This emotion could align with the anxiety or tension described in the audio cues.

### 近邻4：samplenew3_00031464

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, stable
- 与query gold精确词面重合：∅
- 字幕：Luo Qing has already escaped danger and the situation is now stable.
- 描述：In the text, the caption reads: "Lu Qing is out of danger and the current situation is stable." Given the speaker's's calm and measured tone, as well as their clear and concise delivery in the audio cues, coupled with the man's's contemplative and serene state depicted in the video clues, we can infer that this statement likely represents an objective report on Lu Qing's condition. Without any clear indicators from the audio or video about Lu Qing's emotional state, we cannot deduce his feelings. However, considering the man's's tranquil expression and thoughtful demeanor in the video, and the speaker's's calm and measured voice in the audio, we can speculate that Lu Qing might be in a state of stability and calmness.

### 近邻5：samplenew3_00113733

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, encouragement, hope, motivational, positive, support
- 与query gold精确词面重合：∅
- 字幕：You have a long way to go in your life.
- 描述：In the text, the subtitle reads, "You have a long road ahead of you in this life." This sentence is likely spoken by the man in the conversation. Based on the relaxed and open demeanor of the man in the video clues, as well as the individual in the audio mentioning a long and difficult journey, we can infer that this sentence is likely an encouraging or motivational statement. The man may be giving courage and hope to the other person in the conversation, expressing expectations and support for their future. This statement aligns with the overall positive emotions and confident attitude displayed by the man.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 100. samplenew3_00102751｜gain｜ΔF1 +0.333333

gold：entertained, joy, sarcasm

query字幕：Even if one day the emperor really abdicates the throne.

源标注描述：In the text, the subtitle content says, "Even if one day the emperor really abdicates." This sentence is likely spoken by the man in the conversation. Based on the audio clues describing the speaker's voice as filled with excitement and enthusiasm, with an energetic and positive tone, as well as the use of repetition and emphasis, we can infer that this sentence may have a sarcastic or exaggerated tone. Therefore, this sentence is likely the man joking or expressing a humorous viewpoint, consistent with the overall mood of joy and entertainment displayed by the man.

off原始输出：The character's emotional state is humorous, exaggerated, positive.

retrieval原始输出：The character's emotional state is humorous, surprised, sarcastic.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|exaggerated, humor, positive|0.000000|0|3|3|
|retrieval|humor, sarcasm, surprise|0.333333|1|2|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.000000变为0.333333，差值+0.333333。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：surprise。
- 相对off新增命中的gold标签：sarcasm。
- 相对off移除未精确匹配gold的标签：exaggerated, positive。

gate：0.119967371；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00112458

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：disappointment, discontent, dissatisfaction, fear, tension
- 与query gold精确词面重合：∅
- 字幕：Brother, this statement may not be appropriate. Let's continue with our secret plan, but be careful not to violate orders and create chaos.
- 描述：In the text, caption content: "Brother, this might be inappropriate. Following to our receipt of the secret edict, it's being misused as a false decree." Based on the audio cues describing the speaker's's voice tense and tight, with tremors, and the use of words such as "treason" and "disappointment", it can be inferred that the speaker is likely experiencing a state of tension, fear, and disappointment. The words in this sentence also suggest the speaker's dissatisfaction and disagreement with some action or decision, further supporting the assumption that they may be in a negative emotional state. Therefore, this sentence could be the speaker's's expression of criticism or discontent towards someone or a decision.

### 近邻2：samplenew3_00113015

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, enthusiasm, humor, passion
- 与query gold精确词面重合：∅
- 字幕：Xiu Dao Sima Yi Zhang He is Cao Cao crawling out of the tomb.
- 描述：In the text, caption content: "Monk Wei Yi Zhang He is none other than Cao Cao rising from his grave." This sentence might be a description or comment by a male speaker on the topic of discussion. Given that the male speaker's is enthusiastic and passionate, with a clear tone, strong expression skills, and confidence in the subject being discussed, we can infer that the statement might carry an element of exaggeration or humor. Therefore, this phrase could be a humorous or exaggerated way of expression, consistent with the overall positive mood portrayed by the male speaker.

### 近邻3：samplenew3_00072580

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, desires, excitement, positive expectations
- 与query gold精确词面重合：∅
- 字幕：They are all very willing
- 描述：In the text, the subtitle content "They are all very willing" may be an expression of the individual's attitude or desire towards certain people or things. Based on the audio clues describing the slight tremor in the individual's voice and the slightly faster speech rate, as well as the video clues of the individual's complex facial expressions and body language, we can infer that this sentence may carry a sense of excitement and anxiety. Therefore, this sentence may be an expression of the individual's positive expectations or desires towards certain people or things, aligning with the complex emotions displayed by the individual as a whole.

### 近邻4：samplenew3_00079134

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：determination, hope, inspired, passion, urgency
- 与query gold精确词面重合：∅
- 字幕：Born in a chaotic world is unfortunate, but if we can turn chaos into ambition.
- 描述：In the text, the caption reads: "Born in turmoil is unfortunate, but yet to turn chaos into resolve." This phrase might be a statement made by the speaker during their speech. Given the audio clues that depict the speaker's with enthusiasm and emotional investment, their voice conveying urgency and importance, as well as the video clues showing the man's's passion, intense discussion, and sense of urgency, we can infer that this phrase could be part of the speaker's emphasizing the unfortunate circumstances of being born in turmoil, while expressing a determination to transform the chaos into a resolve. The sentence may carry an inspiring or uplifting tone, aligning with the overall passion and sense of urgency displayed by the man.

### 近邻5：samplenew3_00090625

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, determination, emotionally detached, frustration, tension
- 与query gold精确词面重合：∅
- 字幕：The lawyer ate chicken, but didn't eat the speaker's food.
- 描述：In the text, caption content: "Lawyer Ge eats chicken quai, he didn't eat the speaker's's meal." This sentence might be an evaluation or reaction from one person to another. Considering the emotional state of the speaker described in the audio clues, feeling anxious, tense, and emotionally detached, and the emotional state portrayed by the person making facial expressions, showing anger, frustration, or determination, we can infer that the sentence might have a negative, provocative tone. Therefore, this sentence could be an expression of criticism or irony, which alignss with the observed emotional states in the video.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 101. samplenew3_00091362｜gain｜ΔF1 +0.333333

gold：anger, anxiety, fear

query字幕：If it weren't for your cold-heartedness, locking me inside the building

源标注描述：In the text, the subtitle reads: "If it weren't for your cold-heartedness, I wouldn't be locked inside the building." This sentence may be a complaint or accusation from the individual in the audio. Based on the trembling and shaking of the individual's voice, fluctuating pitch, and the muffled audio, we can infer that this sentence carries a sense of anger, fear, or anxiety. The individual may be complaining or accusing the other person of their cold-hearted behavior, which has resulted in them being locked inside the building, further supporting the inference that the individual is experiencing negative emotions and distress.

off原始输出：The character's emotional state is anger, fear, sadness.

retrieval原始输出：The character's emotional state is anger, fear, anxiety.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, fear, sadness|0.666667|2|1|1|
|retrieval|anger, anxiety, fear|1.000000|3|0|0|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为1.000000，差值+0.333333。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：anxiety。
- 相对off移除未精确匹配gold的标签：sadness。

gate：0.119991943；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00037686

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：despair, disappointment, frustration, sadness
- 与query gold精确词面重合：∅
- 字幕：I understand now that it's completely over between me and Xiaoguo.
- 描述：In the text, the subtitle content "I realized that it's completely over between me and Xiaoguo." This sentence indicates that the individual recognizes that their relationship with someone has ended, possibly evoking a feeling of disappointment, sadness, or despair. Based on the highly negative emotions described in the audio clues, as well as the solemn expression and solitary posture of the man in the video, we can infer that this sentence may be expressing a state of frustration or despair. Overall, the video, audio, and subtitle content all indicate that the individual is experiencing a negative emotion, possibly due to some form of loss or adversity.

### 近邻2：samplenew3_00056080

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：agitation, anger, dissatisfaction, opposition
- 与query gold精确词面重合：anger
- 字幕：You can't say that the common people are not allowed to eat.
- 描述：In the text, the caption reads: "You can't deny the people their food." This phrase could be an evaluation or response from one of the standing individuals to one of the seated ones. Given the audio cues with a sense of urgency and importance, as well as the video clues showing the standing person's actively engaging in dialogue and expressing strong opinions through body language and gestures, we can infer that the tone might convey agitation or anger. Therefore, this sentence might reflect the standing person's's dissatisfaction or opposition to the views or decisions of the seated person.

### 近邻3：samplenew3_00028433

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：enthusiasm, excitement
- 与query gold精确词面重合：∅
- 字幕：Isn't that adding wings to the tiger when doing business with me, revealing that the password technique is very high.
- 描述：In the text, caption content: "That would be like giving me an advantage in doing business with cryptography being high." This sentence might be what this woman said in the video. Based on the audio clues described by the higher pitch and sharp staccato rhythm, as well as the video hints showing the woman's happy and satisfied emotion, we can infer that the tone of this sentence might convey excitement or enthusiasm. Therefore, this sentence could be the woman expressing her excitement or surprise about a certain situation, which alignss with her overall positive mood.

### 近邻4：samplenew3_00046449

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：appreciation, calm, content
- 与query gold精确词面重合：∅
- 字幕：Although sometimes warm and thoughtful
- 描述：In the text, the caption reads: "Although sometimes warm and considerate." This sentence could be a man's evaluation or response to someone or a certain situation. Given the audio cues describing the individual speaking calmly and restrained, with an even tone without any fluctuations, and with a warm and inviting tone, we can infer that this phrase might be a form of praise or an affirming expression. Therefore, this sentence might be the man's's appreciation for someone's warm and considerate actions or a commendation of a certain situation, in line with his overall display of calmness and contentment.

### 近邻5：samplenew3_00112142

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, doubt, responsibility, suspicion, tension, unease
- 与query gold精确词面重合：anxiety
- 字幕：Who told you who this person is?
- 描述：In the text, the caption reads: "Tell me who is this person." This sentence could be a query or confusion from a man to someone nearby. Considering the audio clues that describe the individual's voice trembling and shaking, along with video clues showing the man's in a serious demeanor possibly indicating anxiety or responsibility, we can infer that the tone of the sentence might be tense or uneasy. Therefore, the sentence could be the man expressing doubt or suspicion towards someone nearby, aligning with his overall display of tension.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 102. samplenew3_00063258｜gain｜ΔF1 +0.333333

gold：humor, positive, sarcasm

query字幕：I'm sure it's even stricter than the emperor's butler.

源标注描述：In the text, caption content: "Probably even more stringent than the emperor's steward." This sentence could be an evaluation or response from a woman towards someone or something. Given the audio cues describing a person speaking with a high pitch, in a lively yet quick manner, and video clues showing a woman with a calm and composed facial expression and relaxed body language, we can infer that this sentence might carry a tone of humor or sarcasm. Therefore, this phrase might be an ironic or playful expression, fitting well with the overall positive emotion displayed by the woman.

off原始输出：The character's emotional state is humorous, mocking, positive.

retrieval原始输出：The character's emotional state is humorous, sarcastic, positive.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|humor, mockery, positive|0.666667|2|1|1|
|retrieval|humor, positive, sarcasm|1.000000|3|0|0|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.666667变为1.000000，差值+0.333333。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：sarcasm。
- 相对off移除未精确匹配gold的标签：mockery。

gate：0.120072246；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00110406

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：release, relief
- 与query gold精确词面重合：∅
- 字幕：The emperor and the empress finally breathed a sigh of relief.
- 描述：In the text, the caption reads: "The emperor and the empress finally heaved a sigh of relief." This sentence could be a commentary or response from a female character in the video. Given the emotional cues described in the audio, such as sadness, anger, and frustration, and the visual cues from the female character's facial expressions and body language, we can infer that this phrase might carry a tone of relief or release. Therefore, it is possible that this line refers to the female character after experiencing stress or hardship, finally gaining relief or good news, so she she lets out a sigh. This contrasts with the negative emotions described in the audio, potentially marking a turning point in her emotional state.

### 近邻2：samplenew3_00022690

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, calm, contemplation, excitement, stress, urgency
- 与query gold精确词面重合：∅
- 字幕：Once a daughter gets married, she is no longer a daughter.
- 描述：In the text, the caption reads: "Once a daughter marries, she's no longer your daughter." This statement could be something a woman might say to herself during introspection or pondering over her family dynamics. Given the video hints of her expressionless demeanor, relaxed gestures, and the simplicity of her surroundings, it can be inferred that she she might be in a state of calmness or deep contemplation.   From the audio cues, the speaker has a higher pitch voice with slight tremors and speaks at a relatively fast pace, suggesting that she might be experiencing heightened emotional arousal, possibly due to anxiety or excitement, and may feel a sense of urgency or pressure in conveying her message. Therefore, this sentence might reflect a complex emotional state for the woman as she considers through the changes in her family structure and her own role following her daughter's marriage, potentially encompassing elements of anxiety, stress, or thoughtful reflection.

### 近邻3：samplenew3_00093818

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, enthusiasm, excitement
- 与query gold精确词面重合：∅
- 字幕：The servant has already delivered the message, it should arrive soon, that's good.
- 描述：In the text, the caption reads: "Servant has already sent word out, they should be arriving soon, that's good." This sentence could belong to a female character describing a situation or convey a message. Given the emotional tone of individual experiencing happiness, excitement, and anticipation described in the audio clue, along with the urgency and lively characteristic of the tone, we can infer that this sentence might be spoken with an air of expectation and enthusiasm. The female character might be awaiting the arrival of someone important or an event, and she is filled with anticipation and excitement. Thus, this sentence expresses her optimistic attitude towards what is about to happen.

### 近邻4：samplenew3_00047688

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：calm, excitement, focused, nervousness, seriousness
- 与query gold精确词面重合：∅
- 字幕：Your vision needs to be broader, after all, you still have a long way to go.
- 描述：In the text, the subtitle reads, "You need to broaden your perspective, at least you still have a chance." This sentence may be the woman's advice or criticism to someone. Based on the woman's serious and confident expression in the video clues, as well as her calm and controlled body language, we can infer that this sentence may have a serious and calm tone. Additionally, based on the slight tremor in the individual's voice and the slightly faster speech rate in the audio clues, we can speculate that the individual may be feeling nervous and excited. Therefore, this sentence may be the woman giving advice to someone with a certain level of seriousness and nervousness, while also demonstrating her confidence and focus.

### 近邻5：samplenew3_00034490

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：annoyance, confidence, determination, frustration, resolve, self-assuredness
- 与query gold精确词面重合：∅
- 字幕：I will never let him be in a sorry state.
- 描述：In the text, the caption reads: "I will never let him suffer from my favor." Given the speaker's's delivery as described in the audio cues, with confidence and firmness, the tone being assertive and strong, it suggests that she has control over the situation and possibly experienced feelings of frustration and annoyance. From this, we can infer that the statement expresses the speaker's's determination and resolve, that she will not allow someone to gain her favor or exploit her. This statement reflects the speaker's's confidence and determination, aligning with their overall display of steadfastness and self-assuredness.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 103. samplenew3_00070426｜gain｜ΔF1 +0.363636

gold：calm, compassion, contentment, despair, empathy, sadness, understanding

query字幕：Save a life, please

源标注描述：In the text, the caption reads: "Saving a life with a single breath." Given the video hints describing the woman in a state of tranquility and contentment, and the audio clues depicting the singer experiencing intense emotional sorrow and despair, we can infer that this phrase might be her evaluation or reaction to the singer. Based on the woman's calm and satisfied state in the video and the singer's emotional sadness and hopelessness in the audio, we can deduce that the phrase may carry an element of empathy or understanding. Therefore, it appears that this statement reflects the woman's understanding and sympathy for the singer's emotional state, aligning with her overall portrayal of calmness and contentment.

off原始输出：The character's emotional state is urgency, importance, fear, surprise.

retrieval原始输出：The character's emotional state is compassion, empathy, care, concern.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|fear, importance, surprise, urgency|0.000000|0|4|7|
|retrieval|care, compassion, concern, empathy|0.363636|2|2|5|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.000000变为0.363636，差值+0.363636。
- TP变化+2，FP变化-2，FN变化-2。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：care, concern。
- 相对off新增命中的gold标签：compassion, empathy。
- 相对off移除未精确匹配gold的标签：fear, importance, surprise, urgency。

gate：0.119959615；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00078114

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, dissatisfaction, fear, panic
- 与query gold精确词面重合：∅
- 字幕：But did you know that I am married to the emperor?
- 描述：In the text, the caption reads: "But you know I married the emperor, right?" Given the elaborate attire and setting described in the video clues, as well as the cup she holds, it can be inferred that she might be the Empress or the emperor's wife. Furthermore, the expression and body language of the woman depicted in the video clues suggest a tone of disdain and anger, hinting that she might be dissatisfied or provoked by certain matters. Based on the audio cues, which include a high-pitched voice with slight tremors and a state of heightened arousal, it can be speculated that she is experiencing strong emotions such as fear, anxiety, or panic. Therefore, this sentence could possibly be her expression of dissatisfaction or complaint to someone nearby or about a situation.

### 近邻2：samplenew3_00088285

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, blame, complaint, dissatisfaction, frustration, sadness
- 与query gold精确词面重合：sadness
- 字幕：Are you blaming me, Song Yongxing?
- 描述：In the text, the caption reads: "You're blaming me for Shunyuu's success." This sentence might be a response or complaint from a woman to someone else. Considering the negative emotions described in the audio cues, such as frustration, anger, and sadness, and the angry and contemptuous expressions and body language shown in the video clues, we can infer that this sentence might carry an element of blame or complaint. The woman might feel unhappy about someone's actions or words, and expresses her dissatisfaction through this sentence.

### 近邻3：samplenew3_00021294

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：happiness, joy, serene peace
- 与query gold精确词面重合：∅
- 字幕：Only then can one be considered truly talented as an emperor.
- 描述：In the text, caption content: "Only then can one be considered truly gifted with imperial talent." Based on the video clues, where the woman is dressed in traditional Chinese attire, her hairdo intricately styled and adorned with exquisite jewelry, and her facial expression calm and composed, conveying a sense of tranquility through her body language, it can be inferred that the woman is experiencing a state of serene peace. From the audio clues, the individual speaking is described with a high-pitched, enthusiastic voice, the tone being quite high, speaking rapidly and urgently, and the high-pitched, excited tone suggesting feelings of joy or happiness, among other positive emotions. Therefore, based on the analysis of the video and audio clues, it can be deduced that the woman's state of serene peace does not align well with the person in the audio experiencing strong excitement or passion. This caption content might be an evaluation or reaction to the woman, possibly with a hint of irony or mockery.

### 近邻4：samplenew3_00104107

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, sadness
- 与query gold精确词面重合：sadness
- 字幕：You have to do two big things to show them.
- 描述：In the text, the caption reads: "You need to do two big things to show them." This sentence might be a suggestion or an expectation from a woman towards someone or some people. Given the fast pace and sharp tone described in the audio cues, as well as the woman's expressed anger and sadness in the video clues, we can infer that this sentence might carry a strong tone and emotion. The woman may be expressing her dissatisfaction with someone or demanding action from them out of anger and sadness. Therefore, this sentence could be a form of warning, threat, or a strong demand, which alignss with the woman's overall expression of anger and sadness.

### 近邻5：samplenew3_00014037

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, disdain, frustration, surprise
- 与query gold精确词面重合：∅
- 字幕：You guys can't wait for me to get old.
- 描述：In the text, the caption reads: "You all wish that I was old," according to the woman's expression and body language described in the video clues, her emotional state is a mix of surprise and disdain. This caption might be an evaluation or reaction from the woman towards those around her. Given the tension and effort in the voice described in the audio clues, as well as the quick pace of speech, we can infer that this sentence may carry an element of anger or frustration. Therefore, this sentence could be the woman expressing her anger or frustration towards those around her, which alignss with her overall displayed emotional state.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 104. samplenew3_00004032｜gain｜ΔF1 +0.400000

gold：questioning, unhappy

query字幕：Is this not arranged by an IQ-level leader? Let me tell you.

源标注描述：In the text, caption content: "Is this not arranged by someone of intelligence level? I tell you." This sentence could be a comment or reaction from a female towards a male. Given the audio clues where describe the male speaking in a calm and confident manner, while the female speaks in a tense and agitated way, along with the video clues showing the male displaying a serious and thoughtful expression, we can infer that the sentence might carry a tone of challenge or skepticism. The female may hold a differing opinion about the male's's decisions or actions, expressing her dissatisfaction or lack of agreement in an unhappy way. Therefore, this sentence might reflect the female's feelings of dissatisfaction or questioning, contrasting with the male's's overall focused and confident demeanor.

off原始输出：The character's emotional state is skepticism, distrust, dissatisfaction, anxiety.

retrieval原始输出：The character's emotional state is skepticism, dissatisfaction, questioning.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, dissatisfaction, distrust, skepticism|0.000000|0|4|2|
|retrieval|dissatisfaction, questioning, skepticism|0.400000|1|2|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.000000变为0.400000，差值+0.400000。
- TP变化+1，FP变化-2，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：questioning。
- 相对off移除未精确匹配gold的标签：anxiety, distrust。

gate：0.119999193；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00032464

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, appreciation, excitement
- 与query gold精确词面重合：∅
- 字幕：Thank you for believing in me and giving me three days.
- 描述：In the text, the caption reads: "And thank you for believing in me, giving me three days." Based on the described personal feelings of anxiety or tension, as well as excitement or being full of energy, we can infer that this statement might be an expression of gratitude and commitment from one person to another. The individual may feel excited and anxious because they has been given three days to complete a task or fulfill a promise. This complex emotional state could be due to the significance of the task or the individual's expectations regarding its outcome. Therefore, this sentence expresses appreciation and determination, aligning with the emotional state described in the audio clues.

### 近邻2：samplenew3_00086045

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：guilt, regret, sadness
- 与query gold精确词面重合：∅
- 字幕：I ignored that it was Zhao Pengchao who got drunk with me, not the person I commemorated.
- 描述：In the text, caption reads: "I overlooked that it was with Zhao Pengchao in his drunken state." This sentence might be spoken by the speaker reflectinging on themselves or pondering over a particular issue. With the audio clues describing the speaker's in a calm tone, tinged with sadness, and displaying a sense of detachment or disconnection in body language, we can infer that this statement might carry an element of guilt or regret. The speaker may be reflectinging on neglecting something important or valuable, and feeling sorrow or sadness about it. Therefore, this sentence might reflect the emotional state of the speaker.

### 近邻3：samplenew3_00086980

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：Just on that day, he happened to set up a camera across the dock number two.
- 描述：In the text, the subtitle reads: "Just on the day of the incident, he set up a camera across from Dock 2." Based on the neutral expression and calm body language of the man in the video, as well as the slight tremor in the individual's voice and slightly faster speech rate in the audio clues, we can infer that this sentence may be the man describing an event or providing some kind of information. Since the man's expression and tone do not show any obvious emotional signs, we cannot accurately infer his emotional state. However, based on his professional environment and attire, we can speculate that he is likely providing an objective description or information rather than expressing personal emotions.

### 近邻4：samplenew3_00046462

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, worry
- 与query gold精确词面重合：∅
- 字幕：I'm just afraid that your emotions might make him uncomfortable or something like that.
- 描述：In the text, the caption reads: "I'm just worried about you being emotional and him not feeling well." This sentence might be what a man tells a woman. Based on the audio cues described with a high pitch and quick pace of speech, along with the depiction of negative emotions and a sense of being trapped, we can infer that this phrase might carry a tone of concern or worry. The man may be concerned that the woman's emotions could affect him or make him feel uncomfortable. Therefore, this sentence could be the man expressing his concern and worry about the woman's emotions.

### 近邻5：samplenew3_00002231

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, seriousness, significant, tension
- 与query gold精确词面重合：∅
- 字幕：Because my master is afraid of leaking the interrogation results.
- 描述：In the text, the subtitle reads: "Because my master feared the exposure of the interrogation results." Given the demeanor of the man described in the video hints - his seriousness and concentration - and the auditory cues of his trembling voice and slightly faster pace, we can infer that this sentence might be part of a tense or significant situation. It could pertain to discussions about interrogation results or other sensitive topics. The man's's serious expression, body language, and the negative emotional cues from the audio hints all support this interpretation.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 105. samplenew3_00080412｜gain｜ΔF1 +0.400000

gold：anger, dissatisfaction, resentment

query字幕：Where is it? It's just a scammer.

源标注描述：In the text, the subtitle reads, "Where is it? It's this scammer." This sentence may be the individual's evaluation or reaction to someone or something. Based on the audio clues describing the individual's high-pitched, fast manner of speaking, as well as the use of vulgar language and aggressive speech, we can infer that this sentence carries a sense of anger, dissatisfaction, or resentment. Therefore, this sentence may be the individual's negative evaluation or accusation towards someone or something.

off原始输出：The character's emotional state is anger, frustration.

retrieval原始输出：The character's emotional state is anger, dissatisfaction.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, frustration|0.400000|1|1|2|
|retrieval|anger, dissatisfaction|0.800000|2|0|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.400000变为0.800000，差值+0.400000。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：dissatisfaction。
- 相对off移除未精确匹配gold的标签：frustration。

gate：0.119978987；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [{"prediction_label": "frustration", "unmatched_gold_label": "dissatisfaction"}], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00009730

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, threatening
- 与query gold精确词面重合：anger
- 字幕：You still have a mouth now.
- 描述：In the text, the caption reads: "Now you're just talking." This phrase could be a response or accusation from one individual to another. Given the audio cues describing the person's's voice filled with anger and frustration, the tone is sharp and aggressive, and the pace is fast, indicating with urgency and impatience, we can infer that this statement carries an angry and threatening tone. Therefore, this sentence might be an expression of blame or threat, aligning with the individual's overall display of anger.

### 近邻2：samplenew3_00002647

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, dissatisfaction, frustration, resentment
- 与query gold精确词面重合：anger, dissatisfaction, resentment
- 字幕：I don't want those people to keep criticizing me for being old-fashioned.
- 描述：In the text, caption content: "To spare those people's always think I'm old-fashioned." This sentence could be a response or complaint from a woman to someone or some people. Judginging from the video clues, the woman's expression shows anger or dissatisfaction, her eyebrows are tightly furrowed and her lips are slightly pursed, and she is holding herself tightly across her chest, which suggests that she holds negative feelings towards certain people's's evaluations or attitudes. Additionally, based on the audio clues describing the speaker's's provocative and hostile tone, as well as the use of vulgar language and abusive remarks, it can be inferred that the speaker might be experiencing negative emotions such as anger, frustration, or resentment. Therefore, the woman's response may be in response to the speaker's's negative emotions, expressing her discontent or anger towards the speaker.

### 近邻3：samplenew3_00076288

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：self-conscious, tension
- 与query gold精确词面重合：∅
- 字幕：It's not like that. Listen to me. Didn't I tell you that I went to a small stall to buy meat that day?
- 描述：In the text, the caption reads: "It's not like that you have to listen to me, I'll tell you what happened. The day I went to the street vendor to buy meat." Given the personal intonation described in the audio cues - calm and controlled with a slight tremor, and a speech pattern with a hint of accent - it can be inferred that the individual might feel anxious, tense, and self-conscious. The manner in which the content is expressed also supports this inference. The person seems to be explaining or justifying something, with a tone that carries a certain level of tension and uncertainty. Therefore, it can be deduced that the individual likely felt tense and self-conscious during this conversation, possibly due to the need to explain or justify an issue.

### 近邻4：samplenew3_00046603

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, excitement, humor, positive, teasing
- 与query gold精确词面重合：∅
- 字幕：Have you heard of any child who is a master of electronic piano? That's on a different level compared to the piano.
- 描述：In the text, the subtitle content says, "Have you heard of any child who is a master of the electronic keyboard? It's on a different level than the piano." Based on the description of the speaker's confident and firm tone, relatively high pitch indicating excitement or enthusiasm, and a stable and consistent rhythm indicating a sense of control and stability in the audio clues, we can infer that this sentence may have a confident and excited tone. At the same time, based on the relaxed and joyful emotion displayed by the woman in the video, we can speculate that this sentence may be a humorous or teasing expression, consistent with the overall positive emotion exhibited by the woman. Therefore, this sentence may be a humorous comment or question intended to evoke laughter or create a relaxed atmosphere.

### 近邻5：samplenew3_00094702

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：boredom, complaint, dejected, dissatisfaction, negative, stress, uninterested
- 与query gold精确词面重合：dissatisfaction
- 字幕：Our New Year's Eve dinner is not lively even when we are eating.
- 描述：In the text, the subtitle reads: "Our New Year's Eve dinner is not lively at all." Based on the audio clues describing the speaker's monotonous tone, lack of intonation, and relatively slow speech rate, we can infer that the speaker may feel bored, uninterested, or stressed. The phrase "not lively" in this sentence may be the speaker's evaluation or reaction to the New Year's Eve dinner. Based on the emotional state described in the audio clues, we can infer that this sentence may carry a negative or dejected tone. Therefore, this sentence may be the speaker's complaint or expression of dissatisfaction with the lack of liveliness in the New Year's Eve dinner, aligning with the emotional state described in the audio clues.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 106. samplenew3_00099175｜gain｜ΔF1 +0.400000

gold：heavy, sadness, tension

query字幕：You are saying that he killed Yan Ming.

源标注描述：In the text, the subtitle content "You mean he killed Yan Ming." This sentence may be spoken by the man while thinking or reflecting. Based on the visual clue of the man's head-down thinking posture and the dim environment in the video, as well as the trembling of the individual's voice and slightly faster speech rate in the audio clue, we can infer that this sentence may carry a heavy or tense emotion. This sentence may be the man's expression of a significant issue he is contemplating or a disturbing event he is recalling, aligning with the overall display of the man's thinking, reflection, and sadness.

off原始输出：The character's emotional state is serious, contemplative, angry, frustrated.

retrieval原始输出：The character's emotional state is anger, sadness.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anger, contemplation, frustration, seriousness|0.000000|0|4|3|
|retrieval|anger, sadness|0.400000|1|1|2|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.000000变为0.400000，差值+0.400000。
- TP变化+1，FP变化-3，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：sadness。
- 相对off移除未精确匹配gold的标签：contemplation, frustration, seriousness。

gate：0.119972311；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00002681

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：The master means that Fengzhi is now in Jin Siyu's hands.
- 描述：In the text, the caption reads: "Master's intention is to honor it as currently in Jin Siyu's possession." Given the audio clues, where the speaker uses a monotonous tone and a flat pitch with no inflection or emotion, and at a moderate pace, we can infer that this statement is conveyed in a calm and objective manner. Additionally, the video clues show the person with their eyes closed, head slightly tilted, conveying a sense of tranquility and serenity. Thus, this sentence might be describing or discussing someone's situation being in Jin Siyu's hands, without any apparent emotional connotations.

### 近邻2：samplenew3_00040493

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：friendliness, harmony, polite, positivity, respect, sincere
- 与query gold精确词面重合：∅
- 字幕：Please invite the two friends of my father's to our house.
- 描述：In the text, the caption reads: "If the two gentlemen are indeed dear to your father, then invite them home." This sentence could be an invitation or suggestion made by a man to a woman. Given the speaker's's voice is described as calm and restrained, with a confident and authoritative tone, and considering the video cues of the man and woman's composed demeanor, we can infer that this statement might be a polite and sincere invitation, reflectinging the man's's respect and friendliness towards the woman. Therefore, it alignss well with the harmonious interaction and positive emotions between the man and the woman.

### 近邻3：samplenew3_00031058

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, tension
- 与query gold精确词面重合：tension
- 字幕：How did Xu Ru Gui say that she ate the pill?
- 描述：In the text, caption content: "How did Xu Ruigui say she ate that pill?" This sentence might be a man's's question or confusion about an event or plot. Based on the video clues, such as the man's's serious and focused expression and body language, as well as the audio cues describing a highly tense state, we can infer that this sentence might be said with a sense of anxiety or tension. The man's's facial features and overall demeanor indicate that he is very serious about what he is doing, which could be due to his attention and concern for the event. Therefore, this sentence might be the man's's questioning or misunderstanding of a crucial detail or plot, fitting in with his overall tense emotion.

### 近邻4：samplenew3_00020212

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：irony, mockery, negative
- 与query gold精确词面重合：∅
- 字幕：Grandma, grandma, is your mouth so big to eat me?
- 描述：In the text, the caption reads: "Grandma, Grandma, your mouth is so big, are you trying to eat me?" This phrase might be a joke or a teasing remark directed at the grandmother by an individual. Given the description of the sound in the audio clue as being harsh and confrontational, along with the person's's potentially negative emotional state depicted in the video clue, we can infer that the statement might carry a tone of irony or mockery. Therefore, this sentence may not reflect genuine concern or fear, but it rather serves as a humorous expression, consistent with the overall negative emotion displayed by the individual.

### 近邻5：samplenew3_00061626

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, condescending, distrust, mockery, overwhelm, stress
- 与query gold精确词面重合：∅
- 字幕：You said you admire me.
- 描述：In the text, the caption reads: "You say you admire me." Based on the individuals' expressions of surprise or shock in the video hints, as well as their actions holding sticks or similar objects, it can be inferred that they they have witnessed something unexpected or startling. The caption's "You say you admire me" might be a response or reaction from an individual to someone. From the audio hints describing an individual's with a trembling voice and body, along with a tense and pressured tone, it can be deduced that the individual is likely experiencing a state of anxiety, being overwhelmed, or under a great deal of stress. Therefore, this sentence may carry a condescending, mocking, or distrustful undertone, fitting well with the overall intense emotional response of the individual.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 107. samplenew3_00036294｜gain｜ΔF1 +0.400000

gold：firmness, frustration, irritation, negativity, strength, urgency

query字幕：Then you have to go and meet him in person.

源标注描述：In the text, the caption reads: "In which case, you'll have to meet him personally." This sentence could be a suggestion or demand made to someone. Given the audio cues, the individual's voice carries an urgency and tension, with the tone indicating feelings of frustration or irritation. Coupled with the video clues showing a woman with neutral facial expressions and various other expressions, we can infer that this statement might be in response to someone's confusion or hesitation, conveying a firm or strong recommendation. This recommendation may align with the individual's current negative emotional state, possibly put forth to address issues or tackle challenges.

off原始输出：The character's emotional state is neutral.

retrieval原始输出：The character's emotional state is assertive, decisive, urgent, frustrated.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|neutral|0.000000|0|1|6|
|retrieval|assertive, decisive, frustration, urgency|0.400000|2|2|4|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.000000变为0.400000，差值+0.400000。
- TP变化+2，FP变化+1，FN变化-2。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增未精确匹配gold的标签：assertive, decisive。
- 相对off新增命中的gold标签：frustration, urgency。
- 相对off移除未精确匹配gold的标签：neutral。

gate：0.120014414；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00113641

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confidence, happiness
- 与query gold精确词面重合：∅
- 字幕：We two are both extraordinary women.
- 描述：In the text, the caption reads: "The two of us were always standard girls." Based on the comedic facial expressions and body language of the female figure in the video clues, as well as the clear and confident voice and moderate speaking pace in the audio clues, it can be inferred that this woman is experiencing positive emotions such as happiness or confidence. The term "standard girl" in the caption might be a way for her to express pride and confidence in herself, which alignss with the positive emotions indicated by the video and audio clues.

### 近邻2：samplenew3_00114579

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：frustration, pressure, stress, urgency
- 与query gold精确词面重合：frustration, urgency
- 字幕：Then I'll have to trouble you to make a trip.
- 描述：In the text, with subtitles reading: "That would be a burden on you," the serious facial expressions and body language of the female figure, along with the trembling voice and tense tone of speech in the audio clues, allow us to infer that this sentence might be a request or task proposed by someone to another person. The serious expressions and body language of the female suggest she might be dealing with an important issue, while the speaker's's tense tone and trembling voice indicate they may feel stressed or frustrated. Therefore, this sentence carries a sense of urgency and pressure, requiring the other party to run an errand.

### 近邻3：samplenew3_00060673

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, defeated, disheartened
- 与query gold精确词面重合：∅
- 字幕：That can make oneself full of glory.
- 描述：In the text, the subtitle reads: "That would amount to grandeur for oneself." Given the slight tremble in the speaker's's voice as indicated by the audio clues and the use of the phrase "seems to never do it right," suggesting the speaker might feel discouraged or disheartened, we can infer that this statement might carry a tone of irony or mockery. Therefore, this phrase could be seen as a mocking or ironic comment on someone or something, aligning with the anxious, defeated, and disheartened emotions described in the audio cues.

### 近邻4：samplenew3_00098634

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：concern, curiosity, heartbreak, longing, loss, sadness
- 与query gold精确词面重合：∅
- 字幕：In the end, I cannot escape the fate of being a nail.
- 描述：In the text, the caption reads: "After all, it was destined to be a nail." This line might be a line lyric sung by a female singer. Based on the emotional cues conveyed through the audio, such as the singer's expression of sadness and longing, and the video, which shows the woman's curiosity and concern, we can infer that this line may express a sense of loss and heartbreak. This alignss with the emotional states described in both the audio and video clues.

### 近邻5：samplenew3_00047224

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：appreciation, comfortable, praising, warm
- 与query gold精确词面重合：∅
- 字幕：Lizhi is transported all the way to Beijing, which is really precious.
- 描述：In the text, caption reads: "The persimmons sent from afar by Reiko are truly precious." This sentence might be spoken by a woman to a man. Given the warmth and comfort conveyed in the narrator's voice as described in the audio clues, along with the woman's smile and cheerful mood shown in the video, we can infer that this phrase might carry an appreciative or praising tone. The woman might be acknowledging and admiring the effort made by the man, as well as recognizing the value of the persimmons. This alignss with the overall positive emotion displayed by the woman;

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 108. samplenew3_00054854｜gain｜ΔF1 +0.416667

gold：authoritative, seriousness, stress

query字幕：Cao Cao has always been strict with military discipline.

源标注描述：In the text, the caption reads: "Cao Cao was is always strict with military discipline." This phrase could be an evaluation or description of the male character in the video. Given the serious expression, strong posture, and dramatic contrast with the black background of the video clues, we can infer that this sentence might emphasize the seriousness and authoritative nature of the male character. Additionally, based on the audio cues describing the individual's voice being tense, agitated, with a high pitch, and shaking, we can deduce that this sentence might depict the tension and pressure resulting from the character's stringent military discipline and high standards. Therefore, this sentence could be highlighting the seriousness of the male character and the stress he faces, aligning with the emotional states suggested by both the video and audio clues.

off原始输出：The character's emotional state is serious, focused, determined, tense, anxious.

retrieval原始输出：The character's emotional state is serious, focused, authoritative.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|anxiety, determination, focused, seriousness, tension|0.250000|1|4|2|
|retrieval|authoritative, focused, seriousness|0.666667|2|1|1|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.250000变为0.666667，差值+0.416667。
- TP变化+1，FP变化-3，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：authoritative。
- 相对off移除未精确匹配gold的标签：anxiety, determination, tension。

gate：0.119977966；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00041568

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, confusion, tension, unease
- 与query gold精确词面重合：∅
- 字幕：Didn't you hear the folk song just now?
- 描述：In the text, caption content: "Didn't you hear the folksong just sung?" This sentence might be a man's response to some event or situation. Given the audio cues described by the trembling voice, shallow and rapid breathing, and the choice of tone and vocabulary which suggests they might feel overwhelmed or under significant stress, we can infer that this sentence might carry an anxious or tense tone. Therefore, this sentence could be the man expressing his confusion or unease about what happened earlier.

### 近邻2：samplenew3_00095808

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, fear, tension, urgency, worry
- 与query gold精确词面重合：∅
- 字幕：Prime Minister has wanted to kill me several times.
- 描述：In the text, the caption reads: "Prime Minister has attempted to kill me several times." This sentence might be an Asian man's describing his predicament or danger. Given the emotional cues from the audio description of the individual feeling fear, anxiety, and tension, as well as the video showing the Asian man in a calm and focused state, we can infer that this sentence is likely describing the situation he is facing, and that he is worried and uneasy about it. The tone of the sentence carries a sense of urgency and anxiety, contrasting with the overall sense of inner calm and composure exhibited by the Asian man.

### 近邻3：samplenew3_00047764

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confrontational, mockery, negative
- 与query gold精确词面重合：∅
- 字幕：Every Han Chinese
- 描述：In the text, "Every large populace outputs." This sentence might be the speaker's's evaluation or perspective on a particular group or individual. Given the video clues of the men's serious and focused expressions, as well as the audio clues of the speaker's's deep, monotonous, and aggressive tone, we can infer that this sentence may carry a negative, confrontational, or mocking tone. Therefore, this sentence might be a negative assessment or an offensive remark directed at a group, contrary to the serious and contemplative mood conveyed by the men.

### 近邻4：samplenew3_00110252

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, courteous, excitement, humble, polite, respect
- 与query gold精确词面重合：∅
- 字幕：Madam, I apologize for my rudeness.
- 描述：In the text, the subtitle reads: "My elder sister-in-law, I beg your pardon." Based on the changes in the facial expressions and body language of the man described in the video hints, as well as the excitement and anxiety in the speaker's's emotional tone as described in the audio clues, we can infer that this phrase might be a courteous or polite way for the man to address his elder sister-in-law, expressing his respect and humility towards her. This phrase could possibly be part of an address or greeting by the man to his elder sisterin-law within a palace setting, which alignss with the complex and multi-layered emotional responses the man exhibits overall.

### 近邻5：samplenew3_00086839

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, excitement, pressure
- 与query gold精确词面重合：∅
- 字幕：Visiting Zhuge Liang is of great importance.
- 描述：In the text, the caption reads: "Meeting Zhuge Liang is of utmost importance." Based on the man's's confidence, decisiveness, and focus as described in the video clues, along with the sense of urgency and significance conveyed in his voice as detailed in the audio cues, we can infer that this statement might have been made by him while conveying information or giving a presentation. This suggests that the man has a strong understanding and awareness of the importance of meeting Zhuge Liang, possibly carrying an emotional tone of excitement, anticipation, and pressure. This alignss well with the positive emotional state described in the video and audio clues.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 109. samplenew3_00088733｜gain｜ΔF1 +0.428571

gold：ease, positive response, satisfaction

query字幕：Ke He said it well.

源标注描述：In the text, the caption reads: "Gee said it well." This phrase might be what someone at the table said to the man. Given the audio cues describing an individual experiencing a mix of positive and negative emotions, slightly leaning towards the positive, and the video hints of the man's's relaxed body language and the context of dining, we can infer that this sentence could be a form of praise or acknowledgment. Therefore, this sentence might be a positive response to what the man said, fitting with his overall displayed sense of satisfaction or ease.

off原始输出：The character's emotional state is satisfaction, ease, recognition, appreciation.

retrieval原始输出：The character's emotional state is satisfaction, ease, positive response.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|appreciation, ease, recognition, satisfaction|0.571429|2|2|1|
|retrieval|ease, positive response, satisfaction|1.000000|3|0|0|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.571429变为1.000000，差值+0.428571。
- TP变化+1，FP变化-2，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：positive response。
- 相对off移除未精确匹配gold的标签：appreciation, recognition。

gate：0.119932599；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00061103

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confusion, unease
- 与query gold精确词面重合：∅
- 字幕：Oh my god, heaven is really tempting me, Qin country.
- 描述：In the text, the subtitle reads, "Oh my, Heaven is really tempting me in the state of Qin." This sentence may be an individual's evaluation or reaction to their environment or situation. Based on the audio cues describing the trembling voice, fluctuating tone, and slow and cautious speech of the individual, we can infer that this sentence may carry a sense of anxiety, unease, or confusion. The individual is trying to control their emotions, but the trembling voice indicates that the emotions are still present. Therefore, this sentence may be the individual expressing their feelings of unease or confusion about the current situation.

### 近邻2：samplenew3_00040183

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：indifference, nonchalant, positive
- 与query gold精确词面重合：∅
- 字幕：So what if it's big?
- 描述：In the text, caption content: "Big deal, right?" This phrase could be the man's response to some issue or challenge. Given the video hints of the man's's smile and the joyful mood he exhibits, as well as the audio cues describing tension, excitement, and negative emotions, we can infer that this sentence might carry a tone of nonchalance or indifference. The man might express a lack of concern or importance in his response to something, aligning with the overall positive emotion he portrays.

### 近邻3：samplenew3_00111704

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：care, concern
- 与query gold精确词面重合：∅
- 字幕：Is your illness getting better?
- 描述：In the text, the subtitle says, "Are you feeling better?" This sentence may be the bald man's inquiry or concern for someone. Based on the audio clues describing the individual's higher pitch voice, positive and enthusiastic tone, as well as the video clues of the man's serious and focused expression and the formality of the environment, we can infer that this sentence may carry a tone of care or concern. Therefore, this sentence may be the man's inquiry about someone's health, expressing his care and concern.

### 近邻4：samplenew3_00096602

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, tension
- 与query gold精确词面重合：∅
- 字幕：Black Po Shangjun has already arranged your title and position for you to sit on.
- 描述：In the text, caption content: "The Black Mother has already arranged your rank to sit." This sentence might be a man's's evaluation or reaction to someone. Given the audio cues that describe a trembling voice, feeling overwhelmed or under immense pressure, and the video clues showing the man with his eyebrows furrowed, lips tightly closed, and fists clenched body language, we can infer that the tone of this sentence might be tense, anxious, or even angry. Therefore, this sentence could possibly be the man's's warning or threat to someone, which alignss well with the overall tension and anger he is displaying.

### 近邻5：samplenew3_00037043

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：defeat, despondency, disappointment
- 与query gold精确词面重合：∅
- 字幕：The emperor will be even more surprised. Just now, Sima Yi was still asking for rewards for his achievements, but now he has lost again.
- 描述：In the text, the caption reads: "His Majesty would be even more astonished, for Sima Yi was still claiming credit and seeking rewards just moments ago, yet now, he has failed again." Given the description of the male voice in the audio clues, it is calm and restrained, yet carries a hint of sadness. Coupled with the video clues showing a middle-aged man with a serious expression and looking off into the distance, we can infer that this statement might be his evaluation or reaction to an event or situation. The sorrowful tone described in the audio clues and the serious expression and contemplative state shown in the video clues suggest that this evaluation may carry feelings of disappointment, defeat, or despondency. Therefore, this sentence could be the middle-aged man's response to a situation of failure or setback.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 110. samplenew3_00002174｜gain｜ΔF1 +0.500000

gold：anger, determination

query字幕：This time I must take Jingzhou.

源标注描述：In the text, the caption reads: "This time, I shall seize Jingzhou." This sentence might be shouted by someone. Given the audio clues describing a male voice that is firm and powerful, and the video clues showing the person shouting with a strong facial expression and body language, we can infer that this statement might convey a sense of determination and anger. The person shouting may be expressing their resolve and anger possibly due to some conflict or disagreement with another individual.

off原始输出：The character's emotional state is determination, resolve.

retrieval原始输出：The character's emotional state is determination, anger.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|determination, resolve|0.500000|1|1|1|
|retrieval|anger, determination|1.000000|2|0|0|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.500000变为1.000000，差值+0.500000。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：anger。
- 相对off移除未精确匹配gold的标签：resolve。

gate：0.119954221；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00078108

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, confidence, determination
- 与query gold精确词面重合：anger, determination
- 字幕：I can destroy Cao
- 描述：In the text, the subtitle content "I can destroy Cao" may indicate that the man is expressing confidence and determination. Based on the description of the deep, throaty voice with a sense of urgency in the audio clues, as well as the authoritative tone, we can infer that this statement may be the man expressing his ability and determination, possibly in response to a challenge or to showcase his strength. Therefore, this statement may express the man's anger, determination, and confidence, aligning with the serious facial expression of the man in the video and the possible formal or professional context.

### 近邻2：samplenew3_00072321

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：focused, neutral
- 与query gold精确词面重合：∅
- 字幕：Today, Cao Cao holds the emperor hostage and uses him to control the feudal lords.
- 描述：In the text, caption reads: "Today Cao Cao seizes the emperor to justify his actions to the lords." Based on the video hints of the man's's composed facial expression and relaxed body language, as well as the acoustic information described in the audio clues, we can infer that this sentence might be the man describing or discussing historical events or plotlines. The man's's composed and relaxed state suggests he is interested or familiar with the topic, and the acoustic information in the audio clues implies his emotion could be neutral or focused. Therefore, this sentence likely represents an objective statement by the man about historical events or plotlines, rather than a strongly emotionally charged expression.

### 近邻3：samplenew3_00103273

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, concern
- 与query gold精确词面重合：∅
- 字幕：Nothing, just a little worried.
- 描述：In the text, the caption reads: "Nothing, just a bit concerned." This sentence might be a man's response to an issue or situation. Given the audio cues, with the description of a deliberate and slow pace, and a calm, restrained tone, we can infer that this expression conveys the man's's concern. He might be responding to someone's concern or inquiry, attempting to downplay his worries while still conveying a certain level of anxiety. This alignss with the video clues of the man's's thoughtful and mournful expression.

### 近邻4：samplenew3_00093708

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：The Road to War Arm II
- 描述：In the text, caption content: "War Arm Path II". This phrase might be the title of a movie or game that the character in the video is saying. Based on the description of the video clues where the person wears a green robe, wears a crown, and has a serious and focused expression, as well as the audio clues where the speaker's's voice is hoarse, with an aggressive and provocative tone, we can infer that this phrase might be a way the speaker describes or discusses this movie or game. Due to the lack of emotional clues in both the video and audio hints, we cannot accurately deduce the character's emotional state.

### 近邻5：samplenew3_00047559

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：frustration, helplessness
- 与query gold精确词面重合：∅
- 字幕：Things that cannot be done
- 描述：In the text, with caption content: Given that there are no feasible options as described through audio cues indicating an individual experiencing high levels of negative emotions such as anger, frustration, or anxiety, and considering the serious expression, body posture, and solemn ambiance depicted in the video clues, we can infer that this sentence might be the man's's description or complaint about something unattainable or a predicament he is facing. This sentence likely conveys his sense of frustration and helplessness, aligning with the overall serious and focused emotional state he exhibits.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 111. samplenew3_00063251｜gain｜ΔF1 +0.500000

gold：cheerful, light-hearted

query字幕：When we meet like-minded people on the road, we can set up a game right there.

源标注描述：In the text, the caption reads: "When we meet fellow enthusiasts on the road, we set up a game there and then." This sentence could be an individual's suggestion or proposal for some activity or game. Given the audio cues with the speaker's in a calm and soothing tone, and the video hints showing the individual with a humorous expression and a relaxed state, we can infer that this sentence might carry a light-hearted or cheerful tone. Therefore, this sentence is likely an individual suggesting or proposing an interesting activity to increase everyone's joy and relaxation.

off原始输出：The character's emotional state is positive, cheerful.

retrieval原始输出：The character's emotional state is light-hearted, cheerful.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|cheerful, positive|0.500000|1|1|1|
|retrieval|cheerful, light-hearted|1.000000|2|0|0|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.500000变为1.000000，差值+0.500000。
- TP变化+1，FP变化-1，FN变化-1。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：light-hearted。
- 相对off移除未精确匹配gold的标签：positive。

gate：0.119996637；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00037328

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：pride, satisfaction
- 与query gold精确词面重合：∅
- 字幕：The outcome of me and him should be considered a half-point difference.
- 描述：In the text, the subtitle reads: "The outcome of our competition should be a half-point difference." This sentence may be the speaker's evaluation or viewpoint on the result of a match or competition. Based on the confident and firm tone described in the audio clues, as well as the use of the word "victory" implying a sense of triumph or success, we can infer that the speaker may hold a proud and satisfied attitude towards the outcome of their competition with someone else. Therefore, this sentence expresses a positive emotional state, feeling proud and satisfied with their achievements.

### 近邻2：samplenew3_00100962

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：inspiring, positive, uplifting
- 与query gold精确词面重合：∅
- 字幕：I saw a poem that is powerful enough to turn your defeat into victory.
- 描述：In the text, the caption reads: "I've seen a melody so enchanting it could turn defeat into victory." Given the description of the male voice in the audio cues as calm and soothing, along with the serene and tranquil ambiance created by the background music, this statement can be inferred to possibly describe a piece of music or artwork. Moreover, considering the character's's calm and organized demeanor in the video clues, coupled with his apparent deep contemplation, this statement might describe a piece of music that brings about inner peace and reflection, or could be offering someone a positive encouragement and support. Therefore, this phrase may carry an uplifting and inspiring emotional tone, aligning well with the male's's overall calm and positive disposition.

### 近邻3：samplenew3_00082068

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：confusion, doubt, uncertainty
- 与query gold精确词面重合：∅
- 字幕：I wonder if there is any connection.
- 描述：In the text, the subtitle content says, "I wonder if there is any connection." This sentence may indicate the individual's questioning or contemplation about a certain topic or situation. Based on the calm and composed expression of the individual in the video clues, as well as the slight tremors in the individual's voice and the hesitant and cautious tone in the audio clues, we can infer that this sentence may carry a sense of doubt or uncertainty. The individual may feel confused or uncertain when thinking about a certain question or situation, hence posing this question.

### 近邻4：samplenew3_00063844

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：contemplation, immediacy, importance, introspection, responsibility, urgency
- 与query gold精确词面重合：∅
- 字幕：Also, you must complete the task before you can pass.
- 描述：In the text, caption content: "It's something you have to complete on your own before the exam." This sentence could be a man describing a task or thing that one must accomplish independently prior to an exam. Given the urgency and significance conveyed in the individual's tone as described through audio clues, as well as the man's serious and thoughtful expression depicted in the video, we can infer that this statement might carry a sense of responsibility and immediacy. Therefore, this sentence may emphasize the importance and urgency of completing the task, aligning with the man's overall portrayal of contemplation and introspection.

### 近邻5：samplenew3_00014376

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, confusion, stress, uncertainty
- 与query gold精确词面重合：∅
- 字幕：I carefully thought about it and I don't even know how to be born or die.
- 描述：In the text, the caption reads: "I gave it some thought, not even knowing if I'll live or die." This sentence might be a man contemplating or expressing his confusion and uncertainty. Given the emotional state described in the audio clues, characterized by high stress and anxiety, and the visual cues of the man looking down, possibly showing signs of shyness, tension, or deep thought, we can infer that this sentence might be the man expressing his bewilderment and uncertainty about life and death, the future, or major decisions. This sense of confusion and uncertainty could be a result of the pressure and anxiety stemming from his professional environment.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

## 112. samplenew3_00047065｜gain｜ΔF1 +1.000000

gold：anger, frustration

query字幕：The queen is only more headache than us, and the queen is not in a hurry, why should we be in a hurry.

源标注描述：In the text, the subtitle reads: "The queen is only more headache than us. The queen is not in a hurry, why are we in a hurry?" This sentence may be the speaker's evaluation or reaction to someone or a group. Based on the aggressive and forceful tone described in the audio clues, along with the sense of urgency and the repetition and emphasis of certain words, we can infer that this sentence may carry a tone of dissatisfaction or anger. The speaker may be unhappy with the actions or attitudes of someone or a group, believing that they are not aware of the seriousness of the problem or taking action to solve it. Therefore, this sentence expresses the speaker's feelings of frustration and anger.

off原始输出：The character's emotional state is calm, rational, understanding, empathy.

retrieval原始输出：The character's emotional state is anger, frustration.

|方法|规范化标签|F1（既有）|TP|FP|FN|
|---|---|---:|---:|---:|---:|
|off|calm, empathy, rational, understanding|0.000000|0|4|2|
|retrieval|anger, frustration|1.000000|2|0|0|

已确认的词面计分事实：

- 既有冻结评分下，F1由0.000000变为1.000000，差值+1.000000。
- TP变化+2，FP变化-4，FN变化-2。
- 五个实际近邻ID均在fit清单，未见同ID或同manifest group检索。
- 相对off新增命中的gold标签：anger, frustration。
- 相对off移除未精确匹配gold的标签：calm, empathy, rational, understanding。

gate：0.120033041；Memory启用：True。

人工复核候选（不表示等价，不改变原评分）：

表面词形：{"off": [], "retrieval": []}

相关语义：{"off": [], "retrieval": []}

实际5近邻证据：

### 近邻1：samplenew3_00016623

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：pride, satisfaction
- 与query gold精确词面重合：∅
- 字幕：These clothes still have to be made by yourself.
- 描述：In the text, the caption reads: "These clothes have to be made by hand." Based on the video hints of the woman wearing traditional Chinese attire and the decorative elements in her surroundings, it can be inferred that she might be discussing her experience or skill in sewing clothes herself. Given the audio clues describing an individual experiencing a range of emotions, such as frustration, annoyance, even anger, alongside potentially experiencing positive feelings like excitement or enthusiasm, we cannot accurately determine her emotional state during this phrase. However, considering the video hints of the woman's confident and decisive body language, along with her calm demeanor and tranquil environment, it can be speculated that she expresses a sense of pride and satisfaction in this sentence, because she is able to make her own clothes.

### 近邻2：samplenew3_00050213

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anger, anxiety, helplessness
- 与query gold精确词面重合：anger
- 字幕：If I can help him, how could I stay silent?
- 描述：In the text, caption content: "If I could help him, why wouldn't I speak up?" This sentence might be a self-questioning or inner monologue for a female in a video. Based on the audio cues describing the speaker's's tense, excited voice and high pitch, as well as the video clues showing the woman's expressions of surprise and curiosity, we can infer that this sentence may carry an anxious, helpless, or angry emotion. The female might feel unable to assist others when facing a dilemma or problem, leading to a sense of helplessness and disappointment. This alignss with the negative emotional experience deduction described in the audio cues.

### 近邻3：samplenew3_00081746

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anticipation, excitement, joy, love, positive attitude, support
- 与query gold精确词面重合：∅
- 字幕：When I heard Jinxi say that she was eight months pregnant.
- 描述：In the text, the subtitle reads, "I heard Jinxi say when she was eight months pregnant." Based on the audio clues describing the individual's likely experience of a range of emotions related to pregnancy, such as excitement, anticipation, and anxiety, as well as a range of emotions related to their partner, such as joy, love, and support, we can infer that this sentence is the individual mentioning their pregnancy to someone else. Based on the mention of being eight months pregnant in the subtitle, we can further infer that the individual is likely in the later stages of pregnancy, which may bring about some physical discomfort and fatigue. Therefore, this sentence likely expresses the individual's positive attitude and anticipation towards their pregnancy, while also implying that they are sharing their joy and support with others.

### 近邻4：samplenew3_00053531

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：anxiety, pressure, respect
- 与query gold精确词面重合：∅
- 字幕：Also, always remind him to respect and be peaceful to his father.
- 描述：In the text, the subtitle reads: "It's good to constantly remind him to respect and settle down with his father." This sentence may be the woman's advice or response to someone nearby. Based on the emotional clues related to the individual's relationship with their father described in the audio, including being reminded of their father's expectations, feeling pressure and anxiety, and respecting their father's opinions, we can infer that this sentence may be the woman advising someone nearby to constantly remind themselves to respect and settle down with their father. Therefore, this sentence expresses the woman's respect for her father and her emphasis on traditional values.

### 近邻5：samplenew3_00055986

- 来源：fit；同ID：False；同manifest group：False
- 规范化标签：neutral
- 与query gold精确词面重合：∅
- 字幕：Is it better to use coral or black jade for Hua Hua?
- 描述：In the text, the subtitle content says, "Is it better to use coral or black jade for Huahua?" This sentence is about Huahua's choice between using coral or black jade. Based on the neutral facial expression and body language described in the video clues, as well as the negative emotions described in the audio clues, we can infer that this sentence may be the woman asking or discussing a topic unrelated to her personal emotions. She may be trying to shift attention or seeking others' opinions to alleviate her own emotions. Therefore, this sentence may not be directly related to the woman's emotional state, but rather a way of diverting attention or seeking help from others.

未解决的归因：off与retrieval是分别训练的LoRA；文本近邻的重合/差异和小gate均不能单独证明误检索、标签复制、gate抑制或学习率原因。需等待同checkpoint干预结果及必要的视听盲审。

