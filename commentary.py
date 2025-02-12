from openai import OpenAI
import os
import argparse
import itertools
import csv
from dotenv import load_dotenv

language_mapping = {'SB': "射門被阻擋次數",
                'SCORE': "得分",
                'PEN': "罰球次數",
                'OFF': "越位次數",
                'SHG': "射正球門次數",
                'SUB': "換人次數",
                'SHW': "射中球框次數",
                'CR': "角球次數",
                'conversion_rate': "命中率",
                'YC': "黃牌數",
                'attack': "進攻次數",
                'SHB': "射偏次數",
                "block": "成功阻擋射門次數",
                "shot": "射門次數"
                }

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key
client = OpenAI()

SHG_rule = [
        "主客隊的射正次數都是0",
        "主客隊的射正次數相同",
        "主隊的射正次數比客隊多2次以下",
        "主隊的射正次數比客隊多3~5次",
        "主隊的射正次數比客隊多6次以上",
        "客隊的射正次數比主隊多2次以下",
        "客隊的射正次數比主隊多3~5次",
        "客隊的射正次數比主隊多6次以上",
    ]

SHB_rule = [
        "主客隊的射偏次數都是0",
        "主客隊的射偏次數相同",
        "主隊的射偏次數比客隊多2次以下",
        "主隊的射偏次數比客隊多3~5次",
        "主隊的射偏次數比客隊多6次以上",
        "客隊的射偏次數比主隊多2次以下",
        "客隊的射偏次數比主隊多3~5次",
        "客隊的射偏次數比主隊多6次以上",
    ]

SHW_rule = [
        "主客隊的射中球框次數都是0",
        "主客隊的射中球框次數相同",
        "主隊的射中球框次數比客隊多2次以下",
        "主隊的射中球框次數比客隊多3次以上",
        "客隊的射中球框次數比主隊多2次以下",
        "客隊的射中球框次數比主隊多3次以上",
    ]

SB_rule = [
        "主客隊的射門被阻擋次數都是0",
        "主客隊的射門被阻擋次數相同",
        "主隊的射門被阻擋次數比客隊多2次以下",
        "主隊的射門被阻擋次數比客隊多3~5次",
        "主隊的射門被阻擋次數比客隊多6次以上",
        "客隊的射門被阻擋次數比主隊多2次以下",
        "客隊的射門被阻擋次數比主隊多3~5次",
        "主隊的射門被阻擋次數比客隊多6次以上"
    ]

shot_rule = [
        "主客隊的射門次數都是0",
        "主客隊的射門次數相同",
        "主隊的射門次數比客隊多2次以下",
        "主隊的射門次數比客隊多3~5次",
        "主隊的射門次數比客隊多6次以上",
        "客隊的射門次數比主隊多2次以下",
        "客隊的射門次數比主隊多3~5次",
        "客隊的射門次數比主隊多6次以上",
    ]

def translate_event(event_text):
    """使用 OpenAI API 翻譯足球事件"""
    result = client.chat.completions.create(
        model="gpt-4o",  # 或 gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "你是一名專業的足球主播，僅依據我提供的統計數據播報足球比賽現場主隊與客隊的情況。請直接描述場上動態和相關統計，只使用第三人稱描述，不進行自我介紹、不與觀眾互動，也不要加入主觀期待或臆測。請完全使用繁體中文。"},
            {"role": "user", "content": event_text}
        ]
    )
    return result.to_dict()['choices'][0]['message']['content']

def get_SUB_content():
    contents = []

    for (sub1, sub2) in itertools.product(range(7), repeat=2):
        content = f"主客隊的換人次數是{sub1}比{sub2}"
        contents.append(content)
    
    return contents

def get_SB_content():
    contents = []

    for rule in SB_rule:
        content = f"{rule}，需要提及兩隊的射門被阻擋次數，用#SB1和#SB2來代替，主隊和客隊分別用#TA和#TB來代替"
        contents.append(content)
    
    return contents

def get_RC_YC_content():
    contents = []

    yc_rules = [
        "主客隊的黃卡次數都是0次",
        "主隊的黃卡次數是15次，再多拿到一張黃牌就會終止比賽，因為這樣會使場上的人數小於規定的數量",
        "客隊的黃卡次數是15次，再多拿到一張黃牌就會終止比賽，因為這樣會使場上的人數小於規定的數量",
        "主隊的黃卡次數是16次，使場上的人數小於規定的人而比賽終止",
        "客隊的黃卡次數是16次，使場上的人數小於規定的人而比賽終止",
        "主隊客隊的黃卡次數相同",
        "主隊的黃卡次數比客隊多2次以下",
        "主隊的黃卡次數比客隊多3次以上",
        "客隊的黃卡次數比主隊多2次以下",
        "客隊的黃卡次數比主隊多3次以上"
    ]

    for rc1, rc2, rule in itertools.product(range(6), range(6), yc_rules):
        content = (
            f"主客隊的紅卡次數是{rc1}比{rc2}，"
            f"{rule}，"
            "需要提及兩隊的黃牌次數，用#YC1和#YC2來代替，"
            "主隊和客隊分別用#TA和#TB來代替"
        )
        contents.append(content)
    
    return contents

def get_SCORE_attack_content():
    contents = []

    score_rule = [
        "主客隊的分數都是0",
        "主客隊的分數相同",
        "主隊的分數比客隊多1分",
        "主隊的分數比客隊多2分",
        "主隊的分數比客隊多3分以上",
        "客隊的分數比主隊多1分",
        "客隊的分數比主隊多2分",
        "客隊的分數比主隊多3分以上"
    ]

    attack_rule = [
        "主客隊的攻擊次數都是0，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替",
        "主客隊的攻擊次數相同，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替",
        "主隊的攻擊次數比客隊多10次以內，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替",
        "客隊的攻擊次數比主隊多10次以內，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替",
        "主客隊的攻擊次數相同且有一定的數量，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替",
        "主隊的攻擊次數是客隊的1.5倍，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替，差距的倍數可以用#attack_ratio代替",
        "主隊的攻擊次數是客隊的3倍以上，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替，差距的倍數可以用#attack_ratio代替",
        "客隊的攻擊次數是主隊的1.5，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替，差距的倍數可以用#attack_ratio代替倍",
        "客隊的攻擊次數是主隊的3倍以上，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替，差距的倍數可以用#attack_ratio代替"
    ]

    for (s_rule, a_rule) in itertools.product(score_rule, attack_rule):
        content = (
            f"{s_rule}，需要提及兩隊的分數，用#SCORE1和#SCORE2來代替，"
            f"{a_rule}，如果次數相同可以用其中一個表示就好，主隊和客隊分別用#TA和#TB來代替"
        )
        contents.append(content)
    
    return contents

def get_OFF_attack_content():
    contents = []

    OFF_rule = [
        "主客隊的越位次數都是0",
        "主客隊的越位次數相同",
        "主隊的越位次數比客隊多2次以內",
        "主隊的越位次數比客隊多3次以上",
        "客隊的越位次數比主隊多2次以內",
        "客隊的越位次數比主隊多3次以上"
    ]

    attack_rule = [
        "主客隊的攻擊次數都是0，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替",
        "主客隊的攻擊次數相同，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替",
        "主隊的攻擊次數比客隊多10次以內，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替",
        "客隊的攻擊次數比主隊多10次以內，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替",
        "主客隊的攻擊次數相同且有一定的數量，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替",
        "主隊的攻擊次數是客隊的1.5倍，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替，差距的倍數可以用#attack_ratio代替",
        "主隊的攻擊次數是客隊的3倍以上，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替，差距的倍數可以用#attack_ratio代替",
        "客隊的攻擊次數是主隊的1.5，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替，差距的倍數可以用#attack_ratio代替倍",
        "客隊的攻擊次數是主隊的3倍以上，需要提及兩隊的攻擊次數，用#attack1和#attack2來代替，差距的倍數可以用#attack_ratio代替"
    ]

    for (o_rule, a_rule) in itertools.product(OFF_rule, attack_rule):
        content = (
            f"{o_rule}，需要提及兩隊的越位次數，用#OFF1和#OFF2來代替，如果次數相同可以用其中一個表示就好，"
            f"{a_rule}，如果次數相同可以用其中一個表示就好，主隊和客隊分別用#TA和#TB來代替"
        )
        contents.append(content)
    
    return contents

def get_SCORE_PEN_content():
    contents = []

    score_rule = [
        "主客隊的分數都是0",
        "主客隊的分數相同",
        "主隊的分數比客隊多1分",
        "主隊的分數比客隊多2分",
        "主隊的分數比客隊多3分以上",
        "客隊的分數比主隊多1分",
        "客隊的分數比主隊多2分",
        "客隊的分數比主隊多3分以上"
    ]

    for s_rule, pen1, pen2 in itertools.product(score_rule, range(6), range(6)):
        content = (
            f"{s_rule}，需要提及兩隊的分數，用#SCORE1和#SCORE2來代替，"
            f"主客隊的罰球次數是{pen1}比{pen2}，"
            "需要提及兩隊的罰球次數，用#PEN1和#PEN2來代替，"
            "主隊和客隊分別用#TA和#TB來代替"
        )
        contents.append(content)
    
    return contents

def get_SHG_shot_content():
    contents = []

    for (shg_rule, s_rule) in itertools.product(SHG_rule, shot_rule):
        content = (
            f"{shg_rule}，需要提及兩隊的射正次數，用#SHG1和#SHG2來代替，"
            f"{s_rule}，需要提及兩隊的射門次數，用#shot1和#shot2來代替，"
            "如果次數相同可以用其中一個表示就好，主隊和客隊分別用#TA和#TB來代替"
        )
        contents.append(content)
    
    return contents

def get_SHB_shot_content():
    contents = []

    for (shb_rule, s_rule) in itertools.product(SHB_rule, shot_rule):
        content = (
            f"{shb_rule}，需要提及兩隊的射偏次數，用#SHB1和#SHB2來代替，"
            f"{s_rule}，需要提及兩隊的射門次數，用#shot1和#shot2來代替，"
            "如果次數相同可以用其中一個表示就好，主隊和客隊分別用#TA和#TB來代替"
        )
        contents.append(content)
    
    return contents

def get_SHW_shot_content():
    contents = []

    for (shw_rule, s_rule) in itertools.product(SHW_rule, shot_rule):
        content = (
            f"{shw_rule}，需要提及兩隊的射中球框次數，用#SHG1和#SHG2來代替，"
            f"{s_rule}，需要提及兩隊的射門次數，用#shot1和#shot2來代替，"
            "如果次數相同可以用其中一個表示就好，主隊和客隊分別用#TA和#TB來代替"
        )
        contents.append(content)
    
    return contents

def get_SB_shot_content():
    contents = []

    for (sb_rule, s_rule) in itertools.product(SB_rule, shot_rule):
        content = (
            f"{sb_rule}，需要提及兩隊的射門被阻擋次數，用#SB1和#SB2來代替，"
            f"{s_rule}，需要提及兩隊的射門次數，用#shot1和#shot2來代替，"
            "如果次數相同可以用其中一個表示就好，主隊和客隊分別用#TA和#TB來代替"
        )
        contents.append(content)
    
    return contents

def get_SHG_SHB_SHW_content():
    contents = []

    for (shg_rule, shb_rule, shw_rule) in itertools.product(SHG_rule, SHB_rule, SHW_rule):
        content = (
            f"{shg_rule}，需要提及兩隊的射正次數，用#SHG1和#SHG2來代替，"
            f"{shb_rule}，需要提及兩隊的射偏次數，用#SHB1和#SHB2來代替，"
            f"{shw_rule}，需要提及兩隊的射中球框次數，用#SHG1和#SHG2來代替，"
            "如果次數相同可以用其中一個表示就好，主隊和客隊分別用#TA和#TB來代替"
        )
        contents.append(content)
    
    return contents

def get_CR_content():
    contents = []

    cr_rule = [
        "主客隊的角球次數都是0",
        "主隊的角球次數是0，客隊的角球次數大於0",
        "客隊的角球次數是0，主隊的角球次數大於0",
        "主客隊的角球次數相同",
        "主隊的角球次數比客隊多3次以內",
        "主隊的角球次數比客隊多4次以上",
        "客隊的角球次數比主隊多3次以內",
        "客隊的角球次數比主隊多4次以上"
    ]


    for rule in cr_rule:
        content = (
            f"{rule}，需要提及兩隊的角球次數，分別用#CR1和#CR2代替，"
            "如果次數相同可以用其中一個表示就好，主隊和客隊分別用#TA和#TB來代替"
        )
        contents.append(content)
    
    return contents


def get_commentary(contents):
    commentary = []
    for c in contents:
        commentary.append(translate_event(c))

    return commentary

def save_to_csv(comms, contents, filename):
    max_len = max(len(comms), len(contents))

    comms += [""] * (max_len - len(comms))
    contents += [""] * (max_len - len(contents))

    with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["台詞", "gpt command"])  # 寫入表頭

        for comm, cont in zip(comms, contents):
            writer.writerow([comm, cont])  # 每行寫入一組數據

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", 
                        default=["CR"], 
                        nargs="+",
                        choices=["all", "CR", "RC_YC", "SUB", "SB", "SCORE_attack", "OFF_attack", "SCORE_PEN", 
                                 "SHG_shot", "SHB_shot", "SHW_shot", "SB_shot", "SHG_SHB_SHW"],
                        help="The type of commentary you want to generate, for example, --type RC_YC SUB SB"
                                )
    args = parser.parse_args()

    if args.type == ["all"]:
        args.type = ["CR", "RC_YC", "SUB", "SB", "SCORE_attack", "OFF_attack", "SCORE_PEN", 
                     "SHG_shot", "SHB_shot", "SHW_shot", "SB_shot", "SHG_SHB_SHW"]

    for type in args.type:
        if type == "CR":
            CR_content = get_CR_content()
            cr_commentary = get_commentary(CR_content)
            save_to_csv(cr_commentary, CR_content, "./commentary/CR.csv")
            print("CR done")

        elif type == "RC_YC":
            RC_YC_content = get_RC_YC_content()
            RC_YC_commentary = get_commentary(RC_YC_content)
            save_to_csv(RC_YC_commentary, RC_YC_content, "./commentary/RC_YC.csv")
            print("RC_YC done")

        elif type == "SUB":
            SUB_content = get_SUB_content()
            sub_commentary = get_commentary(SUB_content)
            save_to_csv(sub_commentary, SUB_content, "./commentary/SUB.csv")
            print("SUB done")

        elif type == "SB":
            SB_content = get_SB_content()
            sub_commentary = get_commentary(SB_content)
            save_to_csv(sub_commentary, SB_content, "./commentary/SB.csv")
            print("SB done")

        elif type == "SCORE_attack":
            SCORE_attack_content = get_SCORE_attack_content()
            SCORE_attack_commentary = get_commentary(SCORE_attack_content)
            save_to_csv(SCORE_attack_commentary, SCORE_attack_content, "./commentary/SCORE_attack.csv")
            print("SCORE_attack done")

        elif type == "OFF_attack":
            OFF_attack_content = get_OFF_attack_content()
            OFF_attack_commentary = get_commentary(OFF_attack_content)
            save_to_csv(OFF_attack_commentary, OFF_attack_content, "./commentary/OFF_attack.csv")
            print("OFF_attack done")

        elif type == "SCORE_PEN":
            SCORE_PEN_content = get_SCORE_PEN_content()
            SCORE_PEN_commentary = get_commentary(SCORE_PEN_content)
            save_to_csv(SCORE_PEN_commentary, SCORE_PEN_content, "./commentary/SCORE_PEN.csv")
            print("SCORE_PEN done")

        elif type == "SHG_shot":
            SHG_shot_content = get_SHG_shot_content()
            SHG_shot_commentary = get_commentary(SHG_shot_content)
            save_to_csv(SHG_shot_commentary, SHG_shot_content, "./commentary/SHG_shot.csv")
            print("SHG_shot done")

        elif type == "SHB_shot":
            SHB_shot_content = get_SHB_shot_content()
            SHB_shot_commentary = get_commentary(SHB_shot_content)
            save_to_csv(SHB_shot_commentary, SHB_shot_content, "./commentary/SHB_shot.csv")
            print("SHB_shot done")

        elif type == "SHW_shot":
            SHW_shot_content = get_SHW_shot_content()
            SHW_shot_commentary = get_commentary(SHW_shot_content)
            save_to_csv(SHW_shot_commentary, SHW_shot_content, "./commentary/SHW_shot.csv")
            print("SHW_shot done")  

        elif type == "SB_shot":
            SB_shot_content = get_SB_shot_content()
            SB_shot_commentary = get_commentary(SB_shot_content)
            save_to_csv(SB_shot_commentary, SB_shot_content, "./commentary/SB_shot.csv")
            print("SB_shot done")

        elif type == "SHG_SHB_SHW":
            SHG_SHB_SHW_content = get_SHG_SHB_SHW_content()
            SHG_SHB_SHW_commentary = get_commentary(SHG_SHB_SHW_content)
            save_to_csv(SHG_SHB_SHW_commentary, SHG_SHB_SHW_content, "./commentary/SHG_SHB_SHW.csv")
            print("SHG_SHB_SHW done")


    

    

    
