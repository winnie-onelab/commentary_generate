# commentary_generate

根據組合生成台詞

# How to use
```bash
# 1. add .env under the project

# 2. run the code
#    can use multiple group types, for example --type CR RC_YC
python commentary.py --type <group type>
```

|group type | description |
|----------|--------------|
|CR | 角球次數分析 |
|RC_YC | 紅黃牌數據分析 |
|SUB | 換人次數分析 |
|SB | 射門被阻擋次數分析 |
|SCORE_attack |	得分與進攻次數分析 |
|OFF_attack | 越位與進攻次數分析 |
|SCORE_PEN | 得分與罰球次數分析 |
|SHG_shot | 射正次數與總射門數分析 |
|SHB_shot | 射偏次數與總射門數分析 |
|SHW_shot | 射中球框次數與總射門數分析 |
|SHG_SHB_SHW | 射正、射偏與射中球框數據綜合分析 |
