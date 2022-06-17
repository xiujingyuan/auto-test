GRANT_ASSET_IMPORT_URL = ""

FROM_SYSTEM_DICT = {
    "草莓": "strawberry",
    "重庆草莓": "strawberry",
    "香蕉": "banana",
    "火龙果": "pitaya",
}

# source_type 组合
IRR_NO = ("irr36", "", "")
APR_RONGDAN = ("apr36", "rongdan", "")
IRR_QUANYI = ("irr36_quanyi", "", "lieyin")
IRR_RONGDAN = ("irr36", "rongdan_irr", "")
IRR_RONGDAN_QUANYI = ("irr36_quanyi", "rongdan_irr", "lieyin")

# 各个资方能使用的source_type场景
CHANNEL_SOURCE_TYPE_DICT = {
  "qinnong": [IRR_NO, IRR_QUANYI],
  "qinnong_jieyi": [IRR_NO, IRR_QUANYI],
  "mozhi_jinmeixin": [IRR_NO, IRR_QUANYI],
  "beiyin_tianbang": [APR_RONGDAN, IRR_QUANYI],
  "weipin_zhongwei": [APR_RONGDAN, IRR_QUANYI],
  "jincheng_hanchen": [APR_RONGDAN, IRR_QUANYI],
  "zhongyuan_zunhao": [APR_RONGDAN, IRR_QUANYI],
  "yilian_dingfeng": [APR_RONGDAN],
  "hamitianshan_xingjiang": [APR_RONGDAN, IRR_QUANYI],
  "hami_tianshan": [APR_RONGDAN, IRR_QUANYI],
  "hami_tianshan_tianbang": [APR_RONGDAN, IRR_QUANYI],
  "huabei_runqian": [APR_RONGDAN, IRR_QUANYI],
  "longjiang_daqin": [APR_RONGDAN, IRR_RONGDAN_QUANYI],
  "mozhi_beiyin_zhongyi": [APR_RONGDAN],
  "zhongke_lanzhou": [APR_RONGDAN, IRR_RONGDAN_QUANYI],
  # "zhongke_hegang": [IRR_NO, IRR_QUANYI],
  "zhongke_hegang": [APR_RONGDAN, IRR_RONGDAN_QUANYI],
  "shilong_siping": [APR_RONGDAN, IRR_RONGDAN_QUANYI],
  "lanzhou_haoyue": [APR_RONGDAN, IRR_RONGDAN_QUANYI],
  "lanzhou_dingsheng_zkbc2": [APR_RONGDAN, IRR_RONGDAN_QUANYI],
  "tongrongqianjingjing": [APR_RONGDAN, IRR_QUANYI],
  "haohanqianjingjing": [APR_RONGDAN, IRR_QUANYI],
  "jinmeixin_daqin": [APR_RONGDAN, IRR_QUANYI],
  "weishenma_daxinganling": [APR_RONGDAN],
}










