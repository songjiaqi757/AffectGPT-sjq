# 新增166例逐样本目录

固定分层抽取，排除上轮72例；OV诊断F不等于官方F_s。详细口径见EXPANDED_REPORT.md。

## 1. MER2023 / sample_00001907 — 50权重持续错误/零命中

- 参考：angry；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：Are you being asked? Did he say anything?
- 中文：问你话呢？他说了没有。
- 起点回答：The character's emotional state is tense, uneasy, concerned, uncertain.
- 赢家回答：The character's emotional state is nervousness, anxiety, sadness.
- 起点抽取：[tense, uneasy, concerned, uncertain]
- 赢家抽取：[nervousness, anxiety, sadness]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN
- 图候选：apathetic, disappointed, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 1.0}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00001907.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is tension, anxiety.|
|long_graph_dataset_best|0.0000|The character's emotional state is tense, anxious.|
|base35_A|0.0000|The character's emotional state is nervous, anxious, tense, anxious.|
|base35_B|0.0000|The emotional state is anxious, tense, worried, concerned.|
|base35_C|0.0000|The character's emotional state is anxious, tense, concerned.|
|base35_D|0.0000|The character's emotional state is anxious, tense, concerned.|
|base35_E|0.0000|The character's emotional state is anxious, tense, concerned.|
|base35_F|0.0000|The character's emotional state is anxious, tense, concerned.|
|graph40_A|0.0000|The character's emotional state is nervous, uneasy, tense, anxious.|
|graph40_B|0.0000|The character's emotional state is nervous, uneasy, tense, anxious.|
|graph40_C|0.0000|The character's emotional state is nervous, uneasy, tense, anxious.|
|graph40_D|0.0000|The character's emotional state is nervous, uneasy, tense, anxious.|
|graph40_E|0.0000|The character's emotional state is nervous, uneasy, tense, anxious.|
|graph40_F|0.0000|The character's emotional state is nervousness, worry.|
|base35_G|0.0000|The character's emotional state is anxious, tense, concerned.|
|graph40_G|0.0000|The character's emotional state is nervousness, worry.|

## 2. MER2023 / sample_00004856 — 50权重持续错误/零命中

- 参考：surprise；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：Thirty-five thousand is too low, isn't it? This car of mine should at least, at least sell for eighty thousand, right?
- 中文：三五万太低了吧？我这车怎么着也得，也得卖八万块吧。
- 起点回答：The character's emotional state is anger, frustration, disappointment.
- 赢家回答：The character's emotional state is disappointment, dissatisfaction, frustration.
- 起点抽取：[anger, frustration, disappointment]
- 赢家抽取：[disappointment, dissatisfaction, frustration]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_RISING, VIS_BROWS_FURROWED
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9929454025602688}, {"state": "AGR_RELEVANT", "relative_support": 0.007054597439731272}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8463861474557953}, {"state": "AGC_MIXED", "relative_support": 0.09808666118451301}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6834883754105158}, {"state": "AEX_EXPECTED", "relative_support": 0.31651162458948434}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.44597751706440414}, {"state": "AAG_SELF", "relative_support": 0.3524538697310451}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.813097927639721}, {"state": "ACT_CERTAIN", "relative_support": 0.186902072360279}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8431986041724108}, {"state": "ACP_HIGH", "relative_support": 0.15680139582758928}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00004856.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is anger, frustration, dissatisfaction.|
|long_graph_dataset_best|0.2500|The character's emotional state is discontent, anger.|
|base35_A|0.0000|The character's emotional state is dissatisfaction, anger.|
|base35_B|0.0000|The character's emotional state is dissatisfaction, anger.|
|base35_C|0.0000|The character's emotional state is disappointment, dissatisfaction, frustration.|
|base35_D|0.0000|The character's emotional state is dissatisfaction, anger.|
|base35_E|0.0000|The character's emotional state is disappointment, dissatisfaction, frustration.|
|base35_F|0.0000|The character's emotional state is disappointment, dissatisfaction, frustration.|
|graph40_A|0.0000|The character's emotional state is disappointment, dissatisfaction, frustration.|
|graph40_B|0.0000|The character's emotional state is disappointment, dissatisfaction, frustration.|
|graph40_C|0.0000|The character's emotional state is disappointment, dissatisfaction, frustration.|
|graph40_D|0.0000|The character's emotional state is disappointment, dissatisfaction, frustration.|
|graph40_E|0.0000|The character's emotional state is disappointment, dissatisfaction, frustration.|
|graph40_F|0.0000|The character's emotional state is disappointment, dissatisfaction, frustration.|
|base35_G|0.0000|The character's emotional state is disappointment, dissatisfaction, frustration.|
|graph40_G|0.0000|The character's emotional state is disappointment, dissatisfaction, frustration.|

## 3. MER2023 / sample_00000491 — 50权重持续错误/零命中

- 参考：angry；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：He is a good person.
- 中文：他是好人。
- 起点回答：The character's emotional state is positive, praise, affirmation.
- 赢家回答：The character's emotional state is appreciative, affirmative.
- 起点抽取：[positive]
- 赢家抽取：[appreciative, affirmative]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8079441590586514}, {"state": "AGC_MIXED", "relative_support": 0.17229180081467904}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6527771750777147}, {"state": "AEX_EXPECTED", "relative_support": 0.3472228249222854}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7895177150450293}, {"state": "AAG_SELF", "relative_support": 0.2104822849549707}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7156639530269857}, {"state": "ACT_CERTAIN", "relative_support": 0.2843360469730144}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00000491.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is positive, excitement, enthusiasm.|
|long_graph_dataset_best|0.0000|The character's emotional state is happiness, satisfaction.|
|base35_A|0.0000|The character's emotional state is appreciative, affirmative.|
|base35_B|0.0000|The character's emotional state is positive, enthusiastic, excited.|
|base35_C|0.0000|The character's emotional state is positive evaluation, excitement.|
|base35_D|0.0000|The character's emotional state is positive, enthusiastic, excited.|
|base35_E|0.0000|The character's emotional state is positive evaluation, excitement.|
|base35_F|0.0000|The character's emotional state is positive, excitement, surprise.|
|graph40_A|0.0000|The character's emotional state is positive, appreciative.|
|graph40_B|0.0000|The character's emotional state is appreciative, affirmative.|
|graph40_C|0.0000|The character's emotional state is positive, happy, satisfied.|
|graph40_D|0.0000|The character's emotional state is appreciative, affirmative.|
|graph40_E|0.0000|The character's emotional state is positive, happy, satisfied.|
|graph40_F|0.0000|The character's emotional state is positive, praise, affirmation, happiness, confidence.|
|base35_G|0.0000|The character's emotional state is positive, excitement, surprise.|
|graph40_G|0.0000|The character's emotional state is positive, praise, affirmation, happiness, confidence.|

## 4. MER2023 / sample_00001006 — 50权重持续正确/满命中

- 参考：worried；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：Oh no, what should I do?
- 中文：哎呦，我怎么办？
- 起点回答：The character's emotional state is confused, anxious, helpless, helpless.
- 赢家回答：The character's emotional state is anxiety, tension, distress.
- 起点抽取：[confused, anxious, helpless]
- 赢家抽取：[anxiety, tension, distress]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_LOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_RISING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN, VIS_HEAD_LOWERED
- 图候选：depressed, despair, ashamed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5317414333896827}, {"state": "AGC_CONGRUENT", "relative_support": 0.3795183075895822}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5020183178090851}, {"state": "AEX_UNEXPECTED", "relative_support": 0.4979816821909149}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.49952508335881873}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.36356163321998264}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9253355821092891}, {"state": "ACT_CERTAIN", "relative_support": 0.07466441789071099}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7164783584825148}, {"state": "ACP_HIGH", "relative_support": 0.2835216415174852}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00001006.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is confused, anxious, frustrated, sad, disappointed.|
|long_graph_dataset_best|1.0000|The character's emotional state is sadness, despair, anxiety, helplessness.|
|base35_A|1.0000|The character's emotional state is anxiety, tension, distress.|
|base35_B|1.0000|The character's emotional state is anxiety, fear, overwhelmed, sadness, depression, boredom, emotional numbness.|
|base35_C|1.0000|The character's emotional state is anxiety, fear, overwhelmed.|
|base35_D|1.0000|The character might be experiencing fear, anxiety, or sadness.|
|base35_E|0.8000|The character's emotional state is sadness, fear, powerlessness.|
|base35_F|0.8000|The character's emotional state is sadness, fear, power.|
|graph40_A|1.0000|The character's emotional state is anxiety, tension, distress.|
|graph40_B|1.0000|The character's emotional state is anxiety, distress, confusion.|
|graph40_C|1.0000|The character's emotional state is anxiety, tension, distress.|
|graph40_D|1.0000|The character's emotional state is anxiety, stress, distress.|
|graph40_E|1.0000|The character's emotional state is anxiety, tension, distress.|
|graph40_F|1.0000|The character's emotional state is anxiety, tension, distress.|
|base35_G|1.0000|The character's emotional state is anxiety, tension, distress.|
|graph40_G|1.0000|The character's emotional state is anxiety, tension, distress.|

## 5. MER2023 / sample_00006932 — 50权重持续正确/满命中

- 参考：happy；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：Thank you all, thank you for not treating me as an outsider. Actually, before this, I thought I only had one friend in my life, Old Tan. I didn't expect to meet you all on the 22nd floor.
- 中文：谢谢你们，谢谢你们没有跟我见外。其实在这之前，我以为我这辈子只有老谭这一个朋友，没想到在二十二楼还能遇到你们
- 起点回答：The character's emotional state is grateful, joyful, happy.
- 赢家回答：The character's emotional state is gratitude, joy, surprise.
- 起点抽取：[grateful, joyful, happy]
- 赢家抽取：[gratitude, joy, surprise]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9840129937619453}, {"state": "AGR_RELEVANT", "relative_support": 0.015987006238054782}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6378763940836424}, {"state": "AGC_MIXED", "relative_support": 0.2531843650862862}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8328520507904456}, {"state": "AEX_UNEXPECTED", "relative_support": 0.16714794920955453}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6324370416430479}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3618938760084871}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7711306796249662}, {"state": "ACT_UNCERTAIN", "relative_support": 0.22886932037503377}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.6716381779312297}, {"state": "ACP_LOW", "relative_support": 0.32836182206877035}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00006932.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is gratitude, joy, surprise.|
|long_graph_dataset_best|1.0000|The character's emotional state is grateful, surprised, happy.|
|base35_A|1.0000|The character's emotional state is gratitude, joy, happiness.|
|base35_B|1.0000|The character's emotional state is gratitude, surprise, happiness.|
|base35_C|1.0000|The character's emotional state is gratitude, surprise, happiness, anxiety.|
|base35_D|1.0000|The character's emotional state is gratitude, surprise, happiness.|
|base35_E|1.0000|The character's emotional state is gratitude, surprise, happiness, anxiety.|
|base35_F|1.0000|The character's emotional state is gratitude, surprise, happiness, anxiety.|
|graph40_A|1.0000|The character's emotional state is gratitude, joy, surprise.|
|graph40_B|1.0000|The character's emotional state is gratitude, joy, surprise.|
|graph40_C|1.0000|The character's emotional state is gratitude, joy, surprise.|
|graph40_D|1.0000|The character's emotional state is gratitude, joy, surprise.|
|graph40_E|1.0000|The character's emotional state is gratitude, joy, surprise.|
|graph40_F|1.0000|The character's emotional state is gratitude, joy, surprise.|
|base35_G|1.0000|The character's emotional state is gratitude, surprise, happiness, anxiety.|
|graph40_G|1.0000|The character's emotional state is gratitude, joy, surprise.|

## 6. MER2023 / sample_00002897 — 50权重持续正确/满命中

- 参考：angry；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：I'm telling you, Hu Qixing, do you understand that this is illegal?
- 中文：我告诉你胡七星，这违法你懂不懂？
- 起点回答：The character's emotional state is anger, frustration.
- 赢家回答：The character's emotional state is anger, frustration, anxiety, irritability.
- 起点抽取：[anger, frustration]
- 赢家抽取：[anger, frustration, anxiety, irritability]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_RHETORICAL_QUESTION, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：disappointed, anger, care（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.686012331827605}, {"state": "AGC_CONGRUENT", "relative_support": 0.313987668172395}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.9027663031327765}, {"state": "AAG_SELF", "relative_support": 0.09723369686722345}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8742876845999028}, {"state": "ACT_CERTAIN", "relative_support": 0.12571231540009714}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5756034903633198}, {"state": "ACP_HIGH", "relative_support": 0.42439650963668013}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00002897.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is angry, frustrated, tense.|
|long_graph_dataset_best|1.0000|The character's emotional state is angry, frustrated.|
|base35_A|1.0000|The character's emotional state is anger, frustration.|
|base35_B|1.0000|The character's emotional state is anger, frustration, anxiety, tension.|
|base35_C|1.0000|The character's emotional state is anger, frustration, anxiety, uncertainty.|
|base35_D|1.0000|The character's emotional state is anger, frustration, anxiety, pressure.|
|base35_E|1.0000|The character's emotional state is anger, sadness, power, authority.|
|base35_F|1.0000|The character's emotional state is anger, frustration, anxiety, stress.|
|graph40_A|1.0000|The character's emotional state is anger, frustration.|
|graph40_B|1.0000|The character's emotional state is anger, frustration.|
|graph40_C|1.0000|The character's emotional state is anger, frustration.|
|graph40_D|1.0000|The character's emotional state is anger, frustration.|
|graph40_E|1.0000|The character's emotional state is anger, frustration.|
|graph40_F|1.0000|The character's emotional state is anger, frustration.|
|base35_G|1.0000|The character's emotional state is anger, frustration, anxiety, stress.|
|graph40_G|1.0000|The character's emotional state is anger, frustration.|

## 7. MER2023 / sample_00005903 — 赢家零/错，其他权重经常命中/对

- 参考：happy；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：1.0000→0.0000；50权重零/错3次、满/对12次。
- 模型字幕：How do you know?
- 中文：你咋知道啊？
- 起点回答：The character's emotional state is teasing, playful, positive.
- 赢家回答：The character's emotional state is surprised, incredulous, anxious, frustrated, irritable.
- 起点抽取：[teasing, playful, positive]
- 赢家抽取：[surprised, incredulous, anxious, frustrated, irritable]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_RHETORICAL_QUESTION, TXT_EXCLAMATION_INTERJECTION, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, care, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7669015400736718}, {"state": "AGC_INCONGRUENT", "relative_support": 0.23309845992632822}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8458953423724828}, {"state": "AEX_EXPECTED", "relative_support": 0.15410465762751732}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6831394269119353}, {"state": "AAG_SELF", "relative_support": 0.23072016441013574}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9249433534290393}, {"state": "ACT_CERTAIN", "relative_support": 0.07505664657096074}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7231951459986228}, {"state": "ACP_LOW", "relative_support": 0.2768048540013771}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00005903.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.8000|The character's emotional state is curiosity, surprise, positive.|
|long_graph_dataset_best|0.4000|The character's emotional state is curiosity, surprise, positive mood.|
|base35_A|0.4000|The character's emotional state is surprised, curious.|
|base35_B|0.0000|In this case, the caption reads: "How do you know?" This sentence might be a query or rebuttal from a man to someone else. Given the personal high pitch and fluctuating tone as described in the audio cues, along with the man's's smile and relaxed demeanor depicted in the video clues, we can infer that the statement might be delivered in a questioning or puzzled manner. Thus, this sentence could be the man's's doubt of someone, not knowing how the other person knows certain things.|
|base35_C|1.0000|The character's emotional state is surprised, engaged, happy, confident, curious.|
|base35_D|0.0000|In this case, the caption reads: "How do you know?" This sentence might be a query or rebuttal from a man to someone else. Given the personal high pitch and fluctuating tone as described in the audio cues, along with the man's's smile and relaxed demeanor depicted in the video clues, we can infer that the statement might be delivered in a questioning or puzzled manner. Thus, this sentence could be the man's's doubt of someone, not knowing how the other person knows certain things.|
|base35_E|1.0000|The character's emotional state is surprised, engaged, happy, confident, curious.|
|base35_F|1.0000|The character's emotional state is surprised, engaged, happy, satisfied.|
|graph40_A|0.4000|The character's emotional state is surprised, curious.|
|graph40_B|0.4000|The character's emotional state is surprised, curious.|
|graph40_C|0.4000|The character's emotional state is surprised, curious.|
|graph40_D|0.4000|The character's emotional state is surprised, curious.|
|graph40_E|0.4000|The character's emotional state is surprised, curious.|
|graph40_F|0.4000|The character's emotional state is surprised, curious.|
|base35_G|1.0000|The character's emotional state is surprised, engaged, happy, satisfied.|
|graph40_G|0.4000|The character's emotional state is surprised, curious.|

## 8. MER2023 / sample_00002066 — 赢家零/错，其他权重经常命中/对

- 参考：angry；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：0.2000→0.0000；50权重零/错13次、满/对18次。
- 模型字幕：This wine, you don't drink it, watermelon juice, you don't drink that either, what do you want to do then?
- 中文：这酒，酒不喝，西瓜汁，西瓜汁不喝，你要干什么呀？
- 起点回答：The character's emotional state is anxious, irritable, overwhelmed.
- 赢家回答：The character's emotional state is anxiety, gloom, impatience, dissatisfaction, disappointment.
- 起点抽取：[anxious, irritable, overwhelmed]
- 赢家抽取：[anxiety, gloom, impatience, dissatisfaction, disappointment]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_RHETORICAL_QUESTION, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_HEAD_LOWERED
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9378854746775789}, {"state": "AEX_EXPECTED", "relative_support": 0.06211452532242119}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8781393936453331}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.06614503731574241}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9874738175345071}, {"state": "ACT_CERTAIN", "relative_support": 0.012526182465492815}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00002066.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is anxiety, frustration, anger, dissatisfaction.|
|long_graph_dataset_best|1.0000|The character's emotional state is anxious, angry, frustrated.|
|base35_A|0.4000|The character's emotional state is anxiety, frustration.|
|base35_B|0.8000|Emotional state: discontent, confusion, frustration, resignation.|
|base35_C|0.4000|The character's emotional state is anxiety, frustration.|
|base35_D|0.8000|Emotional state: discontent, confusion, frustration, resignation.|
|base35_E|0.4000|The character's emotional state is anxiety, frustration.|
|base35_F|0.4000|The character's emotional state is anxiety, frustration.|
|graph40_A|0.0000|The character's emotional state is anxiety, tension, overwhelmed, stress, dissatisfaction, gloominess.|
|graph40_B|0.0000|The character's emotional state is anxiety, tension, overwhelmed, stress, dissatisfaction, gloominess.|
|graph40_C|0.0000|The character's emotional state is anxiety, tension, overwhelmed, stress, dissatisfaction, gloom.|
|graph40_D|0.0000|The character's emotional state is anxiety, tension, overwhelmed, stress, dissatisfaction, gloominess.|
|graph40_E|0.0000|The character's emotional state is anxiety, tension, overwhelmed, stress, dissatisfaction, gloom.|
|graph40_F|0.0000|The character's emotional state is anxiety, tension, overwhelmed, stress, dissatisfaction, gloominess.|
|base35_G|0.4000|The character's emotional state is anxiety, frustration.|
|graph40_G|0.0000|The character's emotional state is anxiety, tension, overwhelmed, stress, dissatisfaction, gloominess.|

## 9. MER2023 / sample_00004046 — 赢家零/错，其他权重经常命中/对

- 参考：worried；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：1.0000→0.0000；50权重零/错18次、满/对30次。
- 模型字幕：Then I won't leave, you have to let Peng Jiahe know.
- 中文：那我不走了你得让彭佳禾知道啊
- 起点回答：The character's emotional state is tense, anxious.
- 赢家回答：The character's emotional state is determined, firm, angry.
- 起点抽取：[tense, anxious]
- 赢家抽取：[firm, angry]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_EXCLAMATION_INTERJECTION, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_HEAD_LOWERED
- 图候选：depressed, despair, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9869972526526845}, {"state": "AGR_RELEVANT", "relative_support": 0.013002747347315616}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7351326042611398}, {"state": "AGC_MIXED", "relative_support": 0.14680574427378565}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7090733207845852}, {"state": "AEX_UNEXPECTED", "relative_support": 0.2909266792154148}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.528385230305901}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.38903808422481917}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.5432454183120133}, {"state": "ACT_CERTAIN", "relative_support": 0.45675458168798666}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8366844220005404}, {"state": "ACP_HIGH", "relative_support": 0.16331557799945948}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00004046.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is firm, resolute, anxious, tense.|
|long_graph_dataset_best|1.0000|The character's emotional state is determined, firm, tense, anxious.|
|base35_A|1.0000|The character's emotional state is tense, anxious, determined.|
|base35_B|1.0000|The character's emotional state is firm, resolute, tense, anxious, emotionally numb, emotionally detached.|
|base35_C|1.0000|The character's emotional state is tense, anxious, determined.|
|base35_D|0.0000|The character might be expressing a firm stance or dissatisfaction in response to some demand or suggestion. Considering the visual clues, such as the person's's frown, squinted eyes, and lowered mouth corners, along with the audio cues like the individual's slow pace, monotone voice, and low pitch, we can infer that this sentence might convey a sense of dissatisfaction, firmness, or anger.|
|base35_E|1.0000|The character's emotional state is tense, anxious, determined.|
|base35_F|1.0000|The character's emotional state is firm, resolute, tense, anxious.|
|graph40_A|0.0000|The character's emotional state is firm, resolute, dissatisfaction, unwillingness.|
|graph40_B|0.0000|The character's emotional state is firm, determined, confident.|
|graph40_C|0.0000|The character's emotional state is firm, resolute, dissatisfaction, unwillingness.|
|graph40_D|0.0000|The character's emotional state is firm, resolute, dissatisfaction, disagreement, firm stance, demand, expectation.|
|graph40_E|1.0000|The character's emotional state is assertive, persistent, tense, anxious.|
|graph40_F|1.0000|The character's emotional state is assertive, persistent, tense, anxious.|
|base35_G|0.6000|The character's emotional state is firm, unwilling, stress, frustration.|
|graph40_G|1.0000|The character's emotional state is assertive, persistent, tense, anxious.|

## 10. MER2023 / sample_00004295 — 赢家满/对，其他权重经常不满/错

- 参考：angry；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错7次、满/对11次。
- 模型字幕：However, when it comes to matters of the heart, I must be the one to decide. Let's put an end to this topic and not discuss it anymore.
- 中文：但是感情的事情，必须是由我自己来做主。这件事情到此为止不再说了。
- 起点回答：The character's emotional state is anger, frustration, determination.
- 赢家回答：The character's emotional state is firm, determined, frustrated, annoyed, anxious, stressed, sorrowful, dejected.
- 起点抽取：[anger, frustration, determination]
- 赢家抽取：[firm, determined, frustrated, annoyed, anxious, stressed, sorrowful, dejected]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_FALLING, AUD_VOICE_TENSE, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：hopeful, joy, disappointed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.986936445066079}, {"state": "AGR_RELEVANT", "relative_support": 0.013063554933920982}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_MIXED", "relative_support": 0.39328159139676444}, {"state": "AGC_CONGRUENT", "relative_support": 0.3444410025113686}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5922633651988982}, {"state": "AEX_UNEXPECTED", "relative_support": 0.40773663480110167}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5961126108223097}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.2947450573434419}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7485447582624231}, {"state": "ACT_UNCERTAIN", "relative_support": 0.251455241737577}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.6512645179026303}, {"state": "ACP_LOW", "relative_support": 0.3487354820973696}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00004295.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is firm, resolute, anxious, angry, pressured, confused.|
|long_graph_dataset_best|1.0000|The character's emotional state is anger, determination, dissatisfaction.|
|base35_A|1.0000|The character's emotional state is resolute, angry.|
|base35_B|0.4000|The character's emotional state is dissatisfaction, firmness, tension, distress.|
|base35_C|0.4000|The character's emotional state is dissatisfaction, frustration, tension, anxiety.|
|base35_D|0.4000|The character's emotional state is dissatisfaction, firmness, tension, distress.|
|base35_E|0.4000|The character's emotional state is dissatisfaction, frustration, tension, anxiety.|
|base35_F|0.4000|The character's emotional state is dissatisfaction, frustration, firmness, determination.|
|graph40_A|0.4000|The character's emotional state is determination, firmness, frustration, overwhelm.|
|graph40_B|0.4000|The character's emotional state is determination, firmness, frustration, overwhelm.|
|graph40_C|0.4000|The character's emotional state is determination, firmness, frustration, overwhelm.|
|graph40_D|0.4000|The character's emotional state is determination, firmness, frustration, overwhelm.|
|graph40_E|0.4000|The character's emotional state is determination, firmness, frustration, overwhelm.|
|graph40_F|0.4000|The character's emotional state is determination, firmness, frustration, overwhelm.|
|base35_G|0.4000|The character's emotional state is dissatisfaction, frustration, firmness, determination.|
|graph40_G|0.4000|The character's emotional state is determination, firmness, frustration, overwhelm.|

## 11. MER2023 / sample_00004886 — 赢家满/对，其他权重经常不满/错

- 参考：sad；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错37次、满/对13次。
- 模型字幕：The house of my brother was bought by my parents. They are worried that my sister-in-law might cause a divorce and divide the property.
- 中文：我哥的房子是我爸妈花钱买的，他们担心我嫂子会闹离婚分房子
- 起点回答：The character's emotional state is concern, sadness.
- 赢家回答：The character's emotional state is concerned, anxious, worried, uneasy, sorrowful, contemplative.
- 起点抽取：[concern, sadness]
- 赢家抽取：[concerned, anxious, worried, uneasy, sorrowful, contemplative]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_LOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN, VIS_TEARING_PRESENT, VIS_HEAD_LOWERED
- 图候选：depressed, despair, grief（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7927887684993652}, {"state": "AGC_MIXED", "relative_support": 0.1437010489696329}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8268954649311979}, {"state": "AEX_UNEXPECTED", "relative_support": 0.17310453506880213}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4460662498737375}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.35421551544727403}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6212032124498224}, {"state": "ACT_UNCERTAIN", "relative_support": 0.3787967875501777}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9941351684573765}, {"state": "ACP_HIGH", "relative_support": 0.005864831542623499}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00004886.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is anxious, fearful, concerned.|
|long_graph_dataset_best|1.0000|The character's emotional state is worry, anxiety, sadness.|
|base35_A|1.0000|The character's emotional state is concerned, anxious, worried, sad, distressed.|
|base35_B|1.0000|The character's emotional state is concerned, anxious, worried, sad, depressed.|
|base35_C|0.2000|The character's emotional state is concerned, anxious, worried, helpless, lack of coping ability.|
|base35_D|1.0000|The character's emotional state is sad, fearful, anxious.|
|base35_E|1.0000|The character's emotional state is sad, fearful, anxious.|
|base35_F|1.0000|The character's emotional state is sad, fearful, anxious.|
|graph40_A|0.0000|The character's emotional state is concerned, anxious, worried, unsettled.|
|graph40_B|0.0000|The character's emotional state is concerned, anxious, worried, unsettled.|
|graph40_C|0.0000|The character's emotional state is concerned, anxious, worried, unsettled.|
|graph40_D|0.0000|The character's emotional state is concerned, anxious, worried, unsettled.|
|graph40_E|0.0000|The character's emotional state is concerned, anxious, worried, unsettled.|
|graph40_F|0.0000|The character's emotional state is concerned, anxious, worried, unsettled.|
|base35_G|1.0000|The character's emotional state is concerned, anxious, worried, sad, distressed.|
|graph40_G|0.0000|The character's emotional state is concerned, anxious, worried, unsettled.|

## 12. MER2023 / sample_00002226 — 赢家满/对，其他权重经常不满/错

- 参考：happy；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：0.0000→1.0000；50权重零/错21次、满/对6次。
- 模型字幕：They had even invited Zhou Bo before, but he couldn't adjust his schedule.
- 中文：他们之前还邀请周波呢，结果他档期调不开。
- 起点回答：The character's emotional state is neutral, casual, indifferent.
- 赢家回答：The character's emotional state is playful, satisfied, happy, frustrated, irritated.
- 起点抽取：[neutral, casual, indifferent]
- 赢家抽取：[playful, satisfied, happy, frustrated, irritated]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：disappointed, joy, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9853639849868271}, {"state": "AGR_RELEVANT", "relative_support": 0.014636015013172809}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.41656668542782155}, {"state": "AGC_INCONGRUENT", "relative_support": 0.38382726236872633}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7804593828009764}, {"state": "AEX_EXPECTED", "relative_support": 0.21954061719902362}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.46520103496967397}, {"state": "AAG_SELF", "relative_support": 0.30034696824871987}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.621663298966087}, {"state": "ACT_CERTAIN", "relative_support": 0.3783367010339129}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5502162277717505}, {"state": "ACP_HIGH", "relative_support": 0.4497837722282495}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00002226.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.6000|The character's emotional state is calm, contentment.|
|long_graph_dataset_best|1.0000|The character's emotional state is happiness, satisfaction, calmness.|
|base35_A|0.0000|The character's emotional state is disappointed, frustrated.|
|base35_B|0.0000|The character's emotional state is disappointed, frustrated.|
|base35_C|0.0000|The character's emotional state is disappointed, frustrated.|
|base35_D|0.0000|The character's emotional state is disappointed, frustrated.|
|base35_E|0.0000|The character's emotional state is disappointed, frustrated.|
|base35_F|0.0000|The character's emotional state is disappointed, frustrated.|
|graph40_A|0.0000|The character's emotional state is disappointed, frustrated.|
|graph40_B|0.0000|The character's emotional state is disappointed, frustrated.|
|graph40_C|0.0000|The character's emotional state is disappointed, frustrated.|
|graph40_D|0.0000|The character's emotional state is disappointed, frustrated.|
|graph40_E|0.0000|The character's emotional state is disappointed, frustrated.|
|graph40_F|0.0000|The character's emotional state is disappointed, frustrated.|
|base35_G|0.0000|The character's emotional state is disappointed, frustrated.|
|graph40_G|0.0000|The character's emotional state is disappointed, frustrated.|

## 13. MER2023 / sample_00003174 — 相对自身起点改善

- 参考：happy；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：0.8000→1.0000；50权重零/错0次、满/对40次。
- 模型字幕：Also, speaking the same language, what do you guys think of our family's Zhao Chong?
- 中文：还有共同语言，你们觉得我们家赵冲怎么样？
- 起点回答：The character's emotional state is curious, anticipatory, positive.
- 赢家回答：The character's emotional state is joyful, enthusiastic, positive.
- 起点抽取：[curious, anticipatory, positive]
- 赢家抽取：[joyful, enthusiastic, positive]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_LAUGHTER_PRESENT, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8991890847732432}, {"state": "AGC_INCONGRUENT", "relative_support": 0.10081091522675678}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7930511724986955}, {"state": "AEX_EXPECTED", "relative_support": 0.20694882750130453}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6012196880355631}, {"state": "AAG_SELF", "relative_support": 0.29599827121230493}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8586887885087303}, {"state": "ACT_CERTAIN", "relative_support": 0.14131121149126968}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8177264639560639}, {"state": "ACP_LOW", "relative_support": 0.18227353604393612}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00003174.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.8000|The character's emotional state is excited, enthusiastic, positive.|
|long_graph_dataset_best|1.0000|The character's emotional state is positive, satisfied, happy.|
|base35_A|1.0000|The character's emotional state is satisfaction, happiness, excitement, passion, enthusiasm.|
|base35_B|0.8000|The character's emotional state is excited, enthusiastic, positive.|
|base35_C|0.8000|The character's emotional state is excited, enthusiastic, positive.|
|base35_D|0.8000|The character's emotional state is excited, enthusiastic, positive.|
|base35_E|0.8000|The character's emotional state is excited, enthusiastic, positive.|
|base35_F|0.8000|The character's emotional state is excited, enthusiastic, positive.|
|graph40_A|1.0000|The character's emotional state is satisfaction, happiness, excitement, enthusiasm, confidence, assurance.|
|graph40_B|1.0000|The character's emotional state is satisfaction, happiness, excitement, enthusiasm, confidence.|
|graph40_C|1.0000|The character's emotional state is confident, enthusiastic, curious, interested, happy.|
|graph40_D|1.0000|The character's emotional state is satisfaction, happiness, excitement, enthusiasm, confidence.|
|graph40_E|1.0000|The character's emotional state is confident, enthusiastic, curious, interested, happy.|
|graph40_F|1.0000|The character's emotional state is confident, enthusiastic, curious, interested, friendly.|
|base35_G|0.8000|The character's emotional state is excited, enthusiastic, positive.|
|graph40_G|1.0000|The character's emotional state is confident, enthusiastic, curious, interested, friendly.|

## 14. MER2023 / sample_00004705 — 相对自身起点改善

- 参考：angry；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：0.4000→1.0000；50权重零/错15次、满/对29次。
- 模型字幕：I'm at work right now. Oh no, what big thing has happened again?
- 中文：我这上班呢。哎哟又出什么大事啦？
- 起点回答：The character's emotional state is anxious, frustrated, stressed.
- 赢家回答：The character's emotional state is sadness, anger, frustration, anxiety, pressure.
- 起点抽取：[anxious, frustrated, stressed]
- 赢家抽取：[sadness, anger, frustration, anxiety, pressure]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_VOICE_TENSE, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN
- 图候选：anger, disappointed, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9749528409832852}, {"state": "AEX_EXPECTED", "relative_support": 0.025047159016714875}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.9347622375574168}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.0652377624425831}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7873672531099174}, {"state": "ACT_CERTAIN", "relative_support": 0.2126327468900826}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00004705.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is sadness, distress, anger.|
|long_graph_dataset_best|0.4000|The character's emotional state is anxious, troubled, work-related issues, big things, distress, pressure.|
|base35_A|0.0000|The character's emotional state is stressed, anxious.|
|base35_B|0.4000|The character's emotional state is stressed, anxious, frustrated.|
|base35_C|0.0000|The character's emotional state is stressed, anxious.|
|base35_D|0.0000|The character's emotional state is stressed, anxious.|
|base35_E|0.0000|The character's emotional state is stressed, anxious.|
|base35_F|0.0000|The character's emotional state is stressed, anxious.|
|graph40_A|1.0000|The character's emotional state is sadness, anger, frustration, stress, anxiety.|
|graph40_B|1.0000|The character's emotional state is sadness, anger, frustration, stress, anxiety.|
|graph40_C|1.0000|The character's emotional state is sadness, anger, frustration, stress, anxiety.|
|graph40_D|1.0000|The character's emotional state is sadness, anger, frustration, stress, anxiety.|
|graph40_E|1.0000|The character's emotional state is sadness, anger, frustration, stress, anxiety.|
|graph40_F|1.0000|The character's emotional state is sadness, anger, frustration, anxiety, pressure.|
|base35_G|0.0000|The character's emotional state is stressed, anxious.|
|graph40_G|1.0000|The character's emotional state is sadness, anger, frustration, stress, anxiety.|

## 15. MER2023 / sample_00000532 — 相对自身起点改善

- 参考：surprise；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：0.0000→0.2500；50权重零/错7次、满/对25次。
- 模型字幕：Really? You still keep it now?
- 中文：不会吧？你现在还留着呢？
- 起点回答：The character's emotional state is agreement, satisfaction, positive mood.
- 赢家回答：The character's emotional state is happy, satisfied, excited.
- 起点抽取：[agreement, satisfaction, positive mood]
- 赢家抽取：[happy, satisfied, excited]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, TXT_RHETORICAL_QUESTION, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT, VIS_HEAD_LOWERED
- 图候选：joy, hopeful, delightful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6151594423967969}, {"state": "AGC_INCONGRUENT", "relative_support": 0.2887508874651544}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5012385016035587}, {"state": "AEX_UNEXPECTED", "relative_support": 0.4987614983964414}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5209161660816539}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.26950720667436995}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7376420115821761}, {"state": "ACT_CERTAIN", "relative_support": 0.262357988417824}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5063344143741879}, {"state": "ACP_HIGH", "relative_support": 0.49366558562581214}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00000532.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is surprised, excited.|
|long_graph_dataset_best|0.5000|The character's emotional state is excited, unsure.|
|base35_A|0.0000|The character's emotional state is happy, satisfied, content.|
|base35_B|1.0000|The character's emotional state is surprised, curious, engaged.|
|base35_C|0.5000|The emotional state is uncertain, hesitant, curious, excited.|
|base35_D|1.0000|The character's emotional state is surprised, curious, engaged.|
|base35_E|0.5000|The emotional state is uncertain, hesitant, curious, excited.|
|base35_F|1.0000|The character's emotional state is surprised, curious, engaged.|
|graph40_A|0.0000|The character's emotional state is happy, satisfied, anticipatory.|
|graph40_B|0.2500|The character's emotional state is happy, satisfied, excited.|
|graph40_C|0.2500|The character's emotional state is happy, satisfied, excited.|
|graph40_D|0.2500|The character's emotional state is happy, satisfied, excited.|
|graph40_E|0.2500|The character's emotional state is happy, satisfied, excited.|
|graph40_F|0.2500|The character's emotional state is happy, satisfied, excited.|
|base35_G|1.0000|The character's emotional state is surprised, curious, engaged.|
|graph40_G|0.2500|The character's emotional state is happy, satisfied, excited.|

## 16. MER2023 / sample_00006663 — 相对自身起点恶化

- 参考：worried；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：1.0000→0.4000；50权重零/错1次、满/对12次。
- 模型字幕：Why do I feel so complicated? But even when I look at myself like this, I still can't understand.
- 中文：我怎么感觉好复杂，可是我就这样看我也，我也看不明白啊。
- 起点回答：The character's emotional state is confused, anxious, contemplative, frustrated.
- 赢家回答：The character's emotional state is sadness, confusion, frustration, perplexity, inability to understand.
- 起点抽取：[confused, anxious, contemplative, frustrated]
- 赢家抽取：[sadness, confusion, frustration, perplexity]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_LIPS_PRESSED, VIS_HEAD_LOWERED
- 图候选：disappointed, depressed, ashamed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.613502825330445}, {"state": "AGC_MIXED", "relative_support": 0.3479065190272982}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6022414074183217}, {"state": "AEX_UNEXPECTED", "relative_support": 0.39775859258167834}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.46931790293905884}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3554681853576795}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.5105819685214416}, {"state": "ACT_CERTAIN", "relative_support": 0.48941803147855856}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9862597661347614}, {"state": "ACP_HIGH", "relative_support": 0.013740233865238498}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00006663.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is confused, anxious, uncertain.|
|long_graph_dataset_best|0.6000|The character's emotional state is confused, perplexed, uncertain.|
|base35_A|0.6000|The character's emotional state is confused, distressed, puzzled, lack of understanding.|
|base35_B|0.6000|Observed emotional state: confused, misunderstood, helpless, emotional stability, calmness.|
|base35_C|0.4000|The character's emotional state is sadness, contemplation, emotional numbness, confusion.|
|base35_D|1.0000|The character's emotional state is sadness, anxiety, confusion.|
|base35_E|0.6000|The character's emotional state is sadness, confusion, uncertainty.|
|base35_F|0.6000|The character's emotional state is sadness, confusion, uncertainty.|
|graph40_A|0.4000|The character's emotional state is sadness, contemplation, confusion, perplexity.|
|graph40_B|0.4000|The character's emotional state is sadness, contemplation, emotional complexity, confusion.|
|graph40_C|0.0000|The character's emotional state is sadness, contemplation, emotional turmoil.|
|graph40_D|0.4000|The character's emotional state is sadness, contemplation, confusion, perplexity.|
|graph40_E|0.4000|The character's emotional state is sadness, contemplation, confusion, perplexity.|
|graph40_F|0.4000|The character's emotional state is sadness, contemplation, confusion, perplexity.|
|base35_G|0.0000|The character's emotional state is sadness, contemplation, emotional distance.|
|graph40_G|0.0000|The character's emotional state is sadness, contemplation, emotional turmoil.|

## 17. MER2023 / sample_00005600 — 相对自身起点恶化

- 参考：happy；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：1.0000→0.6000；50权重零/错0次、满/对6次。
- 模型字幕：Teacher Sun is my idol.
- 中文：孙老师就是我的偶像。
- 起点回答：The character's emotional state is admiration, respect, happiness, contentment.
- 赢家回答：The character's emotional state is admiration, respect, contentment.
- 起点抽取：[admiration, respect, happiness, contentment]
- 赢家抽取：[admiration, respect, contentment]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8506248137308323}, {"state": "AGC_MIXED", "relative_support": 0.13629986018673074}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6029941604330135}, {"state": "AEX_UNEXPECTED", "relative_support": 0.39700583956698665}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4909429766630475}, {"state": "AAG_OTHER", "relative_support": 0.36141186363859923}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6056738741723252}, {"state": "ACT_CERTAIN", "relative_support": 0.39432612582767473}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.9377131646962636}, {"state": "ACP_LOW", "relative_support": 0.06228683530373629}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00005600.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.6000|The character's emotional state is admiration, respect, affection, positive mood, warmth, friendliness.|
|long_graph_dataset_best|1.0000|The character's emotional state is admiration, respect, happiness, positivity.|
|base35_A|0.6000|The character's emotional state is admiration, respect, positivity.|
|base35_B|0.8000|The emotional state is admiration, respect, excitement, positivity.|
|base35_C|0.8000|The character's emotional state is admiration, excitement, positivity.|
|base35_D|0.8000|The emotional state is admiration, respect, excitement, positivity.|
|base35_E|0.8000|The character's emotional state is admiration, excitement, positivity.|
|base35_F|0.8000|The character's emotional state is admiration, excitement, positivity.|
|graph40_A|0.6000|The character's emotional state is admiration, respect, positivity.|
|graph40_B|0.6000|The character's emotional state is admiration, respect, positivity.|
|graph40_C|0.6000|The character's emotional state is admiration, respect, positivity.|
|graph40_D|0.6000|The character's emotional state is admiration, respect, positivity.|
|graph40_E|0.6000|The character's emotional state is admiration, respect, positivity.|
|graph40_F|0.6000|The character's emotional state is admiration, respect, positivity.|
|base35_G|0.8000|The character's emotional state is admiration, excitement, positivity.|
|graph40_G|0.6000|The character's emotional state is admiration, respect, positivity.|

## 18. MER2023 / sample_00001649 — 相对自身起点恶化

- 参考：sad；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：0.2000→0.0000；50权重零/错43次、满/对3次。
- 模型字幕：
- 中文：
- 起点回答：The character's emotional state is anxious, tense, serious, engaged, stressed, anxious.
- 赢家回答：The character's emotional state is fear, anxiety, tension, stress.
- 起点抽取：[anxious, tense, serious, engaged, stressed]
- 赢家抽取：[fear, anxiety, tension, stress]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_RISING, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_HEAD_LOWERED
- 图候选：depressed, despair, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7934521608170604}, {"state": "AGC_MIXED", "relative_support": 0.1315503102896922}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5834161378162291}, {"state": "AEX_UNEXPECTED", "relative_support": 0.41658386218377086}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.43909254218143934}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3869692025252817}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.879983976892687}, {"state": "ACT_CERTAIN", "relative_support": 0.12001602310731302}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00001649.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is anxious, excited, nervous, confident, determined.|
|long_graph_dataset_best|1.0000|The character's emotional state is sorrow, melancholy.|
|base35_A|0.0000|The character's emotional state is fear, anxiety, tension, emotional detachment.|
|base35_B|1.0000|The character's emotional state is anxiety, sadness.|
|base35_C|1.0000|The emotional state of the character can be inferred from the description of the serious expression, focused posture, and the room's calm atmosphere in the video clues. According to the audio clues, the individual's slow and cautious pace, low pitch with less pitch variation, and intonation suggesting uncertainty or hesitation, it can be inferred that the character may be experiencing a heavy, melancholic, or contemplative emotional state. The slow-paced background music also supports this inference. Overall, the character's emotional state might be a blend of heavy, melancholic, contemplative, and serious emotions.|
|base35_D|1.0000|The character's emotional state is anxiety, sadness.|
|base35_E|1.0000|The emotional state of the character can be inferred from the description of the serious expression, focused posture, and the room's calm atmosphere in the video clues. According to the audio clues, the individual's slow and cautious pace, low pitch with less pitch variation, and intonation suggesting uncertainty or hesitation, it can be inferred that the character may be experiencing a heavy, melancholic, or contemplative emotional state. The slow-paced background music also supports this inference. Overall, the character's emotional state might be a blend of heavy, melancholic, contemplative, and serious emotions.|
|base35_F|1.0000|The emotional state of the character can be inferred from the description of the serious expression, focused posture, and the way the hands are positioned on the table. Based on the audio clues, such as the slow and deliberate pace of speech with a monotonous tone, it can be deduced that this person might be experiencing a heavy, sorrowful, or thoughtful emotional state. Their tone suggests they may feel overwhelmed or under immense pressure. Consequently, the caption content mentioning "the end of the world" could be a way for this person to express themselves negatively or pessimistically about their current situation. This alignss with the emotional state described in both the video and audio clues.|
|graph40_A|0.0000|The character's emotional state is fear, anxiety, tension, stress.|
|graph40_B|0.2000|The character's emotional state is fear, anxiety, tension, overwhelm, pressure.|
|graph40_C|0.2000|The character's emotional state is fear, anxiety, tension, overwhelm, pressure.|
|graph40_D|0.2000|The character's emotional state is fear, anxiety, tension, overwhelm, pressure.|
|graph40_E|0.2000|The character's emotional state is fear, anxiety, tension, overwhelm, pressure.|
|graph40_F|0.2000|The character's emotional state is fear, anxiety, tension, overwhelm, pressure.|
|base35_G|1.0000|The emotional state of the character can be inferred from the description of the serious expression, focused posture, and the way the hands are positioned on the table. Based on the audio clues, such as the slow and deliberate pace of speech with a monotonous tone, it can be deduced that this person might be experiencing a heavy, sorrowful, or thoughtful emotional state. Their tone suggests they may feel overwhelmed or under immense pressure. Consequently, the caption content mentioning "the end of the world" could be a way for this person to express themselves negatively or pessimistically about their current situation. This alignss with the emotional state described in both the video and audio clues.|
|graph40_G|0.2000|The character's emotional state is fear, anxiety, tension, overwhelm, pressure.|

## 19. MER2023 / sample_00005263 — neutral参考，HIT不计分

- 参考：neutral；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：未计分→未计分；50权重零/错None次、满/对None次。
- 模型字幕：I want my sister to finish high school properly and get into a good university.
- 中文：我想让我妹好好读完高中，好好考上大学。
- 起点回答：The character's emotional state is hope, longing, concern, expectation, pressure.
- 赢家回答：The character's emotional state is concern, hope, worry, anxiety.
- 起点抽取：[hope, longing, concern, expectation, pressure]
- 赢家抽取：[concern, hope, worry, anxiety]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：
- 图候选：（仅实际level3展示）。
- Appraisal：{}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00005263.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|未计分|The character's emotional state is anticipation, concern, hope, expectation, worry, support.|
|long_graph_dataset_best|未计分|The character's emotional state is anxiety, pressure, concern, expectation.|
|base35_A|未计分|The character's emotional state is expectation, worry, hope, concern.|
|base35_B|未计分|The emotional state is concerned, protective, caring.|
|base35_C|未计分|The character's emotional state is expectation, worry, hope, disappointment.|
|base35_D|未计分|The emotional state is concerned, protective, caring.|
|base35_E|未计分|The character's emotional state is expectation, worry, hope, disappointment.|
|base35_F|未计分|The character's emotional state is expectation, worry, hope, disappointment.|
|graph40_A|未计分|The character's emotional state is expectation, worry, hope, concern.|
|graph40_B|未计分|The character's emotional state is expectation, worry, hope, pressure.|
|graph40_C|未计分|The character's emotional state is expectation, worry, hope, responsibility.|
|graph40_D|未计分|The character's emotional state is expectation, worry, hope, pressure.|
|graph40_E|未计分|The character's emotional state is expectation, worry, hope, responsibility.|
|graph40_F|未计分|The character's emotional state is expectation, worry, hope, responsibility.|
|base35_G|未计分|The character's emotional state is expectation, worry, hope, disappointment.|
|graph40_G|未计分|The character's emotional state is expectation, worry, hope, responsibility.|

## 20. MER2023 / sample_00003992 — neutral参考，HIT不计分

- 参考：neutral；赢家：from_30_epoch_39_MER2023；起点epoch30。
- 质量：未计分→未计分；50权重零/错None次、满/对None次。
- 模型字幕：More importantly, no company would appreciate.
- 中文：更重要的是，没有一个公司会欣赏
- 起点回答：The character's emotional state is disappointed, angry, frustrated, sad.
- 赢家回答：The character's emotional state is disappointed, angry.
- 起点抽取：[disappointed, angry, frustrated, sad]
- 赢家抽取：[disappointed, angry]
- 实际level：2；原因：['emotion_support_not_separated', 'mixed_text_affect_or_evaluation']。
- Cue：
- 图候选：（仅实际level3展示）。
- Appraisal：{}
- 视频：/ai/sjq/AffectGPT/dataset/mer2023-dataset-process/video/sample_00003992.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|未计分|The character's emotional state is concern, negativity, seriousness, anxiety.|
|long_graph_dataset_best|未计分|The character's emotional state is anxiety, fear, tension, dissatisfaction, concern.|
|base35_A|未计分|The character's emotional state is disappointed, frustrated.|
|base35_B|未计分|The character's emotional state is negative, overwhelmed, under pressure.|
|base35_C|未计分|The character's emotional state is disappointed, frustrated.|
|base35_D|未计分|The character's emotional state is negative, overwhelmed, under pressure.|
|base35_E|未计分|The character's emotional state is disappointed, frustrated.|
|base35_F|未计分|The character's emotional state is negative, dissatisfaction, disapproval.|
|graph40_A|未计分|The character's emotional state is negative, pessimistic, disappointment, frustration.|
|graph40_B|未计分|The character's emotional state is disappointed, frustrated.|
|graph40_C|未计分|The character's emotional state is disappointed, frustrated.|
|graph40_D|未计分|The character's emotional state is disappointed, frustrated.|
|graph40_E|未计分|The character's emotional state is disappointed, frustrated.|
|graph40_F|未计分|The character's emotional state is disappointed, frustrated.|
|base35_G|未计分|The character's emotional state is negative, dissatisfaction, disapproval.|
|graph40_G|未计分|The character's emotional state is disappointed, frustrated.|

## 21. MER2024 / samplenew_00017645 — 50权重持续错误/零命中

- 参考：sad；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：0.2000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：孙玉婷同志。
- 中文：孙玉婷同志。
- 起点回答：The character's emotional state is formal, serious, supportive.
- 赢家回答：The character's emotional state is formal, important, stressed, anxious.
- 起点抽取：[formal, serious, supportive]
- 赢家抽取：[formal, important, stressed, anxious]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_HIGH, AUD_VOICE_TENSE, AUD_VOICE_TREMBLING, AUD_CRYING_SOBBING_PRESENT
- 图候选：despair, depressed, grief（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9192976640308004}, {"state": "AGC_MIXED", "relative_support": 0.08070233596919968}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9574672419170769}, {"state": "AEX_EXPECTED", "relative_support": 0.04253275808292322}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5151737047929015}, {"state": "AAG_SELF", "relative_support": 0.25410873818508783}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6533357125753685}, {"state": "ACT_CERTAIN", "relative_support": 0.3466642874246315}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00017645.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.2000|The character's emotional state is formal, serious, supportive.|
|long_graph_dataset_best|0.0000|The character's emotional state is comfort, support.|

## 22. MER2024 / samplenew_00020306 — 50权重持续错误/零命中

- 参考：angry；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：那么，快，就有了孩子，那就难办了。
- 中文：那么，快，就有了孩子，那就难办了。
- 起点回答：The character's emotional state is tense, anxious.
- 赢家回答：The character's emotional state is anxious, troubled, uneasy.
- 起点抽取：[tense, anxious]
- 赢家抽取：[anxious, troubled, uneasy]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_MOUTH_CORNERS_DOWN
- 图候选：disappointed, ashamed, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8449449077503165}, {"state": "AGC_MIXED", "relative_support": 0.07877235377587344}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.923275498535333}, {"state": "AEX_UNEXPECTED", "relative_support": 0.07672450146466704}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.46648164556166866}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.40819524571142635}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8263529484361276}, {"state": "ACT_UNCERTAIN", "relative_support": 0.17364705156387242}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9902839260143317}, {"state": "ACP_HIGH", "relative_support": 0.009716073985668244}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00020306.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is tense, anxious.|
|long_graph_dataset_best|1.0000|The character's emotional state is anxious, frustrated, sad, angry.|

## 23. MER2024 / sample_00002192 — 50权重持续错误/零命中

- 参考：surprise；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：要你想死啊。
- 中文：要你想死啊。
- 起点回答：The character's emotional state is angry, frustrated.
- 赢家回答：The character's emotional state is anger, frustration.
- 起点抽取：[angry, frustrated]
- 赢家抽取：[anger, frustration]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EXCLAMATION_INTERJECTION, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN
- 图候选：disappointed, anger, depressed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9393010586726329}, {"state": "AGC_CONGRUENT", "relative_support": 0.03451454278424815}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.657507845598751}, {"state": "AEX_EXPECTED", "relative_support": 0.3424921544012489}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.4791518904948088}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.2688525370101699}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9311481768538175}, {"state": "ACT_CERTAIN", "relative_support": 0.06885182314618261}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/sample_00002192.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is angry, frustrated.|
|long_graph_dataset_best|0.0000|The character's emotional state is anger, frustration.|

## 24. MER2024 / samplenew_00034323 — 50权重持续正确/满命中

- 参考：angry；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：你现在无异于把这个罪名送给了他们。
- 中文：你现在无异于把这个罪名送给了他们。
- 起点回答：The character's emotional state is anger, frustration, aggression.
- 赢家回答：The character's emotional state is angry, discontented.
- 起点抽取：[anger, frustration, aggression]
- 赢家抽取：[angry, discontented]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, AUD_VOICE_TENSE, VIS_BROWS_FURROWED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN
- 图候选：anger, disappointed, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9016988948846743}, {"state": "AGC_CONGRUENT", "relative_support": 0.08672552028399674}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7024246410897351}, {"state": "AEX_EXPECTED", "relative_support": 0.29757535891026476}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6699298130102428}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.17678019613936985}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5239084378964589}, {"state": "ACT_UNCERTAIN", "relative_support": 0.47609156210354103}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8621165830632481}, {"state": "ACP_HIGH", "relative_support": 0.13788341693675188}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00034323.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is anger, frustration, aggression.|
|long_graph_dataset_best|1.0000|The character's emotional state is angry, frustrated.|

## 25. MER2024 / samplenew_00029298 — 50权重持续正确/满命中

- 参考：surprise；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：你。你，原来是应龙夜神。
- 中文：你。你，原来是应龙夜神。
- 起点回答：The character's emotional state is surprise, admiration.
- 赢家回答：The character's emotional state is surprised, astonished.
- 起点抽取：[surprise, admiration]
- 赢家抽取：[surprised, astonished]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, trusting, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7741073677579371}, {"state": "AGC_INCONGRUENT", "relative_support": 0.15167625790542952}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.93616526204518}, {"state": "AEX_EXPECTED", "relative_support": 0.06383473795481998}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.3930981630699699}, {"state": "AAG_OTHER", "relative_support": 0.3406552435640271}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8510648880299607}, {"state": "ACT_CERTAIN", "relative_support": 0.14893511197003936}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7202185117385231}, {"state": "ACP_LOW", "relative_support": 0.27978148826147675}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00029298.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is surprise, admiration.|
|long_graph_dataset_best|1.0000|The character's emotional state is surprise, shock, awe, recognition, respect.|

## 26. MER2024 / samplenew_00013077 — 50权重持续正确/满命中

- 参考：worried；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：我：久都没有太消息了。
- 中文：我：久都没有太消息了。
- 起点回答：The character's emotional state is worry, anxiety, depression, dissatisfaction.
- 赢家回答：The character's emotional state is worry, concern, disappointment, frustration, anxiety.
- 起点抽取：[worry, anxiety, depression, dissatisfaction]
- 赢家抽取：[worry, concern, disappointment, frustration, anxiety]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_RAISED
- 图候选：apathetic, helpless, pity（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5007640060276249}, {"state": "AGC_INCONGRUENT", "relative_support": 0.3708150089098964}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8538907933780787}, {"state": "AEX_UNEXPECTED", "relative_support": 0.14610920662192128}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5930515464004964}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.40694845359950366}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7711284941449751}, {"state": "ACT_UNCERTAIN", "relative_support": 0.228871505855025}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5883102357610185}, {"state": "ACP_HIGH", "relative_support": 0.41168976423898157}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00013077.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is worry, anxiety, depression, dissatisfaction.|
|long_graph_dataset_best|1.0000|The character's emotional state is anxiety, concern.|

## 27. MER2024 / samplenew_00035010 — 赢家零/错，其他权重经常命中/对

- 参考：happy；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：1.0000→0.0000；50权重零/错21次、满/对27次。
- 模型字幕：你，这还跟我没完没了的！你。
- 中文：你，这还跟我没完没了的！你。
- 起点回答：The character's emotional state is positive, happy, satisfied, anger, dissatisfaction.
- 赢家回答：The character's emotional state is angry, frustrated.
- 起点抽取：[positive, happy, satisfied, angry, dissatisfied]
- 赢家抽取：[angry, frustrated]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, disappointed, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5296204317979744}, {"state": "AGC_INCONGRUENT", "relative_support": 0.4703795682020255}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7730901244087113}, {"state": "AEX_EXPECTED", "relative_support": 0.2269098755912886}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6130039691917514}, {"state": "AAG_SELF", "relative_support": 0.28542505563998444}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6588348917833888}, {"state": "ACT_CERTAIN", "relative_support": 0.3411651082166111}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5596851442591909}, {"state": "ACP_HIGH", "relative_support": 0.44031485574080903}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00035010.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is positive, happy, satisfied, anger, dissatisfaction.|
|long_graph_dataset_best|1.0000|The character's emotional state is joking, teasing, playful, positive.|

## 28. MER2024 / samplenew_00003862 — 赢家零/错，其他权重经常命中/对

- 参考：sad；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：0.0000→0.0000；50权重零/错20次、满/对29次。
- 模型字幕：咱俩永远都是绑在一块的。
- 中文：咱俩永远都是绑在一块的。
- 起点回答：The character's emotional state is comforting, supportive, intimate, emotionally distressed.
- 赢家回答：The character's emotional state is comfort, support, emotional distress.
- 起点抽取：[comforting, supportive, intimate, emotionally distressed]
- 赢家抽取：[comfort, support, emotional distress]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_MOUTH_CORNERS_DOWN, VIS_LIPS_PRESSED, VIS_HEAD_LOWERED
- 图候选：depressed, despair, ashamed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.6996384642634165}, {"state": "AGC_MIXED", "relative_support": 0.15186760205091335}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9311954845721885}, {"state": "AEX_UNEXPECTED", "relative_support": 0.06880451542781152}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.601672197298544}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.374670281872789}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7756445630876285}, {"state": "ACT_UNCERTAIN", "relative_support": 0.22435543691237142}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9765611240564496}, {"state": "ACP_HIGH", "relative_support": 0.023438875943550385}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00003862.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is comforting, supportive, intimate, emotionally distressed.|
|long_graph_dataset_best|1.0000|The character's emotional state is comfort, support, sadness, distress.|

## 29. MER2024 / samplenew_00013570 — 赢家零/错，其他权重经常命中/对

- 参考：angry；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：1.0000→0.0000；50权重零/错7次、满/对25次。
- 模型字幕：连最简单的水雾术都施不了。
- 中文：连最简单的水雾术都施不了。
- 起点回答：The character's emotional state is disappointment, defeat, anger.
- 赢家回答：The character's emotional state is disappointment, defeat.
- 起点抽取：[disappointment, defeat, anger]
- 赢家抽取：[disappointment, defeat]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN
- 图候选：disappointed, anger, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9914063570343699}, {"state": "AGR_RELEVANT", "relative_support": 0.008593642965630196}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7967639060036824}, {"state": "AGC_CONGRUENT", "relative_support": 0.20323609399631754}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9757455007783865}, {"state": "AEX_EXPECTED", "relative_support": 0.02425449922161346}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.4804777235239712}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3243468515249628}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.594655883980183}, {"state": "ACT_CERTAIN", "relative_support": 0.405344116019817}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.775198884994977}, {"state": "ACP_HIGH", "relative_support": 0.224801115005023}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00013570.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is disappointment, defeat, anger.|
|long_graph_dataset_best|1.0000|The character's emotional state is disappointment, frustration, anger, anxiety, stress.|

## 30. MER2024 / samplenew_00041142 — 赢家满/对，其他权重经常不满/错

- 参考：sad；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：0.0000→1.0000；50权重零/错42次、满/对8次。
- 模型字幕：妈妈会领你打电话的。
- 中文：妈妈会领你打电话的。
- 起点回答：The character's emotional state is anxiety, fear, comfort, reassurance.
- 赢家回答：The character's emotional state is comfort, reassurance, sadness.
- 起点抽取：[anxiety, fear, comfort, reassurance]
- 赢家抽取：[comfort, reassurance, sadness]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_VOICE_TENSE, AUD_VOICE_TREMBLING, AUD_CRYING_SOBBING_PRESENT, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：anger, disappointed, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9800157371008649}, {"state": "AEX_EXPECTED", "relative_support": 0.019984262899135137}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.9217944090061979}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.07820559099380203}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6981759349521093}, {"state": "ACT_CERTAIN", "relative_support": 0.30182406504789067}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00041142.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is anxiety, fear, comfort, reassurance.|
|long_graph_dataset_best|0.0000|The character's emotional state is comfort, promise.|

## 31. MER2024 / sample_00002086 — 赢家满/对，其他权重经常不满/错

- 参考：surprise；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：0.7500→1.0000；50权重零/错12次、满/对1次。
- 模型字幕：那怎么会搭过到一块。
- 中文：那怎么会搭过到一块。
- 起点回答：The character's emotional state is disbelief, confusion, sadness, distress.
- 赢家回答：The character's emotional state is disappointment, confusion, surprise, sorrow.
- 起点抽取：[disbelief, confusion, sadness, distress]
- 赢家抽取：[disappointment, confusion, surprise, sorrow]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_RHETORICAL_QUESTION, AUD_INTONATION_RISING, VIS_EYES_SQUINTED
- 图候选：anxious, care, disappointed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9641051876661798}, {"state": "AEX_EXPECTED", "relative_support": 0.03589481233382023}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8301850711433859}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.16981492885661417}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9762513823591741}, {"state": "ACT_CERTAIN", "relative_support": 0.023748617640825944}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/sample_00002086.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.7500|The character's emotional state is disbelief, confusion, sadness, distress.|
|long_graph_dataset_best|0.7500|The character's emotional state is confused, puzzled, uncertain, sad, frustrated, anxious.|

## 32. MER2024 / sample_00003408 — 赢家满/对，其他权重经常不满/错

- 参考：worried；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：0.0000→1.0000；50权重零/错24次、满/对18次。
- 模型字幕：我马上派人去帮你！好！就这样，程俊在事故现场，他那边在处理伤员，实在忙不过来。
- 中文：我马上派人去帮你！好！就这样，程俊在事故现场，他那边在处理伤员，实在忙不过来。
- 起点回答：The character's emotional state is resolve, action-oriented, explanation, comfort.
- 赢家回答：The character's emotional state is calmness, professionalism, frustration, anxiety.
- 起点抽取：[resolve, action-oriented]
- 赢家抽取：[calmness, professionalism, frustration, anxiety]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN
- 图候选：depressed, disappointed, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9895673671789755}, {"state": "AGR_RELEVANT", "relative_support": 0.010432632821024475}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.41253439567608774}, {"state": "AGC_CONGRUENT", "relative_support": 0.3885517316221313}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.732529392301873}, {"state": "AEX_UNEXPECTED", "relative_support": 0.267470607698127}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4954517002096566}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.41317306888077443}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6703433520849068}, {"state": "ACT_UNCERTAIN", "relative_support": 0.32965664791509314}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7459063296491765}, {"state": "ACP_HIGH", "relative_support": 0.2540936703508235}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/sample_00003408.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is resolve, action-oriented, explanation, comfort.|
|long_graph_dataset_best|1.0000|The character's emotional state is determination, responsibility, excitement, anticipation, concern.|

## 33. MER2024 / samplenew_00004873 — 相对自身起点改善

- 参考：happy；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：0.8000→1.0000；50权重零/错0次、满/对41次。
- 模型字幕：富察氏，是个好孩子，额，娘，很放心。
- 中文：富察氏，是个好孩子，额，娘，很放心。
- 起点回答：The character's emotional state is pride, satisfaction, positive.
- 赢家回答：The character's emotional state is comfort, encouragement, appreciation, trust, satisfaction.
- 起点抽取：[pride, satisfaction, positive]
- 赢家抽取：[comfort, encouragement, appreciation, trust, satisfaction]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_POSITIVE, TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.850032265853113}, {"state": "AGC_MIXED", "relative_support": 0.13471999903129295}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9098430412809048}, {"state": "AEX_UNEXPECTED", "relative_support": 0.09015695871909521}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6559569383396687}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.33377992500300874}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8852276975848591}, {"state": "ACT_UNCERTAIN", "relative_support": 0.1147723024151409}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8874313339685052}, {"state": "ACP_LOW", "relative_support": 0.11256866603149485}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00004873.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.8000|The character's emotional state is pride, satisfaction, positive.|
|long_graph_dataset_best|1.0000|The character's emotional state is positive, praise, reassurance, confidence.|

## 34. MER2024 / samplenew_00016438 — 相对自身起点改善

- 参考：surprise；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：0.5000→1.0000；50权重零/错8次、满/对19次。
- 模型字幕：什么。
- 中文：什么。
- 起点回答：The character's emotional state is confused, dissatisfied, skeptical.
- 赢家回答：The character's emotional state is dissatisfaction, confusion, surprise.
- 起点抽取：[confused, dissatisfied, skeptical]
- 赢家抽取：[dissatisfaction, confusion, surprise]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN
- 图候选：anger, disappointed, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.861829120012056}, {"state": "AGC_CONGRUENT", "relative_support": 0.13817087998794397}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 1.0}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7859653490194021}, {"state": "ACP_HIGH", "relative_support": 0.21403465098059793}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00016438.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.5000|The character's emotional state is confused, dissatisfied, skeptical.|
|long_graph_dataset_best|0.5000|The character's emotional state is confused, misunderstanding, dissatisfaction.|

## 35. MER2024 / sample_00003208 — 相对自身起点改善

- 参考：worried；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：0.0000→1.0000；50权重零/错23次、满/对16次。
- 模型字幕：乔。阳。
- 中文：乔。阳。
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is concentration, thought, excitement, anxiety, passion.
- 起点抽取：[]
- 赢家抽取：[concentration, thought, excitement, anxiety, passion]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：anxious, care, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8994721342092569}, {"state": "AGC_INCONGRUENT", "relative_support": 0.10052786579074302}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8359965569873726}, {"state": "AAG_SELF", "relative_support": 0.16400344301262734}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9943964499418079}, {"state": "ACT_CERTAIN", "relative_support": 0.005603550058192102}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/sample_00003208.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is neutral.|
|long_graph_dataset_best|0.2000|The character's emotional state is intense focus, concentration.|

## 36. MER2024 / samplenew_00013216 — 相对自身起点恶化

- 参考：angry；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：1.0000→0.0000；50权重零/错45次、满/对5次。
- 模型字幕：打下龙骨，立即。
- 中文：打下龙骨，立即。
- 起点回答：The character's emotional state is strong, determined, immediate, resolute, anger, frustration.
- 赢家回答：The character's emotional state is determined, immediate, tense, anxious.
- 起点抽取：[anger, frustration]
- 赢家抽取：[determined, tense, anxious]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_INTENSIFIER_PRESENT, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, AUD_VOICE_TENSE, VIS_BROWS_FURROWED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN
- 图候选：anger, disappointed, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8332637476712131}, {"state": "AGC_CONGRUENT", "relative_support": 0.14972956163980825}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7488058920920275}, {"state": "AEX_EXPECTED", "relative_support": 0.2511941079079725}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7316387862647534}, {"state": "AAG_SELF", "relative_support": 0.15617368485207891}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5348544269169331}, {"state": "ACT_UNCERTAIN", "relative_support": 0.4651455730830668}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7606097140503425}, {"state": "ACP_HIGH", "relative_support": 0.23939028594965736}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00013216.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is strong, determined, immediate, resolute, anger, frustration.|
|long_graph_dataset_best|0.0000|The character's emotional state is firm, decisive, positive.|

## 37. MER2024 / samplenew_00003374 — 相对自身起点恶化

- 参考：happy；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：1.0000→0.4000；50权重零/错6次、满/对14次。
- 模型字幕：那，你忙你的吧，我赶紧走了。
- 中文：那，你忙你的吧，我赶紧走了。
- 起点回答：The character's emotional state is happiness, contentment, politeness.
- 赢家回答：The character's emotional state is anxiety, agitation, frustration, impatience, surprise, excitement, enjoyment.
- 起点抽取：[happiness, contentment, politeness]
- 赢家抽取：[anxiety, agitation, frustration, impatience, surprise, excitement, enjoyment]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_INTENSIFIER_PRESENT, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, manic（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.9208985116132752}, {"state": "AGC_INCONGRUENT", "relative_support": 0.07910148838672486}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7718045708057282}, {"state": "AEX_EXPECTED", "relative_support": 0.22819542919427188}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5919572829171537}, {"state": "AAG_SELF", "relative_support": 0.40804271708284645}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7516698943611066}, {"state": "ACT_CERTAIN", "relative_support": 0.24833010563889335}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.9614196064738335}, {"state": "ACP_LOW", "relative_support": 0.03858039352616652}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00003374.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is happiness, contentment, politeness.|
|long_graph_dataset_best|1.0000|The character's emotional state is happy, satisfied, anxious, stressed.|

## 38. MER2024 / samplenew_00011516 — 相对自身起点恶化

- 参考：worried；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：1.0000→0.8000；50权重零/错1次、满/对19次。
- 模型字幕：我们要不要去一趟校府？想要讨个主意。
- 中文：我们要不要去一趟校府？想要讨个主意。
- 起点回答：The character's emotional state is anxiety, nervousness, stress.
- 赢家回答：The character's emotional state is hesitation, uncertainty, fear.
- 起点抽取：[anxiety, nervousness, stress]
- 赢家抽取：[fear, hesitation, uncertainty]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, TXT_DESIRE_NEED, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：hopeful, joy, anxious（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9866843466959958}, {"state": "AGR_RELEVANT", "relative_support": 0.01331565330400417}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6192757384519505}, {"state": "AGC_INCONGRUENT", "relative_support": 0.3807242615480494}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8030893918158242}, {"state": "AEX_EXPECTED", "relative_support": 0.1969106081841758}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5287252399292792}, {"state": "AAG_SELF", "relative_support": 0.4712747600707208}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9943602363234484}, {"state": "ACT_CERTAIN", "relative_support": 0.005639763676551645}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7752221504179946}, {"state": "ACP_LOW", "relative_support": 0.22477784958200553}]}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00011516.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is anxiety, nervousness, stress.|
|long_graph_dataset_best|0.0000|The character's emotional state is neutral.|

## 39. MER2024 / samplenew_00017788 — neutral参考，HIT不计分

- 参考：neutral；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：未计分→未计分；50权重零/错None次、满/对None次。
- 模型字幕：我就不要什么了，再给我来一瓶人头马瓜。
- 中文：我就不要什么了，再给我来一瓶人头马瓜。
- 起点回答：The character's emotional state is relaxed, humorous, positive mood.
- 赢家回答：The character's emotional state is excited, anticipate, positive.
- 起点抽取：[relaxed, humorous, positive mood]
- 赢家抽取：[excited, positive]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：
- 图候选：（仅实际level3展示）。
- Appraisal：{}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00017788.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|未计分|The character's emotional state is relaxed, humorous, positive mood.|
|long_graph_dataset_best|未计分|The character's emotional state is positive, enthusiastic, urgent.|

## 40. MER2024 / samplenew_00040713 — neutral参考，HIT不计分

- 参考：neutral；赢家：from_45_epoch_54_MER2024；起点epoch45。
- 质量：未计分→未计分；50权重零/错None次、满/对None次。
- 模型字幕：那我估计，咱们俩怎么也得在山上待上半个月吧。
- 中文：那我估计，咱们俩怎么也得在山上待上半个月吧。
- 起点回答：The character's emotional state is concerned, uneasy, tense, worried.
- 赢家回答：The character's emotional state is contemplative, concerned, uncertain.
- 起点抽取：[concerned, uneasy, tense, worried]
- 赢家抽取：[contemplative, concerned, uncertain]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：
- 图候选：（仅实际level3展示）。
- Appraisal：{}
- 视频：/ai/sjq/AffectGPT/dataset/mer2024-dataset-process/video/samplenew_00040713.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|未计分|The character's emotional state is concerned, uneasy, tense, worried.|
|long_graph_dataset_best|未计分|The character's emotional state is neutral.|

## 41. MELD / test_dia237_utt6 — 50权重持续错误/零命中

- 参考：anger；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕："You are ideally suited for a career in data processing for a large multinational corporation."
- 中文：你非常适合在一家大型跨国公司从事数据处理的职业。
- 起点回答：The character's emotional state is excited, anxious, positive, affirming.
- 赢家回答：The character's emotional state is encouraged, praising, confident, assured, analytical, evaluative.
- 起点抽取：[excited, anxious, positive, affirming]
- 赢家抽取：[encouraged, praising, confident, assured]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN, VIS_HEAD_LOWERED
- 图候选：appreciated, awe, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5572622374405004}, {"state": "AGC_INCONGRUENT", "relative_support": 0.27618650207634754}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.582131859401012}, {"state": "AEX_UNEXPECTED", "relative_support": 0.41786814059898814}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.511829690622221}, {"state": "AAG_SELF", "relative_support": 0.32944208035024086}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.560430003743124}, {"state": "ACT_UNCERTAIN", "relative_support": 0.4395699962568761}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5682851973104199}, {"state": "ACP_HIGH", "relative_support": 0.43171480268958007}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia237_utt6.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is encouraging, positive, excitement, anxiety.|
|long_graph_dataset_best|0.0000|The character's emotional state is encouraging, affirming, supportive, positive.|

## 42. MELD / test_dia12_utt6 — 50权重持续错误/零命中

- 参考：sadness；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：Two very good points, look I've known you both a long time, and I've never seen either of you one/millionth as happy as you've been since you've got together.
- 中文：两个非常好的观点，看，我认识你们俩很久了，但我从未见过你们中的任何一个/百万分之一像你们在一起后那样快乐。
- 起点回答：The character's emotional state is excited, enthusiastic, positive, surprised, happy, admiration.
- 赢家回答：The character's emotional state is happy, excited, enthusiastic.
- 起点抽取：[excited, enthusiastic, positive, happy, admiration]
- 赢家抽取：[happy, excited, enthusiastic]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_POSITIVE, TXT_EVALUATION_POSITIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, appreciated, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9835898241627768}, {"state": "AGR_RELEVANT", "relative_support": 0.016410175837223217}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7563002380072262}, {"state": "AGC_MIXED", "relative_support": 0.1368650380368617}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5197338325122808}, {"state": "AEX_UNEXPECTED", "relative_support": 0.4802661674877192}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4560654073961694}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3114892671361879}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5420491821429527}, {"state": "ACT_UNCERTAIN", "relative_support": 0.45795081785704733}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.75464459116706}, {"state": "ACP_LOW", "relative_support": 0.24535540883294005}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia12_utt6.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is excitement, enthusiasm, happiness, admiration.|
|long_graph_dataset_best|0.0000|The character's emotional state is positive, praise, excitement, enthusiasm, happiness.|

## 43. MELD / test_dia70_utt9 — 50权重持续错误/零命中

- 参考：disgust；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：What do you think you're gonna do, have sex with her right here    on my couch?
- 中文：你觉得你要做什么，就在我的沙发上和她发生性关系吗？
- 起点回答：The character's emotional state is angry, frustrated.
- 赢家回答：The character's emotional state is anger, dissatisfaction, unhappiness.
- 起点抽取：[angry, frustrated]
- 赢家抽取：[anger, dissatisfaction, unhappiness]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：anger, disappointed, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9936988668584983}, {"state": "AEX_EXPECTED", "relative_support": 0.006301133141501673}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 1.0}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9051791770264204}, {"state": "ACT_CERTAIN", "relative_support": 0.09482082297357963}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia70_utt9.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is angry, frustrated.|
|long_graph_dataset_best|0.0000|The character's emotional state is anger, frustration.|

## 44. MELD / test_dia169_utt21 — 50权重持续正确/满命中

- 参考：surprise；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：Oh my God! I know who the father is
- 中文：哦，我的天！我知道是谁是父亲了。
- 起点回答：The character's emotional state is excited, curious, surprised, amused, positive.
- 赢家回答：The character's emotional state is surprised, happy, excited, anticipatory, nervous.
- 起点抽取：[excited, curious, surprised, amused, positive]
- 赢家抽取：[surprised, happy, excited, anticipatory, nervous]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_HEAD_LOWERED
- 图候选：delightful, acceptance, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_MIXED", "relative_support": 0.37398072579226044}, {"state": "AGC_CONGRUENT", "relative_support": 0.3661230724846698}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8971824101881545}, {"state": "AEX_UNEXPECTED", "relative_support": 0.10281758981184555}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5801863802967117}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3953010254057235}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7293875671156929}, {"state": "ACT_UNCERTAIN", "relative_support": 0.27061243288430725}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9636002706451948}, {"state": "ACP_HIGH", "relative_support": 0.03639972935480524}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia169_utt21.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is surprised, excited.|
|long_graph_dataset_best|1.0000|The character's emotional state is surprise, excitement, admiration.|

## 45. MELD / test_dia158_utt4 — 50权重持续正确/满命中

- 参考：anger；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：Sophie, would you please climb out of my butt. Why hasn't he called, Rachel? Why?
- 中文：Sophie，请你从我的屁股里爬出来。为什么他还没有打电话给我，Rachel？为什么？
- 起点回答：The character's emotional state is angry, frustrated, anxious, irritable, impatient.
- 赢家回答：The character's emotional state is angry, frustrated, unhappy.
- 起点抽取：[angry, frustrated, anxious, irritable, impatient]
- 赢家抽取：[angry, frustrated, unhappy]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_RHETORICAL_QUESTION, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_LAUGHTER_PRESENT, VIS_BROWS_FURROWED, VIS_BROWS_RAISED, VIS_MOUTH_CORNERS_DOWN
- 图候选：anger, disappointed, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9927920958289306}, {"state": "AGR_RELEVANT", "relative_support": 0.007207904171069532}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7247247279269827}, {"state": "AGC_CONGRUENT", "relative_support": 0.2752752720730174}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9099831828502639}, {"state": "AEX_EXPECTED", "relative_support": 0.09001681714973601}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.828571818118632}, {"state": "AAG_SELF", "relative_support": 0.17142818188136805}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.960035116103555}, {"state": "ACT_CERTAIN", "relative_support": 0.039964883896445015}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6797250399877265}, {"state": "ACP_HIGH", "relative_support": 0.3202749600122735}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia158_utt4.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is anger, dissatisfaction.|
|long_graph_dataset_best|1.0000|The character's emotional state is dissatisfaction, anxiety, anger, agitation, frustration.|

## 46. MELD / test_dia216_utt1 — 50权重持续正确/满命中

- 参考：joy；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：I can't believe you're getting married!
- 中文：我简直不敢相信你要结婚了！
- 起点回答：The character's emotional state is envy, admiration, happiness, excitement.
- 赢家回答：The character's emotional state is excitement, joy.
- 起点抽取：[envy, admiration, happiness, excitement]
- 赢家抽取：[excitement, joy]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, disappointed, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5268088008756527}, {"state": "AGC_INCONGRUENT", "relative_support": 0.4731911991243473}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6973065776470017}, {"state": "AEX_EXPECTED", "relative_support": 0.3026934223529984}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5312598197036094}, {"state": "AAG_SELF", "relative_support": 0.36178826039274814}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6299533146532229}, {"state": "ACT_CERTAIN", "relative_support": 0.37004668534677704}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.568649517334847}, {"state": "ACP_HIGH", "relative_support": 0.4313504826651531}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia216_utt1.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.4000|The character's emotional state is surprise, excitement.|
|long_graph_dataset_best|1.0000|The character's emotional state is joy, excitement.|

## 47. MELD / test_dia196_utt4 — 赢家零/错，其他权重经常命中/对

- 参考：anger；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：0.0000→0.0000；50权重零/错20次、满/对28次。
- 模型字幕：I mean, I either keep my wife and lose one of my-my-my best friends or I keep my friend and get divorced the second time before I'm 30!
- 中文：我的意思是，要么我保留我的妻子但失去我最好的朋友之一，要么我保留我的朋友但在30岁之前第二次离婚！
- 起点回答：The character's emotional state is disappointment, despair, helplessness, confusion, fear, anxiety, sadness.
- 赢家回答：The character's emotional state is despair, confusion, fear, anxiety, hopelessness, despondency, disappointment, disillusionment, dissatisfaction, heartache, sorrow.
- 起点抽取：[disappointment, despair, helplessness, confusion, fear, anxiety, sadness]
- 赢家抽取：[despair, confusion, fear, anxiety, hopelessness, despondency, disappointment, disillusionment, dissatisfaction, heartache, sorrow]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_CONTRAST_PRESENT, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, AUD_VOICE_TENSE, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN
- 图候选：anger, disappointed, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.8757092382213434}, {"state": "AGR_RELEVANT", "relative_support": 0.12429076177865662}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7505187372026504}, {"state": "AGC_MIXED", "relative_support": 0.23839969276110784}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8514847977563119}, {"state": "AEX_EXPECTED", "relative_support": 0.14851520224368808}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6179833343413317}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.25585499552727275}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.5491523120542166}, {"state": "ACT_CERTAIN", "relative_support": 0.4508476879457834}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9965773921163528}, {"state": "ACP_HIGH", "relative_support": 0.003422607883647151}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia196_utt4.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.4000|The character's emotional state is confused, anxious, desperate, frustrated.|
|long_graph_dataset_best|1.0000|The character's emotional state is anxiety, confusion, anger.|

## 48. MELD / test_dia204_utt2 — 赢家零/错，其他权重经常命中/对

- 参考：surprise；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：1.0000→0.0000；50权重零/错9次、满/对10次。
- 模型字幕：What?
- 中文：什么？
- 起点回答：The character's emotional state is anxious, tense, sad, surprised, confused, stressed, emotionally aroused.
- 赢家回答：The character's emotional state is frustration, boredom, dissatisfaction, annoyance.
- 起点抽取：[anxious, tense, sad, surprised, confused, stressed, emotionally aroused]
- 赢家抽取：[frustration, boredom, dissatisfaction, annoyance]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：AUD_INTONATION_RISING, VIS_HEAD_LOWERED
- 图候选：bewildered, sceptical, curious（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8699768808559347}, {"state": "AEX_EXPECTED", "relative_support": 0.13002311914406522}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8447324609496707}, {"state": "AAG_SELF", "relative_support": 0.15526753905032936}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia204_utt2.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is neutral.|
|long_graph_dataset_best|0.5000|The character's emotional state is neutral, curiosity, confusion.|

## 49. MELD / test_dia212_utt6 — 赢家零/错，其他权重经常命中/对

- 参考：sadness；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：0.6000→0.0000；50权重零/错8次、满/对6次。
- 模型字幕：On no! No! It's not good-bye, I'm not leaving until you get on that plane.
- 中文：哦不！不！这不是告别，我不会离开，直到你上了飞机。
- 起点回答：The character's emotional state is anxiety, tension, dissatisfaction, distress.
- 赢家回答：The character's emotional state is annoyed, angry.
- 起点抽取：[anxiety, tension, dissatisfaction, distress]
- 赢家抽取：[annoyed, angry]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9213224965016402}, {"state": "AGC_CONGRUENT", "relative_support": 0.07867750349835984}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 1.0}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9882508134379165}, {"state": "ACT_CERTAIN", "relative_support": 0.011749186562083456}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8793562988533339}, {"state": "ACP_HIGH", "relative_support": 0.12064370114666614}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia212_utt6.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.6000|The character's emotional state is excited, distressed, agitated, angry, frustrated.|
|long_graph_dataset_best|1.0000|The character's emotional state is anxiety, frustration, anger, sadness.|

## 50. MELD / test_dia41_utt8 — 赢家满/对，其他权重经常不满/错

- 参考：surprise；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错1次、满/对1次。
- 模型字幕：Oh no!
- 中文：哦不！
- 起点回答：The character's emotional state is surprise, concern, urgency.
- 赢家回答：The character's emotional state is excited, enthusiastic, anxious, tense, surprised, disappointed.
- 起点抽取：[surprise, concern, urgency]
- 赢家抽取：[excited, enthusiastic, anxious, tense, surprised, disappointed]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：care, anger, anxious（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5165721146603751}, {"state": "AGC_CONGRUENT", "relative_support": 0.4834278853396249}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.9032831799747145}, {"state": "AAG_SELF", "relative_support": 0.09671682002528552}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9661889191778401}, {"state": "ACT_CERTAIN", "relative_support": 0.03381108082215991}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.6372314677514439}, {"state": "ACP_LOW", "relative_support": 0.3627685322485561}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia41_utt8.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.2500|The character's emotional state is fear, anxiety, panic.|
|long_graph_dataset_best|1.0000|The character's emotional state is anger, frustration, fear, surprise, tension, unease.|

## 51. MELD / test_dia30_utt3 — 赢家满/对，其他权重经常不满/错

- 参考：joy；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错15次、满/对3次。
- 模型字幕：Oh,  I wish. No, you know he was just trying Ross's Hug and Roll thing.
- 中文：哦，我希望如此。不，你知道他只是在尝试罗斯的拥抱和翻滚。
- 起点回答：The character's emotional state is excited, happy.
- 赢家回答：The character's emotional state is excitement, enthusiasm, joy.
- 起点抽取：[excited, happy]
- 赢家抽取：[excitement, enthusiasm, joy]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_EXCLAMATION_INTERJECTION, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_HEAD_LOWERED
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9872244689161132}, {"state": "AGR_RELEVANT", "relative_support": 0.012775531083886876}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5276227799121049}, {"state": "AGC_CONGRUENT", "relative_support": 0.4295771496038438}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7976283596426246}, {"state": "AEX_EXPECTED", "relative_support": 0.2023716403573754}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.4566496524890526}, {"state": "AAG_SELF", "relative_support": 0.36540494224210357}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9769922536922065}, {"state": "ACT_CERTAIN", "relative_support": 0.02300774630779342}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5084508925507465}, {"state": "ACP_HIGH", "relative_support": 0.4915491074492535}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia30_utt3.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.6000|The character's emotional state is excited, enthusiastic, curious, puzzled.|
|long_graph_dataset_best|0.4000|The character's emotional state is excited, enthusiastic.|

## 52. MELD / test_dia56_utt4 — 赢家满/对，其他权重经常不满/错

- 参考：anger；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错14次、满/对17次。
- 模型字幕：No, I don't see it!
- 中文：不，我没有看到它！
- 起点回答：The character's emotional state is sadness, anger, frustration.
- 赢家回答：The character's emotional state is disappointment, frustration, anger.
- 起点抽取：[sadness, anger, frustration]
- 赢家抽取：[disappointment, frustration, anger]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_VOICE_TENSE, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：anger, disappointed, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9824253707187809}, {"state": "AEX_EXPECTED", "relative_support": 0.01757462928121909}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.9234418394566917}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.07655816054330833}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8010727502227127}, {"state": "ACT_CERTAIN", "relative_support": 0.19892724977728732}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia56_utt4.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is disappointment, anger, sadness, frustration.|
|long_graph_dataset_best|1.0000|The character's emotional state is disappointment, frustration, anger, confusion, uncertainty.|

## 53. MELD / test_dia195_utt0 — 相对自身起点改善

- 参考：fear；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：0.2000→1.0000；50权重零/错16次、满/对14次。
- 模型字幕：Okay look, don't...don't be mad okay?
- 中文：好吧，听着，不要...不要生气，好吗？
- 起点回答：The character's emotional state is concerned, comforting.
- 赢家回答：The character's emotional state is nervousness, anxiety, fear, concern, soothing.
- 起点抽取：[concerned, comforting]
- 赢家抽取：[nervousness, anxiety, fear, concern, soothing]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_NEGATION_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：disappointed, anger, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5804613873795674}, {"state": "AGC_CONGRUENT", "relative_support": 0.41953861262043257}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9096640780006447}, {"state": "AEX_EXPECTED", "relative_support": 0.09033592199935528}], "APP_AGENCY": [], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9729234107206862}, {"state": "ACT_CERTAIN", "relative_support": 0.027076589279313768}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5400649722421897}, {"state": "ACP_LOW", "relative_support": 0.4599350277578102}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia195_utt0.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.2000|The character's emotional state is anxious, tense, frustrated, angry.|
|long_graph_dataset_best|0.2000|The character's emotional state is anxiety, tension, stress, frustration, anger.|

## 54. MELD / test_dia200_utt4 — 相对自身起点改善

- 参考：anger；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：0.0000→1.0000；50权重零/错11次、满/对30次。
- 模型字幕：We're trying to think!
- 中文：我们正在努力思考！
- 起点回答：The character's emotional state is joyful, excited.
- 赢家回答：The character's emotional state is frustrated, angry, playful, relaxed.
- 起点抽取：[joyful, excited]
- 赢家抽取：[frustrated, angry, playful, relaxed]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_DESIRE_NEED, AUD_INTONATION_RISING, VIS_LIPS_PRESSED, VIS_HEAD_LOWERED
- 图候选：delightful, proud, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5294665913195786}, {"state": "AGC_INCONGRUENT", "relative_support": 0.47053340868042137}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6412129368883465}, {"state": "AEX_EXPECTED", "relative_support": 0.35878706311165354}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5033874648748514}, {"state": "AAG_SELF", "relative_support": 0.49661253512514847}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7959315994346208}, {"state": "ACP_LOW", "relative_support": 0.20406840056537928}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia200_utt4.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.2000|The character's emotional state is excitement, surprise, joy, humor, self-deprecation, irony.|
|long_graph_dataset_best|0.0000|The character's emotional state is anxiety, stress, confusion, dissatisfaction, humor.|

## 55. MELD / test_dia38_utt3 — 相对自身起点改善

- 参考：joy；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：0.4000→0.8000；50权重零/错0次、满/对3次。
- 模型字幕：You bet! What's the part?
- 中文：当然！是哪个部分？
- 起点回答：The character's emotional state is excited, enthusiastic.
- 赢家回答：The character's emotional state is excited, enthusiastic, confident, firm, positive.
- 起点抽取：[excited, enthusiastic]
- 赢家抽取：[excited, enthusiastic, confident, firm, positive]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_RHETORICAL_QUESTION, AUD_INTONATION_RISING, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, care, anxious（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7211032674330957}, {"state": "AGC_INCONGRUENT", "relative_support": 0.2788967325669044}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7786403893774717}, {"state": "AEX_EXPECTED", "relative_support": 0.22135961062252826}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.610409876191362}, {"state": "AAG_SELF", "relative_support": 0.24249715313828}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.924489410202532}, {"state": "ACT_CERTAIN", "relative_support": 0.07551058979746805}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.573917112024595}, {"state": "ACP_LOW", "relative_support": 0.426082887975405}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia38_utt3.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.8000|The character's emotional state is excited, enthusiastic, positive.|
|long_graph_dataset_best|0.8000|The character's emotional state is excited, confident, positive.|

## 56. MELD / test_dia205_utt5 — 相对自身起点恶化

- 参考：disgust；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：0.3333→0.0000；50权重零/错41次、满/对4次。
- 模型字幕：Oh, that is so sick.
- 中文：哦，那真是太恶心了。
- 起点回答：The character's emotional state is disappointed, frustrated, angry, sarcastic, mocking, disapproval, disagreement.
- 赢家回答：The character's emotional state is unhappy, concerned, frustrated, annoyed.
- 起点抽取：[disappointed, frustrated, angry, sarcastic, mocking, disapproval, disagreement]
- 赢家抽取：[unhappy, concerned, frustrated, annoyed]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：disappointed, anger, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8074586291003952}, {"state": "AGC_CONGRUENT", "relative_support": 0.1925413708996048}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9050587436681857}, {"state": "AEX_EXPECTED", "relative_support": 0.09494125633181431}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8199956836543254}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.12566437378444198}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7061100106919613}, {"state": "ACT_CERTAIN", "relative_support": 0.2938899893080386}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.726829964881195}, {"state": "ACP_HIGH", "relative_support": 0.27317003511880494}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia205_utt5.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is disappointment, dejection, concern, worry, dissatisfaction.|
|long_graph_dataset_best|0.0000|The character's emotional state is disappointment, helplessness, frustration.|

## 57. MELD / test_dia88_utt0 — 相对自身起点恶化

- 参考：joy；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：1.0000→0.8000；50权重零/错0次、满/对25次。
- 模型字幕：Welcome everybody, welcome to Amazing Discoveries!
- 中文：欢迎大家，欢迎来到惊奇发现！
- 起点回答：The character's emotional state is excited, passionate, positive, confident, authoritative.
- 赢家回答：The character's emotional state is excited, confident, energetic.
- 起点抽取：[excited, passionate, positive, confident, authoritative]
- 赢家抽取：[excited, confident, energetic]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_VOICE_TENSE, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, hopeful, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7126238115953751}, {"state": "AGC_MIXED", "relative_support": 0.15253043910379863}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7683520292351286}, {"state": "AEX_EXPECTED", "relative_support": 0.23164797076487145}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.9040965920853558}, {"state": "AAG_SELF", "relative_support": 0.09590340791464426}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6540985478507997}, {"state": "ACT_CERTAIN", "relative_support": 0.3459014521492004}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.9425209191917482}, {"state": "ACP_LOW", "relative_support": 0.05747908080825179}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia88_utt0.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is positive, enthusiastic, passionate, joyful, excited.|
|long_graph_dataset_best|1.0000|The character's emotional state is positive, enthusiastic, passionate.|

## 58. MELD / test_dia271_utt3 — 相对自身起点恶化

- 参考：fear；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：1.0000→0.0000；50权重零/错10次、满/对4次。
- 模型字幕：I'm trppd... in an ATM vstbl... wth
- 中文：我被困在一个ATM可见的地方...和...在一起。
- 起点回答：The character's emotional state is anxious, excited, frustrated, angry.
- 赢家回答：The character's emotional state is frustrated, angry, agitated, negative, depressed.
- 起点抽取：[anxious, excited, frustrated, angry]
- 赢家抽取：[frustrated, angry, agitated, negative, depressed]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_HIGH, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN, VIS_LIPS_PRESSED, VIS_HEAD_LOWERED
- 图候选：disappointed, anger, skeptical（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9382181277412995}, {"state": "AGC_MIXED", "relative_support": 0.06178187225870041}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8342936451774468}, {"state": "AEX_EXPECTED", "relative_support": 0.16570635482255316}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.42466324667600314}, {"state": "AAG_SELF", "relative_support": 0.34439247299335346}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9882918493463781}, {"state": "ACP_HIGH", "relative_support": 0.011708150653621777}]}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia271_utt3.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.6000|The character's emotional state is happy, satisfied.|
|long_graph_dataset_best|0.0000|The character's emotional state is anger, sadness, frustration, hopelessness, confusion, contemplation.|

## 59. MELD / test_dia169_utt14 — neutral参考，HIT不计分

- 参考：neutral；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：未计分→未计分；50权重零/错None次、满/对None次。
- 模型字幕：Ohh I wonder if that dude.
- 中文：哦，我想知道那个家伙。
- 起点回答：The character's emotional state is confused, skeptical, uncertain.
- 赢家回答：The character's emotional state is curiosity, tension, anxiety.
- 起点抽取：[confused, skeptical, uncertain]
- 赢家抽取：[curiosity, tension, anxiety]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：
- 图候选：（仅实际level3展示）。
- Appraisal：{}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia169_utt14.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|未计分|The character's emotional state is curious, excited, teasing.|
|long_graph_dataset_best|未计分|The character's emotional state is questioning, uncertainty, worry, anxiety, frustration, irritability.|

## 60. MELD / test_dia58_utt11 — neutral参考，HIT不计分

- 参考：neutral；赢家：from_30_epoch_39_MELD；起点epoch30。
- 质量：未计分→未计分；50权重零/错None次、满/对None次。
- 模型字幕：Are you okay?
- 中文：你还好吗？
- 起点回答：The character's emotional state is concerned, caring, positive.
- 赢家回答：The character's emotional state is concern, inquiry, happiness.
- 起点抽取：[concerned, caring, positive]
- 赢家抽取：[concern, inquiry, happiness]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：
- 图候选：（仅实际level3展示）。
- Appraisal：{}
- 视频：/ai/sjq/AffectGPT/dataset/meld-process/subvideo/test_dia58_utt11.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|未计分|The character's emotional state is care, concern, happiness, satisfaction.|
|long_graph_dataset_best|未计分|The character's emotional state is concern, care.|

## 61. IEMOCAPFour / Ses05M_script02_2_F015 — 50权重持续错误/零命中

- 参考：sad；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：Dancing barefoot in the sand, drinking champagne out of the bottle.
- 中文：在沙滩上赤脚跳舞，喝着瓶装香槟。
- 起点回答：The character's emotional state is positive, contrast, negative.
- 赢家回答：The character's emotional state is excited, joyful, content, satisfied.
- 起点抽取：[positive, negative]
- 赢家抽取：[excited, joyful, content, satisfied]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_HEAD_LOWERED
- 图候选：ashamed, depressed, pity（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_MIXED", "relative_support": 0.40807024462714914}, {"state": "AGC_INCONGRUENT", "relative_support": 0.3700700723785813}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5698052351476292}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4301947648523709}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7338336656005162}, {"state": "ACT_UNCERTAIN", "relative_support": 0.26616633439948384}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9791113312974267}, {"state": "ACP_HIGH", "relative_support": 0.020888668702573387}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_script02_2_F015.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is positive, contrast, negative.|
|long_graph_dataset_best|0.0000|The character's emotional state is joy, satisfaction, freedom, unrestricted, happiness.|

## 62. IEMOCAPFour / Ses05F_script03_2_F030 — 50权重持续错误/零命中

- 参考：anger；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：There aren't any people upstairs; it's a photographer's studio.
- 中文：楼上没有人，那是一个摄影师的工作室。
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is neutral.
- 起点抽取：[neutral]
- 赢家抽取：[neutral]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, AUD_INTONATION_FALLING, VIS_LIPS_PRESSED
- 图候选：apathetic, disappointed, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8575251724388171}, {"state": "AGC_CONGRUENT", "relative_support": 0.09745199034619399}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6000659544344026}, {"state": "AEX_UNEXPECTED", "relative_support": 0.3999340455655974}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6241413527786867}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3758586472213134}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8474466305916669}, {"state": "ACT_UNCERTAIN", "relative_support": 0.152553369408333}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9181522147422353}, {"state": "ACP_HIGH", "relative_support": 0.08184778525776462}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_script03_2_F030.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is neutral.|
|long_graph_dataset_best|0.0000|The character's emotional state is neutral, indifferent, bored.|

## 63. IEMOCAPFour / Ses05F_script01_3_F015 — 50权重持续错误/零命中

- 参考：happy；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：I'll never forgive you.  Why did you wait so long?  All this time I've been wondering if I was a fool for thinking of you!
- 中文：我永远不会原谅你。你为什么等了这么久？这段时间我一直在想，我是否傻了，为了想着你！
- 起点回答：The character's emotional state is angry, disappointed, sad.
- 赢家回答：The character's emotional state is anger, frustration, disappointment, dissatisfaction.
- 起点抽取：[angry, disappointed, sad]
- 赢家抽取：[anger, frustration, disappointment, dissatisfaction]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_UNCERTAINTY_HEDGE, TXT_RHETORICAL_QUESTION, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_SELF, AUD_SPEECH_RATE_REL_FAST, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_LAUGHTER_PRESENT, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：anger, disappointed, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5921948609205586}, {"state": "AGC_CONGRUENT", "relative_support": 0.3991296706641987}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8072404939918336}, {"state": "AEX_EXPECTED", "relative_support": 0.19275950600816644}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.44363551000700163}, {"state": "AAG_SELF", "relative_support": 0.44150702661890917}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8271306308724707}, {"state": "ACT_CERTAIN", "relative_support": 0.17286936912752934}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6999206831386078}, {"state": "ACP_HIGH", "relative_support": 0.3000793168613922}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_script01_3_F015.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is angry, disappointed, sad.|
|long_graph_dataset_best|0.0000|The character's emotional state is disappointment, anger, frustration, unhappiness.|

## 64. IEMOCAPFour / Ses05M_impro07_F022 — 50权重持续正确/满命中

- 参考：happy；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：Oh I'm so glad.
- 中文：哦，我太高兴了。
- 起点回答：The character's emotional state is happy, excited, surprised.
- 赢家回答：The character's emotional state is excited, joyful, delighted, pleased.
- 起点抽取：[happy, excited, surprised]
- 赢家抽取：[excited, joyful, delighted, pleased]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_POSITIVE, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.930003654639002}, {"state": "AGC_INCONGRUENT", "relative_support": 0.06999634536099808}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7458008922154015}, {"state": "AEX_EXPECTED", "relative_support": 0.2541991077845986}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5538485415098915}, {"state": "AAG_SELF", "relative_support": 0.3225190519973957}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7226018746108092}, {"state": "ACT_CERTAIN", "relative_support": 0.27739812538919095}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8225870518789157}, {"state": "ACP_LOW", "relative_support": 0.17741294812108424}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_impro07_F022.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is happy, excited, surprised.|
|long_graph_dataset_best|1.0000|The character's emotional state is excited, joyful.|

## 65. IEMOCAPFour / Ses05F_script03_2_F038 — 50权重持续正确/满命中

- 参考：anger；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：No, no.  I'm tired of listening to you.  You're boorish and idiotic and completely overbearing.
- 中文：不，不。我厌倦了听你说话。你粗鲁、愚蠢而且完全专横。
- 起点回答：The character's emotional state is anger, frustration, disrespect.
- 赢家回答：The character's emotional state is anger, frustration, dissatisfaction.
- 起点抽取：[anger, frustration]
- 赢家抽取：[anger, frustration, dissatisfaction]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN
- 图候选：anger, disappointed, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9975331422063148}, {"state": "AGR_RELEVANT", "relative_support": 0.0024668577936852436}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8471455329259845}, {"state": "AGC_CONGRUENT", "relative_support": 0.15285446707401548}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9414247767968045}, {"state": "AEX_EXPECTED", "relative_support": 0.058575223203195484}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8992781375916352}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.06362609154373697}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6155844132575456}, {"state": "ACT_CERTAIN", "relative_support": 0.38441558674245435}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7890354758951008}, {"state": "ACP_HIGH", "relative_support": 0.21096452410489924}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_script03_2_F038.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is anger, frustration, disrespect.|
|long_graph_dataset_best|1.0000|The character's emotional state is anger, frustration, irritability.|

## 66. IEMOCAPFour / Ses05M_impro06_M008 — 50权重持续正确/满命中

- 参考：sad；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：And he's gone now and I  -- I just can't believe it.
- 中文：他现在走了，我--我简直不敢相信。
- 起点回答：The character's emotional state is disappointment, sadness, anxiety, overwhelm.
- 赢家回答：The character's emotional state is disappointment, dejection, sadness, surprise, shock, disbelief.
- 起点抽取：[disappointment, sadness, anxiety, overwhelm]
- 赢家抽取：[disappointment, dejection, sadness, surprise, shock, disbelief]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED
- 图候选：ashamed, despair, depressed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.4950170062004981}, {"state": "AGC_CONGRUENT", "relative_support": 0.3284040489573302}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8818460932920312}, {"state": "AEX_UNEXPECTED", "relative_support": 0.1181539067079688}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.57082078946586}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4291792105341401}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7304205591598893}, {"state": "ACT_UNCERTAIN", "relative_support": 0.26957944084011076}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7349770639947971}, {"state": "ACP_HIGH", "relative_support": 0.26502293600520294}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_impro06_M008.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is disappointment, sadness, anxiety, overwhelm.|
|long_graph_dataset_best|1.0000|The character's emotional state is sadness, grief, loss, surprise.|

## 67. IEMOCAPFour / Ses05M_script01_1_F021 — 赢家零/错，其他权重经常命中/对

- 参考：anger；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：1.0000→0.0000；50权重零/错10次、满/对37次。
- 模型字幕：I ignore what I got to ignore.  I mean, the girl is Larry's girl.
- 中文：我忽略我需要忽略的事情。我的意思是，那个女孩是拉里的女孩。
- 起点回答：The character's emotional state is confused, anxious, frustrated, angry, aggressive, mocking, confrontational.
- 赢家回答：The character's emotional state is tense, uneasy, anxious.
- 起点抽取：[confused, anxious, frustrated, angry, aggressive, confrontational]
- 赢家抽取：[tense, uneasy, anxious]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_DESIRE_NEED, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9896950734779317}, {"state": "AGR_RELEVANT", "relative_support": 0.01030492652206831}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9384881461368151}, {"state": "AGC_CONGRUENT", "relative_support": 0.061511853863184925}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8717034995875245}, {"state": "AEX_EXPECTED", "relative_support": 0.1282965004124755}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7400240408230259}, {"state": "AAG_SELF", "relative_support": 0.18312123172991765}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9821303667797643}, {"state": "ACT_CERTAIN", "relative_support": 0.017869633220235846}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8151613742915104}, {"state": "ACP_HIGH", "relative_support": 0.18483862570848955}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_script01_1_F021.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is confused, anxious, frustrated, angry, aggressive, mocking, confrontational.|
|long_graph_dataset_best|1.0000|The character's emotional state is angry, negative, complaint, dissatisfaction.|

## 68. IEMOCAPFour / Ses05F_impro04_F000 — 赢家零/错，其他权重经常命中/对

- 参考：sad；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：1.0000→0.0000；50权重零/错22次、满/对26次。
- 模型字幕：Brian, I need help.
- 中文：布莱恩，我需要帮助。
- 起点回答：The character's emotional state is distress, need for assistance, sadness, anxiety, tension.
- 赢家回答：The character's emotional state is distress, need for assistance.
- 起点抽取：[distress, need for assistance, sadness, anxiety, tension]
- 赢家抽取：[distress]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_EYES_SQUINTED, VIS_LIPS_PRESSED
- 图候选：delightful, awe, acceptance（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_MIXED", "relative_support": 0.42256793189851954}, {"state": "AGC_CONGRUENT", "relative_support": 0.3862271141063021}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5806862134840185}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4193137865159814}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6429963582651359}, {"state": "ACT_UNCERTAIN", "relative_support": 0.35700364173486404}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5077481310152346}, {"state": "ACP_LOW", "relative_support": 0.4922518689847653}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_impro04_F000.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is distress, need for assistance, sadness, anxiety, tension.|
|long_graph_dataset_best|1.0000|The character's emotional state is sadness, distress, overwhelm.|

## 69. IEMOCAPFour / Ses05M_script03_1_M004 — 赢家零/错，其他权重经常命中/对

- 参考：happy；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：0.8000→0.0000；50权重零/错15次、满/对13次。
- 模型字幕：I don't care then.
- 中文：我不在乎。
- 起点回答：The character's emotional state is positive, lighthearted, indifferent.
- 赢家回答：The character's emotional state is indifference, disregard, nonchalance.
- 起点抽取：[positive, lighthearted, indifferent]
- 赢家抽取：[indifference, disregard, nonchalance]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.796209276321802}, {"state": "AGC_INCONGRUENT", "relative_support": 0.20379072367819798}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.659386137386196}, {"state": "AEX_EXPECTED", "relative_support": 0.34061386261380405}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5046307422153765}, {"state": "AAG_OTHER", "relative_support": 0.3378859106865843}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8446333870562039}, {"state": "ACT_CERTAIN", "relative_support": 0.15536661294379603}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.6889013852307573}, {"state": "ACP_LOW", "relative_support": 0.31109861476924267}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_script03_1_M004.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.8000|The character's emotional state is positive, lighthearted, indifferent.|
|long_graph_dataset_best|0.8000|The character's emotional state is indifferent, unconcerned, positive, cheerful.|

## 70. IEMOCAPFour / Ses05M_script03_2_M035 — 赢家满/对，其他权重经常不满/错

- 参考：anger；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：1.0000→1.0000；50权重零/错20次、满/对7次。
- 模型字幕：This is no time of the year for Tunis.
- 中文：这不是突尼斯的时候。
- 起点回答：The character's emotional state is discontent, anger, anxiety, stress.
- 赢家回答：The character's emotional state is discontent, frustration, anger, sadness, melancholy.
- 起点抽取：[discontent, anger, anxiety, stress]
- 赢家抽取：[discontent, frustration, anger, sadness, melancholy]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, AUD_INTONATION_RISING, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7049492959876318}, {"state": "AGC_INCONGRUENT", "relative_support": 0.29505070401236816}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6820313644475615}, {"state": "AEX_EXPECTED", "relative_support": 0.3179686355524385}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.45427401675619805}, {"state": "AAG_OTHER", "relative_support": 0.40916749550475495}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8656419870218998}, {"state": "ACT_CERTAIN", "relative_support": 0.1343580129781003}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5344400757968979}, {"state": "ACP_LOW", "relative_support": 0.4655599242031022}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_script03_2_M035.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is discontent, anger, anxiety, stress.|
|long_graph_dataset_best|0.6000|The character's emotional state is excited, passionate, critical, dissatisfied.|

## 71. IEMOCAPFour / Ses05F_impro06_F016 — 赢家满/对，其他权重经常不满/错

- 参考：sad；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：0.2000→1.0000；50权重零/错17次、满/对20次。
- 模型字幕：I can't imagine what his- what his parents are going through.
- 中文：我无法想象他的父母正在经历什么。
- 起点回答：The character's emotional state is sympathy, concern, confusion.
- 赢家回答：The character's emotional state is sympathy, helplessness, distress, sorrow, negative emotions.
- 起点抽取：[sympathy, concern, confusion]
- 赢家抽取：[sympathy, helplessness, distress, sorrow, negative emotions]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, AUD_VOICE_TREMBLING, AUD_CRYING_SOBBING_PRESENT, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN, VIS_LIPS_PRESSED, VIS_HEAD_LOWERED
- 图候选：despair, depressed, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8669288699707938}, {"state": "AGC_MIXED", "relative_support": 0.07139720100917744}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6988246937390292}, {"state": "AEX_UNEXPECTED", "relative_support": 0.3011753062609708}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5494379751107987}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3876013417417415}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5910578910609819}, {"state": "ACT_UNCERTAIN", "relative_support": 0.40894210893901806}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9873357953059768}, {"state": "ACP_HIGH", "relative_support": 0.012664204694023226}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_impro06_F016.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.2000|The character's emotional state is sympathy, concern, confusion.|
|long_graph_dataset_best|1.0000|The character's emotional state is sadness, helplessness, confusion.|

## 72. IEMOCAPFour / Ses05M_script03_1_M015 — 赢家满/对，其他权重经常不满/错

- 参考：happy；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：0.4000→1.0000；50权重零/错29次、满/对14次。
- 模型字幕：uh- the- Being flippant brings out the acid in their damned beauty and light.
- 中文：嗯-那个-轻率地行事会激发出他们该死的美丽和光芒中的酸液。
- 起点回答：The character's emotional state is excited, anxious.
- 赢家回答：The character's emotional state is joy, surprise, mockery, humor, sarcasm.
- 起点抽取：[excited, anxious]
- 赢家抽取：[joy, surprise, mockery, humor, sarcasm]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, ashamed, disappointed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.4788678477066032}, {"state": "AGC_CONGRUENT", "relative_support": 0.4245149657025016}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8090261936146799}, {"state": "AEX_UNEXPECTED", "relative_support": 0.19097380638532016}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5135320507639743}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3673416253281532}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7610198263975424}, {"state": "ACT_UNCERTAIN", "relative_support": 0.2389801736024576}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5795114722677791}, {"state": "ACP_HIGH", "relative_support": 0.42048852773222095}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_script03_1_M015.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.4000|The character's emotional state is excited, anxious.|
|long_graph_dataset_best|1.0000|The character's emotional state is joyful, humorous.|

## 73. IEMOCAPFour / Ses05M_script01_3_F015 — 相对自身起点改善

- 参考：happy；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：0.6000→0.8000；50权重零/错0次、满/对20次。
- 模型字幕：Not like that you're not.
- 中文：不是那样的，你不是。
- 起点回答：The character's emotional state is excited, enthusiastic, playful, humorous.
- 赢家回答：The character's emotional state is positive, dissatisfied, critical.
- 起点抽取：[excited, enthusiastic, playful, humorous]
- 赢家抽取：[positive, dissatisfied, critical]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6014732064933589}, {"state": "AGC_INCONGRUENT", "relative_support": 0.3985267935066411}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7171722090229394}, {"state": "AEX_EXPECTED", "relative_support": 0.2828277909770606}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.47751942459411106}, {"state": "AAG_SELF", "relative_support": 0.38019996447802445}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7549544990856312}, {"state": "ACT_CERTAIN", "relative_support": 0.24504550091436872}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5238904478093265}, {"state": "ACP_LOW", "relative_support": 0.47610955219067347}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_script01_3_F015.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.6000|The character's emotional state is excited, enthusiastic, playful, humorous.|
|long_graph_dataset_best|0.8000|The character's emotional state is positive, negative.|

## 74. IEMOCAPFour / Ses05M_script02_2_F017 — 相对自身起点改善

- 参考：sad；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：0.0000→1.0000；50权重零/错11次、满/对11次。
- 模型字幕：No.
- 中文：不。
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is boredom, sadness, emotional numbness, disconnection.
- 起点抽取：[]
- 赢家抽取：[boredom, sadness, emotional numbness, disconnection]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, AUD_INTONATION_RISING, VIS_HEAD_LOWERED
- 图候选：disappointed, apathetic, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8817576106709153}, {"state": "AEX_EXPECTED", "relative_support": 0.11824238932908464}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8220382467420553}, {"state": "AAG_SELF", "relative_support": 0.1779617532579447}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_script02_2_F017.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is neutral.|
|long_graph_dataset_best|0.6000|The character's emotional state is boredom, disinterest.|

## 75. IEMOCAPFour / Ses05F_impro05_F019 — 相对自身起点改善

- 参考：anger；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：0.0000→0.4000；50权重零/错17次、满/对16次。
- 模型字幕：No, but I mean like why can't- why can't you find it?  Where did it go?  Who lost it?
- 中文：不，但我的意思是为什么不能-为什么你找不到它？它去哪了？谁弄丢了它？
- 起点回答：The character's emotional state is tense, anxious.
- 赢家回答：The character's emotional state is anxiety, frustration, confusion, dissatisfaction, defeat, tension.
- 起点抽取：[tense, anxious]
- 赢家抽取：[anxiety, frustration, confusion, dissatisfaction, defeat, tension]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_RHETORICAL_QUESTION, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN
- 图候选：apathetic, disappointed, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.6211341329738429}, {"state": "AGC_MIXED", "relative_support": 0.3788658670261571}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 1.0}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_impro05_F019.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is tense, anxious.|
|long_graph_dataset_best|0.4000|The character's emotional state is anxiety, frustration, confusion, dissatisfaction.|

## 76. IEMOCAPFour / Ses05M_script01_1b_M036 — 相对自身起点恶化

- 参考：anger；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：0.2000→0.0000；50权重零/错9次、满/对0次。
- 模型字幕：Yeah, I'd like one hour a day.  If I have to grub for money all day long, I'd like to go home to something beautiful.  I'd like a family.  I'd like some kids.
- 中文：是的，我每天想要一个小时。如果我必须整天为钱而奔波，我想回家看到美好的事物。我想要一个家庭。我想要一些孩子。
- 起点回答：The character's emotional state is happiness, satisfaction, longing, desire.
- 赢家回答：The character's emotional state is passionate, excited, enthusiastic, longing.
- 起点抽取：[happiness, satisfaction, longing, desire]
- 赢家抽取：[passionate, excited, enthusiastic, longing]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：hopeful, joy, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7356707294851238}, {"state": "AGC_MIXED", "relative_support": 0.15393495525456405}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.624346179880448}, {"state": "AEX_EXPECTED", "relative_support": 0.37565382011955195}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.630583366943232}, {"state": "AAG_SELF", "relative_support": 0.3018062267348281}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.520706445442288}, {"state": "ACT_CERTAIN", "relative_support": 0.47929355455771216}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.9728368561159646}, {"state": "ACP_LOW", "relative_support": 0.02716314388403535}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_script01_1b_M036.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.2000|The character's emotional state is happiness, satisfaction, longing, desire.|
|long_graph_dataset_best|0.0000|The character's emotional state is positive, optimistic, desire for a family, desire for children.|

## 77. IEMOCAPFour / Ses05M_impro07_M013 — 相对自身起点恶化

- 参考：happy；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：0.2000→0.0000；50权重零/错32次、满/对0次。
- 模型字幕：What are you, wait, what are you doing?
- 中文：你是谁，等等，你在做什么？
- 起点回答：The character's emotional state is surprised, confused, amused, teasing.
- 赢家回答：The character's emotional state is anxious, irritated, angry, dissatisfied, impatient.
- 起点抽取：[surprised, confused, amused, teasing]
- 赢家抽取：[anxious, irritated, angry, dissatisfied, impatient]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_EXCLAMATION_INTERJECTION, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：anxious, care, focused（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.914995213717732}, {"state": "AGC_INCONGRUENT", "relative_support": 0.085004786282268}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8059643960707135}, {"state": "AAG_SELF", "relative_support": 0.19403560392928662}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9929626500906741}, {"state": "ACT_CERTAIN", "relative_support": 0.007037349909325935}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_impro07_M013.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.2000|The character's emotional state is surprised, confused, amused, teasing.|
|long_graph_dataset_best|0.0000|The character's emotional state is anxiety, unease, confusion.|

## 78. IEMOCAPFour / Ses05M_impro02_M018 — 相对自身起点恶化

- 参考：sad；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：0.6000→0.0000；50权重零/错49次、满/对0次。
- 模型字幕：I know.  But I'll-I'll send the pictures all the time and I'll write them emails and you can read them the emails that I send them.
- 中文：我知道。但是我会一直发送照片，写邮件给他们，你可以读给他们我发送的邮件。
- 起点回答：The character's emotional state is excitement, frustration, anxiety.
- 赢家回答：The character's emotional state is anxious, tense, uneasy.
- 起点抽取：[excitement, frustration, anxiety]
- 赢家抽取：[anxious, tense, uneasy]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_FAST, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_PAUSE_LONG, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, anger, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.42023137097267993}, {"state": "AGC_MIXED", "relative_support": 0.3816021123859396}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.837357129776508}, {"state": "AEX_EXPECTED", "relative_support": 0.16264287022349191}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.48836935554197136}, {"state": "AAG_SELF", "relative_support": 0.3244194756309753}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7568147059300715}, {"state": "ACT_CERTAIN", "relative_support": 0.24318529406992848}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5883830086276461}, {"state": "ACP_LOW", "relative_support": 0.4116169913723539}]}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05M_impro02_M018.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.6000|The character's emotional state is excitement, frustration, anxiety.|
|long_graph_dataset_best|0.6000|The character's emotional state is anxious, tense, confused, overwhelmed, helpless, hopeless.|

## 79. IEMOCAPFour / Ses05F_script02_1_F005 — neutral参考，HIT不计分

- 参考：neutral；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：未计分→未计分；50权重零/错None次、满/对None次。
- 模型字幕：yes.
- 中文：是的。
- 起点回答：The character's emotional state is neutral, calm, relaxed, tense, anxious.
- 赢家回答：The character's emotional state is neutral, positive.
- 起点抽取：[neutral, calm, relaxed, tense, anxious]
- 赢家抽取：[neutral, positive]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：
- 图候选：（仅实际level3展示）。
- Appraisal：{}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_script02_1_F005.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|未计分|The character's emotional state is neutral, calm, relaxed, tense, anxious.|
|long_graph_dataset_best|未计分|The character's emotional state is neutral.|

## 80. IEMOCAPFour / Ses05F_impro08_F010 — neutral参考，HIT不计分

- 参考：neutral；赢家：from_30_epoch_39_IEMOCAPFour；起点epoch30。
- 质量：未计分→未计分；50权重零/错None次、满/对None次。
- 模型字幕：So is it, is- is it at all possible that maybe this statement is just old and that the transaction hadn't been processed yet?
- 中文：那么，这是不是说，这个陈述可能只是旧的，而且这笔交易还没有被处理呢？
- 起点回答：The character's emotional state is anxious, tense, uncertain, worried, dissatisfied.
- 赢家回答：The character's emotional state is worried, anxious.
- 起点抽取：[anxious, tense, uncertain, worried, dissatisfied]
- 赢家抽取：[worried, anxious]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：
- 图候选：（仅实际level3展示）。
- Appraisal：{}
- 视频：/ai/sjq/AffectGPT/dataset/iemocap-process/subvideo-tgt/Ses05F_impro08_F010.avi

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|未计分|The character's emotional state is anxious, tense, uncertain, worried, dissatisfied.|
|long_graph_dataset_best|未计分|The character's emotional state is anxious, uneasy, tense.|

## 81. CMUMOSI / cXypl4FnoZo_11 — 50权重持续错误/零命中

- 参考：1.4；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：UM ANYWAY I WOULD SAY JUST YOU GO AND SEE IT IF YOU WERE THINKING ABOUT SEEING IT BUT YOU WERENT SURE IF IT WOULD BE WORTH SEEING
- 中文：总的来说，我会建议你去看看，如果你在考虑是否要去看，但又不确定是否值得看的话。
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is neutral.
- 起点抽取：[]
- 赢家抽取：[]
- 最终极性：neutral→neutral。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_UNCERTAINTY_HEDGE, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_LIPS_PRESSED
- 图候选：hesitant, sceptical, anxious（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_MIXED", "relative_support": 0.46933774041956916}, {"state": "AGC_CONGRUENT", "relative_support": 0.31830026332679723}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6548180656024511}, {"state": "AEX_UNEXPECTED", "relative_support": 0.3451819343975488}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.611951706439829}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3739818859924918}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.756842347606662}, {"state": "ACT_CERTAIN", "relative_support": 0.243157652393338}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5528755933394551}, {"state": "ACP_LOW", "relative_support": 0.4471244066605449}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/cXypl4FnoZo_11.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is uncertain, hesitant.|
|long_graph_dataset_best|0.0000|The character's emotional state is neutral, hesitant, uncertain.|

## 82. CMUMOSI / lXPQBPVc5Cw_4 — 50权重持续错误/零命中

- 参考：-1.2；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：CHUCKLING I MEAN AND I DONT ACTUALLY GO AND IM NOT BEING BIASED BECAUSE I DONT REALLY GO FOR THE ANIMATED TYPE FILMS
- 中文：我笑着说，我并不真的去看，我也没有偏见，因为我真的不太喜欢动画类型的电影。
- 起点回答：The character's emotional state is relaxed, humorous, teasing, joking, positive.
- 赢家回答：The character's emotional state is relaxed, humorous, sarcastic, teasing.
- 起点抽取：[relaxed, humorous, teasing, joking, positive]
- 赢家抽取：[relaxed, humorous, sarcastic, teasing]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PAUSE_LONG, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.6773865649398548}, {"state": "AGC_CONGRUENT", "relative_support": 0.23699708377376935}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6493001712034836}, {"state": "AEX_EXPECTED", "relative_support": 0.3506998287965164}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.40164396273839453}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3460628095217466}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.5802324429827159}, {"state": "ACT_CERTAIN", "relative_support": 0.419767557017284}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7544083142876379}, {"state": "ACP_HIGH", "relative_support": 0.2455916857123622}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/lXPQBPVc5Cw_4.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is light-hearted, humorous, indifferent.|
|long_graph_dataset_best|0.0000|The character's emotional state is cheerful, humorous, positive.|

## 83. CMUMOSI / dq3Nf_lMPnE_4 — 50权重持续错误/零命中

- 参考：-0.4；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：THEY SOLVED THIS DILEMMA BY REMOVING THE PAST WITHIN ITS A WONDERFUL LIFE TWIST COURTECY OF NEW BETTY RUMPELSTILTSKIN
- 中文：他们通过移除过去，以新贝蒂鲁赛尔斯金的《美好生活》的转折来解决这个困境。
- 起点回答：The character's emotional state is excited, enthusiastic, optimistic, positive.
- 赢家回答：The character's emotional state is optimistic, problem-solving, contemplative, introspective, hopeful.
- 起点抽取：[excited, enthusiastic, optimistic, positive]
- 赢家抽取：[optimistic, problem-solving, contemplative, introspective, hopeful]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER, TXT_EXPLICIT_SUCCESS_OUTCOME, AUD_SPEECH_RATE_REL_SLOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：proud, hopeful, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8032391086105698}, {"state": "AGC_MIXED", "relative_support": 0.17278517379075134}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8377553374593989}, {"state": "AEX_UNEXPECTED", "relative_support": 0.16224466254060113}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5756047597847009}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.21993834434648016}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8463019106493641}, {"state": "ACT_UNCERTAIN", "relative_support": 0.15369808935063584}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8811647585287271}, {"state": "ACP_LOW", "relative_support": 0.11883524147127285}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/dq3Nf_lMPnE_4.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is excited, satisfied.|
|long_graph_dataset_best|0.0000|The character's emotional state is positive, optimistic, excited, anticipatory.|

## 84. CMUMOSI / k5Y_838nuGo_26 — 50权重持续正确/满命中

- 参考：2.0；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：BUT IT AS GREAT
- 中文：但它很棒
- 起点回答：The character's emotional state is positive, excited, satisfied, content, comfortable.
- 赢家回答：The character's emotional state is positive, excited, confident.
- 起点抽取：[positive, excited, satisfied, content, comfortable]
- 赢家抽取：[positive, excited, confident]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_INTONATION_RISING, VIS_MOUTH_CORNERS_DOWN
- 图候选：appreciated, awe, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.4776191964655584}, {"state": "AGC_MIXED", "relative_support": 0.37324528670027746}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6387940973603289}, {"state": "AEX_EXPECTED", "relative_support": 0.3612059026396711}], "APP_AGENCY": [], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.647218587455403}, {"state": "ACT_CERTAIN", "relative_support": 0.35278141254459705}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5742910881651548}, {"state": "ACP_LOW", "relative_support": 0.42570891183484527}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/k5Y_838nuGo_26.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is positive, happiness, excitement.|
|long_graph_dataset_best|1.0000|The character's emotional state is positive.|

## 85. CMUMOSI / f_pcplsH_V0_11 — 50权重持续正确/满命中

- 参考：-0.4；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：NOW I DIDNT REALLY LIKE THE FIRST HOUR THAT MUCH THOUGH
- 中文：不过，我真的不太喜欢开始的那一个小时。
- 起点回答：The character's emotional state is negative, dissatisfaction, disappointment, anxiety, excitement.
- 赢家回答：The character's emotional state is neutral.
- 起点抽取：[negative, dissatisfaction, disappointment, anxiety, excitement]
- 赢家抽取：[neutral]
- 最终极性：negative→neutral。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_HEAD_LOWERED
- 图候选：disappointed, anger, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7345251931412767}, {"state": "AGC_CONGRUENT", "relative_support": 0.23179717950656825}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6188552990742067}, {"state": "AEX_EXPECTED", "relative_support": 0.3811447009257932}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.37236026462568667}, {"state": "AAG_OTHER", "relative_support": 0.3315323378997074}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.667123112362705}, {"state": "ACT_CERTAIN", "relative_support": 0.332876887637295}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7373445854690489}, {"state": "ACP_HIGH", "relative_support": 0.26265541453095115}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/f_pcplsH_V0_11.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is dissatisfied, disappointed, anxious, tense, excited.|
|long_graph_dataset_best|1.0000|The character's emotional state is neutral, slightly negative.|

## 86. CMUMOSI / cXypl4FnoZo_16 — 50权重持续正确/满命中

- 参考：-0.6；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：I DONT KNOW HOW TO LIKE TELL YOU WHO HE IS COZ YOURE GONNA BE LIKE THAT DOESNT NARROW IT DOWN AT ALL
- 中文：我不知道该如何向你描述他是谁，因为你可能会觉得这根本无法帮你缩小范围。
- 起点回答：The character's emotional state is agitated, anxious, tense, confused, dissatisfied.
- 赢家回答：The character's emotional state is frustrated, angry, impatient, overwhelmed, anxious.
- 起点抽取：[agitated, anxious, tense, confused, dissatisfied]
- 赢家抽取：[frustrated, angry, impatient, overwhelmed, anxious]
- 最终极性：negative→negative。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_UNCERTAINTY_HEDGE, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_LIPS_PRESSED
- 图候选：hesitant, sceptical, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5266627363134919}, {"state": "AGC_INCONGRUENT", "relative_support": 0.473337263686508}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8914215803071404}, {"state": "AEX_EXPECTED", "relative_support": 0.10857841969285965}], "APP_AGENCY": [], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8917393705440676}, {"state": "ACT_CERTAIN", "relative_support": 0.10826062945593233}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.6206037769309048}, {"state": "ACP_LOW", "relative_support": 0.3793962230690952}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/cXypl4FnoZo_16.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is impatience, stress, dissatisfaction, confusion.|
|long_graph_dataset_best|1.0000|The character's emotional state is anxiety, agitation, frustration, helplessness.|

## 87. CMUMOSI / iiK8YX8oH1E_11 — 赢家零/错，其他权重经常命中/对

- 参考：1.0；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：1.0000→0.0000；50权重零/错17次、满/对33次。
- 模型字幕：SO I WILL GIVE IT POINTS FOR NOT BEING EXACTLY LIKE MY BEST FRIENDS WEDDING EVEN AT THE TRAILER SETS IT UP THAT WAY
- 中文：所以我会给它一些分数，因为它并不完全像我的朋友的婚礼，即使预告片的设置就是这样。
- 起点回答：The character's emotional state is excited, enthusiastic.
- 赢家回答：The character's emotional state is excited, enthusiastic, dissatisfied, anxious, disappointed, stressed.
- 起点抽取：[excited, enthusiastic]
- 赢家抽取：[excited, enthusiastic, dissatisfied, anxious, disappointed, stressed]
- 最终极性：positive→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER, AUD_SPEECH_RATE_REL_FAST, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_RAISED
- 图候选：disappointed, anger, appalled（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9958607666377626}, {"state": "AGR_RELEVANT", "relative_support": 0.004139233362237502}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.564709212862891}, {"state": "AGC_MIXED", "relative_support": 0.2564610454468322}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7069671709065317}, {"state": "AEX_EXPECTED", "relative_support": 0.2930328290934683}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7431204556615383}, {"state": "AAG_SELF", "relative_support": 0.1739066146568229}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.59126506314572}, {"state": "ACT_UNCERTAIN", "relative_support": 0.4087349368542799}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7314455118999736}, {"state": "ACP_HIGH", "relative_support": 0.26855448810002636}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/iiK8YX8oH1E_11.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is neutral.|
|long_graph_dataset_best|1.0000|The character's emotional state is positive.|

## 88. CMUMOSI / wMbj6ajWbic_16 — 赢家零/错，其他权重经常命中/对

- 参考：-0.4；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：1.0000→0.0000；50权重零/错23次、满/对27次。
- 模型字幕：BUT YOU KNOW THIS MOVIE UM THIS REALLY UM WOULDVE MADE UP FOR A DISAPPOINTMENT THAT IT HAD A TERMINATOR SALVATION
- 中文：但你知道这部电影，嗯，如果它是《终结者：救世主》，那真的会弥补之前的失望。
- 起点回答：The character's emotional state is disappointed, dissatisfaction, negative, gloomy.
- 赢家回答：The character's emotional state is excited, enthusiastic, positive.
- 起点抽取：[dissatisfied, disappointed, negative, gloomy]
- 赢家抽取：[excited, enthusiastic, positive]
- 最终极性：negative→positive。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：anger, disappointed, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_MIXED", "relative_support": 0.40294207328536524}, {"state": "AGC_INCONGRUENT", "relative_support": 0.30035169199022355}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9155441294424855}, {"state": "AEX_EXPECTED", "relative_support": 0.08445587055751445}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7610691679825644}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.12750925287530293}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7272522659179937}, {"state": "ACT_CERTAIN", "relative_support": 0.2727477340820063}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.704807407183304}, {"state": "ACP_LOW", "relative_support": 0.2951925928166959}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/wMbj6ajWbic_16.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is disappointment, frustration, enthusiasm, passion.|
|long_graph_dataset_best|0.0000|The character's emotional state is disappointment, excitement, enthusiasm, anxiety.|

## 89. CMUMOSI / ob23OKe5a9Q_5 — 赢家零/错，其他权重经常命中/对

- 参考：-1.8；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：1.0000→0.0000；50权重零/错19次、满/对31次。
- 模型字幕：THAT UM I GUESS THE ONLY OTHER PROBLEM I HAD WITH IT WAS THAT UM THE JOKES WERE REALLY CHEESY
- 中文：我想我遇到的唯一其他问题就是，嗯，里面的笑话真的很俗气。
- 起点回答：The character's emotional state is disappointment, dissatisfaction, humor, irony.
- 赢家回答：The character's emotional state is disappointment, dissatisfaction, disdain, irony, humor, excitement, happiness, enthusiasm.
- 起点抽取：[disappointment, dissatisfaction, humor, irony]
- 赢家抽取：[disappointment, dissatisfaction, disdain, irony, humor, excitement, happiness, enthusiasm]
- 最终极性：negative→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT, VIS_HEAD_LOWERED
- 图候选：ashamed, disappointed, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5069727474991077}, {"state": "AGC_CONGRUENT", "relative_support": 0.38960238599383673}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7276591768562936}, {"state": "AEX_UNEXPECTED", "relative_support": 0.2723408231437064}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.46554310040583863}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3676190305990534}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5153700015274492}, {"state": "ACT_UNCERTAIN", "relative_support": 0.48462999847255084}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7546635720567378}, {"state": "ACP_HIGH", "relative_support": 0.2453364279432621}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/ob23OKe5a9Q_5.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is calm, satisfied, neutral.|
|long_graph_dataset_best|1.0000|The character's emotional state is negative, dissatisfaction, disappointment.|

## 90. CMUMOSI / c7UH_rxdZv4_9 — 赢家满/对，其他权重经常不满/错

- 参考：-0.4；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：1.0000→1.0000；50权重零/错34次、满/对16次。
- 模型字幕：AND UNLIKE OTHER FILMS FOR THEY KIND OF A NARCISSTIC XXX BOY BUT THEY BRING SOMETHING TO THE TABLE YOU KNOW
- 中文：与其他电影不同，他们有一种自恋的XXX男孩，但他们带来了一些你知道的东西。
- 起点回答：The character's emotional state is neutral, casual, evaluative.
- 赢家回答：The character's emotional state is complex, fear, anxiety, nervousness, dissatisfaction, disapproval, disagreement, misunderstanding.
- 起点抽取：[neutral, casual, evaluative]
- 赢家抽取：[fear, anxiety, nervousness, dissatisfaction, disapproval, disagreement, misunderstanding]
- 最终极性：neutral→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_CONTRAST_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：disappointed, ashamed, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.4214446429762446}, {"state": "AGC_MIXED", "relative_support": 0.3225363099087563}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7611648881295399}, {"state": "AEX_UNEXPECTED", "relative_support": 0.23883511187046003}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4730367495521431}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.40253128345718736}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8267235618796339}, {"state": "ACT_UNCERTAIN", "relative_support": 0.1732764381203662}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6047392689291535}, {"state": "ACP_HIGH", "relative_support": 0.3952607310708464}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/c7UH_rxdZv4_9.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is anxious, tense, overwhelmed, excited, passionate.|
|long_graph_dataset_best|0.0000|The character's emotional state is positive, evaluative, affirming, praising.|

## 91. CMUMOSI / ob23OKe5a9Q_9 — 赢家满/对，其他权重经常不满/错

- 参考：-1.4；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：1.0000→1.0000；50权重零/错30次、满/对20次。
- 模型字幕：BEYOND THIS AGE THE PROBLEM I HAD WITH THE MOVIE THEATRE IS THERE WERE KIDS CRYING THE WHOLE TIME AND WHISPERING XXX DOES BABY CRYING GET ON YOUR NERVES EVER IF IT DOES WOULDNT RECOMMEND GOING TO THIS MOVIE CUZ THERES A BUNCH OF KIDS OR SNEAK INTO A REALLY LATE SHOWING CUZ I DONT THINK KIDS ARE GOING TO BE OUT THAT LATE BUT THATS THE ONLY PROBLEM I HAD WITH IT
- 中文：超过这个年龄，我对电影院的问题是有孩子一直在哭泣和低语。如果婴儿的哭声让你感到烦躁，我不建议你去看这部电影，因为那里有一群孩子。或者你可以选择在很晚的时候偷偷进去看，因为我不认为孩子们会那么晚出来。但这是我对它唯一的问题。
- 起点回答：The character's emotional state is bothered, inconvenienced, dissatisfied.
- 赢家回答：The character's emotional state is annoyance, dissatisfaction, irritation.
- 起点抽取：[bothered, inconvenienced, dissatisfied]
- 赢家抽取：[annoyance, dissatisfaction, irritation]
- 最终极性：negative→negative。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.4801048727099917}, {"state": "AGC_CONGRUENT", "relative_support": 0.265978323628824}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5203687064270262}, {"state": "AEX_UNEXPECTED", "relative_support": 0.47963129357297374}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4470164164626189}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.34264837255996944}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5044806569589505}, {"state": "ACT_UNCERTAIN", "relative_support": 0.4955193430410495}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7637709088105484}, {"state": "ACP_HIGH", "relative_support": 0.23622909118945146}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/ob23OKe5a9Q_9.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is dissatisfaction, annoyance, humor, jest.|
|long_graph_dataset_best|1.0000|The character's emotional state is annoyance, dissatisfaction.|

## 92. CMUMOSI / c7UH_rxdZv4_10 — 赢家满/对，其他权重经常不满/错

- 参考：0.8；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：1.0000→1.0000；50权重零/错27次、满/对23次。
- 模型字幕：THERES SOMETHING THAT JUST KIND OF MAKES THAM SO SL SLIGHTLY ENDEARING EVEN THOUGH THEYRE KIND OF THE JACK ASS YOU KNOW
- 中文：有些东西使他们稍微讨人喜欢，即使他们有点像你知道的那种讨厌鬼。
- 起点回答：The character's emotional state is complex, contradictory, humor, annoyance, liking, appreciation.
- 赢家回答：The character's emotional state is sarcastic, mocking, amused, cheerful.
- 起点抽取：[complex, contradictory, humor, annoyance, liking, appreciation]
- 赢家抽取：[sarcastic, mocking, amused, cheerful]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.47582127400029434}, {"state": "AGC_INCONGRUENT", "relative_support": 0.3348396801424369}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7820730398301305}, {"state": "AEX_UNEXPECTED", "relative_support": 0.21792696016986948}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.559402277121441}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3119261632758912}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8460605303101894}, {"state": "ACT_UNCERTAIN", "relative_support": 0.15393946968981076}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5105534920496557}, {"state": "ACP_LOW", "relative_support": 0.48944650795034433}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/c7UH_rxdZv4_10.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is complex, irony, humor, contradiction, praise, mockery.|
|long_graph_dataset_best|1.0000|The character's emotional state is complex, negative emotions, humor, sarcasm, enthusiasm.|

## 93. CMUMOSI / tmZoasNr4rU_12 — 相对自身起点改善

- 参考：-2.2；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：0.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：BUT I JUST COULDNT FIND IT FUNNY
- 中文：但我就是觉得它不好笑
- 起点回答：The character's emotional state is disbelieving, perplexed, lack of understanding, enjoyment.
- 赢家回答：The character's emotional state is unable to find humor, dissatisfaction, disappointment.
- 起点抽取：[disbelieving, perplexed, lack of understanding, enjoyment]
- 赢家抽取：[dissatisfied, disappointed]
- 最终极性：positive→negative。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_MOUTH_CORNERS_DOWN, VIS_HEAD_LOWERED
- 图候选：disappointed, anger, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.608765694948791}, {"state": "AGC_MIXED", "relative_support": 0.34733035885209046}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7153037103994265}, {"state": "AEX_UNEXPECTED", "relative_support": 0.28469628960057347}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.49820170644853956}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3372353915332148}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7866518993001435}, {"state": "ACT_UNCERTAIN", "relative_support": 0.21334810069985655}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9929741727100365}, {"state": "ACP_HIGH", "relative_support": 0.007025827289963363}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/tmZoasNr4rU_12.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is neutral.|
|long_graph_dataset_best|1.0000|The character's emotional state is puzzled, confused, unable to understand, intense negative emotions, overwhelmed, stressed.|

## 94. CMUMOSI / cXypl4FnoZo_1 — 相对自身起点改善

- 参考：1.0；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：0.0000→1.0000；50权重零/错10次、满/对40次。
- 模型字幕：XXX SEEING RED RIDING HOOD FOR A REALLY LONG TIME
- 中文：XXX长时间以来一直在看红帽小女孩
- 起点回答：The character's emotional state is calm, objective.
- 赢家回答：The character's emotional state is fondness, admiration, appreciation.
- 起点抽取：[calm, objective]
- 赢家抽取：[fondness, admiration, appreciation]
- 最终极性：neutral→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, AUD_INTONATION_RISING, VIS_LIPS_PRESSED
- 图候选：anxious, care, appalled（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.956906669713294}, {"state": "AEX_EXPECTED", "relative_support": 0.04309333028670605}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8976307445502134}, {"state": "AAG_SELF", "relative_support": 0.10236925544978663}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7825000833302194}, {"state": "ACT_CERTAIN", "relative_support": 0.21749991666978064}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/cXypl4FnoZo_1.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is excited, satisfied.|
|long_graph_dataset_best|0.0000|The character's emotional state is neutral.|

## 95. CMUMOSI / nzpVDcQ0ywM_20 — 相对自身起点改善

- 参考：0.2；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：0.0000→1.0000；50权重零/错35次、满/对15次。
- 模型字幕：HE IS AVERAGE
- 中文：他是普通的
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is light-hearted, humorous, positive.
- 起点抽取：[neutral]
- 赢家抽取：[light-hearted, humorous, positive]
- 最终极性：neutral→positive。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, manic（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.9297086827202538}, {"state": "AGC_INCONGRUENT", "relative_support": 0.05212125072237716}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7066108504926868}, {"state": "AEX_EXPECTED", "relative_support": 0.2933891495073131}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5354102154384869}, {"state": "AAG_OTHER", "relative_support": 0.3334993474729175}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.902097064753908}, {"state": "ACT_CERTAIN", "relative_support": 0.09790293524609188}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8884824488845545}, {"state": "ACP_LOW", "relative_support": 0.11151755111544549}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/nzpVDcQ0ywM_20.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is neutral, calm.|
|long_graph_dataset_best|1.0000|The character's emotional state is neutral, lighthearted, positive.|

## 96. CMUMOSI / jUzDDGyPkXU_20 — 相对自身起点恶化

- 参考：-2.2；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：1.0000→0.0000；50权重零/错1次、满/对49次。
- 模型字幕：EVERYTHING THEY SAY JUST SOUNDS SO FUCKING STUPID
- 中文：他们说的每一句话听起来都特么的愚蠢
- 起点回答：The character's emotional state is anger, dissatisfaction, negative emotions.
- 赢家回答：The character's emotional state is anger, frustration, sadness, happiness, excitement.
- 起点抽取：[anger, dissatisfaction, negative_emotions]
- 赢家抽取：[anger, frustration, sadness, happiness, excitement]
- 最终极性：negative→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：disappointed, anger, ashamed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.6035723547960805}, {"state": "AGC_CONGRUENT", "relative_support": 0.35714602941479123}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8409314473788024}, {"state": "AEX_UNEXPECTED", "relative_support": 0.1590685526211976}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4758105245778318}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3503485701046823}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5754901289729667}, {"state": "ACP_HIGH", "relative_support": 0.4245098710270333}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/jUzDDGyPkXU_20.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is anger, frustration, disappointment.|
|long_graph_dataset_best|1.0000|The character's emotional state is anger, dissatisfaction.|

## 97. CMUMOSI / nzpVDcQ0ywM_5 — 相对自身起点恶化

- 参考：-0.4；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：1.0000→0.0000；50权重零/错43次、满/对7次。
- 模型字幕：I FEEL LIKE IT ALMOST SHOULD HAVE HAD A G RATING
- 中文：我觉得它几乎应该被评为G级。
- 起点回答：The character's emotional state is excited, tense, excited.
- 赢家回答：The character's emotional state is humor, jest, excitement, enthusiasm.
- 起点抽取：[excited, tense]
- 赢家抽取：[humor, jest, excitement, enthusiasm]
- 最终极性：negative→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, TXT_UNCERTAINTY_HEDGE, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：skeptical, depressed, disappointed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7133659067716781}, {"state": "AGC_CONGRUENT", "relative_support": 0.19752104775661236}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6614552467864624}, {"state": "AEX_UNEXPECTED", "relative_support": 0.3385447532135376}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5124377590866832}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3545999443137042}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7260257071786772}, {"state": "ACT_CERTAIN", "relative_support": 0.27397429282132274}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8381012718380212}, {"state": "ACP_HIGH", "relative_support": 0.16189872816197878}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/nzpVDcQ0ywM_5.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is excited, enthusiastic, amused.|
|long_graph_dataset_best|1.0000|The character's emotional state is anxious, tense, overwhelmed, stressed, uncertain, concerned, hopeful, expectant.|

## 98. CMUMOSI / yDtzw_Y-7RU_23 — 相对自身起点恶化

- 参考：2.2；赢家：from_50_epoch_57_CMUMOSI；起点epoch50。
- 质量：1.0000→0.0000；50权重零/错1次、满/对49次。
- 模型字幕：UM I ENJOYED MYSELF IN IT YOU MIGHT AS WELL
- 中文：嗯，我在其中过得很开心，你也可能会喜欢的。
- 起点回答：The character's emotional state is enthusiastic, passionate, excited, urgent.
- 赢家回答：The character's emotional state is sarcastic, provocative, ironic.
- 起点抽取：[enthusiastic, passionate, excited, urgent]
- 赢家抽取：[sarcastic, provocative, ironic]
- 最终极性：positive→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, hopeful, manic（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.9740827926094724}, {"state": "AGC_MIXED", "relative_support": 0.025917207390527695}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5219013894006439}, {"state": "AEX_UNEXPECTED", "relative_support": 0.47809861059935616}], "APP_AGENCY": [], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.925725998278911}, {"state": "ACT_UNCERTAIN", "relative_support": 0.07427400172108896}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosi-process/subvideo/yDtzw_Y-7RU_23.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is excited, enthusiastic, positive.|
|long_graph_dataset_best|1.0000|The character's emotional state is positive, enthusiastic.|

## 99. CMUMOSEI / wnL3ld9bM2o_2 — 50权重持续错误/零命中

- 参考：0.3333333432674408；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：People go from project to project or day job to day job rather than having a job
- 中文：人们从一个项目转到另一个项目，或者从一份日常工作转到另一份日常工作，而不是拥有一份工作。
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is neutral.
- 起点抽取：[neutral]
- 赢家抽取：[neutral]
- 最终极性：neutral→neutral。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED
- 图候选：helpless, depressed, apathetic（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_MIXED", "relative_support": 0.5590847386426748}, {"state": "AGC_INCONGRUENT", "relative_support": 0.2426027861034923}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8076669090500024}, {"state": "AEX_UNEXPECTED", "relative_support": 0.19233309094999762}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5524945277071993}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.44750547229280074}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6881133038773953}, {"state": "ACT_UNCERTAIN", "relative_support": 0.31188669612260467}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7081838835538155}, {"state": "ACP_HIGH", "relative_support": 0.29181611644618455}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/wnL3ld9bM2o_2.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is neutral.|
|long_graph_dataset_best|0.0000|The character's emotional state is neutral, objective.|

## 100. CMUMOSEI / BRSyH6yfDLk_3 — 50权重持续错误/零命中

- 参考：1.3333333730697632；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：Fuckin hypocrite i had not seen as many Indians in New Delhi as I saw in New York Subway, Dunkin Donuts, Hudson news, Hudson Deli
- 中文：该输入含有不适当的言辞，无法提供翻译。
- 起点回答：The character's emotional state is excited, passionate, dissatisfied.
- 赢家回答：The character's emotional state is negative, anger, anxiety, stress, dissatisfaction, criticism.
- 起点抽取：[excited, passionate, dissatisfied]
- 赢家抽取：[negative, anger, anxiety, stress, dissatisfaction, criticism]
- 最终极性：negative→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, AUD_SPEECH_RATE_REL_FAST, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_RISING, AUD_LAUGHTER_PRESENT, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：anger, disappointed, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.6638147673987246}, {"state": "AGC_CONGRUENT", "relative_support": 0.27485174506012056}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9361229784333596}, {"state": "AEX_EXPECTED", "relative_support": 0.06387702156664042}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6215172016388553}, {"state": "AAG_SELF", "relative_support": 0.2171334276530422}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7988570586191672}, {"state": "ACT_CERTAIN", "relative_support": 0.20114294138083275}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7007680334443286}, {"state": "ACP_HIGH", "relative_support": 0.29923196655567136}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/BRSyH6yfDLk_3.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is angry, frustrated, mocking, ironic.|
|long_graph_dataset_best|0.0000|The character's emotional state is anger, frustration, hostility.|

## 101. CMUMOSEI / 200941_12 — 50权重持续错误/零命中

- 参考：-1.3333333730697632；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：It was definitely a comedy and I guess if you're a true Simpsons fan you're gonna wanna see the movie
- 中文：这绝对是一部喜剧，我猜如果你是一个真正的辛普森迷，你一定想看这部电影。
- 起点回答：The character's emotional state is excited, enthusiastic, positive.
- 赢家回答：The character's emotional state is positive, excited.
- 起点抽取：[excited, enthusiastic, positive]
- 赢家抽取：[positive, excited]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：hopeful, joy, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7802662183213084}, {"state": "AGC_MIXED", "relative_support": 0.19092775449445715}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9439710322308269}, {"state": "AEX_UNEXPECTED", "relative_support": 0.05602896776917304}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6389510853463007}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3555963259454403}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7881077079877972}, {"state": "ACT_UNCERTAIN", "relative_support": 0.21189229201220278}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8780794469829214}, {"state": "ACP_LOW", "relative_support": 0.12192055301707855}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/200941_12.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is enthusiastic, excited, passionate.|
|long_graph_dataset_best|0.0000|The character's emotional state is excited, enthusiastic, positive.|

## 102. CMUMOSEI / 8VhVf0TbjDA_1 — 50权重持续正确/满命中

- 参考：1.3333333730697632；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：As the West Sub-Area Advisory Managing Partner of Ernst &amp; Young LLP, Blair’s leadership has resulted in her sub-area gaining the number one rankings for sales performance, revenue growth and profitability within Ernst &amp; Young LLP, and in her personally being voted “best in class” by her colleagues for her exemplary and strategic leadership.
- 中文：作为安永会计师事务所西部分区咨询管理合伙人，布莱尔的领导力使得她所负责的分区在销售业绩、收入增长和盈利能力方面获得了安永会计师事务所的第一名，并且她个人因其出色和战略性的领导力被同事们评选为“最佳班级”。
- 起点回答：The character's emotional state is satisfaction, pride.
- 赢家回答：The character's emotional state is excited, enthusiastic, proud, confident.
- 起点抽取：[satisfaction, pride]
- 赢家抽取：[excited, enthusiastic, proud, confident]
- 最终极性：positive→positive。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER, TXT_EXPLICIT_SUCCESS_OUTCOME, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_VOICE_TENSE, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7935771845747831}, {"state": "AGC_INCONGRUENT", "relative_support": 0.1139322415037593}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7025811807031168}, {"state": "AEX_EXPECTED", "relative_support": 0.2974188192968831}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6612653153263921}, {"state": "AAG_SELF", "relative_support": 0.3387346846736079}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.506885108855041}, {"state": "ACT_UNCERTAIN", "relative_support": 0.493114891144959}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.9474503416251037}, {"state": "ACP_LOW", "relative_support": 0.05254965837489629}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/8VhVf0TbjDA_1.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is positive, recognition, appreciation.|
|long_graph_dataset_best|1.0000|The character's emotional state is confidence, satisfaction, pride, joy, fulfillment.|

## 103. CMUMOSEI / 23656_21 — 50权重持续正确/满命中

- 参考：-0.3333333432674408；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：So if you're a younger kid then maybe watch it
- 中文：所以如果你是一个年轻的孩子，那么也许可以看一下。
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is neutral.
- 起点抽取：[neutral]
- 赢家抽取：[neutral]
- 最终极性：neutral→neutral。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_UNCERTAINTY_HEDGE, TXT_DESIRE_NEED, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_EYES_SQUINTED, VIS_HEAD_LOWERED
- 图候选：delightful, curious, hesitant（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6355302654718505}, {"state": "AGC_MIXED", "relative_support": 0.23451894513785357}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6277457571122271}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.372254242887773}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8235548260055245}, {"state": "ACT_CERTAIN", "relative_support": 0.17644517399447537}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.514332110142511}, {"state": "ACP_HIGH", "relative_support": 0.48566788985748893}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/23656_21.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is neutral, cautious.|
|long_graph_dataset_best|1.0000|The character's emotional state is neutral.|

## 104. CMUMOSEI / vGkIaClHKDg_10 — 50权重持续正确/满命中

- 参考：0.3333333432674408；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：Online Marketing Often times, word-of-mouth is not enough, and you need to find new customers.
- 中文：在线营销 往往情况下，口碑传播是不够的，你需要找到新的客户。
- 起点回答：The character's emotional state is positive, excitement, enthusiasm.
- 赢家回答：The character's emotional state is positive, confident.
- 起点抽取：[positive, excitement, enthusiasm]
- 赢家抽取：[positive, confident]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_DESIRE_NEED, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：hopeful, joy, disappointed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9827404761602745}, {"state": "AGR_RELEVANT", "relative_support": 0.017259523839725475}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.538688321452623}, {"state": "AGC_INCONGRUENT", "relative_support": 0.4409533830772897}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5570807939492224}, {"state": "AEX_UNEXPECTED", "relative_support": 0.4429192060507776}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5236897554491754}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.26492408368529713}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5317798343352141}, {"state": "ACT_UNCERTAIN", "relative_support": 0.4682201656647858}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5213461809995502}, {"state": "ACP_LOW", "relative_support": 0.47865381900044973}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/vGkIaClHKDg_10.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is positive, energetic.|
|long_graph_dataset_best|1.0000|The character's emotional state is positive, enthusiastic, urgent.|

## 105. CMUMOSEI / GK-Pprzh0t0_5 — 赢家零/错，其他权重经常命中/对

- 参考：-0.6666666865348816；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：0.0000→0.0000；50权重零/错14次、满/对36次。
- 模型字幕：How can we, in the United States, help stop the world's worst humanitarian crisis, thousands of miles away?
- 中文：我们在美国如何帮助停止数千英里之外的世界上最严重的人道主义危机？
- 起点回答：The character's emotional state is concern, enthusiasm, urgency, responsibility.
- 赢家回答：The character's emotional state is concern, responsibility, urgency, frustration, determination, commitment.
- 起点抽取：[concern, enthusiasm, urgency, responsibility]
- 赢家抽取：[concern, responsibility, urgency, frustration, determination, commitment]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED
- 图候选：disappointed, ashamed, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9148112746120972}, {"state": "AGR_RELEVANT", "relative_support": 0.08518872538790273}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.6358939788783294}, {"state": "AGC_CONGRUENT", "relative_support": 0.3074392610163928}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.959354966681441}, {"state": "AEX_UNEXPECTED", "relative_support": 0.04064503331855892}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5254175354598426}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.36300696163450585}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8168097901689617}, {"state": "ACT_UNCERTAIN", "relative_support": 0.18319020983103831}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6037408284242983}, {"state": "ACP_HIGH", "relative_support": 0.39625917157570173}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/GK-Pprzh0t0_5.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is urgency, concern, frustration, confusion, resolve.|
|long_graph_dataset_best|1.0000|The character's emotional state is concerned, determined, tense, anxious, pressured, responsible, sense_of_duty.|

## 106. CMUMOSEI / ZKErPftd--w_7 — 赢家零/错，其他权重经常命中/对

- 参考：0.6666666865348816；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：0.0000→0.0000；50权重零/错25次、满/对25次。
- 模型字幕：But how on earth did that happen
- 中文：但是这到底是怎么发生的呢
- 起点回答：The character's emotional state is surprised, curious, puzzled.
- 赢家回答：The character's emotional state is confused, curious, surprised, satisfied, unhappy.
- 起点抽取：[surprised, curious, puzzled]
- 赢家抽取：[confused, curious, surprised, unsatisfied]
- 最终极性：neutral→negative。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, manic（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5803174567787776}, {"state": "AGC_MIXED", "relative_support": 0.30286866610692575}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8140938180933774}, {"state": "AEX_EXPECTED", "relative_support": 0.18590618190662253}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6334374575879865}, {"state": "AAG_SELF", "relative_support": 0.3665625424120135}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8297141230353803}, {"state": "ACT_CERTAIN", "relative_support": 0.1702858769646196}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.9004209714254743}, {"state": "ACP_LOW", "relative_support": 0.09957902857452557}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/ZKErPftd--w_7.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is curiosity, surprise, excitement, tension.|
|long_graph_dataset_best|0.0000|The character's emotional state is confusion, surprise.|

## 107. CMUMOSEI / SKTyBOhDX6U_1 — 赢家零/错，其他权重经常命中/对

- 参考：-0.3333333432674408；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：0.0000→0.0000；50权重零/错19次、满/对31次。
- 模型字幕：Whether we acknowledge our role as a world leader in disability rights are not, other countries still look to the US for leadership on human rights issues
- 中文：无论我们是否承认自己在残疾权利方面的世界领导地位，其他国家仍然将美国视为人权问题上的领导者。
- 起点回答：The character's emotional state is serious, focused, concerned, authoritative, professional.
- 赢家回答：The character's emotional state is serious, focused, authoritative, confident, passionate, determined.
- 起点抽取：[serious, focused, concerned, authoritative, professional]
- 赢家抽取：[serious, focused, authoritative, confident, passionate, determined]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, AUD_SPEECH_RATE_REL_FAST, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9822969079269414}, {"state": "AGR_RELEVANT", "relative_support": 0.017703092073058667}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5566159012728391}, {"state": "AGC_MIXED", "relative_support": 0.32283602484542995}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.5449992500956994}, {"state": "AEX_EXPECTED", "relative_support": 0.45500074990430067}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4105242520703618}, {"state": "AAG_OTHER", "relative_support": 0.3283527454064828}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5199633182184422}, {"state": "ACT_UNCERTAIN", "relative_support": 0.4800366817815578}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7842095989046781}, {"state": "ACP_LOW", "relative_support": 0.21579040109532183}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/SKTyBOhDX6U_1.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is serious, confident, authoritative, important.|
|long_graph_dataset_best|0.0000|The character's emotional state is confident, authoritative, passionate, critical, serious.|

## 108. CMUMOSEI / RVC8l5hf2Eg_12 — 赢家满/对，其他权重经常不满/错

- 参考：0.6666666865348816；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：0.0000→1.0000；50权重零/错45次、满/对5次。
- 模型字幕：-Rounding out the top five spots were Target – Wegmen’s – Whole Foods – and Ahold.
- 中文：排名前五的位置分别是Target、Wegmen's、Whole Foods和Ahold。
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is positive, enthusiastic, passionate, confident, authoritative.
- 起点抽取：[]
- 赢家抽取：[positive, enthusiastic, passionate, confident, authoritative]
- 最终极性：neutral→positive。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_LIPS_PRESSED
- 图候选：delightful, hopeful, acceptance（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.39809125517836347}, {"state": "AGC_MIXED", "relative_support": 0.3648836020976866}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5471367051939068}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.45286329480609333}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8318954934392974}, {"state": "ACT_UNCERTAIN", "relative_support": 0.16810450656070255}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.867403476754367}, {"state": "ACP_HIGH", "relative_support": 0.1325965232456329}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/RVC8l5hf2Eg_12.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is neutral.|
|long_graph_dataset_best|0.0000|The character's emotional state is neutral.|

## 109. CMUMOSEI / 94481_10 — 赢家满/对，其他权重经常不满/错

- 参考：-0.6666666865348816；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：0.0000→1.0000；50权重零/错30次、满/对20次。
- 模型字幕：(uhh) But it gives you a little kind of a taste of history
- 中文：(嗯) 但它给你一点点历史的味道
- 起点回答：The character's emotional state is excited, anticipatory, nervous.
- 赢家回答：The character's emotional state is thoughtful, contemplative, reflective, serious, historical, somber.
- 起点抽取：[excited, anticipatory, nervous]
- 赢家抽取：[thoughtful, contemplative, reflective, serious, somber]
- 最终极性：positive→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_HEAD_LOWERED
- 图候选：depressed, ashamed, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_MIXED", "relative_support": 0.6422592049250995}, {"state": "AGC_INCONGRUENT", "relative_support": 0.27227110431776264}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7969227026055823}, {"state": "AEX_UNEXPECTED", "relative_support": 0.2030772973944178}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4936755229143598}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.45148157130298566}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.694886082115745}, {"state": "ACT_UNCERTAIN", "relative_support": 0.30511391788425496}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9824096719881904}, {"state": "ACP_HIGH", "relative_support": 0.01759032801180951}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/94481_10.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is excited, anticipatory, tense, excited.|
|long_graph_dataset_best|0.0000|The character's emotional state is enthusiastic, passionate.|

## 110. CMUMOSEI / ktblaVOnFVE_5 — 赢家满/对，其他权重经常不满/错

- 参考：0.3333333432674408；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：1.0000→1.0000；50权重零/错37次、满/对13次。
- 模型字幕：Because I've always believed that both are equally as important, but generally, I try to be more logical than impulsive
- 中文：因为我一直相信两者同等重要，但一般来说，我尽量更加理性而不冲动。
- 起点回答：The character's emotional state is confident, self-aware.
- 赢家回答：The character's emotional state is self-doubt, rational thought, uncertainty, confidence, anxiety, nervousness, excitement, enthusiasm.
- 起点抽取：[confident, self-aware]
- 赢家抽取：[self-doubt, rational thought, uncertainty, confidence, anxiety, nervousness, excitement, enthusiasm]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9593562655602571}, {"state": "AGR_RELEVANT", "relative_support": 0.040643734439742916}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5578460976282217}, {"state": "AGC_MIXED", "relative_support": 0.30833024862323105}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7410096483580644}, {"state": "AEX_EXPECTED", "relative_support": 0.2589903516419356}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7624211777710994}, {"state": "AAG_SELF", "relative_support": 0.23757882222890053}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6345139308353018}, {"state": "ACT_CERTAIN", "relative_support": 0.3654860691646981}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8799606048783479}, {"state": "ACP_LOW", "relative_support": 0.12003939512165208}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/ktblaVOnFVE_5.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is happiness, amusement, anxiety, stress, introspection, contemplation.|
|long_graph_dataset_best|1.0000|The character's emotional state is confident, self-affirming.|

## 111. CMUMOSEI / DnBHq5I52LM_0 — 相对自身起点改善

- 参考：-1.6666666269302368；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：0.0000→1.0000；50权重零/错20次、满/对30次。
- 模型字幕：We need tax cuts and tax reform now
- 中文：我们现在需要减税和税制改革
- 起点回答：The character's emotional state is discontent, demand, expectation, urgency, excitement.
- 赢家回答：The character's emotional state is excitement, agitation, frustration, agitation, hope, dissatisfaction, expectation.
- 起点抽取：[discontent, demand, expectation, urgency, excitement]
- 赢家抽取：[excitement, agitation, frustration, hope, dissatisfaction, expectation]
- 最终极性：positive→mixed。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_DESIRE_NEED, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：anxious, hopeful, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.9111313270232878}, {"state": "AGC_INCONGRUENT", "relative_support": 0.08886867297671217}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7563043396834215}, {"state": "AEX_EXPECTED", "relative_support": 0.2436956603165785}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5282981214843053}, {"state": "AAG_SELF", "relative_support": 0.4717018785156947}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.994430522377807}, {"state": "ACT_CERTAIN", "relative_support": 0.005569477622192933}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/DnBHq5I52LM_0.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is urgent, anxious, concerned, hopeful.|
|long_graph_dataset_best|1.0000|The character's emotional state is frustrated, annoyed, anxious, agitated, hopeful, enthusiastic.|

## 112. CMUMOSEI / yUqNp-poh9M_1 — 相对自身起点改善

- 参考：1.0；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：0.0000→1.0000；50权重零/错24次、满/对26次。
- 模型字幕：The government of Canada will be fixed
- 中文：加拿大政府将被修复。
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is positive, optimistic.
- 起点抽取：[]
- 赢家抽取：[positive, optimistic]
- 最终极性：neutral→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_EXPLICIT_SUCCESS_OUTCOME, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN
- 图候选：proud, joy, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.772162635042538}, {"state": "AGC_MIXED", "relative_support": 0.14014414024266436}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.607361892227054}, {"state": "AEX_UNEXPECTED", "relative_support": 0.39263810777294605}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6241946636910862}, {"state": "AAG_OTHER", "relative_support": 0.21714803923112214}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5051068829517212}, {"state": "ACT_UNCERTAIN", "relative_support": 0.49489311704827876}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8009018049838086}, {"state": "ACP_LOW", "relative_support": 0.19909819501619136}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/yUqNp-poh9M_1.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is neutral.|
|long_graph_dataset_best|1.0000|The character's emotional state is optimistic, confident, enthusiastic.|

## 113. CMUMOSEI / 221153_9 — 相对自身起点改善

- 参考：0.3333333432674408；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：0.0000→1.0000；50权重零/错44次、满/对6次。
- 模型字幕：(umm) It is rated R for some strong violence (uhh) during the robbery
- 中文：（嗯）这部电影被评为限制级，因为在抢劫过程中有一些强烈的暴力场面（嗯）。
- 起点回答：The character's emotional state is concentration, thoughtfulness, stress.
- 赢家回答：The character's emotional state is serious, professional, enthusiastic, humorous, excited, anxious, tense.
- 起点抽取：[concentration, thoughtfulness, stress]
- 赢家抽取：[serious, professional, enthusiastic, humorous, excited, anxious, tense]
- 最终极性：negative→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：ashamed, pity, depressed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5015728681340492}, {"state": "AGC_CONGRUENT", "relative_support": 0.3455517503906725}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8044730267931037}, {"state": "AEX_UNEXPECTED", "relative_support": 0.19552697320689622}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4934849557487936}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3898217308568494}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7736197318964575}, {"state": "ACT_UNCERTAIN", "relative_support": 0.2263802681035424}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6046685514946957}, {"state": "ACP_HIGH", "relative_support": 0.3953314485053042}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/221153_9.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is tense, urgent.|
|long_graph_dataset_best|0.0000|The character's emotional state is anxiety, stress, overwhelm.|

## 114. CMUMOSEI / 111881_8 — 相对自身起点恶化

- 参考：0.6666666865348816；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：1.0000→0.0000；50权重零/错49次、满/对1次。
- 模型字幕：This is rated PG so you can watch this with your kids
- 中文：这部电影被评为PG级，所以你可以和你的孩子一起观看。
- 起点回答：The character's emotional state is neutral, positive.
- 赢家回答：The character's emotional state is neutral, focused, calm, emotionally stable, dealing with emotions/trauma.
- 起点抽取：[neutral, positive]
- 赢家抽取：[neutral, focused, calm, emotionally stable]
- 最终极性：positive→neutral。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_MOUTH_CORNERS_DOWN, VIS_LIPS_PRESSED
- 图候选：appreciated, hopeful, confident（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6569069377706781}, {"state": "AGC_MIXED", "relative_support": 0.1822286674665264}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9403574461709219}, {"state": "AEX_UNEXPECTED", "relative_support": 0.05964255382907818}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5980096910051854}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.36199807223927316}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.9318655590597371}, {"state": "ACT_UNCERTAIN", "relative_support": 0.06813444094026283}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.6130970929072507}, {"state": "ACP_LOW", "relative_support": 0.3869029070927492}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/111881_8.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is neutral.|
|long_graph_dataset_best|0.0000|The character's emotional state is neutral.|

## 115. CMUMOSEI / bkX5FOX22Tw_2 — 相对自身起点恶化

- 参考：0.3333333432674408；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：1.0000→0.0000；50权重零/错8次、满/对42次。
- 模型字幕：We also have a new item
- 中文：我们还有一个新项目。
- 起点回答：The character's emotional state is enthusiastic, passionate, excited, optimistic.
- 赢家回答：The character's emotional state is tension, excitement, anticipation, stress, anxiety.
- 起点抽取：[enthusiastic, passionate, excited, optimistic]
- 赢家抽取：[tension, excitement, anticipation, stress, anxiety]
- 最终极性：positive→negative。
- 实际level：1；原因：['weak_or_absent_graph_support']。
- Cue：AUD_INTONATION_RISING
- 图候选：anxious, care, curious（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 1.0}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": []}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/bkX5FOX22Tw_2.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is excited, enthusiastic, positive.|
|long_graph_dataset_best|1.0000|The character's emotional state is excited, anticipatory, nervous.|

## 116. CMUMOSEI / 208592_7 — 相对自身起点恶化

- 参考：-1.0；赢家：from_50_epoch_55_CMUMOSEI；起点epoch50。
- 质量：1.0000→0.0000；50权重零/错40次、满/对10次。
- 模型字幕：(umm) The only good thing about this movie are the songs and the dances
- 中文：这部电影唯一好的地方就是歌曲和舞蹈。
- 起点回答：The character's emotional state is neutral, slightly negative.
- 赢家回答：The character's emotional state is positive, neutral.
- 起点抽取：[neutral, negative]
- 赢家抽取：[positive, neutral]
- 最终极性：negative→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：appreciated, hopeful, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7572122739948843}, {"state": "AGC_MIXED", "relative_support": 0.20910231647320074}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9280098194685912}, {"state": "AEX_UNEXPECTED", "relative_support": 0.0719901805314089}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.550051100497833}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.44260251739718787}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8695386211433941}, {"state": "ACT_UNCERTAIN", "relative_support": 0.13046137885660597}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8294482018193897}, {"state": "ACP_LOW", "relative_support": 0.17055179818061028}]}
- 视频：/ai/sjq/AffectGPT/dataset/cmumosei-process/subvideo_new/208592_7.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is excited, enthusiastic.|
|long_graph_dataset_best|0.0000|The character's emotional state is positive, neutral.|

## 117. SIMS / video_0029_0007 — 50权重持续错误/零命中

- 参考：0.2；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：I'll never have a chance to do this again. I have to blow it all my life
- 中文：以后我再也没有机会干这种事了，这牛我得吹一辈子
- 起点回答：The character's emotional state is despair, resignation, anger, frustration, helplessness, despair.
- 赢家回答：The character's emotional state is disappointment, despair.
- 起点抽取：[despair, resignation, anger, frustration, helplessness]
- 赢家抽取：[disappointment, despair]
- 最终极性：negative→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_HIGH, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_FALLING, AUD_VOICE_TENSE, AUD_VOICE_TREMBLING, AUD_LAUGHTER_PRESENT, AUD_CRYING_SOBBING_PRESENT, VIS_BROWS_FURROWED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, despair, anger（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9783014351161692}, {"state": "AGR_RELEVANT", "relative_support": 0.02169856488383083}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8069073920881962}, {"state": "AGC_CONGRUENT", "relative_support": 0.1283262841184378}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6323676518451451}, {"state": "AEX_EXPECTED", "relative_support": 0.367632348154855}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.39598420995216854}, {"state": "AAG_OTHER", "relative_support": 0.3051729451877484}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6512314131239798}, {"state": "ACT_UNCERTAIN", "relative_support": 0.3487685868760202}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8572449240293825}, {"state": "ACP_HIGH", "relative_support": 0.14275507597061757}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0029_0007.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is anger, sadness, frustration, hopelessness.|
|long_graph_dataset_best|0.0000|The character's emotional state is disappointment, frustration, sadness.|
|base35_A|0.0000|The character's emotional state is despair, helplessness, disappointment.|
|base35_B|0.0000|The emotional state of the character is disappointment, despair, helplessness, regret, anxiety, tension, emotional fragility, sadness.|
|base35_C|0.0000|The character's emotional state is despair, helplessness, negative emotions, emotional fluctuations, stress, anxiety.|
|base35_D|0.0000|The character's emotional state is despair, helplessness, anger.|
|base35_F|0.0000|The character's emotional state is sadness, anger, fear.|
|base35_E|0.0000|The character's emotional state is sadness, despair.|
|graph40_A|0.0000|The character's emotional state is anger, frustration, despair, disappointment, regret, helplessness.|
|graph40_B|0.0000|The character's emotional state is anger, frustration, despair, disappointment, regret.|
|graph40_C|0.0000|The character's emotional state is anger, frustration, despair, disappointment, regret.|
|graph40_D|0.0000|The character's emotional state is anger, frustration, despair, disappointment, regret.|
|graph40_E|0.0000|The character's emotional state is anger, frustration, despair, disappointment, regret.|
|graph40_F|0.0000|The character's emotional state is anger, frustration, despair, disappointment, regret.|
|base35_G|0.0000|The character's emotional state is despair, helplessness, negative emotions, coping difficulties.|
|graph40_G|0.0000|The character's emotional state is anger, frustration, despair, disappointment, regret.|

## 118. SIMS / video_0045_0040 — 50权重持续错误/零命中

- 参考：-0.8；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：He is really a fantasy
- 中文：他真的就是个幻想
- 起点回答：The character's emotional state is enthusiastic, confident, passionate.
- 赢家回答：The character's emotional state is excited, passionate, surprised, appreciative, admiring.
- 起点抽取：[enthusiastic, confident, passionate]
- 赢家抽取：[excited, passionate, surprised, appreciative, admiring]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.9483671160736581}, {"state": "AGC_CONGRUENT", "relative_support": 0.03531660569145275}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5777240085541663}, {"state": "AEX_UNEXPECTED", "relative_support": 0.42227599144583383}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.42864754943321687}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.32704413131055543}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8301886918552174}, {"state": "ACT_UNCERTAIN", "relative_support": 0.16981130814478262}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9937535675587232}, {"state": "ACP_HIGH", "relative_support": 0.006246432441276814}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0045_0040.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is admiration, surprise, positive.|
|long_graph_dataset_best|0.0000|The character's emotional state is positive, energetic, enthusiastic, humorous, teasing.|
|base35_A|0.0000|The character's emotional state is humorous, exaggerated, joyful, positive.|
|base35_B|1.0000|The character's emotional state is anxious, tense, irritable, depressed.|
|base35_C|1.0000|The character's emotional state is anxious, excited, tense, irritable, depressed.|
|base35_D|1.0000|The character's emotional state is sadness, anger, fear.|
|base35_F|0.0000|The character's emotional state is fantasy, exaggerated, humor, positive.|
|base35_E|1.0000|The character's emotional state is negative evaluation, sarcasm, anxiety, stress, contemplation.|
|graph40_A|0.0000|The character's emotional state is fantasy, surprise, admiration.|
|graph40_B|0.0000|The character's emotional state is appreciative, approving.|
|graph40_C|0.0000|The character's emotional state is appreciative, approving, excited, confident.|
|graph40_D|0.0000|The character's emotional state is appreciative, approving, excited, happy.|
|graph40_E|0.0000|The character's emotional state is appreciative, approving, excited, happy.|
|graph40_F|0.0000|The character's emotional state is appreciative, approving, excited, happy.|
|base35_G|1.0000|The character's emotional state is anxious, excited, tense, irritable, sad.|
|graph40_G|0.0000|The character's emotional state is appreciative, approving, excited, happy.|

## 119. SIMS / video_0046_0055 — 50权重持续错误/零命中

- 参考：-0.2；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：Because I used to run in Yangming Mountain, he often appeared in Yangming Mountain when he was a child.
- 中文：因为我以前常常在阳明山跑步，他小时候也常常在阳明山出现
- 起点回答：The character's emotional state is enthusiastic, passionate, positive.
- 赢家回答：The character's emotional state is calm, confident.
- 起点抽取：[enthusiastic, passionate, positive]
- 赢家抽取：[calm, confident]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_RAISED
- 图候选：appreciated, hopeful, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7645175649147835}, {"state": "AGC_MIXED", "relative_support": 0.15552286851753785}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5983788439838285}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4016211560161715}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8548481489601502}, {"state": "ACT_UNCERTAIN", "relative_support": 0.14515185103984973}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.6519174976502963}, {"state": "ACP_LOW", "relative_support": 0.3480825023497038}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0046_0055.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is neutral.|
|long_graph_dataset_best|0.0000|The character's emotional state is excited, enthusiastic.|
|base35_A|0.0000|The character's emotional state is pride, satisfaction, enthusiasm, engagement.|
|base35_B|1.0000|The character's emotional state is excited, enthusiastic, tense, calm.|
|base35_C|0.0000|The character's emotional state is positive, confident, tense, anxious.|
|base35_D|1.0000|The character's emotional state is excited, enthusiastic, tense, calm.|
|base35_F|1.0000|The character's emotional state is excited, enthusiastic, tense, uncertain.|
|base35_E|0.0000|The character's emotional state is positive, confident, tense, anxious.|
|graph40_A|0.0000|The character's emotional state is calm, confident, professional, relaxed, comfortable.|
|graph40_B|0.0000|The character's emotional state is calm, confident.|
|graph40_C|0.0000|The character's emotional state is calm, confident, professional, relaxed, comfortable.|
|graph40_D|0.0000|The character's emotional state is calm, confident.|
|graph40_E|0.0000|The character's emotional state is calm, confident, professional, relaxed, comfortable.|
|graph40_F|0.0000|The character's emotional state is calm, confident.|
|base35_G|1.0000|The character's emotional state is excited, enthusiastic, tense, uncertain.|
|graph40_G|0.0000|The character's emotional state is calm, confident.|

## 120. SIMS / video_0002_0037 — 50权重持续正确/满命中

- 参考：0.8；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：He is the conscience of the capital market
- 中文：他可是资本市场良心啊
- 起点回答：The character's emotional state is positive, affirmation, praise.
- 赢家回答：The character's emotional state is pride, confidence, positive.
- 起点抽取：[positive, affirmation, praise]
- 赢家抽取：[pride, confidence, positive]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.823972689020605}, {"state": "AGC_MIXED", "relative_support": 0.1405636235225136}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.5965120970387329}, {"state": "AEX_EXPECTED", "relative_support": 0.4034879029612671}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6372315800712995}, {"state": "AAG_SELF", "relative_support": 0.3627684199287004}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.639733512420669}, {"state": "ACT_CERTAIN", "relative_support": 0.36026648757933105}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.978012796983851}, {"state": "ACP_LOW", "relative_support": 0.021987203016149086}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0002_0037.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is positive, praise, recognition.|
|long_graph_dataset_best|1.0000|The character's emotional state is excited, enthusiastic, confident, authoritative, positive.|
|base35_A|1.0000|The character's emotional state is pride, confidence, positive.|
|base35_B|1.0000|The character's emotional state is pride, enthusiasm, focus, comfort.|
|base35_C|1.0000|The character's emotional state is pride, enthusiasm, responsibility, professionalism.|
|base35_D|1.0000|The character's emotional state is pride, enthusiasm, focus, comfort.|
|base35_F|1.0000|The character's emotional state is pride, enthusiasm, importance, positivity.|
|base35_E|1.0000|The character's emotional state is pride, enthusiasm, responsibility, professionalism.|
|graph40_A|1.0000|The character's emotional state is admiration, recognition, positive evaluation, professionalism, friendliness, enthusiasm.|
|graph40_B|1.0000|The character's emotional state is pride, confidence, responsibility, sense of duty.|
|graph40_C|1.0000|The character's emotional state is admiration, recognition, positive evaluation, professionalism, friendliness, confidence.|
|graph40_D|1.0000|The character's emotional state is pride, confidence, responsibility, sense of duty.|
|graph40_E|1.0000|The character's emotional state is admiration, recognition, positive evaluation, professionalism, friendliness, confidence.|
|graph40_F|1.0000|The character's emotional state is admiration, appreciation, positive evaluation, professionalism, friendliness, confidence.|
|base35_G|1.0000|The character's emotional state is pride, enthusiasm, importance, positivity.|
|graph40_G|1.0000|The character's emotional state is admiration, appreciation, positive evaluation, professionalism, friendliness, confidence.|

## 121. SIMS / video_0040_0022 — 50权重持续正确/满命中

- 参考：-0.8；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：My best friends Meng Xiaojun and Wang Yang laughed at me
- 中文：我最好的朋友孟晓骏和王阳嘲笑我
- 起点回答：The character's emotional state is unhappy, embarrassed, mocked.
- 赢家回答：The character's emotional state is dissatisfaction, frustration, anger, confidence, determination.
- 起点抽取：[unhappy, embarrassed, mocked]
- 赢家抽取：[dissatisfaction, frustration, anger, confidence, determination]
- 最终极性：negative→negative。
- 实际level：2；原因：['mixed_text_affect_or_evaluation']。
- Cue：TXT_AFFECT_WORD_POSITIVE, TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, hopeful, disappointed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5607678472932336}, {"state": "AGC_INCONGRUENT", "relative_support": 0.40563132801244456}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8736534758289998}, {"state": "AEX_UNEXPECTED", "relative_support": 0.12634652417100015}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5013288299747468}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3776636357099213}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5112348877507041}, {"state": "ACP_LOW", "relative_support": 0.48876511224929575}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0040_0022.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is anxious, nervous, uncertain, frustrated, angry.|
|long_graph_dataset_best|1.0000|The character's emotional state is angry, frustrated, annoyed.|
|base35_A|1.0000|The character's emotional state is dissatisfaction, frustration, anger, confidence, determination.|
|base35_B|1.0000|The character's emotional state is dissatisfaction, frustration, anger, sadness.|
|base35_C|1.0000|The character's emotional state is sadness, frustration, anger, helplessness, surprise, astonishment.|
|base35_D|1.0000|The character's emotional state is dissatisfaction, frustration, anger, sadness.|
|base35_F|1.0000|The character's emotional state is dissatisfaction, frustration, anger, sadness.|
|base35_E|1.0000|The character's emotional state is sadness, frustration, anger, helplessness, surprise, astonishment.|
|graph40_A|1.0000|The character's emotional state is disappointed, sad, frustrated, angry.|
|graph40_B|1.0000|The character's emotional state is disappointed, sad, frustrated, angry.|
|graph40_C|1.0000|The character's emotional state is disappointed, sad, frustrated, angry.|
|graph40_D|1.0000|The character's emotional state is disappointed, sad, frustrated, angry.|
|graph40_E|1.0000|The character's emotional state is disappointed, sad, frustrated, angry.|
|graph40_F|1.0000|The character's emotional state is dissatisfaction, frustration, anger, confidence, determination.|
|base35_G|1.0000|The character's emotional state is dissatisfaction, frustration, anger, sadness.|
|graph40_G|1.0000|The character's emotional state is dissatisfaction, frustration, anger, confidence, determination.|

## 122. SIMS / video_0009_0021 — 50权重持续正确/满命中

- 参考：0.4；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：No, I just want to try it on.
- 中文：没有，我就穿上这身衣服试试。
- 起点回答：The character's emotional state is relaxed, open, positive, curious, excited.
- 赢家回答：The character's emotional state is excited, curious, positive, joyful.
- 起点抽取：[relaxed, open, positive, curious, excited]
- 赢家抽取：[excited, curious, positive, joyful]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_DESIRE_NEED, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：hopeful, joy, manic（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9869094047596824}, {"state": "AGR_RELEVANT", "relative_support": 0.013090595240317646}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7711053090744385}, {"state": "AGC_INCONGRUENT", "relative_support": 0.22889469092556158}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6853623038930727}, {"state": "AEX_EXPECTED", "relative_support": 0.31463769610692743}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6215381719656579}, {"state": "AAG_OTHER", "relative_support": 0.37846182803434214}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9348043278282776}, {"state": "ACT_CERTAIN", "relative_support": 0.0651956721717225}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8231529380859378}, {"state": "ACP_LOW", "relative_support": 0.17684706191406216}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0009_0021.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is excited, curious, positive.|
|long_graph_dataset_best|1.0000|The character's emotional state is positive, curious, interested, excited.|
|base35_A|1.0000|The character's emotional state is excited, curious, open-minded.|
|base35_B|1.0000|The character's emotional state is excited, curious, open-minded.|
|base35_C|0.0000|The character's emotional state is excited, curious, relaxed, tense, uncertain, certain, capable, pressured, non-capable.|
|base35_D|1.0000|The character's emotional state is excited, curious, open-minded.|
|base35_F|1.0000|The character's emotional state is excited, curious, relaxed, confident, positive.|
|base35_E|0.0000|The character's emotional state is excited, curious, relaxed, tense, uncertain, certain, capable, pressured, non-capable.|
|graph40_A|1.0000|The character's emotional state is excited, curious.|
|graph40_B|1.0000|The character's emotional state is excited, curious.|
|graph40_C|1.0000|The character's emotional state is excited, curious.|
|graph40_D|1.0000|The character's emotional state is excited, curious.|
|graph40_E|1.0000|The character's emotional state is excited, curious.|
|graph40_F|1.0000|The character's emotional state is excited, curious.|
|base35_G|1.0000|The character's emotional state is excited, curious, relaxed, confident, positive.|
|graph40_G|1.0000|The character's emotional state is excited, curious.|

## 123. SIMS / video_0035_0011 — 赢家零/错，其他权重经常命中/对

- 参考：1.0；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：1.0000→0.0000；50权重零/错9次、满/对41次。
- 模型字幕：Bai Juyi, he's crazy
- 中文：白居易，他可狂得很
- 起点回答：The character's emotional state is excitement, anxiety, enthusiasm.
- 赢家回答：The character's emotional state is excitement, frustration, humor, sarcasm, mockery.
- 起点抽取：[excitement, anxiety, enthusiasm]
- 赢家抽取：[excitement, frustration, humor, mockery]
- 最终极性：positive→mixed。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, AUD_INTONATION_FALLING, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：disappointed, anger, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5506521088992972}, {"state": "AGC_CONGRUENT", "relative_support": 0.4382396439599271}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9403189859838019}, {"state": "AEX_UNEXPECTED", "relative_support": 0.05968101401619809}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.43751347700460147}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.35283865641671963}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 1.0}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7071292828009599}, {"state": "ACP_HIGH", "relative_support": 0.29287071719904006}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0035_0011.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is excited, expectant, frustrated, angry, ironic, humorous.|
|long_graph_dataset_best|1.0000|The character's emotional state is excited, amused, teasing, joking.|
|base35_A|1.0000|The character's emotional state is excited, passionate, ironic, humorous.|
|base35_B|0.0000|The character's emotional state is crazy, negative, difficult, challenge, pressure.|
|base35_C|0.0000|The character's emotional state is crazy, negative, despondent, helpless.|
|base35_D|0.0000|The character's emotional state is crazy, negative, difficult, challenge, pressure.|
|base35_F|0.0000|The character's emotional state is crazy, negative, difficult, challenging, unable to accept.|
|base35_E|0.0000|The character's emotional state is crazy, negative, despondent, helpless.|
|graph40_A|1.0000|The character's emotional state is happy, excited, teasing.|
|graph40_B|1.0000|The character's emotional state is happy, entertained.|
|graph40_C|1.0000|The character's emotional state is excitement, tension, nervousness, anxiety, mockery, jest, happiness, positive.|
|graph40_D|1.0000|The character's emotional state is happy, entertained.|
|graph40_E|1.0000|The character's emotional state is excitement, tension, nervousness, anxiety, mockery, jest, happiness, positive.|
|graph40_F|1.0000|The character's emotional state is happy, entertained.|
|base35_G|0.0000|The character's emotional state is crazy, negative, difficult, challenging, unable to accept.|
|graph40_G|1.0000|The character's emotional state is happy, entertained.|

## 124. SIMS / video_0054_0039 — 赢家零/错，其他权重经常命中/对

- 参考：-0.4；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：0.0000→0.0000；50权重零/错25次、满/对25次。
- 模型字幕：Choosing this career means that you don't have so many choices.
- 中文：选择这个职业，就意味着你没有那么多的选择了
- 起点回答：The character's emotional state is serious, determined, positive.
- 赢家回答：The character's emotional state is committed, determined, serious, reflective.
- 起点抽取：[serious, determined, positive]
- 赢家抽取：[committed, determined, serious, reflective]
- 最终极性：positive→positive。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_LIPS_PRESSED, VIS_HEAD_LOWERED
- 图候选：hopeful, content, acceptance（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.6529888053793735}, {"state": "AGC_CONGRUENT", "relative_support": 0.21836810228873688}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8400061905443982}, {"state": "AEX_UNEXPECTED", "relative_support": 0.15999380945560182}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6245363200950306}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3754636799049695}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.935785858901188}, {"state": "ACT_UNCERTAIN", "relative_support": 0.06421414109881199}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9202921098951684}, {"state": "ACP_HIGH", "relative_support": 0.07970789010483163}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0054_0039.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is determination, focus, stress, overwhelm.|
|long_graph_dataset_best|1.0000|The character's emotional state is committed, irrevocable, no options, firm, unwavable, emotional calmness, reflection, contemplation.|
|base35_A|0.0000|The character's emotional state is anxious, nervous, overwhelmed, stressed, firm, positive.|
|base35_B|1.0000|The emotional state is committed, firm, determined, resolve, sense of control, tense, pressured.|
|base35_C|0.0000|The emotional state is committed, firm, determined, positive.|
|base35_D|1.0000|The character might be feeling a sense of pressure or challenge.|
|base35_F|1.0000|The character's emotional state is contemplative, introspective, overwhelmed, uncertain.|
|base35_E|1.0000|The character's emotional state is contemplative, hesitant, pressured, uncertain.|
|graph40_A|0.0000|The character's emotional state is committed, determined, positive.|
|graph40_B|1.0000|The character's emotional state is contemplative, introspective, overwhelmed, under pressure.|
|graph40_C|0.0000|The character's emotional state is committed, determined, positive.|
|graph40_D|0.0000|The character's emotional state is committed, determined, positive.|
|graph40_E|1.0000|The character's emotional state is contemplative, introspective, overwhelmed, under pressure.|
|graph40_F|1.0000|The character's emotional state is contemplative, introspective, overwhelmed, under pressure.|
|base35_G|0.0000|The emotional state is committed, firm, determined, resolve, sense of duty.|
|graph40_G|1.0000|The character's emotional state is contemplative, introspective, overwhelmed, under pressure.|

## 125. SIMS / video_0058_0002 — 赢家零/错，其他权重经常命中/对

- 参考：-0.8；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：1.0000→0.0000；50权重零/错14次、满/对36次。
- 模型字幕：You are not good enough.
- 中文：你确实还差点意思
- 起点回答：The character's emotional state is dissatisfaction, frustration, disappointment, criticism, negativity.
- 赢家回答：The character's emotional state is anxious, stressed, overwhelmed, happy, content, at ease.
- 起点抽取：[dissatisfaction, frustration, disappointment, criticism, negativity]
- 赢家抽取：[anxious, stressed, overwhelmed, happy, content, at ease]
- 最终极性：negative→positive。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, disappointed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5675209445258306}, {"state": "AGC_INCONGRUENT", "relative_support": 0.4324790554741694}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7414793099256242}, {"state": "AEX_EXPECTED", "relative_support": 0.25852069007437584}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5704669474072094}, {"state": "AAG_SELF", "relative_support": 0.42953305259279073}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6092808634300189}, {"state": "ACT_CERTAIN", "relative_support": 0.3907191365699812}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5506190297442743}, {"state": "ACP_LOW", "relative_support": 0.44938097025572565}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0058_0002.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is fear, anxiety, tension, doubt, uncertainty, pressure.|
|long_graph_dataset_best|1.0000|The character's emotional state is disappointment, dissatisfaction, criticism, frustration.|
|base35_A|1.0000|The character's emotional state is anxious, stressed, overwhelmed, critical, negative.|
|base35_B|1.0000|The character might be experiencing a sense of failure or inadequacy, with a negative evaluation and a strong negation present. However, given the audio cues where describe the character's's voice trembling and the visual clues show the character's expression of surprise, it can be inferred that the character might be going through a strong emotional turmoil, such as fear, anxiety, or nervousness. Therefore, this statement might be a self-evaluation or a reaction to someone else, possibly carrying a negative emotion.|
|base35_C|1.0000|The character's emotional state is anxious, under pressure, overwhelmed, negative, self-critical.|
|base35_D|1.0000|The character might be experiencing a sense of failure or inadequacy, with a negative evaluation and a strong negation present. However, given the audio cues where describe the character's's voice trembling and the visual clues show the character's expression of surprise, it can be inferred that the character might be going through a strong emotional turmoil, such as fear, anxiety, or nervousness. Therefore, this statement might be a self-evaluation or a reaction to someone else, possibly carrying a negative emotion.|
|base35_F|1.0000|The character's emotional state is anxious, uneasy, tense, overwhelmed, under immense pressure, negative, dissatisfaction, disappointment.|
|base35_E|1.0000|The character's emotional state is anxious, under pressure, overwhelmed, negative, self-critical.|
|graph40_A|1.0000|The character's emotional state is disappointment, dissatisfaction, frustration, annoyance.|
|graph40_B|1.0000|The character's emotional state is disappointment, dissatisfaction, frustration, annoyance, sadness, despair, confidence, determination.|
|graph40_C|1.0000|The character's emotional state is disappointment, frustration, anger.|
|graph40_D|1.0000|The character's emotional state is disappointment, dissatisfaction, frustration, annoyance, sadness, despair, confidence, determination.|
|graph40_E|1.0000|The character's emotional state is disappointment, frustration, anger.|
|graph40_F|1.0000|The character's emotional state is disappointment, frustration, anger, annoyance.|
|base35_G|1.0000|The character's emotional state is anxious, uneasy, tense, overwhelmed, under immense pressure, negative, dissatisfaction, disappointment.|
|graph40_G|1.0000|The character's emotional state is disappointment, frustration, anger, annoyance.|

## 126. SIMS / video_0028_0019 — 赢家满/对，其他权重经常不满/错

- 参考：-0.2；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：0.0000→1.0000；50权重零/错32次、满/对18次。
- 模型字幕：The last time I saw you, I thought you were familiar.
- 中文：我上一次见到你我就觉得你很眼熟。
- 起点回答：The character's emotional state is teasing, jest, playful, humorous, positive.
- 赢家回答：The character's emotional state is curiosity, surprise, nervousness, tension.
- 起点抽取：[teasing, jest, playful, humorous, positive]
- 赢家抽取：[curiosity, surprise, nervousness, tension]
- 最终极性：positive→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_UNCERTAINTY_HEDGE, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, delightful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6862616132526125}, {"state": "AGC_INCONGRUENT", "relative_support": 0.18015526570535917}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9276904024540781}, {"state": "AEX_UNEXPECTED", "relative_support": 0.07230959754592191}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6098834549341156}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.39011654506588445}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6709239364109119}, {"state": "ACT_CERTAIN", "relative_support": 0.3290760635890881}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5079935693220583}, {"state": "ACP_LOW", "relative_support": 0.49200643067794164}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0028_0019.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is anticipation, curiosity.|
|long_graph_dataset_best|1.0000|The character's emotional state is anxious, tense, confused, overwhelmed.|
|base35_A|0.0000|The character's emotional state is curiosity, surprise, positive.|
|base35_B|1.0000|The character's emotional state is curiosity, interest, positive mood, fear, anxiety, tension, detachment, emotional numbness.|
|base35_C|0.0000|The character's emotional state is curiosity, interest, positive, calm, organized, uncertainty.|
|base35_D|1.0000|The character's emotional state is curiosity, interest, positive mood, fear, anxiety, tension, detachment, emotional numbness.|
|base35_F|0.0000|The character's emotional state is curiosity, interest, positive mood, reflection, thoughtfulness.|
|base35_E|0.0000|The character's emotional state is curiosity, interest, positive, calm, organized, uncertainty.|
|graph40_A|0.0000|The character's emotional state is curiosity, surprise, happiness, engagement, enthusiasm, anticipation.|
|graph40_B|0.0000|The character's emotional state is curiosity, surprise, happiness, engagement, enjoyment.|
|graph40_C|0.0000|The character's emotional state is curiosity, surprise, happiness, engagement, enjoyment.|
|graph40_D|0.0000|The character's emotional state is curiosity, surprise, happiness, engagement, enjoyment.|
|graph40_E|0.0000|The character's emotional state is curiosity, surprise, happiness, engagement, enjoyment.|
|graph40_F|0.0000|The character's emotional state is curiosity, surprise, happiness, engagement, enjoyment.|
|base35_G|0.0000|The character's emotional state is curiosity, interest, positive mood, reflection, thoughtfulness.|
|graph40_G|0.0000|The character's emotional state is curiosity, surprise, happiness, engagement, enjoyment.|

## 127. SIMS / video_0046_0054 — 赢家满/对，其他权重经常不满/错

- 参考：0.2；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：0.0000→1.0000；50权重零/错38次、满/对12次。
- 模型字幕：The three tutors are all avoiding your speech
- 中文：三位导师，三位都在回避着你的演讲怎么样
- 起点回答：The character's emotional state is neutral.
- 赢家回答：The character's emotional state is anxious, tense, excited, energetic, stressed, overwhelmed.
- 起点抽取：[neutral]
- 赢家抽取：[anxious, tense, excited, energetic, stressed, overwhelmed]
- 最终极性：neutral→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED
- 图候选：joy, appalled, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5337771967139369}, {"state": "AGC_MIXED", "relative_support": 0.2992181934530704}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.5536418143560767}, {"state": "AEX_EXPECTED", "relative_support": 0.4463581856439232}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4310741842818165}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.36519375165220497}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7670626328709881}, {"state": "ACT_CERTAIN", "relative_support": 0.2329373671290119}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.546795622238108}, {"state": "ACP_HIGH", "relative_support": 0.45320437776189204}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0046_0054.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is tense, uneasy, anxious.|
|long_graph_dataset_best|1.0000|The character's emotional state is excited, tense, anticipatory, playful, teasing.|
|base35_A|1.0000|The character's emotional state is humorous, teasing, lighthearted.|
|base35_B|1.0000|The character's emotional state is excited, tense, anticipatory.|
|base35_C|1.0000|The character's emotional state is uncertain, tense, anxious, excited, motivated.|
|base35_D|1.0000|The character's emotional state is excited, tense, anticipatory.|
|base35_F|0.0000|The character's emotional state is excited, tense, surprised, confused, stressed.|
|base35_E|1.0000|The character's emotional state is uncertain, tense, anxious, excited, motivated.|
|graph40_A|1.0000|The character's emotional state is tension, anxiety, stress, humor, teasing.|
|graph40_B|0.0000|The character's emotional state is tension, anxiety, stress, nervous, uneasy.|
|graph40_C|0.0000|The character's emotional state is tension, anxiety, stress, humor, irony.|
|graph40_D|0.0000|The character's emotional state is tension, anxiety, stress, nervous, uneasy.|
|graph40_E|0.0000|The character's emotional state is tension, anxiety, stress, humor, irony.|
|graph40_F|0.0000|The character's emotional state is tension, anxiety, stress, humor, irony.|
|base35_G|0.0000|The character's emotional state is excited, tense, surprised, confused, stressed.|
|graph40_G|0.0000|The character's emotional state is tension, anxiety, stress, humor, irony.|

## 128. SIMS / video_0053_0010 — 赢家满/对，其他权重经常不满/错

- 参考：-1.0；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：0.0000→1.0000；50权重零/错38次、满/对12次。
- 模型字幕：Is it interesting that you said I'm fat?
- 中文：你就说我胖，有意思吗
- 起点回答：The character's emotional state is teasing, humorous, positive.
- 赢家回答：The character's emotional state is humorous, provocative, anxious, frustrated.
- 起点抽取：[teasing, humorous, positive]
- 赢家抽取：[humorous, provocative, anxious, frustrated]
- 最终极性：positive→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_RHETORICAL_QUESTION, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：anger, disappointed, apathetic（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.6811480036790691}, {"state": "AGC_CONGRUENT", "relative_support": 0.31885199632093086}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.9302434877983126}, {"state": "AAG_SELF", "relative_support": 0.06975651220168737}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8932408068222026}, {"state": "ACT_CERTAIN", "relative_support": 0.10675919317779735}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.560151015118983}, {"state": "ACP_HIGH", "relative_support": 0.439848984881017}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0053_0010.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is positive, humor, self-mockery.|
|long_graph_dataset_best|0.0000|The character's emotional state is joyful, humorous, teasing.|
|base35_A|1.0000|The character's emotional state is humorous, teasing, anxious, frustrated.|
|base35_B|0.0000|The character's emotional state is humorous, playful.|
|base35_C|1.0000|The character's emotional state is dissatisfaction, frustration.|
|base35_D|0.0000|The character's emotional state is humorous, playful.|
|base35_F|0.0000|The character's emotional state is ironic, humorous.|
|base35_E|0.0000|The character's emotional state is humorous, playful.|
|graph40_A|0.0000|The character's emotional state is humorous, teasing, positive.|
|graph40_B|0.0000|The character's emotional state is humorous, teasing, positive.|
|graph40_C|0.0000|The character's emotional state is humorous, teasing, positive.|
|graph40_D|0.0000|The character's emotional state is humorous, teasing, positive.|
|graph40_E|0.0000|The character's emotional state is humorous, teasing, positive.|
|graph40_F|0.0000|The character's emotional state is humorous, sarcastic, happy, comfortable.|
|base35_G|0.0000|The character's emotional state is humorous, playful.|
|graph40_G|0.0000|The character's emotional state is humorous, teasing, positive.|

## 129. SIMS / video_0045_0044 — 相对自身起点改善

- 参考：-0.8；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：0.0000→1.0000；50权重零/错44次、满/对6次。
- 模型字幕：Let I tell you, dreams are like underpants.
- 中文：我告诉你们，梦想就像是内裤
- 起点回答：The character's emotional state is passionate, humorous, urgent.
- 赢家回答：The character's emotional state is disdain, mockery, discontent.
- 起点抽取：[passionate, humorous, urgent]
- 赢家抽取：[disdain, mockery, discontent]
- 最终极性：positive→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：despair, depressed, disappointed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7928692126965524}, {"state": "AGC_MIXED", "relative_support": 0.10691170862629508}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7380562034087331}, {"state": "AEX_UNEXPECTED", "relative_support": 0.2619437965912668}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.4742998880314454}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.41047998168465444}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6405803326356536}, {"state": "ACT_UNCERTAIN", "relative_support": 0.35941966736434644}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9914455461796514}, {"state": "ACP_HIGH", "relative_support": 0.008554453820348671}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0045_0044.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is jokey, humorous, light-hearted, cheerful.|
|long_graph_dataset_best|0.0000|The character's emotional state is confidence, conviction, passion.|
|base35_A|1.0000|The character's emotional state is negative, dismissive, contemptuous.|
|base35_B|1.0000|The emotional state is negative, depressed, angry, defensive.|
|base35_C|1.0000|The character's emotional state is negative, dissatisfaction, disagreement.|
|base35_D|1.0000|The character's emotional state is negative, depressed, angry.|
|base35_F|1.0000|The character's emotional state is negative, dismissive, contemptuous.|
|base35_E|1.0000|The character's emotional state is negative, depressed, angry.|
|graph40_A|0.0000|The character's emotional state is excitement, passion, enthusiasm.|
|graph40_B|0.0000|The character's emotional state is excitement, enthusiasm, confidence.|
|graph40_C|0.0000|The character's emotional state is enthusiastic, humorous, passionate.|
|graph40_D|0.0000|The character's emotional state is excitement, enthusiasm, confidence.|
|graph40_E|0.0000|The character's emotional state is enthusiastic, humorous, passionate.|
|graph40_F|0.0000|The character's emotional state is enthusiastic, humorous, passionate.|
|base35_G|1.0000|The character's emotional state is negative, angry, defensive.|
|graph40_G|0.0000|The character's emotional state is enthusiastic, humorous, passionate.|

## 130. SIMS / video_0013_0035 — 相对自身起点改善

- 参考：0.2；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：0.0000→1.0000；50权重零/错28次、满/对22次。
- 模型字幕：Your method of being lazy is too inferior
- 中文：你这偷懒的方法太低级了
- 起点回答：The character's emotional state is mocking, sarcastic, negative, playful.
- 赢家回答：The character's emotional state is playful, teasing, positive.
- 起点抽取：[mocking, sarcastic, negative, playful]
- 赢家抽取：[playful, teasing, positive]
- 最终极性：negative→positive。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6403429339848066}, {"state": "AGC_INCONGRUENT", "relative_support": 0.35965706601519337}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7150649583670646}, {"state": "AEX_EXPECTED", "relative_support": 0.2849350416329354}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5877079129938392}, {"state": "AAG_SELF", "relative_support": 0.41229208700616077}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6231306172321168}, {"state": "ACT_CERTAIN", "relative_support": 0.3768693827678833}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.634742129359463}, {"state": "ACP_LOW", "relative_support": 0.36525787064053705}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0013_0035.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is joyful, humorous, playful.|
|long_graph_dataset_best|1.0000|The character's emotional state is positive, excited, humorous, sarcastic.|
|base35_A|0.0000|The character's emotional state is anger, frustration, sarcasm.|
|base35_B|1.0000|Emotional state: positive, exaggerated, teasing, positive.|
|base35_C|0.0000|The character's emotional state is anger, frustration, sarcasm.|
|base35_D|1.0000|Emotional state: positive, exaggerated, teasing, positive.|
|base35_F|0.0000|The character's emotional state is anger, aggression, sarcasm, mockery.|
|base35_E|0.0000|The character's emotional state is anger, frustration, sarcasm.|
|graph40_A|1.0000|The character's emotional state is happiness, satisfaction, playful.|
|graph40_B|1.0000|The character's emotional state is happiness, satisfaction, playful.|
|graph40_C|1.0000|The character's emotional state is positive, humorous, playful.|
|graph40_D|1.0000|The character's emotional state is happiness, satisfaction, playful.|
|graph40_E|1.0000|The character's emotional state is positive, humorous, playful.|
|graph40_F|1.0000|The character's emotional state is happiness, satisfaction, playful.|
|base35_G|0.0000|The character's emotional state is anger, aggression, sarcasm, mockery.|
|graph40_G|1.0000|The character's emotional state is happiness, satisfaction, playful.|

## 131. SIMS / video_0021_0005 — 相对自身起点改善

- 参考：-0.2；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：0.0000→1.0000；50权重零/错31次、满/对19次。
- 模型字幕：That also allows me to see your skills.
- 中文：那也让我见识下你的本事。
- 起点回答：The character's emotional state is challenge, mockery, confidence, determination.
- 赢家回答：The character's emotional state is challenge, anticipation of professional respect, confrontation, tension.
- 起点抽取：[challenge, mockery, confidence, determination]
- 赢家抽取：[challenge, anticipation, confrontation, tension]
- 最终极性：positive→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED
- 图候选：appreciated, joy, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6634672218410155}, {"state": "AGC_MIXED", "relative_support": 0.1809350367226057}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6898619129911004}, {"state": "AEX_EXPECTED", "relative_support": 0.3101380870088995}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 1.0}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7382226793175649}, {"state": "ACT_CERTAIN", "relative_support": 0.2617773206824351}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7129491297147741}, {"state": "ACP_LOW", "relative_support": 0.2870508702852258}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0021_0005.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is appreciative, admiring, confident.|
|long_graph_dataset_best|0.0000|The character's emotional state is challenge, confidence, determination.|
|base35_A|1.0000|The character's emotional state is challenge, mockery, confidence.|
|base35_B|0.0000|The character's emotional state is challenge, mockery, frustration, excitement.|
|base35_C|0.0000|The character's emotional state is challenge, mockery, confidence, self-assurance.|
|base35_D|0.0000|The character's emotional state is challenge, mockery, frustration, excitement.|
|base35_F|0.0000|The character's emotional state is challenge, mockery, frustration, excitement.|
|base35_E|0.0000|The character's emotional state is challenge, mockery, confidence, self-assurance.|
|graph40_A|0.0000|The character's emotional state is appreciative, encouraging, confident, focused.|
|graph40_B|0.0000|The character's emotional state is appreciative, encouraging, confident, focused.|
|graph40_C|0.0000|The character's emotional state is appreciative, encouraging, confident, calm.|
|graph40_D|0.0000|The character's emotional state is appreciative, encouraging, confident, focused.|
|graph40_E|0.0000|The character's emotional state is appreciative, encouraging, confident, calm.|
|graph40_F|0.0000|The character's emotional state is appreciative, encouraging, confident.|
|base35_G|0.0000|The character's emotional state is challenge, mockery, frustration, excitement.|
|graph40_G|0.0000|The character's emotional state is appreciative, encouraging, confident.|

## 132. SIMS / video_0001_0031 — 相对自身起点恶化

- 参考：0.6；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：1.0000→0.0000；50权重零/错39次、满/对11次。
- 模型字幕：Isn't it almost bankrupt?
- 中文：不是都快破产了吗
- 起点回答：The character's emotional state is teasing, sarcastic, positive.
- 赢家回答：The character's emotional state is worry, anxiety, irony.
- 起点抽取：[teasing, sarcastic, positive]
- 赢家抽取：[worry, anxiety]
- 最终极性：positive→negative。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：disappointed, anger, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9935714277916978}, {"state": "AGR_RELEVANT", "relative_support": 0.006428572208302071}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7778222483777892}, {"state": "AGC_CONGRUENT", "relative_support": 0.22217775162221076}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9479455765690481}, {"state": "AEX_EXPECTED", "relative_support": 0.05205442343095185}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.519135247451964}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.31491594483476115}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7346865484988924}, {"state": "ACT_CERTAIN", "relative_support": 0.2653134515011077}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.7344437261464357}, {"state": "ACP_HIGH", "relative_support": 0.26555627385356434}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0001_0031.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is anxious, tense, critical, negative.|
|long_graph_dataset_best|0.0000|The character's emotional state is sarcastic, ironic, anxious, tense, frustrated, irritated.|
|base35_A|1.0000|The character's emotional state is teasing, ironic, playful.|
|base35_B|0.0000|The character's emotional state is concerned, anxious, fearful.|
|base35_C|0.0000|The character's emotional state is concerned, anxious, surprised.|
|base35_D|0.0000|The character's emotional state is concerned, anxious, fearful.|
|base35_F|0.0000|The character's emotional state is concern, anxiety, uncertainty.|
|base35_E|0.0000|The character's emotional state is concerned, anxious, surprised.|
|graph40_A|0.0000|The character's emotional state is anxiety, stress, overwhelm.|
|graph40_B|0.0000|The character's emotional state is sarcastic, mocking, negative, anxiety, frustration, anger.|
|graph40_C|1.0000|The character's emotional state is teasing, humorous, playful.|
|graph40_D|0.0000|The character's emotional state is sarcastic, mocking, negative, anxiety, frustration, anger.|
|graph40_E|1.0000|The character's emotional state is teasing, humorous, playful.|
|graph40_F|1.0000|The character's emotional state is teasing, humorous, playful.|
|base35_G|0.0000|The character's emotional state is concern, anxiety, uncertainty.|
|graph40_G|1.0000|The character's emotional state is teasing, humorous, playful.|

## 133. SIMS / video_0026_0020 — 相对自身起点恶化

- 参考：0.4；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：1.0000→0.0000；50权重零/错36次、满/对14次。
- 模型字幕：Is it? It's very good. Destroy what is harmful to the people.
- 中文：是吗？挺好，为民除害。
- 起点回答：The character's emotional state is supportive, agreeable, concerned, focused.
- 赢家回答：The character's emotional state is calm, indifferent.
- 起点抽取：[supportive, agreeable, concerned, focused]
- 赢家抽取：[calm, indifferent]
- 最终极性：positive→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：appreciated, hopeful, confident（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.707262058939203}, {"state": "AGC_MIXED", "relative_support": 0.25666012048149073}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9306824793609505}, {"state": "AEX_UNEXPECTED", "relative_support": 0.06931752063904935}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.558913736599731}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.43429669519624503}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8156784253438876}, {"state": "ACT_UNCERTAIN", "relative_support": 0.18432157465611243}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8173066456913854}, {"state": "ACP_LOW", "relative_support": 0.1826933543086146}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0026_0020.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is thoughtful, calm, concerned, supportive.|
|long_graph_dataset_best|0.0000|The character's emotional state is affirmative, supportive.|
|base35_A|0.0000|The character's emotional state is excited, angry.|
|base35_B|0.0000|The character's emotional state is calm, detached, excited, worried.|
|base35_C|0.0000|The character's emotional state is calm, detached, possibly melancholic.|
|base35_D|0.0000|The character's emotional state is calm, detached, excited, worried.|
|base35_F|0.0000|The character's emotional state is excited, nervous, serious, determined.|
|base35_E|0.0000|The character's emotional state is calm, detached, possibly melancholic.|
|graph40_A|1.0000|The character's emotional state is excited, supportive, affirmative.|
|graph40_B|1.0000|The character's emotional state is excited, supportive, affirmative.|
|graph40_C|1.0000|The character's emotional state is affirmative, supportive, serious, determined.|
|graph40_D|1.0000|The character's emotional state is excited, supportive, affirmative.|
|graph40_E|1.0000|The character's emotional state is affirmative, supportive, serious, determined.|
|graph40_F|1.0000|The character's emotional state is excited, supportive, affirmative.|
|base35_G|1.0000|The character's emotional state is excited, nervous, serious, determined.|
|graph40_G|1.0000|The character's emotional state is excited, supportive, affirmative.|

## 134. SIMS / video_0027_0023 — 相对自身起点恶化

- 参考：-1.0；赢家：from_35_epoch_41_SIMS；起点epoch35。
- 质量：1.0000→0.0000；50权重零/错22次、满/对28次。
- 模型字幕：This time, my mother also cooked new dumplings for you, 20.
- 中文：这回娘也给你煮了新的饺子，还是20个。
- 起点回答：The character's emotional state is tense, anxious.
- 赢家回答：The character's emotional state is warm, comforting, encouraging.
- 起点抽取：[tense, anxious]
- 赢家抽取：[warm, comforting, encouraging]
- 最终极性：negative→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_LOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN, VIS_HEAD_LOWERED
- 图候选：depressed, despair, ashamed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7068309259706366}, {"state": "AGC_MIXED", "relative_support": 0.2029869581023598}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8512479923898164}, {"state": "AEX_UNEXPECTED", "relative_support": 0.14875200761018348}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5502770238966195}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.398335966495661}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5989679909427594}, {"state": "ACT_UNCERTAIN", "relative_support": 0.4010320090572405}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9918248583888363}, {"state": "ACP_HIGH", "relative_support": 0.008175141611163604}]}
- 视频：/ai/sjq/AffectGPT/dataset/sims-process/video/video_0027_0023.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is sadness, emotional numbness.|
|long_graph_dataset_best|1.0000|The character's emotional state is sadness, anger, frustration, helplessness, overwhelmed, gloom, depression.|
|base35_A|1.0000|The character's emotional state is sadness, longing, nostalgia.|
|base35_B|1.0000|The character might be experiencing sadness, depression, boredom, loneliness, anxiety.|
|base35_C|1.0000|The character's emotional state is depressed, anxious, overwhelmed.|
|base35_D|1.0000|The character might be experiencing sadness, fear, and disgust.|
|base35_F|1.0000|Based on the audio clues describing slow speech rate, low pitch, low vocal intensity, low pitch variability, long pauses, falling intonation, and flat tone, it can be inferred that the individual is likely experiencing feelings of sadness, fear, or disgust. These clues suggest that the individual may be feeling emotionally numb or disconnected from their emotions. Therefore, this sentence might be the individual's's expression of disappointment or dissatisfaction towards someone or something.|
|base35_E|1.0000|The character's emotional state is sad, fearful, disgusted.|
|graph40_A|0.0000|The character's emotional state is warm, caring, comforting.|
|graph40_B|0.0000|The character's emotional state is warm, caring, concerned, comforting.|
|graph40_C|0.0000|The character's emotional state is warm, caring, comforting.|
|graph40_D|0.0000|The character's emotional state is warm, caring, concerned, comforting.|
|graph40_E|0.0000|The character's emotional state is warm, caring, comforting.|
|graph40_F|0.0000|The character's emotional state is warm, caring, comforting.|
|base35_G|1.0000|The character's emotional state is depressed, anxious, isolated.|
|graph40_G|0.0000|The character's emotional state is warm, caring, comforting.|

## 135. SIMSv2 / video_0037_0005 — 50权重持续错误/零命中

- 参考：0.2；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：Sorry, I have a lot of earwax recently.
- 中文：不好意思啊，最近耳屎比较多
- 起点回答：The character's emotional state is dissatisfaction, discomfort, anxiety, stress.
- 赢家回答：The character's emotional state is humor, lightheartedness, discomfort, embarrassment.
- 起点抽取：[dissatisfaction, discomfort, anxiety, stress]
- 赢家抽取：[humor, lightheartedness, discomfort, embarrassment]
- 最终极性：negative→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.892521831112495}, {"state": "AGC_CONGRUENT", "relative_support": 0.06784475391132379}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6661260516646793}, {"state": "AEX_UNEXPECTED", "relative_support": 0.33387394833532075}], "APP_AGENCY": [{"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4482485658310385}, {"state": "AAG_SELF", "relative_support": 0.36039906007452915}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7673080784002408}, {"state": "ACT_UNCERTAIN", "relative_support": 0.23269192159975907}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9931850940653205}, {"state": "ACP_HIGH", "relative_support": 0.006814905934679506}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/video_0037_0005.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is anxious, tense, stressed, dissatisfied, uncomfortable, troubled, painful.|
|long_graph_dataset_best|0.0000|The character's emotional state is anxiety, tension, stress.|

## 136. SIMSv2 / aqgy5_0020_00020 — 50权重持续错误/零命中

- 参考：-0.4；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：Do you want me to invite you for a drink, while drinking and chatting, we can emit the fragrance of single dogs.
- 中文：要不要请你喝一杯，边喝边聊，咱们散发单身狗的清香。
- 起点回答：The character's emotional state is humorous, playful, positive.
- 赢家回答：The character's emotional state is humorous, teasing, anxious, excited.
- 起点抽取：[humorous, playful, positive]
- 赢家抽取：[humorous, teasing, anxious, excited]
- 最终极性：positive→positive。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_DESIRE_NEED, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED
- 图候选：hopeful, appreciated, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7608353892256061}, {"state": "AGC_MIXED", "relative_support": 0.18567071278247013}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.5962670285513424}, {"state": "AEX_EXPECTED", "relative_support": 0.40373297144865755}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6861948088534763}, {"state": "AAG_SELF", "relative_support": 0.31380519114652367}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.7436333980040034}, {"state": "ACT_CERTAIN", "relative_support": 0.2563666019959966}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.9673085996368648}, {"state": "ACP_LOW", "relative_support": 0.03269140036313518}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/aqgy5_0020_00020.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is humorous, joking, positive.|
|long_graph_dataset_best|0.0000|The character's emotional state is jokey, humorous, positive.|

## 137. SIMSv2 / aqgy4_0012_00051 — 50权重持续错误/零命中

- 参考：0.6；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：We must quickly resolve this, there are still a bunch of cases waiting for me to handle.
- 中文：那必须速战速决呀，后面还有一大堆案子等着我处理呢。
- 起点回答：The character's emotional state is urgent, stressed, agitated, impatient.
- 赢家回答：The character's emotional state is anxiety, stress.
- 起点抽取：[urgent, stressed, agitated, impatient]
- 赢家抽取：[anxiety, stress]
- 最终极性：negative→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, TXT_EXCLAMATION_INTERJECTION, TXT_DESIRE_NEED, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_GRIMACE_PRESENT
- 图候选：anger, disappointed, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8662618092453833}, {"state": "AGC_CONGRUENT", "relative_support": 0.13373819075461668}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8219031346820891}, {"state": "AEX_EXPECTED", "relative_support": 0.17809686531791089}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6951788806458618}, {"state": "AAG_SELF", "relative_support": 0.2025160084086333}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8221798599946024}, {"state": "ACT_CERTAIN", "relative_support": 0.1778201400053976}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6906699756791386}, {"state": "ACP_HIGH", "relative_support": 0.3093300243208615}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/aqgy4_0012_00051.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is anxious, impatient, frustrated, pressured.|
|long_graph_dataset_best|0.0000|The character's emotional state is anxiety, stress.|

## 138. SIMSv2 / video_0045_0011 — 50权重持续正确/满命中

- 参考：0.6；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：I like all three children very much.
- 中文：三个孩子我都特别喜欢
- 起点回答：The character's emotional state is excitement, enthusiasm, passion, affection, longing.
- 赢家回答：The character's emotional state is excitement, nervousness, joy, affection.
- 起点抽取：[excitement, enthusiasm, passion, affection, longing]
- 赢家抽取：[excitement, nervousness, joy, affection]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_POSITIVE, TXT_EVALUATION_POSITIVE, TXT_INTENSIFIER_PRESENT, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：appreciated, joy, awe（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6300759349673447}, {"state": "AGC_INCONGRUENT", "relative_support": 0.24044884432852892}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7104296259757912}, {"state": "AEX_UNEXPECTED", "relative_support": 0.2895703740242088}], "APP_AGENCY": [], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8297158271762236}, {"state": "ACT_UNCERTAIN", "relative_support": 0.17028417282377642}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6026964998403466}, {"state": "ACP_HIGH", "relative_support": 0.3973035001596534}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/video_0045_0011.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is joy, excitement, affection.|
|long_graph_dataset_best|1.0000|The character's emotional state is excitement, anticipation, nervousness, love, affection.|

## 139. SIMSv2 / video_0012_0026 — 50权重持续正确/满命中

- 参考：-1.0；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：Why did I give birth to such a stupid daughter like you?
- 中文：你说我怎么就生了你这样一个笨女儿呢我。
- 起点回答：The character's emotional state is angry, frustrated.
- 赢家回答：The character's emotional state is angry, frustrated, disappointment, dissatisfaction.
- 起点抽取：[angry, frustrated]
- 赢家抽取：[angry, frustrated, disappointment, dissatisfaction]
- 最终极性：negative→negative。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_SELF, AUD_SPEECH_RATE_REL_FAST, AUD_PITCH_LEVEL_REL_HIGH, AUD_VOCAL_INTENSITY_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_VOICE_TENSE, VIS_HEAD_LOWERED
- 图候选：anger, disappointed, ashamed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.919205465566415}, {"state": "AEX_EXPECTED", "relative_support": 0.08079453443358502}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.5529839733441398}, {"state": "AAG_SELF", "relative_support": 0.4162878540438478}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6853276984820578}, {"state": "ACT_CERTAIN", "relative_support": 0.31467230151794223}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/video_0012_0026.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is anger, frustration, sadness.|
|long_graph_dataset_best|1.0000|The character's emotional state is anger, frustration, self-doubt, dissatisfaction, guilt, shame.|

## 140. SIMSv2 / video_0032_0007 — 50权重持续正确/满命中

- 参考：-0.4；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：Mr. Wu, just accept your bad luck.
- 中文：吴先生，你就认倒霉吧
- 起点回答：The character's emotional state is anger, dissatisfaction, mockery.
- 赢家回答：The character's emotional state is mocking, indifferent, callous.
- 起点抽取：[anger, dissatisfaction, mockery]
- 赢家抽取：[mocking, indifferent, callous]
- 最终极性：negative→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_EYES_SQUINTED
- 图候选：disappointed, ashamed, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.923394695311836}, {"state": "AGR_RELEVANT", "relative_support": 0.07660530468816391}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.8538647762193494}, {"state": "AGC_CONGRUENT", "relative_support": 0.07332266983744794}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9561400515766749}, {"state": "AEX_UNEXPECTED", "relative_support": 0.04385994842332506}], "APP_AGENCY": [{"state": "AAG_CIRCUMSTANCE", "relative_support": 0.5014723840705078}, {"state": "AAG_SELF", "relative_support": 0.40527677161668746}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8619617640082559}, {"state": "ACT_UNCERTAIN", "relative_support": 0.13803823599174408}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9918169389828394}, {"state": "ACP_HIGH", "relative_support": 0.008183061017160577}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/video_0032_0007.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is dissatisfaction, mockery, negative assessment.|
|long_graph_dataset_best|1.0000|The character's emotional state is impatience, contempt, negative evaluation, blame.|

## 141. SIMSv2 / test5_00018 — 赢家零/错，其他权重经常命中/对

- 参考：0.2；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：0.0000→0.0000；50权重零/错21次、满/对29次。
- 模型字幕：The joy, anger, sorrow, and happiness of parents are a standard for judging whether I am doing things right or not.
- 中文：父母的喜怒哀乐是卧判断我做事情对不对的一个标准。
- 起点回答：The character's emotional state is understanding, resonance, acceptance, sadness, anger, frustration, anxiety.
- 赢家回答：The character's emotional state is reflection, thought, understanding, standards.
- 起点抽取：[understanding, resonance, acceptance, sadness, anger, frustration, anxiety]
- 赢家抽取：[]
- 最终极性：negative→neutral。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_POSITIVE, TXT_NEGATION_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, appreciated, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6736888863689743}, {"state": "AGC_INCONGRUENT", "relative_support": 0.20517426099543046}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8929794970458625}, {"state": "AEX_UNEXPECTED", "relative_support": 0.10702050295413747}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5930248654110791}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.406975134588921}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6951395922352476}, {"state": "ACT_UNCERTAIN", "relative_support": 0.30486040776475243}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6746697545664804}, {"state": "ACP_HIGH", "relative_support": 0.32533024543351957}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/test5_00018.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is recognition, gratitude, awareness, importance, emphasis, positivity.|
|long_graph_dataset_best|0.0000|The character's emotional state is positive, negative.|

## 142. SIMSv2 / aqgy3_0008_00014 — 赢家零/错，其他权重经常命中/对

- 参考：-0.8；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：0.0000→0.0000；50权重零/错24次、满/对26次。
- 模型字幕：What else can we discuss now?
- 中文：那我们现在还能讨论什么。
- 起点回答：The character's emotional state is joyful, humorous.
- 赢家回答：The character's emotional state is joyful, happy, relaxed, excited, cheerful.
- 起点抽取：[joyful, humorous]
- 赢家抽取：[joyful, happy, relaxed, excited, cheerful]
- 最终极性：positive→positive。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, TXT_RHETORICAL_QUESTION, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN
- 图候选：disappointed, anger, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 1.0}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9796995738826242}, {"state": "AEX_EXPECTED", "relative_support": 0.02030042611737577}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8998606289505741}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.10013937104942584}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9826612583870413}, {"state": "ACT_CERTAIN", "relative_support": 0.017338741612958626}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/aqgy3_0008_00014.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is anger, frustration, irony, humor.|
|long_graph_dataset_best|1.0000|The character's emotional state is excited, anxious.|

## 143. SIMSv2 / video_0043_0058 — 赢家零/错，其他权重经常命中/对

- 参考：1.0；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：1.0000→0.0000；50权重零/错4次、满/对46次。
- 模型字幕：I can only say that I was lucky this time.
- 中文：我只能说我这次是侥幸
- 起点回答：The character's emotional state is surprised, fortunate.
- 赢家回答：The character's emotional state is relaxed, humorous, self-deprecating, satirical, tense, stressed.
- 起点抽取：[surprised, fortunate]
- 赢家抽取：[relaxed, humorous, self-deprecating, satirical, tense, stressed]
- 最终极性：positive→mixed。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7839026225683499}, {"state": "AGC_INCONGRUENT", "relative_support": 0.15241316324249532}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9323199818378658}, {"state": "AEX_UNEXPECTED", "relative_support": 0.06768001816213412}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6059904834743356}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3883993436597598}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.8125096390131759}, {"state": "ACT_UNCERTAIN", "relative_support": 0.18749036098682412}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.6669250392908718}, {"state": "ACP_LOW", "relative_support": 0.33307496070912823}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/video_0043_0058.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is surprised, satisfied, humorous.|
|long_graph_dataset_best|0.0000|The character's emotional state is surprised, disappointed, frustrated, stressed, anxious, sarcastic, self-deprecating.|

## 144. SIMSv2 / video_0027_0026 — 赢家满/对，其他权重经常不满/错

- 参考：-0.8；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：0.0000→1.0000；50权重零/错28次、满/对22次。
- 模型字幕：What else can I do for you, Youqing?
- 中文：你看还能为有庆做点什么吗
- 起点回答：The character's emotional state is positive, helpful, supportive.
- 赢家回答：The character's emotional state is serious, focused.
- 起点抽取：[positive, helpful, supportive]
- 赢家抽取：[serious, focused]
- 最终极性：positive→negative。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_RHETORICAL_QUESTION, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_RISING, VIS_EYES_SQUINTED
- 图候选：bewildered, disappointed, depressed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7354554863895293}, {"state": "AGC_MIXED", "relative_support": 0.21305928003787175}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7101571659723972}, {"state": "AEX_EXPECTED", "relative_support": 0.28984283402760275}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.3722306517130609}, {"state": "AAG_OTHER", "relative_support": 0.32243630130443907}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9456600018439165}, {"state": "ACT_CERTAIN", "relative_support": 0.054339998156083424}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/video_0027_0026.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is excited, anxious, positive.|
|long_graph_dataset_best|0.0000|The character's emotional state is positive, supportive.|

## 145. SIMSv2 / video_0053_0049 — 赢家满/对，其他权重经常不满/错

- 参考：0.4；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：0.0000→1.0000；50权重零/错26次、满/对24次。
- 模型字幕：It's not yet the beginning of summer, but it's as hot as a steamer in this palace. My body is really dry.
- 中文：还没入伏，这宫里热的就跟蒸笼一样，本宫的身子实在是燥得很
- 起点回答：The character's emotional state is happiness, excitement, anticipation, anxiety, tension, sadness, depression.
- 赢家回答：The character's emotional state is relaxed, cheerful, humorous.
- 起点抽取：[happiness, excitement, anticipation, anxiety, tension, sadness, depression]
- 赢家抽取：[relaxed, cheerful, humorous]
- 最终极性：mixed→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_CONTRAST_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_RAISED, VIS_MOUTH_CORNERS_DOWN
- 图候选：disappointed, depressed, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5813205688810085}, {"state": "AGC_MIXED", "relative_support": 0.3031617082806185}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7765161016973612}, {"state": "AEX_UNEXPECTED", "relative_support": 0.22348389830263887}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.49924448052976844}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4084683386470085}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7451473876144183}, {"state": "ACT_UNCERTAIN", "relative_support": 0.25485261238558177}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.8952505909162816}, {"state": "ACP_HIGH", "relative_support": 0.10474940908371853}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/video_0053_0049.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is joyful, humorous.|
|long_graph_dataset_best|1.0000|The character's emotional state is joy, happiness.|

## 146. SIMSv2 / aqgy4_0007_00023 — 赢家满/对，其他权重经常不满/错

- 参考：0.6；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：1.0000→1.0000；50权重零/错29次、满/对21次。
- 模型字幕：That's for sure, his son.
- 中文：那是肯定的，他儿子。
- 起点回答：The character's emotional state is excited, joyful, positive, amused, light-hearted, sarcastic.
- 赢家回答：The character's emotional state is joyful, teasing, humorous.
- 起点抽取：[excited, joyful, positive, amused, light-hearted]
- 赢家抽取：[joyful, teasing, humorous]
- 最终极性：positive→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：anxious, care, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.9118992837587745}, {"state": "AGC_INCONGRUENT", "relative_support": 0.08810071624122545}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.9706202493438644}, {"state": "AEX_EXPECTED", "relative_support": 0.029379750656135663}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.8030273659753503}, {"state": "AAG_SELF", "relative_support": 0.19697263402464968}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.802410524123072}, {"state": "ACT_CERTAIN", "relative_support": 0.19758947587692796}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/aqgy4_0007_00023.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is enthusiastic, passionate, confident, sarcastic, mocking.|
|long_graph_dataset_best|1.0000|The character's emotional state is surprised, curious, teasing, positive.|

## 147. SIMSv2 / aqgy5_0012_00028 — 相对自身起点改善

- 参考：-0.4；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：0.0000→1.0000；50权重零/错35次、满/对15次。
- 模型字幕：I'm sorry, this is a misunderstanding. It's a well-intentioned lie.
- 中文：对不起这是个误会这是个善意的谎言。
- 起点回答：The character's emotional state is understanding, comfort, reassurance, explanation, clarification.
- 赢家回答：The character's emotional state is understanding, forgiveness, tension, pressure, relief.
- 起点抽取：[understanding, comfort, reassurance, explanation, clarification]
- 赢家抽取：[understanding, forgiveness, tension, pressure, relief]
- 最终极性：positive→mixed。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_LOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_PAUSE_FREQUENT, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_HEAD_LOWERED
- 图候选：ashamed, depressed, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7750812531396768}, {"state": "AGC_MIXED", "relative_support": 0.15572155882884237}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9660531171347959}, {"state": "AEX_UNEXPECTED", "relative_support": 0.03394688286520409}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5182665830211326}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4054311735444015}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7672592142855807}, {"state": "ACT_UNCERTAIN", "relative_support": 0.23274078571441925}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9913551092110222}, {"state": "ACP_HIGH", "relative_support": 0.008644890788977724}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/aqgy5_0012_00028.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is understanding, nonchalance, humor, light-heartedness.|
|long_graph_dataset_best|0.0000|The character's emotional state is apologetic, explanatory, anxious, excited, joyful, misinterpreted, misunderstanding.|

## 148. SIMSv2 / test12_00001 — 相对自身起点改善

- 参考：0.2；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：0.0000→1.0000；50权重零/错12次、满/对38次。
- 模型字幕：Why do you have that kind of feeling in your mind?
- 中文：就是你心理会有那种凭什么？
- 起点回答：The character's emotional state is anxious, tense, under significant stress, questioning, probing.
- 赢家回答：The character's emotional state is anxious, tense, excited, happy, confident, dominant.
- 起点抽取：[anxious, tense, stressed, questioning, probing]
- 赢家抽取：[anxious, tense, excited, happy, confident, dominant]
- 最终极性：negative→positive。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_RHETORICAL_QUESTION, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, apathetic（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.757847395987076}, {"state": "AGC_INCONGRUENT", "relative_support": 0.2421526040129241}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8652080410457549}, {"state": "AEX_EXPECTED", "relative_support": 0.1347919589542451}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7361513842238612}, {"state": "AAG_SELF", "relative_support": 0.2638486157761388}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9561595986684729}, {"state": "ACT_CERTAIN", "relative_support": 0.043840401331527105}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8167912504912402}, {"state": "ACP_LOW", "relative_support": 0.1832087495087599}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/test12_00001.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is happy, excitement, anxiety, tension.|
|long_graph_dataset_best|1.0000|The character's emotional state is happiness, excitement, nervousness, anxiety.|

## 149. SIMSv2 / video_0057_0015 — 相对自身起点改善

- 参考：1.0；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：0.0000→1.0000；50权重零/错1次、满/对49次。
- 模型字幕：Don't worry, Aunt Wang, I am very patient.
- 中文：放心吧王阿姨，我很有耐心的
- 起点回答：The character's emotional state is reassuring, positive, anxious.
- 赢家回答：The character's emotional state is comforting, supportive, positive.
- 起点抽取：[reassuring, positive, anxious]
- 赢家抽取：[comforting, supportive, positive]
- 最终极性：negative→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_POSITIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9847047513827027}, {"state": "AGR_RELEVANT", "relative_support": 0.015295248617297216}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.7552102783964466}, {"state": "AGC_INCONGRUENT", "relative_support": 0.13572556680321665}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.5214523666202621}, {"state": "AEX_EXPECTED", "relative_support": 0.47854763337973794}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5457371019932246}, {"state": "AAG_OTHER", "relative_support": 0.3768129827547729}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.5261907113326967}, {"state": "ACT_CERTAIN", "relative_support": 0.4738092886673034}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8244095494906343}, {"state": "ACP_LOW", "relative_support": 0.1755904505093657}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/video_0057_0015.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is patient, calm, reassuring.|
|long_graph_dataset_best|1.0000|The character's emotional state is patient, positive.|

## 150. SIMSv2 / video_0054_0032 — 相对自身起点恶化

- 参考：0.2；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：1.0000→0.0000；50权重零/错45次、满/对5次。
- 模型字幕：Feeling very honored, feeling scared, how do I act with him, we are not familiar with each other and have never acted together.
- 中文：特别尊贵的感觉，感觉很害怕，怎么和他对戏啊，也不熟两个人也没有演过戏
- 起点回答：The character's emotional state is nervous, uncertain, tense, excited.
- 赢家回答：The character's emotional state is honored, scared, anxious, uncertain, unfamiliar, inexperienced.
- 起点抽取：[nervous, uncertain, tense, excited]
- 赢家抽取：[honored, scared, anxious, uncertain, unfamiliar, inexperienced]
- 最终极性：positive→negative。
- 实际level：2；原因：['mixed_text_affect_or_evaluation']。
- Cue：TXT_AFFECT_WORD_POSITIVE, TXT_AFFECT_WORD_NEGATIVE, TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, TXT_RHETORICAL_QUESTION, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_FALLING, AUD_LAUGHTER_PRESENT, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6894881884918357}, {"state": "AGC_INCONGRUENT", "relative_support": 0.2883248706286899}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.5934487644377532}, {"state": "AEX_EXPECTED", "relative_support": 0.4065512355622468}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.44379834113763905}, {"state": "AAG_OTHER", "relative_support": 0.27848030958024755}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5109206442313721}, {"state": "ACT_UNCERTAIN", "relative_support": 0.489079355768628}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5629409025557726}, {"state": "ACP_LOW", "relative_support": 0.43705909744422755}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/video_0054_0032.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is nervous, uneasy, uncertain, surprised, joyful, stressed, tense.|
|long_graph_dataset_best|0.0000|The character's emotional state is anxious, uneasy, uncertain, confused, bewildered, under immense pressure.|

## 151. SIMSv2 / aqgy5_0006_00021 — 相对自身起点恶化

- 参考：0.6；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：1.0000→0.0000；50权重零/错28次、满/对22次。
- 模型字幕：It has been a long time since we watched the stars together like we are now.
- 中文：我们多久没有像现在一样一起看星星了。
- 起点回答：The character's emotional state is longing, nostalgia, warmth, contemplative, reflective.
- 赢家回答：The character's emotional state is nostalgia, longing, contemplation.
- 起点抽取：[longing, nostalgia, warmth, contemplative, reflective]
- 赢家抽取：[nostalgia, longing, contemplation]
- 最终极性：positive→negative。
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, AUD_PITCH_VARIABILITY_LOW, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8165723300685204}, {"state": "AGC_INCONGRUENT", "relative_support": 0.1693573251818875}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6420934391735351}, {"state": "AEX_UNEXPECTED", "relative_support": 0.3579065608264649}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.805376164469844}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.17330328622960434}], "APP_CERTAINTY": [], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.7948937344343318}, {"state": "ACP_LOW", "relative_support": 0.20510626556566827}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/aqgy5_0006_00021.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is longing, nostalgia, reflection, desire for shared experiences.|
|long_graph_dataset_best|1.0000|The character's emotional state is warmth, nostalgia, sentimentality, reflection.|

## 152. SIMSv2 / video_0045_0040 — 相对自身起点恶化

- 参考：-0.8；赢家：from_45_epoch_49_SIMSv2；起点epoch45。
- 质量：1.0000→0.0000；50权重零/错38次、满/对12次。
- 模型字幕：He really is just a fantasy.
- 中文：他真的就是个幻想
- 起点回答：The character's emotional state is surprised, admiring, sarcastic, disagreeable.
- 赢家回答：The character's emotional state is enthusiastic, passionate, humorous, playful.
- 起点抽取：[surprised, admiring, sarcastic, disagreeable]
- 赢家抽取：[enthusiastic, passionate, humorous, playful]
- 最终极性：negative→positive。
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_INTENSIFIER_PRESENT, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：disappointed, anger, despair（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.950459636683684}, {"state": "AGC_CONGRUENT", "relative_support": 0.033885333221936056}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5726327373086803}, {"state": "AEX_UNEXPECTED", "relative_support": 0.42736726269131986}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.4393092224903534}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.32081186776896814}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.830119150338631}, {"state": "ACT_UNCERTAIN", "relative_support": 0.16988084966136896}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9939627967726041}, {"state": "ACP_HIGH", "relative_support": 0.006037203227395977}]}
- 视频：/ai/sjq/AffectGPT/dataset/simsv2-process/video_new/video_0045_0040.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is enthusiastic, excited, passionate, critical, questioning, skeptical.|
|long_graph_dataset_best|1.0000|The character's emotional state is enthusiastic, passionate, confident, mocking, sarcastic, dissatisfaction, disapproval.|

## 153. OVMERDPlus / samplenew3_00055533 — 50权重持续错误/零命中

- 参考：serious, deep in thought, slightly nervous；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：Red
- 中文：
- 起点回答：The character's emotional state is excited, anticipating, red-related, tense.
- 赢家回答：The character's emotional state is excited, joyful, enthusiastic.
- 起点抽取：[excited, anticipating, tense]
- 赢家抽取：[excited, joyful, enthusiastic]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：AUD_INTONATION_RISING, AUD_LAUGHTER_PRESENT, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：joy, hopeful, manic（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.9344635881656707}, {"state": "AGC_INCONGRUENT", "relative_support": 0.06553641183432936}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.7883499875907807}, {"state": "AAG_SELF", "relative_support": 0.2116500124092193}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9750649430452953}, {"state": "ACT_CERTAIN", "relative_support": 0.02493505695470452}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 1.0}]}
- 逐轮映射：{"1": {"reference": [], "winner": ["happy", "surprised"]}, "2": {"reference": [], "winner": ["happy", "surprised"]}, "3": {"reference": [], "winner": ["joyful"]}, "4": {"reference": ["sad"], "winner": ["genius", "joy"]}, "5": {"reference": [], "winner": ["joyful", "powerful"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/samplenew3_00055533.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is excited, curious, amused, surprised.|
|long_graph_dataset_best|0.0000|The character's emotional state is excited, positive.|
|base35_A|0.0000|The character's emotional state is excited, positive.|
|base35_B|0.0000|The emotional state is excited, joyful, positive.|
|base35_C|0.0000|The character's emotional state is positive, excitement, joy, happiness.|
|base35_D|0.0000|The emotional state is excited, joyful, positive.|
|base35_E|0.0000|The character's emotional state is positive, excitement, joy, happiness.|
|base35_F|0.0000|The character's emotional state is positive, excitement, surprise.|
|graph40_A|0.0000|The character's emotional state is positive, joyful, enthusiastic.|
|graph40_B|0.0000|The character's emotional state is positive, joyful, surprised.|
|graph40_C|0.0000|The character's emotional state is positive, joyful, surprised.|
|graph40_D|0.0000|The character's emotional state is positive, joyful, surprised.|
|graph40_E|0.0000|The character's emotional state is positive, joyful, surprised.|
|graph40_F|0.0000|The character's emotional state is positive, joyful, surprised.|
|base35_G|0.0000|The character's emotional state is positive, excitement, surprise.|
|graph40_G|0.0000|The character's emotional state is positive, joyful, surprised.|

## 154. OVMERDPlus / sample_00000653 — 50权重持续错误/零命中

- 参考：sad；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：Extra care for my body.
- 中文：
- 起点回答：The character's emotional state is gratitude, appreciation, satisfaction.
- 赢家回答：The character's emotional state is positive, humorous, teasing.
- 起点抽取：[gratitude, appreciation, satisfaction]
- 赢家抽取：[positive, humorous, teasing]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_INTONATION_FALLING, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：hopeful, joy, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.9719956140095728}, {"state": "AGC_MIXED", "relative_support": 0.02800438599042715}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.703473707976485}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.29652629202351505}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.9349672475066811}, {"state": "ACT_UNCERTAIN", "relative_support": 0.0650327524933188}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.8568452437104124}, {"state": "ACP_LOW", "relative_support": 0.14315475628958754}]}
- 逐轮映射：{"1": {"reference": ["sad"], "winner": ["happy", "mad"]}, "2": {"reference": ["sad"], "winner": ["angry", "happy"]}, "3": {"reference": ["sad"], "winner": ["joyful"]}, "4": {"reference": ["sad"], "winner": []}, "5": {"reference": ["sad"], "winner": ["powerful"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00000653.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is playful, humorous, positive.|
|long_graph_dataset_best|0.0000|The character's emotional state is care, concern, interest, curiosity, pleasure, enjoyment.|
|base35_A|0.0000|The character's emotional state is grateful, happy.|
|base35_B|0.0000|The character's emotional state is grateful, cared-for, relaxed, satisfied.|
|base35_C|0.0000|The character's emotional state is desire, need, care, appreciation.|
|base35_D|0.0000|The character's emotional state is grateful, cared-for, relaxed, satisfied.|
|base35_E|0.0000|The character's emotional state is desire, need, care, appreciation.|
|base35_F|0.0000|The character's emotional state is positive, self-care, concern, appreciation.|
|graph40_A|0.0000|The character's emotional state is grateful, cared-for, relaxed, serene.|
|graph40_B|0.0000|The character's emotional state is grateful, cared-for, relaxed, serene.|
|graph40_C|0.0000|The character's emotional state is grateful, cared-for, relaxed, satisfied.|
|graph40_D|0.0000|The character's emotional state is grateful, cared-for, relaxed, serene.|
|graph40_E|0.0000|The character's emotional state is grateful, cared-for, relaxed, satisfied.|
|graph40_F|0.0000|The character's emotional state is grateful, cared-for, relaxed, serene.|
|base35_G|0.0000|The character's emotional state is positive, self-care, concern, appreciation.|
|graph40_G|0.0000|The character's emotional state is grateful, cared-for, relaxed, serene.|

## 155. OVMERDPlus / samplenew3_00098820 — 50权重持续错误/零命中

- 参考：embarrassment, hesitation；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：0.0000→0.0000；50权重零/错50次、满/对0次。
- 模型字幕：Good good good
- 中文：
- 起点回答：The character's emotional state is positive, happy, content.
- 赢家回答：The character's emotional state is positive, affirmative, excited.
- 起点抽取：[positive, happy, content]
- 赢家抽取：[positive, affirmative, excited]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_EVALUATION_POSITIVE, AUD_INTONATION_RISING, AUD_LAUGHTER_PRESENT, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, content（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8637927776566781}, {"state": "AGC_MIXED", "relative_support": 0.12428112573753715}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.6069226748541877}, {"state": "AEX_UNEXPECTED", "relative_support": 0.39307732514581234}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.48720504006668713}, {"state": "AAG_OTHER", "relative_support": 0.3366718627704842}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.5895188590510231}, {"state": "ACT_CERTAIN", "relative_support": 0.4104811409489768}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.9261755774513665}, {"state": "ACP_LOW", "relative_support": 0.07382442254863354}]}
- 逐轮映射：{"1": {"reference": ["disgusted", "sad"], "winner": ["happy", "surprised"]}, "2": {"reference": ["disgusted", "sad"], "winner": ["happy"]}, "3": {"reference": ["sad"], "winner": ["joyful"]}, "4": {"reference": ["anger", "disgust"], "winner": ["genius"]}, "5": {"reference": ["sad"], "winner": ["joyful", "powerful"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/samplenew3_00098820.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is positive, satisfaction, acceptance.|
|long_graph_dataset_best|0.0000|The character's emotional state is positive, happy, relaxed, excited, nervous.|
|base35_A|0.0000|The character's emotional state is positive, affirmative, encouraging.|
|base35_B|0.0000|The emotional state is positive, excitement, happiness.|
|base35_C|0.0000|The character's emotional state is positive, enthusiastic, joyful, satisfied.|
|base35_D|0.0000|The emotional state is positive, excitement, happiness.|
|base35_E|0.0000|The character's emotional state is positive, enthusiastic, joyful, satisfied.|
|base35_F|0.0000|The character's emotional state is positive, enthusiastic, joyful, satisfied.|
|graph40_A|0.0000|The character's emotional state is positive, affirmative, confident.|
|graph40_B|0.0000|The character's emotional state is positive, affirmative, confident.|
|graph40_C|0.0000|The character's emotional state is positive, affirmative, confident.|
|graph40_D|0.0000|The character's emotional state is positive, affirmative, confident.|
|graph40_E|0.0000|The character's emotional state is positive, affirmative, confident.|
|graph40_F|0.0000|The character's emotional state is positive, affirmative, confident.|
|base35_G|0.0000|The character's emotional state is positive, enthusiastic, joyful, satisfied.|
|graph40_G|0.0000|The character's emotional state is positive, affirmative, confident.|

## 156. OVMERDPlus / sample_00002078 — 50权重持续正确/满命中

- 参考：negative emotions, criticism, anger, dissatisfaction；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：No woman can bear it. Not to mention that it's your fault first.
- 中文：
- 起点回答：The character's emotional state is angry, frustrated.
- 赢家回答：The character's emotional state is anger, frustration.
- 起点抽取：[angry, frustrated]
- 赢家抽取：[anger, frustration]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER, TXT_EXPLICIT_FAILURE_LOSS_OUTCOME, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_LOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_FURROWED, VIS_EYES_SQUINTED, VIS_MOUTH_CORNERS_DOWN
- 图候选：disappointed, despair, depressed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9861295238107278}, {"state": "AGR_RELEVANT", "relative_support": 0.013870476189272148}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.865611674942576}, {"state": "AGC_MIXED", "relative_support": 0.09290572318082355}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7259193553476742}, {"state": "AEX_UNEXPECTED", "relative_support": 0.27408064465232584}], "APP_AGENCY": [{"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4028056400297188}, {"state": "AAG_SELF", "relative_support": 0.3843835856147778}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.6774793932328383}, {"state": "ACT_UNCERTAIN", "relative_support": 0.32252060676716154}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9957473296577897}, {"state": "ACP_HIGH", "relative_support": 0.0042526703422103825}]}
- 逐轮映射：{"1": {"reference": ["mad", "sad"], "winner": ["mad", "sad"]}, "2": {"reference": ["angry", "sad"], "winner": ["angry", "sad"]}, "3": {"reference": ["mad"], "winner": ["mad"]}, "4": {"reference": ["anger", "sad"], "winner": ["anger", "sad"]}, "5": {"reference": ["mad"], "winner": ["mad"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00002078.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is anger, frustration.|
|long_graph_dataset_best|1.0000|The character's emotional state is anger, frustration.|
|base35_A|1.0000|The character's emotional state is anger, frustration.|
|base35_B|1.0000|The character's emotional state is anger, frustration.|
|base35_C|1.0000|The character's emotional state is anger, frustration.|
|base35_D|1.0000|The character's emotional state is anger, frustration.|
|base35_E|0.8667|The character's emotional state is sadness, anger.|
|base35_F|0.8667|The character's emotional state is sadness, anger.|
|graph40_A|1.0000|The character's emotional state is anger, frustration.|
|graph40_B|1.0000|The character's emotional state is anger, frustration.|
|graph40_C|1.0000|The character's emotional state is anger, frustration.|
|graph40_D|1.0000|The character's emotional state is anger, frustration.|
|graph40_E|1.0000|The character's emotional state is anger, frustration.|
|graph40_F|1.0000|The character's emotional state is anger, frustration.|
|base35_G|1.0000|The character's emotional state is anger, frustration.|
|graph40_G|1.0000|The character's emotional state is anger, frustration.|

## 157. OVMERDPlus / sample_00000338 — 50权重持续正确/满命中

- 参考：anxiety, nervousness, worry；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：1.0000→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：Oh no, my phone and wallet are both in the bag.
- 中文：
- 起点回答：The character's emotional state is anxiety, tension.
- 赢家回答：The character's emotional state is worry, anxiety.
- 起点抽取：[anxiety, tension]
- 赢家抽取：[worry, anxiety]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_NEGATION_PRESENT, TXT_EXCLAMATION_INTERJECTION, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_LOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, AUD_INTONATION_FLAT, VIS_BROWS_FURROWED, VIS_MOUTH_CORNERS_DOWN, VIS_LIPS_PRESSED
- 图候选：depressed, despair, helpless（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.7595864389264548}, {"state": "AGC_MIXED", "relative_support": 0.16511938413825103}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7143972141226291}, {"state": "AEX_UNEXPECTED", "relative_support": 0.28560278587737087}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5315497106677483}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.40218585100501436}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.548864126562009}, {"state": "ACT_UNCERTAIN", "relative_support": 0.45113587343799094}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9856415091241488}, {"state": "ACP_HIGH", "relative_support": 0.014358490875851296}]}
- 逐轮映射：{"1": {"reference": ["scared"], "winner": ["scared"]}, "2": {"reference": ["fearful"], "winner": ["fearful"]}, "3": {"reference": ["scared"], "winner": ["scared"]}, "4": {"reference": ["fear"], "winner": ["fear"]}, "5": {"reference": ["scared"], "winner": ["scared"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00000338.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is anxiety, tension, concern, urgency.|
|long_graph_dataset_best|1.0000|The character's emotional state is anxiety, concern.|
|base35_A|1.0000|The character's emotional state is worry, anxiety.|
|base35_B|0.6667|The character's emotional state is worry, anxiety, sadness.|
|base35_C|1.0000|The character's emotional state is worry, anxiety.|
|base35_D|0.6667|The character's emotional state is worry, anxiety, sadness.|
|base35_E|0.1000|The character's emotional state is sad, fear, disgust.|
|base35_F|1.0000|The character's emotional state is worry, anxiety.|
|graph40_A|1.0000|The character's emotional state is worry, anxiety.|
|graph40_B|1.0000|The character's emotional state is worry, anxiety.|
|graph40_C|1.0000|The character's emotional state is worry, anxiety.|
|graph40_D|1.0000|The character's emotional state is worry, anxiety.|
|graph40_E|1.0000|The character's emotional state is worry, anxiety.|
|graph40_F|1.0000|The character's emotional state is worry, anxiety.|
|base35_G|1.0000|The character's emotional state is worry, anxiety.|
|graph40_G|1.0000|The character's emotional state is worry, anxiety.|

## 158. OVMERDPlus / sample_00003211 — 50权重持续正确/满命中

- 参考：angry, dissatisfied；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：0.8667→1.0000；50权重零/错0次、满/对50次。
- 模型字幕：I look at him and he seems like a normal person, fundamentally. However, he lacks basic manners and etiquette.
- 中文：
- 起点回答：The character's emotional state is anger, frustration, dissatisfaction, disappointment.
- 赢家回答：The character's emotional state is anger, frustration.
- 起点抽取：[anger, frustration, dissatisfaction, disappointment]
- 赢家抽取：[anger, frustration]
- 实际level：2；原因：['emotion_support_not_separated', 'mixed_text_affect_or_evaluation']。
- Cue：TXT_EVALUATION_POSITIVE, TXT_EVALUATION_NEGATIVE, TXT_CONTRAST_PRESENT, AUD_SPEECH_RATE_REL_FAST, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_LEVEL_REL_HIGH, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, AUD_INTONATION_FALLING, VIS_BROWS_FURROWED, VIS_EYES_WIDENED, VIS_MOUTH_CORNERS_DOWN, VIS_GRIMACE_PRESENT
- 图候选：anger, disappointed, depressed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.907894220683303}, {"state": "AGR_RELEVANT", "relative_support": 0.09210577931669703}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.4060772971940575}, {"state": "AGC_CONGRUENT", "relative_support": 0.3336223180986293}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.7273899184963969}, {"state": "AEX_EXPECTED", "relative_support": 0.2726100815036031}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.6864958365495967}, {"state": "AAG_SELF", "relative_support": 0.17333242539467356}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.5517014119998743}, {"state": "ACT_CERTAIN", "relative_support": 0.44829858800012556}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6610419001192441}, {"state": "ACP_HIGH", "relative_support": 0.33895809988075587}]}
- 逐轮映射：{"1": {"reference": ["mad", "sad"], "winner": ["mad", "sad"]}, "2": {"reference": ["angry", "sad"], "winner": ["angry", "sad"]}, "3": {"reference": ["mad"], "winner": ["mad"]}, "4": {"reference": ["anger", "sad"], "winner": ["anger", "sad"]}, "5": {"reference": ["mad"], "winner": ["mad"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00003211.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is anger, dissatisfaction.|
|long_graph_dataset_best|0.5467|The character's emotional state is disapproval, dissatisfaction, frustration, anxiety.|
|base35_A|1.0000|The character's emotional state is anger, dissatisfaction.|
|base35_B|1.0000|The character's emotional state is anger, dissatisfaction.|
|base35_C|1.0000|The character's emotional state is anger, frustration.|
|base35_D|1.0000|The character's emotional state is anger, dissatisfaction.|
|base35_E|1.0000|The character's emotional state is anger, frustration.|
|base35_F|1.0000|The character's emotional state is anger, frustration.|
|graph40_A|1.0000|The character's emotional state is anger, frustration.|
|graph40_B|1.0000|The character's emotional state is anger, frustration.|
|graph40_C|1.0000|The character's emotional state is anger, dissatisfaction.|
|graph40_D|1.0000|The character's emotional state is anger, frustration.|
|graph40_E|1.0000|The character's emotional state is anger, dissatisfaction.|
|graph40_F|1.0000|The character's emotional state is anger, dissatisfaction.|
|base35_G|1.0000|The character's emotional state is anger, frustration.|
|graph40_G|1.0000|The character's emotional state is anger, dissatisfaction.|

## 159. OVMERDPlus / sample_00002465 — 赢家零/错，其他权重经常命中/对

- 参考：sadness, negativity, heartbreak, melancholy；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：0.5133→0.0000；50权重零/错13次、满/对3次。
- 模型字幕：
- 中文：
- 起点回答：The character's emotional state is sadness, distress, support, empathy.
- 赢家回答：The character's emotional state is worry, anxiety, concern, focus, determination.
- 起点抽取：[sadness, distress, support, empathy]
- 赢家抽取：[worry, anxiety, concern, determination]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FLAT, VIS_MOUTH_CORNERS_DOWN, VIS_LIPS_PRESSED, VIS_HEAD_LOWERED
- 图候选：depressed, despair, ashamed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.6195103147205009}, {"state": "AGC_MIXED", "relative_support": 0.306857180562976}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.9406651154830935}, {"state": "AEX_UNEXPECTED", "relative_support": 0.059334884516906584}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5663712462581802}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.420250221604649}], "APP_CERTAINTY": [], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9843809149571668}, {"state": "ACP_HIGH", "relative_support": 0.015619085042833141}]}
- 逐轮映射：{"1": {"reference": ["sad"], "winner": ["scared"]}, "2": {"reference": ["bad", "sad"], "winner": ["fearful"]}, "3": {"reference": ["sad"], "winner": ["scared"]}, "4": {"reference": ["sad"], "winner": ["fear", "genius"]}, "5": {"reference": ["sad"], "winner": ["scared"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00002465.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.0000|The character's emotional state is concerned, anxious.|
|long_graph_dataset_best|0.0800|The character's emotional state is stressed, anxious, calm, tranquil, happy, peaceful.|
|base35_A|0.9333|The character's emotional state is indifferent, unresponsive.|
|base35_B|0.6333|The emotional state is calm, indifferent, unenthusiastic, neutral.|
|base35_C|0.9333|The character's emotional state is indifferent, unresponsive, negative.|
|base35_D|0.6333|The character's emotional state is sad, fearful, anxious, under pressure, helpless, desperate.|
|base35_E|0.5467|The character's emotional state is sad, fearful, disgusted.|
|base35_F|0.5467|The character's emotional state is sad, fear, disgust.|
|graph40_A|0.0000|The character's emotional state is worry, anxiety, tension.|
|graph40_B|0.0000|The character's emotional state is worry, anxiety, tension.|
|graph40_C|0.0000|The character's emotional state is worry, anxiety, tension.|
|graph40_D|0.0000|The character's emotional state is worry, anxiety, tension.|
|graph40_E|0.0000|The character's emotional state is worry, anxiety, tension.|
|graph40_F|0.0000|The character's emotional state is worry, anxiety, tension.|
|base35_G|0.9333|The character's emotional state is indifferent, unresponsive, negative.|
|graph40_G|0.5000|The character's emotional state is worry, anxiety, responsibility.|

## 160. OVMERDPlus / sample_00000680 — 赢家零/错，其他权重经常命中/对

- 参考：shy, relaxed, positive, grateful, happy；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：0.0000→0.0000；50权重零/错7次、满/对0次。
- 模型字幕：Last night, I forgot to properly thank you.
- 中文：
- 起点回答：The character's emotional state is gratitude, apology.
- 赢家回答：The character's emotional state is gratitude, apology, friendliness, positivity.
- 起点抽取：[gratitude, apology]
- 赢家抽取：[gratitude, apology, friendliness, positivity]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_NEGATION_PRESENT, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT, VIS_HEAD_LOWERED
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.6777346643235901}, {"state": "AGC_INCONGRUENT", "relative_support": 0.24954725814059545}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.8770934527200189}, {"state": "AEX_UNEXPECTED", "relative_support": 0.12290654727998103}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6066499903809932}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.3933500096190068}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7990741369454255}, {"state": "ACT_UNCERTAIN", "relative_support": 0.20092586305457455}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.6070661123185773}, {"state": "ACP_HIGH", "relative_support": 0.3929338876814227}]}
- 逐轮映射：{"1": {"reference": ["happy"], "winner": []}, "2": {"reference": ["happy"], "winner": []}, "3": {"reference": ["joyful", "peaceful", "powerful"], "winner": []}, "4": {"reference": ["joy"], "winner": []}, "5": {"reference": ["peaceful", "powerful", "sad"], "winner": []}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00000680.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.8000|The character's emotional state is gratitude, apology, appreciation.|
|long_graph_dataset_best|0.6467|The character's emotional state is grateful, apologetic, friendly, grateful.|
|base35_A|0.6333|The character's emotional state is gratitude, apology, curiosity, interest, enjoyment.|
|base35_B|0.0000|The emotional state is gratitude, apology, slight anxiety, tension.|
|base35_C|0.8000|The character's emotional state is gratitude, apology, appreciation.|
|base35_D|0.0000|The emotional state is gratitude, apology, slight anxiety, tension.|
|base35_E|0.8000|The character's emotional state is gratitude, apology, appreciation.|
|base35_F|0.8000|The character's emotional state is gratitude, apology, appreciation.|
|graph40_A|0.0000|The character's emotional state is gratitude, apology.|
|graph40_B|0.0000|The character's emotional state is gratitude, apology, friendliness, positivity.|
|graph40_C|0.0000|The character's emotional state is gratitude, apology.|
|graph40_D|0.0000|The character's emotional state is gratitude, apology, friendliness, positivity.|
|graph40_E|0.0000|The character's emotional state is gratitude, apology.|
|graph40_F|0.3800|The character's emotional state is gratitude, apology, excitement, anticipation, nervousness.|
|base35_G|0.8000|The character's emotional state is gratitude, apology, appreciation.|
|graph40_G|0.3800|The character's emotional state is gratitude, apology, excitement, anticipation, nervousness.|

## 161. OVMERDPlus / sample_00000877 — 相对自身起点改善

- 参考：concern, worry；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：0.9333→1.0000；50权重零/错0次、满/对49次。
- 模型字幕：Did the surgery go smoothly?
- 中文：
- 起点回答：The character's emotional state is concerned, tense.
- 赢家回答：The character's emotional state is tension, anxiety.
- 起点抽取：[concerned, tense]
- 赢家抽取：[tension, anxiety]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_UNCERTAINTY_HEDGE, TXT_RHETORICAL_QUESTION, AUD_SPEECH_RATE_REL_SLOW, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED
- 图候选：sceptical, hesitant, bewildered（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5564590012241297}, {"state": "AGC_CONGRUENT", "relative_support": 0.3883955441482711}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.8910133448681307}, {"state": "AEX_EXPECTED", "relative_support": 0.10898665513186938}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.4996437507487078}, {"state": "AAG_SELF", "relative_support": 0.27161531814710593}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.9954238068800388}, {"state": "ACT_CERTAIN", "relative_support": 0.004576193119961089}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5249924195288932}, {"state": "ACP_HIGH", "relative_support": 0.47500758047110675}]}
- 逐轮映射：{"1": {"reference": ["scared"], "winner": ["scared"]}, "2": {"reference": ["fearful"], "winner": ["fearful"]}, "3": {"reference": ["scared"], "winner": ["scared"]}, "4": {"reference": ["fear"], "winner": ["fear"]}, "5": {"reference": ["scared"], "winner": ["scared"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00000877.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|1.0000|The character's emotional state is tension, anxiety, concern.|
|long_graph_dataset_best|1.0000|The character's emotional state is anxiety, tension, concern.|
|base35_A|1.0000|The character's emotional state is tension, anxiety.|
|base35_B|1.0000|The character's emotional state is concern, anxiety.|
|base35_C|1.0000|The character's emotional state could be anxiety, concern.|
|base35_D|1.0000|The character's emotional state is concern, anxiety.|
|base35_E|1.0000|The character's emotional state is concern, anxiety.|
|base35_F|1.0000|The character's emotional state could be anxiety, tension.|
|graph40_A|1.0000|The character's emotional state is tension, anxiety.|
|graph40_B|1.0000|The character's emotional state is tension, anxiety.|
|graph40_C|1.0000|The character's emotional state is tension, anxiety.|
|graph40_D|1.0000|The character's emotional state is tension, anxiety.|
|graph40_E|1.0000|The character's emotional state is tension, anxiety.|
|graph40_F|1.0000|The character's emotional state is tension, anxiety.|
|base35_G|1.0000|The character's emotional state could be anxiety, tension, concern, worry.|
|graph40_G|1.0000|The character's emotional state is tension, anxiety.|

## 162. OVMERDPlus / samplenew3_00019671 — 相对自身起点改善

- 参考：joy, humor, happiness, emphasis；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：0.0000→0.6000；50权重零/错10次、满/对1次。
- 模型字幕：The chicken table needs to be disinfected.
- 中文：
- 起点回答：The character's emotional state is neutral, informative, advisory.
- 赢家回答：The character's emotional state is calm, rational.
- 起点抽取：[neutral]
- 赢家抽取：[calm, rational]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_HIGH, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_WIDENED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, manic（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8749855756123379}, {"state": "AGC_INCONGRUENT", "relative_support": 0.09493306751248917}], "APP_EXPECTEDNESS": [{"state": "AEX_UNEXPECTED", "relative_support": 0.6024652366197015}, {"state": "AEX_EXPECTED", "relative_support": 0.39753476338029853}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5667013900125872}, {"state": "AAG_OTHER", "relative_support": 0.2786486908771073}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.8958862965587596}, {"state": "ACT_CERTAIN", "relative_support": 0.10411370344124037}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.825227606930058}, {"state": "ACP_LOW", "relative_support": 0.17477239306994186}]}
- 逐轮映射：{"1": {"reference": ["happy"], "winner": ["happy"]}, "2": {"reference": ["happy"], "winner": ["happy"]}, "3": {"reference": ["joyful"], "winner": ["peaceful"]}, "4": {"reference": ["joy"], "winner": ["joy"]}, "5": {"reference": ["powerful"], "winner": ["peaceful"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/samplenew3_00019671.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.4267|The character's emotional state is concerned, careful, cautious, aware, positive.|
|long_graph_dataset_best|0.5333|The character's emotional state is calm, focused.|
|base35_A|0.6000|The character's emotional state is calm, rational.|
|base35_B|0.8000|The emotional state is positive, engaged, interested.|
|base35_C|0.6667|The character's emotional state is excited, amused, positive, suggestion, reminder.|
|base35_D|0.8000|The emotional state is positive, engaged, interested.|
|base35_E|0.6667|The character's emotional state is excited, amused, positive, suggestion, reminder.|
|base35_F|0.3333|The character's emotional state is excited, enthusiastic.|
|graph40_A|0.0000|The character's emotional state is concerned, cautious.|
|graph40_B|0.0000|The character's emotional state is concerned, cautious.|
|graph40_C|0.0000|The character's emotional state is concerned, cautious.|
|graph40_D|0.0000|The character's emotional state is concerned, cautious.|
|graph40_E|0.0000|The character's emotional state is concerned, cautious.|
|graph40_F|0.0000|The character's emotional state is concerned, cautious.|
|base35_G|0.3333|The character's emotional state is excited, enthusiastic.|
|graph40_G|0.0000|The character's emotional state is concerned, cautious.|

## 163. OVMERDPlus / samplenew3_00090533 — 相对自身起点改善

- 参考：worried, joyful, relaxed, nervous, pleading；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：0.3333→0.5800；50权重零/错1次、满/对0次。
- 模型字幕：It seems like you spared the two of us, right? Let's not write calligraphy, we can't do it.
- 中文：
- 起点回答：The character's emotional state is teasing, humor, playful.
- 赢家回答：The character's emotional state is appreciative, celebratory, positive.
- 起点抽取：[teasing, humor, playful]
- 赢家抽取：[appreciative, celebratory, positive]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_NEGATIVE, TXT_NEGATION_PRESENT, TXT_RHETORICAL_QUESTION, TXT_DESIRE_NEED, TXT_EXPLICIT_CAUSAL_ATTRIBUTION_OTHER, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：disappointed, joy, hopeful（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_IRRELEVANT", "relative_support": 0.9907342383913419}, {"state": "AGR_RELEVANT", "relative_support": 0.009265761608658007}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5244557249943483}, {"state": "AGC_INCONGRUENT", "relative_support": 0.43951384855284914}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.7120306900770793}, {"state": "AEX_UNEXPECTED", "relative_support": 0.28796930992292075}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.448826161343833}, {"state": "AAG_OTHER", "relative_support": 0.3145737358992619}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.5866216364994715}, {"state": "ACT_UNCERTAIN", "relative_support": 0.4133783635005284}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.5429566474599332}, {"state": "ACP_HIGH", "relative_support": 0.45704335254006684}]}
- 逐轮映射：{"1": {"reference": ["happy", "scared"], "winner": ["happy"]}, "2": {"reference": ["fearful", "happy"], "winner": ["happy"]}, "3": {"reference": ["joyful", "peaceful", "scared"], "winner": ["joyful", "powerful"]}, "4": {"reference": ["fear", "joy"], "winner": ["joy"]}, "5": {"reference": ["peaceful", "powerful", "scared"], "winner": ["powerful"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/samplenew3_00090533.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.6533|The character's emotional state is joking, teasing, relaxed, positive.|
|long_graph_dataset_best|0.7200|The character's emotional state is positive, humorous, relaxed.|
|base35_A|0.5133|The character's emotional state is teasing, jest, playful, positive.|
|base35_B|0.5933|Observing cues from the video, such as the young person's raised eyebrows, squinted eyes, and smile, it can be inferred that he is experiencing a moment of happiness and enjoyment. These clues suggest that he feels relaxed and content, possibly because he is enjoying a pleasant moment or engaging in an enjoyable activity. The overall impression is one of positive emotions, possibly happiness, enjoyment, or satisfaction. Given the negative evaluation in the audio clues, it can be deduced that this statement might be a form of teasing or joking manner, which alignss well with the overall positive mood displayed by the young person.|
|base35_C|0.6133|The character's emotional state is teasing, challenge, frustration, self-blame, anxiety, tension, humor, optimism.|
|base35_D|0.5933|Observing cues from the video, such as the young person's raised eyebrows, squinted eyes, and smile, it can be inferred that he is experiencing a moment of happiness and enjoyment. These clues suggest that he feels relaxed and content, possibly because he is enjoying a pleasant moment or engaging in an enjoyable activity. The overall impression is one of positive emotions, possibly happiness, enjoyment, or satisfaction. Given the negative evaluation in the audio clues, it can be deduced that this statement might be a form of teasing or joking manner, which alignss well with the overall positive mood displayed by the young person.|
|base35_E|0.6133|The character's emotional state is teasing, challenge, frustration, self-blame, anxiety, tension, humor, optimism.|
|base35_F|0.1600|The character's emotional state is teasing, challenge, frustration, disappointment.|
|graph40_A|0.4467|The character's emotional state is positive, confident, knowledgeable.|
|graph40_B|0.4467|The character's emotional state is positive, confident, encouraging.|
|graph40_C|0.4467|The character's emotional state is positive, confident, encouraging.|
|graph40_D|0.4467|The character's emotional state is positive, confident, encouraging.|
|graph40_E|0.4467|The character's emotional state is positive, confident, encouraging.|
|graph40_F|0.4467|The character's emotional state is positive, confident, encouraging.|
|base35_G|0.1600|The character's emotional state is teasing, challenge, frustration, disappointment.|
|graph40_G|0.4467|The character's emotional state is positive, confident, encouraging.|

## 164. OVMERDPlus / samplenew3_00019990 — 相对自身起点恶化

- 参考：concern, contemplation, thinking, worry, seriousness, deep thought；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：0.6333→0.2667；50权重零/错4次、满/对0次。
- 模型字幕：The tomb is built in the attic, he will definitely be scared.
- 中文：
- 起点回答：The character's emotional state is fearful, surprised.
- 赢家回答：The character's emotional state is humorous, teasing, calm, relaxed.
- 起点抽取：[fearful, surprised]
- 赢家抽取：[humorous, teasing, calm, relaxed]
- 实际level：3；原因：['supported_full_evidence']。
- Cue：TXT_AFFECT_WORD_NEGATIVE, TXT_INTENSIFIER_PRESENT, AUD_SPEECH_RATE_REL_SLOW, AUD_VOCAL_INTENSITY_REL_LOW, AUD_PITCH_VARIABILITY_LOW, AUD_PAUSE_LONG, AUD_INTONATION_FALLING, VIS_LIPS_PRESSED
- 图候选：ashamed, pity, depressed（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [], "APP_GOAL_CONGRUENCE": [{"state": "AGC_INCONGRUENT", "relative_support": 0.5762836946222175}, {"state": "AGC_MIXED", "relative_support": 0.2745879160332152}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.5709739174119989}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.4290260825880012}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7831079510760881}, {"state": "ACT_UNCERTAIN", "relative_support": 0.2168920489239119}], "APP_COPING_POTENTIAL": [{"state": "ACP_LOW", "relative_support": 0.9628690341345486}, {"state": "ACP_HIGH", "relative_support": 0.03713096586545138}]}
- 逐轮映射：{"1": {"reference": ["scared"], "winner": ["happy", "mad"]}, "2": {"reference": ["fearful"], "winner": ["angry", "happy"]}, "3": {"reference": ["peaceful", "scared"], "winner": ["peaceful"]}, "4": {"reference": ["fear", "sad"], "winner": ["joy"]}, "5": {"reference": ["peaceful", "scared"], "winner": ["peaceful"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/samplenew3_00019990.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.7333|The character's emotional state is scared, tense, uneasy.|
|long_graph_dataset_best|0.1800|The character's emotional state is humorous, exaggerated, fear, tension, anger, frustration.|
|base35_A|0.2333|The character's emotional state is fear, surprise.|
|base35_B|0.7333|The character's emotional state is tense, fearful, anxious.|
|base35_C|0.6333|The character's emotional state is tense, fearful, uncertain.|
|base35_D|0.2333|The character's emotional state is fear, sadness.|
|base35_E|0.5200|The character's emotional state is sad, joyful, fearful.|
|base35_F|0.2000|The character's emotional state is fear.|
|graph40_A|0.2667|The character's emotional state is humorous, teasing, calm, tranquil.|
|graph40_B|0.2667|The character's emotional state is humorous, teasing, calm, tranquil.|
|graph40_C|0.2667|The character's emotional state is humorous, teasing, calm, tranquil.|
|graph40_D|0.2667|The character's emotional state is humorous, teasing, calm, tranquil.|
|graph40_E|0.2667|The character's emotional state is humorous, teasing, calm, tranquil.|
|graph40_F|0.2667|The character's emotional state is humorous, teasing, calm, tranquil.|
|base35_G|0.5333|The character's emotional state is fear, unease, tension, contemplation, sadness, stress.|
|graph40_G|0.0000|The character's emotional state is humorous, teasing, positive.|

## 165. OVMERDPlus / sample_00000215 — 相对自身起点恶化

- 参考：relaxed, agree, positive, accept, pleasant, happy；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：0.8933→0.7267；50权重零/错0次、满/对0次。
- 模型字幕：This matter is easy to handle.
- 中文：
- 起点回答：The character's emotional state is positive, happy, satisfied.
- 赢家回答：The character's emotional state is positive, confident, optimistic, happy, excited.
- 起点抽取：[positive, happy, satisfied]
- 赢家抽取：[positive, confident, optimistic, happy, excited]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_EVALUATION_POSITIVE, AUD_INTONATION_RISING, VIS_BROWS_RAISED, VIS_EYES_SQUINTED, VIS_SMILE_PRESENT
- 图候选：joy, hopeful, appreciated（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.8383292320158935}, {"state": "AGC_MIXED", "relative_support": 0.1449160275327937}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 0.5170475250892943}, {"state": "AEX_UNEXPECTED", "relative_support": 0.48295247491070564}], "APP_AGENCY": [{"state": "AAG_OTHER", "relative_support": 0.4713295534245284}, {"state": "AAG_SELF", "relative_support": 0.4195391632652634}], "APP_CERTAINTY": [{"state": "ACT_UNCERTAIN", "relative_support": 0.6696503833075439}, {"state": "ACT_CERTAIN", "relative_support": 0.3303496166924561}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.9554287730226436}, {"state": "ACP_LOW", "relative_support": 0.04457122697735634}]}
- 逐轮映射：{"1": {"reference": ["happy"], "winner": ["happy", "surprised"]}, "2": {"reference": ["happy"], "winner": ["happy"]}, "3": {"reference": ["joyful", "peaceful"], "winner": ["joyful", "powerful"]}, "4": {"reference": ["joy"], "winner": ["genius", "joy"]}, "5": {"reference": ["joyful", "peaceful", "powerful"], "winner": ["joyful", "powerful"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/sample_00000215.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.9600|The character's emotional state is relaxed, joyful.|
|long_graph_dataset_best|0.6000|The character's emotional state is confident, optimistic, positive.|
|base35_A|0.8533|The character's emotional state is positive, confident, satisfied, happy.|
|base35_B|0.5667|The emotional state is contentment, excitement.|
|base35_C|0.8533|The character's emotional state is positive, confident, satisfied, happy.|
|base35_D|0.5667|The emotional state is contentment, excitement.|
|base35_E|0.8533|The character's emotional state is positive, confident, satisfied, happy.|
|base35_F|0.8533|The character's emotional state is positive, confident, satisfied, happy.|
|graph40_A|0.7267|The character's emotional state is positive, confident, optimistic, happy, excited.|
|graph40_B|0.7267|The character's emotional state is positive, confident, optimistic, happy, excited.|
|graph40_C|0.7267|The character's emotional state is positive, confident, optimistic, happy, excited.|
|graph40_D|0.7267|The character's emotional state is positive, confident, optimistic, happy, excited.|
|graph40_E|0.7267|The character's emotional state is positive, confident, optimistic, happy, excited.|
|graph40_F|0.7267|The character's emotional state is positive, confident, optimistic, happy, excited.|
|base35_G|0.8533|The character's emotional state is positive, confident, satisfied, happy.|
|graph40_G|0.7267|The character's emotional state is positive, confident, optimistic, happy, excited.|

## 166. OVMERDPlus / samplenew3_00024731 — 相对自身起点恶化

- 参考：worried, focused, alert, concerned, serious, cautious, vigilant；赢家：from_35_epoch_40_OVMERDPlus；起点epoch35。
- 质量：0.8000→0.0800；50权重零/错0次、满/对0次。
- 模型字幕：Be more careful later.
- 中文：
- 起点回答：The character's emotional state is caution, concern.
- 赢家回答：The character's emotional state is care, reminder, hopeful.
- 起点抽取：[caution, concern]
- 赢家抽取：[care, hopeful]
- 实际level：2；原因：['emotion_support_not_separated']。
- Cue：TXT_INTENSIFIER_PRESENT, TXT_DESIRE_NEED, AUD_SPEECH_RATE_REL_SLOW, AUD_PITCH_VARIABILITY_LOW, AUD_INTONATION_FALLING, VIS_LIPS_PRESSED
- 图候选：delightful, content, joy（仅实际level3展示）。
- Appraisal：{"APP_GOAL_RELEVANCE": [{"state": "AGR_RELEVANT", "relative_support": 1.0}], "APP_GOAL_CONGRUENCE": [{"state": "AGC_CONGRUENT", "relative_support": 0.5142948944079025}, {"state": "AGC_MIXED", "relative_support": 0.32373861213923455}], "APP_EXPECTEDNESS": [{"state": "AEX_EXPECTED", "relative_support": 1.0}], "APP_AGENCY": [{"state": "AAG_SELF", "relative_support": 0.6317335998444752}, {"state": "AAG_CIRCUMSTANCE", "relative_support": 0.36826640015552475}], "APP_CERTAINTY": [{"state": "ACT_CERTAIN", "relative_support": 0.7800611918816869}, {"state": "ACT_UNCERTAIN", "relative_support": 0.21993880811831315}], "APP_COPING_POTENTIAL": [{"state": "ACP_HIGH", "relative_support": 0.5706071075677734}, {"state": "ACP_LOW", "relative_support": 0.42939289243222645}]}
- 逐轮映射：{"1": {"reference": ["scared"], "winner": ["happy"]}, "2": {"reference": ["fearful"], "winner": ["happy"]}, "3": {"reference": ["powerful", "scared"], "winner": ["joyful", "peaceful"]}, "4": {"reference": ["anger", "fear", "genius", "sad"], "winner": ["genius"]}, "5": {"reference": ["joyful", "scared"], "winner": ["peaceful", "powerful"]}}
- 视频：/ai/sjq/AffectGPT/dataset/ovmerdplus-process/video/samplenew3_00024731.mp4

|历史/提示对照|诊断质量|原回答|
|---|---:|---|
|original_dataset_best|0.8000|The character's emotional state is caution, concern.|
|long_graph_dataset_best|0.7333|The character's emotional state is concerned, caution, tension, anxiety.|
|base35_A|0.8381|The character's emotional state is serious, cautious, concerned, worried.|
|base35_B|0.1333|The character's emotional state is serious, cautious.|
|base35_C|0.7333|The character's emotional state is anxious, tense, cautious, worried.|
|base35_D|0.1333|The character's emotional state is serious, cautious.|
|base35_E|0.7333|The character's emotional state is anxious, tense, cautious, worried.|
|base35_F|0.3143|The emotional state is calm, peaceful, overwhelmed, stressed.|
|graph40_A|0.7467|The character's emotional state is concern, reminder.|
|graph40_B|0.7467|The character's emotional state is concern, reminder.|
|graph40_C|0.8000|The character's emotional state is concern, reminder, cautious.|
|graph40_D|0.7467|The character's emotional state is concern, reminder.|
|graph40_E|0.8000|The character's emotional state is concern, reminder, cautious.|
|graph40_F|0.7467|The character's emotional state is concern, reminder.|
|base35_G|0.3143|The emotional state is calm, peaceful, overwhelmed, stressed.|
|graph40_G|0.7467|The character's emotional state is concern, reminder.|
