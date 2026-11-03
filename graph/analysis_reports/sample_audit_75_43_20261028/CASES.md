# 72例逐样本证据目录

OV逐样本F不等于官方F_s；满HIT不等于排他正确。选取规则见REPORT.md。

## 1. MER2023 / sample_00000714 — 起点/赢家均零命中或判错

- 参考：sad；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 诊断质量：0.0000→0.0000；50权重零/错47次，满/对0次。
- 模型字幕：Also, last time we had me write a written review, this review might be filed in my records.
- 中文：还因为，我们上次让我写书面检查，这个检查可能要夹在我的档案里。
- 起点回答：The character's emotional state is anxiety, tension, concern, unease.
- 赢家回答：The character's emotional state is nervous, concerned, uneasy, worried, anxious.
- 起点抽取：[anxiety, tension, concern, unease]
- 赢家抽取：[nervous, concerned, uneasy, worried, anxious]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_UNCERTAINTY_HEDGE, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_HIGH, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, AUD_VOICE_TENSE, AUD_VOICE_TREMBLING, AUD_CRYING_SOBBING_PRESENT, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN
- 图候选：despair, depressed, grief（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.824053795005745}, {"state": "AGC_MIXED", "relative_support": 0.14096614846924252}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.5015113359449285}, {"state": "AEX_EXPECTED", "relative_support": 0.4984886640550714}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.46157432002411236}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3097877253812501}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7929488970413253}, {"state": "ACT_CERTAIN", "relative_support": 0.20705110295867474}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9951554139178397}, {"state": "ACP_HIGH", "relative_support": 0.00484458608216033}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00000714.avi

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.0000|The character's emotional state is tension, concern.|
|base35_B|0.0000|The emotional state is concern, tension, uncertainty, emotional fragility.|
|base35_C|0.2000|The character's emotional state is tension, uncertainty, stress, confusion.|
|base35_D|1.0000|The character might be feeling sad, fear, anger.|
|base35_E|1.0000|The character might be feeling sad, fearful, and angry.|
|base35_F|1.0000|The character's emotional state is sad, fear, anger.|
|graph40_A|0.0000|The character's emotional state is tension, unease, uncertainty, pressure, concern.|
|graph40_B|0.0000|The character's emotional state is tension, unease, uncertainty, concern.|
|graph40_C|0.0000|The character's emotional state is tension, unease, uncertainty, pressure, anxiety.|
|graph40_D|0.0000|The character's emotional state is tension, anxiety, stress, unease.|
|graph40_E|0.0000|The character's emotional state is tension, unease, uncertainty, pressure, concern.|
|graph40_F|0.0000|The character's emotional state is tension, unease.|
|base35_G|0.0000|The emotional state of the character is uncertain, worried.|
|graph40_G|0.0000|The character's emotional state is tension, unease, uncertainty, pressure, anxiety.|

## 2. MER2023 / sample_00003175 — 起点/赢家均零命中或判错

- 参考：happy；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 诊断质量：0.0000→0.0000；50权重零/错50次，满/对0次。
- 模型字幕：I don't know how.
- 中文：我就不会了。
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is confused, frustrated, helpless.
- 起点抽取：[]
- 赢家抽取：[confused, frustrated, helpless]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, focused, care（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6168610879885909}, {"state": "AGC_INCONGRUENT", "relative_support": 0.3831389120114092}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7762538582836533}, {"state": "AAG_SELF", "relative_support": 0.22374614171634674}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.992282656370732}, {"state": "ACT_CERTAIN", "relative_support": 0.0077173436292679864}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7150791864339432}, {"state": "ACP_LOW", "relative_support": 0.28492081356605686}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00003175.avi

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.0000|The character's emotional state is neutral.|
|base35_B|0.0000|The character's emotional state is uncertain, confused, surprised, concerned.|
|base35_C|0.0000|The character's emotional state is uncertain, anxious, overwhelmed.|
|base35_D|0.0000|The character's emotional state is uncertain, confused, surprised, concerned.|
|base35_E|0.0000|The character's emotional state is uncertain, anxious, overwhelmed.|
|base35_F|0.0000|The character's emotional state is uncertain, unresolved.|
|graph40_A|0.0000|The character's emotional state is sadness, frustration, uncertainty, confusion.|
|graph40_B|0.0000|The character's emotional state is sadness, frustration, overwhelmed, stress, helplessness, confusion.|
|graph40_C|0.0000|The character's emotional state is sadness, frustration, hopelessness, confusion, helplessness.|
|graph40_D|0.0000|The character's emotional state is sadness, frustration, overwhelmed, stress, helplessness, confusion.|
|graph40_E|0.0000|The character's emotional state is sadness, frustration, hopelessness, confusion, helplessness.|
|graph40_F|0.0000|The character's emotional state is sadness, frustration, hopelessness, confusion, helplessness.|
|base35_G|0.0000|The character's emotional state is uncertain, unresolved.|
|graph40_G|0.0000|The character's emotional state is sadness, frustration, hopelessness, confusion, helplessness.|

## 3. MER2023 / sample_00004071 — 起点/赢家均满命中或判对

- 参考：happy；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 诊断质量：1.0000→1.0000；50权重零/错0次，满/对41次。
- 模型字幕：Got it, this, this, this, this shopping card.
- 中文：知道了，这个，这个，这个，这个购物卡
- 起点回答：The character's emotional state is excited, joyful, happy, satisfied.
- 赢家回答：The character's emotional state is excitement, surprise, joy.
- 起点抽取：[excited, joyful, happy, satisfied]
- 赢家抽取：[excitement, surprise, joy]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_EXCLAMATION_INTERJECTION, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT, VIS_HEAD_LOWERED
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.9488350876903145}, {"state": "AGC_INCONGRUENT", "relative_support": 0.03621222826098101}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6563788234181158}, {"state": "AEX_UNEXPECTED", "relative_support": 0.34362117658188407}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5490227259226673}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.25111429428152887}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.505944368723068}, {"state": "ACT_CERTAIN", "relative_support": 0.49405563127693203}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7796834807466997}, {"state": "ACP_LOW", "relative_support": 0.2203165192533002}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00004071.avi

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|1.0000|The character's emotional state is excitement, joy, pleasure.|
|base35_B|0.4000|The emotional state of the woman can be inferred from a series of emotions experienced by an individual as described in the audio cues, including a mix of excitement and frustration. The excited tone, urgency, and sense of determination, combined with hesitation and uncertainty indicated by the tone, suggest that she may be experiencing a range of complex emotions. Her facial expressions and body language in the video also hint at excitement and anticipation. She raises her eyebrows and squints her eyes, and her smile suggests that she is sharing a positive emotion with others, while also possibly feeling some tension or unease. Therefore, the individual might be expressing excitement and anticipation towards a shopping card in this subtitle content.|
|base35_C|1.0000|The character's emotional state is excitement, anticipation, pleasure.|
|base35_D|0.8000|The emotional state of the woman can be inferred from a series of emotions experienced by an individual as described in the audio cues, including a mix of excitement and frustration. The excited tone, urgency, and sense of determination, combined with hesitation and uncertainty indicated by the tone, suggest that she may be experiencing a range of complex emotions. Her facial expressions and body language in the video also hint at excitement and anticipation. She raises her eyebrows and squints her eyes, and her smile suggests that she is sharing a positive emotion with others, while also possibly feeling some tension or unease. Therefore, the individual might be expressing excitement and anticipation towards a shopping card in this subtitle content.|
|base35_E|1.0000|The character's emotional state is excitement, anticipation, pleasure.|
|base35_F|1.0000|The character's emotional state is excitement, anticipation, pleasure.|
|graph40_A|1.0000|The character's emotional state is excitement, joy, pleasure.|
|graph40_B|1.0000|The character's emotional state is excitement, joy, pleasure.|
|graph40_C|1.0000|The character's emotional state is excitement, joy, pleasure.|
|graph40_D|1.0000|The character's emotional state is excitement, joy, pleasure.|
|graph40_E|1.0000|The character's emotional state is excitement, joy, pleasure.|
|graph40_F|1.0000|The character's emotional state is excitement, joy, pleasure.|
|base35_G|1.0000|The character's emotional state is excitement, anticipation, pleasure.|
|graph40_G|1.0000|The character's emotional state is excitement, joy, pleasure.|

## 4. MER2023 / sample_00003944 — 起点/赢家均满命中或判对

- 参考：worried；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 诊断质量：1.0000→1.0000；50权重零/错0次，满/对50次。
- 模型字幕：Where on earth is he?
- 中文：他到底在哪儿呢？
- 起点回答：The character's emotional state is tense, anxious, worry, unease.
- 赢家回答：The character's emotional state is anxiety, tension, disappointment, frustration.
- 起点抽取：[tense, anxious, worry, unease]
- 赢家抽取：[anxiety, tension, disappointment, frustration]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8312737451495933}, {"state": "AGC_CONGRUENT", "relative_support": 0.16872625485040674}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.982747358345166}, {"state": "AEX_EXPECTED", "relative_support": 0.017252641654834}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 1.0}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8802810658853712}, {"state": "ACT_CERTAIN", "relative_support": 0.11971893411462872}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6949695410880924}, {"state": "ACP_HIGH", "relative_support": 0.30503045891190755}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00003944.avi

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|1.0000|The character's emotional state is tense, anxious.|
|base35_B|1.0000|The character's emotional state is anxiety, tension, impatience, frustration.|
|base35_C|1.0000|The character's emotional state is anxious, emotionally distant, under stress, worried.|
|base35_D|1.0000|The character's emotional state is anxious, urgent, troubled.|
|base35_E|1.0000|The character's emotional state is anxious, urgent, impatient.|
|base35_F|1.0000|The character's emotional state is anxious, urgent.|
|graph40_A|1.0000|The character's emotional state is anxiety, tension.|
|graph40_B|1.0000|The character's emotional state is anxiety, tension, impatience, frustration.|
|graph40_C|1.0000|The character's emotional state is anxiety, tension.|
|graph40_D|1.0000|The character's emotional state is anxiety, tension.|
|graph40_E|1.0000|The character's emotional state is anxiety, tension.|
|graph40_F|1.0000|The character's emotional state is anxiety, tension.|
|base35_G|1.0000|The character's emotional state is anxious, emotionally distant, under stress, worried.|
|graph40_G|1.0000|The character's emotional state is anxiety, tension.|

## 5. MER2023 / sample_00006600 — 相对起点诊断改善

- 参考：surprise；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 诊断质量：0.2500→0.5000；50权重零/错0次，满/对5次。
- 模型字幕：Where did you hear that San Ge has a partner?
- 中文：三哥哪有对象？你听谁说的？
- 起点回答：The character's emotional state is questioning, disbelief, skepticism.
- 赢家回答：The character's emotional state is confused, skeptical, doubtful, mistrustful.
- 起点抽取：[questioning, disbelief, skepticism]
- 赢家抽取：[confused, skeptical, doubtful, mistrustful]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_RHETORICAL_QUESTION, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.975083788753391}, {"state": "AEX_EXPECTED", "relative_support": 0.024916211246609067}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.889074683919649}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.11092531608035096}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9703065924096971}, {"state": "ACT_CERTAIN", "relative_support": 0.029693407590302985}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00006600.avi

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.5000|The character's emotional state is confused, skeptical, doubtful.|
|base35_B|0.7500|The character's emotional state is confused, dissatisfied, challenged, uncertain, doubtful.|
|base35_C|0.7500|The character's emotional state is confused, dissatisfied, challenged, uncertain, helpless.|
|base35_D|0.7500|The character's emotional state is confused, dissatisfied, challenged, uncertain, doubtful.|
|base35_E|0.7500|The character's emotional state is confused, dissatisfied, challenged, uncertain, helpless.|
|base35_F|0.7500|The character's emotional state is confused, dissatisfied, challenged, uncertain, overwhelmed.|
|graph40_A|0.5000|The character's emotional state is skepticism, challenge, dissatisfaction, anxiety, tension.|
|graph40_B|0.5000|The character's emotional state is skepticism, questioning, dissatisfaction, anxiety, irritability, frustration.|
|graph40_C|0.5000|The character's emotional state is skepticism, challenge, dissatisfaction, anxiety, tension.|
|graph40_D|0.5000|The character's emotional state is skepticism, questioning, dissatisfaction, anxiety, irritability, frustration.|
|graph40_E|0.5000|The character's emotional state is skepticism, challenge, dissatisfaction, anxiety, tension.|
|graph40_F|0.5000|The character's emotional state is skepticism, challenge, dissatisfaction, anxiety, irritability.|
|base35_G|0.7500|The character's emotional state is confused, dissatisfied, challenged, uncertain, overwhelmed.|
|graph40_G|0.5000|The character's emotional state is skepticism, challenge, dissatisfaction, anxiety, irritability.|

## 6. MER2023 / sample_00003805 — 相对起点诊断改善

- 参考：angry；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 诊断质量：0.0000→1.0000；50权重零/错9次，满/对31次。
- 模型字幕：You go, go, go, go.
- 中文：你走吧，走，走，走。
- 起点回答：The character's emotional state is encouraging, supportive, positive.
- 赢家回答：The character's emotional state is frustrated, angry, supportive, encouraging, understanding.
- 起点抽取：[encouraging, supportive, positive]
- 赢家抽取：[frustrated, angry, supportive, encouraging, understanding]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_DESIRE_NEED, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9597506111545809}, {"state": "AGC_CONGRUENT", "relative_support": 0.04024938884541911}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8838793505692132}, {"state": "AEX_EXPECTED", "relative_support": 0.11612064943078693}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7470755219265004}, {"state": "AAG_SELF", "relative_support": 0.12805614921499203}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9607175212233054}, {"state": "ACT_CERTAIN", "relative_support": 0.039282478776694635}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.898292813478636}, {"state": "ACP_HIGH", "relative_support": 0.10170718652136403}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00003805.avi

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|1.0000|The character's emotional state is impatience, frustration, annoyance, stress, distress.|
|base35_B|0.0000|The emotional state is fear, anxiety, overwhelmed, under pressure.|
|base35_C|0.0000|The character's emotional state is anxious, overwhelmed, stressed.|
|base35_D|0.0000|The emotional state is fear, anxiety, overwhelmed, under pressure.|
|base35_E|0.0000|The character's emotional state is anxious, overwhelmed, stressed.|
|base35_F|0.0000|The character's emotional state is anxious, overwhelmed, stressed.|
|graph40_A|1.0000|The character's emotional state is anger, frustration, anxiety.|
|graph40_B|1.0000|The character's emotional state is anger, frustration, anxiety.|
|graph40_C|1.0000|The character's emotional state is anger, frustration, anxiety.|
|graph40_D|1.0000|The character's emotional state is anger, frustration, anxiety.|
|graph40_E|1.0000|The character's emotional state is anger, frustration, anxiety.|
|graph40_F|1.0000|The character's emotional state is anger, frustration, anxiety.|
|base35_G|0.0000|The character's emotional state is anxious, overwhelmed, stressed.|
|graph40_G|1.0000|The character's emotional state is anger, frustration, anxiety.|

## 7. MER2023 / sample_00000766 — 相对起点诊断恶化

- 参考：worried；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 诊断质量：0.6000→0.0000；50权重零/错31次，满/对5次。
- 模型字幕：Stop thinking about it, let's leave it to fate.
- 中文：别想了，这看缘分吧。
- 起点回答：The character's emotional state is resignation, acceptance, frustration, stress.
- 赢家回答：The character's emotional state is comfort, resignation.
- 起点抽取：[resignation, acceptance, frustration, stress]
- 赢家抽取：[comfort, resignation]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, TXT_UNCERTAINTY_HEDGE, TXT_DESIRE_NEED, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN
- 图候选：hesitant, curious, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9878777615387118}, {"state": "AGR_RELEVANT", "relative_support": 0.012122238461288274}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7047302420813802}, {"state": "AGC_CONGRUENT", "relative_support": 0.21908241073665174}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.836308372539025}, {"state": "AEX_UNEXPECTED", "relative_support": 0.1636916274609751}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6165464351977713}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.35898123629594125}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7392216854963827}, {"state": "ACT_CERTAIN", "relative_support": 0.2607783145036173}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7186812821016946}, {"state": "ACP_HIGH", "relative_support": 0.28131871789830537}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00000766.avi

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.0000|The character's emotional state is calm, accepting.|
|base35_B|0.6000|The emotional state is negative, depressed, helpless.|
|base35_C|0.0000|The character's emotional state is calm, accepting.|
|base35_D|0.6000|The emotional state is negative, depressed, helpless.|
|base35_E|0.0000|The character's emotional state is calm, accepting.|
|base35_F|0.6000|The character's emotional state is negative, pessimistic, helpless.|
|graph40_A|0.0000|The character's emotional state is calm, accepting.|
|graph40_B|0.2000|The character's emotional state is calm, detached, acceptance, letting-go.|
|graph40_C|0.2000|The character's emotional state is calm, detached, sorrowful, melancholic.|
|graph40_D|0.2000|The character's emotional state is calm, detached, acceptance, letting-go.|
|graph40_E|0.2000|The character's emotional state is calm, detached, sorrowful, melancholic.|
|graph40_F|0.2000|The character's emotional state is calm, detached.|
|base35_G|0.6000|The character's emotional state is negative, pessimistic, helpless.|
|graph40_G|0.2000|The character's emotional state is calm, detached.|

## 8. MER2023 / sample_00004280 — 相对起点诊断恶化

- 参考：angry；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 诊断质量：0.4000→0.0000；50权重零/错44次，满/对2次。
- 模型字幕：Is it interesting? Cheng Dongqing.
- 中文：有意思吗？成东青。
- 起点回答：The character's emotional state is teasing, humorous, excited.
- 赢家回答：The character's emotional state is excited, expectant.
- 起点抽取：[teasing, humorous, excited]
- 赢家抽取：[excited, expectant]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_RHETORICAL_QUESTION, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT, VIS_HEAD_LOWERED
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9728386556626363}, {"state": "AGR_RELEVANT", "relative_support": 0.027161344337363797}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.4647613821852872}, {"state": "AGC_INCONGRUENT", "relative_support": 0.3982562234086946}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7258161902585664}, {"state": "AEX_EXPECTED", "relative_support": 0.2741838097414336}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8325187933812537}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.10573859880567102}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8123121764798987}, {"state": "ACT_CERTAIN", "relative_support": 0.18768782352010124}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.696811056301359}, {"state": "ACP_HIGH", "relative_support": 0.30318894369864097}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00004280.avi

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.0000|The character's emotional state is excited, anxious, tense.|
|base35_B|0.0000|The emotional state is interested, curious, anxious, tense.|
|base35_C|0.0000|The character's emotional state is excited, anxious, tense.|
|base35_D|0.0000|The emotional state is interested, curious, anxious, tense.|
|base35_E|0.0000|The character's emotional state is excited, anxious, tense.|
|base35_F|0.0000|The character's emotional state is excited, anxious, tense.|
|graph40_A|0.0000|The character's emotional state is excited, anxious, positive.|
|graph40_B|0.0000|The character's emotional state is excited, anxious, interesting, intriguing.|
|graph40_C|0.0000|The character's emotional state is excited, anxious, positive.|
|graph40_D|0.0000|The character's emotional state is excited, anxious, interesting, intriguing.|
|graph40_E|0.0000|The character's emotional state is excited, anxious, positive.|
|graph40_F|0.0000|The character's emotional state is excited, anxious, positive.|
|base35_G|0.0000|The character's emotional state is excited, anxious, tense.|
|graph40_G|0.0000|The character's emotional state is excited, anxious, positive.|

## 9. MER2024 / samplenew_00011679 — 起点/赢家均零命中或判错

- 参考：sad；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 诊断质量：0.0000→0.0000；50权重零/错41次，满/对0次。
- 模型字幕：何处？葛？寻？机密，远岭。
- 中文：何处？葛？寻？机密，远岭。
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is tension, anxiety, fear.
- 起点抽取：[]
- 赢家抽取：[tension, anxiety, fear]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_RHETORICAL_QUESTION, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_RISING, VIS_MOUTH_CORNERS_DOWN, VIS_HEAD_LOWERED
- 图候选：disappointed, bewildered, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9316122299545214}, {"state": "AGC_MIXED", "relative_support": 0.06838777004547854}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8712314019042137}, {"state": "AEX_EXPECTED", "relative_support": 0.12876859809578628}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.4863859534215418}, {"state": "AAG_SELF", "relative_support": 0.3002332929444183}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00011679.mp4

## 10. MER2024 / samplenew_00033356 — 起点/赢家均零命中或判错

- 参考：worried；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 诊断质量：0.0000→0.0000；50权重零/错27次，满/对15次。
- 模型字幕：从成都，到消停，再快，也需要很多日啊。
- 中文：从成都，到消停，再快，也需要很多日啊。
- 起点回答：The character's emotional state is contemplative, analytical, curious, interested.
- 赢家回答：The character's emotional state is contemplative, distant, nostalgic, longing.
- 起点抽取：[contemplative, analytical, curious, interested]
- 赢家抽取：[contemplative, distant, nostalgic, longing]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN
- 图候选：depressed, despair, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.661397708912107}, {"state": "AGC_MIXED", "relative_support": 0.18611188173997978}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6259115180901322}, {"state": "AEX_UNEXPECTED", "relative_support": 0.37408848190986776}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5276921136452734}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3501078900171773}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6031084186566781}, {"state": "ACT_UNCERTAIN", "relative_support": 0.3968915813433219}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8713722872838228}, {"state": "ACP_HIGH", "relative_support": 0.12862771271617723}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00033356.mp4

## 11. MER2024 / samplenew_00004144 — 起点/赢家均满命中或判对

- 参考：sad；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 诊断质量：1.0000→1.0000；50权重零/错13次，满/对27次。
- 模型字幕：让阿牛好好看看。
- 中文：让阿牛好好看看。
- 起点回答：The character's emotional state is anger, anxiety, sadness, surprise, disgust.
- 赢家回答：The character's emotional state is anger, frustration, anxiety, stress, sadness, surprise.
- 起点抽取：[anger, anxiety, sadness, surprise, disgust]
- 赢家抽取：[anger, frustration, anxiety, stress, sadness, surprise]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT, VIS_TEARING_PRESENT, VIS_HEAD_LOWERED
- 图候选：depressed, despair, disappointed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9535513379406503}, {"state": "AGC_MIXED", "relative_support": 0.04644866205934978}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7744402017325906}, {"state": "AEX_EXPECTED", "relative_support": 0.2255597982674094}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.348620495408792}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.33467281658947906}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7749634898293718}, {"state": "ACT_CERTAIN", "relative_support": 0.22503651017062815}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00004144.mp4

## 12. MER2024 / samplenew_00040546 — 起点/赢家均满命中或判对

- 参考：angry；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 诊断质量：1.0000→1.0000；50权重零/错0次，满/对50次。
- 模型字幕：你想替那几只走狗出头？
- 中文：你想替那几只走狗出头？
- 起点回答：The character's emotional state is anger, frustration, dissatisfaction.
- 赢家回答：The character's emotional state is anger, frustration.
- 起点抽取：[anger, frustration, dissatisfaction]
- 赢家抽取：[anger, frustration]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_DESIRE_NEED, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_VOICE_TENSE, VIS_BROWS_FURROWED, VIS_EYES_WIDENED
- 图候选：anger, disappointed, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.8928930928858726}, {"state": "AGR_RELEVANT", "relative_support": 0.10710690711412749}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8499418792603103}, {"state": "AGC_CONGRUENT", "relative_support": 0.15005812073968972}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8881408113947206}, {"state": "AEX_EXPECTED", "relative_support": 0.11185918860527948}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8422816570937467}, {"state": "AAG_SELF", "relative_support": 0.15771834290625336}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8405350452977381}, {"state": "ACT_CERTAIN", "relative_support": 0.15946495470226188}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6289855509192286}, {"state": "ACP_HIGH", "relative_support": 0.3710144490807715}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00040546.mp4

## 13. MER2024 / samplenew_00017770 — 相对起点诊断改善

- 参考：sad；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 诊断质量：0.0000→1.0000；50权重零/错9次，满/对40次。
- 模型字幕：随父母到渭城，来，投奔亲戚。
- 中文：随父母到渭城，来，投奔亲戚。
- 起点回答：The character's emotional state is peaceful, contented.
- 赢家回答：The character's emotional state is tranquility, contentment, sadness, nostalgia, fear, anxiety, stress.
- 起点抽取：[peaceful, contented]
- 赢家抽取：[tranquility, contentment, sadness, nostalgia, fear, anxiety, stress]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN
- 图候选：depressed, disappointed, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8255353252263314}, {"state": "AGC_CONGRUENT", "relative_support": 0.10798002713957673}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6544596816669103}, {"state": "AEX_UNEXPECTED", "relative_support": 0.34554031833308985}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5401845728881487}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3084407250493478}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.5346920298682049}, {"state": "ACT_CERTAIN", "relative_support": 0.4653079701317951}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8262792389183026}, {"state": "ACP_HIGH", "relative_support": 0.17372076108169734}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00017770.mp4

## 14. MER2024 / samplenew_00005133 — 相对起点诊断改善

- 参考：happy；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 诊断质量：0.4000→0.8000；50权重零/错0次，满/对25次。
- 模型字幕：当然，是真的了，留，我看着，都眼热呢。
- 中文：当然，是真的了，留，我看着，都眼热呢。
- 起点回答：The character's emotional state is excited, enthusiastic, envious.
- 赢家回答：The character's emotional state is excited, enthusiastic, admiring.
- 起点抽取：[excited, enthusiastic, envious]
- 赢家抽取：[excited, enthusiastic, admiring]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.916125942128973}, {"state": "AGC_INCONGRUENT", "relative_support": 0.04460196610596035}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6219948848912987}, {"state": "AEX_UNEXPECTED", "relative_support": 0.3780051151087013}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6068087498157777}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.25222640805196556}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5784318999560468}, {"state": "ACT_UNCERTAIN", "relative_support": 0.4215681000439531}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8505010665360418}, {"state": "ACP_LOW", "relative_support": 0.14949893346395818}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00005133.mp4

## 15. MER2024 / samplenew_00011342 — 相对起点诊断恶化

- 参考：happy；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 诊断质量：1.0000→0.0000；50权重零/错13次，满/对10次。
- 模型字幕：该知道，不认识我了。
- 中文：该知道，不认识我了。
- 起点回答：The character's emotional state is anxious, tense, impatient, urgent, dissatisfaction, urgency, mockery, joy, curiosity, interest.
- 赢家回答：The character's emotional state is confused, anxious, frustrated, angry.
- 起点抽取：[anxious, tense, impatient, urgent, dissatisfaction, urgency, joy, curiosity, interest]
- 赢家抽取：[confused, anxious, frustrated, angry]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, AUD_INTONATION_RISING, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7261972811836453}, {"state": "AGC_INCONGRUENT", "relative_support": 0.27380271881635476}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6913315256758661}, {"state": "AEX_EXPECTED", "relative_support": 0.30866847432413397}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.42384492202415536}, {"state": "AAG_SELF", "relative_support": 0.39181356069144574}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8704813869475152}, {"state": "ACT_CERTAIN", "relative_support": 0.12951861305248477}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5310737707208917}, {"state": "ACP_LOW", "relative_support": 0.4689262292791083}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00011342.mp4

## 16. MER2024 / samplenew_00040578 — 相对起点诊断恶化

- 参考：angry；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 诊断质量：1.0000→0.4000；50权重零/错7次，满/对4次。
- 模型字幕：那就说明，我们的政策出了问题呀。
- 中文：那就说明，我们的政策出了问题呀。
- 起点回答：The character's emotional state is concerned, perplexed, frustrated, angry.
- 赢家回答：The character's emotional state is disappointment, frustration, anxiety, concern.
- 起点抽取：[concerned, perplexed, frustrated, angry]
- 赢家抽取：[disappointment, frustration, anxiety, concern]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_EXCLAMATION_INTERJECTION, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN
- 图候选：disappointed, anger, depressed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 1.0}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8613065336831282}, {"state": "ACT_CERTAIN", "relative_support": 0.1386934663168718}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00040578.mp4

## 17. MELD / test_dia57_utt5 — 起点/赢家均零命中或判错

- 参考：disgust；赢家：from_30_epoch_39_MELD；起点epoch30。
- 诊断质量：0.0000→0.0000；50权重零/错50次，满/对0次。
- 模型字幕：But you will always be the guy who peed on me.
- 中文：但你永远都会是那个对我撒尿的人。
- 起点回答：The character's emotional state is anger, dissatisfaction.
- 赢家回答：The character's emotional state is angry, dissatisfied.
- 起点抽取：[anger, dissatisfaction]
- 赢家抽取：[angry, dissatisfied]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_LAUGHTER_PRESENT, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, disappointed, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.4206002566450682}, {"state": "AGC_INCONGRUENT", "relative_support": 0.32642050214405016}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8677980132964631}, {"state": "AEX_EXPECTED", "relative_support": 0.13220198670353683}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7578222980838135}, {"state": "AAG_SELF", "relative_support": 0.24217770191618643}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.621713301767678}, {"state": "ACT_CERTAIN", "relative_support": 0.378286698232322}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5541074142178575}, {"state": "ACP_LOW", "relative_support": 0.44589258578214264}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia57_utt5.mp4

## 18. MELD / test_dia260_utt8 — 起点/赢家均零命中或判错

- 参考：anger；赢家：from_30_epoch_39_MELD；起点epoch30。
- 诊断质量：0.0000→0.0000；50权重零/错48次，满/对0次。
- 模型字幕：Give me your hands.  Strings. Gimme it!  Pick. Do you want to learn to play guitar?
- 中文：给我你的手。弦。给我！挑选。你想学弹吉他吗？
- 起点回答：The character's emotional state is positive, energetic, excited.
- 赢家回答：The character's emotional state is excited, anticipatory, positive, enthusiastic.
- 起点抽取：[positive, energetic, excited]
- 赢家抽取：[excited, anticipatory, positive, enthusiastic]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_PAUSE_LONG, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_SMILE_PRESENT
- 图候选：hopeful, joy, delightful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6658649040480836}, {"state": "AGC_MIXED", "relative_support": 0.18602997437427632}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5284196918594216}, {"state": "AEX_UNEXPECTED", "relative_support": 0.47158030814057844}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5296237363024493}, {"state": "AAG_OTHER", "relative_support": 0.2633470373664301}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6384343284922178}, {"state": "ACT_CERTAIN", "relative_support": 0.3615656715077823}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.6983103755650507}, {"state": "ACP_LOW", "relative_support": 0.30168962443494923}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia260_utt8.mp4

## 19. MELD / test_dia72_utt13 — 起点/赢家均满命中或判对

- 参考：anger；赢家：from_30_epoch_39_MELD；起点epoch30。
- 诊断质量：1.0000→1.0000；50权重零/错15次，满/对24次。
- 模型字幕：Go get back on that case honey!
- 中文：去吧，亲爱的，重新处理那个案子！
- 起点回答：The character's emotional state is angry, frustrated, passionate.
- 赢家回答：The character's emotional state is frustrated, angry, encouraging.
- 起点抽取：[angry, frustrated, passionate]
- 赢家抽取：[frustrated, angry, encouraging]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_DESIRE_NEED, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_LAUGHTER_PRESENT, VIS_BROWS_FURROWED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN
- 图候选：anger, disappointed, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7099732913635264}, {"state": "AGC_CONGRUENT", "relative_support": 0.29002670863647356}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8824748937189051}, {"state": "AEX_EXPECTED", "relative_support": 0.11752510628109497}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8215583578906039}, {"state": "AAG_SELF", "relative_support": 0.17844164210939603}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8786605691182542}, {"state": "ACT_CERTAIN", "relative_support": 0.12133943088174579}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6406317577250696}, {"state": "ACP_HIGH", "relative_support": 0.3593682422749304}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia72_utt13.mp4

## 20. MELD / test_dia262_utt16 — 起点/赢家均满命中或判对

- 参考：surprise；赢家：from_30_epoch_39_MELD；起点epoch30。
- 诊断质量：1.0000→1.0000；50权重零/错14次，满/对36次。
- 模型字幕：What?! Oh.
- 中文：什么？哦。
- 起点回答：The character's emotional state is excited, surprised, positive.
- 赢家回答：The character's emotional state is surprised, bewildered.
- 起点抽取：[excited, surprised, positive]
- 赢家抽取：[surprised, bewildered]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_EXCLAMATION_INTERJECTION, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：anxious, care, focused（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7972140881689166}, {"state": "AGC_INCONGRUENT", "relative_support": 0.2027859118310834}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8876999630864405}, {"state": "AAG_SELF", "relative_support": 0.11230003691355953}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9046536406160826}, {"state": "ACT_CERTAIN", "relative_support": 0.09534635938391739}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia262_utt16.mp4

## 21. MELD / test_dia76_utt16 — 相对起点诊断改善

- 参考：joy；赢家：from_30_epoch_39_MELD；起点epoch30。
- 诊断质量：0.8000→1.0000；50权重零/错0次，满/对27次。
- 模型字幕：Ah! Well! There you go! Last to know again! And I'm guessing... since nobody told me... this is Paolo.
- 中文：啊！好吧！你又来了！又是最后一个知道！我猜...因为没有人告诉我...这是保罗。
- 起点回答：The character's emotional state is excitement, curiosity, anticipation.
- 赢家回答：The character's emotional state is excited, happy, amused.
- 起点抽取：[excitement, curiosity, anticipation]
- 赢家抽取：[excited, happy, amused]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_LAUGHTER_PRESENT, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, anger, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7194029211714063}, {"state": "AGC_INCONGRUENT", "relative_support": 0.2805970788285938}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8690754925196087}, {"state": "AEX_EXPECTED", "relative_support": 0.13092450748039122}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7378911319736513}, {"state": "AAG_SELF", "relative_support": 0.2621088680263487}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7917806352258462}, {"state": "ACT_CERTAIN", "relative_support": 0.20821936477415373}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7715149055666697}, {"state": "ACP_LOW", "relative_support": 0.2284850944333303}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia76_utt16.mp4

## 22. MELD / test_dia52_utt7 — 相对起点诊断改善

- 参考：surprise；赢家：from_30_epoch_39_MELD；起点epoch30。
- 诊断质量：0.0000→0.2500；50权重零/错11次，满/对4次。
- 模型字幕：She is?
- 中文：她是谁？
- 起点回答：The character's emotional state is doubt, curiosity.
- 赢家回答：The character's emotional state is questioning, puzzlement, uncertainty, anxiety, stress.
- 起点抽取：[doubt, curiosity]
- 赢家抽取：[questioning, puzzlement, uncertainty, anxiety, stress]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED
- 图候选：anger, confident, disappointed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.75581994632671}, {"state": "AGC_CONGRUENT", "relative_support": 0.24418005367328996}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 1.0}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6247674338452779}, {"state": "ACP_HIGH", "relative_support": 0.37523256615472206}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia52_utt7.mp4

## 23. MELD / test_dia133_utt8 — 相对起点诊断恶化

- 参考：surprise；赢家：from_30_epoch_39_MELD；起点epoch30。
- 诊断质量：1.0000→0.2500；50权重零/错0次，满/对36次。
- 模型字幕：Oh my God.
- 中文：哦，我的天。
- 起点回答：The character's emotional state is surprised, excited, incredulous, emotional stress, overwhelmed, anxiety, tension.
- 赢家回答：The character's emotional state is excited, surprised, happy.
- 起点抽取：[surprised, excited, incredulous, emotional stress, overwhelmed, anxiety, tension]
- 赢家抽取：[excited, happy]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EXCLAMATION_INTERJECTION, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9759000238266733}, {"state": "AEX_EXPECTED", "relative_support": 0.02409997617332672}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.877554188349712}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.12244581165028795}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9666386619272965}, {"state": "ACT_CERTAIN", "relative_support": 0.03336133807270338}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia133_utt8.mp4

## 24. MELD / test_dia274_utt3 — 相对起点诊断恶化

- 参考：joy；赢家：from_30_epoch_39_MELD；起点epoch30。
- 诊断质量：1.0000→0.0000；50权重零/错17次，满/对1次。
- 模型字幕：Yeah! You wanna come?
- 中文：是的！你想来吗？
- 起点回答：The character's emotional state is teasing, playful, positive.
- 赢家回答：The character's emotional state is challenge, mockery, negative emotion.
- 起点抽取：[teasing, playful, positive]
- 赢家抽取：[challenge, mockery, negative emotion]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EXCLAMATION_INTERJECTION, TXT_DESIRE_NEED, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9413315633764763}, {"state": "AGC_CONGRUENT", "relative_support": 0.05866843662352368}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8655675622554706}, {"state": "AEX_EXPECTED", "relative_support": 0.13443243774452943}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7700731839426692}, {"state": "AAG_SELF", "relative_support": 0.22992681605733084}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9902169732633865}, {"state": "ACT_CERTAIN", "relative_support": 0.00978302673661356}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8501926053527152}, {"state": "ACP_HIGH", "relative_support": 0.14980739464728476}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia274_utt3.mp4

## 25. IEMOCAPFour / Ses05F_script03_2_M041 — 起点/赢家均零命中或判错

- 参考：anger；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 诊断质量：0.0000→0.0000；50权重零/错50次，满/对0次。
- 模型字幕：Very music- amusing indeed.
- 中文：非常有趣的音乐。
- 起点回答：The character's emotional state is excited, positive, amused.
- 赢家回答：The character's emotional state is appreciation, joy.
- 起点抽取：[excited, positive, amused]
- 赢家抽取：[joy, appreciation]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7867567542445648}, {"state": "AGC_MIXED", "relative_support": 0.17006980420389967}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6941097443753497}, {"state": "AEX_EXPECTED", "relative_support": 0.3058902556246503}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8509266626975369}, {"state": "AAG_SELF", "relative_support": 0.14907333730246308}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6167329375878867}, {"state": "ACT_CERTAIN", "relative_support": 0.38326706241211334}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.975237343499318}, {"state": "ACP_LOW", "relative_support": 0.02476265650068194}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_script03_2_M041.avi

## 26. IEMOCAPFour / Ses05F_script01_3_F022 — 起点/赢家均零命中或判错

- 参考：sad；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 诊断质量：0.0000→0.0000；50权重零/错44次，满/对2次。
- 模型字幕：how many?
- 中文：多少个？
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is neutral.
- 起点抽取：[]
- 赢家抽取：[neutral]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：AUD_INTONATION_RISING, VIS_LIPS_PRESSED
- 图候选：anxious, motivate, proud（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8979288855946979}, {"state": "AAG_SELF", "relative_support": 0.10207111440530214}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_script01_3_F022.avi

## 27. IEMOCAPFour / Ses05M_script03_1_F003 — 起点/赢家均满命中或判对

- 参考：happy；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 诊断质量：1.0000→1.0000；50权重零/错0次，满/对39次。
- 模型字幕：Now and always, my sweet.
- 中文：现在和永远，我的甜蜜。
- 起点回答：The character's emotional state is joyful, loving, positive.
- 赢家回答：The character's emotional state is love, affection, happiness, satisfaction.
- 起点抽取：[joyful, loving, positive]
- 赢家抽取：[love, affection, happiness, satisfaction]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_POSITIVE, TXT_EVALUATION_POSITIVE, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8743816649247159}, {"state": "AGC_MIXED", "relative_support": 0.11384349051782944}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5893949951625069}, {"state": "AEX_UNEXPECTED", "relative_support": 0.4106050048374931}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.45626920414742533}, {"state": "AAG_OTHER", "relative_support": 0.36752502365229756}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.601929799534178}, {"state": "ACT_CERTAIN", "relative_support": 0.3980702004658221}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.9251511574198341}, {"state": "ACP_LOW", "relative_support": 0.0748488425801659}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_script03_1_F003.avi

## 28. IEMOCAPFour / Ses05F_impro05_F018 — 起点/赢家均满命中或判对

- 参考：anger；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 诊断质量：1.0000→1.0000；50权重零/错8次，满/对37次。
- 模型字幕：Uh- Not lose the baggage in the first place. I mean You're offering a service here. I paid so much money for that ticket.
- 中文：嗯，首先不要丢失行李。我的意思是，你在提供一项服务。我为那张机票付了这么多钱。
- 起点回答：The character's emotional state is anger, frustration, dissatisfaction.
- 赢家回答：The character's emotional state is discontent, anger, frustration.
- 起点抽取：[anger, frustration, dissatisfaction]
- 赢家抽取：[discontent, anger, frustration]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_FAST, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_RAISED
- 图候选：disappointed, anger, appalled（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5245939576849595}, {"state": "AGC_CONGRUENT", "relative_support": 0.4296849255693761}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7700556512370494}, {"state": "AEX_EXPECTED", "relative_support": 0.22994434876295058}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.4952558263412266}, {"state": "AAG_SELF", "relative_support": 0.30981836695916276}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6312534902444619}, {"state": "ACT_CERTAIN", "relative_support": 0.36874650975553813}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5406788280394612}, {"state": "ACP_HIGH", "relative_support": 0.4593211719605388}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_impro05_F018.avi

## 29. IEMOCAPFour / Ses05F_script01_3_M037 — 相对起点诊断改善

- 参考：sad；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 诊断质量：0.8000→1.0000；50权重零/错0次，满/对37次。
- 模型字幕：It felt wrong to be alive-to open that bank-book; to buy that new car; to look at that new refrigerator.  I mean, you can take those things out of the war, but if you drive that car, you have to know that that comes from the love that a man has for a man.  And you've got to be a little bit better than that!
- 中文：感觉活着是错误的-打开那本银行账户；买那辆新车；看那台新冰箱。我的意思是，你可以把这些东西从战争中带出来，但如果你开着那辆车，你必须知道那是源于一个人对另一个人的爱。而你必须要比那更好一点！
- 起点回答：The character's emotional state is guilt, remorse, regret.
- 赢家回答：The character's emotional state is regret, dissatisfaction, guilt, shame, internal conflict, struggle.
- 起点抽取：[guilt, remorse, regret]
- 赢家抽取：[regret, dissatisfaction, guilt, shame, internal conflict, struggle]
- 实际证据level：2；原因：['mixed_text_affect_or_evaluation']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_POSITIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_VOICE_TENSE, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：anger, disappointed, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.972759617977199}, {"state": "AGR_RELEVANT", "relative_support": 0.027240382022800953}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.4516648563544852}, {"state": "AGC_CONGRUENT", "relative_support": 0.3204779995990836}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7914721013219802}, {"state": "AEX_EXPECTED", "relative_support": 0.20852789867801977}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7803835541976206}, {"state": "AAG_SELF", "relative_support": 0.16424848923543622}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.5685688199074658}, {"state": "ACT_CERTAIN", "relative_support": 0.4314311800925342}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5333843021012783}, {"state": "ACP_LOW", "relative_support": 0.46661569789872165}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_script01_3_M037.avi

## 30. IEMOCAPFour / Ses05F_script02_1_M019 — 相对起点诊断改善

- 参考：happy；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 诊断质量：0.8000→1.0000；50权重零/错0次，满/对6次。
- 模型字幕：Think about people in Kansas, they have to get a- a plane reservation and a hotel reservation just to see this uh- but we are just forty minutes away.  Too good to pass up.
- 中文：想想堪萨斯州的人们，他们必须预订飞机和酒店才能来看这个，但我们只需要40分钟的路程。太好了，不容错过。
- 起点回答：The character's emotional state is excitement, enthusiasm, admiration.
- 赢家回答：The character's emotional state is excited, joyful, satisfied.
- 起点抽取：[excitement, enthusiasm, admiration]
- 赢家抽取：[excited, joyful, satisfied]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_FAST, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_EYES_SQUINTED
- 图候选：hopeful, appreciated, awe（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5358830291020945}, {"state": "AGC_MIXED", "relative_support": 0.39763617848308724}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5791583061304141}, {"state": "AEX_UNEXPECTED", "relative_support": 0.420841693869586}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.40997846684523315}, {"state": "AAG_OTHER", "relative_support": 0.3217507705911301}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5078578612860716}, {"state": "ACT_UNCERTAIN", "relative_support": 0.49214213871392826}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8230823521027834}, {"state": "ACP_LOW", "relative_support": 0.17691764789721665}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_script02_1_M019.avi

## 31. IEMOCAPFour / Ses05F_script02_1_M030 — 相对起点诊断恶化

- 参考：happy；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 诊断质量：1.0000→0.8000；50权重零/错0次，满/对7次。
- 模型字幕：Oh, this is great.  I wouldn't miss this for the world.  I mean think about this. I know you are not interested but think about this for a second.
- 中文：哦，这太棒了。我不会错过这个机会。我是说想想这个。我知道你对此不感兴趣，但请花一秒钟思考一下。
- 起点回答：The character's emotional state is joy, surprise, passion, enthusiasm, excitement.
- 赢家回答：The character's emotional state is excited, passionate, enthusiastic.
- 起点抽取：[joy, surprise, passion, enthusiasm, excitement]
- 赢家抽取：[excited, passionate, enthusiastic]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_POSITIVE, TXT_EVALUATION_POSITIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_EYES_SQUINTED
- 图候选：joy, appreciated, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9711635193935707}, {"state": "AGR_RELEVANT", "relative_support": 0.02883648060642932}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6934739631206598}, {"state": "AGC_INCONGRUENT", "relative_support": 0.168590395993227}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6013694769351808}, {"state": "AEX_EXPECTED", "relative_support": 0.3986305230648191}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5827048517603862}, {"state": "AAG_SELF", "relative_support": 0.26902945030146125}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.5279738409693602}, {"state": "ACT_CERTAIN", "relative_support": 0.47202615903063994}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7516475305985137}, {"state": "ACP_LOW", "relative_support": 0.2483524694014863}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_script02_1_M030.avi

## 32. IEMOCAPFour / Ses05F_impro06_M007 — 相对起点诊断恶化

- 参考：sad；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 诊断质量：0.8000→0.0000；50权重零/错41次，满/对0次。
- 模型字幕：There's no reason for it.
- 中文：没有理由这样做。
- 起点回答：The character's emotional state is indifferent, apathetic, neutral.
- 赢家回答：The character's emotional state is neutral.
- 起点抽取：[indifferent, apathetic, neutral]
- 赢家抽取：[neutral]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, AUD_INTONATION_RISING, VIS_HEAD_LOWERED
- 图候选：disappointed, anger, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8748044167020769}, {"state": "AEX_EXPECTED", "relative_support": 0.1251955832979232}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.874185344569444}, {"state": "AAG_SELF", "relative_support": 0.12581465543055606}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7947941583410977}, {"state": "ACT_CERTAIN", "relative_support": 0.2052058416589022}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_impro06_M007.avi

## 33. CMUMOSI / yvsjCA6Y5Fc_8 — 起点/赢家均零命中或判错

- 参考：0.4；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 诊断质量：0.0000→0.0000；50权重零/错50次，满/对0次。
- 模型字幕：LIKE I SAID MAYBE MY EXPECTATIONS WERE LOWERED BECAUSE OF ALL OF THOSE REVIEWS BUT I REALLY DIDNT HATE IT
- 中文：就像我说的，可能是因为所有的那些评论，我的期望值降低了，但我真的并不讨厌它。
- 起点回答：The character's emotional state is disappointment, dissatisfaction, excitement, anxiety.
- 赢家回答：The character's emotional state is disappointed, negative, frustrated.
- 起点抽取：[disappointment, dissatisfaction, excitement, anxiety]
- 赢家抽取：[disappointed, negative, frustrated]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_UNCERTAINTY_HEDGE, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9838379860623178}, {"state": "AGR_RELEVANT", "relative_support": 0.016162013937682126}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.6868917392346864}, {"state": "AGC_MIXED", "relative_support": 0.25179762033758346}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5236676979304937}, {"state": "AEX_UNEXPECTED", "relative_support": 0.4763323020695063}], "APP_AGENCY": [{"state": "AAG_CIRCUMSTANCE", "relative_support": 0.35427997058471167}, {"state": "AAG_SELF", "relative_support": 0.32318496455661366}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6131597224221028}, {"state": "ACT_CERTAIN", "relative_support": 0.3868402775778971}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9160243912153117}, {"state": "ACP_HIGH", "relative_support": 0.0839756087846883}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/yvsjCA6Y5Fc_8.mp4

## 34. CMUMOSI / k5Y_838nuGo_27 — 起点/赢家均零命中或判错

- 参考：-0.8；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 诊断质量：0.0000→0.0000；50权重零/错48次，满/对2次。
- 模型字幕：YES UM SOMETHING ABOUT WAFFLE HOLE AM I THE ONLY ONE AM I PERVERTED NOT TO THINK THAT THAT SOUNDS DIRTY COZ IT TOTALLY DOES WAFFLE HOLE
- 中文：是的，关于华夫饼孔的事情，我是唯一一个觉得这听起来很下流的人吗？因为它确实听起来很下流，华夫饼孔。
- 起点回答：The character's emotional state is jokey, humorous, teasing, joking.
- 赢家回答：The character's emotional state is humorous, lighthearted, playful, joking.
- 起点抽取：[jokey, humorous, teasing, joking]
- 赢家抽取：[humorous, lighthearted, playful, joking]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, AUD_SPEECH_RATE_REL_SLOW, AUD_PAUSE_LONG, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_MOUTH_CORNERS_DOWN
- 图候选：disappointed, anger, depressed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8155049103316528}, {"state": "AGC_CONGRUENT", "relative_support": 0.10703993977521578}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6652288767959539}, {"state": "AEX_EXPECTED", "relative_support": 0.3347711232040462}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.38518694601893716}, {"state": "AAG_SELF", "relative_support": 0.3075894134482923}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6672273053390573}, {"state": "ACT_CERTAIN", "relative_support": 0.3327726946609428}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8985572240636984}, {"state": "ACP_HIGH", "relative_support": 0.10144277593630158}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/k5Y_838nuGo_27.mp4

## 35. CMUMOSI / zhpQhgha_KU_35 — 起点/赢家均满命中或判对

- 参考：0.6；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 诊断质量：1.0000→1.0000；50权重零/错0次，满/对50次。
- 模型字幕：UM SO IF YOU LIKE TO HEAR A UM LIKE MORE POSITIVE REVIEW CHECK OUT HER REVIEW IT IS VERY GOOD
- 中文：那么，如果你想听一个更积极的评价，可以去看看她的评价，非常好。
- 起点回答：The character's emotional state is positive, happy.
- 赢家回答：The character's emotional state is positive, confident, encouraging.
- 起点抽取：[positive, happy]
- 赢家抽取：[positive, confident, encouraging]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：hopeful, joy, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8062341793795084}, {"state": "AGC_MIXED", "relative_support": 0.1670286390556811}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9086295098943836}, {"state": "AEX_UNEXPECTED", "relative_support": 0.09137049010561628}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6433557726640643}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3474870058048431}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7915325808252625}, {"state": "ACT_UNCERTAIN", "relative_support": 0.2084674191747375}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8863760991214745}, {"state": "ACP_LOW", "relative_support": 0.11362390087852556}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/zhpQhgha_KU_35.mp4

## 36. CMUMOSI / cXypl4FnoZo_29 — 起点/赢家均满命中或判对

- 参考：-1.4；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 诊断质量：1.0000→1.0000；50权重零/错0次，满/对50次。
- 模型字幕：I DIDNT LIKE PETER
- 中文：我不喜欢彼得
- 起点回答：The character's emotional state is disapproval, dissatisfaction, dislike, negativity.
- 赢家回答：The character's emotional state is dissatisfied, angry, frustrated.
- 起点抽取：[disapproval, dissatisfaction, dislike, negativity]
- 赢家抽取：[dissatisfied, angry, frustrated]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_DESIRE_NEED, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：disappointed, anger, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9840873085963125}, {"state": "AGR_RELEVANT", "relative_support": 0.01591269140368758}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.6610566324634447}, {"state": "AGC_CONGRUENT", "relative_support": 0.3389433675365553}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7454778134720049}, {"state": "AEX_EXPECTED", "relative_support": 0.25452218652799513}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5401405133768291}, {"state": "AAG_SELF", "relative_support": 0.3402088605279762}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8671029436175065}, {"state": "ACT_CERTAIN", "relative_support": 0.1328970563824935}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.52440191187326}, {"state": "ACP_LOW", "relative_support": 0.47559808812674}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/cXypl4FnoZo_29.mp4

## 37. CMUMOSI / c7UH_rxdZv4_18 — 相对起点诊断改善

- 参考：-2.25；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 诊断质量：0.0000→1.0000；50权重零/错7次，满/对43次。
- 模型字幕：WHAT WA WHAT HES WHAT W WHY YOU HAVE NO SKILLS WHATSOEVER
- 中文：什么是什么，他是什么，为什么你一点技能都没有
- 起点回答：The character's emotional state is anger, frustration, excitement, enthusiasm.
- 赢家回答：The character's emotional state is anger, frustration, dissatisfaction, criticism.
- 起点抽取：[anger, frustration, excitement, enthusiasm]
- 赢家抽取：[anger, frustration, dissatisfaction, criticism]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：disappointed, anger, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.6060566466503737}, {"state": "AGC_CONGRUENT", "relative_support": 0.27744351671979806}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5526456192189269}, {"state": "AEX_UNEXPECTED", "relative_support": 0.44735438078107315}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4501290648375052}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.33210128070473593}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.523172987464997}, {"state": "ACT_CERTAIN", "relative_support": 0.4768270125350031}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6627474781575337}, {"state": "ACP_HIGH", "relative_support": 0.33725252184246635}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/c7UH_rxdZv4_18.mp4

## 38. CMUMOSI / f_pcplsH_V0_4 — 相对起点诊断改善

- 参考：0.5；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 诊断质量：0.0000→1.0000；50权重零/错4次，满/对46次。
- 模型字幕：BECAUSE IT DOES MAKE A LOT MORE SENSE HAVING THE KILLER BE ABLE TO BE EVERYWHERE IF THERES TWO OF THEM
- 中文：因为如果有两个凶手，他们能够无所不在，这会让事情更有意义。
- 起点回答：The character's emotional state is concentration, contemplation, seriousness.
- 赢家回答：The character's emotional state is excitement, enthusiasm, passion, contemplation, realization.
- 起点抽取：[concentration, contemplation, seriousness]
- 赢家抽取：[excitement, enthusiasm, passion, contemplation, realization]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：hopeful, appreciated, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7239412564343601}, {"state": "AGC_MIXED", "relative_support": 0.23020695286667267}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8999995844127958}, {"state": "AEX_UNEXPECTED", "relative_support": 0.10000041558720418}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.46224852907403435}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.35049021547872905}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8364989119680694}, {"state": "ACT_UNCERTAIN", "relative_support": 0.1635010880319306}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8192438113176872}, {"state": "ACP_LOW", "relative_support": 0.18075618868231283}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/f_pcplsH_V0_4.mp4

## 39. CMUMOSI / f9O3YtZ2VfI_14 — 相对起点诊断恶化

- 参考：1.2；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 诊断质量：1.0000→0.0000；50权重零/错3次，满/对47次。
- 模型字幕：JUST GIVE ME A NICE INTERESTING CHOKE
- 中文：只需给我一个有趣的好的压制技巧
- 起点回答：The character's emotional state is humorous, teasing, positive.
- 赢家回答：The character's emotional state is playful, sarcastic.
- 起点抽取：[humorous, teasing, positive]
- 赢家抽取：[playful, sarcastic]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：hopeful, appreciated, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8255697140255468}, {"state": "AGC_MIXED", "relative_support": 0.17443028597445331}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8582740595020979}, {"state": "AEX_UNEXPECTED", "relative_support": 0.1417259404979021}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.7593560442493443}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.21245531454022837}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.9349317939029191}, {"state": "ACT_UNCERTAIN", "relative_support": 0.0650682060970809}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/f9O3YtZ2VfI_14.mp4

## 40. CMUMOSI / etzxEpPuc6I_7 — 相对起点诊断恶化

- 参考：-1.2；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 诊断质量：1.0000→0.0000；50权重零/错15次，满/对35次。
- 模型字幕：BUT THE THING ABOUT GI JOE COMPARED TO TRANSFORMERS IS TRANSFOMERS 2 DIDNT KNOW WHAT IT WANTED TO DO
- 中文：但是关于GI JOE与变形金刚的比较，问题在于变形金刚2并不知道它想要做什么。
- 起点回答：The character's emotional state is excited, enthusiastic, confused, bewildered.
- 赢家回答：The character's emotional state is confused, uncertain, anxious, nervous, excited, enthusiastic.
- 起点抽取：[excited, enthusiastic, confused, bewildered]
- 赢家抽取：[confused, uncertain, anxious, nervous, excited, enthusiastic]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：apathetic, depressed, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_MIXED", "relative_support": 0.48832526777544655}, {"state": "AGC_CONGRUENT", "relative_support": 0.30520010075701254}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7144577307575387}, {"state": "AEX_UNEXPECTED", "relative_support": 0.2855422692424613}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.562121050260434}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.42955132905075494}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6448217128593564}, {"state": "ACT_UNCERTAIN", "relative_support": 0.35517828714064353}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5269875271991789}, {"state": "ACP_LOW", "relative_support": 0.47301247280082115}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/etzxEpPuc6I_7.mp4

## 41. CMUMOSEI / r46amqjpWgg_0 — 起点/赢家均零命中或判错

- 参考：2.0；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 诊断质量：0.0000→0.0000；50权重零/错43次，满/对7次。
- 模型字幕：a lot of people, they write a beautiful speech, and they're just not sure how to communicate it
- 中文：很多人，他们写了一篇漂亮的演讲，只是不确定如何传达出来。
- 起点回答：The character's emotional state is disappointment, confusion.
- 赢家回答：The character's emotional state is disappointment, frustration, confusion, anxiety.
- 起点抽取：[disappointment, confusion]
- 赢家抽取：[disappointment, frustration, confusion, anxiety]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_POSITIVE, TXT_EVALUATION_POSITIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PAUSE_LONG, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9838184911474006}, {"state": "AGR_RELEVANT", "relative_support": 0.016181508852599405}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5967935343717433}, {"state": "AGC_MIXED", "relative_support": 0.30968501109862917}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5121353301730311}, {"state": "AEX_UNEXPECTED", "relative_support": 0.48786466982696874}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4924658899979785}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.30259983880746516}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5161857557835335}, {"state": "ACT_UNCERTAIN", "relative_support": 0.4838142442164665}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7655468747245006}, {"state": "ACP_LOW", "relative_support": 0.23445312527549939}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/r46amqjpWgg_0.mp4

## 42. CMUMOSEI / 53609_12 — 起点/赢家均零命中或判错

- 参考：-0.3333333432674408；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 诊断质量：0.0000→0.0000；50权重零/错24次，满/对26次。
- 模型字幕：But I knew going in it was going to be bad and it wasn't as bad as I thought it was gonna be
- 中文：但是我在进去之前就知道会很糟糕，而且它并没有我想象中那么糟糕。
- 起点回答：The character's emotional state is relief, slight optimism, positive.
- 赢家回答：The character's emotional state is relieved, somewhat positive.
- 起点抽取：[relief, optimistic, positive]
- 赢家抽取：[relieved, positive]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：disappointed, anger, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.46008801090373475}, {"state": "AGC_CONGRUENT", "relative_support": 0.3066675833788587}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5712919131893723}, {"state": "AEX_UNEXPECTED", "relative_support": 0.4287080868106277}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4208891816338414}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.31995614544404694}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.9388067065723663}, {"state": "ACT_UNCERTAIN", "relative_support": 0.061193293427633695}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6205456703955359}, {"state": "ACP_HIGH", "relative_support": 0.3794543296044642}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/53609_12.mp4

## 43. CMUMOSEI / nZFPKP9kBkw_1 — 起点/赢家均满命中或判对

- 参考：0.3333333432674408；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 诊断质量：1.0000→1.0000；50权重零/错0次，满/对50次。
- 模型字幕：Really, really a depth of understanding with our consumers is one of the biggest ways that we catalyze great creativity.
- 中文：真正地，真正地与我们的消费者有深入的理解是我们激发出伟大创造力的最重要途径之一。
- 起点回答：The character's emotional state is excited, enthusiastic, passionate, satisfied, involved.
- 赢家回答：The character's emotional state is positive, satisfied, passionate, excited, energetic, confident, self-assured.
- 起点抽取：[excited, enthusiastic, passionate, satisfied, involved]
- 赢家抽取：[positive, satisfied, passionate, excited, energetic, confident, self-assured]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_FAST, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED
- 图候选：appreciated, awe, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6595699994665164}, {"state": "AGC_MIXED", "relative_support": 0.1865555605410253}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6599615505806476}, {"state": "AEX_UNEXPECTED", "relative_support": 0.3400384494193524}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.4540050441523842}, {"state": "AAG_SELF", "relative_support": 0.3177435478790686}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8918763048051874}, {"state": "ACT_UNCERTAIN", "relative_support": 0.10812369519481263}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7377966690959901}, {"state": "ACP_LOW", "relative_support": 0.26220333090400993}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/nZFPKP9kBkw_1.mp4

## 44. CMUMOSEI / x8UZQkN52o4_2 — 起点/赢家均满命中或判对

- 参考：-1.3333333730697632；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 诊断质量：1.0000→1.0000；50权重零/错14次，满/对36次。
- 模型字幕：( AUDIENCE REACTS ) I FEEL LIKE MY HEART IS CRYING
- 中文：（观众反应）我感觉我的心在哭泣。
- 起点回答：The character's emotional state is enthusiastic, passionate, surprised, excited, sad.
- 赢家回答：The character's emotional state is anger, sadness, anxiety, stress.
- 起点抽取：[enthusiastic, passionate, surprised, excited, sad]
- 赢家抽取：[anger, sadness, anxiety, stress]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_UNCERTAINTY_HEDGE, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：anger, disappointed, hesitant（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5454764786523489}, {"state": "AGC_CONGRUENT", "relative_support": 0.454523521347651}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9107856317406895}, {"state": "AEX_EXPECTED", "relative_support": 0.0892143682593104}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8155066187970142}, {"state": "AAG_SELF", "relative_support": 0.11364445247276542}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9355389696532609}, {"state": "ACT_CERTAIN", "relative_support": 0.06446103034673906}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.700926281935957}, {"state": "ACP_LOW", "relative_support": 0.29907371806404315}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/x8UZQkN52o4_2.mp4

## 45. CMUMOSEI / XKyumlBmix8_9 — 相对起点诊断改善

- 参考：0.6666666865348816；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 诊断质量：0.0000→1.0000；50权重零/错32次，满/对18次。
- 模型字幕：Let's put it on pause for a second okay
- 中文：让我们暂停一下，好吗？
- 起点回答：The character's emotional state is nervous, uncertain.
- 赢家回答：The character's emotional state is calm, gentle.
- 起点抽取：[nervous, uncertain]
- 赢家抽取：[calm, gentle]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_DESIRE_NEED, AUD_INTONATION_RISING, VIS_MOUTH_CORNERS_DOWN, VIS_LIPS_PRESSED, VIS_HEAD_LOWERED
- 图候选：disappointed, proud, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8137622166099862}, {"state": "AGC_CONGRUENT", "relative_support": 0.1862377833900137}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6267236235597139}, {"state": "AEX_EXPECTED", "relative_support": 0.3732763764402861}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5155558808779631}, {"state": "AAG_OTHER", "relative_support": 0.48444411912203694}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6030621250674322}, {"state": "ACP_HIGH", "relative_support": 0.39693787493256794}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/XKyumlBmix8_9.mp4

## 46. CMUMOSEI / MtIklGnIMGo_5 — 相对起点诊断改善

- 参考：-1.3333333730697632；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 诊断质量：0.0000→1.0000；50权重零/错1次，满/对49次。
- 模型字幕：So then you have people that follow them that think well my leaders want peace, they say they want peace, I want peace so if they think it's okay to build more settlements, that will bring peace, they're going to follow those people but we're not going to get peace.
- 中文：那么，你有一些追随他们的人认为，我的领导者想要和平，他们说他们想要和平，我也想要和平，所以如果他们认为建设更多的定居点可以带来和平，他们会追随这些人，但我们不会得到和平。
- 起点回答：The character's emotional state is anxiety, agitation, tension, excitement, passion.
- 赢家回答：The character's emotional state is anxious, tense, frustrated, angry.
- 起点抽取：[anxiety, agitation, tension, excitement, passion]
- 赢家抽取：[anxious, tense, frustrated, angry]
- 实际证据level：2；原因：['emotion_support_not_separated', 'mixed_text_affect_or_evaluation']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_UNCERTAINTY_HEDGE, TXT_DESIRE_NEED, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_SPEECH_RATE_REL_FAST, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：disappointed, hopeful, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9730581854110475}, {"state": "AGR_RELEVANT", "relative_support": 0.026941814588952537}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.4029459734159636}, {"state": "AGC_INCONGRUENT", "relative_support": 0.32566808104963013}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5236711231841757}, {"state": "AEX_UNEXPECTED", "relative_support": 0.4763288768158242}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.44407465889364284}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.29396230749915114}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6276263705167606}, {"state": "ACT_CERTAIN", "relative_support": 0.3723736294832394}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5369722489175612}, {"state": "ACP_LOW", "relative_support": 0.4630277510824388}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/MtIklGnIMGo_5.mp4

## 47. CMUMOSEI / 7mb8Y2AhXIY_4 — 相对起点诊断恶化

- 参考：0.6666666865348816；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 诊断质量：1.0000→0.0000；50权重零/错2次，满/对48次。
- 模型字幕：It may just be community around friendship and who they know and who they trust.
- 中文：可能只是围绕友谊、他们认识的人和他们信任的人的社区。
- 起点回答：The character's emotional state is positive, confident, self-affirming.
- 赢家回答：The character's emotional state is excitement, anticipation, tension, uncertainty, concern, worry, seriousness, confidence, relaxation, comfort, ease.
- 起点抽取：[positive, confident, self-affirming]
- 赢家抽取：[excitement, anticipation, tension, uncertainty, concern, worry, seriousness, confidence, relaxation, comfort, ease]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_UNCERTAINTY_HEDGE, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, hesitant（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7820515855737817}, {"state": "AGC_CONGRUENT", "relative_support": 0.16610927247576038}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6719576981659738}, {"state": "AEX_UNEXPECTED", "relative_support": 0.32804230183402616}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5103387092336189}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.30141723740203735}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7950213118218665}, {"state": "ACT_CERTAIN", "relative_support": 0.20497868817813342}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8768441051074168}, {"state": "ACP_HIGH", "relative_support": 0.12315589489258318}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/7mb8Y2AhXIY_4.mp4

## 48. CMUMOSEI / 222247_8 — 相对起点诊断恶化

- 参考：-2.0；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 诊断质量：1.0000→0.0000；50权重零/错12次，满/对38次。
- 模型字幕：The ending was a little bit surprising but by then I I (stutter) really didn't care anymore
- 中文：结局有点令人惊讶，但那时候我真的不再在乎了。
- 起点回答：The character's emotional state is release, indifference, surprise.
- 赢家回答：The character's emotional state is calm, unconcerned, acceptance, let-go, positivity.
- 起点抽取：[release, indifference, surprise]
- 赢家抽取：[calm, unconcerned, acceptance, let-go, positivity]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED
- 图候选：disappointed, anger, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5068889928412276}, {"state": "AGC_MIXED", "relative_support": 0.4385953839066793}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6776301490676866}, {"state": "AEX_UNEXPECTED", "relative_support": 0.3223698509323134}], "APP_AGENCY": [{"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4771763545200341}, {"state": "AAG_SELF", "relative_support": 0.4322220526096509}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8129404988982104}, {"state": "ACT_UNCERTAIN", "relative_support": 0.18705950110178962}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9890766515840564}, {"state": "ACP_HIGH", "relative_support": 0.01092334841594359}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/222247_8.mp4

## 49. SIMS / video_0037_0005 — 起点/赢家均零命中或判错

- 参考：0.2；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 诊断质量：0.0000→0.0000；50权重零/错47次，满/对3次。
- 模型字幕：I'm sorry. There's a lot of earwax these days
- 中文：不好意思啊，最近耳屎比较多
- 起点回答：The character's emotional state is anxiety, stress, frustration, irritation.
- 赢家回答：The character's emotional state is sad, depressed.
- 起点抽取：[anxiety, stress, frustration, irritation]
- 赢家抽取：[sad, depressed]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.892692887281888}, {"state": "AGC_CONGRUENT", "relative_support": 0.06773677604160741}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6662180322680346}, {"state": "AEX_UNEXPECTED", "relative_support": 0.33378196773196533}], "APP_AGENCY": [{"state": "AAG_CIRCUMSTANCE", "relative_support": 0.44735147742855647}, {"state": "AAG_SELF", "relative_support": 0.3610854099114698}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7666881057143321}, {"state": "ACT_UNCERTAIN", "relative_support": 0.233311894285668}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.993185221617841}, {"state": "ACP_HIGH", "relative_support": 0.006814778382159035}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0037_0005.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.0000|The character's emotional state is sad, depressed.|
|base35_B|0.0000|The character's emotional state is sad, depressed, uncomfortable, dissatisfied, painful.|
|base35_C|0.0000|The character's emotional state is sad, down, uncomfortable, dissatisfied, negative.|
|base35_D|0.0000|The character's emotional state is sad, anger, fear.|
|base35_F|0.0000|The character's emotional state is sad, anger, fear.|
|base35_E|0.0000|The character's emotional state is sad, anger, fear.|
|graph40_A|0.0000|The character's emotional state is sad, depressed.|
|graph40_B|0.0000|The character's emotional state is sad, depressed, frustrated, annoyed, irritated, amused, surprised, shocked.|
|graph40_C|0.0000|The character's emotional state is sad, depressed.|
|graph40_D|0.0000|The character's emotional state is sad, depressed.|
|graph40_E|0.0000|The character's emotional state is sad, depressed.|
|graph40_F|0.0000|The character's emotional state is sad, depressed.|
|base35_G|0.0000|The character's emotional state is discomfort, pain, anxiety, tension, frustration, distress.|
|graph40_G|0.0000|The character's emotional state is sad, depressed.|

## 50. SIMS / video_0008_0011 — 起点/赢家均零命中或判错

- 参考：-0.2；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 诊断质量：0.0000→0.0000；50权重零/错50次，满/对0次。
- 模型字幕：I can do whatever it takes.
- 中文：花多少钱我都可以的啦。
- 起点回答：The character's emotional state is positive, enthusiastic, confident.
- 赢家回答：The character's emotional state is positive, determined, willing, capable.
- 起点抽取：[positive, enthusiastic, confident]
- 赢家抽取：[positive, determined, willing, capable]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：hopeful, appreciated, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7591604905782723}, {"state": "AGC_MIXED", "relative_support": 0.19754606439460762}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8508941774790156}, {"state": "AEX_UNEXPECTED", "relative_support": 0.1491058225209843}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5965848095420104}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3789095105712583}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.840013701673498}, {"state": "ACT_UNCERTAIN", "relative_support": 0.15998629832650205}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7560838173439507}, {"state": "ACP_LOW", "relative_support": 0.2439161826560493}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0008_0011.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.0000|The character's emotional state is positive, determined, willing, confident.|
|base35_B|0.0000|The character's emotional state is positive, committed, determined, calm, focused.|
|base35_C|0.0000|The character's emotional state is positive, determined, excited, surprised, uncertain.|
|base35_D|0.0000|The character's emotional state is positive, committed, determined, calm, focused.|
|base35_F|0.0000|The character's emotional state is positive, determined, resolved, calm, confident.|
|base35_E|0.0000|The character's emotional state is positive, determined, excited, surprised, uncertain.|
|graph40_A|0.0000|The character's emotional state is positive, determined, enthusiastic.|
|graph40_B|0.0000|The character's emotional state is positive, determined, enthusiastic.|
|graph40_C|0.0000|The character's emotional state is positive, determined, enthusiastic.|
|graph40_D|0.0000|The character's emotional state is positive, determined, enthusiastic.|
|graph40_E|0.0000|The character's emotional state is positive, determined, enthusiastic.|
|graph40_F|0.0000|The character's emotional state is positive, determined, enthusiastic.|
|base35_G|0.0000|The character's emotional state is positive, determined, resolved, calm, confident.|
|graph40_G|0.0000|The character's emotional state is positive, determined, enthusiastic.|

## 51. SIMS / video_0036_0014 — 起点/赢家均满命中或判对

- 参考：-1.0；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 诊断质量：1.0000→1.0000；50权重零/错0次，满/对50次。
- 模型字幕：It's a shame for me to lose under Yang Cang's knife. Ziyu reminds himself of this injury
- 中文：败在杨苍刀下是我一生之耻，子虞以此伤提醒自己
- 起点回答：The character's emotional state is loss, pain, frustration.
- 赢家回答：The character's emotional state is loss, failure, frustration, anger, anxiety, stress.
- 起点抽取：[loss, pain, frustration]
- 赢家抽取：[loss, failure, frustration, anger, anxiety, stress]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_LOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_EYES_SQUINTED
- 图候选：despair, ashamed, disappointed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.8872738526995086}, {"state": "AGR_RELEVANT", "relative_support": 0.11272614730049131}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8014116963758527}, {"state": "AGC_MIXED", "relative_support": 0.13691344084007126}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.963694327658153}, {"state": "AEX_UNEXPECTED", "relative_support": 0.036305672341847076}], "APP_AGENCY": [{"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4314455561599925}, {"state": "AAG_SELF", "relative_support": 0.3900980257682622}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8311174780856821}, {"state": "ACT_UNCERTAIN", "relative_support": 0.16888252191431785}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9928671115253094}, {"state": "ACP_HIGH", "relative_support": 0.007132888474690729}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0036_0014.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|1.0000|The character's emotional state is loss, failure, pain, reflection, introspection, emotional turmoil.|
|base35_B|1.0000|The character's emotional state is sadness, disappointment, anxiety, stress, introspection, regret.|
|base35_C|1.0000|The character's emotional state is sadness, disappointment, anxiety, uncertainty, hopelessness, self-blame.|
|base35_D|1.0000|The character's emotional state is sadness, fear, anger.|
|base35_F|1.0000|The character's emotional state is sadness, fear, anxiety, anger, frustration.|
|base35_E|1.0000|The character's emotional state is sadness, fear, anxiety.|
|graph40_A|1.0000|The character's emotional state is sadness, frustration, anxiety, stress, self-blame, pain.|
|graph40_B|1.0000|The character's emotional state is fear, anxiety, stress, anger, frustration, self-blame, pain.|
|graph40_C|1.0000|The character's emotional state is fear, anxiety, tension, stress, anger, frustration, self-reproach, regret.|
|graph40_D|1.0000|The character's emotional state is sadness, disappointment, frustration, anger, aggression, defensiveness.|
|graph40_E|1.0000|The character's emotional state is fear, anxiety, tension, stress, pain, frustration.|
|graph40_F|1.0000|The character's emotional state is fear, anxiety, tension, stress, anger, frustration, self-reproach, self-criticism, shame.|
|base35_G|1.0000|The character's emotional state is sadness, disappointment, anxiety, uncertainty.|
|graph40_G|1.0000|The character's emotional state is fear, anxiety, tension, stress, pain, defeat, self-reproach, guilt.|

## 52. SIMS / video_0024_0100 — 起点/赢家均满命中或判对

- 参考：1.0；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 诊断质量：1.0000→1.0000；50权重零/错16次，满/对34次。
- 模型字幕：Please believe in a father's love for his son.
- 中文：请相信一个爸爸对儿子的爱。
- 起点回答：The character's emotional state is serious, determined, loving, sincere.
- 赢家回答：The character's emotional state is reassuring, empathetic, caring.
- 起点抽取：[serious, determined, loving, sincere]
- 赢家抽取：[reassuring, empathetic, caring]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED
- 图候选：hopeful, appreciated, confident（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.660288423217206}, {"state": "AGC_MIXED", "relative_support": 0.2210958429999163}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9246807801786886}, {"state": "AEX_UNEXPECTED", "relative_support": 0.07531921982131147}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5996353711206389}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.35442636271161876}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7387689668156465}, {"state": "ACT_UNCERTAIN", "relative_support": 0.2612310331843535}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.668574580024428}, {"state": "ACP_LOW", "relative_support": 0.3314254199755719}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0024_0100.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|1.0000|The character's emotional state is anxious, stressed, under pressure, love, care, support.|
|base35_B|1.0000|The character's emotional state is anxious, stressed, under pressure, positive, caring.|
|base35_C|1.0000|The character's emotional state is anxious, stressed, uncertain, determined, hopeful.|
|base35_D|1.0000|The character's emotional state is anxious, stressed, under pressure, positive, caring.|
|base35_F|1.0000|The character's emotional state is love, concern, care.|
|base35_E|1.0000|The character's emotional state is anxious, stressed, uncertain, determined, hopeful.|
|graph40_A|1.0000|The character's emotional state is reassuring, supportive, caring, supportive, emotional.|
|graph40_B|1.0000|The character's emotional state is reassuring, supportive, caring.|
|graph40_C|1.0000|The character's emotional state is reassuring, empathetic, caring, firm, sincere.|
|graph40_D|1.0000|The character's emotional state is reassuring, supportive, caring.|
|graph40_E|1.0000|The character's emotional state is reassuring, empathetic, caring, firm, sincere.|
|graph40_F|0.0000|The character's emotional state is reassuring, supportive, caring, trusting, anxious, overwhelmed.|
|base35_G|1.0000|The character's emotional state is love, concern, care.|
|graph40_G|0.0000|The character's emotional state is reassuring, supportive, caring, trusting, anxious, overwhelmed.|

## 53. SIMS / video_0041_0031 — 相对起点诊断改善

- 参考：-1.0；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 诊断质量：0.0000→1.0000；50权重零/错20次，满/对30次。
- 模型字幕：I pretended to ask him for an interview and asked him to go
- 中文：我假装约他采访约他去
- 起点回答：The character's emotional state is humor, irony, amusement.
- 赢家回答：The character's emotional state is tense, uneasy, anxiety.
- 起点抽取：[humor, irony, amusement]
- 赢家抽取：[tense, uneasy, anxiety]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_HIGH, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_FALLING, AUD_VOICE_TENSE, AUD_VOICE_TREMBLING, AUD_CRYING_SOBBING_PRESENT, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_HEAD_LOWERED
- 图候选：despair, depressed, disappointed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8199480161104824}, {"state": "AGC_MIXED", "relative_support": 0.14567729270374358}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6571017900414949}, {"state": "AEX_EXPECTED", "relative_support": 0.342898209958505}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.38213940999167273}, {"state": "AAG_OTHER", "relative_support": 0.3531883082753725}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5324764910035488}, {"state": "ACT_UNCERTAIN", "relative_support": 0.46752350899645123}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9950552859143499}, {"state": "ACP_HIGH", "relative_support": 0.004944714085650083}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0041_0031.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|1.0000|The character's emotional state is tense, uneasy, anxiety.|
|base35_B|1.0000|The emotional state is anxious, tense, emotional stress, sadness, distress.|
|base35_C|1.0000|The emotional state of the character might be sadness, anxiety, or depression.|
|base35_D|1.0000|The character's emotional state is tense, anxious, sad.|
|base35_F|1.0000|The character's emotional state is tense, anxious.|
|base35_E|1.0000|The character's emotional state is tense, anxious, sad.|
|graph40_A|1.0000|The character's emotional state is tense, uneasy, anxiety, pressure.|
|graph40_B|1.0000|The character's emotional state is tense, uneasy, anxiety, pressure.|
|graph40_C|1.0000|The character's emotional state is tense, uneasy, determination.|
|graph40_D|1.0000|The character's emotional state is tense, uneasy, anxiety, fear, pressure.|
|graph40_E|0.0000|The character's emotional state is tense, uneasy, anxiety, excitement.|
|graph40_F|0.0000|The character's emotional state is tense, uneasy, urgent, anxious, excited.|
|base35_G|1.0000|The character's emotional state is tense, anxious, under pressure, sadness, distress.|
|graph40_G|1.0000|The character's emotional state is tense, uneasy, determination.|

## 54. SIMS / video_0048_0022 — 相对起点诊断改善

- 参考：1.0；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 诊断质量：0.0000→1.0000；50权重零/错10次，满/对40次。
- 模型字幕：What do you say, what do you mean to marry for nothing, then we both have to eat, don't we
- 中文：你说这什么话，什么叫白娶了，那咱们俩不也得吃饭吗是不是
- 起点回答：The character's emotional state is anger, frustration, anxiety, stress.
- 赢家回答：The character's emotional state is excited, amused, sarcastic, teasing.
- 起点抽取：[anger, frustration, anxiety, stress]
- 赢家抽取：[excited, amused, sarcastic, teasing]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_RHETORICAL_QUESTION, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT, VIS_HEAD_LOWERED
- 图候选：disappointed, anger, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5359281041427346}, {"state": "AGC_CONGRUENT", "relative_support": 0.4640718958572654}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8278046795240668}, {"state": "AEX_EXPECTED", "relative_support": 0.1721953204759332}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7038605426656117}, {"state": "AAG_SELF", "relative_support": 0.23712065852753778}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8457230605025959}, {"state": "ACT_CERTAIN", "relative_support": 0.15427693949740406}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6076352356636127}, {"state": "ACP_HIGH", "relative_support": 0.3923647643363873}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0048_0022.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.0000|The character's emotional state is anger, frustration.|
|base35_B|0.0000|Observations: The text content indicates that the man has a negative evaluation of someone nearby, using a rhetorical question to express his point of view, suggesting that he might feel discontented or disrespected. Based on the audio cues described with a high pitch and high pitch variation, along with the intonation of the voice being upward, it can be inferred that the man may have experienced excitement, enthusiasm, and a certain level of tension or anxiety. Considering the video clues showing the man's's expression and body language, such as furrowing his brows, squinting his eyes, and lowering his head, one can deduce that he might be under stress or struggling to express his emotions. Integrating these clues, the man's's emotional state could possibly be excitement, enthusiasm, tension, or anxiety.|
|base35_C|0.0000|The character's emotional state is dissatisfaction, anger.|
|base35_D|0.0000|The character's emotional state is anger, frustration.|
|base35_F|0.0000|The character's emotional state is anger, frustration.|
|base35_E|0.0000|The character's emotional state is anger, frustration.|
|graph40_A|1.0000|The character's emotional state is excited, enthusiastic, joyful, teasing, joking.|
|graph40_B|1.0000|The character's emotional state is excited, enthusiastic, surprised.|
|graph40_C|1.0000|The character's emotional state is excited, enthusiastic, joyful.|
|graph40_D|1.0000|The character's emotional state is excited, enthusiastic, joyful, teasing, joking.|
|graph40_E|1.0000|The character's emotional state is excited, enthusiastic, joyful.|
|graph40_F|1.0000|The character's emotional state is excited, enthusiastic, joyful, teasing, joking.|
|base35_G|0.0000|The character's emotional state is anger, frustration.|
|graph40_G|1.0000|The character's emotional state is excited, enthusiastic, joyful, teasing, joking.|

## 55. SIMS / video_0025_0018 — 相对起点诊断恶化

- 参考：0.2；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 诊断质量：1.0000→0.0000；50权重零/错15次，满/对35次。
- 模型字幕：Don't look down on them. I have made great efforts to gather all kinds of gods.
- 中文：你不要瞧不起他们哦，为了把各路大神聚集，我是费了大力气的。
- 起点回答：The character's emotional state is anger, frustration, passion, determination.
- 赢家回答：The character's emotional state is nervous, excited, proud, angry, disappointed.
- 起点抽取：[anger, frustration, passion, determination]
- 赢家抽取：[nervous, excited, proud, angry, disappointed]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_POSITIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_SELF, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9863547828538461}, {"state": "AGR_RELEVANT", "relative_support": 0.013645217146153854}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6988814780737455}, {"state": "AGC_INCONGRUENT", "relative_support": 0.19249221042547918}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.710016622587829}, {"state": "AEX_EXPECTED", "relative_support": 0.289983377412171}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6332748964760513}, {"state": "AAG_OTHER", "relative_support": 0.3365126560351599}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6247183257516282}, {"state": "ACT_CERTAIN", "relative_support": 0.3752816742483717}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7728473944046047}, {"state": "ACP_LOW", "relative_support": 0.22715260559539524}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0025_0018.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.0000|The character's emotional state is frustrated, excited, angry, passionate, dissatisfied.|
|base35_B|1.0000|The character's emotional state is frustrated, excited, determined, proud, confident.|
|base35_C|1.0000|The character's emotional state is positive, excited, determined, self-assured.|
|base35_D|1.0000|The character's emotional state is frustrated, excited, determined, proud, confident.|
|base35_F|1.0000|The character's emotional state is positive, excited, determined, passionate, confident.|
|base35_E|1.0000|The character's emotional state is positive, excited, determined, self-assured.|
|graph40_A|1.0000|The character's emotional state is anger, frustration, anxiety, tension, confidence, determination.|
|graph40_B|1.0000|The character's emotional state is nervous, excited, concerned, passionate, confident.|
|graph40_C|0.0000|The character's emotional state is anger, frustration, anxiety, tension, confidence.|
|graph40_D|1.0000|The character's emotional state is nervous, excited, concerned, passionate, confident.|
|graph40_E|0.0000|The character's emotional state is anger, frustration, anxiety, tension, confidence.|
|graph40_F|1.0000|The character's emotional state is anger, frustration, anxiety, tension, confidence, determination.|
|base35_G|1.0000|The character's emotional state is positive, excited, determined, passionate, confident.|
|graph40_G|1.0000|The character's emotional state is anger, frustration, anxiety, tension, confidence, determination.|

## 56. SIMS / video_0040_0041 — 相对起点诊断恶化

- 参考：-0.8；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 诊断质量：1.0000→0.0000；50权重零/错21次，满/对29次。
- 模型字幕：Those who choose to give up from the beginning will not fail.
- 中文：那些从一开始就选择放弃的人他不会失败
- 起点回答：The character's emotional state is apathy, negativity, emotional control.
- 赢家回答：The character's emotional state is ironic, mocking, challenging, contemplative, making decisions.
- 起点抽取：[apathy, negativity, emotional control]
- 赢家抽取：[ironic, mocking, challenging, contemplative, making decisions]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_NEGATION_PRESENT, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：disappointed, despair, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9927408391691145}, {"state": "AGR_RELEVANT", "relative_support": 0.007259160830885596}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.505389427379191}, {"state": "AGC_CONGRUENT", "relative_support": 0.45364982033937146}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7256427397612293}, {"state": "AEX_UNEXPECTED", "relative_support": 0.2743572602387707}], "APP_AGENCY": [{"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4967806487614718}, {"state": "AAG_SELF", "relative_support": 0.4894348364287716}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.9299355726557315}, {"state": "ACT_UNCERTAIN", "relative_support": 0.07006442734426852}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.523945281407635}, {"state": "ACP_HIGH", "relative_support": 0.4760547185923649}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0040_0041.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|1.0000|The character's emotional state is frustrated, anxious, impatient, negative, discouraging, evaluation, response.|
|base35_B|1.0000|The character's emotional state is negative, discouraged, frustrated, bored, disengaged.|
|base35_C|1.0000|The character's emotional state is negative, disappointment, defeat, helplessness.|
|base35_D|1.0000|The character's emotional state is negative, discouraged, frustrated, bored, disengaged.|
|base35_F|1.0000|The character's emotional state is negative, discouraged, frustrated, helpless, hopeless.|
|base35_E|1.0000|The character's emotional state is negative, disappointment, defeat, helplessness.|
|graph40_A|0.0000|The character's emotional state is encouraging, comforting.|
|graph40_B|0.0000|The character's emotional state is encouraging, comforting.|
|graph40_C|0.0000|The character's emotional state is encouraging, comforting.|
|graph40_D|0.0000|The character's emotional state is encouraging, comforting.|
|graph40_E|0.0000|The character's emotional state is encouraging, comforting.|
|graph40_F|0.0000|The character's emotional state is encouraging, comforting.|
|base35_G|1.0000|The character's emotional state is negative, discouraged, frustrated, helpless, hopeless.|
|graph40_G|0.0000|The character's emotional state is encouraging, comforting.|

## 57. SIMSv2 / test14_00010 — 起点/赢家均零命中或判错

- 参考：-0.2；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 诊断质量：0.0000→0.0000；50权重零/错48次，满/对2次。
- 模型字幕：Just let me know like this, and then I will do it immediately.
- 中文：就告诉我一声这样子，然后我当时就。
- 起点回答：The character's emotional state is positive, willing to act, enthusiastic.
- 赢家回答：The character's emotional state is positive, enthusiastic.
- 起点抽取：[positive, enthusiastic]
- 赢家抽取：[positive, enthusiastic]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_INTONATION_RISING, VIS_BROWS_RAISED
- 图候选：hopeful, anxious, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.938082134295019}, {"state": "AGC_INCONGRUENT", "relative_support": 0.061917865704981034}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.5521798761273948}, {"state": "AEX_EXPECTED", "relative_support": 0.4478201238726051}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6344174945793424}, {"state": "AAG_OTHER", "relative_support": 0.3655825054206576}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7173417993385709}, {"state": "ACT_CERTAIN", "relative_support": 0.2826582006614291}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/test14_00010.mp4

## 58. SIMSv2 / aqgy3_0004_00011 — 起点/赢家均零命中或判错

- 参考：0.6；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 诊断质量：0.0000→0.0000；50权重零/错19次，满/对31次。
- 模型字幕：I want to find a job by myself and be self-reliant.
- 中文：我要自己找一份工作，自力更生。
- 起点回答：The character's emotional state is anxiety, fear, stress, uncertainty, tension, unease, determination, resolve.
- 赢家回答：The character's emotional state is anxiety, tension, motivation, determination, sense of urgency, frustration, anger, confusion, uncertainty, longing, desire.
- 起点抽取：[anxiety, fear, stress, uncertainty, tension, unease, determination, resolve]
- 赢家抽取：[anxiety, tension, motivation, determination, frustration, anger, confusion, uncertainty, longing, desire]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_DESIRE_NEED, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：anxious, hopeful, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.920735471231747}, {"state": "AGC_INCONGRUENT", "relative_support": 0.07926452876825295}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7265592164472656}, {"state": "AEX_EXPECTED", "relative_support": 0.27344078355273427}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5106807080680038}, {"state": "AAG_OTHER", "relative_support": 0.48931929193199614}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.993820786987353}, {"state": "ACT_CERTAIN", "relative_support": 0.006179213012647059}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/aqgy3_0004_00011.mp4

## 59. SIMSv2 / test5_00008 — 起点/赢家均满命中或判对

- 参考：-0.4；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 诊断质量：1.0000→1.0000；50权重零/错0次，满/对50次。
- 模型字幕：Your grandmother treats you so well, other children don't have this treatment, and you still don't study hard.
- 中文：你外婆对你这么好，别的孩子都没有这个待遇，你还不好好学习。
- 起点回答：The character's emotional state is anger, disappointment, anxiety, stress.
- 赢家回答：The character's emotional state is disappointment, frustration, anger.
- 起点抽取：[anger, disappointment, anxiety, stress]
- 赢家抽取：[disappointment, frustration, anger]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN
- 图候选：depressed, appreciated, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9838623928388527}, {"state": "AGR_RELEVANT", "relative_support": 0.016137607161147295}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.44342386373601694}, {"state": "AGC_MIXED", "relative_support": 0.29895470351076686}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8324866403564096}, {"state": "AEX_UNEXPECTED", "relative_support": 0.16751335964359043}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5354556118683871}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4448032166992682}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7447492912675965}, {"state": "ACT_UNCERTAIN", "relative_support": 0.25525070873240363}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.658964127026355}, {"state": "ACP_HIGH", "relative_support": 0.34103587297364507}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/test5_00008.mp4

## 60. SIMSv2 / aqgy5_0017_00014 — 起点/赢家均满命中或判对

- 参考：0.8；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 诊断质量：1.0000→1.0000；50权重零/错0次，满/对50次。
- 模型字幕：If it is a cute and big castle, that would be even better.
- 中文：如果是一个萌萌的大城堡那就更好了。
- 起点回答：The character's emotional state is excitement, enthusiasm, positivity, optimism.
- 赢家回答：The character's emotional state is excited, enthusiastic, positive, fantasy, desire.
- 起点抽取：[excitement, enthusiasm, positivity, optimism]
- 赢家抽取：[excited, enthusiastic, positive]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：hopeful, joy, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7864911154483583}, {"state": "AGC_MIXED", "relative_support": 0.16738345762321272}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6386784486244328}, {"state": "AEX_EXPECTED", "relative_support": 0.36132155137556715}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6986187348722006}, {"state": "AAG_SELF", "relative_support": 0.3013812651277993}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6447394975061196}, {"state": "ACT_CERTAIN", "relative_support": 0.3552605024938804}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.9758924849075253}, {"state": "ACP_LOW", "relative_support": 0.024107515092474698}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/aqgy5_0017_00014.mp4

## 61. SIMSv2 / test13_00008 — 相对起点诊断改善

- 参考：0.4；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 诊断质量：0.0000→1.0000；50权重零/错29次，满/对21次。
- 模型字幕：Should we go to the Forbidden City and the Great Wall? It's meaningless to talk about such places.
- 中文：我说故宫长城去不去，这种地方说出来就很没有意义。
- 起点回答：The character's emotional state is disapproval, discontentment, anxiety, tension.
- 赢家回答：The character's emotional state is happiness, relaxation, humor.
- 起点抽取：[disapproval, discontentment, anxiety, tension]
- 赢家抽取：[happiness, relaxation, humor]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：disappointed, joy, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.49326644198737335}, {"state": "AGC_CONGRUENT", "relative_support": 0.4339304374907931}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7302177487953085}, {"state": "AEX_UNEXPECTED", "relative_support": 0.2697822512046915}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.47697404739805704}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3684188135503686}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6075605499998695}, {"state": "ACT_UNCERTAIN", "relative_support": 0.3924394500001305}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6555057917999702}, {"state": "ACP_HIGH", "relative_support": 0.34449420820002974}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/test13_00008.mp4

## 62. SIMSv2 / video_0040_0046 — 相对起点诊断改善

- 参考：-0.2；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 诊断质量：0.0000→1.0000；50权重零/错18次，满/对32次。
- 模型字幕：But after all, Zhang Ji is an elder.
- 中文：但张冀毕竟是个元老
- 起点回答：The character's emotional state is serious, tense, confident, authoritative, persuasive.
- 赢家回答：The character's emotional state is objective, neutral.
- 起点抽取：[serious, tense, confident, authoritative, persuasive]
- 赢家抽取：[]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_CONTRAST_PRESENT, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN
- 图候选：disappointed, depressed, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_MIXED", "relative_support": 0.4872519811333174}, {"state": "AGC_INCONGRUENT", "relative_support": 0.4846723287107064}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.5266945732700724}, {"state": "AEX_EXPECTED", "relative_support": 0.4733054267299276}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.37455070747459296}, {"state": "AAG_OTHER", "relative_support": 0.35639040240050385}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6490982549438794}, {"state": "ACT_UNCERTAIN", "relative_support": 0.35090174505612065}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.990951698145581}, {"state": "ACP_HIGH", "relative_support": 0.009048301854418891}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/video_0040_0046.mp4

## 63. SIMSv2 / aqgy5_0014_00032 — 相对起点诊断恶化

- 参考：0.2；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 诊断质量：1.0000→0.0000；50权重零/错9次，满/对41次。
- 模型字幕：When I am sad and upset, you always accompany me, patiently listening to me and chatting with me without getting tired.
- 中文：在我伤心难过的时候都会陪着我，不厌其烦的听我倾诉陪我聊天。
- 起点回答：The character's emotional state is sadness, appreciation, gratitude.
- 赢家回答：The character's emotional state is gratitude, appreciation, sadness.
- 起点抽取：[sadness, appreciation, gratitude]
- 赢家抽取：[gratitude, appreciation, sadness]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_HEAD_LOWERED
- 图候选：disappointed, helpless, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8125720797787206}, {"state": "AGC_MIXED", "relative_support": 0.09747879557921711}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7942329509980229}, {"state": "AEX_UNEXPECTED", "relative_support": 0.20576704900197712}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.49464942398882167}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.46343033462525907}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7336117594811428}, {"state": "ACT_UNCERTAIN", "relative_support": 0.2663882405188572}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9882839965488397}, {"state": "ACP_HIGH", "relative_support": 0.011716003451160258}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/aqgy5_0014_00032.mp4

## 64. SIMSv2 / aqgy5_0013_00019 — 相对起点诊断恶化

- 参考：-1.0；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 诊断质量：1.0000→0.0000；50权重零/错3次，满/对47次。
- 模型字幕：I warn you, don't take my tolerance as your shameless capital.
- 中文：我警告你，别拿我的容忍，当成你们不要脸的资本。
- 起点回答：The character's emotional state is anger, frustration, dissatisfaction.
- 赢家回答：The character's emotional state is anger, frustration, confidence, determination.
- 起点抽取：[anger, frustration, dissatisfaction]
- 赢家抽取：[anger, frustration, confidence, determination]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, AUD_VOICE_TENSE, VIS_BROWS_FURROWED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN
- 图候选：anger, disappointed, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9437903679954915}, {"state": "AGC_CONGRUENT", "relative_support": 0.04870116984842202}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8288638182015561}, {"state": "AEX_EXPECTED", "relative_support": 0.1711361817984438}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8007139561938463}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.11243288178167932}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.5275780193917586}, {"state": "ACT_CERTAIN", "relative_support": 0.4724219806082413}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9173987211772373}, {"state": "ACP_HIGH", "relative_support": 0.08260127882276269}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/aqgy5_0013_00019.mp4

## 65. OVMERDPlus / sample_00001097 — 起点/赢家均零命中或判错

- 参考：curious；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 诊断质量：0.0000→0.0000；50权重零/错16次，满/对3次。
- 模型字幕：What are you touching here?
- 中文：
- 起点回答：The character's emotional state is dissatisfaction, frustration, confusion.
- 赢家回答：The character's emotional state is anger, dissatisfaction, tension, anxiety.
- 起点抽取：[dissatisfaction, frustration, confusion]
- 赢家抽取：[anger, dissatisfaction, tension, anxiety]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_POSITIVE, TXT_RHETORICAL_QUESTION, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, apathetic, trusting（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8257509941498663}, {"state": "AGC_INCONGRUENT", "relative_support": 0.17424900585013378}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8761756186322074}, {"state": "AAG_SELF", "relative_support": 0.12382438136779254}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9736501957913426}, {"state": "ACT_CERTAIN", "relative_support": 0.026349804208657415}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8755827977092134}, {"state": "ACP_LOW", "relative_support": 0.12441720229078647}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00001097.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.0000|The character's emotional state is anger, dissatisfaction, tension.|
|base35_B|0.4667|The emotional state is excited, curious, frustrated, anxious.|
|base35_C|0.6667|The character's emotional state is inquiry, dissatisfaction, curiosity.|
|base35_D|0.4667|The emotional state is excited, curious, frustrated, anxious.|
|base35_E|0.6667|The character's emotional state is inquiry, dissatisfaction, curiosity.|
|base35_F|0.6667|The character's emotional state is inquiry, dissatisfaction, curiosity.|
|graph40_A|0.4667|The character's emotional state is anger, dissatisfaction, curiosity, excitement.|
|graph40_B|0.3778|The character's emotional state is anger, frustration, contemplation, focus, anxiety, tension, curiosity, interest.|
|graph40_C|0.4667|The character's emotional state is anger, dissatisfaction, curiosity, excitement.|
|graph40_D|0.3778|The character's emotional state is anger, frustration, contemplation, focus, anxiety, tension, curiosity, interest.|
|graph40_E|0.4667|The character's emotional state is anger, dissatisfaction, curiosity, excitement.|
|graph40_F|0.4667|The character's emotional state is anger, dissatisfaction, curiosity, excitement.|
|base35_G|0.6667|The character's emotional state is inquiry, dissatisfaction, curiosity.|
|graph40_G|0.4667|The character's emotional state is anger, dissatisfaction, curiosity, excitement.|

## 66. OVMERDPlus / samplenew3_00033160 — 起点/赢家均零命中或判错

- 参考：fearlessness, encouragement, seriousness, determination；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 诊断质量：0.0000→0.0000；50权重零/错37次，满/对0次。
- 模型字幕：You just stand up and poke a hole down.
- 中文：
- 起点回答：The character's emotional state is urgent, pressured, negative.
- 赢家回答：The character's emotional state is tense, anxious.
- 起点抽取：[urgent, pressured, negative]
- 赢家抽取：[tense, anxious]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_INTENSIFIER_PRESENT, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN, VIS_HEAD_LOWERED
- 图候选：disappointed, anger, depressed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9152252719895545}, {"state": "AGC_CONGRUENT", "relative_support": 0.05798544288202373}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6206893371892747}, {"state": "AEX_UNEXPECTED", "relative_support": 0.3793106628107253}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4312593343225332}, {"state": "AAG_OTHER", "relative_support": 0.31023319073602823}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.748416644394725}, {"state": "ACT_UNCERTAIN", "relative_support": 0.25158335560527506}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9905734548153725}, {"state": "ACP_HIGH", "relative_support": 0.009426545184627516}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/samplenew3_00033160.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.0000|The character's emotional state is tense, anxious.|
|base35_B|0.2600|The emotional state is calm, rational, anxious, stressed, depressed, negative.|
|base35_C|0.1000|The emotional state of the character can be inferred to be confused, anxious, uncertain, helpless.|
|base35_D|0.4400|The emotional state is sad, fear, anger.|
|base35_E|0.4400|The character's emotional state is sadness, anger, fear.|
|base35_F|0.0000|The character's emotional state is tense, anxious.|
|graph40_A|0.0000|The character's emotional state is tense, anxious.|
|graph40_B|0.0000|The character's emotional state is tense, anxious.|
|graph40_C|0.0000|The character's emotional state is tense, anxious.|
|graph40_D|0.0000|The character's emotional state is tense, anxious.|
|graph40_E|0.0000|The character's emotional state is tense, anxious.|
|graph40_F|0.0000|The character's emotional state is tense, anxious.|
|base35_G|0.1000|The character's emotional state is tense, anxious, overwhelmed, under pressure.|
|graph40_G|0.0000|The character's emotional state is tense, anxious.|

## 67. OVMERDPlus / sample_00000476 — 起点/赢家均满命中或判对

- 参考：anxiety, worry；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 诊断质量：1.0000→1.0000；50权重零/错0次，满/对26次。
- 模型字幕：Why haven't you come back yet?
- 中文：
- 起点回答：The character's emotional state is anxiety, concern, worry.
- 赢家回答：The character's emotional state is concern, anxiety.
- 起点抽取：[anxiety, concern, worry]
- 赢家抽取：[concern, anxiety]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9140841100741095}, {"state": "AGC_CONGRUENT", "relative_support": 0.08591588992589048}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9896559602999604}, {"state": "AEX_EXPECTED", "relative_support": 0.010344039700039588}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 1.0}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9241204496059592}, {"state": "ACT_CERTAIN", "relative_support": 0.07587955039404078}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8118840699892831}, {"state": "ACP_HIGH", "relative_support": 0.18811593001071703}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00000476.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.6667|The character's emotional state is anxious, frustrated.|
|base35_B|0.6667|The character's emotional state is anxious, frustrated.|
|base35_C|1.0000|The character's emotional state is concern, anxiety.|
|base35_D|0.6667|The character's emotional state is anxious, frustrated.|
|base35_E|0.6667|The character's emotional state is anxious, frustrated.|
|base35_F|0.6667|The character's emotional state is anxious, frustrated.|
|graph40_A|1.0000|The character's emotional state is concern, anxiety.|
|graph40_B|0.6667|The character's emotional state is anxious, frustrated.|
|graph40_C|1.0000|The character's emotional state is concern, anxiety.|
|graph40_D|1.0000|The character's emotional state is concern, anxiety.|
|graph40_E|1.0000|The character's emotional state is concern, anxiety.|
|graph40_F|1.0000|The character's emotional state is concern, anxiety.|
|base35_G|0.6667|The character's emotional state is anxious, frustrated.|
|graph40_G|1.0000|The character's emotional state is concern, anxiety.|

## 68. OVMERDPlus / sample_00003084 — 起点/赢家均满命中或判对

- 参考：angry, dissatisfied；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 诊断质量：1.0000→1.0000；50权重零/错0次，满/对39次。
- 模型字幕：What's up, just before leaving, you want to unite with your father.
- 中文：
- 起点回答：The character's emotional state is anger, dissatisfaction.
- 赢家回答：The character's emotional state is anger, frustration.
- 起点抽取：[anger, dissatisfaction]
- 赢家抽取：[anger, frustration]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_RHETORICAL_QUESTION, TXT_DESIRE_NEED, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9801370340825751}, {"state": "AGR_RELEVANT", "relative_support": 0.019862965917424803}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9350150376042735}, {"state": "AGC_CONGRUENT", "relative_support": 0.06498496239572649}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8359425164585044}, {"state": "AEX_EXPECTED", "relative_support": 0.16405748354149563}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6863391319539058}, {"state": "AAG_SELF", "relative_support": 0.19795463671312472}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9688452233341166}, {"state": "ACT_CERTAIN", "relative_support": 0.03115477666588341}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8360114502707165}, {"state": "ACP_HIGH", "relative_support": 0.16398854972928342}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00003084.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|1.0000|The character's emotional state is anger, dissatisfaction.|
|base35_B|1.0000|The character's emotional state is anger, dissatisfaction.|
|base35_C|1.0000|The character's emotional state is anger, dissatisfaction.|
|base35_D|1.0000|The character's emotional state is anger, dissatisfaction.|
|base35_E|1.0000|The character's emotional state is anger, dissatisfaction.|
|base35_F|1.0000|The character's emotional state is anger, dissatisfaction.|
|graph40_A|1.0000|The character's emotional state is anger, dissatisfaction.|
|graph40_B|1.0000|The character's emotional state is anger, dissatisfaction.|
|graph40_C|1.0000|The character's emotional state is anger, frustration.|
|graph40_D|1.0000|The character's emotional state is anger, dissatisfaction.|
|graph40_E|1.0000|The character's emotional state is anger, frustration.|
|graph40_F|1.0000|The character's emotional state is anger, frustration.|
|base35_G|1.0000|The character's emotional state is anger, dissatisfaction.|
|graph40_G|1.0000|The character's emotional state is anger, frustration.|

## 69. OVMERDPlus / samplenew3_00033143 — 相对起点诊断改善

- 参考：unease, curiosity, worry, nervousness, confusion；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 诊断质量：0.7067→0.8800；50权重零/错0次，满/对2次。
- 模型字幕：What is this customer?
- 中文：
- 起点回答：The character's emotional state is anxious, tense, dissatisfied.
- 赢家回答：The character's emotional state is confused, inquisitive.
- 起点抽取：[anxious, tense, dissatisfied]
- 赢家抽取：[confused, inquisitive]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_RHETORICAL_QUESTION, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_RISING
- 图候选：apathetic, bewildered, sceptical（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8533945285014902}, {"state": "AGC_MIXED", "relative_support": 0.14660547149850978}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9715989762417421}, {"state": "AEX_EXPECTED", "relative_support": 0.02840102375825792}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5456757956400303}, {"state": "AAG_SELF", "relative_support": 0.23812188290559033}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/samplenew3_00033143.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.8800|The character's emotional state is confused, curious, puzzled.|
|base35_B|0.0000||
|base35_C|0.7200|The character's emotional state is confused, uncertain, puzzled.|
|base35_D|0.8800|The character's emotional state is confused, anxious, puzzled.|
|base35_E|0.8267|The character's emotional state is confused, anxious, uncertain.|
|base35_F|0.7200|The character's emotional state is confused, uncertain, puzzled.|
|graph40_A|0.8800|The character's emotional state is confused, inquisitive.|
|graph40_B|0.8800|The character's emotional state is confused, inquisitive.|
|graph40_C|0.8800|The character's emotional state is confused, inquisitive.|
|graph40_D|0.8800|The character's emotional state is confused, inquisitive.|
|graph40_E|0.8800|The character's emotional state is curious, confused, focused.|
|graph40_F|0.8800|The character's emotional state is confused, inquisitive.|
|base35_G|0.6333|The character's emotional state could be confusion, curiosity, surprise, contemplation, frustration, doubt.|
|graph40_G|0.8800|The character's emotional state is confused, inquisitive.|

## 70. OVMERDPlus / samplenew3_00004480 — 相对起点诊断改善

- 参考：alert, concentrate, doubt, worry, serious, reflect, ponder；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 诊断质量：0.4733→0.5267；50权重零/错0次，满/对0次。
- 模型字幕：I think we should check the company's network system. Our system might have been hacked.
- 中文：
- 起点回答：The character's emotional state is tension, concern.
- 赢家回答：The character's emotional state is serious, concerned, anxious.
- 起点抽取：[tension, concern]
- 赢家抽取：[serious, concerned, anxious]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_UNCERTAINTY_HEDGE, TXT_DESIRE_NEED, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED
- 图候选：disappointed, anger, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.8612352750209481}, {"state": "AGR_RELEVANT", "relative_support": 0.13876472497905193}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7330711656617009}, {"state": "AGC_CONGRUENT", "relative_support": 0.15414279592803076}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7840010537636004}, {"state": "AEX_UNEXPECTED", "relative_support": 0.21599894623639962}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.44768694676706644}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3209202296459627}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7007611300104516}, {"state": "ACT_CERTAIN", "relative_support": 0.2992388699895484}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7629782071416022}, {"state": "ACP_HIGH", "relative_support": 0.23702179285839775}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/samplenew3_00004480.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.5314|The character's emotional state is serious, focused, anxious, tense.|
|base35_B|0.4400|The character's emotional state is concerned, worried, tense.|
|base35_C|0.4200|The character's emotional state is concerned, worried, uncertain.|
|base35_D|0.4000|The character's emotional state is concerned, tense, uncertain.|
|base35_E|0.4000|The character's emotional state is concerned, tense, uncertain.|
|base35_F|0.4400|The character's emotional state is anxious, concerned, tense.|
|graph40_A|0.7981|The character's emotional state is anxious, nervous, under pressure, concern, worry, anger, frustration.|
|graph40_B|0.7981|The character's emotional state is anxious, nervous, under pressure, concern, worry, anger, frustration.|
|graph40_C|0.4733|The character's emotional state is anxious, nervous, under pressure.|
|graph40_D|0.4733|The character's emotional state is anxious, nervous, concerned.|
|graph40_E|0.4733|The character's emotional state is anxious, nervous, under pressure.|
|graph40_F|0.7981|The character's emotional state is anxious, nervous, under pressure, concern, worry, anger, frustration.|
|base35_G|0.4200|The character's emotional state is anxious, concerned, uncertain.|
|graph40_G|0.4733|The character's emotional state is anxious, nervous, under pressure.|

## 71. OVMERDPlus / sample_00000689 — 相对起点诊断恶化

- 参考：provocation, angry, impatient, complaint, dissatisfaction；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 诊断质量：0.8533→0.5943；50权重零/错0次，满/对0次。
- 模型字幕：Wang Sufen, I have been waiting for you for a long time.
- 中文：
- 起点回答：The character's emotional state is frustration, anger.
- 赢家回答：The character's emotional state is anxiety, impatience, frustration.
- 起点抽取：[frustration, anger]
- 赢家抽取：[anxiety, impatience, frustration]
- 实际证据level：3；原因：['supported_full_evidence']。
- Cue：TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED
- 图候选：content, acceptance, fulfilled（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.47971177731029835}, {"state": "AGC_CONGRUENT", "relative_support": 0.38516714830401877}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7528295061610324}, {"state": "AEX_UNEXPECTED", "relative_support": 0.2471704938389676}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5816971277348724}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.33546610460676524}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6717045532559677}, {"state": "ACT_UNCERTAIN", "relative_support": 0.3282954467440323}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5230429618448}, {"state": "ACP_HIGH", "relative_support": 0.4769570381552}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00000689.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.5943|The character's emotional state is anxiety, impatience, frustration.|
|base35_B|0.2267|The character's emotional state is anxiety, disappointment.|
|base35_C|0.2267|The character's emotional state is anxiety, disappointment, dissatisfaction.|
|base35_D|0.2267|The character's emotional state is anxiety, disappointment.|
|base35_E|0.2267|The character's emotional state is anxiety, disappointment, dissatisfaction.|
|base35_F|0.2267|The character's emotional state is anxiety, disappointment.|
|graph40_A|0.5943|The character's emotional state is anxiety, impatience, frustration.|
|graph40_B|0.5943|The character's emotional state is anxiety, impatience, frustration.|
|graph40_C|0.5943|The character's emotional state is anxiety, impatience, frustration.|
|graph40_D|0.5943|The character's emotional state is anxiety, impatience, frustration.|
|graph40_E|0.5943|The character's emotional state is anxiety, impatience, frustration.|
|graph40_F|0.5943|The character's emotional state is anxiety, impatience, frustration.|
|base35_G|0.2267|The character's emotional state is anxiety, disappointment.|
|graph40_G|0.5943|The character's emotional state is anxiety, impatience, frustration.|

## 72. OVMERDPlus / sample_00000927 — 相对起点诊断恶化

- 参考：excited, joyful, happy；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 诊断质量：0.6667→0.5133；50权重零/错0次，满/对0次。
- 模型字幕：Little earthworm, when are you coming back?
- 中文：
- 起点回答：The character's emotional state is anticipation, longing, positive.
- 赢家回答：The character's emotional state is urgent, anxious, humorous, relaxed, happy.
- 起点抽取：[anticipation, longing, positive]
- 赢家抽取：[urgent, anxious, humorous, relaxed, happy]
- 实际证据level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_RHETORICAL_QUESTION, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5645662897235852}, {"state": "AGC_CONGRUENT", "relative_support": 0.4354337102764147}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8914102484619671}, {"state": "AAG_SELF", "relative_support": 0.10858975153803287}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9963791966967548}, {"state": "ACT_CERTAIN", "relative_support": 0.00362080330324517}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5087312900083941}, {"state": "ACP_LOW", "relative_support": 0.49126870999160593}]}
- 服务器视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00000927.mp4

|后续实验|诊断质量|原回答|
|---|---:|---|
|base35_A|0.6667|The character's emotional state is anticipation, longing, positive.|
|base35_B|0.7667|The character's emotional state is anticipation, longing, curiosity, tension, desire.|
|base35_C|0.5467|The character's emotional state is anticipation, longing, curiosity, desire, uncertainty.|
|base35_D|0.7667|The character's emotional state is anticipation, longing, curiosity, tension, desire.|
|base35_E|0.5467|The character's emotional state is anticipation, longing, curiosity, desire, uncertainty.|
|base35_F|0.5667|The character's emotional state is anticipation, longing, curiosity, tension, uncertainty.|
|graph40_A|0.3333|The character's emotional state is urgent, anticipatory, affectionate, concerned.|
|graph40_B|0.3333|The character's emotional state is urgent, anticipatory, affectionate, concerned.|
|graph40_C|0.3333|The character's emotional state is urgent, anticipatory, affectionate, concerned.|
|graph40_D|0.3333|The character's emotional state is urgent, anticipatory, affectionate, concerned.|
|graph40_E|0.3333|The character's emotional state is urgent, anticipatory, affectionate, concerned.|
|graph40_F|0.3333|The character's emotional state is urgent, anticipatory, affectionate, concerned.|
|base35_G|0.5667|The character's emotional state is anticipation, longing, curiosity, tension, uncertainty.|
|graph40_G|0.3333|The character's emotional state is urgent, anticipatory, affectionate, concerned.|
