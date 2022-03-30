import{s as e,c as a,d as t}from"./index.05817ad8.js";import{c as l,a1 as s,$ as i,a4 as n,a5 as d,m as r,t as o,F as u,M as c,l as p,Q as m}from"./@vue.160ddf67.js";import"./vue-router.852e3a0b.js";import"./vuex.1d6888bc.js";import"./axios.7b768d2b.js";import"./element-plus.ae16b58d.js";import"./resize-observer-polyfill.8deb1e21.js";import"./lodash.0d6f7410.js";import"./vue-i18n.3f148863.js";import"./@intlify.b71b68c2.js";import"./vue.21b55118.js";import"./normalize-wheel.1d574cd1.js";import"./mitt.20cc8481.js";import"./dayjs.e712f1b7.js";import"./async-validator.1fa0d626.js";import"./@popperjs.20e5d135.js";var h={name:"case",setup:()=>({items:l((()=>e.getters.getResponseData("case")))}),data:()=>({case_key:[{value:"id",name:"用例ID",width:"80"},{value:"country",name:"国家",width:"100"},{value:"group",name:"项目",width:"120"},{value:"channel",name:"资方",width:"120"},{value:"scene",name:"场景",width:"120"},{value:"asset_info",name:"资产信息",width:"120"},{value:"repay_info",name:"还款信息",width:"120"},{value:"check_capital_notify",name:"推送检查点",width:"120"},{value:"check_capital_tran",name:"资方计划检查点",width:"120"},{value:"check_central_msg",name:"dcs消息检查点",width:"120"},{value:"check_interface",name:"接口检查",width:"100"},{value:"check_capital_settlement_detail",name:"回购数据检测",width:"120"}]}),methods:{runSingleCase(e){a("run_single_case",{case_id:e})},updateSingleCase(e){a("update_single_case",{case:e})}},computed:{getResponseData:()=>a=>e.getters.getResponseData(a),getBtnStatus:()=>a=>e.getters.getSendList.includes(a)},created:function(){t()}};const _={class:"crumbs",style:{display:"none"}},v=d("i",{class:"el-icon-lx-calendar"},null,-1),f=m(" 用例 "),w=d("div",{class:"name-wrapper"}," 详细内容 ",-1),g=m(" 执行 "),b=m(" 更新 ");h.render=function(e,a,t,l,m,h){const j=s("el-breadcrumb-item"),y=s("el-breadcrumb"),k=s("el-input"),x=s("el-popover"),C=s("el-table-column"),S=s("el-button"),D=s("el-table");return i(),n("div",null,[d("div",_,[r(y,{separator:"/"},{default:o((()=>[r(j,null,{default:o((()=>[v,f])),_:1})])),_:1})]),r(D,{stripe:"",data:e.getResponseData("case"),style:{width:"100%"}},{default:o((()=>[(i(!0),n(u,null,c(e.case_key,(e=>(i(),n(u,null,["repay_info"==e.value||"asset_info"==e.value||e.value.startsWith("check_")?(i(),p(C,{key:0,prop:e.value,label:e.name,width:e.width},{default:o((a=>[r(x,{effect:"light",trigger:"click",placement:"middle",width:500},{default:o((()=>[r(k,{modelValue:a.row[e.value],"onUpdate:modelValue":t=>a.row[e.value]=t,type:"textarea",rows:15},null,8,["modelValue","onUpdate:modelValue"])])),reference:o((()=>[w])),_:2},1024)])),_:2},1032,["prop","label","width"])):(i(),p(C,{key:1,prop:e.value,label:e.name,width:e.width},null,8,["prop","label","width"]))],64)))),256)),r(C,{fixed:"right",label:"操作",width:"120"},{default:o((a=>[r(S,{onClick:t=>e.runSingleCase(a.row.id),type:"text",loading:e.getBtnStatus(a.row.id+"run_single_case"),size:"small"},{default:o((()=>[g])),_:2},1032,["onClick","loading"]),r(S,{onClick:t=>e.updateSingleCase(a.row),type:"text",loading:e.getBtnStatus(a.row.id+"update_single_case"),size:"small"},{default:o((()=>[b])),_:2},1032,["onClick","loading"])])),_:1})])),_:1},8,["data"])])};export default h;
